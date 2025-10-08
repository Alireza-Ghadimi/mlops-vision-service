from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from starlette.datastructures import UploadFile  # use the concrete class

try:
    # If you set __version__ in __init__.py earlier
    from . import __version__
except Exception:  # pragma: no cover
    __version__ = "0.1.0"

app = FastAPI(title="mlops-vision-service", version=__version__)


# ---------- Models (JSON mode) ----------
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
    # Placeholder for "loaded model / ready" checks
    return {"status": "ready"}


# ---------- Unified /predict (JSON OR multipart image) ----------
@app.post("/predict", response_model=PredictResponse)
async def predict(request: Request) -> PredictResponse:
    """
    Accepts EITHER:
      - application/json: PredictJSONRequest
      - multipart/form-data: field 'image' with a file
    """
    ctype = request.headers.get("content-type", "")
    if ctype.startswith("application/json"):
        payload = await request.json()
        try:
            req = PredictJSONRequest.model_validate(payload)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON body: {e}")
        # Dummy logic for demo:
        label = "json_ok" if (req.data or req.image_url) else "json_empty"
        return PredictResponse(label=label, confidence=0.42, mode="json")

    if ctype.startswith("multipart/form-data"):
        form = await request.form()
        file = form.get("image")
        if not isinstance(file, UploadFile):
            raise HTTPException(status_code=400, detail="Expected form field 'image' with a file")
        content = await file.read()
        label = "image_ok" if content else "image_empty"
        return PredictResponse(label=label, confidence=0.73, mode="image")

    raise HTTPException(
        status_code=415,
        detail="Unsupported Media Type. Use application/json or multipart/form-data.",
    )
