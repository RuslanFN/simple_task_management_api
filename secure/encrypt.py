import jwt
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta

load_dotenv()

alg = getenv('ALGORITHM')
secret = getenv('SECRET_KEY')

def create_base_payload(sub):
    time_now = datetime.utcnow()
    exp = time_now + timedelta(days=7)
    iss = 'myapp'
    aud = ['myapp','127.0.0.1:8000', 'localhost']
    nbf = time_now
    iat = time_now
    payload = {'iss': iss,
                'sub': str(sub),
                'aud': aud,
                'exp': exp,
                'nbf': nbf,
                'iat': iat}
    return payload

def create_jwt_token(payload: dict):
    return jwt.encode(payload, key=secret, algorithm=alg)

def decode_jwt_token(token: str):
    payload = jwt.decode(token, key=secret, algorithms=alg, audience='myapp')
    return payload
                

