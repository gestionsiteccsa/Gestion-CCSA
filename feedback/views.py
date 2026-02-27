"""Vues pour l'app feedback."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from feedback.forms import FeedbackCommentForm, FeedbackSettingsForm, FeedbackTicketForm
from feedback.mixins import IsOwnerOrSupportMixin, IsSupportMixin
from feedback.models import FeedbackSettings, FeedbackTicket
from feedback.services.notifications import FeedbackNotificationService


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
        FeedbackNotificationService.notify_new_ticket(ticket, self.request)
        messages.success(
            self.request,
            "Votre ticket a été créé avec succès. "
            "Notre équipe vous répondra dans les plus brefs délais.",
        )
        return super().form_valid(form)


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
            FeedbackNotificationService.notify_status_changed(ticket, self.request)
            messages.success(
                self.request,
                f"Le statut du ticket a été mis à jour : {ticket.get_status_display()}",
            )

        return redirect("feedback:admin_list")


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
        messages.success(
            self.request, "Les paramètres du système de feedback ont été mis à jour."
        )
        return super().form_valid(form)
