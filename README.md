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
