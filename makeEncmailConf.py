#!/usr/bin/python3

import keyring


conffile='/home/harry/DATA/Entwicklung/git/encmail/encmail.conf'



print("die Datei wird angelegt...\n")
emailadress = input("Ihre Emailadresse: ")
emailserver = input("Name des Mailservers: ")
gpg_excludes = input("Schlagwörter die auf Schlüssel passen\ndie ausgeblendet werden sollen\n(kommagetrennte Tags):")
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

