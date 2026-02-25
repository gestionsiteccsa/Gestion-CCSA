"""Vues pour l'app feedback."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from feedback.forms import FeedbackCommentForm, FeedbackSettingsForm, FeedbackTicketForm
from feedback.models import FeedbackSettings, FeedbackTicket


class IsSupportMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur a le rôle Support."""

    def test_func(self):
        """Vérifie que l'utilisateur a le rôle Support."""
        return self.request.user.user_roles.filter(role__name="Support", is_active=True).exists()


class IsOwnerOrSupportMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est propriétaire ou support."""

    def test_func(self):
        """Vérifie que l'utilisateur est propriétaire ou support."""
        if not self.request.user.is_authenticated:
            return False
        ticket = self.get_object()
        is_owner = ticket.created_by == self.request.user
        is_support = self.request.user.user_roles.filter(
            role__name="Support", is_active=True
        ).exists()
        return is_owner or is_support


class FeedbackListView(LoginRequiredMixin, ListView):
    """Vue liste des tickets de l'utilisateur connecté."""

    model = FeedbackTicket
    template_name = "feedback/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 10

    def get_queryset(self):
        """Récupère les tickets de l'utilisateur avec filtres."""
        queryset = FeedbackTicket.objects.filter(created_by=self.request.user).order_by(
            "-created_at"
        )

        # Filtre par statut
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        """Ajoute les filtres au contexte."""
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["status_choices"] = FeedbackTicket.STATUS_CHOICES
        return context


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    """Vue de création d'un ticket."""

    model = FeedbackTicket
    form_class = FeedbackTicketForm
    template_name = "feedback/ticket_form.html"
    success_url = reverse_lazy("feedback:ticket_list")

    def get_form_kwargs(self):
        """Passer l'utilisateur au formulaire."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Sauvegarde le ticket et envoie les notifications."""
        ticket = form.save()
        self.send_notifications(ticket)
        messages.success(
            self.request,
            "Votre ticket a été créé avec succès. "
            "Notre équipe vous répondra dans les plus brefs délais.",
        )
        return super().form_valid(form)

    def send_notifications(self, ticket):
        """Envoie les notifications (email et in-app)."""
        settings_obj = FeedbackSettings.get_settings()

        if settings_obj.notify_on_new_ticket:
            # Envoi d'emails
            self.send_email_notifications(ticket, settings_obj)

            # Création de notifications in-app pour le support
            self.create_support_notifications(ticket)

    def send_email_notifications(self, ticket, settings_obj):
        """Envoie les emails de notification."""
        recipients = list(settings_obj.email_recipients.values_list("email", flat=True))
        if recipients:
            subject = f"[Feedback] Nouveau ticket : {ticket.title}"
            message = f"""
Un nouveau ticket a été créé :

Titre : {ticket.title}
Type : {ticket.get_ticket_type_display()}
Priorité : {ticket.get_priority_display()}
Créé par : {ticket.created_by.get_full_name() or ticket.created_by.email}

Description :
{ticket.description}

Voir le ticket : {self.request.build_absolute_uri(
    reverse('feedback:ticket_detail', kwargs={'pk': ticket.pk})
)}
            """
            from_email = settings_obj.from_email or None
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=True,
            )

    def create_support_notifications(self, ticket):
        """Crée des notifications in-app pour les utilisateurs support."""
        from accounts.models import Notification, User

        # Récupérer tous les utilisateurs avec le rôle Support
        support_users = User.objects.filter(
            user_roles__role__name="Support", user_roles__is_active=True
        ).distinct()

        for support_user in support_users:
            Notification.objects.create(
                user=support_user,
                notification_type="feedback_new_ticket",
                title=f"Nouveau ticket : {ticket.title}",
                message=(
                    f"Un nouveau ticket de type '{ticket.get_ticket_type_display()}' "
                    f"a été créé par {ticket.created_by.email}."
                ),
                link=reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk}),
            )


class FeedbackDetailView(LoginRequiredMixin, IsOwnerOrSupportMixin, DetailView):
    """Vue détail d'un ticket avec commentaires."""

    model = FeedbackTicket
    template_name = "feedback/ticket_detail.html"
    context_object_name = "ticket"

    def get_context_data(self, **kwargs):
        """Ajoute le formulaire de commentaire et les commentaires."""
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related("author").all()
        context["comment_form"] = FeedbackCommentForm()
        return context

    def post(self, request, *args, **kwargs):
        """Gère l'ajout d'un commentaire."""
        self.object = self.get_object()
        form = FeedbackCommentForm(request.POST, ticket=self.object, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Commentaire ajouté avec succès.")
            return redirect("feedback:ticket_detail", pk=self.object.pk)
        return self.render_to_response(self.get_context_data(comment_form=form))


class FeedbackAdminListView(LoginRequiredMixin, IsSupportMixin, ListView):
    """Vue admin pour le support (liste de tous les tickets)."""

    model = FeedbackTicket
    template_name = "feedback/admin_list.html"
    context_object_name = "tickets"
    paginate_by = 20

    def get_queryset(self):
        """Récupère tous les tickets avec filtres."""
        queryset = FeedbackTicket.objects.all().order_by("-created_at")

        # Filtres
        status = self.request.GET.get("status")
        ticket_type = self.request.GET.get("ticket_type")
        priority = self.request.GET.get("priority")

        if status:
            queryset = queryset.filter(status=status)
        if ticket_type:
            queryset = queryset.filter(ticket_type=ticket_type)
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset.select_related("created_by", "assigned_to")

    def get_context_data(self, **kwargs):
        """Ajoute les filtres au contexte."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "status_filter": self.request.GET.get("status", ""),
                "type_filter": self.request.GET.get("ticket_type", ""),
                "priority_filter": self.request.GET.get("priority", ""),
                "status_choices": FeedbackTicket.STATUS_CHOICES,
                "type_choices": FeedbackTicket.TICKET_TYPE_CHOICES,
                "priority_choices": FeedbackTicket.PRIORITY_CHOICES,
            }
        )
        return context


class FeedbackUpdateStatusView(LoginRequiredMixin, IsSupportMixin, UpdateView):
    """Vue pour mettre à jour le statut d'un ticket (support uniquement)."""

    model = FeedbackTicket
    fields = ["status"]
    template_name = "feedback/ticket_update_status.html"

    def get_form(self, form_class=None):
        """Configure le widget pour le champ status."""
        form = super().get_form(form_class)
        form.fields["status"].widget.attrs.update({"class": "form-select"})
        return form

    def form_valid(self, form):
        """Sauvegarde et envoie les notifications."""
        old_status = self.get_object().status
        ticket = form.save()

        if old_status != ticket.status:
            self.send_status_notification(ticket)
            messages.success(
                self.request,
                f"Le statut du ticket a été mis à jour : {ticket.get_status_display()}",
            )

        return redirect("feedback:admin_list")

    def send_status_notification(self, ticket):
        """Envoie une notification au créateur du ticket."""
        settings_obj = FeedbackSettings.get_settings()

        if settings_obj.notify_on_status_change:
            # Notification in-app
            from accounts.models import Notification

            Notification.objects.create(
                user=ticket.created_by,
                notification_type="feedback_status_changed",
                title=f"Mise à jour de votre ticket : {ticket.title}",
                message=f"Le statut de votre ticket est passé à '{ticket.get_status_display()}'.",
                link=reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk}),
            )

            # Email au créateur
            if ticket.created_by.email:
                subject = f"[Feedback] Mise à jour de votre ticket : {ticket.title}"
                message = f"""
Bonjour,

Le statut de votre ticket a été mis à jour :

Titre : {ticket.title}
Nouveau statut : {ticket.get_status_display()}

Voir le ticket : {self.request.build_absolute_uri(
    reverse('feedback:ticket_detail', kwargs={'pk': ticket.pk})
)}

Cordialement,
L'équipe support
                """
                from_email = settings_obj.from_email or None
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=[ticket.created_by.email],
                    fail_silently=True,
                )


class FeedbackSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue de configuration des paramètres (superadmin uniquement)."""

    model = FeedbackSettings
    form_class = FeedbackSettingsForm
    template_name = "feedback/settings.html"
    success_url = reverse_lazy("feedback:settings")

    def test_func(self):
        """Vérifie que l'utilisateur est superadmin."""
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        """Récupère ou crée les paramètres."""
        return FeedbackSettings.get_settings()

    def form_valid(self, form):
        """Sauvegarde les paramètres."""
        messages.success(self.request, "Les paramètres du système de feedback ont été mis à jour.")
        return super().form_valid(form)
