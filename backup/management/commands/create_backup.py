"""Commande pour effectuer une sauvegarde de la base de données et/ou du dossier média."""

import gzip
import os
import shutil
import subprocess
import tarfile
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from backup.models import BackupConfiguration, BackupHistory


class Command(BaseCommand):
    """Commande pour créer une sauvegarde."""

    help = "Crée une sauvegarde de la base de données et/ou du dossier média"

    def add_arguments(self, parser):
        """Ajoute les arguments à la commande."""
        parser.add_argument(
            "--type",
            type=str,
            choices=["database", "media", "full"],
            default="full",
            help="Type de sauvegarde (database, media, full)",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="/home/noro8560/backup-gestionccsa",
            help="Dossier de sortie pour la sauvegarde",
        )
        parser.add_argument(
            "--auto",
            action="store_true",
            help="Indique que la sauvegarde est automatique (via cron)",
        )

    def handle(self, *args, **options):
        """Exécute la commande de sauvegarde."""
        backup_type = options["type"]
        output_dir = options["output"]
        is_auto = options["auto"]

        # Créer le dossier de sauvegarde s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)

        # Créer l'entrée dans l'historique
        history = BackupHistory.objects.create(
            backup_type=backup_type,
            trigger="automatic" if is_auto else "manual",
            status="pending",
        )

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_files = []

            if backup_type in ["database", "full"]:
                db_file = self._backup_database(output_dir, timestamp)
                backup_files.append(db_file)
                self.stdout.write(
                    self.style.SUCCESS(f"Base de données sauvegardée: {db_file}")
                )

            if backup_type in ["media", "full"]:
                media_file = self._backup_media(output_dir, timestamp)
                backup_files.append(media_file)
                self.stdout.write(
                    self.style.SUCCESS(f"Dossier média sauvegardé: {media_file}")
                )

            # Si full, créer une archive contenant les deux
            if backup_type == "full" and len(backup_files) == 2:
                final_file = self._create_full_archive(
                    output_dir, timestamp, backup_files
                )
                # Supprimer les fichiers intermédiaires
                for f in backup_files:
                    os.remove(f)
            else:
                final_file = backup_files[0]

            # Mettre à jour l'historique
            history.status = "success"
            history.file_path = final_file
            history.file_size = os.path.getsize(final_file)
            history.completed_at = timezone.now()
            history.save()

            # Nettoyer les vieilles sauvegardes
            self._cleanup_old_backups(output_dir)

            self.stdout.write(
                self.style.SUCCESS(f"Sauvegarde terminée avec succès: {final_file}")
            )

        except Exception as e:
            history.status = "failed"
            history.error_message = str(e)
            history.completed_at = timezone.now()
            history.save()
            raise CommandError(f"Erreur lors de la sauvegarde: {e}")

    def _backup_database(self, output_dir, timestamp):
        """Sauvegarde la base de données."""
        db_settings = settings.DATABASES["default"]
        db_engine = db_settings.get("ENGINE", "")

        if "postgresql" in db_engine:
            return self._backup_postgresql(db_settings, output_dir, timestamp)
        elif "sqlite" in db_engine:
            return self._backup_sqlite(db_settings, output_dir, timestamp)
        elif "mysql" in db_engine:
            return self._backup_mysql(db_settings, output_dir, timestamp)
        else:
            raise CommandError(f"Moteur de base de données non supporté: {db_engine}")

    def _backup_postgresql(self, db_settings, output_dir, timestamp):
        """Sauvegarde une base PostgreSQL."""
        db_name = db_settings.get("NAME")
        db_user = db_settings.get("USER")
        db_host = db_settings.get("HOST", "localhost")
        db_port = db_settings.get("PORT", "5432")
        db_password = db_settings.get("PASSWORD")

        output_file = os.path.join(output_dir, f"database_{timestamp}.sql.gz")

        # Définir le mot de passe dans l'environnement
        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password

        cmd = [
            "pg_dump",
            "-h",
            db_host,
            "-p",
            str(db_port),
            "-U",
            db_user,
            "-d",
            db_name,
            "--clean",
            "--if-exists",
        ]

        with gzip.open(output_file, "wb") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env)

        if result.returncode != 0:
            raise CommandError(f"pg_dump a échoué: {result.stderr.decode()}")

        return output_file

    def _backup_sqlite(self, db_settings, output_dir, timestamp):
        """Sauvegarde une base SQLite."""
        db_name = db_settings.get("NAME")
        output_file = os.path.join(output_dir, f"database_{timestamp}.sqlite3.gz")

        with open(db_name, "rb") as f_in:
            with gzip.open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        return output_file

    def _backup_mysql(self, db_settings, output_dir, timestamp):
        """Sauvegarde une base MySQL."""
        db_name = db_settings.get("NAME")
        db_user = db_settings.get("USER")
        db_host = db_settings.get("HOST", "localhost")
        db_port = db_settings.get("PORT", "3306")
        db_password = db_settings.get("PASSWORD")

        output_file = os.path.join(output_dir, f"database_{timestamp}.sql.gz")

        cmd = [
            "mysqldump",
            "-h",
            db_host,
            "-P",
            str(db_port),
            "-u",
            db_user,
            "--single-transaction",
            db_name,
        ]

        if db_password:
            cmd.insert(1, f"-p{db_password}")

        with gzip.open(output_file, "wb") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise CommandError(f"mysqldump a échoué: {result.stderr.decode()}")

        return output_file

    def _backup_media(self, output_dir, timestamp):
        """Sauvegarde le dossier média."""
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            # Créer un dossier média vide si inexistant
            os.makedirs(media_root, exist_ok=True)

        output_file = os.path.join(output_dir, f"media_{timestamp}.tar.gz")

        # Créer l'archive tar.gz
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(media_root, arcname="media")

        return output_file

    def _create_full_archive(self, output_dir, timestamp, files):
        """Crée une archive complète contenant DB et média."""
        import tarfile

        output_file = os.path.join(output_dir, f"full_backup_{timestamp}.tar.gz")

        with tarfile.open(output_file, "w:gz") as tar:
            for file_path in files:
                tar.add(file_path, arcname=os.path.basename(file_path))

        return output_file

    def _cleanup_old_backups(self, output_dir, keep_last=10):
        """Supprime les anciennes sauvegardes en gardant les N dernières."""
        # Récupérer la configuration
        try:
            config = BackupConfiguration.objects.first()
            if config:
                keep_last = config.keep_last_n
        except Exception:
            pass

        # Lister tous les fichiers de sauvegarde
        backup_files = []
        for filename in os.listdir(output_dir):
            if filename.endswith((".gz", ".tar.gz")):
                filepath = os.path.join(output_dir, filename)
                backup_files.append((filepath, os.path.getmtime(filepath)))

        # Trier par date de modification (du plus récent au plus ancien)
        backup_files.sort(key=lambda x: x[1], reverse=True)

        # Supprimer les fichiers excédentaires
        for filepath, _ in backup_files[keep_last:]:
            try:
                os.remove(filepath)
                self.stdout.write(f"Ancienne sauvegarde supprimée: {filepath}")
            except OSError:
                pass
