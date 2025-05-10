import sys
import os
import threading
import warnings
from pytube import YouTube
from pydub import AudioSegment
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QFrame, QProgressBar,)
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QFont
import yt_dlp

# Suppress warnings
warnings.filterwarnings("ignore")

class WorkerSignals(QObject):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    transcription = pyqtSignal(str)

class TranscriptionWorker(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()
        # Initialize Vosk model
        from vosk import Model, KaldiRecognizer  # Corrected import
        self.model = Model(r"D:\PP\TexTube_desktop\vosk-model-hi-0.22\vosk-model-hi-0.22")
        self.recognizer = KaldiRecognizer(self.model, 16000)  # Corrected class

    def download_audio_with_ytdlp(self, url, output_file="downloaded_audio.wav"):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloaded_audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists("downloaded_audio.wav"):
            os.rename("downloaded_audio.wav", output_file)

    def split_audio(self, input_file, chunk_length_ms=30000):
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_channels(1)  # Ensure mono
        audio = audio.set_sample_width(2)  # Ensure 16-bit PCM
        chunks = []
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunk_file = f"chunk_{i // chunk_length_ms}.wav"
            chunk.export(chunk_file, format="wav")
            chunks.append(chunk_file)
        return chunks

    def transcribe_audio_whisper(self, filename):
        # REMOVE THIS ENTIRE FUNCTION
        model = whisper.load_model(self.model_size)
        result = model.transcribe(filename)
        return result["text"]

    def transcribe_audio_vosk(self, filename):
        import wave
        import json  # Add missing import
        wf = wave.open(filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Audio file must be WAV format mono PCM")
            
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                results.append(self.recognizer.Result())
        results.append(self.recognizer.FinalResult())
        return " ".join([json.loads(x)['text'] for x in results if x])

    def run(self):
        try:
            download_path = "downloaded_audio.wav"

            self.signals.progress.emit("Starting download...", 10)
            self.download_audio_with_ytdlp(self.url, download_path)
            self.signals.progress.emit("Download completed!", 30)

            self.signals.progress.emit("Processing audio...", 40)
            audio_chunks = self.split_audio(download_path)
            self.signals.progress.emit("Audio processing completed!", 50)

            full_transcription = ""
            chunk_progress = 50
            progress_per_chunk = 40 / len(audio_chunks)

            for i, chunk in enumerate(audio_chunks, 1):
                self.signals.progress.emit(f"Transcribing part {i} of {len(audio_chunks)}...", 
                                        int(chunk_progress))
                transcription = self.transcribe_audio_vosk(chunk)
                full_transcription += transcription + "\n"
                os.remove(chunk)
                chunk_progress += progress_per_chunk

            self.signals.transcription.emit(full_transcription)
            self.signals.progress.emit("Transcription completed successfully!", 100)
            
            if os.path.exists(download_path):
                os.remove(download_path)
            
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))

class ModernFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            ModernFrame {
                background-color: #2A2A2A;
                border-radius: 10px;
                border: 1px solid #3A3A3A;
            }
        """)

class TranscriptionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TextTube')
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #00FFFF;
                font-size: 19px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3A3A3A;
                border-radius: 5px;
                background-color: #2A2A2A;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #008B8B;
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00AEAE;
            }
            QTextEdit {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 5px;
                padding: 10px;
                color: #FFFFFF;
            }
            QProgressBar {
                border: 2px solid #3A3A3A;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #008B8B;
            }
        """)

        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel
        left_panel = ModernFrame()
        left_layout = QVBoxLayout()
        
        # URL input section
        url_label = QLabel('Enter YouTube Video URL:')
        url_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        
        # Add URL input widgets
        left_layout.addWidget(url_label)
        left_layout.addWidget(self.url_input)

       
       
        
        # Transcribe button
        self.transcribe_button = QPushButton('Start Transcription')
        self.transcribe_button.setFixedHeight(40)
        left_layout.addWidget(self.transcribe_button)
        
        # Progress section
        self.progress_label = QLabel('Progress:')
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_output = QTextEdit()
        self.progress_output.setReadOnly(True)
        
        # Add progress widgets
        left_layout.addWidget(self.progress_label)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.progress_output)
        
        left_panel.setLayout(left_layout)
        
        # Right panel
        right_panel = ModernFrame()
        right_layout = QVBoxLayout()
        
        transcription_label = QLabel('Transcription:')
        transcription_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.transcription_output = QTextEdit()
        self.transcription_output.setReadOnly(True)
        
        right_layout.addWidget(transcription_label)
        right_layout.addWidget(self.transcription_output)
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
        # Connect button to function
        self.transcribe_button.clicked.connect(self.start_transcription)

    def update_progress(self, message, progress_value):
        self.progress_output.append(message)
        self.progress_bar.setValue(progress_value)

    def update_transcription(self, text):
        self.transcription_output.setText(text)

    def handle_error(self, error_message):
        self.progress_output.append(f"Error: {error_message}")
        self.progress_output.append("Transcription failed.")
        self.transcribe_button.setEnabled(True)
        self.progress_bar.setValue(0)

    def handle_finished(self):
        self.transcribe_button.setEnabled(True)

    def start_transcription(self):
        video_url = self.url_input.text().strip()
        if not video_url:
            self.progress_output.append("Please enter a YouTube URL")
            return

        # Remove all model selection related code
        self.worker = TranscriptionWorker(video_url)
        self.transcribe_button.setEnabled(False)
        self.progress_output.clear()
        self.transcription_output.clear()
        self.progress_bar.setValue(0)

        # Connect signals
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.transcription.connect(self.update_transcription)
        self.worker.signals.error.connect(self.handle_error)
        self.worker.signals.finished.connect(self.handle_finished)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TranscriptionApp()
    ex.show()
    sys.exit(app.exec_())