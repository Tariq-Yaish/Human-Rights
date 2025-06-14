from fastapi import APIRouter, Body, HTTPException, status
from models.user import User, Login, CurrentUser
from authentication import auth_handler

router = APIRouter()

@router.post("/register",
    response_description="Register a new user",
    response_model=CurrentUser,
    status_code=status.HTTP_201_CREATED
)
async def register_user(new_user: User = Body(...)):
    if await User.find_one(User.username == new_user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken."
        )

    new_user.password = auth_handler.get_password_hash(new_user.password)

    await new_user.create()
    return CurrentUser(id=new_user.id, username=new_user.username)


@router.post("/login", response_description="Login a user")
async def login_user(login_details: Login = Body(...)):
    user = await User.find_one(User.username == login_details.username)

    if (user is None) or (not auth_handler.verify_password(login_details.password, user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username and/or password"
        )

    token = auth_handler.encode_token(user.id, user.username)
    return {'token': token}