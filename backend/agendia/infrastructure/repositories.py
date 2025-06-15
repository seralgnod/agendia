import uuid
from datetime import time
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from agendia.application.ports import IProfissionalRepositorio
from agendia.core.domain import Profissional, Servico, Agendamento, AgendamentoStatus
from .models import ProfissionalDB, ServicoDB, AgendamentoDB

class SQLiteProfissionalRepositorio(IProfissionalRepositorio):
    """Implementação concreta do repositório para SQLAlchemy com SQLite."""

    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, profissional_db: ProfissionalDB) -> Profissional:
        """Converte um modelo ORM para um modelo de domínio."""
        if not profissional_db:
            return None
            
        horario_trabalho_domain = {
            int(day): (time.fromisoformat(start), time.fromisoformat(end))
            for day, (start, end) in profissional_db.horario_trabalho.items()
        } if profissional_db.horario_trabalho else {}

        return Profissional(
            id=profissional_db.id,
            nome=profissional_db.nome,
            horario_trabalho=horario_trabalho_domain,
            servicos_oferecidos=[
                Servico(nome=s.nome, duracao_minutos=s.duracao_minutos)
                for s in profissional_db.servicos_oferecidos
            ],
            agendamentos=[
                Agendamento(
                    id=ag.id,
                    servico=Servico(nome=ag.servico.nome, duracao_minutos=ag.servico.duracao_minutos),
                    data_hora_inicio=ag.data_hora_inicio,
                    cliente_contato=ag.cliente_contato,
                    status=ag.status
                ) for ag in profissional_db.agendamentos
            ]
        )

    def salvar(self, profissional: Profissional) -> None:
        profissional_db = self.session.query(ProfissionalDB).filter_by(id=profissional.id).first()

        if not profissional_db:
            profissional_db = ProfissionalDB(id=profissional.id)
            self.session.add(profissional_db)

        profissional_db.nome = profissional.nome
        profissional_db.horario_trabalho = {
            day: (start.isoformat(), end.isoformat())
            for day, (start, end) in profissional.horario_trabalho.items()
        }
        
        # Lógica para sincronizar serviços (simplificada)
        # Em um app real, você não recriaria os serviços sempre
        profissional_db.servicos_oferecidos = []
        for servico_domain in profissional.servicos_oferecidos:
            servico_db = self.session.query(ServicoDB).filter_by(nome=servico_domain.nome).first()
            if not servico_db:
                servico_db = ServicoDB(
                    id=uuid.uuid4(), 
                    nome=servico_domain.nome, 
                    duracao_minutos=servico_domain.duracao_minutos
                )
                self.session.add(servico_db)
            profissional_db.servicos_oferecidos.append(servico_db)

        self.session.commit()

    def buscar_por_id(self, id_profissional: UUID) -> Profissional | None:
        profissional_db = (self.session.query(ProfissionalDB)
                        .options(joinedload(ProfissionalDB.servicos_oferecidos), 
                                    joinedload(ProfissionalDB.agendamentos).joinedload(AgendamentoDB.servico))
                        .filter_by(id=id_profissional).first())
        
        return self._to_domain(profissional_db)
    
    def buscar_por_contato(self, contato: str) -> Profissional | None:
        agendamento_db = self.session.query(AgendamentoDB).filter_by(cliente_contato=contato).first()
        if agendamento_db and agendamento_db.profissional:
            return self.buscar_por_id(agendamento_db.profissional.id)
        return None