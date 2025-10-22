from io import BytesIO
from pathlib import Path
from typing import Any, Tuple

import numpy as np
from PIL import Image
from tensorflow import keras as tfk  # use tf.keras for .h5 models

# Point to your H5 model
MODEL_PATH = Path(__file__).resolve().parent / "models" / "mnist_model.h5"
if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

# Load once at import
model = tfk.models.load_model(str(MODEL_PATH))

# e.g. (None, 784) or (None, 28, 28, 1)
INPUT_SHAPE: Tuple[Any, ...] = tuple(model.input_shape[1:])


def _preprocess(img: Image.Image) -> np.ndarray[Any, Any]:
    """Convert to grayscale 28x28 and shape to what the model expects."""
    img = img.convert("L").resize((28, 28))
    arr = np.asarray(img, dtype="float32") / 255.0
    if INPUT_SHAPE == (784,):  # MLP expecting flat vector
        arr = arr.reshape(1, 28 * 28)
    elif INPUT_SHAPE == (28, 28, 1):  # CNN expecting channels-last
        arr = arr.reshape(1, 28, 28, 1)
    else:
        raise ValueError(f"Unexpected model input shape: {INPUT_SHAPE}")
    return arr


def predict_digit(image_bytes: bytes) -> int:
    img = Image.open(BytesIO(image_bytes))
    arr = _preprocess(img)
    preds = model.predict(arr, verbose=0)
    return int(np.argmax(preds, axis=-1)[0])


if __name__ == "__main__":
    img = Image.open("digit_sample.jpg")
    arr = _preprocess(img)
    preds = model.predict(arr, verbose=0)
    print(int(np.argmax(preds, axis=-1)[0]))
