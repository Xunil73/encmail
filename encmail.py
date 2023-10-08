#!/usr/bin/python3


# TUTORIALS
# https://www.pythonguis.com/tutorials/pyside6-widgets/
# https://www.pythonguis.com/tutorials/pyside6-creating-your-first-window/
# https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTextEdit.html

gnupg_dir = '/home/harry/.gnupg'
email_login_name = 'harald.seiler@aikq.de'
email_server = 'smtp.aikq.de'
key_user = 'harald.seiler@aikq.de'
email_recipient = 'dj5my@ok.de'


from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout
import sys
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import keyring
import gnupg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("sichere Mail an Harry")

        self.button = QPushButton("sicher Senden")
        self.textBrowser = QTextEdit()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textBrowser)
        self.layout.addWidget(self.button)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(self.centralWidget)

        self.button.clicked.connect(self.on_clicked)

    def on_clicked(self):
        gpg = gnupg.GPG(gnupghome=gnupg_dir)

        msg_raw = self.textBrowser.toPlainText()
        self.textBrowser.clear()
        msg_data = gpg.encrypt(msg_raw, key_user)
        msg = str(msg_data)
        subj = '...'
        frm = email_login_name
        to = email_recipient

        mail = MIMEText(msg, 'plain', 'utf-8')
        mail['Subject'] = Header(subj, 'utf-8')
        mail['From'] = frm
        mail['To'] = to

        smtp = smtplib.SMTP(email_server)
        smtp.starttls()
        smtp.login('harald.seiler@aikq.de', keyring.get_password("email", email_login_name))
        smtp.sendmail(frm, [to], mail.as_string())
        smtp.quit()
        app.quit()
        

app = QApplication(sys.argv)


window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()


