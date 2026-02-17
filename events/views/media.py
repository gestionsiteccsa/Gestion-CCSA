"""Views pour la gestion des médias (images et documents)."""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from events.models import Event, EventDocument, EventImage

logger = logging.getLogger(__name__)


@login_required
@csrf_exempt  # Pour les requêtes AJAX, le token CSRF doit être vérifié côté client
@require_http_methods(["POST"])
def reorder_images(request, slug):
    """Réordonne les images d'un événement via AJAX."""
    event = get_object_or_404(Event, slug=slug, created_by=request.user)

    try:
        data = json.loads(request.body)
        image_order = data.get("order", [])

        # Validation du format des données
        if not isinstance(image_order, list):
            return JsonResponse(
                {"success": False, "error": "Le format doit être une liste"}, status=400
            )

        if not all(isinstance(x, int) for x in image_order):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Tous les éléments doivent être des entiers",
                },
                status=400,
            )

        # Vérifier que tous les IDs existent et appartiennent à l'événement
        existing_ids = set(
            EventImage.objects.filter(event=event).values_list("id", flat=True)
        )
        requested_ids = set(image_order)

        if not requested_ids.issubset(existing_ids):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Certains IDs d'images n'appartiennent pas à cet événement",
                },
                status=400,
            )

        # Mettre à jour l'ordre
        for index, image_id in enumerate(image_order):
            EventImage.objects.filter(id=image_id, event=event).update(order=index)

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        logger.warning("Tentative de reorder_images avec JSON invalide")
        return JsonResponse(
            {"success": False, "error": "Format JSON invalide"}, status=400
        )
    except ValidationError as e:
        logger.warning(f"Erreur de validation dans reorder_images: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Erreur inattendue dans reorder_images: {e}", exc_info=True)
        return JsonResponse(
            {"success": False, "error": "Une erreur interne est survenue"}, status=500
        )


@login_required
@require_http_methods(["POST"])
def delete_image(request, image_id):
    """Supprime une image d'un événement."""
    try:
        image = get_object_or_404(EventImage, id=image_id)
        event = image.event

        # Vérifier que l'utilisateur est le créateur
        if event.created_by != request.user:
            return JsonResponse(
                {"success": False, "error": "Permission refusée"}, status=403
            )

        image.delete()
        return JsonResponse({"success": True})

    except EventImage.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Image non trouvée"}, status=404
        )
    except Exception as e:
        logger.error(
            f"Erreur lors de la suppression d'image {image_id}: {e}", exc_info=True
        )
        return JsonResponse(
            {
                "success": False,
                "error": "Une erreur est survenue lors de la suppression",
            },
            status=500,
        )


@login_required
def delete_document(request, document_id):
    """Supprime un document d'un événement."""
    try:
        document = get_object_or_404(EventDocument, id=document_id)
        event = document.event

        # Vérifier que l'utilisateur est le créateur
        if event.created_by != request.user:
            from django.contrib import messages

            messages.error(
                request, "Vous n'avez pas la permission de supprimer ce document."
            )
            return redirect(event.get_absolute_url())

        document.delete()
        from django.contrib import messages

        messages.success(request, "Le document a été supprimé avec succès.")

    except EventDocument.DoesNotExist:
        from django.contrib import messages

        messages.error(request, "Document non trouvé.")
    except Exception as e:
        from django.contrib import messages

        logger.error(
            f"Erreur lors de la suppression du document {document_id}: {e}",
            exc_info=True,
        )
        messages.error(request, "Une erreur est survenue lors de la suppression.")

    return redirect(event.get_absolute_url())
