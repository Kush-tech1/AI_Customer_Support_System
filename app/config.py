from pathlib import Path

import yaml

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseModel):
    default: str
    complex: str
    fallback: str


class RuntimeConfig(BaseModel):
    max_retries: int
    timeout_seconds: int


class RoutingConfig(BaseModel):
    complex_intents: list[str]


class DemoConfig(BaseModel):
    force_model_failure: bool


class AppConfig(BaseModel):
    models: ModelConfig
    runtime: RuntimeConfig
    routing: RoutingConfig
    demo: DemoConfig


class EnvironmentSettings(BaseSettings):
    gemini_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
    )


def load_config() -> AppConfig:
    config_path = Path("config.yaml")

    with config_path.open("r") as file:
        raw_config = yaml.safe_load(file)

    return AppConfig(**raw_config)


config = load_config()
settings = EnvironmentSettings()