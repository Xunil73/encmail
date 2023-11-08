#!/usr/bin/python3


# TUTORIALS
# https://www.pythonguis.com/tutorials/pyside6-widgets/
# https://www.pythonguis.com/tutorials/pyside6-creating-your-first-window/
# https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTextEdit.html

gnupg_dir = '/home/harry/.gnupg'
email_login_name = 'harald.seiler@aikq.de'
email_server = 'smtp.aikq.de'
key_user = email_login_name
email_recipient = 'dj5my@ok.de'



from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QMessageBox, QGroupBox, QCheckBox, QGridLayout, QScrollArea, QDialogButtonBox
from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QTextDocument
import sys
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import keyring
import gnupg

class ChooseRecipientsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
      
        gpg=gnupg.GPG(gnupghome='/home/harry/.gnupg')
        pubkeys=gpg.list_keys()
        emails = []
        for element in pubkeys:
            emails.extend(element['uids'])

        excludes = ["signing", "Debian", "Tails", "Qubes", "Release", "Kali", "Archlinux", "Eddie", "Ubuntu",
                    "Signing", "VeraCrypt", "Mint", "testschluessel_"]

        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        for email in emails:
            if any(x in email for x in excludes):
                continue
            checkbox = QCheckBox(email)
            self.vbox.addWidget(checkbox)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.vbox.addWidget(self.buttonbox)

        self.widget.setLayout(self.vbox)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 800, 600)
        self.setWindowTitle('Scroll Area Demo')
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("encrypted mail")

        self.button = QPushButton("Empfänger auswählen")
        self.textBrowser = QTextEdit()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textBrowser)
        self.layout.addWidget(self.button)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(self.centralWidget)

        self.button.clicked.connect(self.on_clicked)
        self.textBrowser.textChanged.connect(self.on_text_changed)

    # fetch the pasted text, decrypt and verify the signature and display it
    def on_text_changed(self):
        gpg = gnupg.GPG(gnupghome=gnupg_dir)
        compare_str = '-----BEGIN PGP MESSAGE-----'
        if self.textBrowser.find(compare_str, QTextDocument.FindBackward) :
            encrypted_msg = self.textBrowser.toPlainText()
            verified = gpg.verify(encrypted_msg)
            decrypted_msg = gpg.decrypt(encrypted_msg)
            
            validSig = False
            msgbox = QMessageBox()
            if decrypted_msg.trust_level is not None:
                msgbox.setWindowTitle('%s' % decrypted_msg.username)     
                validSig = True
            else:
                msgbox.setWindowTitle("Mail nicht signiert!")
            # this is the only way to get the german umlauts working:
            msgbox.setText(str(decrypted_msg).encode('latin-1').decode('latin-1'))
            if validSig:   
                msgbox.setInformativeText("<font color=\"green\">gültige Signatur von:\n%s</font>" % decrypted_msg.username)
            else:
                msgbox.setInformativeText("<font color=\"red\">Mail nicht signiert!</font>")
            msgbox.show()
            msgbox.exec()    
            self.textBrowser.clear()    

    def show_exception_box(self, errormsg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle('Fehler')
        msgbox.setInformativeText(errormsg)
        msgbox.setStandardButtons(QMessageBox.Cancel)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.show()
        msgbox.exec()
        app.quit()

    def on_clicked(self):
        self.choosenRecip=ChooseRecipientsWindow()
        self.choosenRecip.show()


    # fetch the typed text, encrypt and sign it and send it to recipient
    def sendMail(self):
        self.button.setStyleSheet('color: green')
        self.button.setText("senden...")
        self.button.repaint()    # we have to repaint the button because the code doesnt reach the event loop
        try:
            gpg = gnupg.GPG(gnupghome=gnupg_dir)
            msg_raw = self.textBrowser.toPlainText()
            self.textBrowser.clear()
            msg_data = gpg.encrypt(msg_raw, email_recipient, sign=key_user, passphrase=keyring.get_password("gpg_aikq", key_user))
            msg = str(msg_data)
            subj = '...'
            frm = email_login_name
            to = email_recipient

            mail = MIMEText(msg, 'plain', 'utf-8')
            mail['Subject'] = Header(subj, 'utf-8')
            mail['From'] = frm
            mail['To'] = to
        except ValueError as e:
            errormsg = "gpg error:\n" + str(e)
            self.show_exception_box(errormsg)
        try:
            smtp = smtplib.SMTP(email_server)
            smtp.starttls()
            smtp.login(email_login_name, keyring.get_password("email", key_user))
            smtp.sendmail(frm, [to], mail.as_string())
            smtp.quit()
            app.quit()
        except BaseException as e:
            errormsg = "mailserver error\n" + str(e)            
            self.show_exception_box(errormsg)



app = QApplication(sys.argv)


window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()


