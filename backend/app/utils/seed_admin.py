from sqlalchemy.exc import IntegrityError
from app.core.security import hash_password
from app.db.base import Base
from app.db.postgres import SessionLocal
from app.repositories.user_repo import create_user, get_by_username


def main():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=db.get_bind())
        existing = get_by_username(db, "admin")
        if existing:
            existing.role = "admin"
            existing.permissions = ",".join(
                [
                    "data:student",
                    "data:course",
                    "data:lecturer",
                    "data:academic",
                ]
            )
            if not existing.email:
                existing.email = "admin@neu.edu.vn"
            if not existing.phone:
                existing.phone = "0900 000 001"
            if not existing.title:
                existing.title = "Quản trị"
            if not existing.department:
                existing.department = "CNTT"
            db.commit()
            db.refresh(existing)
            print("Admin user updated to role=admin.")
            return

        create_user(
            db=db,
            username="admin",
            full_name="NEU Admin",
            role="admin",
            hashed_password=hash_password("admin123"),
            email="admin@neu.edu.vn",
            phone="0900 000 001",
            title="Quản trị",
            department="CNTT",
            permissions=[
                "data:student",
                "data:course",
                "data:lecturer",
                "data:academic",
            ],
        )
        print("Seeded admin user: admin / admin123")
    except IntegrityError:
        db.rollback()
        print("Admin user already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
