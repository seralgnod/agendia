from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexão para o banco de dados SQLite.
# O arquivo 'agendia.db' será criado na raiz da pasta 'backend/'
DATABASE_URL = "sqlite:///./agendia.db"

# O 'engine' é o ponto de entrada principal para o SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    # 'connect_args' é necessário apenas para SQLite para permitir o uso em múltiplos threads
    connect_args={"check_same_thread": False}
)

# 'SessionLocal' é uma fábrica de sessões. Cada instância dela será uma sessão de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 'Base' é uma classe base da qual todos os nossos modelos ORM (tabelas) irão herdar.
Base = declarative_base()