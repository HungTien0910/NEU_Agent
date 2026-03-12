from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.overview import OverviewResponse
from app.services.admin_service import build_overview

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=OverviewResponse)
def admin_overview(db: Session = Depends(get_db)):
    return build_overview(db)
