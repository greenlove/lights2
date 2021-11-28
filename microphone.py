import pyaudio
import wave
import struct
import math
import redis
import datetime
import numpy as np

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 1024 #4096 # 2^12 samples for buffer
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'test1.wav' # name of .wav file

audio = pyaudio.PyAudio() # create pyaudio instantiation
r = redis.Redis()

print(dir(audio))

for index in range(0, audio.get_device_count()):
    print(str(index) + "--" + str(audio.get_device_info_by_index(index)))

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
print("listening")

# loop through stream and append audio chunks to frame array
#for ii in total:
start = datetime.datetime.now()
loudness_sum = 0
average_window = 200
current_weight = 1.0 / average_window
prev_weight = 1.0 - current_weight
variances = []
loudnesses = []
variance_sum = 0
total_chunks = 0
timestep = 1.0 / samp_rate
freq = np.fft.fftfreq(chunk, timestep)
freq_side = freq[range(int(freq.size/2))]
f_low = 60
f_high = 150
f_indices = [x for x in range(freq_side.size) if (freq_side[x] > f_low and freq_side[x] < f_high)]


print("f_indices: " + str(f_indices))

while True:
    data = stream.read(chunk, exception_on_overflow=False))

    total_chunks+=1

    X = np.frombuffer(data, np.ushort)
    fft = np.fft.fft(X)
    fftside = abs(fft[range(int(fft.size/2))])

    loudness = 0
    for index in f_indices:
        loudness += fftside[index]**2
    #loudness = 10.0 * np.log10(np.mean(X*X))
    #print ("loudness: " + str(loudness))
    loudnesses.append(loudness)
    loudness_sum += loudness
    if len(loudnesses) > average_window:
        old_loud = loudnesses.pop(0)
        loudness_sum -= old_loud

    average_loudness = loudness_sum / len(loudnesses)
    d = {}
    d["loudness"] = loudness
    d["avg_loudness"] = average_loudness
    var = pow(loudness - average_loudness, 2)
    variances.append(var)
    variance_sum += var
    if len(variances) > average_window:
        old_var = variances.pop(0)
        variance_sum -= old_var

    stdev = math.sqrt(variance_sum / len(variances))
    d["stdev_loudness"] = stdev
    r.hmset("acoustics", d)
    
    #n = datetime.datetime.now()
    #s = (n - start).total_seconds()
    #print ("chunks/sec:", float(total_chunks) / float(s))
    
        
    #frames.append(data)
#print(str(data))
# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

