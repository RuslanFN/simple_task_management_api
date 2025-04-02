from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

# User models
class UserLogin(SQLModel):
    '''model for authorization and authentication'''
    username: str
    password: str

class UserRegister(UserLogin):
    '''Model for registration users. Base on UerLogin, but added emails field'''
    email: str = EmailStr
    

class User(SQLModel, table=True):
    '''This model is for migration to database'''
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = EmailStr
    hashed_password: str
    tasks: list['Task'] = Relationship(back_populates='user')
# Task models
class TaskById(SQLModel):
    id: int 

class TaskAdd(SQLModel):
    title: str
    detail: str

class Task(TaskAdd, table=True):
    id: int | None = Field(default=None, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.utcnow)
    deadline_at: datetime | None = None
    user_id: int = Field(foreign_key='user.id', ondelete='CASCADE', nullable=False)
    user: User = Relationship(back_populates='tasks')






    
