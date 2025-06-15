import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

# --- Importações da nossa aplicação ---
from agendia.config import settings
from agendia.infrastructure.database import SessionLocal, Base, engine
from agendia.infrastructure.whatsapp_adapter import PyWhatKitAdapter # Usaremos este como placeholder por enquanto
from agendia.infrastructure.repositories import SQLiteProfissionalRepositorio
from agendia.application.ports import IProfissionalRepositorio, IWhatsAppAdapter
from agendia.application.use_cases import (
    RealizarAgendamentoUseCase, AgendamentoInput, ProfissionalNaoEncontradoError, ValueError
)

# --- Criação das Tabelas ---
Base.metadata.create_all(bind=engine)

# --- Instância do FastAPI ---
app = FastAPI(
    title="AgendIA API",
    version="0.1.0",
)

# =============================================================================
# INJEÇÃO DE DEPENDÊNCIA (Dependency Injection)
# =============================================================================

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_profissional_repositorio(db: Session = Depends(get_db_session)) -> IProfissionalRepositorio:
    return SQLiteProfissionalRepositorio(session=db)

# Por enquanto, nosso adaptador de notificação será o PyWhatKit. 
# Podemos trocá-lo facilmente no futuro sem alterar o resto do código.
def get_whatsapp_adapter() -> IWhatsAppAdapter:
    return PyWhatKitAdapter()

# =============================================================================
# ENDPOINTS DA API (CAMADA DE APRESENTAÇÃO)
# =============================================================================

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do AgendIA!"}

@app.post("/agendamentos/", status_code=201)
def criar_agendamento(
    input_data: AgendamentoInput,
    # Injeta nossas dependências na rota
    repo: IProfissionalRepositorio = Depends(get_profissional_repositorio),
    adapter: IWhatsAppAdapter = Depends(get_whatsapp_adapter)
):
    """
    Endpoint para criar um novo agendamento.
    Recebe os dados do agendamento e executa o caso de uso correspondente.
    """
    try:
        # Instancia e executa o caso de uso
        use_case = RealizarAgendamentoUseCase(repositorio=repo, whatsapp_adapter=adapter)
        agendamento_criado = use_case.executar(input_data)
        
        # Retorna uma representação do agendamento criado (simplificado aqui)
        return {
            "id": agendamento_criado.id,
            "cliente_contato": agendamento_criado.cliente_contato,
            "data_hora_inicio": agendamento_criado.data_hora_inicio.isoformat()
        }
    except ProfissionalNaoEncontradoError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e: # Erro de horário indisponível do nosso domínio
        raise HTTPException(status_code=409, detail=str(e)) # 409 Conflict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {e}")

# --- Ponto de entrada ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)