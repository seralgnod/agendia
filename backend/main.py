import uvicorn
from fastapi import FastAPI

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