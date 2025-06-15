import uuid
from datetime import datetime, time, timedelta
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class AgendamentoStatus(str, Enum):
    """Define os status possíveis para um agendamento."""
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"
    CONCLUIDO = "Concluído"


class Servico(BaseModel):
    """
    Representa um serviço oferecido pelo profissional.
    É um objeto de valor simples, definido por seu nome e duração.
    """
    nome: str = Field(..., min_length=3, description="Nome do serviço. Ex: Corte de Cabelo")
    duracao_minutos: int = Field(..., gt=0, description="Duração do serviço em minutos.")


class Agendamento(BaseModel):
    """
    Representa um agendamento na agenda de um profissional.
    Contém a lógica para gerenciar seu próprio ciclo de vida (cancelar, concluir).
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    servico: Servico
    data_hora_inicio: datetime
    data_hora_fim: datetime | None = None
    cliente_contato: str
    status: AgendamentoStatus = Field(default=AgendamentoStatus.CONFIRMADO)

    @model_validator(mode='after')
    def calcular_data_hora_fim(self) -> 'Agendamento':
        if self.data_hora_inicio and self.servico:
            self.data_hora_fim = self.data_hora_inicio + timedelta(minutes=self.servico.duracao_minutos)
        return self

    def cancelar(self):
        if self.status in [AgendamentoStatus.CANCELADO, AgendamentoStatus.CONCLUIDO]:
            raise ValueError(f"Não é possível cancelar um agendamento com status '{self.status.value}'")
        self.status = AgendamentoStatus.CANCELADO

    def concluir(self):
        if self.status != AgendamentoStatus.CONFIRMADO:
            raise ValueError("Apenas agendamentos confirmados podem ser concluídos.")
        self.status = AgendamentoStatus.CONCLUIDO


class Profissional(BaseModel):
    """
    Representa o profissional, que é a raiz de agregação principal.
    Ele gerencia sua lista de serviços e sua agenda de agendamentos.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    nome: str
    telefone_whatsapp: str  # <-- CAMPO CORRIGIDO/ADICIONADO
    servicos_oferecidos: list[Servico] = Field(default_factory=list)
    agendamentos: list[Agendamento] = Field(default_factory=list)
    horario_trabalho: dict[int, tuple[time, time]] = Field(default_factory=dict)

    def esta_disponivel(self, data_hora_desejada: datetime, duracao_servico: int) -> bool:
        dia_da_semana = data_hora_desejada.weekday()
        horario_desejado = data_hora_desejada.time()

        if dia_da_semana not in self.horario_trabalho:
            return False

        inicio_trabalho, fim_trabalho = self.horario_trabalho[dia_da_semana]
        if not (inicio_trabalho <= horario_desejado < fim_trabalho):
            return False

        fim_horario_desejado = (data_hora_desejada + timedelta(minutes=duracao_servico))

        for agendamento in self.agendamentos:
            if agendamento.status == AgendamentoStatus.CONFIRMADO:
                if (max(agendamento.data_hora_inicio, data_hora_desejada) <
                        min(agendamento.data_hora_fim, fim_horario_desejado)):
                    return False
        return True

    def adicionar_novo_agendamento(self, agendamento: Agendamento):
        if not self.esta_disponivel(agendamento.data_hora_inicio, agendamento.servico.duracao_minutos):
            raise ValueError("Horário indisponível para este serviço.")
        self.agendamentos.append(agendamento)