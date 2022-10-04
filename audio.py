#!/usr/bin/python3.9

import re
import os
import sys
import distutils.spawn
def dier(msg):
    sys.exit(msg)

alert = distutils.spawn.find_executable("tts")
if alert:
    print(alert)
else:
    os.system("pip install tts==0.8.0")

if distutils.spawn.find_executable("sox"):
    print("sox was found")
else:
    os.system("sudo apt install sox")

filename = "video.txt"
file1 = open(filename, 'r')
Lines = file1.readlines()
comment_regex = re.compile("^\s*#")
png_regex = re.compile("^image=\w+.\w+")
video_regex = re.compile("^video=\w+.mp4")

tokens = []
video_data = {}
textparts = []
count = 0
for line in Lines:
    count += 1
    line.strip()
    if comment_regex.match(line):
        print("Ignoring comment line " + line)
    elif png_regex.match(line):
        tokens.append({"image": line[6:]})
    elif video_regex.match(line):
        tokens.append({"video": line[6:]})
    else:
        pattern = r'\s*[.!?]+\s+'
        l = list(filter(None, re.split(pattern, line)))
        tokens.append({"text": l})
        # os.system("tts --model_name tts_models/de/thorsten/tacotron2-DDC --out_path output%s.wav --text '%s'" % (count, line))
print(tokens)

count = 0
for token in tokens:
    if "text" in token.keys():
        token["audio"] = []
        for sentence in token["text"]:
            os.system("tts --model_name tts_models/de/thorsten/tacotron2-DDC \
                --out_path output%s.wav --text '%s'" % (count, sentence))
            token["audio"].append("output%s.wav" % count)
            count += 1

print(tokens)

token_is_text = False
count = 0
vid_count = 0
file_entry = ""
for token in tokens:
    if token_is_text and "audio" not in token.keys():
        os.system("sox %s conout%s.wav" % (filenames, count))
        current_audio = "conout%s.wav" %count
    if "audio" in token.keys():
        if not token_is_text:
            filenames = ""
        token_is_text = True

        for filename in token["audio"]:
            filenames += filename + " "
    if "image" in token.keys():
        token_is_text = False
        print(current_audio)
        cmd = '''ffmpeg -i %s -i %s vidout%s.flv''' % (token["image"], current_audio, vid_count)
        cmd = cmd.replace("\n", "")
        file_entry += "file vidout%s.flv\n" % vid_count
        os.system(cmd)
        vid_count += 1

    if "video" in token.keys():
        token_is_text = False
    count += 1

with open("vids.txt", "w") as f:
    f.write(file_entry)

os.system("ffmpeg -f concat -i vids.txt -c copy final.flv")

os.system("ffmpeg -i final.flv -qscale 0 -ar 22050 final.mp4")
