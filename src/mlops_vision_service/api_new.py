from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from starlette.datastructures import UploadFile  # concrete class for type checks

try:
    from . import __version__ as _version
except Exception:
    _version = "0.1.0"
__version__: str = _version

app = FastAPI(title="mlops-vision-service", version=__version__)


# ---------- Pydantic models ----------
class PredictJSONRequest(BaseModel):
    image_url: Optional[str] = None
    data: Optional[List[float]] = None


class PredictResponse(BaseModel):
    label: str
    confidence: float
    mode: str  # "json" or "image"


# ---------- Probes ----------
@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/livez")
async def livez() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    # hook a real “model is loaded” check here later
    return {"status": "ready"}


# ---------- Unified /predict (JSON OR multipart image) ----------
@app.post("/predict", response_model=PredictResponse)
async def predict(request: Request) -> PredictResponse:
    """
    Accepts EITHER:
      - application/json: PredictJSONRequest
      - multipart/form-data: field 'image' with a file upload
    """
    ctype: str = request.headers.get("content-type", "") or ""

    if ctype.startswith("application/json"):
        payload = await request.json()
        req = PredictJSONRequest.model_validate(payload)
        label = "json_ok" if (req.data or req.image_url) else "json_empty"
        return PredictResponse(label=label, confidence=0.42, mode="json")

    if ctype.startswith("multipart/form-data"):
        form = await request.form()
        file_field = form.get("image")  # UploadFile | str | None
        if not isinstance(file_field, UploadFile):
            raise HTTPException(status_code=400, detail="Expected form field 'image' with a file")
        content: bytes = await file_field.read()
        label = "image_ok" if content else "image_empty"
        return PredictResponse(label=label, confidence=0.73, mode="image")

    raise HTTPException(
        status_code=415,
        detail="Unsupported Media Type. Use application/json or multipart/form-data.",
    )
