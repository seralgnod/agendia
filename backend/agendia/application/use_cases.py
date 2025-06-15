from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field

from agendia.core.domain import Agendamento, Profissional, Servico
from agendia.application.ports import IProfissionalRepositorio, IWhatsAppAdapter # <--- Adicionada a nova interface

# ... (DTOs e Exceções permanecem os mesmos) ...

class AgendamentoInput(BaseModel):
    profissional_id: UUID
    cliente_contato: str
    nome_servico: str
    data_hora_inicio: datetime

class ConsultaAgendaInput(BaseModel):
    profissional_id: UUID
    data: date

class ProfissionalNaoEncontradoError(Exception): pass
class ServicoNaoEncontradoError(Exception): pass
class AgendamentoNaoEncontradoError(Exception): pass


# --- Caso de Uso Modificado ---

class RealizarAgendamentoUseCase:
    """Caso de uso para realizar um novo agendamento."""

    # CORREÇÃO: Agora ele recebe também o adaptador de WhatsApp
    def __init__(self, repositorio: IProfissionalRepositorio, whatsapp_adapter: IWhatsAppAdapter):
        self.repositorio = repositorio
        self.whatsapp_adapter = whatsapp_adapter

    def executar(self, input_data: AgendamentoInput) -> Agendamento:
        profissional = self.repositorio.buscar_por_id(input_data.profissional_id)
        if not profissional:
            raise ProfissionalNaoEncontradoError("Profissional não encontrado.")

        servico_encontrado = next(
            (s for s in profissional.servicos_oferecidos if s.nome == input_data.nome_servico), 
            None
        )
        if not servico_encontrado:
            raise ServicoNaoEncontradoError(f"O serviço '{input_data.nome_servico}' não é oferecido.")

        novo_agendamento = Agendamento(
            servico=servico_encontrado,
            data_hora_inicio=input_data.data_hora_inicio,
            cliente_contato=input_data.cliente_contato
        )

        try:
            profissional.adicionar_novo_agendamento(novo_agendamento)
        except ValueError as e:
            raise e

        self.repositorio.salvar(profissional)
        
        # --- NOVA ETAPA: Enviar notificação de confirmação ---
        try:
            texto_confirmacao = (
                f"Olá! ✅ Seu agendamento para o serviço '{servico_encontrado.nome}' "
                f"com {profissional.nome} foi confirmado para o dia "
                f"{novo_agendamento.data_hora_inicio.strftime('%d/%m/%Y às %H:%M')}."
            )
            self.whatsapp_adapter.enviar_texto(
                numero_destino=input_data.cliente_contato,
                texto=texto_confirmacao
            )
        except Exception as e:
            # Mesmo que a notificação falhe, o agendamento foi salvo.
            # Apenas registramos o erro.
            print(f"AVISO: O agendamento foi salvo, mas a notificação via WhatsApp falhou: {e}")

        return novo_agendamento

# ... (ConsultarAgendaUseCase permanece o mesmo) ...

class ConsultarAgendaUseCase:
    def __init__(self, repositorio: IProfissionalRepositorio):
        self.repositorio = repositorio

    def executar(self, input_data: ConsultaAgendaInput) -> list[Agendamento]:
        # ... (código inalterado) ...
        profissional = self.repositorio.buscar_por_id(input_data.profissional_id)
        if not profissional:
            raise ProfissionalNaoEncontradoError("Profissional não encontrado.")
        agenda_do_dia = [
            ag for ag in profissional.agendamentos
            if ag.data_hora_inicio.date() == input_data.data
        ]
        agenda_do_dia.sort(key=lambda ag: ag.data_hora_inicio)
        return agenda_do_dia