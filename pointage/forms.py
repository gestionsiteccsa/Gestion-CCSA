"""Formulaires pour l'app pointage."""

from django import forms

from pointage.models import DailyTracking, SectionType


class SectionTypeForm(forms.ModelForm):
    """Formulaire pour créer/modifier un type de section."""

    class Meta:
        model = SectionType
        fields = ["name", "description", "color", "order"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de la section",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Description (optionnel)",
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
        }


class DateSelectionForm(forms.Form):
    """Formulaire pour sélectionner une date."""

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        label="Date",
    )


class TrackingUpdateForm(forms.ModelForm):
    """Formulaire pour mettre à jour un pointage."""

    delta = forms.IntegerField(
        min_value=-5,
        max_value=5,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = DailyTracking
        fields = ["count"]
