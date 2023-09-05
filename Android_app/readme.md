# workflow 

![app_build_flow drawio](https://github.com/TetraPlex-org/audiomerge-GUI/assets/72141859/7051024c-fa54-4772-a33d-8b7d20b6104c)

## Building APP
- To package/build our python code into an app, we'll use a tool [Buildozer](https://buildozer.readthedocs.io/en/latest/installation.html)
- Buildozer is a tool that aim to package mobiles application easily. It automates the entire build process, download the prerequisites like python-for-android, Android SDK, NDK
- Buildozer manages a file named buildozer.spec in your application directory, describing your application requirements and settings such as title, icon, included modules etc. It will use the specification file to create a package for Android, iOS, and more.
- You must have a Linux or OSX computer to be able to compile for Android, windows users may use `google collab` or `wsl`
- use `buildozer -v android debug` to start build process, Buildozer will start download necessary files and packaging apps
 using `buildozer.spec` file, it takes a lot of time in the build process for the first time
- once the Build process is completed, you can find the app in `bin` directory


## Checking for errors and byte data using adb
- install the app on you're android device and enable USB debugging (for logs)
- install [adb](https://www.xda-developers.com/install-adb-windows-macos-linux/) in your system
- after connecting your phone with your system
- run `adb logcat -s python` this command will filter out python activities, log related to our app
- open the app, you'll start seeing logs updating upon further interactions with app
