""" This script extracts Joe Rogan's voice based on transcripts from rev.com.

Usage (4 arguments):
python rev_audio_extract.py path/to/transcript/eeee.txt path/to/audio/eeee.wav seg_len path/to/output_dir

where:
eeee = episode number in 4 int format (0001, 0459)
seg_len = maximum segment length in seconds (put 0 if you want to keep the original speech segments)

E.g:
python rev_audio_extract.py ../1480.txt ../1480.wav 3 ../out
"""

from pydub import AudioSegment
import datetime
import re
from math import ceil
import sys
import os
import shutil


def strip_time(text):
    # Strip timestamp from string "Joe Rogan: (00:11)\n" to string "00:11".
    return re.sub('[(){}<>\n]', '', text.split(': ', 1)[-1])


def time_str_to_sec(time_str):
    time_obj = None
    for time_format in ['%M:%S', '%H:%M:%S']:
        try:
            time_obj = datetime.datetime.strptime(time_str, time_format)
            break
        except ValueError:
            pass
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second


def get_timestamps(text, audio_len):
    prefix = 'Joe Rogan'
    next_timestamp = 3
    start_times = []
    end_times = []
    for i in range(0, len(text)):
        line = text[i]
        if prefix in line:
            start_time = time_str_to_sec(strip_time(line))
            if (i + next_timestamp) < len(text):
                end_time = time_str_to_sec(strip_time(text[i + next_timestamp]))
            else:
                end_time = audio_len

            # Exclude audio that are < 1s.
            if (end_time - start_time) > 1:
                start_times.append(start_time)
                end_times.append(end_time)

    return start_times, end_times


def further_segment(start_time, end_time, seg_len):
    seg_start_times = []
    seg_end_times = []
    if end_time - start_time > seg_len != 0:
        for i in range(start_time, end_time, seg_len):
            seg_start_times.append(i)
            if i + seg_len < end_time:
                seg_end_times.append(i + seg_len)
            else:
                seg_end_times.append(end_time)

        return seg_start_times, seg_end_times
    else:
        return [start_time], [end_time]


def main():
    transcript = sys.argv[1]
    wav = sys.argv[2]
    seg_len = int(sys.argv[3])
    episode_num = transcript[-8:].replace('.txt', '')
    output_dir = os.path.join(sys.argv[4], episode_num)

    audio = AudioSegment.from_wav(wav)
    audio_len = ceil(len(audio) / 1000)

    # Extract start and end time of Joe's speech.
    with open(transcript, 'r') as file:
        start_times, end_times = get_timestamps(file.readlines(), audio_len)

    # Make output directory.
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Extract audio.
    for i in range(0, len(start_times)):
        seg_start_times, seg_end_times = further_segment(start_times[i], end_times[i], seg_len)
        for j in range(0, len(seg_start_times)):
            start_seg = seg_start_times[j] * 1000  # Works in milliseconds
            end_seg = seg_end_times[j] * 1000
            if end_seg < len(audio):
                segment = audio[start_seg:end_seg]
            else:
                segment = audio[start_seg:]

            datetime_t1 = datetime.timedelta(seconds=seg_start_times[j])
            output_filename = episode_num + '_' + '0' + str(datetime_t1).replace(':', '_')
            segment.export(f'{output_dir}/{output_filename}.wav', format="wav")

    print("Done.")


if __name__ == '__main__':
    main()
