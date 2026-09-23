from django.urls import path
from . import views

app_name = "monitoria"

urlpatterns = [
    path("duvidas/", views.lista_duvidas, name="lista_duvidas"),

    path(
        "duvidas/nova/",
        views.CriarDuvidaView.as_view(),
        name="criar_duvida",
    ),
]