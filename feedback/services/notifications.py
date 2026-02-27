"""Service de notification pour le système de feedback."""

from django.core.mail import send_mail
from django.urls import reverse

from accounts.models import Notification, User
from feedback.models import FeedbackSettings


class FeedbackNotificationService:
    """Service de notification pour les tickets de feedback.
    
    Gère l'envoi de notifications email et in-app pour les événements
    liés au système de feedback (création de ticket, changement de statut).
    """

    @staticmethod
    def notify_new_ticket(ticket, request=None):
        """Notifie le support quand un nouveau ticket est créé.
        
        Args:
            ticket: Le FeedbackTicket créé
            request: La requête HTTP (optionnel, pour construire les URLs absolues)
        """
        settings_obj = FeedbackSettings.get_settings()

        if settings_obj.notify_on_new_ticket:
            # Envoi d'emails
            FeedbackNotificationService._send_new_ticket_emails(ticket, settings_obj, request)
            
            # Création de notifications in-app pour le support
            FeedbackNotificationService._create_support_notifications(ticket)

    @staticmethod
    def _send_new_ticket_emails(ticket, settings_obj, request=None):
        """Envoie les emails de notification pour un nouveau ticket."""
        recipients = list(settings_obj.email_recipients.values_list("email", flat=True))
        if recipients:
            subject = f"[Feedback] Nouveau ticket : {ticket.title}"
            
            # Construire l'URL du ticket
            ticket_url = reverse('feedback:ticket_detail', kwargs={'pk': ticket.pk})
            if request:
                ticket_absolute_url = request.build_absolute_uri(ticket_url)
            else:
                from django.conf import settings
                ticket_absolute_url = f"{settings.SITE_URL}{ticket_url}"
            
            message = f"""
Un nouveau ticket a été créé :

Titre : {ticket.title}
Type : {ticket.get_ticket_type_display()}
Priorité : {ticket.get_priority_display()}
Créé par : {ticket.created_by.get_full_name() or ticket.created_by.email}

Description :
{ticket.description}

Voir le ticket : {ticket_absolute_url}
            """
            from_email = settings_obj.from_email or None
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=True,
            )

    @staticmethod
    def _create_support_notifications(ticket):
        """Crée des notifications in-app pour les utilisateurs support."""
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

    @staticmethod
    def notify_status_changed(ticket, request=None):
        """Notifie le créateur quand le statut d'un ticket change.
        
        Args:
            ticket: Le FeedbackTicket modifié
            request: La requête HTTP (optionnel, pour construire les URLs absolues)
        """
        settings_obj = FeedbackSettings.get_settings()

        if settings_obj.notify_on_status_change:
            # Notification in-app
            FeedbackNotificationService._create_status_notification(ticket)
            
            # Email au créateur
            FeedbackNotificationService._send_status_email(ticket, settings_obj, request)

    @staticmethod
    def _create_status_notification(ticket):
        """Crée une notification in-app pour le changement de statut."""
        Notification.objects.create(
            user=ticket.created_by,
            notification_type="feedback_status_changed",
            title=f"Mise à jour de votre ticket : {ticket.title}",
            message=f"Le statut de votre ticket est passé à '{ticket.get_status_display()}'.",
            link=reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk}),
        )

    @staticmethod
    def _send_status_email(ticket, settings_obj, request=None):
        """Envoie un email de notification pour le changement de statut."""
        if ticket.created_by.email:
            # Construire l'URL du ticket
            ticket_url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
            if request:
                ticket_absolute_url = request.build_absolute_uri(ticket_url)
            else:
                from django.conf import settings
                ticket_absolute_url = f"{settings.SITE_URL}{ticket_url}"
            
            subject = f"[Feedback] Mise à jour de votre ticket : {ticket.title}"
            message = f"""
Bonjour,

Le statut de votre ticket a été mis à jour :

Titre : {ticket.title}
Nouveau statut : {ticket.get_status_display()}

Voir le ticket : {ticket_absolute_url}

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
