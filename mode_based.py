import sys
import os
import threading
import warnings
from pytube import YouTube
from pydub import AudioSegment
import whisper
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QFrame, QProgressBar,
    QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor, QFont
import yt_dlp

# Suppress warnings
warnings.filterwarnings("ignore")

class WorkerSignals(QObject):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    transcription = pyqtSignal(str)

class TranscriptionWorker(threading.Thread):
    def __init__(self, url, model_size):
        super().__init__()
        self.url = url
        self.model_size = model_size
        self.signals = WorkerSignals()

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
        chunks = []
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunk_file = f"chunk_{i // chunk_length_ms}.wav"
            chunk.export(chunk_file, format="wav")
            chunks.append(chunk_file)
        return chunks

    def transcribe_audio_whisper(self, filename):
        model = whisper.load_model(self.model_size)
        result = model.transcribe(filename)
        return result["text"]

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
                transcription = self.transcribe_audio_whisper(chunk)
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

class ModelSelectionFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            ModelSelectionFrame {
                background-color: #2A2A2A;
                border-radius: 10px;
                border: 1px solid #3A3A3A;
                padding: 10px;
                margin: 10px 0;
            }
            QRadioButton {
                color: #00FFFF;
                padding: 5px;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                background-color: #008B8B;
                border: 2px solid #00FFFF;
                border-radius: 7px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 7px;
            }
            QLabel {
                color: #FF6B6B;
                padding: 5px;
            }
        """)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Model Selection")
        title.setFont(QFont('Arial', 12, QFont.Bold))
        title.setStyleSheet("color: #00FFFF;")
        layout.addWidget(title)

        # Model selection radio buttons
        self.model_group = QButtonGroup()
        
        models = [
            ("Base", "Fastest - Good for English"),
            ("Small", "Fast - Better for multiple languages"),
            ("Medium", "Slower - High accuracy"),
            ("Large", "Slowest - Highest accuracy")
        ]
        
        for i, (model, desc) in enumerate(models):
            radio = QRadioButton(f"{model} ({desc})")
            self.model_group.addButton(radio, i)
            layout.addWidget(radio)
            if model == "Base":  # Default selection
                radio.setChecked(True)

        # Notice section
        notice_text = """
<span style='color: #FF6B6B; font-weight: bold;'>Notice Regarding Model Selection and System Requirements</span><br><br>
<span style='color: #00FFFF;'>
• As you increase the model size, accuracy improves, but processing time increases significantly.<br><br>
• <span style='color: #FF6B6B; font-weight: bold;'>Important:</span> "Large" mode requires:<br>
  - Intel Core i7 processor (or equivalent)<br>
  - Minimum 16GB RAM<br>
  Using "Large" mode below these specs may harm your device.<br><br>
• "Base" mode provides sufficient accuracy for English language videos.<br><br>
• For international languages or lower quality audio, use "Small" or "Medium" models.
</span>
"""
        notice = QLabel(notice_text)
        notice.setWordWrap(True)
        notice.setTextFormat(Qt.RichText)
        notice.setStyleSheet("""
            QLabel {
                background-color: #232323;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(notice)
        
        self.setLayout(layout)

    def get_selected_model(self):
        return ["base", "small", "medium", "large"][self.model_group.checkedId()]

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

        # Add model selection frame
        self.model_selection = ModelSelectionFrame()
        left_layout.addWidget(self.model_selection)
        
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

        selected_model = self.model_selection.get_selected_model()
        
        # Additional warning for large model
        if selected_model == "large":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("You've selected the 'Large' model")
            msg.setInformativeText("This model requires high system specifications (Intel Core i7 or equivalent, 16GB+ RAM). "
                                 "Using it on lower-spec systems may cause issues. Do you want to continue?")
            msg.setWindowTitle("Performance Warning")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            
            if msg.exec_() == QMessageBox.No:
                return

        self.transcribe_button.setEnabled(False)
        self.progress_output.clear()
        self.transcription_output.clear()
        self.progress_bar.setValue(0)

        self.worker = TranscriptionWorker(video_url, selected_model)
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