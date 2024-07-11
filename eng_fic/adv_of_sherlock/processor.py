import os
from pydub import AudioSegment


# exp: format("1.txt.", "1n.txt")
def format(from_file_name, to_file_name):
    new_text = ""
    # open the file
    with open(from_file_name, 'r') as file:
        # read the file
        text = file.read()

        lines = text.split('\n')

        new_lines = []

        curr_line = ""
        for i in range(len(lines)):
            # remove white space to one
            curr_line += ' '.join(lines[i].split())
            if i+1 >= len(lines) or len(lines[i+1]) <= 1:
                new_lines.append(curr_line)
                curr_line = ""
        
        new_text = '\n'.join(new_lines)

    # write the new text to the new file
    with open(to_file_name, 'w') as file:
        file.write(new_text)

# foler_path: folder containing the audio files
# output_file: the output file to save the concatenated audio
def concat_audio_files(folder_path, output_file):

    files = os.listdir(folder_path)
    files = [f for f in files if f.endswith('.mp3')]

    files = sorted(files, key=lambda x: int(x.split('_')[-1].split('.')[0]))

    print(f"files: {files}")

    audio = AudioSegment.empty()
    for f in files:
        audio += AudioSegment.from_file(f"{folder_path}/{f}")

    audio.export(output_file, format="mp3")