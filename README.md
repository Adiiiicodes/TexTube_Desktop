# TexTube_Desktop
  

```markdown
# TextTube 🎥✍️  
**TextTube** is a Python-based desktop application designed to transcribe YouTube videos into text. With a sleek user interface and the power of OpenAI's Whisper model, this app makes it simple to convert audio from YouTube videos into written content.  

---

## 🚀 Features  

- **Transcribe Any YouTube Video**: Paste a YouTube link, and the app handles everything from downloading audio to transcription.  
- **Model Flexibility**: Choose from four Whisper AI models (`Base`, `Small`, `Medium`, `Large`) based on your accuracy and speed requirements.  
- **Real-Time Progress Updates**: Stay informed with live updates during audio processing and transcription.  
- **Error Handling**: Detects and resolves issues during transcription to ensure smooth performance.  
- **Chunk-Based Processing**: Efficiently handles long audio by splitting it into smaller chunks for better processing.  
- **Modern UI**: Built with PyQt5 for a user-friendly and visually appealing experience.  

---

## 🛠️ Tech Stack  

- **Python**: Core programming language.  
- **PyQt5**: For building a responsive and modern graphical user interface.  
- **Whisper by OpenAI**: AI-powered transcription engine.  
- **yt-dlp**: High-performance YouTube downloader for extracting audio.  
- **Pydub**: For splitting and processing audio files efficiently.  

---

## 📋 Requirements  

- **Python 3.10+**  
- **System Specifications** (recommended for "Large" Whisper model):  
  - Processor: Intel Core i7 or equivalent.  
  - RAM: 16GB or higher.  

Install the required dependencies by running:  

```bash
pip install -r requirements.txt
```

---

## 📦 Installation  

1. Clone this repository:  
   ```bash
   git clone https://github.com/your-username/TextTube.git
   cd TextTube
   ```  

2. Install the required dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  

3. Run the application:  
   ```bash
   python main.py
   ```  

---

## 🖥️ Usage  

1. Launch the app by running `main.py`.  
2. Paste a YouTube video URL into the provided input field.  
3. Select one of the four transcription models:  
   - `Base`: Fastest, good for English.  
   - `Small`: Fast, better for multiple languages.  
   - `Medium`: Slower, high accuracy.  
   - `Large`: Slowest, highest accuracy (requires high system specs).  
4. Click "Start Transcription" and wait for the transcription to complete.  
5. View the transcription in the app, or copy it for further use.  

---

## 🚧 Challenges  

- **Packaging with PyInstaller**: Ensured all dependencies, including the Whisper model assets, were included in the standalone executable.  
- **Memory Management**: Optimized performance for chunk-based processing to handle long videos efficiently.  

---

## 🌟 Future Enhancements  

- Add support for multiple output formats (e.g., `.txt`, `.srt`).  
- Optimize performance for systems with lower specifications.  
- Include support for additional languages.  
- Open-source the project for contributions and improvements.  

---

## 🤝 Contributing  

Contributions, issues, and feature requests are welcome!  

1. Fork the repository.  
2. Create a new branch (`git checkout -b feature/YourFeature`).  
3. Commit your changes (`git commit -m 'Add your feature'`).  
4. Push to the branch (`git push origin feature/YourFeature`).  
5. Open a pull request.  

---

## 🛡️ License  

This project is licensed under the [MIT License](LICENSE).  

---

## 📫 Contact  

If you have any questions or feedback, feel free to reach out:  
- **Email**: [nalawadeaditya017@gmail.com](mailto:nalawadeaditya017@gmail.com)  
- **LinkedIn**: [Aditya Nalawade]([https://linkedin.com/in/your-profile](https://www.linkedin.com/in/aditya-nalawade-a4b081297/))  
- **GitHub**: [Adiiiicodes](https://github.com/Adiiiicodes)  

---

### 📌 Acknowledgments  

- Special thanks to **OpenAI** for the Whisper model and **yt-dlp** for their incredible tools.  
- Inspired by the potential of AI in simplifying everyday tasks.  

---

**Let’s make transcriptions easier, one video at a time!** 🎉  
```

### How to Use It
  
- If you have additional dependencies or special instructions for running the app, include them under **Requirements** or **Installation**.  

This README should provide clear documentation and attract collaborators or users to your project! 🚀