from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime

from agendia.core.domain import Profissional, Agendamento

# ... (IProfissionalRepositorio e IAgendamentoRepositorio permanecem os mesmos) ...

class IProfissionalRepositorio(ABC):
    """
    Interface (Contrato) que define os métodos para persistir dados 
    da entidade Profissional.
    """

    @abstractmethod
    def salvar(self, profissional: Profissional) -> None:
        """Salva uma instância nova ou atualiza uma existente de um Profissional."""
        pass

    @abstractmethod
    def buscar_por_id(self, id_profissional: UUID) -> Profissional | None:
        """Busca um Profissional pelo seu ID único."""
        pass

    @abstractmethod
    def buscar_por_contato(self, contato: str) -> Profissional | None:
        """
        Busca um Profissional pelo seu contato (ex: número de WhatsApp).
        Essencial para o chatbot identificar com quem está falando.
        """
        pass


class IAgendamentoRepositorio(ABC):
    """
    Interface (Contrato) que define os métodos para persistir dados
    da entidade Agendamento.
    """

    @abstractmethod
    def buscar_proximos_agendamentos(self, data_limite: "datetime") -> list[Agendamento]:
        """Busca todos os agendamentos até uma data/hora específica, para enviar lembretes."""
        pass

# --- NOVA INTERFACE ---
class IWhatsAppAdapter(ABC):
    """
    Interface (Contrato) para qualquer serviço de envio de mensagens do WhatsApp.
    """
    
    @abstractmethod
    def enviar_texto(self, numero_destino: str, texto: str) -> None:
        """
        Envia uma mensagem de texto para um número de destino.
        """
        pass