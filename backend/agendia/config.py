from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Carrega as configurações do projeto a partir de um arquivo .env.
    """
    # Defina aqui as variáveis que você quer carregar do seu arquivo .env
    # Por enquanto, não precisamos de nenhuma para o pywhatkit, mas a estrutura já fica pronta.
    # Exemplo para o futuro (com Evolution API):
    # evolution_api_url: str = "http://localhost:8080"
    # evolution_api_key: str = "YOUR_API_KEY"

    # Configuração para dizer ao Pydantic para ler o arquivo .env
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

# Cria uma instância única das configurações para ser usada em toda a aplicação
settings = Settings()