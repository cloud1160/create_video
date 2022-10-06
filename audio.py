#!/usr/bin/python3.9

import re
from os import path, makedirs, system
import sys
import distutils.spawn
from hashlib import md5
import argparse


def dier(msg):
    sys.exit(msg)


def file_exists(entry):
    if path.exists(entry.replace("\n", "")):
        print("The file %s exists" % entry.replace("\n", ""))
        return True
    else:
        dier("The file %s doesn't exist programm stops." %
             entry.replace("\n", ""))


def is_installed(program_name, install_command):
    if distutils.spawn.find_executable(program_name):
        print("%s is installed: continue" % program_name)
    else:
        system(install_command)


replace_words = {"gpus": "ge pe us", "ssh": "s s h"}

ap = argparse.ArgumentParser()

ap.add_argument("--file")
ap.add_argument("--overwrite")
args = vars(ap.parse_args())

overwrite = ""
if args["overwrite"] == "y":
    overwrite = " -y"

is_installed("tts", "pip install tts==0.8.0")
is_installed("sox", "sudo apt install sox")

if not path.exists("tmp"):
    makedirs("tmp")

Lines = []
filename = "video.txt"
# dier(args["file"])
if file_exists(args["file"]):
    # dier("file %s exists" % args["file"])
    filename = args["file"]
else:
    dier("%s does not exist." % filename)
try:
    with open(filename, 'r') as file1:
        Lines = file1.readlines()
except:
    dier("create and write a video.txt file")

comment_regex = re.compile("^\s*#")
png_regex = re.compile("^image=(.+\.\w+)$")
video_regex = re.compile("^video=(.+)$")

tokens = []
video_data = {}
textparts = []
count = 0
for line in Lines:
    count += 1
    line.strip()
    if comment_regex.match(line):
        pass
    elif fname := png_regex.match(line):
        # print(line[6:].replace("\n", ""))
        print(fname.group(1))
        tokens.append({"image": fname.group(1)})
        file_exists(fname.group(1))
    elif fname := video_regex.match(line):
        tokens.append({"video": fname.group(1)})
        file_exists(fname.group(1))
    else:
        for word in replace_words:
            if word in line:
                line = line.replace(word, replace_words[word])
        pattern = r'\s*[.!?]+\s+'
        l = list(filter(None, re.split(pattern, line)))
        tokens.append({"text": l})
print(tokens)

count = 0
for token in tokens:
    if "text" in token.keys():
        token["audio"] = []

        for sentence in token["text"]:
            md5_hash = md5(sentence.encode('utf-8')).hexdigest()
            sentence = sentence.replace("'", "")
            if path.exists("tmp/%s.wav" % md5_hash):
                print("Audio '%s' was already created" % sentence)
            else:
                system("tts --model_name tts_models/de/thorsten/tacotron2-DDC \
                --out_path tmp/%s.wav --text '%s'" % (md5_hash, sentence))
            token["audio"].append("tmp/%s.wav" % md5_hash)
            count += 1

print(tokens)

token_is_text = False
count = 0
vid_count = 0
file_entry = ""
for token in tokens:
    if token_is_text and "audio" not in token.keys():
        system("sox %s conout%s.wav" % (filenames, count))
        current_audio = "conout%s.wav" % count
    if "audio" in token.keys():
        if not token_is_text:
            filenames = ""
        token_is_text = True

        for filename in token["audio"]:
            filenames += filename + " "
    if "image" in token.keys():
        token_is_text = False
        print(current_audio)
        cmd = 'ffmpeg -i %s -i %s vidout%s.flv%s' % (
            token["image"], current_audio, vid_count, overwrite)
        cmd = cmd.replace("\n", "").replace("'", "")
        file_entry += "file vidout%s.flv\n" % vid_count
        system(cmd)
        vid_count += 1

    if "video" in token.keys():
        print("--------- Video ist drin! Welches? %s ----------------" %
              token["video"])
        token_is_text = False
        cmd = "ffmpeg -i %s %s.flv%s" % (token["video"],
                                         token["video"][:3], overwrite)
        cmd = cmd.replace("\n", "").replace("'", " ")
        system(cmd)
        file_entry += "file %s.flv\n" % token["video"][:3]
    count += 1

with open("vids.txt", "w") as f:
    f.write(file_entry)

system("ffmpeg -f concat -i vids.txt -c copy final.flv%s" % overwrite)

system("ffmpeg -i final.flv -c:a copy -c:v mpeg4 final.mp4%s" % overwrite)
