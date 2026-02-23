"""Views pour la gestion de base des événements."""

from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView

from accounts.models import Role, UserRole
from accounts.services import NotificationService
from events.forms import EventCommentForm
from events.models import Event


class EventListView(ListView):
    """Vue liste des événements à venir (timeline uniquement)."""

    model = Event
    template_name = "events/event_list.html"
    context_object_name = "upcoming_events"

    def get_queryset(self):
        """Retourne uniquement les événements à venir pour la timeline."""
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)

        return (
            Event.objects.filter(
                is_active=True,
                start_datetime__date__gte=today,
                start_datetime__date__lte=thirty_days_later,
            )
            .prefetch_related("sectors", "validation", "video_requests")
            .order_by("start_datetime")[:10]
        )

    def get_context_data(self, **kwargs):
        """Ajoute la date actuelle pour le regroupement par semaine."""
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class EventArchiveView(ListView):
    """Vue des archives d'événements avec recherche et filtres."""

    model = Event
    template_name = "events/event_archives.html"
    context_object_name = "events"
    paginate_by = 12

    def _user_has_communication_role(self):
        """Vérifie si l'utilisateur a le rôle Communication (avec cache)."""
        if not self.request.user.is_authenticated:
            return False

        # Cache pour éviter les requêtes répétées
        cache_key = f"user_comm_role_{self.request.user.id}"
        result = cache.get(cache_key)

        if result is None:
            try:
                communication_role = Role.objects.get(
                    name="Communication", is_active=True
                )
                result = UserRole.objects.filter(
                    user=self.request.user, role=communication_role, is_active=True
                ).exists()
            except Role.DoesNotExist:
                result = False
            cache.set(cache_key, result, 300)  # Cache pendant 5 minutes

        return result

    def get_queryset(self):
        """Filtre les événements archivés selon les paramètres GET."""
        today = date.today()

        # Filtrer uniquement les événements passés (archives)
        queryset = (
            Event.objects.filter(is_active=True, start_datetime__date__lt=today)
            .prefetch_related("sectors", "validation")
            .select_related("created_by")
        )

        # Filtre par secteurs (multiple)
        sector_ids = self.request.GET.getlist("sector")
        if sector_ids:
            queryset = queryset.filter(sectors__id__in=sector_ids).distinct()

        # Filtre par ville
        city = self.request.GET.get("city")
        if city:
            queryset = queryset.filter(city__icontains=city)

        # Filtre par date
        date_from = self.request.GET.get("date_from")
        if date_from:
            queryset = queryset.filter(start_datetime__date__gte=date_from)

        date_to = self.request.GET.get("date_to")
        if date_to:
            queryset = queryset.filter(start_datetime__date__lte=date_to)

        # Recherche texte (paramètre 'q' pour la barre de recherche)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(location__icontains=q)
                | Q(city__icontains=q)
            )

        # Filtre par statut de validation
        status = self.request.GET.get("status")
        if status:
            if status == "validated":
                queryset = queryset.filter(validation__is_validated=True)
            elif status == "pending":
                queryset = queryset.filter(validation__isnull=True)
            elif status == "rejected":
                queryset = queryset.filter(validation__is_validated=False)

        return queryset.order_by("-start_datetime")

    def get_context_data(self, **kwargs):
        """Ajoute les filtres au contexte."""
        context = super().get_context_data(**kwargs)
        from events.models import Sector

        context["sectors"] = Sector.objects.filter(is_active=True)

        # Déterminer si l'utilisateur a le rôle Communication
        user_has_comm_role = self._user_has_communication_role()
        context["user_has_comm_role"] = user_has_comm_role

        # Filtrer les villes selon le rôle de l'utilisateur (avec caching)
        cache_key = f"event_cities_{user_has_comm_role}_{self.request.user.id if self.request.user.is_authenticated else 'anon'}"
        cities = cache.get(cache_key)

        if cities is None:
            cities_queryset = Event.objects.filter(is_active=True)
            cities = list(
                cities_queryset.values_list("city", flat=True)
                .distinct()
                .order_by("city")
            )
            cache.set(cache_key, cities, 3600)  # Cache pendant 1 heure

        context["cities"] = cities

        # Secteurs sélectionnés pour le filtre
        context["selected_sectors"] = self.request.GET.getlist("sector")
        # Conserver les paramètres de filtre pour la pagination (en excluant 'page')
        filter_params = self.request.GET.copy()
        if "page" in filter_params:
            filter_params.pop("page")
        context["filter_params"] = filter_params.urlencode()

        return context


class EventCalendarView(ListView):
    """Vue calendrier des événements."""

    model = Event
    template_name = "events/event_calendar.html"
    context_object_name = "events"

    def get_queryset(self):
        """Filtre les événements selon le mois et l'année."""
        import calendar

        year = self.kwargs.get("year", timezone.now().year)
        month = self.kwargs.get("month", timezone.now().month)

        # Récupérer tous les événements actifs avec prefetch_related pour optimisation
        events = Event.objects.filter(is_active=True).prefetch_related("sectors")

        # Filtrer par mois et année
        events = events.filter(start_datetime__year=year, start_datetime__month=month)

        return events.order_by("start_datetime")

    def get_context_data(self, **kwargs):
        """Ajoute les données du calendrier au contexte."""
        import calendar

        context = super().get_context_data(**kwargs)

        year = self.kwargs.get("year", timezone.now().year)
        month = self.kwargs.get("month", timezone.now().month)

        # Créer le calendrier
        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(year, month)

        context["year"] = year
        context["month"] = month
        context["month_name"] = calendar.month_name[month]
        context["month_days"] = month_days

        # Navigation
        if month == 1:
            context["prev_month"] = 12
            context["prev_year"] = year - 1
        else:
            context["prev_month"] = month - 1
            context["prev_year"] = year

        if month == 12:
            context["next_month"] = 1
            context["next_year"] = year + 1
        else:
            context["next_month"] = month + 1
            context["next_year"] = year

        return context


class EventDetailView(DetailView):
    """Vue détail d'un événement."""

    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Inclut les relations pour optimisation."""
        return Event.objects.filter(is_active=True).prefetch_related(
            "sectors", "images", "documents", "comments__author"
        )

    def get_context_data(self, **kwargs):
        """Ajoute le formulaire de commentaire au contexte."""
        context = super().get_context_data(**kwargs)
        context["comment_form"] = EventCommentForm()
        return context

    def post(self, request, *args, **kwargs):
        """Gère l'ajout d'un commentaire."""
        self.object = self.get_object()
        form = EventCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = self.object
            comment.user = request.user
            comment.save()

            # Envoyer une notification
            NotificationService.notify_event_commented(comment)

            from django.contrib import messages

            messages.success(request, "Votre commentaire a été ajouté.")
            return redirect(self.object.get_absolute_url())

        context = self.get_context_data(object=self.object)
        context["comment_form"] = form
        return self.render_to_response(context)


class MyEventsView(LoginRequiredMixin, ListView):
    """Vue pour afficher les événements créés par l'utilisateur connecté."""

    model = Event
    template_name = "events/my_events.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        """Retourne uniquement les événements créés par l'utilisateur."""
        queryset = Event.objects.filter(
            created_by=self.request.user, is_active=True
        ).prefetch_related("sectors", "validation")

        # Filtre par statut de validation
        status = self.request.GET.get("status")
        if status:
            if status == "validated":
                queryset = queryset.filter(validation__is_validated=True)
            elif status == "pending":
                queryset = queryset.filter(validation__isnull=True)
            elif status == "rejected":
                queryset = queryset.filter(validation__is_validated=False)

        # Filtre par type (passés/à venir)
        event_type = self.request.GET.get("type")
        today = timezone.now()
        if event_type == "upcoming":
            queryset = queryset.filter(start_datetime__gte=today)
        elif event_type == "past":
            queryset = queryset.filter(start_datetime__lt=today)

        return queryset.order_by("-start_datetime")

    def get_context_data(self, **kwargs):
        """Ajoute les statistiques et filtres au contexte."""
        context = super().get_context_data(**kwargs)

        # Statistiques
        user_events = Event.objects.filter(created_by=self.request.user, is_active=True)

        context["total_events"] = user_events.count()
        context["validated_count"] = user_events.filter(
            validation__is_validated=True
        ).count()
        context["pending_count"] = user_events.filter(validation__isnull=True).count()
        context["rejected_count"] = user_events.filter(
            validation__is_validated=False
        ).count()

        # Événements à venir
        today = timezone.now()
        context["upcoming_count"] = user_events.filter(
            start_datetime__gte=today
        ).count()

        # Filtres actuels
        context["current_status"] = self.request.GET.get("status", "")
        context["current_type"] = self.request.GET.get("type", "")

        # Conserver les paramètres de filtre pour la pagination
        filter_params = self.request.GET.copy()
        if "page" in filter_params:
            filter_params.pop("page")
        context["filter_params"] = filter_params.urlencode()

        return context
