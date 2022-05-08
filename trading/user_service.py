#The service function will look user name and password.If user is found
#it will return an authenticated token that can be used for all applications
import sqlite3
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import request, g
import jwt

SECRET = 'bfg28y7efg238re7r6t32gfo23vfy7237yibdyo238do2v3'

#Gets users credentials (e.g. email and password)
def get_user_with_credentials(email, password):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        cur.execute('''
            SELECT email, name, password FROM users where email=?''',
                    (email,))
        row = cur.fetchone()
        if row is None:
            return None
        email, name, hash = row
        if not pbkdf2_sha256.verify(password, hash):
            return None
        return {"email": email, "name": name, "token": create_token(email)}
    finally:
        con.close()

#Authenticate the user's credentials and authenticate the tokens on the cookies. Once verified it is passed on to the flask session
def logged_in():
    token = request.cookies.get('auth_token')
    try:
        data = jwt.decode(token, SECRET, algorithms=['HS256'])
        g.user = data['sub']
        return True
    except jwt.InvalidTokenError:
        return False

#After authenticating token for the user using the symetric login algorithm HS256, verifies the user's signature with secret key
def create_token(email):
    now = datetime.utcnow()
    payload = {'sub': email, 'iat': now, 'exp': now + timedelta(minutes=60)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token
