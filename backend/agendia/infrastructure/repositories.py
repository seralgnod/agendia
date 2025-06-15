import uuid
from datetime import time
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from agendia.application.ports import IProfissionalRepositorio
from agendia.core.domain import Profissional, Servico, Agendamento
from .models import ProfissionalDB, ServicoDB, AgendamentoDB

class SQLiteProfissionalRepositorio(IProfissionalRepositorio):
    """Implementação concreta do repositório para SQLAlchemy com SQLite."""

    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, profissional_db: ProfissionalDB) -> Profissional | None:
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
            telefone_whatsapp=profissional_db.telefone_whatsapp,
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

        # Mapeia os campos simples
        profissional_db.nome = profissional.nome
        profissional_db.telefone_whatsapp = profissional.telefone_whatsapp
        profissional_db.horario_trabalho = {
            day: (start.isoformat(), end.isoformat())
            for day, (start, end) in profissional.horario_trabalho.items()
        }
        
        # Mapeia relacionamentos
        # Limpa listas para sincronizar com o estado atual do objeto de domínio
        profissional_db.servicos_oferecidos.clear()
        
        for servico_domain in profissional.servicos_oferecidos:
            servico_db = self.session.query(ServicoDB).filter_by(nome=servico_domain.nome).first()
            if not servico_db:
                servico_db = ServicoDB(id=uuid.uuid4(), nome=servico_domain.nome, duracao_minutos=servico_domain.duracao_minutos)
                self.session.add(servico_db)
            profissional_db.servicos_oferecidos.append(servico_db)
        
        self.session.commit()

    def buscar_por_id(self, id_profissional: UUID) -> Profissional | None:
        profissional_db = (self.session.query(ProfissionalDB)
                           .options(
                               joinedload(ProfissionalDB.servicos_oferecidos), 
                               joinedload(ProfissionalDB.agendamentos).joinedload(AgendamentoDB.servico)
                            )
                           .filter_by(id=id_profissional).first())
        return self._to_domain(profissional_db)
    
    def buscar_por_telefone(self, telefone: str) -> Profissional | None:
        profissional_db = (self.session.query(ProfissionalDB)
                           .options(
                               joinedload(ProfissionalDB.servicos_oferecidos), 
                               joinedload(ProfissionalDB.agendamentos).joinedload(AgendamentoDB.servico)
                            )
                           .filter_by(telefone_whatsapp=telefone).first())
        return self._to_domain(profissional_db)