from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.database.db import get_db
from src.auth.service import Auth
from src.auth.schemas import UserCreate, Token, UserDB
from src.auth.models import User

auth_service = Auth()
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserDB
)
async def signup(
	body: UserCreate,
	db = Depends(get_db)
) -> UserDB:
	
	user = db.query(User).filter(User.username==body.username).first()
	
	if user is not None:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="user exists"
		)

	hash_password = auth_service.hash_password(body.password)
	new_user = User(
		username = body.username,
		hash_password = hash_password 
	)

	db.add(new_user)
	db.commit()
	return new_user


@router.post("/login", response_model=Token)
async def login(
	form_data: OAuth2PasswordRequestForm = Depends(),
	db = Depends(get_db)
) -> Token:
	
	user = db.query(User).filter(User.username==form_data.username).first()

	if user is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="user not found"
		)
	
	verification = auth_service.verify_password(
		form_data.password, user.hash_password
	)
	if not verification:
		raise HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Auth error"
	)

	access_token = auth_service.create_access_token(user.username)
	refresh_token = auth_service.create_refresh_token(user.username)

	user.refresh_token = refresh_token
	db.commit()

	return Token(
		access_token = access_token,
		refresh_token = refresh_token
	)

@router.post("/logout", response_model=UserDB)
async def logout(
	user = Depends(auth_service.get_user),
	db = Depends(get_db)
) -> UserDB:
	user.refresh_token = None
	db.commit()
	return user