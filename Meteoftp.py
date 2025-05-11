import os
from ftplib import FTP
import imapclient
import pyzmail
import io  # Utilisation de io pour BytesIO
from config import EMAIL, PASSWORD, IMAP_SERVER, FTP_host, Ftp_user, FTP_mdp

def connexion_ftp():
    """Établit une connexion FTP avec les identifiants fournis dans config.py."""
    try:
        ftp = FTP(FTP_host)
        ftp.login(Ftp_user, FTP_mdp)
        return ftp
    except Exception as e:
        print(f"❌ Erreur de connexion FTP : {e}")
        return None

def creer_dossier_ftp(ftp, chemin):
    """Crée récursivement un chemin de dossier FTP s’il n’existe pas."""
    for part in chemin.split('/'):
        if part not in ftp.nlst():
            ftp.mkd(part)
        ftp.cwd(part)

def upload_attachment_with_zone(message, email_num, model, zone, ftp):
    """Envoie les pièces jointes d'un mail au FTP dans un dossier structuré selon le modèle et la zone."""
    for part in message.mailparts:
        if part.filename:
            filename = part.filename
            new_filename = renommer_fichier(filename, model)  # Renommage du fichier
            folder_path = f"{model}/{zone}"

            try:
                ftp.cwd('/')  # Revenir à la racine avant chaque opération
                creer_dossier_ftp(ftp, folder_path)  # Crée le dossier modèle/zone
            except Exception as e:
                print(f"❌ Erreur création dossier FTP : {e}")
                return

            payload = part.get_payload()
            if payload:
                try:
                    # Utiliser io.BytesIO pour envoyer la pièce jointe
                    ftp.storbinary(f"STOR {new_filename}", io.BytesIO(payload))
                    print(f"✅ Mail {email_num} : {new_filename} envoyé dans {folder_path}")
                except Exception as e:
                    print(f"❌ Erreur d’envoi FTP pour {new_filename} : {e}")
            else:
                print(f"⚠️ Aucune donnée dans la pièce jointe : {filename}")

def renommer_fichier(filename, model):
    """Renomme le fichier en ne gardant que le modèle et la date."""
    # Extraire la date des 8 premiers caractères après le modèle
    if model in filename:
        date_part = filename[len(model):len(model)+8]  # Exemple : "20250415"
        new_filename = f"{model}{date_part}.grb"  # Nouveau nom de fichier
        return new_filename
    return filename  # Si le modèle n'est pas trouvé, on garde le nom initial

# Fonction pour traiter les emails et renommer les pièces jointes
def traiter_emails():
    print("🔄 Début du traitement des emails...")
    try:
        with imapclient.IMAPClient(IMAP_SERVER, ssl=True) as client:
            client.login(EMAIL, PASSWORD)
            client.select_folder('INBOX', readonly=True)

            messages = client.search(['FROM', 'sub-server@saildocs.com'])

            if not messages:
                print("❌ Aucun message trouvé.")
                return

            ftp = connexion_ftp()
            if not ftp:
                print("❌ Impossible de se connecter au serveur FTP.")
                return

            for email_num, msgid in enumerate(messages, 1):
                raw_message = client.fetch([msgid], ['BODY[]', 'FLAGS'])
                message = pyzmail.PyzMessage.factory(raw_message[msgid][b'BODY[]'])

                # Récupération du body (texte brut ou HTML fallback)
                body = ""
                if message.text_part:
                    charset = message.text_part.charset or "utf-8"
                    body = message.text_part.get_payload().decode(charset, errors='replace')
                elif message.html_part:
                    charset = message.html_part.charset or "utf-8"
                    body = message.html_part.get_payload().decode(charset, errors='replace')
                else:
                    print(f"⚠️ Mail {email_num} sans contenu texte ou HTML lisible.")

                # Traite l'email et détecte la zone et le modèle
                model, zone = traiter_email(body, email_num)

                if model and zone:
                    print(f"📩 Mail {email_num} : Modèle {model}, Zone : {zone}")
                    upload_attachment_with_zone(message, email_num, model, zone, ftp)
                else:
                    print(f"⚠️ Mail {email_num} : Modèle ou zone non détectés.")

            ftp.quit()

    except Exception as e:
        print(f"❌ Erreur lors du traitement des emails : {e}")

# Fonction pour extraire le modèle et la zone du contenu de l'email
def traiter_email(email_body, email_num):
    """Fonction adaptée pour extraire le modèle et la zone à partir du contenu de l'email."""
    # Recherche de la chaîne contenant 'ecmwf' ou 'gfs' et récupère les données associées
    if "ecmwf" in email_body:
        model = "ecmwf"
    elif "gfs" in email_body:
        model = "gfs"
    else:
        print(f"❌ Aucun modèle météo trouvé dans le mail {email_num}.")
        return None, None

    # Découpe la chaîne en parties pour extraire les zones
    if model == "ecmwf":
        # Si modèle ecmwf, zones sont dans l'email, ex: "ecmwf: -90,90,-180,0"
        chaine = email_body.split("ecmwf:")[1].split("\n")[0]
    elif model == "gfs":
        # Si modèle gfs, zones sont dans l'email, ex: "gfs: -90,90,-180,0"
        chaine = email_body.split("gfs:")[1].split("\n")[0]

    zones = chaine.split("|")[0].split(",")  # Divise la chaîne en 4 valeurs (latitude, longitude)

    # Comparaison avec les zones définies
    if zones == ['-90', '90', '-180', '0']:
        zone = "zone1"
    elif zones == ['-90', '90', '0', '90']:
        zone = "zone2"
    elif zones == ['-90', '90', '90', '180']:
        zone = "zone3"
    else:
        print(f"⚠️ Zones non reconnues pour le mail {email_num}: {zones}")
        return None, None

    return model, zone

# Appel de la fonction pour traiter les emails
if __name__ == "__main__":
    traiter_emails()
