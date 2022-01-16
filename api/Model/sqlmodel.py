import logging
from typing import Optional
import time
from sqlmodel import Field, Session, SQLModel, create_engine,select
from datetime import datetime
from Model.model import *
from Auth.serverauth import get_password_hash, verify_password

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

class UserTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)    
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    last_access: float #timestamp
    last_login: float #timestamp

class PostTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    likes: int
    unlikes: int

    user_id: int = Field(default=None, foreign_key="usertable.id")

class AnalyticTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action_type: int #1=like, 0=unlike
    timestamp: float

    user_id: int = Field(default=None, foreign_key="usertable.id")

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def get_user(username: str):
    user_dict = {}
    with Session(engine) as session:
        statement = select(UserTable).where(UserTable.username == username)
        user = session.exec(statement).first()
        if user != None:
            
            user_dict["username"] = user.username
            user_dict["password"] = user.password
            user_dict["full_name"] = user.full_name
            user_dict["email"] = user.email

            return User(**user_dict)

def update_last_access(username):
    with Session(engine) as s:
        statement = select(UserTable).where(UserTable.username == username)
        user = s.exec(statement).first()
        if user !=None:
            user.last_access = float(time.time())
            s.add(user)
            s.commit()
            s.refresh(user)
            logging.warning("Last access updated for user: {}".format(username))

def signup(username, password, full_name=None, email=None):
    with Session(engine) as session:
        statement = select(UserTable).where(UserTable.username == username)
        user = session.exec(statement).first()
        if user == None: #check for unique username
            session.add(UserTable(username=username, password=get_password_hash(password), full_name=full_name, email=email, last_access=float(time.time()), last_login=float(0)))
            session.commit()
            logging.warning("User: {} successfully signed up".format(username))
            return {"detail": "Successfully signed up"}
    
def login(username, password):
    authenticated = authenticate_user(username, password)
    if authenticated:
        logging.warning("User: {} authenticated".format(username))
        with Session(engine) as s:
            statement = select(UserTable).where(UserTable.username == username)
            user = s.exec(statement).first()

            update_last_access(username)
            user.last_login = float(time.time())
            logging.warning("Last login updated for user: {}".format(username))

            s.add(user)
            s.commit()
            s.refresh(user)
        logging.warning("User: {} successfully logged in".format(username))
        return {"detail": "Succesfully Logged In"} 
    else:
        return {"detail": "Wrong Password"}

def get_user_id(username):
    with Session(engine) as session:
        statement = select(UserTable).where(UserTable.username == username)
        user = session.exec(statement).first()

        logging.warning("User id: {} for user: {}".format(user.id, username))
        return user.id

def create_post(title, user_id, description=None):
    with Session(engine) as session:
        statement = select(UserTable).where(UserTable.id == user_id)
        user = session.exec(statement).first()
        if user != None:
            with Session(engine) as session:
                session.add(PostTable(title=title, description=description, likes=0, unlikes=0, user_id=user_id))
                session.commit()

            with Session(engine) as session:
                statement = select(PostTable).where(PostTable.title == title)
                post = session.exec(statement).first()
                
                logging.warning("Post id: {} successfully created".format(post.id))
                return {"detail": "Post Created", "post_id": post.id}

def like_post(id, username):
    user_id = get_user_id(username)
    with Session(engine) as session:
        statement = select(PostTable).where(PostTable.id == id)
        post = session.exec(statement).first()

        post.likes +=1

        session.add(post)
        session.commit()
        session.refresh(post)
        logging.warning("Post: {} liked by user: {}".format(post.id, username))

    with Session(engine) as session:
        session.add(AnalyticTable(action_type=1, timestamp=float(time.time()), user_id=user_id))
        session.commit()

    return {"detail": "Post: {} liked by user: {}".format(id, username)}

def unlike_post(id):
    with Session(engine) as session:
        statement = select(PostTable).where(PostTable.id == id)
        post = session.exec(statement).first()

        post.unlikes +=1

        session.add(post)
        session.commit()
        session.refresh(post)
        logging.warning("Post: {} unliked".format(post.id))

        return {"detail": "Post unliked"}

def get_user_activity(username):
    results = {}
    with Session(engine) as s:
        statement = select(UserTable).where(UserTable.username == username)
        user = s.exec(statement).first()        
        results["last_access"] = datetime.fromtimestamp(user.last_access)
        results["last_login"] = datetime.fromtimestamp(user.last_login)

        return results

def get_analytics(date_from, date_to):
    timestamp_from = datetime.timestamp(datetime(int(date_from[0]),int(date_from[1]),int(date_from[2])))
    timestamp_to = datetime.timestamp(datetime(int(date_to[0]),int(date_to[1]),int(date_to[2])))
   
    num_of_actions = 0
    with Session(engine) as session:
        statement = select(AnalyticTable).where(AnalyticTable.action_type==1)
        all_actions = session.exec(statement).fetchall()
        
        for action in all_actions:
            if action.timestamp>timestamp_from and action.timestamp<timestamp_to:
                num_of_actions += action.action_type

    return {"detail": "Number of actions: {} from: {} to: {}".format(num_of_actions, date_from, date_to)}