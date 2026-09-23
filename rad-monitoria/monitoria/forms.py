from django import forms

from .models import Disciplina, Duvida


class DuvidaForm(forms.ModelForm):
    class Meta:
        model = Duvida
        fields = ("titulo", "descricao", "disciplina")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["disciplina"].queryset = Disciplina.objects.filter(
            ativa=True
        )