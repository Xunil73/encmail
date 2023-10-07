#!/usr/bin/python3


# dieses Script sendet eine Email mit dem Standardtext über meinen 
# Emailaccount harald.seiler@aikq.de
# Das zum Verbindungsaufbau benötigte smtp-Serverpasswort wird 
# aus dem Gnome-Keyring (der automatisch bei der Anmeldung entsperrt wird)
# mittels des keyring Moduls geholt. 

from email.mime.text import MIMEText
from email.header import Header
import smtplib
import keyring
import gnupg


gpg = gnupg.GPG(gnupghome='/home/harry/.gnupg')

msg_raw = 'das ist eine erste Testmail die verschlüsselt werden muss'
msg_data = gpg.encrypt(msg_raw, 'harald.seiler@aikq.de')
msg = str(msg_data)
subj = '...'
frm = 'harald.seiler@aikq.de'
to = 'dj5my@ok.de'

mail = MIMEText(msg, 'plain', 'utf-8')
mail['Subject'] = Header(subj, 'utf-8')
mail['From'] = frm
mail['To'] = to

smtp = smtplib.SMTP('smtp.aikq.de')
smtp.starttls()
smtp.login('harald.seiler@aikq.de', keyring.get_password("email","harald.seiler@aikq.de"))
smtp.sendmail(frm, [to], mail.as_string())
smtp.quit()

