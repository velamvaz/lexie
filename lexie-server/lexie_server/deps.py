from fastapi import Depends, Header, HTTPException, Request

from lexie_server.config import Settings, get_settings


def _bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:].strip() or None


def require_device_key(
    request: Request,
    settings: Settings = Depends(get_settings),
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_device_key: str | None = Header(default=None, alias="X-Device-Key"),
) -> None:
    # SPEC: if LEXIE_DEVICE_KEY unset, accept (development)
    if not settings.device_key:
        return
    token = _bearer(authorization) or (x_device_key and x_device_key.strip())
    if not token or token != settings.device_key:
        raise HTTPException(status_code=401, detail={"error": "unauthorized"})


def require_admin(
    request: Request,
    settings: Settings = Depends(get_settings),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    token = _bearer(authorization)
    if not settings.admin_token:
        # Misconfiguration: do not allow admin with empty token
        raise HTTPException(status_code=500, detail={"error": "internal"})
    if not token or token != settings.admin_token:
        raise HTTPException(status_code=401, detail={"error": "unauthorized"})
