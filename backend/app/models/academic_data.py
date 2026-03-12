from sqlalchemy import Column, Float, Integer, String
from app.db.base import Base


class StudentRecord(Base):
    __tablename__ = "student_records"

    id = Column(Integer, primary_key=True, index=True)
    mssv = Column(String(30), unique=True, index=True, nullable=False)
    ho_ten = Column(String(150), nullable=True)
    ngay_sinh = Column(String(30), nullable=True)
    gioi_tinh = Column(String(20), nullable=True)
    que_quan = Column(String(120), nullable=True)
    lop = Column(String(50), nullable=True)
    khoa = Column(String(80), nullable=True)
    nam_nhap_hoc = Column(String(20), nullable=True)
    trang_thai = Column(String(40), nullable=True)
    gpa10 = Column(Float, nullable=True)
    gpa4 = Column(Float, nullable=True)


class CourseRecord(Base):
    __tablename__ = "course_records"

    id = Column(Integer, primary_key=True, index=True)
    ma_hoc_phan = Column(String(30), unique=True, index=True, nullable=False)
    ten_mon_hoc = Column(String(200), nullable=True)
    so_tin_chi = Column(Float, nullable=True)


class LecturerRecord(Base):
    __tablename__ = "lecturer_records"

    id = Column(Integer, primary_key=True, index=True)
    ma_giang_vien = Column(String(30), unique=True, index=True, nullable=False)
    ho_ten = Column(String(150), nullable=True)
    chuc_danh = Column(String(120), nullable=True)
    khoa = Column(String(80), nullable=True)


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(40), unique=True, index=True, nullable=False)
    mssv = Column(String(30), nullable=True)
    ma_hoc_phan = Column(String(30), nullable=True)
    ten_mon_hoc = Column(String(200), nullable=True)
    so_tin_chi = Column(Float, nullable=True)
    hoc_ky = Column(String(20), nullable=True)
    nam_hoc = Column(String(30), nullable=True)
    lop_hoc_phan = Column(String(60), nullable=True)
    giang_vien_phu_trach = Column(String(150), nullable=True)
    diem_thanh_phan = Column(Float, nullable=True)
    diem_tong_ket = Column(Float, nullable=True)
    ket_qua = Column(String(40), nullable=True)
