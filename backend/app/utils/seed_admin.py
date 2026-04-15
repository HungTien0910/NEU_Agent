from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.base import Base
from app.db.postgres import SessionLocal
from app.repositories.user_repo import create_user, get_by_username


def main():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=db.get_bind())
        permissions = [
            "data:student",
            "data:course",
            "data:lecturer",
            "data:academic",
        ]

        existing = get_by_username(db, "admin")
        if existing:
            existing.role = "admin"
            existing.permissions = ",".join(permissions)
            if not existing.email:
                existing.email = "admin@neu.edu.vn"
            if not existing.phone:
                existing.phone = "0900 000 001"
            if not existing.title:
                existing.title = "Quan tri"
            if not existing.department:
                existing.department = "CNTT"
            db.commit()
            db.refresh(existing)
            print("Admin user updated to role=admin.")
            return

        created = create_user(
            db=db,
            username="admin",
            full_name="NEU Admin",
            role="admin",
            hashed_password=hash_password("admin123"),
            email="admin@neu.edu.vn",
            permissions=permissions,
        )

        created.phone = "0900 000 001"
        created.title = "Quan tri"
        created.department = "CNTT"
        db.commit()
        db.refresh(created)
        print("Seeded admin user: admin / admin123")
    except IntegrityError:
        db.rollback()
        print("Admin user already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
