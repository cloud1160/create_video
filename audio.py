#!/usr/bin/python3
import argparse
from hashlib import md5
import distutils.spawn
import sys
from os import path, makedirs, system, mkdir
import re


def is_installed(program_name, install_command):
    if distutils.spawn.find_executable(program_name):
        print("%s is installed: continue" % program_name)
    else:
        system(install_command)


is_installed("pdf2image", "pip install pdf2image")
from pdf2image import convert_from_path


def dier(msg):
    sys.exit(msg)


def file_exists(entry):
    if entry and path.exists(entry.replace("\n", "")):
        # print("The file %s exists" % entry.replace("\n", ""))
        return True
    return False
    # dier("The file %s doesn't exist programm stops.".replace("\n", "") %
    #      entry)


def save_video_paths(file_entry):
    with open("vids.txt", "w") as f:
        f.write(file_entry)


replace_words = {"gpus": "ge pe us", "ssh": "es es ha", "https": "ha te te pe es ", "-": " minus ",
                 "/": "schraegstrich ", ":": "doppelpunkt "}

ap = argparse.ArgumentParser()

ap.add_argument("--file")
ap.add_argument("--overwrite")
ap.add_argument("--name")
args = vars(ap.parse_args())

# when y is given all files neccessary for creating the video will be overwritten
# automatically, without allowing it manually
overwrite = ""
if args["overwrite"] == "y":
    overwrite = " -y"

is_installed("tts", "pip install tts==0.8.0")
is_installed("sox", "sudo apt install sox")
is_installed("tree", "sudo apt install tree")
is_installed("espeak", "sudo apt install espeak")

if not path.exists("tmp"):
    makedirs("tmp")
if not path.exists("pdf"):
    mkdir("pdf")

Lines = []
# the program uses by default the video.txt file, this can be changed when
# another filename is given through the --file parameter
filename = "video.txt"
if file_exists(args["file"]):
    filename = args["file"]
else:
    print("%s does not exist." % args["file"])

try:
    with open(filename, 'r') as file1:
        Lines = file1.readlines()
except:
    dier("create and write a video.txt file")

comment_regex = re.compile("^\s*#")
image_regex = re.compile("^image=(.+\.\w+)")
video_regex = re.compile("^video=(.+)$")
site_regex = re.compile("^.*s=([0-9]+)\n$")

tokens = []
video_data = {}
textparts = []
count = 0
for line in Lines:
    count += 1
    line.strip()
    if comment_regex.match(line):
        pass
    elif fname := image_regex.match(line):
        filename = fname.group(1)
        if "png" in filename:
            print(filename + " is an png")
        if "pdf" in filename:
            site_number = 1
            if s_number := site_regex.match(line):
                site_number = int(s_number.group(1))
            print(filename + " is an pdf")
            images = convert_from_path(
                filename, 62, "pdf", site_number, site_number)
            filename = '%s.png' % filename
            images[0].save(filename, 'PNG')
        tokens.append({"image": filename})
        file_exists(filename)
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

last_token_was_audio = False
count = 0
vid_count = 0
file_entry = ""
for token in tokens:
    if last_token_was_audio and "audio" not in token.keys():
        system("sox %s conout%s.wav" % (filenames, count))
        current_audio = "conout%s.wav" % count
    if "audio" in token.keys():
        if not last_token_was_audio:
            filenames = ""
            last_token_was_audio = True

        for filename in token["audio"]:
            filenames += filename + " "
    if "image" in token.keys():
        last_token_was_audio = False
        # creating parts of the video with an image and an audio file
        if current_audio:
            cmd = 'ffmpeg -i %s -i %s -crf 0 vidout%s.mp4%s' % (
                token["image"], current_audio, vid_count, overwrite)
            cmd = cmd.replace("\n", "").replace("'", "")
            file_entry += "file vidout%s.mp4\n" % vid_count
            system(cmd)
            vid_count += 1
        else:
            dier("No audio for this image. Write first a text and then the image")
    if "video" in token.keys():
        last_token_was_audio = False
        cmd = "ffmpeg -i %s -crf 0 -pix_fmt yuv420p -vcodec mpeg4 -vf fps=30 \
        -video_track_timescale 90000 %s.mp4%s" % (token["video"], overwrite)
        # cmd = "ffmpeg -pix_fmt yuv420p -i %s -crf 0 %s.mp4%s" % (token["video"],
        #                                         token["video"][:3], overwrite)
        cmd = cmd.replace("\n", "").replace("'", " ")
        system(cmd)
        file_entry += "file %s.mp4\n" % token["video"][:3]
    count += 1

save_video_paths(file_entry)

name = "final"
if args["name"]:
    name = args["name"]

# dier(name)
# system("ffmpeg -f concat -i vids.txt -crf 0 -c copy final.flv%s" % overwrite)
system("ffmpeg -f concat -i vids.txt -crf 0 -pix_fmt yuv420p -max_muxing_queue_size 9999 \
 %s.mp4%s" % (name, overwrite))

# system("ffmpeg -i final.flv -crf 0 -c:a copy -c:v mpeg4 final.mp4%s" % overwrite)
