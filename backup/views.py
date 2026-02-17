"""Vues pour la gestion des sauvegardes (superadmin uniquement)."""

import os
import shutil
from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from backup.models import BackupConfiguration, BackupHistory


def superuser_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est superadmin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden(
                "Accès réservé aux superadministrateurs."
            )
        return view_func(request, *args, **kwargs)
    return wrapper


@superuser_required
def backup_dashboard(request):
    """Page principale de gestion des sauvegardes."""
    # Récupérer ou créer la configuration
    config, created = BackupConfiguration.objects.get_or_create(
        defaults={
            'backup_directory': '/home/noro8560/backup-gestionccsa',
            'backup_type': 'full',
            'frequency': 'daily',
            'keep_last_n': 10
        }
    )

    # Historique des sauvegardes (20 dernières)
    history = BackupHistory.objects.all()[:20]

    # Vérifier l'espace disque disponible (cross-platform Windows/Linux/Mac)
    backup_dir = config.backup_directory
    disk_usage = None
    if os.path.exists(backup_dir):
        usage = shutil.disk_usage(backup_dir)
        disk_usage = {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
        }

    # Lister les fichiers de sauvegarde existants
    backup_files = []
    if os.path.exists(backup_dir):
        for filename in sorted(os.listdir(backup_dir), reverse=True):
            filepath = os.path.join(backup_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                backup_files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'path': filepath
                })

    context = {
        'config': config,
        'history': history,
        'disk_usage': disk_usage,
        'backup_files': backup_files[:10],  # 10 derniers fichiers
    }

    return render(request, 'backup/dashboard.html', context)


@superuser_required
@require_POST
def create_backup_ajax(request):
    """Crée une sauvegarde via AJAX."""
    import subprocess
    import sys

    backup_type = request.POST.get('type', 'full')

    # Créer l'entrée dans l'historique
    history = BackupHistory.objects.create(
        backup_type=backup_type,
        trigger='manual',
        status='pending',
        created_by=request.user
    )

    try:
        # Exécuter la commande de sauvegarde
        result = subprocess.run(
            [sys.executable, 'manage.py', 'create_backup', 
             '--type', backup_type],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )

        if result.returncode == 0:
            # Rafraîchir l'objet pour obtenir les mises à jour
            history.refresh_from_db()
            return JsonResponse({
                'success': True,
                'message': 'Sauvegarde créée avec succès',
                'history_id': history.id,
                'file_path': history.file_path,
                'file_size': history.get_file_size_display() if history.file_size else 'N/A'
            })
        else:
            history.status = 'failed'
            history.error_message = result.stderr
            history.completed_at = timezone.now()
            history.save()
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la sauvegarde: {result.stderr}'
            })

    except subprocess.TimeoutExpired:
        history.status = 'failed'
        history.error_message = 'Timeout - La sauvegarde a pris trop de temps'
        history.completed_at = timezone.now()
        history.save()
        return JsonResponse({
            'success': False,
            'message': 'La sauvegarde a pris trop de temps'
        })
    except Exception as e:
        history.status = 'failed'
        history.error_message = str(e)
        history.completed_at = timezone.now()
        history.save()
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@superuser_required
def download_backup(request, filename):
    """Télécharge un fichier de sauvegarde (superadmin uniquement)."""
    config = BackupConfiguration.objects.first()
    if not config:
        messages.error(request, "Configuration de sauvegarde introuvable.")
        return redirect('backup:dashboard')

    # Sécurité : vérifier que le filename ne contient pas de ..
    if '..' in filename or filename.startswith('/'):
        return HttpResponseForbidden("Nom de fichier invalide.")

    filepath = os.path.join(config.backup_directory, filename)

    if not os.path.exists(filepath):
        messages.error(request, "Fichier non trouvé.")
        return redirect('backup:dashboard')

    # Vérifier que le fichier est bien dans le dossier de sauvegarde
    real_path = os.path.realpath(filepath)
    real_backup_dir = os.path.realpath(config.backup_directory)
    if not real_path.startswith(real_backup_dir):
        return HttpResponseForbidden("Accès non autorisé.")

    response = FileResponse(
        open(filepath, 'rb'),
        as_attachment=True,
        filename=filename
    )
    return response


@superuser_required
@require_POST
def delete_backup(request, filename):
    """Supprime un fichier de sauvegarde."""
    config = BackupConfiguration.objects.first()
    if not config:
        return JsonResponse({
            'success': False,
            'message': 'Configuration introuvable'
        })

    # Sécurité
    if '..' in filename or filename.startswith('/'):
        return JsonResponse({
            'success': False,
            'message': 'Nom de fichier invalide'
        })

    filepath = os.path.join(config.backup_directory, filename)

    # Vérifier le chemin
    real_path = os.path.realpath(filepath)
    real_backup_dir = os.path.realpath(config.backup_directory)
    if not real_path.startswith(real_backup_dir):
        return JsonResponse({
            'success': False,
            'message': 'Accès non autorisé'
        })

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return JsonResponse({
                'success': True,
                'message': f'Fichier {filename} supprimé'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Fichier non trouvé'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@superuser_required
@require_POST
def update_config(request):
    """Met à jour la configuration des sauvegardes."""
    config = BackupConfiguration.objects.first()
    if not config:
        config = BackupConfiguration()

    config.backup_type = request.POST.get('backup_type', 'full')
    config.frequency = request.POST.get('frequency', 'daily')
    config.backup_directory = request.POST.get(
        'backup_directory', 
        '/home/noro8560/backup-gestionccsa'
    )
    config.keep_last_n = int(request.POST.get('keep_last_n', 10))
    config.is_active = request.POST.get('is_active') == 'on'
    config.save()

    messages.success(request, "Configuration mise à jour avec succès.")
    return redirect('backup:dashboard')
