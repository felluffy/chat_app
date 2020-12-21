from os import system
import socket
import time
import pyaudio
import wave
import sys
import threading
from threading import Thread

class MicInput:
    def __init__(self, chunk=1024, sample_format=pyaudio.paInt32, channels=2, sample_rate=44100, inputDeviceIndex=0) -> None:
        super().__init__()
        self.chunk = chunk
        self.input_device_index = inputDeviceIndex
        self.sample_format = sample_format
        self.channels = channels
        self.sample_rate = sample_rate
        self.lock = threading.Lock()
        self.aud = None
        self.should_stop = False
        self.sock = None
        self.enabled = False

    def startMic(self, socket_to_listen_to = None, new_props=False, chunk=1024, sample_format=pyaudio.paInt32, channels=2, sample_rate=44100,  inputDeviceIndex=0):
        if new_props == True:
            self.chunk = chunk
            self.sample_format = sample_format
            self.channels = channels
            self.sample_rate = sample_rate
            self.input_device_index = inputDeviceIndex
            self.sock = socket_to_listen_to

        if socket_to_listen_to is not None:
            self.sock = socket_to_listen_to

        self.aud = pyaudio.PyAudio()
        self.audTh = Thread(target=self.run_mic, args=(), daemon=False)
        self.audTh.start()
        self.lisTh = Thread(target=self.listen, args=(), daemon=False)
        self.lisTh.start()
        self.enabled = True
        print("ret")

    def stop(self):
        self.stopHearing()
        self.stopMic()
        self.should_stop = False
        self.enabled = False
        self.aud.terminate()

    def stopHearing(self):
        self.should_stop = True
        self.lisTh.signal = False
        self.listen_stream.stop_stream()
        print(self.should_stop)
        self.lisTh.join()
        print("stop hearing")
        
    def stopMic(self):
        self.should_stop = True
        self.audTh.signal = False
        self.self_stream.stop_stream()
        print(self.should_stop)
        self.audTh.join()
        print("stopped mic")

    def listen(self): #can add deafen later
        self.listen_stream = self.aud.open(format=self.aud.get_format_from_width(4), channels=self.channels, rate=self.sample_rate, input=True, output=True, frames_per_buffer=self.chunk, input_device_index=self.input_device_index)
        self.listen_stream.start_stream()
        print("started to listen")
        while self.should_stop is False:
            data = ""
            if self.sock is not None:
                try:
                    data = self.sock.recv(self.chunk)
                except socket.error as exc:
                    print("Caught exception socket.error : %s" % exc)
            if data != "":
                self.listen_stream.write(data, self.chunk)
        
    def run_mic(self):
        self.self_stream = self.aud.open(format=self.aud.get_format_from_width(4), channels=self.channels, rate=self.sample_rate, input=True, output=True, frames_per_buffer=self.chunk, output_device_index=self.output_device_index)
        self.self_stream.start_stream()
        print("Started to write")
        while self.should_stop is False:
            data = self.self_stream.read(self.chunk)
            
            if self.sock is not None:
                try:
                    self.sock.send(data)
                except socket.error as exc:
                    print("Caught exception socket.error : %s" % exc)

        pass

    def getActiveInputDevices(self):
        if self.aud is not None:
            devices = self.aud.get_host_api_info_by_index(0)
            toRet = {}
            dev = 0
            self.aud_map = {}
            for i in range(0, devices.get('deviceCount')):
                if self.aud.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                    toRet[i] = self.aud.get_device_info_by_host_api_device_index(0, i)
                    self.aud_map[i] = dev
                    dev += 1
            return toRet
        else:
            return {}

    def getDeviceName(self, host_info):
        if host_info is not None:
            return host_info.get('name')

            
    def changeAudioInputDevice(self, index):
        # ind = -1
        # for key, val in self.aud_map.items():
        #         if val == index:
        #             ind = key
        #             break
        
        # if ind != -1:
        #     self.stopMic()
        #     try:
        #     except :
        #     self.input_device_index = ind
        #     self.audTh = Thread(target=self.run_mic, args=(), daemon=False)
        #     self.audTh.start()
        pass


    def changeAudioOutputDevice(self, index):
        #if index in self.out_map.values:
        pass

    def sec(self, frames=None, frames_per_sec=None):
        pass

    def callback (in_data, frame_count, time_info, status):
        pass

    def change_vol(self, vol_multiplier = 1):
        pass


pass