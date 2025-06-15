import uuid
from sqlalchemy import (Column, String, Integer, DateTime, Enum as EnumSQL, 
                        ForeignKey, JSON, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base
from agendia.core.domain import AgendamentoStatus

# Tabela de associação para a relação de serviços de um profissional
profissional_servico_association = Table('profissional_servico', Base.metadata,
    Column('profissional_id', UUID(as_uuid=True), ForeignKey('profissionais.id')),
    Column('servico_id', UUID(as_uuid=True), ForeignKey('servicos.id'))
)

class ProfissionalDB(Base):
    __tablename__ = "profissionais"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, index=True)
    telefone_whatsapp = Column(String, unique=True, index=True)
    horario_trabalho = Column(JSON)

    # --- RELACIONAMENTOS CORRIGIDOS ---
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