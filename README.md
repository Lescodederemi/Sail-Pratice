# Sail-Pratice
Boot discords pour la voile
•	Lancement du bot avec /lvr


3. Météo et routage
•	Lecture de fichiers GRIB depuis ton client FTP (automatisé).
•	Traitement des GRIB hors de Discord.
•	Discord sort les fichier selon les zone demande par l’algoryhme meteomail meteoftp
•	FICHIER ECMWF 3 jour avec pas de 25 min
•	FICHIER GFS 3 JOUR PAS DE 25 min .

Meteomail :


Email de zone a écrire 

query@saildocs.com",
 message_body": sub ecmwf:-90,90,0,90|0.25,0.25|0,72,0.4167|WIND,WAVE
       
query@saildocs.com
 sub ecmwf:-90,90,90,180|0.25,0.25|0,72,0.4167|WIND,WAVE

    query@saildocs.com
        message_body": "sub gfs:-90,90,-180,0|0.25,0.25|0,72,0.4167|WIND,WAVE
        
       query@saildocs.com
        "message_body": "sub gfs:-90,90,0,90|0.25,0.25|0,72,0.4167|WIND,WAVE
        
      query@saildocs.com",
       sub gfs:-90,90,90,180|0.25,0.25|0,72,0.4167|WIND,WAVE
            
destinataire": "query@saildocs.com
sub ecmwf:-90,90,-180,0|0.25,0.25|0,72,0.4167|WIND,WAVE
*

SAIL PRATICE GUIDE

Introduction :
Ce boot discord est un boot discord qui a besoin de plusieurs choses pour fonctionner, 
•	Un clien FTP
•	Une base de donnes pour la gestion des cours.
•	Un client email reserve a cela. 

Fonctionnement générale du boot :
Lancement du bot avec /lvr
Le bot change de langue si on clique sur le drapeau fr ou en bouton Lang avec drapeau Fr et en en miniature  
Toutes les fonctionnalités sont intégrées via des embeds, des boutons et des menus interactifs.
•	Les requêtes slash sont limitées à l’administration des commandes.
•	Gestion multi-langues : français et anglais au choix.
•	Les slash seront réserves au admin 
2. Système d’apprentissage
•	Parcours de formation avec progression.
•	Stockage des cours, chapitres et QCM en base de données MySQL. Les thématiques seront aussi stocké quelle que modélisme naval 
•	Affichage 1 embed à la fois avec navigation par bouton : « Suivant », « Précédent », 
•	Un emebed est parémetrer et représente un chapitre ou contenu 
•	Création des cours avec /lvr créer pour créer un nouveau cours ou exercices via un embed  special
•	Commande pour modifier les cours / lvr mod et ensuite l’invoye en embed demamnde si on veux suprime ruen thematique un cours ou un chapitre

•	Possibilité de valider, corriger ou annuler les travaux à rendre.
•	QCM interactif intégré :
•	Chaque réponse est évaluée avec un pourcentage de réussite personnalisé.
•	Notion de « partiellement acquis » selon les résultats.
•	Correction immédiate avec retour sur les réponses.
•	Système premium : accès aux corrections personnalisées et accompagnement aux devoirs.
•	QCM interactif avec correction automatique et pourcentage de réussite.
•	Système Premium : possibilité de corrections détaillées et de suivre les devoirs en privé.
3. Météo et routage
•	Lecture de fichiers GRIB depuis ton client FTP (automatisé).
•	Traitement des GRIB hors de Discord.
•	Discord sort les fichier selon les zone demande par l’algoryhme meteomail meteoftp
•	FICHIER ECMWF 3 jour avec pas de 25 min
•	FICHIER GFS 3 JOUR PAS DE 25 min .

Meteomail :


Email de zone a écrire 

query@saildocs.com",
 message_body": sub ecmwf:-90,90,0,90|0.25,0.25|0,72,0.4167|WIND,WAVE
       
query@saildocs.com
 sub ecmwf:-90,90,90,180|0.25,0.25|0,72,0.4167|WIND,WAVE

    query@saildocs.com
        message_body": "sub gfs:-90,90,-180,0|0.25,0.25|0,72,0.4167|WIND,WAVE
        
       query@saildocs.com
        "message_body": "sub gfs:-90,90,0,90|0.25,0.25|0,72,0.4167|WIND,WAVE
        
      query@saildocs.com",
       sub gfs:-90,90,90,180|0.25,0.25|0,72,0.4167|WIND,WAVE
            
destinataire": "query@saildocs.com
sub ecmwf:-90,90,-180,0|0.25,0.25|0,72,0.4167|WIND,WAVE


4. Gestion utilisateurs & premium
•	Base de données SQL pour :
•	Lier les utilisateurs Discord à leurs données.
•	Suivre la progression, les scores, les devoirs.
•	Fonctions Premium :
•	Export des parcours en PDF / Excel.
•	Correction détaillée des QCM.
•	Accompagnement sur les devoirs.
Modèle de Fonctionnalités Gratuite vs Premium :
•	Gratuites :
•	Export en PDF.
•	Accès aux QCM et aux cours avec progression.
•	Gestion de Cœur limite a 5 , Une erreur enlevé un cœur
•	Premium :
•	Export en Excel (données modifiables).
•	Routage illimité avec un nombre de points au-delà de la version gratuite.
•	Correction détaillée des QCM et accompagnement pour les devoirs.
•	Acheter des cœur supplémentaires,

5- A implémenter par forcement dans le boot
Gestion des niveaux par rapport au compétences plutôt que en niveau numérique

Débutant : Lorsqu'une personne commence, elle suit des cours introductifs pour se familiariser avec les bases du sujet. Cela pourrait inclure des vidéos et des quiz simples pour valider les connaissances de base.
•	Intermédiaire : Une fois que les bases sont maîtrisées, l'apprenant passe à des sujets plus approfondis. Les cours dans cette catégorie pourraient inclure des simulations ou des exercices plus complexes. Cela marquerait une transition vers des connaissances appliquées.
•	Avancé : À ce niveau, l'apprenant a une bonne maîtrise des concepts, et les cours pourraient inclure des études de cas, des défis plus difficiles, et des simulations de situations réelles.
•	Expert : L'apprenant a une expertise dans le domaine, et cela pourrait se traduire par la validation de son savoir à travers des certifications ou des projets finaux qui combinent tout ce qu'il a appris. Des quiz très complexes ou des évaluations finales pourraient marquer ce stade.
6. Intégration de l’intelligence artificielle
Le bot Discord intègre une IA conversationnelle pour assister les utilisateurs dans leur apprentissage nautique.
L’ia en question sera a définir devellopemen tardif de cela courant 2027.
Fonctionnalités principales :
•	L’IA est déclenchée par une commande spécifique par bouton dans le menu.
•	L’IA se connecte à une base de données SQL contenant les cours, chapitres et QCM.
•	Elle peut également lire et analyser le contenu des PDF pédagogiques liés aux cours.
•	À partir des données extraites, l’IA génère une réponse claire et personnalisée à la question de l’utilisateur.
•	La réponse est ensuite renvoyée directement dans Discord, sous forme de message ou d’embed.
Cas d’usage :
Exemple : un utilisateur demande « Comment virer vent debout ? »
➜ L’IA analyse les documents disponibles, extrait les sections pertinentes, et génère une réponse pédagogique adaptée à son niveau.
Technologies utilisées :
•	Connexion SQL : pymysql ou SQLAlchemy
•	Lecture de PDF : PyMuPDF
•	IA : OpenAI GPT-4 (ou autre modèle compatible)
•	Intégration Discord : discord.py ou nextcord avec interactions slash et boutons
Personnalisation possible :
•	L’IA adapte ses réponses selon le niveau de l’utilisateur (Débutant, Intermédiaire, Avancé, Expert).
•	En version Premium : réponse enrichie, avec documents liés et rappels personnalisés.

