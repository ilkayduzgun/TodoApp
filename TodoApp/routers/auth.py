from datetime import timedelta,datetime
from typing import Annotated, Optional
from fastapi import APIRouter,Depends, Form, HTTPException,Request, Response
from pydantic import BaseModel, Field
from database import SessionLocal,engine
from sqlalchemy.orm import Session
from models import Users
import models
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse


router=APIRouter(
    prefix='/auth',
    tags=['auth']
)
SECRET_KEY='b5e9c1d7e26f6e9426c9a4e9d1e7d0d2d4f5c6e8d2b5e6a5c6d4b5e7a5c6b7'
ALGORITHM='HS256'
bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')
models.Base.metadata.create_all(bind=engine)
templates=Jinja2Templates(directory="templates")

class LoginForm:
    def __init__(self,request:Request):
        self.request: Request=request
        self.username:Optional[str]= None
        self.password: Optional[str]=None
    
    async def create_oauth_form(self):
        form=await self.request.form()
        self.username=form.get("email")
        self.password= form.get("password")


def get_db():
    db=SessionLocal()
    try:
        yield db

    finally:
        db.close()

db_dependency=Annotated[Session , Depends(get_db)]

def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username:str, password: str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str, user_id:int, role:str, expires_delta: timedelta):
    encode={'sub':username, 'id':user_id, 'role': role}
    expires=datetime.utcnow()+expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request:Request):
    try:
        token=request.cookies.get("access_token")
        if token is None:
            return None
        payload=jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        username: str=payload.get('sub')
        user_id: int=payload.get('id')
        user_role: str=payload.get('role')
        if username is None or user_id is None:
           logout(request)
        
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    

    
@router.post("/token")
async def login_for_access_token(response:Response, form_data: Annotated[OAuth2PasswordRequestForm,Depends()], db:db_dependency):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
       raise False
    token=create_access_token(user.username,user.id, user.role, timedelta(minutes=60))
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True

# HTML response   
@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/logout")
async def logout(request:Request):
    msg= "Logout Successful"
    response= templates.TemplateResponse("login.html", {"request":request, "msg":msg})
    response.delete_cookie(key="access_token")
    return response

@router.get("/register", response_class= HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(request:Request, email:str= Form(...), username:str= Form(...), firstname:str=Form(...), lastname:str= Form(...), password:str=Form(...), password2:str=Form(...), db: Session=Depends(get_db)):
   
    validation1= db.query(models.Users).filter(models.Users.username==username).first()
    validation2=db.query(models.Users).filter(models.Users.email==email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg="Invalid registration request"
        return templates.TemplateResponse("register.html", {"request":request, "msg":msg})
    
    user_model=models.Users()
    user_model.username=username
    user_model.email=email
    user_model.first_name=firstname
    user_model.last_name=lastname
    hash_password=get_password_hash(password)
    user_model.hashed_password=hash_password
    user_model.isactive=True

    db.add(user_model)
    db.commit()

    msg="Successful User Creating"
    return templates.TemplateResponse("login.html",{"request":request, "msg":msg})
