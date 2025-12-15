from dotenv import load_dotenv
import os

load_dotenv()

# Configuration MySQL
DB_CONFIG = {
    'host': os.getenv('SQL_HOST'),
    'user': os.getenv('SQL_USER'),
    'password': os.getenv('SQL_PASSWORD'),
    'database': os.getenv('SQL_NAME')
}

# Autres variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
URL_GRIB = os.getenv('URL_GRIB')
URL_INTERFACE = os.getenv('URL_INTERFACE')



