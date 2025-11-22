# from starlette.datastructures import UploadFile
# import imageio as io
import pathlib as Path
import shutil
from typing import Any, List, Optional

import starlette.datastructures as sd
from fastapi import Body, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, model_validator

from mlops_vision_service.inference import predict_digit

UploadFile is sd.UploadFile

app = FastAPI(title="mlops-vision-servic", version="0.1.0")
PREDICT_PAGE = (Path.Path(__file__).resolve().parent / "predict_digit.html").read_text(
    encoding="utf-8"
)


# ------- model for Json in/out ----------
class PredictJSONRequest(BaseModel):
    image_url: Optional[str] = None
    data: Optional[List[float]] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PredictJSONRequest":
        if not (self.image_url or (self.data and len(self.data) > 0)):
            raise ValueError("Provide either 'image_url' or non-empty 'data'.")
        return self


class PredictResponse(BaseModel):
    label: str
    result: int | None
    confidence: float
    mode: str


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/livez")
async def livez() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/predict-json", response_model=PredictResponse)
async def predict_json(payload: PredictJSONRequest = Body(...)) -> PredictResponse:
    label = "json_ok" if (payload.data or payload.image_url) else "json_empty"
    return PredictResponse(label=label, result=0, confidence=0.42, mode="json")


@app.post("/predict", response_model=PredictResponse)
async def predict(request: Request) -> PredictResponse:
    ctype: str = (request.headers.get("content-type") or "").lower()

    # JSON branch
    if ctype.startswith("application/json"):
        payload = await request.json()
        req = PredictJSONRequest.model_validate(payload)
        has_signal = (req.data and len(req.data) > 0) or (req.image_url is not None)
        label = "json_ok" if has_signal else "json_empty"
        return PredictResponse(label=label, result=None, confidence=0.0, mode="json")

    # Multipart branch (file upload)
    if ctype.startswith("multipart/form-data"):
        form = await request.form()
        file_field = form.get("image")  # expect field name: "image"
        print(file_field, isinstance(file_field, UploadFile), UploadFile)
        if not (isinstance(file_field, UploadFile) or isinstance(file_field, sd.UploadFile)):
            raise HTTPException(status_code=400, detail="Expected form field 'image' with a file")

        # testupload(file_field)

        content: bytes = await file_field.read()
        result = predict_digit(content)
        label = "image_ok" if content else "image_empty"
        return PredictResponse(label=label, result=result, confidence=0.73, mode="image")

    # Anything else
    raise HTTPException(status_code=415, detail="Use application/json or multipart/form-data")


@app.get("/predict_digit", response_class=HTMLResponse)
async def predict_digit_form() -> str:
    return PREDICT_PAGE


@app.post("/predict_digit", response_model=PredictResponse)
async def predict_digit_head(image: UploadFile = File(...)) -> PredictResponse:
    content = await image.read()
    r = predict_digit(content)
    label = "image_ok" if content else "image_empty"
    return PredictResponse(label=label, result=r, confidence=0.73, mode="image")


@app.post("/upload")
async def upload_image(
    image: UploadFile = File(...), new_name: str | None = Form(default=None)
) -> dict[str, str | int]:
    # allowed = {".jpg", ".jpeg", ".png", ".gif"}
    # orig_suffix = Path(image.filename or "").suffix.lower()
    # if orig_suffix not in allowed:
    #     return {"error": f"unsupported file type: {orig_suffix}"}
    safe_name = "content.jpg"
    UPLOAD_DIR = Path.Path("uploads")
    dest = UPLOAD_DIR / safe_name
    with dest.open("wb") as f:
        # copy the file-like stream to disk
        shutil.copyfileobj(image.file, f)
    size = dest.stat().st_size
    return {
        "saved_as": str(dest),
        "original_name": image.filename or "",
        "bytes": size,
        "content_type": image.content_type or "",
    }


def testupload(image: Any) -> None:
    safe_name = "content.jpg"
    UPLOAD_DIR = Path.Path("uploads")
    dest = UPLOAD_DIR / safe_name
    with dest.open("wb") as f:
        # copy the file-like stream to disk
        shutil.copyfileobj(image.file, f)
    return
