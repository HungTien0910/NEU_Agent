Graph schema:
- (:Student {mssv, hoTen, ngaySinh, gioiTinh, queQuan, lop, khoa, namNhapHoc, trangThai, gpa10, gpa4})
- (:Course {maHocPhan, tenMonHoc, soTinChi})
- (:Lecturer {maGiangVien, hoTen, chucDanh, khoa})
- (:AcademicRecord {recordId, maHocPhan, hocKy, namHoc, lopHocPhan, diemThanhPhan, diemTongKet, ketQua})
- (:Department {tenKhoa})
- (:Class {tenLop})

Relationships:
(Student)-[:BELONGS_TO]->(Department)
(Student)-[:IN_CLASS]->(Class)
(Lecturer)-[:IN_DEPARTMENT]->(Department)
(Student)-[:HAS_RECORD]->(AcademicRecord)
(AcademicRecord)-[:OF_COURSE]->(Course)
(AcademicRecord)-[:TAUGHT_BY]->(Lecturer)
