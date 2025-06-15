import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import re

# --- Importações da nossa aplicação ---
from agendia.infrastructure.database import SessionLocal, Base, engine
from agendia.infrastructure.repositories import SQLiteProfissionalRepositorio
from agendia.application.ports import IProfissionalRepositorio
from agendia.application.use_cases import (
    ConsultarAgendaUseCase, ConsultaAgendaInput, ProfissionalNaoEncontradoError
)

# --- Criação das Tabelas ---
Base.metadata.create_all(bind=engine)

# --- Instância do FastAPI ---
app = FastAPI(title="AgendIA API", version="0.1.0")

# =============================================================================
# Modelos de Dados para a API (Entrada/Saída)
# =============================================================================
class WhatsappMessageIn(BaseModel):
    """Modelo para a mensagem recebida do webhook do Node.js."""
    sender: str
    text: str

class WebhookResponse(BaseModel):
    """Modelo para a resposta que nosso webhook enviará de volta ao adaptador."""
    reply: str

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

# =============================================================================
# ENDPOINTS DA API
# =============================================================================
@app.get("/")
def read_root():
    return {"message": "API do AgendIA no ar. Webhook em /webhook/whatsapp"}

@app.post("/webhook/whatsapp", response_model=WebhookResponse)
def whatsapp_webhook(
    payload: WhatsappMessageIn,
    repo: IProfissionalRepositorio = Depends(get_profissional_repositorio)
):
    """
    Recebe mensagens do adaptador Node.js, processa o comando e retorna
    uma resposta para ser enviada de volta ao usuário.
    """
    print(f"Webhook recebido de {payload.sender} com texto: '{payload.text}'")
    
    resposta_texto = ""
    mensagem_cliente = payload.text.lower()

    try:
        # --- LÓGICA DE PROCESSAMENTO DE COMANDOS ---
        # Por enquanto, uma lógica simples baseada em palavras-chave.
        
        if "agenda" in mensagem_cliente:
            # Identifica o profissional associado ao número de WhatsApp do remetente
            # A função buscar_por_contato é um placeholder, precisa ser implementada
            # profissional = repo.buscar_por_contato(payload.sender)
            # if profissional:
            #     # Lógica para chamar o ConsultarAgendaUseCase
            #     resposta_texto = "Aqui está sua agenda de hoje..."
            # else:
            #     resposta_texto = "Não encontrei seu cadastro."
            
            # Resposta temporária para teste
            resposta_texto = "Entendi que você quer ver a agenda! Esta função será implementada em breve. agenda"

        elif "marcar" in mensagem_cliente or "agendar" in mensagem_cliente:
            resposta_texto = "Entendi que você quer um novo agendamento! Em breve poderemos fazer isso por aqui."
        
        else:
            resposta_texto = "Olá! Sou o AgendIA. Ainda estou em desenvolvimento. Tente comandos como 'ver agenda' ou 'agendar'."

    except Exception as e:
        print(f"ERRO ao processar comando: {e}")
        resposta_texto = "Desculpe, ocorreu um erro interno e não consegui processar sua mensagem."

    # Retorna a resposta que o adaptador Node.js irá enviar ao usuário
    return WebhookResponse(reply=resposta_texto)