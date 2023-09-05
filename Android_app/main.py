import datetime
from os.path import join
from kivy.app import App
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

# checking platform for asking permission
if platform == 'android':
    from kivy.uix.button import Button
    from kivy.uix.modalview import ModalView
    from kivy.clock import Clock
    from android import api_version, mActivity
    from android.permissions import request_permissions, check_permission, \
        Permission

class AndroidPermissions:
    ''' 
    The AndroidPermissions class is a class that handle permissions
    If the user selects "Don't Allow" for a permission then, the only way to enable
    the permission is to go to the app settings. The AndroidPermissions class gives 
    the user an additional chance to allow the permission if they selected "Don't Allow" once.

    The __init__() method of the AndroidPermissions class takes two arguments: 
    the start_app_callback function and the dont_gc variable. 
    
    The start_app_callback function is the function that will be called when the app is started.
    The dont_gc variable is a boolean variable that indicates whether or not the class should 
    be garbage collected.
    
    The on_start() method of the AndroidPermissions class sets the dont_gc 
    variable to False; This prevents the class from being garbage collected before the start_app_callback()
    function is called.
    
    The start_app() method of the AndroidPermissions class sets the dont_gc variable to None. 
    This allows the class to be garbage collected after the start_app_callback() function is called.
    '''
    def __init__(self, start_app = None):
        self.permission_dialog_count = 0
        self.start_app = start_app
        if platform == 'android':
            self.permissions = [Permission.RECORD_AUDIO, Permission.READ_EXTERNAL_STORAGE]
            self.permission_status([],[])
        elif self.start_app:
            self.start_app()

    def permission_status(self, permissions, grants):
        ''' checks for permission status '''
        granted = True
        for p in self.permissions:
            granted = granted and check_permission(p)
        if granted:
            if self.start_app:
                self.start_app()
        elif self.permission_dialog_count < 3:
            Clock.schedule_once(self.permission_dialog)  
        else:
            self.no_permission_view()
        
    def permission_dialog(self, dt):
        ''' updates permission '''
        self.permission_dialog_count += 1
        request_permissions(self.permissions, self.permission_status)

    @mainthread
    def no_permission_view(self):
        ''' if either of the permissions is not granted, a message is shown.
            which basically is a full-screen button with button_text as message'''
        view = ModalView()
        view.add_widget(Button(text='Permission NOT granted.\n\n' +\
                               'Tap to quit app.\n\n\n' +\
                               'If you selected "Don\'t Allow",\n' +\
                               'enable permission with App Settings.',
                               on_press=self.bye))
        view.open()

    def bye(self, instance):
        ''' exiting from app if button is pressed '''
        mActivity.finishAndRemoveTask() 


from jnius import autoclass
# imporing Android API's using pyjnius's autoclass method
MediaRecorder = autoclass('android.media.MediaRecorder')
AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder') 


class AndroidMediaRecorder(App):
    ''' This class is responsible for managing GUI and recording AUDIO'''
    def build(self):
        '''' The build() method creates a simple user interface with two buttons: "Record" button and a "Stop" button. 
          The "Record" button starts recording audio, and the "Stop" button stops recording audio.'''
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Press 'Record' to start recording")
    
        self.record_button = Button(text="Record")
        self.record_button.bind(on_press=self.start)
    
        self.stop_button = Button(text="Stop")
        self.stop_button.bind(on_press=self.stop)
        self.stop_button.disabled = True
    
        # adding widget to screen and returning GUI  
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.record_button)
        self.layout.add_widget(self.stop_button) 
        return self.layout
        
    def start(self, instance):
        self.label.text = "Recording..."
        self.record_button.disabled = True
        self.stop_button.disabled = False
        # calling record_audio()
        self.record_audio()

    def record_audio(self):
        ''' 
        This function was created seprately beacuse; as start() method handels GUI it was hindering creation of object 
        resulting in exceptions and erros.
        The record_audio method creates a MediaRecorder object and sets the audio source,
        output format, and encoder. The MediaRecorder object is then prepared and started.
        '''
        self.recorder = MediaRecorder()
        self.recorder.setAudioSource(AudioSource.MIC)
        self.recorder.setOutputFormat(OutputFormat.THREE_GPP)
        self.recorder.setOutputFile(self.file_name)
        self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)
        self.recorder.prepare()
        self.recorder.start()

    def stop(self, instance):
        ''' The stop() method stops the MediaRecorder object, releases resources. '''
        self.recorder.stop()
        self.recorder.release()
        self.recorder = None    
        self.label.text = "Recording stopped"
        self.record_button.disabled = False
        self.stop_button.disabled = True

        #printing recorded byte data (would be visible in logs)
        with open(self.file_name,"rb") as f:
            data = f.read()
            print(data)

    def on_start(self):
        '''
        The on_start() method is called when the app is started.
        This method creates a variable called dont_gc and assigns it to an instance of the AndroidPermissions class.
        The AndroidPermissions class is a class that helps to prevent the app from being garbage collected before 
        the user has a chance to grant the necessary permissions.
        '''
        self.dont_gc = AndroidPermissions(self.start_app)

    def start_app(self):
        '''
        The start_app() method is called when the app is first started. 
        This method gets the external cache directory of the app and uses it to create a file name for the audio recording.
        '''
        self.dont_gc = None        
        cache = mActivity.getApplicationContext().getExternalCacheDir()
        date = datetime.datetime.now().strftime("%y_%m_%d")
        time = datetime.datetime.now().strftime("%H_%M_%S")
        self.recorded_filename = f"audiomerge{date}at{time}.wav"
        if cache:
            self.file_name = join(str(cache.toString()),self.recorded_filename)

if __name__ == '__main__':
    AndroidMediaRecorder().run()
