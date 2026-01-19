from django import forms

from .models import Botijao


class BotijaoForm(forms.ModelForm):
    class Meta:
        model = Botijao
        fields = [
            "tag_rfid",
            "fabricante",
            "numero_serie",
            "tara",
            "data_ultima_requalificacao",
            "data_proxima_requalificacao",
            "penultima_envasadora",
            "data_penultimo_envasamento",
            "ultima_envasadora",
            "data_ultimo_envasamento",
        ]

        widgets = {
            "tag_rfid": forms.TextInput(attrs={"class": "form-control"}),
            "fabricante": forms.TextInput(attrs={"class": "form-control"}),
            "numero_serie": forms.TextInput(attrs={"class": "form-control"}),
            "tara": forms.NumberInput(attrs={"class": "form-control"}),
            "data_ultima_requalificacao": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "data_proxima_requalificacao": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "penultima_envasadora": forms.TextInput(attrs={"class": "form-control"}),
            "data_penultimo_envasamento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "ultima_envasadora": forms.TextInput(attrs={"class": "form-control"}),
            "data_ultimo_envasamento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
