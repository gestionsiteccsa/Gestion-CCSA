"""Configuration de l'admin pour l'app events."""

from django.contrib import admin

from events.models import (
    Event,
    EventChangeLog,
    EventComment,
    EventDocument,
    EventImage,
    EventOccurrence,
    EventRecurrence,
    EventValidation,
    Sector,
)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    """Admin pour les secteurs."""

    list_display = ["name", "color_code", "is_active", "order"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    list_editable = ["order", "is_active"]


class EventImageInline(admin.TabularInline):
    """Inline pour les images d'un événement."""

    model = EventImage
    extra = 0
    readonly_fields = ["uploaded_at"]


class EventCommentInline(admin.TabularInline):
    """Inline pour les commentaires d'un événement."""

    model = EventComment
    extra = 0
    readonly_fields = ["author", "created_at"]


class EventChangeLogInline(admin.TabularInline):
    """Inline pour l'historique des modifications."""

    model = EventChangeLog
    extra = 0
    readonly_fields = [
        "changed_by",
        "field_name",
        "old_value",
        "new_value",
        "changed_at",
    ]
    can_delete = False


class EventDocumentInline(admin.TabularInline):
    """Inline pour les documents d'un événement."""

    model = EventDocument
    extra = 0
    readonly_fields = ["uploaded_at", "uploaded_by"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin pour les événements.

    Optimisation: Utilise list_select_related et prefetch_related
    pour éviter les requêtes N+1 dans la liste.
    """

    list_display = [
        "title",
        "display_sectors",
        "start_datetime",
        "city",
        "created_by",
        "is_active",
    ]
    list_filter = ["sectors", "is_active", "start_datetime", "city"]
    search_fields = ["title", "description", "location", "city"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    inlines = [
        EventImageInline,
        EventDocumentInline,
        EventCommentInline,
        EventChangeLogInline,
    ]
    date_hierarchy = "start_datetime"
    filter_horizontal = ["sectors"]

    # Optimisation: Précharger les relations ForeignKey
    list_select_related = ["created_by"]

    fieldsets = (
        (
            "Informations générales",
            {"fields": ("title", "slug", "description", "sectors")},
        ),
        (
            "Lieu et date",
            {"fields": ("location", "city", "start_datetime", "end_datetime")},
        ),
        ("Communication", {"fields": ("comm_before", "comm_during", "comm_after")}),
        ("Options", {"fields": ("needs_filming", "needs_poster")}),
        (
            "Métadonnées",
            {
                "fields": ("created_by", "is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        """Optimise la requête de liste avec prefetch_related."""
        queryset = super().get_queryset(request)
        # Précharger les secteurs pour éviter les requêtes N+1
        return queryset.prefetch_related("sectors")

    def display_sectors(self, obj):
        """Affiche les secteurs sous forme de liste.

        Optimisation: Utilise les secteurs préchargés par prefetch_related
        au lieu de faire une nouvelle requête.
        """
        return ", ".join([s.name for s in obj.sectors.all()])

    display_sectors.short_description = "Secteurs"


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    """Admin pour les images."""

    list_display = ["event", "order", "uploaded_at"]
    list_filter = ["uploaded_at"]
    search_fields = ["event__title"]


@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    """Admin pour les commentaires."""

    list_display = ["event", "author", "created_at", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["content", "event__title", "author__email"]


@admin.register(EventChangeLog)
class EventChangeLogAdmin(admin.ModelAdmin):
    """Admin pour l'historique."""

    list_display = ["event", "field_name", "changed_by", "changed_at"]
    list_filter = ["changed_at"]
    search_fields = ["event__title", "field_name"]
    readonly_fields = [
        "event",
        "changed_by",
        "field_name",
        "old_value",
        "new_value",
        "changed_at",
    ]


@admin.register(EventDocument)
class EventDocumentAdmin(admin.ModelAdmin):
    """Admin pour les documents."""

    list_display = [
        "title",
        "event",
        "document_type",
        "uploaded_by",
        "uploaded_at",
        "get_file_size_display",
    ]
    list_filter = ["document_type", "uploaded_at"]
    search_fields = ["title", "event__title", "uploaded_by__email"]
    readonly_fields = ["uploaded_at", "file_size", "document_type"]


@admin.register(EventRecurrence)
class EventRecurrenceAdmin(admin.ModelAdmin):
    """Admin pour les récurrences."""

    list_display = [
        "event",
        "recurrence_type",
        "interval",
        "end_date",
        "max_occurrences",
    ]
    list_filter = ["recurrence_type"]
    search_fields = ["event__title"]


@admin.register(EventOccurrence)
class EventOccurrenceAdmin(admin.ModelAdmin):
    """Admin pour les occurrences."""

    list_display = ["parent_event", "occurrence", "created_at"]
    search_fields = ["parent_event__title", "occurrence__title"]
    readonly_fields = ["created_at"]


@admin.register(EventValidation)
class EventValidationAdmin(admin.ModelAdmin):
    """Admin pour les validations."""

    list_display = ["event", "is_validated", "validated_by", "validated_at"]
    list_filter = ["is_validated", "validated_at"]
    search_fields = ["event__title", "validated_by__email", "notes"]
    readonly_fields = ["validated_at"]
