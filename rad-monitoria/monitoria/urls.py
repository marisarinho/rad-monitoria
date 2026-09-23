from django.urls import path

from . import views


app_name = "monitoria"


urlpatterns = [

    path(
        "duvidas/",
        views.lista_duvidas,
        name="lista_duvidas",
    ),

    path(
        "duvidas/nova/",
        views.CriarDuvidaView.as_view(),
        name="criar_duvida",
    ),

    path(
        "duvidas/<int:pk>/",
        views.detalhe_duvida,
        name="detalhe_duvida",
    ),

    path(
        "duvidas/<int:pk>/assumir/",
        views.assumir_duvida,
        name="assumir_duvida",
    ),

    path(
        "duvidas/<int:pk>/responder/",
        views.responder_duvida,
        name="responder_duvida",
    ),

    path(
        "duvidas/<int:pk>/encerrar/",
        views.encerrar_duvida,
        name="encerrar_duvida",
    ),

    path(
        "base-conhecimento/",
        views.base_conhecimento,
        name="base_conhecimento",
    ),

    path(
        "contas/cadastro/",
        views.cadastro,
        name="cadastro",
    ),
]