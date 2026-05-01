from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from lexie_server.db import get_db
from lexie_server.deps import require_admin
from lexie_server.models_orm import AgeProfile, utc_now_iso

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileOut(BaseModel):
    child_name: str
    age_years: int
    reading_level: str
    explanation_style: str | None = None


class ProfilePatch(BaseModel):
    model_config = ConfigDict(extra="ignore")

    child_name: str | None = None
    age_years: int | None = None
    reading_level: str | None = None
    explanation_style: str | None = None


def _row(p: AgeProfile) -> ProfileOut:
    return ProfileOut(
        child_name=p.child_name,
        age_years=p.age_years,
        reading_level=p.reading_level,
        explanation_style=p.explanation_style,
    )


@router.get("", dependencies=[Depends(require_admin)])
def get_profile(db: Session = Depends(get_db)) -> ProfileOut:
    p = db.get(AgeProfile, 1)
    if not p:
        raise HTTPException(500, detail={"error": "internal"})
    return _row(p)


@router.patch("", dependencies=[Depends(require_admin)])
def patch_profile(patch: ProfilePatch, db: Session = Depends(get_db)) -> ProfileOut:
    p = db.get(AgeProfile, 1)
    if not p:
        raise HTTPException(500, detail={"error": "internal"})
    d = patch.model_dump(exclude_unset=True)
    if not d:
        raise HTTPException(400, detail={"error": "no_fields"})
    for k, v in d.items():
        if not hasattr(p, k):
            continue
        if k in ("child_name", "reading_level") and v is not None and str(v).strip() == "":
            raise HTTPException(400, detail={"error": "empty_string_forbidden", "field": k})
        setattr(p, k, v)
    p.updated_at = utc_now_iso()
    db.add(p)
    db.commit()
    db.refresh(p)
    return _row(p)
