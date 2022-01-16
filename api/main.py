from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from Model.sqlmodel import *
from jose import JWTError, jwt
import uvicorn
import logging
from Model.model import *
from Auth.serverauth import *

app = FastAPI()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/user/signup")
async def signup_api(user: User):
    try:
        result = signup(user.username, user.password, user.full_name, user.email)
        return result
    except Exception as e:
        logging.warning(e)

@app.post("/user/login")
async def login_api(user: UserInLogin):
    current_user = authenticate_user(user.username, user.password)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    result = login(user.username, user.password)
    return {"access_token": access_token, "token_type": "Bearer", "detail": result["detail"]}

@app.get("/user/activity")
async def get_user_activity_api(current_user: User = Depends(get_current_user)):
    result = get_user_activity(current_user.username)
    update_last_access(current_user.username)
    return result

@app.post("/post/create")
async def post_create_api(post: Post, current_user: User = Depends(get_current_user)):
    try:
        user_id = get_user_id(current_user.username)
        result = create_post(post.title, user_id, post.description)
        update_last_access(current_user.username)
        return result
    except Exception as e:
        logging.warning(e)

@app.get("/post/like/{id}")
async def post_like_api(id: int, current_user: User = Depends(get_current_user)):
    try:
        result = like_post(id, current_user.username)
        update_last_access(current_user.username)
        return result
    except Exception as e:
        logging.warning(e)

@app.get("/post/unlike/{id}")
async def post_unlike_api(id: int, current_user: User = Depends(get_current_user)):
    try:
        result = unlike_post(id)
        update_last_access(current_user.username)
        return result
    except Exception as e:
        logging.warning(e)

@app.get("/analytics/{date_from}/{date_to}")
async def post_analitics_api(date_from:str, date_to:str, current_user: User = Depends(get_current_user)):
    date_from = date_from.split('-')
    date_to = date_to.split('-')

    result = get_analytics(date_from, date_to)
    update_last_access(current_user.username)
    return result

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)