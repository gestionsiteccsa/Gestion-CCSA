"""Modèles pour la gestion des sauvegardes."""

import os
from datetime import datetime

from django.conf import settings
from django.db import models


class BackupConfiguration(models.Model):
    """Configuration des sauvegardes automatiques."""

    BACKUP_TYPE_CHOICES = [
        ('database', 'Base de données uniquement'),
        ('media', 'Dossier média uniquement'),
        ('full', 'Base de données + Média'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ]

    name = models.CharField(max_length=100, default='Configuration principale')
    backup_type = models.CharField(
        max_length=20,
        choices=BACKUP_TYPE_CHOICES,
        default='full',
        verbose_name='Type de sauvegarde'
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily',
        verbose_name='Fréquence'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    backup_directory = models.CharField(
        max_length=255,
        default='/home/noro8560/backup-gestionccsa',
        verbose_name='Dossier de sauvegarde'
    )
    keep_last_n = models.PositiveIntegerField(
        default=10,
        verbose_name='Conserver les N dernières sauvegardes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuration de sauvegarde'
        verbose_name_plural = 'Configurations de sauvegarde'

    def __str__(self):
        return f"{self.name} ({self.get_backup_type_display()})"


class BackupHistory(models.Model):
    """Historique des sauvegardes effectuées."""

    BACKUP_TYPE_CHOICES = [
        ('database', 'Base de données'),
        ('media', 'Dossier média'),
        ('full', 'Complète'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En cours'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
    ]

    TRIGGER_CHOICES = [
        ('manual', 'Manuel'),
        ('automatic', 'Automatique'),
    ]

    backup_type = models.CharField(
        max_length=20,
        choices=BACKUP_TYPE_CHOICES,
        verbose_name='Type de sauvegarde'
    )
    trigger = models.CharField(
        max_length=20,
        choices=TRIGGER_CHOICES,
        default='manual',
        verbose_name='Déclencheur'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Chemin du fichier'
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Taille du fichier (octets)'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Démarré à')
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Terminé à'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Message d\'erreur'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Historique de sauvegarde'
        verbose_name_plural = 'Historiques de sauvegarde'
        ordering = ['-started_at']

    def __str__(self):
        return f"Sauvegarde {self.get_backup_type_display()} - {self.started_at.strftime('%d/%m/%Y %H:%M')}"

    def get_file_size_display(self):
        """Retourne la taille du fichier en format lisible."""
        if self.file_size is None:
            return 'N/A'
        
        for unit in ['o', 'Ko', 'Mo', 'Go', 'To']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.2f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.2f} Po"

    def get_duration(self):
        """Calcule la durée de la sauvegarde."""
        if self.completed_at and self.started_at:
            duration = self.completed_at - self.started_at
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return 'N/A'
