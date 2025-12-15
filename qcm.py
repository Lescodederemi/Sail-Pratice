import mysql.connector
import os

# Récupérer les variables de base de données
SQL_host = os.getenv('SQL_HOST')
Sql_User = os.getenv('SQL_USER')
Sql_mdp = os.getenv('SQL_PASSWORD')
Sql_name = os.getenv('SQL_NAME')


def connect_db():
    return mysql.connector.connect(
        host=SQL_host,
        user=Sql_User,
        password=Sql_mdp,
        database=Sql_name
    )

# Dans chaque fichier
import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def add_qcm(cours_id: int, ordre: int, question: str, bonne_reponse: int,
            reponse_1: str, reponse_2: str, reponse_3: str,
            reponse_4: str, reponse_5: str, reponse_6: str,
            score_min: int) -> bool:
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO qcm (
                cours_id, ordre, question, bonne_reponse,
                reponse_1, reponse_2, reponse_3,
                reponse_4, reponse_5, reponse_6,
                Score_min
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            cours_id, ordre, question, bonne_reponse,
            reponse_1, reponse_2, reponse_3,
            reponse_4, reponse_5, reponse_6,
            score_min
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur ajout QCM : {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def delete_qcm(qcm_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM qcm WHERE id = %s", (qcm_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Erreur SQL suppression QCM : {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def edit_qcm(qcm_id: int, **kwargs):
    """Modifie un QCM existant avec des champs optionnels"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Construire dynamiquement la requête
        updates = []
        params = []
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(qcm_id)
        query = f"UPDATE qcm SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Erreur modification QCM : {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_qcm_by_cours_id(cours_id: int):
    """Récupère les QCM associés à un cours, triés par ordre"""
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM qcm 
            WHERE cours_id = %s
            ORDER BY ordre
        """, (cours_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Erreur récupération QCM: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def save_qcm_result(user_id: int, qcm_id: int, score: int):
    """Enregistre le résultat d'un QCM"""
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO qcm_results (user_id, qcm_id, score, date_completed)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                score = VALUES(score),
                date_completed = NOW()
        """, (user_id, qcm_id, score))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde résultat: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def calculate_qcm_score(qcms, answers):
    """Calcule le score du QCM basé sur les réponses"""
    total_questions = len(qcms)
    correct_answers = 0
    
    for qcm in qcms:
        qcm_id = qcm["id"]
        user_answer = answers.get(qcm_id)
        if user_answer and user_answer == qcm["bonne_reponse"]:
            correct_answers += 1
    
    return (correct_answers / total_questions) * 100 if total_questions > 0 else 0

def get_min_required_score(qcms):
    """Retourne le score minimum requis pour le QCM"""
    return max(qcm["Score_min"] for qcm in qcms) if qcms else 0

def save_qcm_result(user_id: int, cours_id: int, score: int):
    """Enregistre le résultat du QCM dans la base de données"""
    connection = connect_db()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO qcm_results (user_id, cours_id, score, date_completion)
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE score = VALUES(score), date_completion = NOW()
        """
        cursor.execute(query, (user_id, cours_id, score))
        connection.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du résultat: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# Ajouter ces fonctions à la fin du fichier qcm.py

def link_media_to_qcm(qcm_id: int, media_id: int) -> bool:
    """Lie un média à un QCM"""
    conn = connect_db()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE qcm SET media_id = %s WHERE id = %s",
            (media_id, qcm_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur lors de la liaison du média au QCM: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_media_for_qcm(qcm_id: int) -> dict:
    """Récupère le média lié à un QCM"""
    conn = connect_db()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT m.url, m.type 
            FROM media m
            JOIN qcm q ON q.media_id = m.media_id
            WHERE q.id = %s
        """, (qcm_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Erreur get_media_for_qcm: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()