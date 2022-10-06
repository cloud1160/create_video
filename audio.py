#!/usr/bin/python3.9

import re
import os
import sys
import distutils.spawn


def dier(msg):
    sys.exit(msg)


def file_exists(entry):
    if os.path.exists(entry.replace("\n", "")):
        print("The file %s exists" % entry.replace("\n", ""))
        return True
    else:
        dier("The file %s doesn't exist programm stops." %
             entry.replace("\n", ""))


replace_words = {"gpus": "ge pe us", "ssh": "s s h"}

if distutils.spawn.find_executable("tts"):
    print("tts is installed: continue")
else:
    os.system("pip install tts==0.8.0")

if distutils.spawn.find_executable("sox"):
    print("sox is installed: continue")
else:
    os.system("sudo apt install sox")

filename = "video.txt"
try:
    with open(filename, 'r') as file1:
        Lines = file1.readlines()
except:
    print("create and write a video.txt file")

comment_regex = re.compile("^\s*#")
png_regex = re.compile("^image=.+\.\w+")
video_regex = re.compile("^video=.+")

tokens = []
video_data = {}
textparts = []
count = 0
for line in Lines:
    count += 1
    line.strip()
    if comment_regex.match(line):
        pass
        # print("Ignoring comment line " + line)
    elif png_regex.match(line):
        print(line[6:].replace("\n", ""))
        tokens.append({"image": line[6:]})
        file_exists(line[6:])
        # if os.path.exists(line[6:].replace("\n", "")):
        #     print("The file %s exists" % line[6:].replace("\n", ""))
        # else:
        #     dier("The file %s doesn't exist programm stops." %
        #          line[6:].replace("\n", ""))
    elif video_regex.match(line):
        tokens.append({"video": line[6:]})
        file_exists(line[6:])
        # if os.path.exists(line[6:]):
        #     print("The file %s exists" % line[6:])
        # else:
        #     dier("The file %s doesn't exist programm stops." %
        #          line[6:].replace("\n", ""))
    else:
        for word in replace_words:
            if word in line:
                line = line.replace(word, replace_words[word])
                # dier(word + " " + replace_words[word])
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
            # os.system("tts --model_name tts_models/de/thorsten/tacotron2-DDC \
            #     --out_path output%s.wav --text '%s'" % (count, sentence))
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
        cmd = '''ffmpeg -i %s -i %s vidout%s.flv''' % (
            token["image"], current_audio, vid_count)
        cmd = cmd.replace("\n", "")
        file_entry += "file vidout%s.flv\n" % vid_count
        os.system(cmd)
        vid_count += 1

    if "video" in token.keys():
        print("--------- Video ist drin! Welches? %s ----------------" %
              token["video"])
        token_is_text = False
        cmd = "ffmpeg -i %s %s.flv" % (token["video"], token["video"][:3])
        cmd = cmd.replace("\n", "")
        os.system(cmd)
        file_entry += "file %s.flv\n" % token["video"][:3]
    count += 1

with open("vids.txt", "w") as f:
    f.write(file_entry)

os.system("ffmpeg -f concat -i vids.txt -c copy final.flv")

os.system("ffmpeg -i final.flv -c:a copy -c:v mpeg4 final.mp4")

# works but the length is always ten seconds
# ffmpeg -loop 1 -i hongkong.png -i conout1.wav -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -to 00:00:10 b.mp4
