from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # PostgreSQL
    pg_dsn: str = "postgresql+psycopg2://user:pass@localhost:5432/neu"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_ocr_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    admission_chunk_words: int = 180
    admission_chunk_overlap_words: int = 40
    admission_embedding_batch_size: int = 32
    admission_hybrid_weight_text: float = 0.5
    admission_hybrid_weight_vector: float = 0.5

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Email (SMTP)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "NEU Data Query System"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    frontend_base_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
