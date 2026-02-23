"""Admin pour l'app pointage."""

from django.contrib import admin

from pointage.models import DailyTracking, SectionType, TrackingHistory


@admin.register(SectionType)
class SectionTypeAdmin(admin.ModelAdmin):
    """Admin pour les types de sections."""

    list_display = [
        "name",
        "order",
        "color_preview",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["order", "name"]

    def color_preview(self, obj):
        """Affiche un aperçu de la couleur."""
        return f'<div style="width: 20px; height: 20px; background-color: {obj.color}; border-radius: 3px; display: inline-block;"></div> {obj.color}'

    color_preview.short_description = "Couleur"
    color_preview.allow_tags = True


@admin.register(DailyTracking)
class DailyTrackingAdmin(admin.ModelAdmin):
    """Admin pour les pointages journaliers."""

    list_display = [
        "date",
        "section",
        "count",
        "updated_by",
        "updated_at",
    ]
    list_filter = ["date", "section", "created_at"]
    search_fields = ["section__name"]
    date_hierarchy = "date"
    ordering = ["-date", "section__order"]


@admin.register(TrackingHistory)
class TrackingHistoryAdmin(admin.ModelAdmin):
    """Admin pour l'historique des modifications."""

    list_display = [
        "tracking",
        "previous_count",
        "new_count",
        "modified_by",
        "modified_at",
    ]
    list_filter = ["modified_at", "tracking__section"]
    search_fields = ["tracking__section__name", "reason"]
    date_hierarchy = "modified_at"
    ordering = ["-modified_at"]
