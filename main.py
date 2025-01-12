import sys
import asyncio
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from edge_tts import Communicate, VoicesManager
from tempfile import NamedTemporaryFile

class TextToSpeechApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Edge-TTS GUI By MewBaka')
        self.setGeometry(300, 300, 700, 350)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left side: Text box
        self.text_label = QLabel('转换文本:')
        self.text_input = QTextEdit(self)
        left_layout.addWidget(self.text_label)
        left_layout.addWidget(self.text_input)

        # Right side: Parameter settings
        self.language_label = QLabel('选择语言')
        self.language_combo = QComboBox(self)
        right_layout.addWidget(self.language_label)
        right_layout.addWidget(self.language_combo)

        self.model_label = QLabel('选择模型')
        self.model_combo = QComboBox(self)
        right_layout.addWidget(self.model_label)
        right_layout.addWidget(self.model_combo)

        self.file_label = QLabel('保存路径')
        self.file_input = QLineEdit(self)
        right_layout.addWidget(self.file_label)
        right_layout.addWidget(self.file_input)

        self.filename_label = QLabel('文件名（默认值 output.mp3）')
        self.filename_input = QLineEdit(self)
        right_layout.addWidget(self.filename_label)
        right_layout.addWidget(self.filename_input)

        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton('生成语音', self)
        self.save_button.clicked.connect(self.start_tts)
        self.preview_button = QPushButton('试听语音', self)
        self.preview_button.clicked.connect(self.preview)
        self.browse_button = QPushButton('选择文件夹', self)
        self.browse_button.clicked.connect(self.select_folder)

        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.preview_button)
        self.buttons_layout.addWidget(self.browse_button)

        right_layout.addLayout(self.buttons_layout)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 2)

        self.setLayout(main_layout)

        self.player = QMediaPlayer(self)

        self.load_voices()

    async def preview_tts(self, text, voice):
        try:
            tts = Communicate(text=text, voice=voice)

            with NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                temp_audio_file = tmp_file.name
                async for chunk in tts.stream():
                    if chunk["type"] == "audio":
                        tmp_file.write(chunk["data"])

            return temp_audio_file
        except Exception as e:
            if "No audio was received" in str(e):
                raise ValueError("此文本无法在此模型上输出，请检查模型语言。")
            else:
                raise e

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, '选择保存文件夹')
        if folder_path:
            self.file_input.setText(folder_path)

    def start_tts(self):
        text = self.text_input.toPlainText().strip()
        voice = self.model_combo.currentText()
        output_folder = self.file_input.text()
        filename = self.filename_input.text().strip() or 'output.mp3'

        if not text:
            self.show_error
