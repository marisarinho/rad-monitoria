from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

from .forms import DuvidaForm, RespostaForm
from .models import Duvida


def cadastro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            grupo_aluno, _ = Group.objects.get_or_create(
                name="Aluno"
            )

            usuario.groups.add(grupo_aluno)

            messages.success(
                request,
                "Cadastro realizado. Faça login.",
            )

            return redirect("login")

    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/cadastro.html",
        {"form": form},
    )


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

    success_url = reverse_lazy(
        "monitoria:lista_duvidas"
    )

    def form_valid(self, form):
        form.instance.autor = self.request.user

        form.instance.situacao = (
            Duvida.Situacao.ABERTA
        )

        return super().form_valid(form)


@login_required
def detalhe_duvida(request, pk):
    duvida = get_object_or_404(
        Duvida,
        pk=pk,
    )

    usuario = request.user

    eh_professor = usuario.groups.filter(
        name="Professor"
    ).exists()

    eh_monitor_disciplina = (
        usuario.groups.filter(name="Monitor").exists()
        and duvida.disciplina.monitores.filter(
            pk=usuario.pk
        ).exists()
    )

    eh_autor = duvida.autor == usuario

    if not (
        eh_professor
        or eh_monitor_disciplina
        or eh_autor
    ):
        raise PermissionDenied

    pode_assumir = (
        eh_monitor_disciplina
        and duvida.situacao == Duvida.Situacao.ABERTA
        and duvida.monitor_responsavel is None
    )

    pode_responder = (
        duvida.monitor_responsavel == usuario
        and duvida.situacao
        == Duvida.Situacao.EM_ATENDIMENTO
    )

    pode_encerrar = (
        eh_autor
        and duvida.situacao
        == Duvida.Situacao.RESPONDIDA
        and bool(duvida.resposta.strip())
    )

    resposta_form = RespostaForm(instance=duvida)

    return render(
        request,
        "monitoria/detalhe_duvida.html",
        {
            "duvida": duvida,
            "pode_assumir": pode_assumir,
            "pode_responder": pode_responder,
            "pode_encerrar": pode_encerrar,
            "resposta_form": resposta_form,
        },
    )


@login_required
@require_POST
def assumir_duvida(request, pk):
    with transaction.atomic():
        duvida = get_object_or_404(
            Duvida.objects.select_for_update(),
            pk=pk,
        )

        usuario = request.user

        eh_monitor = usuario.groups.filter(
            name="Monitor"
        ).exists()

        monitora_disciplina = (
            duvida.disciplina.monitores.filter(
                pk=usuario.pk
            ).exists()
        )

        if not eh_monitor or not monitora_disciplina:
            raise PermissionDenied

        if (
            duvida.situacao
            != Duvida.Situacao.ABERTA
            or duvida.monitor_responsavel is not None
        ):
            messages.error(
                request,
                "Esta dúvida não pode mais ser assumida.",
            )

            return redirect(
                "monitoria:detalhe_duvida",
                pk=duvida.pk,
            )

        duvida.monitor_responsavel = usuario

        duvida.situacao = (
            Duvida.Situacao.EM_ATENDIMENTO
        )

        duvida.save()

    messages.success(
        request,
        "Você assumiu esta dúvida.",
    )

    return redirect(
        "monitoria:detalhe_duvida",
        pk=duvida.pk,
    )


@login_required
@require_POST
def responder_duvida(request, pk):
    duvida = get_object_or_404(
        Duvida,
        pk=pk,
    )

    if duvida.monitor_responsavel != request.user:
        raise PermissionDenied

    if (
        duvida.situacao
        != Duvida.Situacao.EM_ATENDIMENTO
    ):
        messages.error(
            request,
            "Esta dúvida não pode ser respondida.",
        )

        return redirect(
            "monitoria:detalhe_duvida",
            pk=duvida.pk,
        )

    form = RespostaForm(
        request.POST,
        instance=duvida,
    )

    if form.is_valid():
        duvida = form.save(commit=False)

        duvida.situacao = (
            Duvida.Situacao.RESPONDIDA
        )

        duvida.save()

        messages.success(
            request,
            "Resposta registrada.",
        )

    else:
        messages.error(
            request,
            "A resposta não pode ficar em branco.",
        )

    return redirect(
        "monitoria:detalhe_duvida",
        pk=duvida.pk,
    )


@login_required
@require_POST
def encerrar_duvida(request, pk):
    duvida = get_object_or_404(
        Duvida,
        pk=pk,
    )

    if duvida.autor != request.user:
        raise PermissionDenied

    if (
        duvida.situacao
        != Duvida.Situacao.RESPONDIDA
        or not duvida.resposta.strip()
    ):
        messages.error(
            request,
            "A dúvida só pode ser encerrada após ser respondida.",
        )

        return redirect(
            "monitoria:detalhe_duvida",
            pk=duvida.pk,
        )

    duvida.situacao = (
        Duvida.Situacao.ENCERRADA
    )

    duvida.save()

    messages.success(
        request,
        "Dúvida encerrada.",
    )

    return redirect(
        "monitoria:detalhe_duvida",
        pk=duvida.pk,
    )


@login_required
def base_conhecimento(request):
    duvidas = Duvida.objects.filter(
        Q(situacao=Duvida.Situacao.RESPONDIDA)
        |
        Q(situacao=Duvida.Situacao.ENCERRADA)
    )

    termo = request.GET.get(
        "q",
        "",
    ).strip()

    if termo:
        duvidas = duvidas.filter(
            Q(titulo__icontains=termo)
            |
            Q(descricao__icontains=termo)
        )

    return render(
        request,
        "monitoria/base_conhecimento.html",
        {
            "duvidas": duvidas,
            "termo": termo,
        },
    )