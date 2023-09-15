from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#mySQL Database connection
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:5541769@127.0.0.1:3306/todoapplicatondatabase'
engine= create_engine(SQLALCHEMY_DATABASE_URL)


#PostgreSQL Database connection
#SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:5541769@localhost/TodoApplicationDatabase'
#engine= create_engine(SQLALCHEMY_DATABASE_URL)

#SQLite Database connection
#SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
#engine= create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})  # required for database connection

SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine) # database operations
Base=declarative_base()