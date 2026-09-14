import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Permet la lecture des variables d'environnement depuis le fichier .env
load_dotenv() 

def get_engine():
    return create_engine(
        f"postgresql://{os.environ['DB_USER']}:"
        f"{os.environ['DB_PASSWORD']}@"
        f"{os.environ['DB_HOST']}:"
        f"{os.environ['DB_PORT']}/"
        f"{os.environ['DB_NAME']}"
    )




