from datetime import datetime, time
from uuid import uuid4

from agendia.core.domain import Profissional, Servico
from agendia.application.use_cases import RealizarAgendamentoUseCase, AgendamentoInput
from agendia.infrastructure.database import SessionLocal, Base, engine
from agendia.infrastructure.repositories import SQLiteProfissionalRepositorio
from agendia.infrastructure.whatsapp_adapter import PyWhatKitAdapter

def run_test_scenario():
    """
    Executa um cenário de ponta a ponta: cria um profissional, salva no banco,
    cria um agendamento e dispara uma notificação via WhatsApp.
    """
    print("--- INICIANDO CENÁRIO DE TESTE ---")

    # --- Configuração das Dependências ---
    print("1. Configurando dependências...")
    db_session = SessionLocal()
    whatsapp_adapter = PyWhatKitAdapter()
    profissional_repo = SQLiteProfissionalRepositorio(session=db_session)
    
    # Instancia o caso de uso com as implementações reais
    agendamento_use_case = RealizarAgendamentoUseCase(
        repositorio=profissional_repo,
        whatsapp_adapter=whatsapp_adapter
    )

    # --- Preparação dos Dados (Arrange) ---
    print("2. Preparando dados iniciais...")
    # Cria um profissional e o salva para que o caso de uso possa encontrá-lo
    servico_teste = Servico(nome="Consulta de Teste", duracao_minutos=45)
    id_profissional = uuid4()
    
    profissional = Profissional(
        id=id_profissional,
        nome="Dr. Fulano",
        servicos_oferecidos=[servico_teste],
        horario_trabalho={
            # O dia do agendamento (15/06/2025) é um Domingo (weekday() == 6)
            6: (time(9, 0), time(12, 0)) 
        }
    )
    # Salva o profissional no banco para o teste
    profissional_repo.salvar(profissional)
    print(f"Profissional '{profissional.nome}' salvo no banco de dados.")

    # --- Dados para o Cenário de Teste (Act) ---
    print("3. Definindo dados do agendamento...")
    
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!! MUITO IMPORTANTE: ALTERE O NÚMERO ABAIXO PARA O SEU WHATSAPP !!!!!
    # !!!!! O formato deve ser "+<codigo_do_pais><ddd><numero>"         !!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    numero_do_seu_whatsapp = "+5583988807803" # <-- MUDE AQUI!

    dados_do_agendamento = AgendamentoInput(
        profissional_id=id_profissional,
        cliente_contato=numero_do_seu_whatsapp,
        nome_servico="Consulta de Teste",
        data_hora_inicio=datetime(2025, 6, 15, 10, 0) # Domingo, às 10:00
    )

    # --- Execução do Caso de Uso ---
    print("4. Executando o caso de uso 'RealizarAgendamento'...")
    try:
        agendamento_criado = agendamento_use_case.executar(dados_do_agendamento)
        print("SUCESSO: Caso de uso executado.")
        print(f"Agendamento criado com ID: {agendamento_criado.id}")
        
    except Exception as e:
        print(f"ERRO: A execução do caso de uso falhou: {e}")
    finally:
        # --- Limpeza ---
        print("5. Fechando sessão com o banco de dados.")
        db_session.close()

    print("--- CENÁRIO DE TESTE CONCLUÍDO ---")


if __name__ == "__main__":
    # Cria as tabelas no banco de dados, se ainda não existirem
    Base.metadata.create_all(bind=engine)
    run_test_scenario()