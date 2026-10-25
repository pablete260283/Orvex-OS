from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
app=QApplication([])
view=QWebEngineView();view.resize(1920,1080);view.setWindowTitle('ORVEX preview test host')
view.load(QUrl.fromLocalFile(str(Path(__file__).resolve().parents[1]/'preview/ORVEX-0.2.html')));view.show()
app.exec()
