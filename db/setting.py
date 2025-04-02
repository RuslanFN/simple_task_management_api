from sqlmodel import SQLModel, Session, create_engine
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_NAME = getenv('DB_NAME')
DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT')

CONN_STR = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(CONN_STR, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

