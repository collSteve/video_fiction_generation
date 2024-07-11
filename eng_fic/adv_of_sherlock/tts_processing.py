from TTS.api import TTS
import json

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

def create_audio_t(txt_file, mp3_file, log_file_path, speaker="Royston Min"):

    with open(txt_file, 'r') as file:
        text = file.read()

        paragraphs = text.split('\n')

        # remove empty paragraphs and paragraphs with only whitespace
        paragraphs = [p for p in paragraphs if p.strip() != '']

        # create json log file, create file if not exist
        json_obj = {"paragraphs": paragraphs, "tts_errors": [], "speaker": speaker, "language": "en", "output_file": mp3_file}


        print(f"para size: {len(paragraphs)}")
        for i in range(len(paragraphs)):
            try:
                tts.tts_to_file(text=paragraphs[i], speaker=speaker, language="en", file_path=f"{mp3_file}_{i}.mp3")
            except:
                print(f"Error: paragraph {i} not processed")
                json_obj["tts_errors"].append(i)
        
        # write the json log file
        with open(log_file_path, 'w') as file:
            json.dump(json_obj, file)

def test_audio_creation(text, output_path, speaker="Royston Min"):
    tts.tts_to_file(text=text, speaker=speaker, language="en", file_path=output_path)