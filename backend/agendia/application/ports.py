from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime
from agendia.core.domain import Profissional, Agendamento

class IProfissionalRepositorio(ABC):
    """Contrato que define os métodos para persistir dados da entidade Profissional."""

    @abstractmethod
    def salvar(self, profissional: Profissional) -> None:
        """Salva uma instância nova ou atualiza uma existente de um Profissional."""
        pass

    @abstractmethod
    def buscar_por_id(self, id_profissional: UUID) -> Profissional | None:
        """Busca um Profissional pelo seu ID único."""
        pass

    @abstractmethod
    def buscar_por_telefone(self, telefone: str) -> Profissional | None:
        """Busca um Profissional pelo seu número de WhatsApp."""
        pass

    @abstractmethod
    def listar_todos(self) -> list[Profissional]: # <-- NOVO MÉTODO ADICIONADO
        """Retorna uma lista de todos os profissionais cadastrados."""
        pass

# ... resto do arquivo inalterado ...
class IAgendamentoRepositorio(ABC):
    """Contrato que define os métodos para persistir dados da entidade Agendamento."""
    pass 

class IWhatsAppAdapter(ABC):
    """Contrato para qualquer serviço de envio de mensagens do WhatsApp."""
    
    @abstractmethod
    def enviar_texto(self, numero_destino: str, texto: str) -> None:
        """Envia uma mensagem de texto para um número de destino."""
        pass