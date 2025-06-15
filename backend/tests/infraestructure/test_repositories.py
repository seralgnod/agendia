from uuid import uuid4
from datetime import time
from agendia.core.domain import Profissional, Servico
from agendia.infrastructure.repositories import SQLiteProfissionalRepositorio

def test_salvar_e_buscar_profissional(db_session):
    """
    Testa se é possível salvar um profissional no banco de dados e depois
    buscá-lo, verificando se os dados são consistentes.
    """
    # ARRANGE (Preparação)
    repositorio = SQLiteProfissionalRepositorio(session=db_session)
    
    # Cria um objeto de domínio complexo
    id_profissional = uuid4()
    servico_domain = Servico(nome="Massagem Relaxante", duracao_minutos=60)
    profissional_domain = Profissional(
        id=id_profissional,
        nome="Terapeuta Zen",
        servicos_oferecidos=[servico_domain],
        horario_trabalho={1: (time(10, 0), time(19, 0))} # Trabalha às terças
    )

    # ACT (Ação)
    # Salva o profissional no banco de dados
    repositorio.salvar(profissional_domain)

    # Busca o mesmo profissional pelo ID
    profissional_recuperado = repositorio.buscar_por_id(id_profissional)

    # ASSERT (Verificação)
    assert profissional_recuperado is not None
    assert profissional_recuperado.id == id_profissional
    assert profissional_recuperado.nome == "Terapeuta Zen"
    assert len(profissional_recuperado.servicos_oferecidos) == 1
    assert profissional_recuperado.servicos_oferecidos[0].nome == "Massagem Relaxante"
    assert profissional_recuperado.horario_trabalho[1][0] == time(10, 0)