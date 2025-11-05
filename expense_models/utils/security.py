
from datetime import datetime, timedelta
from expence_tracker.settings import BASE_DIR
import environ
import os
from rest_framework.response import Response
import jwt
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

EXPIRY_LIFETIME = env.int("TOKEN_EXPIRY_LIFETIME")
ALGORITHM = env("ALGORITHM")
SECRET_KEY = env("SECRET_KEY")

def encode_payload( sub : dict):
    payload = sub.copy()
    exp = datetime.now() + timedelta(minutes=EXPIRY_LIFETIME)
    try :
        payload.update({
            "exp": exp
        })
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except jwt.InvalidKeyError as e:
        print(e)
    except Exception as e:
        print(e)
    
