from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import os
import soundfile as sf
import numpy as np
import torch
import traceback
import shutil
import uuid
from datetime import datetime

from inference import StyleTTS2
from text_preprocessor.text_util import TextUtil

app = FastAPI()

repo_dir = './'
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load model
config_path = os.path.join(repo_dir, "Models", "config.yaml")
models_path = os.path.join(repo_dir, "Models", "model.pth")
model = StyleTTS2(config_path, models_path).eval().to(device)

# Path to predefined voice files
voice_path = os.path.join(repo_dir, "reference_audio/vi_trung_tinh")
predefined_voices = {
    "nam": [os.path.join(voice_path, "nam/vn_2.wav")],
    "nu": [os.path.join(voice_path, "nu/vn_3.wav")]
}

# ========== Main inference logic ==========
def generate_audio(reference_paths, text_prompt, denoise, avg_style, stabilize):
    try:
        # Preprocess text
        text_prompt = TextUtil.classify(text_prompt)

        speakers = {}
        for i, path in enumerate(reference_paths, 1):
            speaker_id = f"id_{i}"
            speakers[speaker_id] = {
                "path": path,
                "lang": "vi",
                "speed": 1.0
            }

        with torch.no_grad():
            styles = model.get_styles(speakers, denoise, avg_style)
            r = model.generate(text_prompt, styles, stabilize, 18, "[id_1]")
            r = r / np.abs(r).max()

        # Output path
        today = datetime.now().strftime("%Y%m%d")
        out_dir = os.path.join("data", today)
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.wav"
        out_path = os.path.join(out_dir, filename)
        sf.write(out_path, r, samplerate=24000)
        return out_path, None

    except Exception:
        return None, traceback.format_exc()

# ========== API endpoint ==========
@app.post("/synthesize/")
async def synthesize(
    text: str = Form(...),
    denoise: float = Form(0.6),
    avg_style: bool = Form(True),
    stabilize: bool = Form(True),
    reference_audio_name: Optional[str] = Form(None),
    reference_audios: Optional[List[UploadFile]] = File(None)
):
    temp_audio_paths = []

    try:
        # Use uploaded reference audios
        if reference_audios:
            for file in reference_audios:
                temp_path = f"temp_{uuid.uuid4().hex}_{file.filename}"
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                temp_audio_paths.append(temp_path)

        # Use predefined reference audio by name
        elif reference_audio_name in predefined_voices:
            temp_audio_paths = predefined_voices[reference_audio_name]
        else:
            return JSONResponse(
                content={"error": "Please provide either uploaded reference_audios or valid reference_audio_name ('nam' or 'nu')."},
                status_code=400
            )

        # Run inference
        out_path, error = generate_audio(temp_audio_paths, text, denoise, avg_style, stabilize)

        # Clean up temp files
        for path in temp_audio_paths:
            if path.startswith("temp_") and os.path.exists(path):
                os.remove(path)

        if error:
            return JSONResponse(content={"error": error}, status_code=500)

        return FileResponse(out_path, media_type="audio/wav", filename=os.path.basename(out_path))

    except Exception:
        return JSONResponse(content={"error": traceback.format_exc()}, status_code=500)
