# Caminho do arquivo: G:\Users\Donglares\Documents\PROJETO\Agendia\backend\main.py

import uvicorn
from fastapi import FastAPI

# Importe a Base e o engine do seu arquivo de database
from agendia.infrastructure.database import Base, engine

# Cria todas as tabelas no banco de dados (se não existirem)
# Em um cenário de produção, você usaria ferramentas de migração como Alembic
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AgendIA API",
    version="0.1.0",
    description="API para gerenciar o chatbot de agendamentos AgendIA"
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do AgendIA!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)