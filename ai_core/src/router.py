def infer_sheet(question: str) -> str:
    q = question.lower()
    if "sinh viên" in q or "student" in q:
        return "student"
    if "giảng viên" in q or "lecturer" in q:
        return "lecturer"
    if "môn" in q or "học phần" in q or "khóa học" in q or "course" in q:
        return "course"
    if "điểm" in q or "học kỳ" in q or "academic" in q:
        return "academic"
    return "student"
