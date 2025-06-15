import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List # <-- IMPORTAR List

# ... (outros imports inalterados) ...
from agendia.config import settings
from agendia.infrastructure.database import SessionLocal, Base, engine
from agendia.infrastructure.whatsapp_adapter import PyWhatKitAdapter
from agendia.infrastructure.repositories import SQLiteProfissionalRepositorio
from agendia.application.ports import IProfissionalRepositorio, IWhatsAppAdapter
from agendia.application.use_cases import (
    RealizarAgendamentoUseCase, AgendamentoInput, ProfissionalNaoEncontradoError
)
from pydantic import BaseModel
from typing import Optional

class ProfissionalCreate(BaseModel):
    nome: str
    telefone_whatsapp: str

class ProfissionalPublic(BaseModel):
    id: UUID
    nome: str
    telefone_whatsapp: str
    class Config:
        from_attributes = True

# ... (código de setup inalterado) ...
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AgendIA API", version="0.1.0")
def get_db_session():
    # ...
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_profissional_repositorio(db: Session = Depends(get_db_session)) -> IProfissionalRepositorio:
    return SQLiteProfissionalRepositorio(session=db)
def get_whatsapp_adapter() -> IWhatsAppAdapter:
    return PyWhatKitAdapter()


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do AgendIA!"}

# --- NOVO ENDPOINT ADICIONADO ---
@app.get("/profissionais/", response_model=List[ProfissionalPublic])
def listar_todos_os_profissionais(
    repo: IProfissionalRepositorio = Depends(get_profissional_repositorio)
):
    """
    Retorna uma lista de todos os profissionais cadastrados no sistema.
    """
    return repo.listar_todos()


@app.post("/profissionais/", response_model=ProfissionalPublic, status_code=status.HTTP_201_CREATED)
def criar_profissional(
    profissional_in: ProfissionalCreate,
    repo: IProfissionalRepositorio = Depends(get_profissional_repositorio)
):
    # ... (código do criar_profissional inalterado) ...
    print(f"Recebida requisição para criar profissional: {profissional_in.nome}")
    db_profissional = repo.buscar_por_telefone(profissional_in.telefone_whatsapp)
    if db_profissional:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Um profissional com este número de WhatsApp já existe.")
    from agendia.core.domain import Profissional
    novo_profissional = Profissional(**profissional_in.model_dump())
    repo.salvar(novo_profissional)
    print(f"Profissional '{novo_profissional.nome}' criado com sucesso.")
    return novo_profissional

@app.post("/agendamentos/", status_code=status.HTTP_201_CREATED)
def criar_agendamento(
    input_data: AgendamentoInput,
    repo: IProfissionalRepositorio = Depends(get_profissional_repositorio),
    adapter: IWhatsAppAdapter = Depends(get_whatsapp_adapter)
):
    # ... (código do criar_agendamento inalterado) ...
    try:
        use_case = RealizarAgendamentoUseCase(repositorio=repo, whatsapp_adapter=adapter)
        agendamento_criado = use_case.executar(input_data)
        return {"id": agendamento_criado.id, "cliente_contato": agendamento_criado.cliente_contato, "data_hora_inicio": agendamento_criado.data_hora_inicio.isoformat()}
    except ProfissionalNaoEncontradoError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)