from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__='users'

    id=Column(Integer,primary_key=True, index=True)
    email=Column(String,unique=True)
    username=Column(String, unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password=Column(String)
    isactive=Column(Boolean, default=True)
    role=Column(String)

class Todos(Base):
    __tablename__='todos'

    id=Column(Integer, primary_key=True,index=True)
    title=Column(String)
    description=Column(String)
    priority=Column(Integer)
    complate=Column(Boolean, default=False)
    owner_id=Column(Integer, ForeignKey("users.id"))
