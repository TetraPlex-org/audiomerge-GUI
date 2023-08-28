import wave
import pyaudio 
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
     
class AudioRecorderApp(App):
    '''
    This class inherits the "App" class of Kivy framework
    AudioRecorderApp is our main class reesponsible for handeling 
    GUI activities 
    '''
    def build(self):
        ''' build method takes care of widgets '''
        # setting up title and icon
        self.title =  "AudioMerge"
        self.icon = "icon.png"
        # creating a box layout(child widgets on top of main root window)
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Press 'Record' to start recording")
        # record_button, whihc triggers "start_recording" function on press, enabled bydeault
        self.record_button = Button(text="Record")
        self.record_button.bind(on_press=self.start_recording)
        # stop_button, whihc triggers "stop_recording" function on press, disabled bydefault
        self.stop_button = Button(text="Stop")
        self.stop_button.bind(on_press=self.stop_recording)
        self.stop_button.disabled = True
        # adding widgets to boxlayout and returning layout
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.record_button)
        self.layout.add_widget(self.stop_button)
        return self.layout
    def start_recording(self, instance):
        '''
        Handles GUI changes and audio recording initiation.
        It opens an audio stream and starts recording using the callback method.
        '''
        # as recording is intintated: 
            # label changes to recording.
            # record button is disabled.
            # stop_record button is enabled.
        self.label.text = "Recording..."
        self.record_button.disabled = True
        self.stop_button.disabled = False
        try:
            # pyaudio object
            self.audio = pyaudio.PyAudio()
            # audio stream, "input=true" => record from default microphone
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024,
                                      stream_callback=self.callback)
        except:
            raise OSError("can't access micophone")
        
        else:
        #audio streams are stored as a list in frames object
            self.frames = []
            self.stream.start_stream()
    def callback(self, in_data, frame_count, time_info, status):
        ''' A callback function for the audio stream that appends recorded audio frames to a list 
            takes in new audio data and appends it to frames object
        '''
        self.frames.append(in_data)
        return (None, pyaudio.paContinue)
    
    def stop_recording(self, instance):
        ''' stops & terminates recording and ensures streaming and use of resources has stopped '''
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
       
        # when this functon is called:
            # lable changes to "recording stopped."
            # start_record button enables for another recording 
            # stop_record button disables until new recording begins
        self.label.text = "Recording stopped"
        self.record_button.disabled = False
        self.stop_button.disabled = True
        self.save_recorded_audio()
    def save_recorded_audio(self):
        '''
        Saves the recorded audio frames to a WAV file using the
        current date and time as part of the filename.
        '''
        date = datetime.datetime.now().strftime("%y_%m_%d")
        time = datetime.datetime.now().strftime("%H_%M_%S")
        # formating file name
        self.recorded_filename = f"audiomerge{date}at{time}.wav"
        # checking whether audio data exists
        if self.frames:
            with wave.open(self.recorded_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))
        else:
             raise ValueError("no audio data available to write")

if __name__ == '__main__':
    AudioRecorderApp().run()
