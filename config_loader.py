import os
import json
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv()

def get_bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "y")
# config_loader.py
import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional

class EnvConfig(BaseModel):
    """Valida as variáveis de ambiente."""
    api_key: Optional[str] = Field(None, alias='API_KEY')
    api_secret: Optional[str] = Field(None, alias='API_SECRET')
    live_mode: bool = Field(False, alias='LIVE_MODE')
    risk_percent: float = Field(0.02, alias='RISK_PERCENT')
    symbol: str = Field('EURUSD', alias='SYMBOL')
    timeframe: str = Field('15m', alias='TIMEFRAME')
    log_dir: str = Field('logs', alias='LOG_DIR')
    data_path: str = Field('dummy_data.csv', alias='DATA_PATH')
    config_path: str = Field('config.example.json', alias='CONFIG_PATH')

class JsonConfig(BaseModel):
    """Valida a estrutura do arquivo config.json."""
    initial_balance: float
    strategy: dict
    risk: dict
    execution: dict

def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carrega, valida e combina configurações do .env e config.json.
    """
    # Carrega .env (já feito acima) e valida com Pydantic
    env_config = EnvConfig(**os.environ)

    # Carrega config.json e valida com Pydantic
    try:
        config_path = path or env_config.config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        json_config = JsonConfig(**json_data)
    except FileNotFoundError:
        raise ValueError(f"Arquivo de configuração '{path or env_config.config_path}' não encontrado.")
    except ValidationError as e:
        raise ValueError(f"Erro ao validar o arquivo de configuração: {e}")

    # Combina as configurações em um único objeto
    # Dando prioridade às variáveis de ambiente quando houver sobreposição
    config = {**json_config.dict(), **env_config.dict()}
    return config

# Para teste rápido
if __name__ == "__main__":
    try:
        cfg = load_config()
        print("Configuração carregada e validada com sucesso!")
        print(cfg)
    except ValueError as e:
        print(e)
