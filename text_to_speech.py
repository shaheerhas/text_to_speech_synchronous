# Uncomment them if you're using notebook (Google-Colab or Jupyter)
# Paste this into a cell and hit ctrl-enter
# !pip install gtts
# !pip install pydub
# !pip install mutagen

import time
import os
from gtts import gTTS
from datetime import datetime
from pydub import AudioSegment
from pydub.utils import make_chunks

#--------------------#
# Copy-Pasted this function from pydub repository

# function to speed-up the playback after creation
def speedup(seg, playback_speed=1.5, chunk_size=150, crossfade=25):
    # we will keep audio in 150ms chunks since one waveform at 20Hz is 50ms long
    # (20 Hz is the lowest frequency audible to humans)

    # portion of AUDIO TO KEEP. if playback speed is 1.25 we keep 80% (0.8) and
    # discard 20% (0.2)
    atk = 1.0 / playback_speed

    if playback_speed < 2.0:
        # throwing out more than half the audio - keep 50ms chunks
        ms_to_remove_per_chunk = int(chunk_size * (1 - atk) / atk)
    else:
        # throwing out less than half the audio - throw out 50ms chunks
        ms_to_remove_per_chunk = int(chunk_size)
        chunk_size = int(atk * chunk_size / (1 - atk))

    # the crossfade cannot be longer than the amount of audio we're removing
    crossfade = min(crossfade, ms_to_remove_per_chunk - 1)

    # DEBUG
    # print("chunk: {0}, rm: {1}".format(chunk_size, ms_to_remove_per_chunk))

    chunks = make_chunks(seg, chunk_size + ms_to_remove_per_chunk)
    if len(chunks) < 2:
        raise Exception(
            "Could not speed up AudioSegment, it was too short {2:0.2f}s for the current settings:\n{0}ms chunks at {1:0.1f}x speedup".format(
                chunk_size, playback_speed, seg.duration_seconds))

    # we'll actually truncate a bit less than we calculated to make up for the
    # crossfade between chunks
    ms_to_remove_per_chunk -= crossfade

    # we don't want to truncate the last chunk since it is not guaranteed to be
    # the full chunk length
    last_chunk = chunks[-1]
    chunks = [chunk[:-ms_to_remove_per_chunk] for chunk in chunks[:-1]]

    out = chunks[0]
    for chunk in chunks[1:]:
        out = out.append(chunk, crossfade=crossfade)

    out += last_chunk
    return out

def isTimeFormat(input):
    try:
        time.strptime(input, '%H:%M')
        return True
    except ValueError:
        return False
def process():
    inpath = "D:\\transcript\\transcript.txt"
    global outpath
    FMT = '%M:%S'
    outpath = "D:\\transcript\\audio.mp3"
    mytext = open(inpath).readlines()
    times = []
    sentences = []
    i = 0
    while i < len(mytext):
        if mytext[i] == '\n':
            i += 1
            continue
   #     if mytext[i][0].isdigit() and mytext[i][2] == ':':
        if isTimeFormat(mytext):
            times.append(mytext[i].strip())
        else:
            sentences.append(mytext[i].strip())
        i += 1
    print((sentences),'\n',(times))
    global silent_times
    silent_times = []
    global names
    names = []
    global c
    c = True
    if (not times[0].startswith("00:00")):
        dif1 = datetime.strptime(times[0], FMT) - datetime.strptime("00:00", FMT)
        dif1 = dif1.total_seconds()
        c = False
        if (dif1 > 0):
            silent_times.append(dif1)
        else:
            silent_times.append(0.0)

    if (not os.path.isdir("D:\\transcript\\temp")):
        os.mkdir("D:\\transcript\\temp")

    for i in range(len(times)):
        name = "D:\\transcript\\temp\\audio" + str(i) + ".mp3"
        names.append(name)
        try:
            gTTS(text=sentences[i], lang='en', slow=False, ).save(name)
        except:
            print("Connection to server failed. Run again, check your internet connection.")
            return
        fast_sound = AudioSegment.from_file(name)
        fast_sound = speedup(fast_sound, 1.25)
        if i < len(times) - 1:
            dif1 = datetime.strptime(times[i + 1], FMT) - datetime.strptime(times[i], FMT)
            dif1 = dif1.total_seconds()

            # m = MP3(name)
            playing_time1 = (len(fast_sound) / 1000)
            print("p1", playing_time1)
            # playing_time2 = len(fast_sound)/1000
            if (playing_time1 > dif1):
                fast_sound = fast_sound[0:dif1 * 1000]
                # print ("dif1 inside if ", dif1*1000)

        fast_sound.export(name)
        # m = MP3(name)
        playing_time1 = len(fast_sound) / 1000

        if i < len(times) - 1:
            dif2 = dif1 - playing_time1
            if (dif2 > 0):
                silent_times.append(dif2)
            else:
                silent_times.append(0)

        # print(i,playing_time1, times[i], silent_times[i])


def save():
    try:

        new = AudioSegment.silent(silent_times[0] * 1000)

        new += AudioSegment.from_mp3(names[0])

        new += AudioSegment.silent(silent_times[1] * 1000)

    except:
        print("Error opening file: ", names[0])
        time.sleep(3)

    for i in range(1, len(names) - 1):
        try:
            new += AudioSegment.from_mp3(names[i])
            # print(silent_times[i+1])
            new += AudioSegment.silent(silent_times[i + 1] * 1000)
        except:
            print("Error opening file: ", names[i])
            time.sleep(3)
    # writing mp3 files is a one liner
    # print(names[-1])
    new += AudioSegment.from_mp3(names[-1])
    new.export(outpath, format="mp3")
    # remove the temp files created
    import os
    [os.remove(i) for i in names]
    os.rmdir("D:\\transcript\\temp")


t1 = time.time()
print("Working..")
process()
print('Done')
print("Saving file..")
save()
print("Time taken: ", time.time() - t1, "seconds")
time.sleep(3)
