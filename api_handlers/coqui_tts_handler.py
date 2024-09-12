from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


def voice_over(script, output_path, speaker="Royston Min"):
    tts.tts_to_file(text=script, speaker=speaker, language="en", file_path=output_path)