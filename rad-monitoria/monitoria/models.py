from django.db import models
from django.contrib.auth.models import User


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.IntegerField(unique=True)
    ativa = models.BooleanField(default=True)
    monitores = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.nome


class Duvida(models.Model):

    class Situacao(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        EM_ATENDIMENTO = "em_atendimento", "Em atendimento"
        RESPONDIDA = "respondida", "Respondida"
        ENCERRADA = "encerrada", "Encerrada"

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="duvidas",
    )

    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="duvidas_abertas",
    )

    monitor_responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="duvidas_assumidas",
        null=True,
        blank=True,
    )

    resposta = models.TextField(blank=True)

    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.ABERTA,
    )

    aberta_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo