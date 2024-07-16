import os
from dotenv import load_dotenv, dotenv_values
from passlib.context import CryptContext
# loading variables from .env file
load_dotenv()

# accessing and printing value
SECRET_KET = os.getenv("SECRET_KET")
ALGORITHM = os.getenv("ALGORITHM")

# Hashing password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
