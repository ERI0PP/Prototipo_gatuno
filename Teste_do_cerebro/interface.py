import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout
)

from PySide6.QtCore import Qt

gatuno_interface = QApplication(sys.argv)

flutuante = QWidget()
flutuante.setWindowTitle("iniciar sistema")
flutuante.resize(50, 50)
flutuante.setWindowFlag(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
flutuante.setAttribute(Qt.WA_TranslucentBackground)
flutuante.move(0,1030)


chat = QWidget()
chat.setWindowTitle('Gatuno')
chat.resize(500, 125)

open_gatuno = QPushButton("G", flutuante)
open_gatuno.setStyleSheet("""
    QPushButton{
        background-color: purple;
        border-radius: 25px;
        color: white; 
        border: none;}""")
open_gatuno.resize(50, 50)

flutuante.show()

def on_off():
    if chat.isVisible():
        chat.hide()
    else: 
        chat.show()
open_gatuno.clicked.connect(on_off)

sys.exit(gatuno_interface.exec())

