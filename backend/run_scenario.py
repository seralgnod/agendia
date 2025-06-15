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
    
    agendamento_use_case = RealizarAgendamentoUseCase(
        repositorio=profissional_repo,
        whatsapp_adapter=whatsapp_adapter
    )

    # --- Preparação dos Dados (Arrange) ---
    print("2. Preparando dados iniciais...")
    
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!! DEFINA AQUI O NÚMERO DE WHATSAPP DO SEU NEGÓCIO           !!!!!
    # !!!!! (O número que você escaneou com o QR Code do whatsapp-adapter) !!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    numero_do_negocio = "+5583988918448" # <-- MUDE AQUI!

    servico_teste = Servico(nome="Manicure e Pedicure", duracao_minutos=90)
    id_profissional = uuid4()
    
    # Criamos o profissional com o novo campo obrigatório
    profissional = Profissional(
        id=id_profissional,
        nome="Salão Unhas de Ouro",
        telefone_whatsapp=numero_do_negocio, # <-- CAMPO ADICIONADO
        servicos_oferecidos=[servico_teste],
        horario_trabalho={
            # O dia do agendamento (16/06/2025) é uma Segunda-feira (weekday() == 0)
            0: (time(9, 0), time(18, 0)) 
        }
    )
    # Salva o profissional no banco para o teste
    profissional_repo.salvar(profissional)
    print(f"Profissional '{profissional.nome}' salvo no banco de dados.")

    # --- Dados para o Cenário de Teste (Act) ---
    print("3. Definindo dados do agendamento...")
    
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!! MUITO IMPORTANTE: ALTERE O NÚMERO ABAIXO PARA O SEU WHATSAPP !!!!!
    # !!!!! PESSOAL, para onde a notificação será enviada.              !!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    numero_do_cliente_para_teste = "+5583996230447" # <-- MUDE AQUI!

    dados_do_agendamento = AgendamentoInput(
        profissional_id=id_profissional,
        cliente_contato=numero_do_cliente_para_teste,
        nome_servico="Manicure e Pedicure",
        data_hora_inicio=datetime(2025, 6, 16, 14, 30) # Segunda-feira, às 14:30
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
    # Deleta e recria o banco de dados a cada execução para um teste limpo
    print("Limpando e recriando o banco de dados para o teste...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run_test_scenario()