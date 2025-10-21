from fastapi.testclient import TestClient

from mlops_vision_service.api import app

client = TestClient(app)


def test_predict_json_ok() -> None:
    r = client.post("/predict", json={"data": [1.0, 2.0, 5]})
    assert r.status_code == 200

    body = r.json()

    assert body["mode"] == "json"
    assert body["label"] == "json_ok"


def test_predict_wrong_content_type() -> None:
    r = client.post("/predict", data=["not json"])  # no JSON header/body
    assert r.status_code == 415


def test_predict_image_ok(tmp_path) -> None:
    p = tmp_path / "fake.jpg"
    p.write_bytes(b"\x00\x01\x02")  # tiny fake image
    with p.open("rb") as f:
        r = client.post("/predict", files={"image": ("fake.jpg", f, "image/jpeg")})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "image"
    assert body["label"] == "image_ok"


def test_predict_json_empty_is_422() -> None:
    r = client.post("/predict", json={})
    assert r.status_code == 422


def test_predict_json_ok_with_image_url() -> None:
    r = client.post("/predict", json={"image_url": "https://example.com/cat.jpg"})
    assert r.status_code == 200
    assert r.json()["label"] in {"json_ok", "json_empty"}  # your current logic
