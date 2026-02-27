"""Formulaire de création/édition d'un événement."""

from django import forms
from django.core.exceptions import ValidationError

from events.models import Event, Sector
from events.widgets import ColoredCheckboxSelectMultiple


class EventForm(forms.ModelForm):
    """Formulaire de création/édition d'un événement."""

    sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.filter(is_active=True),
        widget=ColoredCheckboxSelectMultiple,
        label="Secteurs",
        required=True,
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "location",
            "city",
            "start_datetime",
            "end_datetime",
            "sectors",
            "comm_before",
            "comm_during",
            "comm_after",
            "needs_filming",
            "needs_poster",
            "notify_on_publish",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Titre de l'événement"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Description détaillée de l'événement",
                }
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Salle polyvalente"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Saint-Quentin"}
            ),
            "start_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "comm_before": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comm_during": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comm_after": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "needs_filming": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "needs_poster": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notify_on_publish": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "title": "Titre",
            "description": "Description",
            "location": "Lieu",
            "city": "Ville",
            "start_datetime": "Date et heure de début",
            "end_datetime": "Date et heure de fin",
            "sectors": "Secteurs",
            "comm_before": "Communication avant l'événement",
            "comm_during": "Communication pendant l'événement",
            "comm_after": "Communication après l'événement",
            "needs_filming": "Intervention pour filmer",
            "needs_poster": "Demande d'affiche",
            "notify_on_publish": "Recevoir un email lors de la confirmation de la publication",
        }

    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec uniquement les secteurs actifs."""
        super().__init__(*args, **kwargs)
        # Le queryset est déjà défini dans la déclaration du champ
        # mais on le met à jour ici pour être sûr d'avoir les données fraîches
        self.fields["sectors"].queryset = Sector.objects.filter(is_active=True)

        # Rendre les champs datetime cachés dans le template
        self.fields["start_datetime"].widget = forms.HiddenInput()
        self.fields["end_datetime"].widget = forms.HiddenInput()

    def clean(self):
        """Valide que la date de fin est postérieure à la date de début."""
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get("start_datetime")
        end_datetime = cleaned_data.get("end_datetime")

        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                raise ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )

        # Note: La validation "événement dans le passé" est retirée car elle cause
        # des problèmes lors de la soumission (l'heure peut changer entre le
        # chargement du formulaire et la soumission)

        return cleaned_data
