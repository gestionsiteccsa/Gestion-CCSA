"""Widgets personnalisés pour l'app events."""

from django import forms


class ColoredCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Widget de cases à cocher avec indicateur de couleur."""

    template_name = "events/widgets/colored_checkbox_select.html"
    option_template_name = "events/widgets/colored_checkbox_option.html"

    def get_context(self, name, value, attrs):
        """Ajoute les informations de couleur au contexte."""
        context = super().get_context(name, value, attrs)

        # Récupérer le queryset des secteurs
        queryset = None
        if hasattr(self, "choices") and hasattr(self.choices, "queryset"):
            queryset = self.choices.queryset

        # Stocker le queryset dans le contexte pour le template
        if queryset:
            context["sectors_queryset"] = queryset
            # Créer un dict des couleurs
            colors = {}
            for obj in queryset:
                if hasattr(obj, "color_code"):
                    colors[str(obj.pk)] = obj.color_code
            context["sector_colors"] = colors

            # Ajouter les couleurs aux options
            for group_name, group_options, index in context["widget"]["optgroups"]:
                for opt in group_options:
                    sector_id = str(opt["value"])
                    if sector_id in colors:
                        opt["attrs"]["data_color"] = colors[sector_id]

        return context
