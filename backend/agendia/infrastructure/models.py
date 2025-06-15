import uuid
from sqlalchemy import (Column, String, Integer, DateTime, Time, Enum as EnumSQL, 
                        ForeignKey, JSON, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID # Funciona bem com SQLite também

from .database import Base
from agendia.core.domain import AgendamentoStatus

# --- Modelos ORM (Tabelas do Banco de Dados) ---

# Tabela de associação para a relação muitos-para-muitos entre Profissional e Serviço
# (Um profissional pode ter muitos serviços, e no futuro um serviço pode ser reutilizado)
profissional_servico_association = Table('profissional_servico', Base.metadata,
    Column('profissional_id', UUID(as_uuid=True), ForeignKey('profissionais.id')),
    Column('servico_id', UUID(as_uuid=True), ForeignKey('servicos.id'))
)


class ProfissionalDB(Base):
    __tablename__ = "profissionais"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, index=True)
    horario_trabalho = Column(JSON) # Armazenaremos o dicionário de horários como JSON

    servicos_oferecidos = relationship("ServicoDB", secondary=profissional_servico_association)
    agendamentos = relationship("AgendamentoDB", back_populates="profissional", cascade="all, delete-orphan")


class ServicoDB(Base):
    __tablename__ = "servicos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, unique=True, index=True)
    duracao_minutos = Column(Integer)


class AgendamentoDB(Base):
    __tablename__ = "agendamentos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_contato = Column(String)
    data_hora_inicio = Column(DateTime)
    data_hora_fim = Column(DateTime)
    status = Column(EnumSQL(AgendamentoStatus))
    
    servico_id = Column(UUID(as_uuid=True), ForeignKey("servicos.id"))
    profissional_id = Column(UUID(as_uuid=True), ForeignKey("profissionais.id"))
    
    profissional = relationship("ProfissionalDB", back_populates="agendamentos")
    servico = relationship("ServicoDB")