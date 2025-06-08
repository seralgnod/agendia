from abc import ABC, abstractmethod
from uuid import UUID

from agendia.core.domain import Profissional, Agendamento

# =============================================================================
# INTERFACES DOS REPOSITÓRIOS (PORTAS)
# =============================================================================

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
    
    Nota: No nosso design, os agendamentos são gerenciados através da
    entidade Profissional (Raiz de Agregação), então a maioria das
    operações pode ocorrer através do IProfissionalRepositorio.
    Esta interface pode ser expandida se precisarmos de buscas diretas
    em agendamentos.
    """

    @abstractmethod
    def buscar_proximos_agendamentos(self, data_limite: "datetime") -> list[Agendamento]:
        """Busca todos os agendamentos até uma data/hora específica, para enviar lembretes."""
        pass