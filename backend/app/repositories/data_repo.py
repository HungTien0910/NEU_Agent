from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from sqlalchemy.dialects.postgresql import insert
from app.models.academic_data import (
    AcademicRecord,
    CourseRecord,
    LecturerRecord,
    StudentRecord,
)


def _upsert(db: Session, model, rows: List[Dict[str, Any]], key: str):
    if not rows:
        return
    stmt = insert(model).values(rows)
    update_cols = {c.name: c for c in stmt.excluded if c.name != "id"}
    stmt = stmt.on_conflict_do_update(index_elements=[key], set_=update_cols)
    db.execute(stmt)
    db.commit()


def upsert_students(db: Session, rows: List[Dict[str, Any]]):
    _upsert(db, StudentRecord, rows, "mssv")


def upsert_courses(db: Session, rows: List[Dict[str, Any]]):
    _upsert(db, CourseRecord, rows, "ma_hoc_phan")


def upsert_lecturers(db: Session, rows: List[Dict[str, Any]]):
    _upsert(db, LecturerRecord, rows, "ma_giang_vien")


def upsert_academics(db: Session, rows: List[Dict[str, Any]]):
    _upsert(db, AcademicRecord, rows, "record_id")


def clear_all(db: Session):
    db.query(AcademicRecord).delete()
    db.query(LecturerRecord).delete()
    db.query(CourseRecord).delete()
    db.query(StudentRecord).delete()
    db.commit()


def list_students(
    db: Session, search: Optional[str], limit: int, skip: int
) -> List[StudentRecord]:
    query = db.query(StudentRecord)
    if search:
        query = query.filter(
            StudentRecord.mssv.ilike(f"%{search}%")
            | StudentRecord.ho_ten.ilike(f"%{search}%")
            | StudentRecord.lop.ilike(f"%{search}%")
            | StudentRecord.khoa.ilike(f"%{search}%")
            | StudentRecord.que_quan.ilike(f"%{search}%")
            | StudentRecord.trang_thai.ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()


def count_students(db: Session, search: Optional[str]) -> int:
    query = db.query(StudentRecord)
    if search:
        query = query.filter(
            StudentRecord.mssv.ilike(f"%{search}%")
            | StudentRecord.ho_ten.ilike(f"%{search}%")
            | StudentRecord.lop.ilike(f"%{search}%")
            | StudentRecord.khoa.ilike(f"%{search}%")
            | StudentRecord.que_quan.ilike(f"%{search}%")
            | StudentRecord.trang_thai.ilike(f"%{search}%")
        )
    return query.count()


def list_students_all(db: Session, search: Optional[str]) -> List[StudentRecord]:
    return list_students(db, search, limit=1000000, skip=0)


def list_courses(
    db: Session, search: Optional[str], limit: int, skip: int
) -> List[CourseRecord]:
    query = db.query(CourseRecord)
    if search:
        query = query.filter(
            CourseRecord.ma_hoc_phan.ilike(f"%{search}%")
            | CourseRecord.ten_mon_hoc.ilike(f"%{search}%")
            | cast(CourseRecord.so_tin_chi, String).ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()


def count_courses(db: Session, search: Optional[str]) -> int:
    query = db.query(CourseRecord)
    if search:
        query = query.filter(
            CourseRecord.ma_hoc_phan.ilike(f"%{search}%")
            | CourseRecord.ten_mon_hoc.ilike(f"%{search}%")
            | cast(CourseRecord.so_tin_chi, String).ilike(f"%{search}%")
        )
    return query.count()


def list_courses_all(db: Session, search: Optional[str]) -> List[CourseRecord]:
    return list_courses(db, search, limit=1000000, skip=0)


def list_lecturers(
    db: Session, search: Optional[str], limit: int, skip: int
) -> List[LecturerRecord]:
    query = db.query(LecturerRecord)
    if search:
        query = query.filter(
            LecturerRecord.ma_giang_vien.ilike(f"%{search}%")
            | LecturerRecord.ho_ten.ilike(f"%{search}%")
            | LecturerRecord.chuc_danh.ilike(f"%{search}%")
            | LecturerRecord.khoa.ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()


def count_lecturers(db: Session, search: Optional[str]) -> int:
    query = db.query(LecturerRecord)
    if search:
        query = query.filter(
            LecturerRecord.ma_giang_vien.ilike(f"%{search}%")
            | LecturerRecord.ho_ten.ilike(f"%{search}%")
            | LecturerRecord.chuc_danh.ilike(f"%{search}%")
            | LecturerRecord.khoa.ilike(f"%{search}%")
        )
    return query.count()


def list_lecturers_all(db: Session, search: Optional[str]) -> List[LecturerRecord]:
    return list_lecturers(db, search, limit=1000000, skip=0)


def list_academics(
    db: Session, search: Optional[str], limit: int, skip: int
) -> List[AcademicRecord]:
    query = db.query(AcademicRecord)
    if search:
        query = query.filter(
            AcademicRecord.record_id.ilike(f"%{search}%")
            | AcademicRecord.mssv.ilike(f"%{search}%")
            | AcademicRecord.ma_hoc_phan.ilike(f"%{search}%")
            | AcademicRecord.ten_mon_hoc.ilike(f"%{search}%")
            | AcademicRecord.hoc_ky.ilike(f"%{search}%")
            | AcademicRecord.nam_hoc.ilike(f"%{search}%")
            | AcademicRecord.giang_vien_phu_trach.ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()


def count_academics(db: Session, search: Optional[str]) -> int:
    query = db.query(AcademicRecord)
    if search:
        query = query.filter(
            AcademicRecord.record_id.ilike(f"%{search}%")
            | AcademicRecord.mssv.ilike(f"%{search}%")
            | AcademicRecord.ma_hoc_phan.ilike(f"%{search}%")
            | AcademicRecord.ten_mon_hoc.ilike(f"%{search}%")
            | AcademicRecord.hoc_ky.ilike(f"%{search}%")
            | AcademicRecord.nam_hoc.ilike(f"%{search}%")
            | AcademicRecord.giang_vien_phu_trach.ilike(f"%{search}%")
        )
    return query.count()


def list_academics_all(db: Session, search: Optional[str]) -> List[AcademicRecord]:
    return list_academics(db, search, limit=1000000, skip=0)
