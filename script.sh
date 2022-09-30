#!/bin/bash
# set -x
tts

if [ $? ]; then {
    echo "tts is installed"
} else {
    pip install tts
}
fi


tts-server --model_name tts_models/de/thorsten/vits &&


if [ $? ]; then {
    echo "server was started"
}
fi

# ar[0]

# rows=wc -l video.txt

# for [ i in video.txt ]; do {
#     head -n 2 video.txt | tail -n 1

# }
# done
# curl -o ausgabe.wav http://localhost:5002/api/tts\?text\=Hallo.

while read line ; do
    if [[ $line =~ [a-z]+=[a-z]+.png ]]; then
        b=${line:6:10}
        echo "$line is a png"
        a+="image: '$b' "; 
    elif [[ $line =~ [a-z]+=[a-z]+.mp4 ]];then
        b=${line:6:10}
        echo "$line is a video"
        a+="video: '$b' ";
    else
        echo "$line is just text"
        a+="text: '$line' ";
        # text+=$line 
    fi
done < video.txt

echo "$a"
echo "next is array -------------"
array=($a)
IFS=$"\n"
for i in "${array[@]}"; do
    echo "$i";
done

# text="so ist das heutzutage"
# tts --model_name tts_models/de/thorsten/tacotron2-DDC --out_path output.wav --text "$text"