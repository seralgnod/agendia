from datetime import datetime, time
import pytest

from agendia.core.domain import (
    Agendamento,
    AgendamentoStatus,
    Profissional,
    Servico,
)

# --- Testes para a Entidade Agendamento ---

def test_deve_criar_agendamento_e_calcular_hora_fim():
    """Verifica se a hora de fim é calculada corretamente na criação."""
    servico = Servico(nome="Teste", duracao_minutos=60)
    hora_inicio = datetime(2025, 1, 1, 10, 0)
    
    ag = Agendamento(servico=servico, data_hora_inicio=hora_inicio, cliente_contato="123")
    
    assert ag.status == AgendamentoStatus.CONFIRMADO
    assert ag.data_hora_fim == datetime(2025, 1, 1, 11, 0)

def test_deve_cancelar_agendamento_com_sucesso():
    """Verifica a lógica de cancelamento de um agendamento confirmado."""
    servico = Servico(nome="Teste", duracao_minutos=30)
    ag = Agendamento(servico=servico, data_hora_inicio=datetime.now(), cliente_contato="123")
    
    ag.cancelar()
    
    assert ag.status == AgendamentoStatus.CANCELADO

def test_nao_deve_cancelar_agendamento_ja_cancelado():
    """Verifica se uma exceção é levantada ao tentar cancelar um agendamento já cancelado."""
    servico = Servico(nome="Teste", duracao_minutos=30)
    ag = Agendamento(servico=servico, data_hora_inicio=datetime.now(), cliente_contato="123")
    ag.status = AgendamentoStatus.CANCELADO
    
    with pytest.raises(ValueError, match="Não é possível cancelar um agendamento com status 'Cancelado'"):
        ag.cancelar()

# --- Testes para a Entidade Profissional ---

@pytest.fixture
def profissional_exemplo() -> Profissional:
    """Cria uma instância de Profissional para ser usada nos testes."""
    corte = Servico(nome="Corte", duracao_minutos=30)
    prof = Profissional(
        nome="Dr. Teste",
        servicos_oferecidos=[corte],
        horario_trabalho={
            0: (time(9, 0), time(12, 0)), # Segunda-feira
        }
    )
    # Adiciona um agendamento existente para testar conflitos
    agendamento_existente = Agendamento(
        servico=corte,
        data_hora_inicio=datetime(2025, 6, 9, 10, 0), # Uma segunda-feira às 10:00
        cliente_contato="cliente_antigo"
    )
    prof.agendamentos.append(agendamento_existente)
    return prof


def test_profissional_deve_estar_disponivel(profissional_exemplo: Profissional):
    """Verifica um horário claramente livre."""
    horario_desejado = datetime(2025, 6, 9, 9, 0) # Segunda, 9:00
    assert profissional_exemplo.esta_disponivel(horario_desejado, 30) is True

def test_profissional_nao_deve_estar_disponivel_por_conflito(profissional_exemplo: Profissional):
    """Verifica um horário que conflita com um agendamento existente."""
    horario_desejado = datetime(2025, 6, 9, 10, 15) # Conflita com o agendamento das 10:00 às 10:30
    assert profissional_exemplo.esta_disponivel(horario_desejado, 30) is False

def test_profissional_nao_deve_estar_disponivel_fora_do_horario(profissional_exemplo: Profissional):
    """Verifica um horário fora do expediente."""
    horario_desejado = datetime(2025, 6, 9, 14, 0) # Segunda à tarde, não trabalha
    assert profissional_exemplo.esta_disponivel(horario_desejado, 30) is False

def test_adicionar_novo_agendamento_com_sucesso(profissional_exemplo: Profissional):
    """Testa a adição de um agendamento em horário vago."""
    novo_agendamento = Agendamento(
        servico=profissional_exemplo.servicos_oferecidos[0],
        data_hora_inicio=datetime(2025, 6, 9, 11, 0),
        cliente_contato="novo_cliente"
    )
    
    profissional_exemplo.adicionar_novo_agendamento(novo_agendamento)
    
    assert len(profissional_exemplo.agendamentos) == 2
    assert profissional_exemplo.agendamentos[1] == novo_agendamento

def test_nao_deve_adicionar_agendamento_em_horario_indisponivel(profissional_exemplo: Profissional):
    """Verifica se uma exceção é levantada ao tentar agendar em horário ocupado."""
    agendamento_conflitante = Agendamento(
        servico=profissional_exemplo.servicos_oferecidos[0],
        data_hora_inicio=datetime(2025, 6, 9, 10, 0), # Mesmo horário do existente
        cliente_contato="cliente_conflitante"
    )

    with pytest.raises(ValueError, match="Horário indisponível para este serviço."):
        profissional_exemplo.adicionar_novo_agendamento(agendamento_conflitante)