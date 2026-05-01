from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from lexie_server.db import get_db
from lexie_server.deps import require_admin
from lexie_server.models_orm import ExplainRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/usage", dependencies=[Depends(require_admin)])
def usage(db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    ym = f"{now.year:04d}-{now.month:02d}"
    prefix = ym + "-"
    n = db.execute(
        select(func.count()).select_from(ExplainRequest).where(
            ExplainRequest.created_at.startswith(prefix)
        )
    ).scalar()
    return {"month": ym, "explain_count": int(n or 0), "cost_usd_estimated": None}
