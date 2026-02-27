"""Formulaires pour la gestion des congés."""

from django import forms
from django.core.exceptions import ValidationError

from .models import LeaveCalendar, LeaveRequest


class LeaveCalendarForm(forms.ModelForm):
    """Formulaire de création/modification d'un calendrier de congés."""

    class Meta:
        model = LeaveCalendar
        fields = ["name", "description", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Ex: Vacances d'avril 2025",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Description optionnelle...",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                }
            ),
        }
        labels = {
            "name": "Nom du calendrier",
            "description": "Description",
            "start_date": "Date de début",
            "end_date": "Date de fin",
        }

    def clean(self):
        """Vérifie que la date de fin est postérieure à la date de début."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )

        return cleaned_data


class LeaveRequestForm(forms.ModelForm):
    """Formulaire de pose de congés."""

    selected_dates = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        label="Dates sélectionnées",
    )

    class Meta:
        model = LeaveRequest
        fields = ["period", "notes"]
        widgets = {
            "period": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white",
                },
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Notes optionnelles...",
                }
            ),
        }
        labels = {
            "period": "Période",
            "notes": "Notes",
        }

    def clean_selected_dates(self):
        """Valide et parse les dates sélectionnées."""
        dates_str = self.cleaned_data.get("selected_dates", "")
        if not dates_str:
            raise ValidationError("Veuillez sélectionner au moins une date.")

        dates_list = [d.strip() for d in dates_str.split(",") if d.strip()]
        if not dates_list:
            raise ValidationError("Veuillez sélectionner au moins une date.")

        return dates_list
