
from datetime import datetime, timedelta
import jwt
import logging
from expence_tracker import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXPIRY_LIFETIME = int(settings.TOKEN_EXPIRY)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

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
        logging.error(e)
    except Exception as e:
        logging.error(e)


def decode_payload(payload):
    try:
        sub = jwt.decode(payload, SECRET_KEY, algorithms=[ALGORITHM])
        return (sub)
        # email = sub.get("email")
        # id = sub.get("id")
    except Exception as e:
        logging.error(e)
    # return email, id

    
