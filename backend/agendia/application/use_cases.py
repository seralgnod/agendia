from datetime import datetime, time, date  # <--- CORREÇÃO: Importado 'date' aqui
from uuid import UUID

from pydantic import BaseModel, Field

from agendia.core.domain import Agendamento, Profissional, Servico
from agendia.application.ports import IProfissionalRepositorio

# =============================================================================
# DTOs (Data Transfer Objects) - Modelos de Entrada para os Casos de Uso
# =============================================================================

class AgendamentoInput(BaseModel):
    """Dados necessários para criar um novo agendamento."""
    profissional_id: UUID
    cliente_contato: str
    nome_servico: str
    data_hora_inicio: datetime

class ConsultaAgendaInput(BaseModel):
    """Dados para consultar a agenda de um profissional em uma data específica."""
    profissional_id: UUID
    data: date  # <--- CORREÇÃO: Alterado de 'datetime.date' para 'date'

# =============================================================================
# EXCEÇÕES CUSTOMIZADAS DA CAMADA DE APLICAÇÃO
# =============================================================================

class ProfissionalNaoEncontradoError(Exception):
    pass

class ServicoNaoEncontradoError(Exception):
    pass

class AgendamentoNaoEncontradoError(Exception):
    pass

# =============================================================================
# CASOS DE USO (Use Cases)
# =============================================================================

class RealizarAgendamentoUseCase:
    """Caso de uso para realizar um novo agendamento."""

    def __init__(self, repositorio: IProfissionalRepositorio):
        self.repositorio = repositorio

    def executar(self, input_data: AgendamentoInput) -> Agendamento:
        profissional = self.repositorio.buscar_por_id(input_data.profissional_id)
        if not profissional:
            raise ProfissionalNaoEncontradoError("Profissional não encontrado.")

        servico_encontrado = next(
            (s for s in profissional.servicos_oferecidos if s.nome == input_data.nome_servico),
            None
        )
        if not servico_encontrado:
            raise ServicoNaoEncontradoError(f"O serviço '{input_data.nome_servico}' não é oferecido.")

        novo_agendamento = Agendamento(
            servico=servico_encontrado,
            data_hora_inicio=input_data.data_hora_inicio,
            cliente_contato=input_data.cliente_contato
        )
        
        try:
            profissional.adicionar_novo_agendamento(novo_agendamento)
        except ValueError as e:
            raise e

        self.repositorio.salvar(profissional)
        return novo_agendamento

class ConsultarAgendaUseCase:
    """Caso de uso para consultar os agendamentos de um dia."""

    def __init__(self, repositorio: IProfissionalRepositorio):
        self.repositorio = repositorio

    def executar(self, input_data: ConsultaAgendaInput) -> list[Agendamento]:
        profissional = self.repositorio.buscar_por_id(input_data.profissional_id)
        if not profissional:
            raise ProfissionalNaoEncontradoError("Profissional não encontrado.")

        agenda_do_dia = [
            ag for ag in profissional.agendamentos
            if ag.data_hora_inicio.date() == input_data.data
        ]
        
        agenda_do_dia.sort(key=lambda ag: ag.data_hora_inicio)
        return agenda_do_dia