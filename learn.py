from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
import os

# Dans chaque fichier
import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
def ajouter_cours(titre, thematique, niveau):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO cours (titre, thematique_id, niveau) VALUES (%s, %s, %s)"
        cursor.execute(query, (titre, thematique, niveau))
        connection.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout du cours: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def mod_cours(cours_id, titre, thematique, niveau):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "UPDATE cours SET titre = %s, thematique_id = %s, niveau = %s WHERE cours_id = %s"
        cursor.execute(query, (titre, thematique, niveau, cours_id))
        connection.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de la modification du cours: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def supr_cours(cours_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM cours WHERE cours_id = %s"  
        cursor.execute(query, (cours_id,))
        connection.commit()
        return cursor.rowcount > 0  
    except mysql.connector.Error as e:
        print(f"Erreur SQL lors de la suppression : {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def add_chapitre(cours_id: int, titre: str, contenu: str, ordre: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # Vérifier si l'ordre existe déjà
        cursor.execute("SELECT ordre FROM chapitres WHERE cours_id = %s AND ordre = %s", (cours_id, ordre))
        if cursor.fetchone():
            print(f"Erreur : L'ordre {ordre} existe déjà pour ce cours.")
            return False

        # Insérer le chapitre avec l'ordre spécifié
        query = """
        INSERT INTO chapitres (cours_id, titre, contenu, ordre)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (cours_id, titre, contenu, ordre))
        connection.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erreur SQL : {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def mod_chapitre(chapitre_id: int, nouveau_titre: str = None, nouveau_contenu: str = None, nouvel_ordre: int = None) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        updates = []
        params = []

        # Gestion des paramètres optionnels
        if nouveau_titre:
            updates.append("titre = %s")
            params.append(nouveau_titre)
        if nouveau_contenu:
            updates.append("contenu = %s")
            params.append(nouveau_contenu)
        if nouvel_ordre is not None:
            # Vérifier si l'ordre est déjà utilisé
            cursor.execute("SELECT chapitres_id FROM chapitres WHERE ordre = %s AND cours_id = (SELECT cours_id FROM chapitres WHERE chapitres_id = %s)", (nouvel_ordre, chapitre_id))
            existing = cursor.fetchone()
            if existing and existing[0] != chapitre_id:
                print(f"Erreur : L'ordre {nouvel_ordre} est déjà utilisé.")
                return False

            updates.append("ordre = %s")
            params.append(nouvel_ordre)

        if not updates:
            print("Aucune modification spécifiée.")
            return False

        # Construction dynamique de la requête
        query = f"UPDATE chapitres SET {', '.join(updates)} WHERE chapitres_id = %s"
        params.append(chapitre_id)
        
        cursor.execute(query, tuple(params))
        connection.commit()
        return cursor.rowcount > 0

    except mysql.connector.Error as e:
        print(f"Erreur SQL : {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def suppr_chapitre(chapitre_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM chapitres WHERE chapitres_id = %s"
        cursor.execute(query, (chapitre_id,))
        connection.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Erreur SQL : {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_all_thematiques():
    """Récupère toutes les thématiques disponibles"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT DISTINCT thematique_id FROM cours WHERE thematique_id IS NOT NULL ORDER BY thematique_id"
        cursor.execute(query)
        results = cursor.fetchall()
        return [str(row[0]) for row in results]
    except Exception as e:
        print(f"Erreur lors de la récupération des thématiques: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_niveaux_by_thematique(thematique_id):
    """Récupère tous les niveaux disponibles pour une thématique donnée"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT DISTINCT niveau FROM cours WHERE thematique_id = %s ORDER BY niveau"
        cursor.execute(query, (thematique_id,))
        results = cursor.fetchall()
        return [row[0] for row in results]
    except Exception as e:
        print(f"Erreur lors de la récupération des niveaux: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_cours_by_thematique_niveau(thematique_id, niveau):
    """Récupère tous les cours pour une thématique et un niveau donnés"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT cours_id, titre FROM cours WHERE thematique_id = %s AND niveau = %s ORDER BY titre"
        cursor.execute(query, (thematique_id, niveau))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erreur lors de la récupération des cours: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_chapitres_by_cours_id(cours_id):
    """Récupère les chapitres triés par ordre"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT chapitres_id, titre, contenu, ordre 
        FROM chapitres 
        WHERE cours_id = %s 
        ORDER BY ordre
        """
        cursor.execute(query, (cours_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erreur : {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_cours_info(cours_id):
    """Récupère les informations détaillées d'un cours"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT titre, thematique_id, niveau FROM cours WHERE cours_id = %s"
        cursor.execute(query, (cours_id,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Erreur lors de la récupération du cours: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def add_media(url: str, media_type: str) -> int:
    """Ajoute un nouveau média"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO media (url, type) VALUES (%s, %s)",
            (url, media_type)
        )
        connection.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Erreur add_media: {e}")
        return None

def modify_media(media_id: int, new_url: str = None, new_type: str = None) -> bool:
    """Modifie un média existant"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        updates = []
        params = []
        
        if new_url:
            updates.append("url = %s")
            params.append(new_url)
        if new_type:
            updates.append("type = %s")
            params.append(new_type)
            
        if not updates:
            return False
            
        query = f"UPDATE media SET {', '.join(updates)} WHERE media_id = %s"
        params.append(media_id)
        
        cursor.execute(query, tuple(params))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur modify_media: {e}")
        return False

def delete_media(media_id: int) -> bool:
    """Supprime un média"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "DELETE FROM media WHERE media_id = %s",
            (media_id,)
        )
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur delete_media: {e}")
        return False
    
def link_media_to_chapitre(chapitre_id: int, media_id: int) -> bool:
    """Lie un média à un chapitre"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # Vérifie que le chapitre ET le média existent
        cursor.execute("SELECT 1 FROM chapitres WHERE chapitres_id = %s", (chapitre_id,))
        if not cursor.fetchone():
            print(f"Chapitre {chapitre_id} introuvable")
            return False
            
        cursor.execute("SELECT 1 FROM media WHERE media_id = %s", (media_id,))
        if not cursor.fetchone():
            print(f"Média {media_id} introuvable")
            return False

        # Mise à jour
        cursor.execute(
            "UPDATE chapitres SET media_id = %s WHERE chapitres_id = %s",
            (media_id, chapitre_id)
        )
        connection.commit()
        return cursor.rowcount > 0
        
    except mysql.connector.Error as e:
        print(f"Erreur SQL link_media: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def remove_media_from_chapitre(chapitre_id: int) -> bool:
    """Supprime l'association média d'un chapitre"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE chapitres SET media_id = NULL WHERE chapitres_id = %s",
            (chapitre_id,)
        )
        connection.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Erreur SQL remove_media: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_media_for_chapitre(chapitre_id: int) -> dict:
    """Récupère le média lié à un chapitre"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT m.url, m.type 
            FROM media m
            JOIN chapitres c ON c.media_id = m.media_id
            WHERE c.chapitres_id = %s
        """, (chapitre_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Erreur get_media: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_last_chapitre_id(cours_id: int) -> int:
    """Récupère l'ID du dernier chapitre (par ordre) pour un cours donné"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT chapitres_id 
        FROM chapitres 
        WHERE cours_id = %s 
        ORDER BY ordre DESC 
        LIMIT 1
        """
        cursor.execute(query, (cours_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Erreur : {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_qcms_for_cours(cours_id: int):
    """Récupère les QCMs associés à un cours, triés par ordre"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = "SELECT * FROM qcm WHERE cours_id = %s ORDER BY ordre"
        cursor.execute(query, (cours_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erreur lors de la récupération des QCMs: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_last_chapitre_by_order(cours_id: int) -> int:
    """Récupère l'ID du dernier chapitre (par ordre) pour un cours donné"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT chapitres_id 
        FROM chapitres 
        WHERE cours_id = %s 
        ORDER BY ordre DESC 
        LIMIT 1
        """
        cursor.execute(query, (cours_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Erreur : {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def save_progression(discord_id: int, cours_id: int, chapitre_en_cours: int, qcm_id: int, score: float, validated: bool) -> bool:
    """Sauvegarde la progression d'un utilisateur pour un cours"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT * FROM progression WHERE discord_id = %s AND cours_id = %s",
            (discord_id, cours_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            query = """
            UPDATE progression 
            SET chapitre_en_cours = %s, qcm_id = %s, score = %s, validated = %s, date = %s
            WHERE discord_id = %s AND cours_id = %s
            """
            cursor.execute(query, (
                chapitre_en_cours, 
                qcm_id, 
                score, 
                validated, 
                datetime.now(), 
                discord_id, 
                cours_id
            ))
        else:
            query = """
            INSERT INTO progression (discord_id, cours_id, chapitre_en_cours, qcm_id, score, validated, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                discord_id, 
                cours_id, 
                chapitre_en_cours, 
                qcm_id, 
                score, 
                validated, 
                datetime.now()
            ))
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Erreur save_progression: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_last_progression(discord_id: int, cours_id: int) -> int:
    """Récupère le dernier chapitre complété par un utilisateur pour un cours"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT chapitre_id 
        FROM suivi
        WHERE discord_id = %s AND cours_id = %s
        ORDER BY date_activite DESC 
        LIMIT 1
        """
        cursor.execute(query, (discord_id, cours_id))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Erreur get_last_progression: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def is_course_completed(discord_id: int, cours_id: int) -> bool:
    """Vérifie si un utilisateur a validé un cours"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT etat
        FROM suivi
        WHERE discord_id = %s AND cours_id = %s AND type_activite = 'qcm'
        ORDER BY date_activite DESC 
        LIMIT 1
        """
        cursor.execute(query, (discord_id, cours_id))
        result = cursor.fetchone()
        return result and result[0] == 'termine'
    except Exception as e:
        print(f"Erreur is_course_completed: {e}")
        return False
    finally:
        cursor.close()
        connection.close()
        
def update_chapitre_media(chapitre_id: int, new_media_id: int) -> bool:
    """Modifie le média associé à un chapitre"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # Vérifier que le nouveau média existe
        cursor.execute("SELECT 1 FROM media WHERE media_id = %s", (new_media_id,))
        if not cursor.fetchone():
            print(f"Média {new_media_id} introuvable")
            return False

        # Mettre à jour le chapitre
        cursor.execute(
            "UPDATE chapitres SET media_id = %s WHERE chapitres_id = %s",
            (new_media_id, chapitre_id)
        )
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur update_chapitre_media: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_all_cours():
    """Récupère tous les cours disponibles"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT cours_id, titre, thematique_id, niveau FROM cours"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Erreur lors de la récupération des cours: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
