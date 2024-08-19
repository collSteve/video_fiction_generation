import torch
from TTS.api import TTS
import json

device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

"""
log = {
"segment_files": {
    "0": "output.mp3",
    "1": "output1.mp3",
    "3": "output3.mp3"
    },
"paragraphs": paragraphs,
"tts_errors": [1, 3],
"speaker": "Royston Min",
"language": "en",
"output_file": "output.mp3"

}
"""

def create_audio_t(txt_file, mp3_file, log_file_path, speaker="Royston Min"):

    with open(txt_file, 'r') as file:
        text = file.read()

        paragraphs = text.split('\n')

        # remove empty paragraphs and paragraphs with only whitespace
        paragraphs = [p for p in paragraphs if p.strip() != '']

        # create json log file, create file if not exist
        json_obj = {"paragraphs": paragraphs, "tts_errors": [], "speaker": speaker, "language": "en", "output_file": mp3_file, "segment_files": {}}


        print(f"para size: {len(paragraphs)}")
        for i in range(len(paragraphs)):
            try:
                text = paragraphs[i].replace("\"", "") # prevent large quotes from breaking the TTS
                file_path = f"{mp3_file}_{i}.mp3"

                tts.tts_to_file(text=text, speaker=speaker, language="en", file_path=file_path)

                # log the file path
                json_obj["segment_files"][i] = file_path
            except:
                print(f"Error: paragraph {i} not processed")
                json_obj["tts_errors"].append(i)
        
        # write the json log file
        with open(log_file_path, 'w') as file:
            json.dump(json_obj, file)

def test_audio_creation(text, output_path, speaker="Royston Min"):
    tts.tts_to_file(text=text, speaker=speaker, language="en", file_path=output_path)