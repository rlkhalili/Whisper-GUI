import os
import whisper
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout, QLineEdit

class TranscriptionTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # TODO: ALLOW USER TO CHANGE MODELS 
        self.model = whisper.load_model("base.en")

    def initUI(self):
        self.setWindowTitle('Whisper Transcription Tool')
        self.resize(800, 175)
        self.layout = QVBoxLayout(self)

        self.transcribeButton = QPushButton('Transcribe Audio')
        self.transcribeButton.clicked.connect(self.transcribeAudio)
        self.layout.addWidget(self.transcribeButton)

        self.savePathLayout = QHBoxLayout()
        self.savePathEdit = QLineEdit(os.getcwd())
        self.savePathLayout.addWidget(self.savePathEdit)
        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.browseSavePath)
        self.savePathLayout.addWidget(self.browseButton)
        self.layout.addLayout(self.savePathLayout)

        # TODO: ALLOW STATUS LABEL TO CHANGE WHEN MODEL IS BEING SWITCH (TO BE IMPLEMENTED) OR WHEN USER STARTS TRANSCRIPTION
        self.statusLabel = QLabel("Ready")
        self.layout.addWidget(self.statusLabel)

    def getDate(self):
        currentDatetime = datetime.now()
        return currentDatetime.strftime("%B %d, %Y - %H %M")

    def toFile(self, text, savePath):
        filename = os.path.join(savePath, self.getDate() + '.txt')
        try:
            with open(filename, 'w') as file:
                file.write(text)
            self.statusLabel.setText(f"File saved: {filename}")
        except Exception as e:
            self.statusLabel.setText(f"An error occurred: {str(e)}")

    def transcribeAudio(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3)")
        if filename:
            self.statusLabel.setText("Transcribing...")
            try:
                result = self.model.transcribe(filename, fp16=False)
                self.toFile(result["text"], self.savePathEdit.text())
            except Exception as e:
                self.statusLabel.setText(f"An error occurred during transcription: {str(e)}")

    def browseSavePath(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.savePathEdit.setText(directory)

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
