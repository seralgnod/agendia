import uuid
from datetime import datetime, time, timedelta
from enum import Enum

from pydantic import BaseModel, Field, model_validator

# -----------------------------------------------------------------------------
# 1. ENUMS E TIPOS AUXILIARES
# -----------------------------------------------------------------------------

class AgendamentoStatus(str, Enum):
    """Define os status possíveis para um agendamento."""
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"
    CONCLUIDO = "Concluído"


# -----------------------------------------------------------------------------
# 2. ENTIDADES DO DOMÍNIO
# -----------------------------------------------------------------------------

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
    data_hora_fim: datetime | None = None  # Será calculado automaticamente
    cliente_contato: str  # Telefone ou ID do cliente
    status: AgendamentoStatus = Field(default=AgendamentoStatus.CONFIRMADO)

    @model_validator(mode='after')
    def calcular_data_hora_fim(self) -> 'Agendamento':
        """Calcula a data de término com base na duração do serviço."""
        if self.data_hora_inicio and self.servico:
            self.data_hora_fim = self.data_hora_inicio + timedelta(minutes=self.servico.duracao_minutos)
        return self

    def cancelar(self):
        """
        Altera o status do agendamento para Cancelado.
        REGRA: Não é possível cancelar um agendamento que já foi cancelado ou concluído.
        """
        if self.status in [AgendamentoStatus.CANCELADO, AgendamentoStatus.CONCLUIDO]:
            raise ValueError(f"Não é possível cancelar um agendamento com status '{self.status.value}'")
        self.status = AgendamentoStatus.CANCELADO

    def concluir(self):
        """
        Altera o status do agendamento para Concluído.
        REGRA: Apenas agendamentos confirmados podem ser concluídos.
        """
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
    servicos_oferecidos: list[Servico] = Field(default_factory=list)
    agendamentos: list[Agendamento] = Field(default_factory=list)
    # Horários de trabalho padrão (dia_da_semana: (inicio, fim))
    # Ex: {0: (time(9, 0), time(18, 0))} para Segunda das 9h às 18h
    horario_trabalho: dict[int, tuple[time, time]] = Field(default_factory=dict)

    def esta_disponivel(self, data_hora_desejada: datetime, duracao_servico: int) -> bool:
        """
        Verifica se um slot de tempo está disponível na agenda.
        REGRA 1: O horário deve estar dentro do horário de trabalho do profissional.
        REGRA 2: O horário não pode conflitar com agendamentos já confirmados.
        """
        dia_da_semana = data_hora_desejada.weekday()
        horario_desejado = data_hora_desejada.time()

        if dia_da_semana not in self.horario_trabalho:
            return False  # Não trabalha neste dia

        inicio_trabalho, fim_trabalho = self.horario_trabalho[dia_da_semana]
        if not (inicio_trabalho <= horario_desejado < fim_trabalho):
            return False  # Fora do horário de trabalho

        fim_horario_desejado = (data_hora_desejada + timedelta(minutes=duracao_servico))

        for agendamento in self.agendamentos:
            if agendamento.status == AgendamentoStatus.CONFIRMADO:
                # Lógica de sobreposição de horários
                if (max(agendamento.data_hora_inicio, data_hora_desejada) <
                        min(agendamento.data_hora_fim, fim_horario_desejado)):
                    return False  # Conflito encontrado

        return True  # Nenhum conflito, está disponível

    def adicionar_novo_agendamento(self, agendamento: Agendamento):
        """Adiciona um novo agendamento à lista, após validação de disponibilidade."""
        if not self.esta_disponivel(agendamento.data_hora_inicio, agendamento.servico.duracao_minutos):
            raise ValueError("Horário indisponível para este serviço.")

        self.agendamentos.append(agendamento)