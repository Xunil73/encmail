#!/usr/bin/python3

### TODO ###
# rename keyring user 'gpg_posteo' to neutral name in ALL Files
### TODO END ###

import os
import keyring


conffile='/home/harry/DATA/Entwicklung/git/encmail/encmail.conf'



print("die Datei wird angelegt...\n")
emailadress = input("Ihre Emailadresse: ")
emailserver = input("Name des Mailservers: ")
gpg_excludes = input("Schlagwörter die auf Schlüssel passen\ndie ausgeblendet werden sollen\n(kommagetrennte Tags): ")
text='# config-File fuer encmail\n# diese Datei wurde durch makeEncmailConf.py erstellt \
      \n# Editieren sie diese File nach eigenen Anforderungen oder loeschen sie sie\n \
      \n# und erzeugen eine neue Datei durch Ausführen von Encmail \
      \n#\n#\nEMAIL:' + emailadress + \
     '\n#\nSERVER:' + emailserver + '\n# \
      \n# Schlüssel bei denen folgende Schlagwörter auftauchen werden in der \
      \n# Übersicht der Schlüssel ausgeblendet und stehen nicht zur Auswahl\n# \
      \nGPG_EXCLUDES:' + gpg_excludes + '\n#\n#  \
      \n# Entsprechende Daten sind in \n# ' + conffile + '\n# gespeichert. Starten Sie Encmail neu um mit \
      \n# den Einstellungen verschlüsselte Texte zu senden\n'

try:
  fobj = open(conffile, "w")
  fobj.write(text)
except:
  print("Fehler bei Dateioperation")
finally:
  fobj.close()

mail_passwd_ok=False
while mail_passwd_ok != True:
  mail_passwd = input("Passwort für den Emailaccount: ")
  mail_ref_passwd = input("Password wiederholen: ")
  if mail_passwd == mail_ref_passwd:
    mail_passwd_ok=True
    print("die Passwörter stimmen überein.\nPasswort wird im Keyring gespeichert.")
  else:
    print("die Passwörter stimmen nicht überein!")

gpg_passwd_ok=False
while gpg_passwd_ok != True:
  gpg_passwd = input("Passwort für GPG-Key: ")
  gpg_ref_passwd = input("Passwort wiederholen: ")
  if gpg_passwd == gpg_ref_passwd:
    gpg_passwd_ok=True
    print("die Passwörter stimmen überein.\nPasswort wird im Keyring gespeichert.")
  else:
    print("die Passwörter stimmen nicht überein!")

try:
  keyring.set_password("email", emailadress, mail_passwd)
  keyring.set_password("gpg_posteo", emailadress, gpg_passwd)
except:
  print("Fehler - Passwörter konnten nicht im Keyring gespeichert werden.")
finally:
  mail_passwd=None
  mail_ref_passwd=None
  gpg_passwd=None
  gpg_ref_passwd=None

