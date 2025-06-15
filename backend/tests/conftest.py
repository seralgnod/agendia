import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agendia.infrastructure.database import Base

# Usa um banco de dados SQLite em memória para os testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Cria uma sessão de banco de dados limpa para cada teste.
    """
    # Cria todas as tabelas
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        # 'yield' entrega a sessão para o teste que a solicitou
        yield session
    finally:
        # Depois que o teste termina, limpa tudo
        session.close()
        # 'drop_all' remove todas as tabelas, garantindo que o próximo teste comece do zero
        Base.metadata.drop_all(bind=engine)