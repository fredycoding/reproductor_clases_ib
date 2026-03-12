pip install pyinstaller
pyinstaller --noconfirm --windowed --name SecureAudioPlayer --add-data "secure_audio_app\frontend;secure_audio_app\frontend" app.py
