import os

import psycopg2
from psycopg2 import sql
from sqlalchemy.engine import make_url


def resolve_dsn() -> str:
    dsn = os.getenv("pg_dsn") or os.getenv("PG_DSN")
    if dsn:
        return dsn

    from app.core.config import settings

    return settings.pg_dsn


def main() -> int:
    dsn = resolve_dsn()
    url = make_url(dsn)

    target_db = url.database or "neu"
    host = url.host or "localhost"
    port = int(url.port or 5432)
    user = url.username
    password = url.password

    if not user:
        print("Missing username in pg_dsn")
        return 1

    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname="template1",
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            if cur.fetchone():
                print(f"Database '{target_db}' already exists.")
                return 0

            cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(target_db)))
            print(f"Created database '{target_db}'.")
            return 0
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ensure_postgres_db failed: {exc}")
        raise
