from pydantic_settings import BaseSettings


class KeboolaConfig(BaseSettings):
    max_poll_attempts: int = 30
    poll_interval_seconds: int = 2

    class Config:
        env_prefix: str = "KEBOOLA_"