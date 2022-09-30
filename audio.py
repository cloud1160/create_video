#!/usr/bin/python3.9
from cgitb import text
import re
import os
import sys
# from ctts import cTTS
import distutils.spawn
def dier(msg):
    sys.exit(msg)

# cTTS.synthesizeToFile("output.wav", "Das ist ein Test.")

# os.system("tts")

# check = os.system("echo $?")
# if check:
#     print("Is installed")
# else:
#     print("Did not work.")

alarm = distutils.spawn.find_executable("tts")
if alarm:
    print(alarm)
else:
    os.system("pip install tts==0.8.0")

# wie kann der server gestarted werden und gleichzeitig das skript weiterlaufen
# os.system("tts-server --model_name tts_models/de/thorsten/vits")


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
    # print(line)
    if comment_regex.match(line):
        print("Ignoring comment line " + line)
    elif png_regex.match(line):
        tokens.append({"image": line})
        # video_data['image'] = line
    elif video_regex.match(line):
        tokens.append({"video": line[6:]})
        # video_data['video'] = line
    else:
        # print("Line{}: {}".format(count, line))
        pattern = r'\s*[.!?]+\s+'
        l = list(filter(None, re.split(pattern, line)))
        tokens.append({"text": l})
        # video_data['text'] = "output%s.wav" % count
        # os.system("tts --model_name tts_models/de/thorsten/tacotron2-DDC --out_path output%s.wav --text '%s'" % (count, line))
print(tokens)
# os.system("ffmpeg -framerate 1 -pattern_type glob -i '*.png' -i output.wav \
    # -c:v libx264 -pix_fmt yuv420p out5.mp4")