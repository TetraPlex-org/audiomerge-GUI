import wave
import server
import client
import pyaudio 
import datetime
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen

class Welcome(Screen):
    '''This class inherits kivy's screen class(for multiple screen) , display's welcome message
       with lisence info and a continue button which switches screen to setallite/central screen '''
    
    # initialising Screen class with super method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # welcome text label
        welcome_label = Label(
            text="Welcome to AudioMerge\na TetraPlex Product\n\nlicensed under GPL3 Copyright TetraPlex 2023",
            font_size='35sp', 
            halign='center'
        )

        # continue button
        start_button = Button(
            text='continue',
            size_hint=(None, None),
            size=(200, 50),  # Set button size
            pos_hint={'center_x': 0.5, 'top': 0.2},
            on_release=self.switch_to_options
        )
        
        # adding widgets to welcome window
        self.add_widget(welcome_label)
        self.add_widget(start_button)
        
    # when button is pressed, current screen is changed to root/main window
    def switch_to_options(self, button_instance):
        self.manager.current = "client_server_option"

class ClientServerOption(Screen):
    ''' This class inherits kivy's screen class(for multiple screen) , give user option to choose to be central or setallite node '''
    
    # initialising Screen class with super method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # AnchroLayout for label
        self.label_layout = AnchorLayout(anchor_x='center',anchor_y='top',padding=10)
        self.label = Label(text="choose which node this device should run",font_size='35sp',size_hint_y=None)

        # GridLayout for buttons
        self.button_layout = GridLayout(cols=2,spacing=80,padding=150)
        self.central_button = Button(text="central",size_hint=(7,2),size=(200,50),on_press= self.switch_to_central)
        self.setallite_button = Button(text="setallite",size_hint=(7,2),size=(200,50),on_press= self.switchto_setallite)

        # adding widgets to screen
        self.label_layout.add_widget(self.label)
        self.button_layout.add_widget(self.central_button)
        self.button_layout.add_widget(self.setallite_button)
        self.add_widget(self.label_layout)
        self.add_widget(self.button_layout)

    # methods to switch screen to central
    def switch_to_central(self, button_instance):
            self.manager.current = "server"
            serverthread.start()

    # methods to switch screen to setallite
    def switchto_setallite(self, button_instance):
            self.manager.current = "client"

class Root_window(Screen):
    ''' This class represents our root window, which contains main functionality of app 
    i.e, audio recording '''

    # initializing Screen class with super() method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # creating a box label_layout(child widgets on top of main root window)
        self.label_layout = AnchorLayout(anchor_x='center',anchor_y='top',padding=10)
        self.label = Label(text="Press 'Record' to start recording",font_size='35sp',size_hint_y=None)

        # record_button, whihc triggers "start_recording" function on press, enabled bydeault
        self.button_layout = GridLayout(cols=2,spacing=80,padding=150)  

        self.record_button = Button(text="Record",
                                    size_hint=(None, None),
                                    size=(200, 50))
        
        self.record_button.bind(on_press=self.start_recording)

        # stop_button, whihc triggers "stop_recording" function on press, disabled bydefault
        self.stop_button = Button(text="Stop",
                                  size_hint=(None, None),
                                  size=(200, 50))
        
        self.stop_button.bind(on_press=self.stop_recording)
        self.stop_button.disabled = True


        # adding widgets to boxlayout and returning label_layout
        self.label_layout.add_widget(self.label)
        self.button_layout.add_widget(self.record_button)
        self.button_layout.add_widget(self.stop_button)
        self.add_widget(self.label_layout)
        self.add_widget(self.button_layout)

    def start_recording(self, instance):
        '''
        Handles GUI changes and audio recording initiation.
        It opens an audio stream and starts recording using the callback method.

        also checks whether pyaudio object has been successfuly initialized or not and if not 
        then raises an OS error
        '''

        '''as recording is intintated: 
                 label changes to recording.
                record button is disabled.
                 stop_record button is enabled.'''
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
        

def server_thread():
    ''' this function is called when server screen is loaded, it starts server thread'''
    global ip_address, port
    ip_address = server.get_ipaddress()
    port = server.get_port()
    server_socket = server.bind(ip_address,port)
    server.listen(server_socket)
    server.handle_client(server_socket)

# creating a thread for server
serverthread = threading.Thread(target= server_thread)
serverthread.daemon = True

class Server(Screen):
    # initializing Screen class with super() method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        ''' this function is called when server screen is loaded, it starts server thread'''
        Clock.schedule_interval(self.update, 1)
        self.label_layout = AnchorLayout(anchor_x='center',anchor_y='top',padding=10)
        self.label = Label(text="central",font_size='35sp',size_hint_y=None)

        self.grid_layout = GridLayout(cols=2,spacing=10,padding=100,row_force_default=True,row_default_height=50)

        self.ip_address_label = Label(text="IP Address: ",font_size='30sp')
        self.ip_address = Label(text=str(ip_address),font_size='30sp')

        self.port_label = Label(text="Port: ",font_size='30sp')
        self.port = Label(text=str(port),font_size='30sp')

        self.client_label = Label(text="Number of clients: ",font_size='30sp')
        self.client_number = Label(text=str(server.number_of_clients),font_size='30sp')

        self.num_of_connected_clients_label = Label(text="Number of connected clients: ",font_size='30sp')
        self.num_of_connected_clients = Label(text= self.client_number.text,font_size='30sp')

        self.label_layout.add_widget(self.label)
        self.grid_layout.add_widget(self.ip_address_label)
        self.grid_layout.add_widget(self.ip_address)
        self.grid_layout.add_widget(self.port_label)
        self.grid_layout.add_widget(self.port)
        self.grid_layout.add_widget(self.num_of_connected_clients_label)   
        self.grid_layout.add_widget(self.num_of_connected_clients)

        self.add_widget(self.label_layout)
        self.add_widget(self.grid_layout)

    def update(self,*args):
        ''' this function is called every second to update number of connected clients'''
        self.client_number.text = str(server.number_of_clients)
        self.ip_address.text = str(ip_address)
        self.port.text = str(port)

    def on_leave(self, serverthread):
        ''' this function is called when server screen is left, it stops server thread'''
        serverthread.stop()


class Client(Screen):
    ''' This class inherits kivy's screen class(for multiple screen), and used to connect to central node'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # setallite node
        self.label_layout = AnchorLayout(anchor_x='center',anchor_y='top',padding=10)
        self.label = Label(text="setallite node",font_size='35sp',size_hint_y=None)

        # input layout
        self.input_layout = GridLayout(cols=2,spacing=30,padding=100,row_force_default=True,row_default_height=50)
        self.ip_address_lable = Label(text="IP Address :",font_size='30sp')
        self.ip_address = TextInput(font_size='20sp',multiline=False)
        self.port_label = Label(text="Port :",font_size='30sp')
        self.port = TextInput(font_size='20sp',multiline=False)

        # connect button
        self.connect_button_layout = AnchorLayout(anchor_x='center', anchor_y='center', padding=30)
        self.connect_button = Button(text="connect", size_hint=(None, None), size=(200, 50), on_press=self.connect_to_server)

        # continue button
        self.continue_button_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', padding=40)
        self.continue_button = Button(text="continue", size_hint=(None, None), size=(200, 50), on_press=self.switch_to_main)

        # adding widgets to client window
        self.label_layout.add_widget(self.label)
        self.input_layout.add_widget(self.ip_address_lable)
        self.input_layout.add_widget(self.ip_address)
        self.input_layout.add_widget(self.port_label)
        self.input_layout.add_widget(self.port)
        self.connect_button_layout.add_widget(self.connect_button)
        self.continue_button_layout.add_widget(self.continue_button)

        # adding layouts to client window
        self.add_widget(self.label_layout)
        self.add_widget(self.input_layout)
        self.add_widget(self.connect_button_layout)
        self.add_widget(self.continue_button_layout)
    
    def switch_to_main(self, button_instance):
        self.manager.current = "main"
        
    # connecting to setallite central
    def connect_to_server(self, button_instance):
        self.msg = Label(text="connecting....")
        # connect function from client.py
        status = client.connect(self.ip_address.text, self.port.text)

        if status == 200:
            print("connected")
            self.label_layout = BoxLayout(orientation='vertical',spacing=60)
            self.label = Label(text="connected !",font_size='25sp',size_hint_y=None, height=350, font_name='CutiveMono-Regular.ttf')
            self.label_layout.add_widget(self.label)
            self.add_widget(self.label_layout)
        else:
            print(status)
            self.label_layout = BoxLayout(orientation='vertical',spacing=60)
            self.label = Label(text= status,font_size='25sp',size_hint_y=None, height=350, font_name='CutiveMono-Regular.ttf')
            self.label_layout.add_widget(self.label)
            self.add_widget(self.label_layout)

class AudiomergeApp(App):
    ''' this class inherits App class of Kivy,"build" method creates and returns an 
        instance of the ScreenManager that manages different screens of the app'''
    
    def build(self):
        # creating an instance of Screenmanager class
        sm = ScreenManager()

        # adding Screen to Screenmanager
        sm.add_widget(Welcome(name ="welcome"))
        sm.add_widget(ClientServerOption(name="client_server_option"))
        sm.add_widget(Server(name="server"))
        sm.add_widget(Client(name="client"))
        sm.add_widget(Root_window(name="main"))
        return sm
    

if __name__ == '__main__':
    AudiomergeApp().run()
