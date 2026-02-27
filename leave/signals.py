"""Signaux pour l'app leave."""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import LeaveRequest, LeaveHistory


@receiver(post_save, sender=LeaveRequest)
def create_leave_history_on_save(sender, instance, created, **kwargs):
    """Crée un historique lors de la création ou modification d'une demande."""
    action = "created" if created else "updated"
    LeaveHistory.objects.create(
        leave_request=instance,
        action=action,
        changed_by=instance.user,
        new_data={
            "date": str(instance.date),
            "period": instance.period,
            "notes": instance.notes,
        },
    )


@receiver(pre_delete, sender=LeaveRequest)
def create_leave_history_on_delete(sender, instance, **kwargs):
    """Crée un historique lors de la suppression d'une demande."""
    LeaveHistory.objects.create(
        action="deleted",
        changed_by=instance.user,
        leave_request_info={
            "id": str(instance.id),
            "user": f"{instance.user.first_name} {instance.user.last_name}",
            "date": str(instance.date),
            "period": instance.period,
            "notes": instance.notes,
        },
    )
