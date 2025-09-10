import mysql.connector
import os
from dotenv import load_dotenv
from config import DB_CONFIG 

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_table():
    """Crée la table users avec la colonne type_compte"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id BIGINT PRIMARY KEY,
            pseudo VARCHAR(100) NOT NULL,
            type_compte ENUM('free', 'premium') DEFAULT 'free',
            dernier_reset_free TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def register_user(discord_id: int, pseudo: str):
    """Enregistre l'utilisateur dans la table users"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
       
        safe_pseudo = pseudo[:100]
        
        cursor.execute("""
            INSERT INTO users (discord_id, pseudo, type_compte) 
            VALUES (%s, %s, 'free')
            ON DUPLICATE KEY UPDATE 
                pseudo = VALUES(pseudo)
        """, (discord_id, safe_pseudo))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur d'enregistrement: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


from datetime import datetime, timedelta

def get_user_status(discord_id: int):
    """Récupère le statut utilisateur avec gestion des vagues"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT *, 
                CASE 
                    WHEN dernier_reset_free <= NOW() - INTERVAL 8 HOUR THEN 1 
                    ELSE 0 
                END AS reset_needed
            FROM users 
            WHERE discord_id = %s
        """, (discord_id,))
        user = cursor.fetchone()
        
        if user and user['reset_needed']:
            cursor.execute("""
                UPDATE users 
                SET vagues_free = 3, 
                    dernier_reset_free = NOW() 
                WHERE discord_id = %s
            """, (discord_id,))
            conn.commit()
            user['vagues_free'] = 3
        
        return user
    except Exception as e:
        print(f"Erreur get_user_status: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def decrement_vague(discord_id: int) -> int:
    """Décrémente une vague et retourne le nouveau nombre"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        reset_vagues_if_needed()
        
        cursor.execute("""
            UPDATE users 
            SET vagues_free = GREATEST(0, vagues_free - 1) 
            WHERE discord_id = %s
        """, (discord_id,))
        conn.commit()
        
        # Récupérer le nouveau nombre
        cursor.execute("SELECT vagues_free FROM users WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Erreur decrement_vague: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def enregistrer_suivi(discord_id: int, type_activite: str, 
                     etat: str = 'en_cours', 
                     cours_id: int = None, 
                     chapitre_id: int = None, 
                     qcm_id: int = None, 
                     exercice_id: int = None, 
                     score: int = None):
    """Enregistre une activité dans le suivi"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        discord_id = int(discord_id)
        
        cursor.execute("""
            INSERT INTO suivi (
                discord_id, type_activite, etat,
                cours_id, chapitre_id, qcm_id, exercice_id, score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            discord_id, type_activite, etat,
            cours_id, chapitre_id, qcm_id, exercice_id, score
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Erreur enregistrer_suivi: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
def get_derniere_activite(discord_id: int, type_activite: str = None):
    """Récupère la dernière activité par type"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        discord_id = int(discord_id)
        
        if type_activite:
            cursor.execute("""
                SELECT * FROM suivi 
                WHERE discord_id = %s AND type_activite = %s
                ORDER BY date_activite DESC 
                LIMIT 1
            """, (discord_id, type_activite))
        else:
            cursor.execute("""
                SELECT * FROM suivi 
                WHERE discord_id = %s
                ORDER BY date_activite DESC 
                LIMIT 1
            """, (discord_id,))
            
        return cursor.fetchone()
    except Exception as e:
        print(f"Erreur get_derniere_activite: {e}")
        return None
    finally:
        cursor.close()

def get_activite_en_cours(discord_id: int):
    """Récupère l'activité en cours d'un utilisateur"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        discord_id = int(discord_id)
        
        cursor.execute("""
            SELECT * FROM suivi 
            WHERE discord_id = %s 
            AND etat = 'en_cours'
            ORDER BY date_activite DESC 
            LIMIT 1
        """, (discord_id,))
        
        return cursor.fetchone()
    except Exception as e:
        print(f"Erreur get_activite_en_cours: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
def update_suivi_etat(suivi_id: int, etat: str, score: int = None):
    """Met à jour l'état d'un suivi"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE suivi 
            SET etat = %s, score = %s 
            WHERE suivi_id = %s
        """, (etat, score, suivi_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur update_suivi_etat: {e}")
        return False
    finally:
        cursor.close()
        conn.close() 

def update_suivi_chapitre(suivi_id: int, chapitre_id: int):
    """Met à jour le chapitre d'un suivi"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE suivi 
            SET chapitre_id = %s 
            WHERE suivi_id = %s
        """, (chapitre_id, suivi_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur update_suivi_chapitre: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def reset_vagues_if_needed():
    """Réinitialise les vagues toutes les 7 heures si nécessaire"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET vagues_free = 3,
                dernier_reset_free = CURRENT_TIMESTAMP 
            WHERE dernier_reset_free <= NOW() - INTERVAL 7 HOUR
        """)
        conn.commit()
    except Exception as e:
        print(f"Erreur reset_vagues: {e}")
    finally:
        cursor.close()
        conn.close()


def can_access_course(discord_id: int, cours_id: int) -> bool:
    """Vérifie si l'utilisateur peut accéder à un cours gratuit"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Vérifier le type de compte
        cursor.execute("SELECT type_compte FROM users WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
            
        account_type = result[0]
        
        # Compte premium: accès illimité
        if account_type == 'premium':
            return True
            
        # Compte gratuit: vérifier la limite de 3 cours distincts
        cursor.execute("""
            SELECT COUNT(DISTINCT cours_id) 
            FROM suivi 
            WHERE discord_id = %s 
            AND cours_id IS NOT NULL
        """, (discord_id,))
        count_result = cursor.fetchone()
        course_count = count_result[0] if count_result else 0
        
        # Vérifier si l'utilisateur a déjà accédé à ce cours
        cursor.execute("""
            SELECT 1 FROM suivi 
            WHERE discord_id = %s 
            AND cours_id = %s 
            LIMIT 1
        """, (discord_id, cours_id))
        already_accessed = cursor.fetchone() is not None
        
        # Si cours déjà accessible OU moins de 3 cours distincts
        return already_accessed or course_count < 3
    except Exception as e:
        print(f"Erreur can_access_course: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_remaining_vagues(discord_id: int) -> int:
    """Récupère le nombre de vagues restantes"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        reset_vagues_if_needed()
        
        cursor.execute("SELECT vagues_free FROM users WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Erreur get_remaining_vagues: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()


def reset_vies_if_needed():
    """Réinitialise les vies toutes les 7 heures si nécessaire"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET vagues_free = 3,
                dernier_reset_free = CURRENT_TIMESTAMP 
            WHERE dernier_reset_free <= NOW() - INTERVAL 7 HOUR
        """)
        conn.commit()
    except Exception as e:
        print(f"Erreur reset_vies: {e}")
    finally:
        cursor.close()
        conn.close()

def decrement_vie(discord_id: int) -> int:
    """Décrémente une vie et retourne le nouveau nombre"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Réinitialisation périodique des vies
        reset_vies_if_needed()
        
        cursor.execute("""
            UPDATE users 
            SET vagues_free = GREATEST(0, vagues_free - 1) 
            WHERE discord_id = %s
        """, (discord_id,))
        conn.commit()
        
        # Récupérer le nouveau nombre
        cursor.execute("SELECT vagues_free FROM users WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Erreur decrement_vie: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()   

def get_remaining_vies(discord_id: int) -> int:
    """Récupère le nombre de vies restantes"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        reset_vies_if_needed()
        
        cursor.execute("SELECT vagues_free FROM users WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Erreur get_remaining_vies: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

# Ajoutez cette fonction dans votre fichier Users.py
def get_user_type(discord_id: int) -> str:
    """Détermine le type de compte de l'utilisateur (free ou premium)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Vérifier si l'utilisateur existe
        cursor.execute("SELECT COUNT(*) FROM users WHERE discord_id = %s", (discord_id,))
        if cursor.fetchone()[0] == 0:
            return 'free'  # Par défaut si non enregistré
        
        # Vérifier le type de compte
        cursor.execute("SELECT type_compte FROM users WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else 'free'
    except Exception as e:
        print(f"Erreur dans get_user_type: {e}")
        return 'free'
    finally:
        cursor.close()
        conn.close()


def upgrade_to_premium(discord_id: int):
    conn = get_connection('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET premium = 1 WHERE discord_id = ?", (discord_id,))
    conn.commit()
    conn.close()

def get_last_chapitre_suivi(discord_id: int, cours_id: int):
    """Récupère le dernier chapitre suivi pour un cours"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT chapitre_id 
            FROM suivi 
            WHERE discord_id = %s 
                AND cours_id = %s 
                AND type_activite = 'learn'
            ORDER BY date_activite DESC 
            LIMIT 1
        """, (discord_id, cours_id))
        row = cursor.fetchone()
        return row['chapitre_id'] if row else None
    except Exception as e:
        print(f"Erreur get_last_chapitre_suivi: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def is_course_completed(discord_id: int, cours_id: int):
    """Vérifie si un cours est complété"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 1 
            FROM suivi 
            WHERE discord_id = %s 
                AND cours_id = %s 
                AND type_activite = 'learn'
                AND etat = 'termine'
            LIMIT 1
        """, (discord_id, cours_id))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Erreur is_course_completed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

