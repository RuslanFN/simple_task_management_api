import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session    
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.setting import get_session, create_db_and_tables
from db.models import UserRegister, User, UserLogin, TaskById, Task, TaskAdd
from db.setting import get_session
from secure.pwd_hash import get_password_hash, verify_password
from secure.encrypt import create_jwt_token, create_base_payload, decode_jwt_token

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
oauth2_form = OAuth2PasswordRequestForm

def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt_token(token)
        
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Истекло время жизни токена')
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail='Неправильный токен')



def get_user_or_exception(payload: dict = Depends(get_user_from_token),
                          session: Session = Depends(get_session)):
    user_id = int(payload['sub'])
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        return user
    raise HTTPException(status_code=401, detail='Пользователь не найден')

def get_task_by_id(task_id: int,
                   user: User = Depends(get_user_or_exception), 
                   session: Session = Depends(get_session)):
    task_list = [task for task in user.tasks if task.id==task_id]
    if not task_list:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    return task_list[0]

@app.post('/register')
def register(user: UserRegister, session: Session = Depends(get_session)):
    user_exists = session.query(User).filter(User.username == user.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail='Пользователь уже существует')
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, 
                    email=user.email,
                    hashed_password = hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {'status': 200,
            'result':'new user added'}

@app.get('/token')
def login():
    return FileResponse('templates/login.html')

@app.post('/token')
def login(user_login: oauth2_form = Depends(), session: Session = Depends(get_session)):
    user = session.query(User).filter(User.username == user_login.username).first()
    if user:
        if verify_password(user_login.password, user.hashed_password):
            payload = create_base_payload(sub=user.id)
            return {'access_token':create_jwt_token(payload=payload), 'token_type':'bearer'}
        raise HTTPException(status_code=401, detail='Пароль не верный')
    raise HTTPException(status_code=401, detail='Не существует пользователя с таким иминем пользователя')

@app.get('/me')
def my_info(user: User = Depends(get_user_or_exception), session: Session = Depends(get_session)):
    return({'status': 200,
            'you in db': user})

@app.get('/task/{task_id}')
def get_task(task: Task = Depends(get_task_by_id)):
    return {'status':200,
            'result': task}

@app.delete('/task/{task_id}')
def delete_task(task: Task = Depends(get_task_by_id), 
                session: Session = Depends(get_session)):
    session.delete(task)
    session.commit()
    return {'status':204,
            'deleted':task}

@app.put('/task/{task_id}')
def edit_task(add_task: TaskAdd,  
              old_task: Task = Depends(get_task_by_id), 
              session: Session = Depends(get_session)):
    task = old_task
    task.title = add_task.title
    task.detail = add_task.detail
    session.add(task)
    session.commit()
    session.refresh(task)
    return {'status':201,
            'updated':task}

@app.post('/task')
def add_task(data: TaskAdd, 
             user: User = Depends(get_user_or_exception),
             session: Session = Depends(get_session)):
    task = Task(title=data.title, detail=data.detail, user=user)
    session.add(task)
    session.commit()
    session.refresh(task)
    return {'status':201,
            'edited': task}

@app.get('/tasks')
def get_tasks(user: User = Depends(get_user_or_exception), 
             session: Session = Depends(get_session)):
    return {'status':200,
            'result': user.tasks}

if __name__ == '__main__':
    create_db_and_tables()
    uvicorn.run(app=app)