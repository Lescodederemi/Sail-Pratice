import os
import imapclient
import pyzmail
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')

def traiter_email(email_body, email_num):
    # Recherche de la chaîne contenant 'ecmwf' ou 'gfs' et récupère les données associées
    if "ecmwf" in email_body:
        chaine = email_body.split("ecmwf:")[1].split("\n")[0]  # Prend la première ligne après 'ecmwf:'
    elif "gfs" in email_body:
        chaine = email_body.split("gfs:")[1].split("\n")[0]  # Prend la première ligne après 'gfs:'
    else:
        print(f"❌ Aucun modèle météo trouvé dans le mail {email_num}.")
        return None

    # Découpe la chaîne en parties
    valeurs = chaine.split("|")[0]  # Récupère la première partie avant le '|'
    zones = valeurs.split(",")  # Divise la chaîne en 4 valeurs (latitude, longitude)

    # Comparaison avec les zones définies
    # Zone 1: -90,90,-180,0
    if zones == ['-90', '90', '-180', '0']:
        return "Zone 1"
    # Zone 2: -90,90,0,90
    elif zones == ['-90', '90', '0', '90']:
        return "Zone 2"
    # Zone 3: -90,90,90,180
    elif zones == ['-90', '90', '90', '180']:
        return "Zone 3"
    else:
        print(f"⚠️ Zones non reconnues pour le mail {email_num}: {zones}")
        return None
    
# Fonction pour interroger la boîte mail et traiter les emails
def traiter_emails():
    # Connexion à la boîte mail
    with imapclient.IMAPClient(IMAP_SERVER, ssl=True) as client:
        client.login(EMAIL, PASSWORD)
        client.select_folder('INBOX', readonly=True)

        # Recherche des messages
        messages = client.search(['FROM', 'sub-server@saildocs.com'])

        # Vérification de l'existence de messages
        if not messages:
            print("❌ Aucun message trouvé.")
            return

        # Parcours de tous les messages
        for email_num, msgid in enumerate(messages, 1):
            raw_message = client.fetch([msgid], ['BODY[]'])
            message = pyzmail.PyzMessage.factory(raw_message[msgid][b'BODY[]'])

            # Récupération du corps du message
            if message.text_part:
                body = message.text_part.get_payload().decode(message.text_part.charset or 'utf-8', errors='replace')
            elif message.html_part:
                body = message.html_part.get_payload().decode(message.html_part.charset or 'utf-8', errors='replace')
            else:
                print(f"❌ Aucun contenu texte lisible dans l'email {email_num}.")
                continue

            # Traite l'email et détecte la zone
            zone = traiter_email(body, email_num)

            if zone:
                print(f"Mail {email_num} : Zone détectée : {zone}")
            else:
                print(f"Mail {email_num} : Zone non détectée.")

# Appel de la fonction pour traiter les emails
if __name__ == "__main__":
    traiter_emails()


def get_last_message():
    with imapclient.IMAPClient(IMAP_SERVER, ssl=True) as client:
        client.login(EMAIL, PASSWORD)
        client.select_folder('INBOX', readonly=True)

        messages = client.search(['FROM', 'sub-server@saildocs.com'])
        if not messages:
            print("❌ Aucun message trouvé.")
            return None

        last_msg_id = messages[-1]
        raw_message = client.fetch([last_msg_id], ['BODY[]'])
        message = pyzmail.PyzMessage.factory(raw_message[last_msg_id][b'BODY[]'])
        return message
