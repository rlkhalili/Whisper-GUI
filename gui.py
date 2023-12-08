import os
import whisper
import pyaudio
import wave
import threading
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout, QLineEdit, QComboBox
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

class TranscriptionTool(QWidget):
    def __init__(self):
        super().__init__()
        # initialize audio components first
        self.initializeAudioComponents()  
        self.initializeUI()
        self.initTranscriptionModel()

    def initializeUI(self):
        self.setWindowTitle('Whisper Transcription Tool')
        self.resize(800, 175)
        self.layout = QVBoxLayout(self)
        self.setupDeviceSelection()
        self.setupRecordingUI()
        self.setupPathSelection()
        self.setupStatusLabel()

    def initializeAudioComponents(self):
        self.frames = []
        self.is_recording = False
        self.p = pyaudio.PyAudio()

    def initTranscriptionModel(self):
        # TODO: Allow user to change models
        self.model = whisper.load_model("base.en")

    def setupDeviceSelection(self):
        self.deviceComboBox = QComboBox()
        self.populateDeviceList()
        self.layout.addWidget(self.deviceComboBox)

    def setupRecordingUI(self):
        buttonsLayout = QHBoxLayout()

        self.toggleRecordingButton = QPushButton()
        self.toggleRecordingButton.setIcon(QIcon('recordIcon.png'))  # use red circle icon
        self.toggleRecordingButton.clicked.connect(self.toggleRecording)
        self.toggleRecordingButton.setFixedSize(QSize(50, 50))
        buttonsLayout.addWidget(self.toggleRecordingButton)

        self.transcribeButton = QPushButton('Transcribe Audio')
        self.transcribeButton.clicked.connect(self.transcribeAudio)
        buttonsLayout.addWidget(self.transcribeButton)

        self.layout.addLayout(buttonsLayout)

    def setupPathSelection(self):
        self.savePathLayout = QHBoxLayout()
        self.savePathEdit = QLineEdit(os.getcwd())
        self.savePathLayout.addWidget(self.savePathEdit)
        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.browseSavePath)
        self.savePathLayout.addWidget(self.browseButton)
        self.layout.addLayout(self.savePathLayout)

    def setupStatusLabel(self):
        self.statusLabel = QLabel("Ready")
        self.layout.addWidget(self.statusLabel)

    def populateDeviceList(self):
        info = self.p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for i in range(0, num_devices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                self.deviceComboBox.addItem(device_info.get('name'), i)

    def toggleRecording(self):
        if self.is_recording:
            self.stopRecording()
        else:
            self.startRecording()

    def startRecording(self):
        if not self.is_recording:
            self.is_recording = True
            self.toggleRecordingButton.setIcon(QIcon('stopIcon.png'))
            self.statusLabel.setText("Recording...")
            self.frames = []

            device_index = self.deviceComboBox.currentData()
            self.stream = self.p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True,
                                      input_device_index=device_index, frames_per_buffer=1024)
            threading.Thread(target=self.record).start()

    def record(self):
        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stopRecording(self):
        if self.is_recording:
            self.is_recording = False
            self.toggleRecordingButton.setIcon(QIcon('recordIcon.png'))
            self.statusLabel.setText("Stopping and saving recording...")
            self.stream.stop_stream()
            self.stream.close()
            self.saveAndTranscribeRecording()

    def saveAndTranscribeRecording(self):
        # saving the recorded audio and transcribe it.
        filename = QFileDialog.getSaveFileName(self, "Save File", "", "WAV files (*.wav)")
        if filename[0]:
            wf = wave.open(filename[0], 'wb')
            wf.setnchannels(2)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            self.transcribeAudio(filename[0])

    def transcribeAudio(self, filename=None):
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3)")
        if filename:
            self.statusLabel.setText("Transcribing...")
            try:
                result = self.model.transcribe(filename, fp16=False)
                self.saveTranscriptionToFile(result["text"])
            except Exception as e:
                self.statusLabel.setText(f"An error occurred during transcription: {str(e)}")

    def saveTranscriptionToFile(self, text):
        savePath = self.savePathEdit.text()
        filename = os.path.join(savePath, self.getCurrentDateTime() + '.txt')
        try:
            with open(filename, 'w') as file:
                file.write(text)
            self.statusLabel.setText(f"File saved: {filename}")
        except Exception as e:
            self.statusLabel.setText(f"An error occurred: {str(e)}")

    def getCurrentDateTime(self):
        currentDatetime = datetime.now()
        return currentDatetime.strftime("%B %d, %Y - %H %M")

    def browseSavePath(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.savePathEdit.setText(directory)

# Application execution
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet("""
        QWidget { font-size: 14px; }
        QPushButton { background-color: #0078D7; color: white; border-radius: 5px; padding: 6px; min-height: 30px; }
        QPushButton:hover { background-color: #0053ba; }
        QLineEdit { border: 1px solid #c7c7c7; border-radius: 3px; padding: 2px; }
        QLabel { color: #333333; }
    """)
    window = TranscriptionTool()
    window.show()
    app.exec_()
