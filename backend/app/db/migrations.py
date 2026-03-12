from sqlalchemy import inspect, text


def ensure_user_columns(engine):
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("users")}

    statements = []
    if "email" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(120)")
        statements.append(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"
        )
    if "phone" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(30)")
    if "title" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN IF NOT EXISTS title VARCHAR(120)")
    if "birth_date" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_date DATE")
    if "gender" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10)")
    if "address" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN IF NOT EXISTS address VARCHAR(200)")
    if "department" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(120)"
        )

    if "reset_token" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(200)"
        )

    if "reset_token_expires_at" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires_at TIMESTAMPTZ"
        )

    if not statements:
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
