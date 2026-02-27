"""Formulaire pour la configuration de la récurrence des événements."""

from django import forms
from django.core.exceptions import ValidationError

from events.models import EventRecurrence


class EventRecurrenceForm(forms.ModelForm):
    """Formulaire de configuration de la récurrence d'un événement."""

    class Meta:
        model = EventRecurrence
        fields = [
            "recurrence_type",
            "interval",
            "end_date",
            "days_of_week",
            "day_of_month",
            "month_of_year",
            "max_occurrences",
        ]
        widgets = {
            "recurrence_type": forms.Select(attrs={"class": "form-control"}),
            "interval": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 365,
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "days_of_week": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: 0,2,4 pour Lun,Mer,Ven",
                }
            ),
            "day_of_month": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 31,
                }
            ),
            "month_of_year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 12,
                }
            ),
            "max_occurrences": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 100,
                }
            ),
        }
        labels = {
            "recurrence_type": "Type de récurrence",
            "interval": "Intervalle",
            "end_date": "Date de fin",
            "days_of_week": "Jours de la semaine",
            "day_of_month": "Jour du mois",
            "month_of_year": "Mois de l'année",
            "max_occurrences": "Nombre max d'occurrences",
        }
        help_texts = {
            "days_of_week": "Pour hebdomadaire: 0=Lundi, 1=Mardi, etc. Ex: 0,2,4",
            "day_of_month": "Pour mensuel: jour du mois (1-31)",
            "month_of_year": "Pour annuel: mois (1-12)",
        }

    def clean_days_of_week(self):
        """Valide le format des jours de la semaine."""
        days = self.cleaned_data.get("days_of_week")
        if days:
            try:
                day_list = [int(d.strip()) for d in days.split(",")]
                if not all(0 <= d <= 6 for d in day_list):
                    raise ValidationError(
                        "Les jours doivent être entre 0 (Lundi) et 6 (Dimanche)."
                    )
                return ",".join(str(d) for d in day_list)
            except ValueError:
                raise ValidationError(
                    "Format invalide. Utilisez des chiffres séparés par des virgules."
                )
        return days

    def clean(self):
        """Valide la cohérence des données."""
        cleaned_data = super().clean()
        recurrence_type = cleaned_data.get("recurrence_type")
        days_of_week = cleaned_data.get("days_of_week")
        day_of_month = cleaned_data.get("day_of_month")
        month_of_year = cleaned_data.get("month_of_year")

        if recurrence_type == "weekly" and not days_of_week:
            self.add_error(
                "days_of_week", "Veuillez spécifier au moins un jour de la semaine."
            )

        if recurrence_type == "monthly" and not day_of_month:
            self.add_error("day_of_month", "Veuillez spécifier le jour du mois.")

        if recurrence_type == "yearly" and not month_of_year:
            self.add_error("month_of_year", "Veuillez spécifier le mois de l'année.")

        return cleaned_data
