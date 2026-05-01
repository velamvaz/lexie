from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "lexie-server"
    # PRD: public deploy; for local dev use http://127.0.0.1:8000
    public_base_url: str = Field(default="http://127.0.0.1:8000", alias="LEXIE_PUBLIC_BASE_URL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4o-mini", alias="LEXIE_CHAT_MODEL")
    openai_tts_model: str = Field(default="tts-1", alias="LEXIE_TTS_MODEL")
    openai_tts_voice: str = Field(default="nova", alias="LEXIE_TTS_VOICE")
    whisper_model: str = Field(default="whisper-1", alias="LEXIE_WHISPER_MODEL")

    # Required in production: when set, device must send this on /explain
    device_key: str = Field(default="", alias="LEXIE_DEVICE_KEY")
    admin_token: str = Field(default="", alias="LEXIE_ADMIN_TOKEN")

    log_requests: bool = Field(default=False, alias="LEXIE_LOG_REQUESTS")
    headword_tts: bool = Field(default=False, alias="LEXIE_HEADWORD_TTS")

    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
        alias="LEXIE_CORS_ORIGINS",
    )

    data_dir: Path = Field(default=Path("data"), alias="LEXIE_DATA_DIR")
    database_url: str = Field(default="", alias="LEXIE_DATABASE_URL")

    @field_validator("data_dir", mode="before")
    @classmethod
    def _expand_data_dir(cls, v: Path | str) -> Path:
        p = Path(v) if not isinstance(v, Path) else v
        return p

    @property
    def sqlite_path(self) -> Path:
        return (self.data_dir / "lexie.db").resolve()

    @property
    def effective_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{self.sqlite_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
