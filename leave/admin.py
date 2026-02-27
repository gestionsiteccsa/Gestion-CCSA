"""Admin pour l'app leave."""

from django.contrib import admin

from .models import FrenchHoliday, LeaveCalendar, LeaveHistory, LeaveRequest


@admin.register(LeaveCalendar)
class LeaveCalendarAdmin(admin.ModelAdmin):
    """Admin pour les calendriers de congés."""

    list_display = (
        "name",
        "start_date",
        "end_date",
        "created_by",
        "is_active",
    )
    list_filter = ("is_active", "start_date")
    search_fields = ("name", "description")
    filter_horizontal = ("sectors",)
    date_hierarchy = "start_date"


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Admin pour les demandes de congés."""

    list_display = (
        "user",
        "calendar",
        "date",
        "period",
        "created_at",
    )
    list_filter = ("period", "date", "calendar")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    date_hierarchy = "date"


@admin.register(FrenchHoliday)
class FrenchHolidayAdmin(admin.ModelAdmin):
    """Admin pour les jours fériés français."""

    list_display = ("name", "date", "year", "is_active")
    list_filter = ("year", "is_active")
    search_fields = ("name",)
    date_hierarchy = "date"


@admin.register(LeaveHistory)
class LeaveHistoryAdmin(admin.ModelAdmin):
    """Admin pour l'historique des modifications."""

    list_display = (
        "leave_request",
        "action",
        "changed_by",
        "timestamp",
    )
    list_filter = ("action", "timestamp")
    readonly_fields = (
        "leave_request",
        "action",
        "changed_by",
        "old_data",
        "new_data",
        "timestamp",
    )
    date_hierarchy = "timestamp"
