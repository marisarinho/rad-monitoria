from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import DuvidaForm
from .models import Duvida


@login_required
def lista_duvidas(request):
    usuario = request.user

    if usuario.groups.filter(name="Professor").exists():
        duvidas = Duvida.objects.all()

    elif usuario.groups.filter(name="Monitor").exists():
        duvidas = Duvida.objects.filter(
            disciplina__monitores=usuario
        ).distinct()

    else:
        duvidas = Duvida.objects.filter(
            autor=usuario
        )

    return render(
        request,
        "monitoria/lista_duvidas.html",
        {"duvidas": duvidas},
    )


class CriarDuvidaView(LoginRequiredMixin, CreateView):
    model = Duvida
    form_class = DuvidaForm
    template_name = "monitoria/criar_duvida.html"
    success_url = reverse_lazy("monitoria:lista_duvidas")

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.situacao = Duvida.Situacao.ABERTA

        return super().form_valid(form)