from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: SecretStr = Field(min_length=1)
    modelo: str = "openai/gpt-oss-120b"
    cantidad_maxima_por_item: int = Field(default=20, ge=1)
    pedido_minimo: float = Field(default=0, ge=0)
    max_lineas_pedido: int = Field(default=3, ge=1)
    monto_maximo_pedido: float = Field(default=200, gt=0)


def cargar_configuracion() -> Configuracion:
    return Configuracion()
