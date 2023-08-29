import wave
import pyaudio 
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen


class Welcome(Screen):
    '''This class inherits kivy's screen class(for multiple screen) , display's welcome message
       with lisence info and a continue button which on_release changes to screen to root window '''
    
    # initialising Screen class with super method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # welcome text label
        welcome_label = Label(
            text="Welcome to AudioMerge\na TetraPlex Product\n\nlicensed under GPL3 Copyright TetraPlex 2023",
            font_size='35sp',  # Adjust font size as needed
            halign='center'
        )

        # continue button
        start_button = Button(
            text='continue',
            size_hint=(None, None),
            size=(200, 50),  # Set button size
            pos_hint={'center_x': 0.5, 'top': 0.2},
            on_release=self.switch_to_main
        )
        
        # adding widgets to welcome window
        self.add_widget(welcome_label)
        self.add_widget(start_button)
        
    # when button is pressed, current screen is changed to root/main window
    def switch_to_main(self, button_instance):
        self.manager.current = "main"

class Root_window(Screen):
    ''' This class represents our root window, which contains main functionality of app 
    i.e, audio recording '''

    # initializing Screen class with super() method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # adding title and icon
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
        self.add_widget(self.layout)
    
    def start_recording(self, instance):
        '''
        Handles GUI changes and audio recording initiation.
        It opens an audio stream and starts recording using the callback method.

        also checks whether pyaudio object has been successfuly initialized or not and if not 
        then raises an OS error
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
            takes in new audio data and appends it to frames object '''
        
        # appending "in_data" to self.frame and continuing to record audio stream
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
        ''' Saves the recorded audio frames to a WAV file using the
        current date and time as part of the filename '''
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
     
class AudioRecorderApp(App):
    ''' this class inherits App class of Kivy,"build" method creates and returns an 
        instance of the ScreenManager that manages different screens (welcome and root_window)'''
    
    def build(self):
        # creating an instance of Screenmanager class
        sm = ScreenManager()

        # adding Screen to Screenmanager
        sm.add_widget(Welcome(name ="welcome"))
        sm.add_widget(Root_window(name="main"))
        return sm

if __name__ == '__main__':
    AudioRecorderApp().run()
     
