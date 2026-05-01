import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "version": "0.1.0",
        "git_sha": os.environ.get("GIT_SHA", ""),
    }
