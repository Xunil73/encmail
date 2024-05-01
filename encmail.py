#!/usr/bin/python3


# TUTORIALS
# https://www.pythonguis.com/tutorials/pyside6-widgets/
# https://www.pythonguis.com/tutorials/pyside6-creating-your-first-window/
# https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTextEdit.html



from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QGroupBox, QCheckBox, QGridLayout, QScrollArea, QDialogButtonBox, QLabel
from PySide6.QtCore import Qt, QObject, QRunnable, QThreadPool, Signal, Slot, QSize
from PySide6.QtGui import QTextDocument, QPixmap, QImage
import sys
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import keyring
import gnupg
import os 
import subprocess


configs={'EMAIL':'', 'SERVER':'', 'GPG_EXCLUDES':''} # we have the config entrys in a dict, read the values from the file
# the following line must be changed to a hidden file in the basic home directory
conffile='/home/harry/DATA/Entwicklung/git/encmail/encmail.conf'
gnupg_dir = os.environ['HOME'] + '/.gnupg'
keyring_gpg_service = 'gpg_posteo'
keyring_email_service = 'email'

try:
  if os.path.isfile(conffile):
    fobj = open(conffile, "r")
    for line in fobj:
      if line.find('#') > -1:
        continue
      for keyword in configs:
        if line.find(keyword) > -1:
          value = line.split(':')
          temp = value[1].replace("\n", "").replace(" ", "")
          if temp.find(',') > -1:
            configs[keyword] = temp.split(',')
          else: 
            configs[keyword] = temp
  else:
    subcmd="xfce4-terminal -x bash -c \"/home/harry/DATA/Entwicklung/git/encmail/makeEncmailConf.py; exec bash\""
    subprocess.Popen(subcmd, shell=True)
    
except PermissionError:
  print('keine Berechtigung um auf encmail.conf zuzugreifen\n')

email_login_name = configs['EMAIL']
email_server = configs['SERVER']
gpg_exclude_tags = configs['GPG_EXCLUDES']

class WorkerSignals(QObject):

    finished = Signal()


class Worker(QRunnable):

    def __init__(self, all_recipients, unencryptedMessage):
        super(Worker, self).__init__()

        self.signals = WorkerSignals()

        self.recipients = all_recipients
        self.msg_raw = unencryptedMessage

    @Slot()
    def run(self):
        try:
            gpg = gnupg.GPG(gnupghome=gnupg_dir)
            msg_data = gpg.encrypt(self.msg_raw, self.recipients, always_trust=True, sign=email_login_name, passphrase=keyring.get_password(keyring_gpg_service, email_login_name))
            msg = str(msg_data)
            subj = '...'
        
            mail = MIMEText(msg, 'plain', 'utf-8')
            mail['Subject'] = Header(subj, 'utf-8')
            mail['From'] = email_login_name
            mail['To'] = ", ".join(self.recipients)
        except ValueError as e:
            errormsg = "gpg error:\n" + str(e)
            self.show_exception_box(errormsg)
        try:
            smtp = smtplib.SMTP(email_server)
            smtp.starttls()
            smtp.login(email_login_name, keyring.get_password(keyring_email_service, email_login_name))
            smtp.sendmail(email_login_name, self.recipients, mail.as_string())
            smtp.quit()
        except BaseException as e:
            errormsg = "mailserver error\n" + str(e)            
            self.show_exception_box(errormsg)
        finally:
            self.signals.finished.emit()
        
    def show_exception_box(self, errormsg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle('Fehler')
        msgbox.setInformativeText(errormsg)
        msgbox.setStandardButtons(QMessageBox.Cancel)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.show()
        msgbox.exec()
        self.signals.finished.emit()

class ConfirmWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget()
        self.setMinimumSize(QSize(300, 100))
        self.setWindowTitle('processing')
        self.setStyleSheet('background-color: darkblue; border: 3px solid #0f0;')
        self.setWindowFlags(Qt.FramelessWindowHint)
        title = QLabel("<font color=\"yellow\">sende Email...</font>")
        title.setStyleSheet('border: 0px solid #000')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        imageLbl = QLabel()
        imageLbl.setStyleSheet('border: 0px solid #000;')
        imageLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img = QImage('BriefMitSchloss.png')
        pixmap = QPixmap(img.scaledToWidth(50))
        imageLbl.setPixmap(pixmap)
        imageLbl.setScaledContents(False)
        
        layout = QHBoxLayout()
        layout.addWidget(imageLbl)
        layout.addWidget(title)
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)


class ChooseRecipientsWindow(QMainWindow):
    def __init__(self, unencryptedMessage):
        super().__init__()

        self.msg_raw = unencryptedMessage

        self.threadpool = QThreadPool()
      
        gpg=gnupg.GPG(gnupghome=gnupg_dir)
        pubkeys=gpg.list_keys()
        emails = []
        for element in pubkeys:
            emails.extend(element['uids'])

        # Keys im Keyring mit folgenden Schlagwörtern sollen nicht in der Auswahlliste auftauchen:
        excludes = gpg_exclude_tags

        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        self.checkboxes=[]
        for email in emails:
            if any(x in email for x in excludes):
                continue
            checkbox = QCheckBox(email)
            self.checkboxes += [checkbox]
            self.vbox.addWidget(checkbox)

        # Es wäre cool wenn ich die Buttonbox noch etwas anders anordnen könnte.... momentan rechts unten versteckt.
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.vbox.addWidget(self.buttonbox)


        self.widget.setLayout(self.vbox)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 800, 600)
        self.setWindowTitle('Auswahl Empfänger')
    
        self.buttonbox.button(QDialogButtonBox.Ok).clicked.connect(self.processing_recipients)
        self.buttonbox.button(QDialogButtonBox.Ok).clicked.connect(self.showConfirmWindow)
        self.buttonbox.button(QDialogButtonBox.Ok).clicked.connect(self.sendEmail)
        self.buttonbox.button(QDialogButtonBox.Cancel).clicked.connect(self.quitApp)

    def quitApp(self):
        app.quit()

    def showConfirmWindow(self):
        self.cfmWin = ConfirmWindow()
        self.cfmWin.show()
 
    def processing_recipients(self):
        recipients = ''
        for c in self.checkboxes:
            if c.isChecked():
                if c.text().find('<') == -1:
                    recipients += c.text() + ', '
                else:
                    tmp = c.text().split('<')                                
                    recipients += tmp[1].replace('>', ',')            
        recipients_without_last_comma = recipients[:-1]
        self.all_recipients = list(recipients_without_last_comma.split(','))

    def sendEmail(self):
        worker = Worker(self.all_recipients, self.msg_raw)
        worker.signals.finished.connect(self.quitApp)
        self.threadpool.start(worker)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EncMail")

        self.button = QPushButton("Empfänger auswählen")
        self.textBrowser = QTextEdit()
        self.textBrowser.setPlaceholderText('Nachricht verfassen\n\noder\n\nCodeblock hier einfügen\n(copy & paste)')
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


    def on_clicked(self):
        unencryptedMessage = self.textBrowser.toPlainText()
        self.choosenRecip=ChooseRecipientsWindow(unencryptedMessage)
        self.choosenRecip.show()



app = QApplication(sys.argv)


window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()


