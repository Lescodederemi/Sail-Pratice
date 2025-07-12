import mysql.connector
from config import DB_CONFIG

def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Erreur MySQL: {e}")
        return None

def init_exercices_table():
    conn = create_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        # AJOUTER LA COLONNE cours_id
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercices (
            ex_id INT AUTO_INCREMENT PRIMARY KEY,
            cours_id INT NOT NULL,
            niveau ENUM('débutant', 'intermédiaire', 'avancé', 'expert') NOT NULL,
            instruction TEXT NOT NULL,
            etape TEXT NOT NULL,
            reponse VARCHAR(255) NOT NULL,
            FOREIGN KEY (cours_id) REFERENCES cours(cours_id)
        """)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erreur lors de la création de la table: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def ajouter_exercice(cours_id: int, niveau: str, instruction: str, etape: str, reponse: str):
    conn = create_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO exercices (cours_id, niveau, instruction, etape, reponse) VALUES (%s, %s, %s, %s, %s)",
            (cours_id, niveau, instruction, etape, reponse)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erreur lors de l'ajout: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def modifier_exercice(ex_id, cours_id=None, niveau=None, instruction=None, etape=None, reponse=None):
    conn = create_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        
        if cours_id is not None:
            updates.append("cours_id = %s")
            params.append(cours_id)
        if niveau is not None:
            updates.append("niveau = %s")
            params.append(niveau)
        if instruction is not None:
            updates.append("instruction = %s")
            params.append(instruction)
        if etape is not None:
            updates.append("etape = %s")
            params.append(etape)
        if reponse is not None:
            updates.append("reponse = %s")
            params.append(reponse)
        
        if not updates:
            return False
        
        query = "UPDATE exercices SET " + ", ".join(updates) + " WHERE ex_id = %s"
        params.append(ex_id)
        cursor.execute(query, tuple(params))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Erreur lors de la modification: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
def supprimer_exercice(ex_id):
    conn = create_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM exercices WHERE ex_id = %s", (ex_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Erreur lors de la suppression: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_exercice_by_id(ex_id):
    conn = create_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM exercices WHERE ex_id = %s", (ex_id,))
        return cursor.fetchone()
    except mysql.connector.Error as e:
        print(f"Erreur lors de la récupération: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_random_exercice_by_niveau(niveau):
    """Version optimisée avec LIMIT 1"""
    conn = create_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM exercices 
            WHERE niveau = %s 
            ORDER BY RAND() 
            LIMIT 1
        """, (niveau,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_random_exercice_by_cours(cours_id: int):
    """Récupère un exercice aléatoire pour un cours spécifique"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM exercices WHERE cours_id = %s ORDER BY RAND() LIMIT 1",
            (cours_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Erreur SQL: {e}")
        return None
    finally:
        if conn: 
            conn.close()

def get_exercices_by_cours_and_niveau(cours_id, niveau):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM exercices WHERE cours_id = %s AND niveau = %s"
    cursor.execute(query, (cours_id, niveau))
    exercices = cursor.fetchall()
    cursor.close()
    conn.close()
    return exercices