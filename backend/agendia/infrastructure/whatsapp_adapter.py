import pywhatkit
from pywhatkit.core.exceptions import CountryCodeException

from agendia.application.ports import IWhatsAppAdapter

class PyWhatKitAdapter(IWhatsAppAdapter):
    """
    Implementação do adaptador de WhatsApp usando a biblioteca PyWhatKit.
    """
    def enviar_texto(self, numero_destino: str, texto: str) -> None:
        """
        Envia uma mensagem de texto instantaneamente.
        Requer que o usuário esteja logado no WhatsApp Web no navegador padrão.

        Args:
            numero_destino: O número no formato internacional com o sinal de '+'. 
                            Ex: +5583999998888
            texto: A mensagem a ser enviada.
        """
        try:
            print(f"INFO: Tentando enviar mensagem para {numero_destino} com PyWhatKit...")
            
            # O PyWhatKit abrirá uma aba do navegador e enviará a mensagem.
            # O 'wait_time' é o tempo em segundos para a aba carregar antes de enviar.
            pywhatkit.sendwhatmsg_instantly(
                phone_no=numero_destino,
                message=texto,
                wait_time=15,
                tab_close=True # Fecha a aba após o envio
            )
            print("SUCESSO: Mensagem enviada para a fila de envio do PyWhatKit.")

        except CountryCodeException:
            print(f"ERRO: O número '{numero_destino}' é inválido. Ele precisa incluir o código do país com o sinal de '+' (ex: +55).")
        except Exception as e:
            print(f"ERRO: Ocorreu um erro inesperado ao tentar enviar a mensagem com PyWhatKit: {e}")