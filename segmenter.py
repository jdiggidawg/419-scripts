from pydub import AudioSegment
import sys
import datetime 

#takes audio file name as input, as well as desired segment length. 
#outputs audio files of desired segment length split from the main audio file.

def extract_podcast_num(s):
	ret = s.partition('#')[2]
	ret = ret.partition(' ')[0]
	return ret

def msec(n):
	return n*1000

def sec_to_dt(n): 
	return str(datetime.timedelta(seconds = n)) 

aud = sys.argv[1]
podcast_num = extract_podcast_num(aud)
segment_length = msec(int(sys.argv[2])) #in seconds

print(podcast_num)

audioSeg = AudioSegment.from_mp3(aud)

for i in range(0, len(audioSeg), msec(segment_length)):
	
	t1 = i
	t2 = i + segment_length 

	if t2 < len(audioSeg):	
		segment = audioSeg[t1:t2]
	else:
		segment = audioSeg[t1:]

	datetime_t1 = sec_to_dt(int(t1/1000))
	output_name = '' + str(podcast_num) + '_' + str(datetime_t1)
	#output_name = output_name.replace(':', '_')
	print(output_name)
	
	segment.export('/contents/segment_data/'+podcast_num+'/'+output_name+'.wav', format="wav")

