from datetime import datetime, date, time
from uuid import uuid4
import pytest

from agendia.core.domain import Profissional, Servico, Agendamento, AgendamentoStatus
from agendia.application.ports import IProfissionalRepositorio
from agendia.application.use_cases import (
    RealizarAgendamentoUseCase,
    ConsultarAgendaUseCase,
    AgendamentoInput,
    ConsultaAgendaInput,
    ProfissionalNaoEncontradoError,
    ServicoNaoEncontradoError,
)

# --- Testes para RealizarAgendamentoUseCase ---

def test_realizar_agendamento_com_sucesso(mocker):
    """
    Testa o fluxo feliz de um agendamento, garantindo que o repositório
    é chamado corretamente.
    """
    # 1. Setup (Preparação)
    id_profissional = uuid4()
    servico_corte = Servico(nome="Corte", duracao_minutos=30)
    
    # A data do agendamento (2025-01-01) é uma quarta-feira (weekday() == 2)
    profissional_existente = Profissional(
        id=id_profissional,
        nome="Dr. Teste",
        servicos_oferecidos=[servico_corte],
        # --- CORREÇÃO: Adicionado horário de trabalho para o profissional ---
        horario_trabalho={2: (time(9, 0), time(18, 0))}
    )
    
    mock_repo = mocker.Mock(spec=IProfissionalRepositorio)
    mock_repo.buscar_por_id.return_value = profissional_existente

    input_dto = AgendamentoInput(
        profissional_id=id_profissional,
        cliente_contato="cliente_feliz",
        nome_servico="Corte",
        data_hora_inicio=datetime(2025, 1, 1, 10, 0)
    )

    # 2. Execução
    use_case = RealizarAgendamentoUseCase(repositorio=mock_repo)
    novo_agendamento = use_case.executar(input_data=input_dto)

    # 3. Assert (Verificação)
    mock_repo.buscar_por_id.assert_called_once_with(id_profissional)
    mock_repo.salvar.assert_called_once_with(profissional_existente)
    
    assert len(profissional_existente.agendamentos) == 1
    assert profissional_existente.agendamentos[0].cliente_contato == "cliente_feliz"
    assert novo_agendamento is not None
    assert novo_agendamento.status == AgendamentoStatus.CONFIRMADO


def test_realizar_agendamento_falha_se_profissional_nao_existe(mocker):
    """Testa se uma exceção é levantada quando o profissional não é encontrado."""
    id_profissional_inexistente = uuid4()
    mock_repo = mocker.Mock(spec=IProfissionalRepositorio)
    mock_repo.buscar_por_id.return_value = None

    input_dto = AgendamentoInput(
        profissional_id=id_profissional_inexistente,
        cliente_contato="cliente_triste",
        nome_servico="Corte",
        data_hora_inicio=datetime(2025, 1, 1, 10, 0)
    )
    
    use_case = RealizarAgendamentoUseCase(repositorio=mock_repo)
    with pytest.raises(ProfissionalNaoEncontradoError):
        use_case.executar(input_data=input_dto)

    mock_repo.salvar.assert_not_called()


# --- Testes para ConsultarAgendaUseCase ---

def test_consultar_agenda_retorna_agendamentos_do_dia(mocker):
    """Testa se a consulta de agenda filtra e retorna os agendamentos corretos."""
    id_profissional = uuid4()
    servico = Servico(nome="Consulta", duracao_minutos=50)
    
    agendamento_hoje_1 = Agendamento(servico=servico, cliente_contato="A", data_hora_inicio=datetime(2025, 6, 8, 10, 0))
    agendamento_hoje_2 = Agendamento(servico=servico, cliente_contato="B", data_hora_inicio=datetime(2025, 6, 8, 14, 0))
    agendamento_amanha = Agendamento(servico=servico, cliente_contato="C", data_hora_inicio=datetime(2025, 6, 9, 11, 0))
    
    profissional_com_agenda = Profissional(
        id=id_profissional,
        nome="Dr. Agenda",
        agendamentos=[agendamento_hoje_1, agendamento_hoje_2, agendamento_amanha]
    )
    
    mock_repo = mocker.Mock(spec=IProfissionalRepositorio)
    mock_repo.buscar_por_id.return_value = profissional_com_agenda

    input_dto = ConsultaAgendaInput(
        profissional_id=id_profissional,
        data=date(2025, 6, 8)
    )
    
    use_case = ConsultarAgendaUseCase(repositorio=mock_repo)
    agenda_do_dia = use_case.executar(input_data=input_dto)
    
    mock_repo.buscar_por_id.assert_called_once_with(id_profissional)
    assert len(agenda_do_dia) == 2
    assert agenda_do_dia[0] == agendamento_hoje_1
    assert agenda_do_dia[1] == agendamento_hoje_2