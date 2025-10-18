import os
import json
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CONFIG_PATH = os.getenv("CONFIG_PATH", "config.example.json")


def load_config(path: str = None) -> Dict[str, Any]:
    """Carrega o config JSON e mescla com variáveis de ambiente.

    Prioridade: environment vars > json file > defaults.
    """
    path = path or DEFAULT_CONFIG_PATH
    config = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        # fallback para um config mínimo
        config = {
            "mode": "backtest",
            "instrument": os.getenv("SYMBOL", "EURUSD"),
            "data": {"path": os.getenv("DATA_PATH", "dummy_data.csv")},
            "initial_balance": float(os.getenv("INITIAL_BALANCE", 10000)),
        }

    # override com env vars mais comuns
    if os.getenv("SYMBOL"):
        config["instrument"] = os.getenv("SYMBOL")
    if os.getenv("DATA_PATH"):
        config.setdefault("data", {})["path"] = os.getenv("DATA_PATH")
    if os.getenv("INITIAL_BALANCE"):
        try:
            config["initial_balance"] = float(os.getenv("INITIAL_BALANCE"))
        except ValueError:
            pass

    return config


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

def load_config():
    """
    Carrega, valida e combina configurações do .env e config.json.
    """
    # Carrega .env e valida com Pydantic
    load_dotenv()
    env_config = EnvConfig(**os.environ)

    # Carrega config.json e valida com Pydantic
    try:
        with open(env_config.config_path, 'r') as f:
            json_data = json.load(f)
        json_config = JsonConfig(**json_data)
    except FileNotFoundError:
        raise ValueError(f"Arquivo de configuração '{env_config.config_path}' não encontrado.")
    except Exception as e:
        raise ValueError(f"Erro ao validar o arquivo de configuração: {e}")

    # Combina as configurações em um único objeto
    # Dando prioridade às variáveis de ambiente quando houver sobreposição
    config = {**json_config.dict(), **env_config.dict()}

    return config

# Para teste rápido
if __name__ == "__main__":
    try:
        config = load_config()
        print("Configuração carregada e validada com sucesso!")
        print(config)
    except ValueError as e:
        print(e)
