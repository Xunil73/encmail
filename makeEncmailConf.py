#!/usr/bin/python3

import keyring


conffile='/home/harry/DATA/Entwicklung/git/encmail/encmail.conf'



print("die Datei wird angelegt...\n")
emailadress = input("Ihre Emailadresse: ")
emailserver = input("Name des Mailservers: ")
gpg_excludes = input("Schlagwörter die auf Schlüssel passen\ndie ausgeblendet werden sollen\n(kommagetrennte Tags):")
text='# config-File fuer encmail\n# bitte eigene Werte nach dem Muster\
         \n#    EMAIL:user@planet.terra ergaenzen\n\nEMAIL:' + emailadress + \
        '\n\nSERVER:' + emailserver + '\n \
         \nGPG_EXCLUDES:' + gpg_excludes + '\n\n# ******* END OF FILE *********\n\n  \
         Entsprechende Daten sind in \n' + conffile + '\ngespeichert. Starten Sie\n \
         Encmail neu um mit den Einstellungen verschlüsselte Texte zu senden\n'

try:
  fobj = open(conffile, "w")
  fobj.write(text)
except:
  print("Fehler bei Dateioperation")
finally:
  fobj.close()

