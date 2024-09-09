import pyaudio
import numpy as np
import math
import bpy
from bpy.app.handlers import persistent

#Audio setup
pa = pyaudio.PyAudio()
CHUNK = 1024  # Samples: 1024,  512, 256, 128
INDEX = 1
dict = pa.get_device_info_by_index(INDEX)
RATE = int(dict.get("defaultSampleRate"))
FORMAT = pyaudio.paInt16
CHANNELS = dict.get("maxInputChannels")

def reformat(index_in):
    INDEX = index_in
    
    dict = pa.get_device_info_by_index(INDEX)
    RATE = int(dict.get("defaultSampleRate"))
    FORMAT = pyaudio.paInt16
    CHANNELS = dict.get("maxInputChannels")
    
    return pa.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=INDEX)

stream = reformat(INDEX)
#End audio setup

#Vars
SMOOTHING = 0.2
LOWMID = 20
MIDHIGH = 6000
VARDICT = {"lev": 0, 
            "r": 1, 
            "l": 2, 
            "freq": 3}#, 
            #"low": 4,  
            #"mid": 5, 
            #"high": 6}
VARATTR = [[], [], [], []]#, [], [], []
VARMULT = [[], [], [], []]#, [], [], []

def update(var):
    bpy.ops.ui.copy_data_path_button(full_path=True)
    clipboard = bpy.context.window_manager.clipboard

    if clipboard in VARATTR[VARDICT[var]]:
        return
    else:
        if ((isinstance(eval(clipboard), float)) or (isinstance(eval(clipboard), int))):
            VARATTR[VARDICT[var]].append(clipboard)
            VARMULT[VARDICT[var]].append(1)
        else:
            return
            
        
#End vars

#sound functions
def peak(data):
    return np.abs(np.max(data)) / 1000

def left_peak(data):
    dataL = data[0::2]
    return np.abs(np.max(dataL)) / 1000

def right_peak(data):
    dataR = data[1::2]
    return np.abs(np.max(dataR)) / 1000


def fft_peak_freq(data):
    ys = np.abs(np.fft.fft(data))
    xs=np.arange(CHUNK,dtype=float)
    length = (len(ys) / 2)
    ys = ys[:int(CHUNK / 2)]
    xs = xs[:int(CHUNK / 2)]
    #frequency of bin n = RATE * n / length
    #bin of frequency n = np.ceil(length * n / RATE)
    return float(xs[np.minimum(np.argmax(ys), len(xs)-1)])

'''
def low_peak(data):
    ys = np.abs(np.fft.fft(data))
    length = (len(ys) / 2)
    ys = ys[:int(CHUNK / 2)]
    cutoff = int(np.ceil(length * LOWMID / RATE))
    ys = ys[:cutoff]
    if (len(ys) != 0):
        return np.abs(np.max(ys)) / 100000
    else:
        return 0

def mid_peak(data):
    ys = np.abs(np.fft.fft(data))
    length = (len(ys) / 2)
    ys = ys[:int(CHUNK / 2)]
    cutoff1 = int(np.ceil(length * LOWMID / RATE))
    cutoff2 = int(np.ceil(length * MIDHIGH / RATE))
    ys = ys[cutoff1:cutoff2]
    if (len(ys) != 0):
        return np.abs(np.max(ys)) / 100000
    else:
        return 0

def high_peak(data):
    ys = np.abs(np.fft.fft(data))
    length = (len(ys) / 2)
    ys = ys[:int(CHUNK / 2)]
    cutoff = int(np.ceil(length * MIDHIGH / RATE))
    ys = ys[cutoff:]
    if (len(ys) != 0):
        return np.abs(np.max(ys)) / 100000
    else:
        return 0
'''

FUNCTION = [peak, left_peak, right_peak, fft_peak_freq] #, low_peak, mid_peak, high_peak
#end sound functions

def remove(param1, param2):
    del VARATTR[param1][param2]
    del VARMULT[param1][param2]

def isValidPath(str):
    try:
        eval(str)
        return True
    except:
        return False

def change(data):
    for i in range(0,len(FUNCTION)):
        for j in range(0,len(VARATTR[i])):
            if (isValidPath(VARATTR[i][j])):
                old = eval(VARATTR[i][j])
                new = FUNCTION[i](data) * VARMULT[i][j]
                new = ((new - old) * (1-SMOOTHING)) + old
                if (isinstance(eval(VARATTR[i][j]), int)):
                    exec(VARATTR[i][j] + '=' + str(int(new)))
                else:
                    exec(VARATTR[i][j] + '=' + str(new))
            else:
                remove(i, j)    

def render(scene):
    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False),dtype=np.int16)
    change(data)

bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(render)

#begin tests
render(bpy.context.scene)
#end tests



