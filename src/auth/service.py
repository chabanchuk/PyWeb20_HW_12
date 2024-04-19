from typing import Any
from datetime import datetime, timedelta
from src.auth.models import User
from src.database.db import get_db
import jose.jwt
import passlib.context
import fastapi
import fastapi.security



class Auth:
	HASH_CONTEXT = passlib.context.CryptContext(schemes=["bcrypt"])
	ALGORITHM = "HS256"
	SECRET = "puper_duper"
	oauth2_schema = fastapi.security.OAuth2PasswordBearer("/auth/login")

	
	def verify_password(
			self,
			plain_password: str,
			hash_password: str
	) -> bool:
		return self.HASH_CONTEXT.verify(plain_password, hash_password)
	
	
	def hash_password(
			self,
			plain_password: str,
	) -> str:
		return self.HASH_CONTEXT.hash(plain_password)

	
	def create_token(
			self,
			username: str,
			delta: timedelta,
			scope: str			
	) -> str:
		current_time = datetime.now(datetime.timezone.utc)
		expiration_time = current_time + delta

		payload = {
			"sub": username,
			"iat": current_time,
			"exp": expiration_time,
			"scope": scope
		}

		jwt_token = jose.jwt.encode(
			payload, self.SECRET, self.ALGORITHM
		)
		return jwt_token

	
	def create_access_token(
			self,
			username: str
	) -> str:
		return self.create_token(
			username,
			timedelta(minutes=15),
			"access_token"
	)


	def create_refresh_token(
			self,
			username: str
	) -> str:
		return self.create_token(
			username,
			timedelta(days=7),
			"refresh_token"
	)

	
	def get_user(
			self,
			token = fastapi.Depends(oauth2_schema),
			db = fastapi.Depends(get_db)
	) -> User:
		try:
			payload = jose.jwt.decode(
				token, self.SECRET, self.ALGORITHM
			)
		except jose.JWTError as e:
			raise fastapi.HTTPException(
				status_cod=fastapi.status.HTTP_401_UNAUTHORIZED,
				detail=f"invalid token: {e}" 
			)
		
		if payload.get("scope") not in ["access_token", "refresh_token"]:
			raise fastapi.HTTPException(
				status_cod=fastapi.status.HTTP_406_NOT_ACCEPTABLE,
				detail="invalid token scope" 
			)
		
		username = payload.get("sub")
		if username is None:
			raise fastapi.HTTPException(
				status_cod=fastapi.status.HTTP_406_NOT_ACCEPTABLE,
				detail="invalid token scope"
			)			
		
		if payload.get("scope") != "access_token":
			raise fastapi.HTTPException(
				status_cod=fastapi.status.HTTP_401_UNAUTHORIZED,
				detail="invalid token scope" 
			)
		
		user = db.query(User).filter(User.username==username).first()
		if user is None:
			raise fastapi.HTTPException(
				status_cod=fastapi.status.HTTP_401_UNAUTHORIZED,
				detail="invalid token scope"
			)

		if user.refresh_token is None:
			raise fastapi.HTTPException(
				status_cod=fastapi.status.HTTP_401_UNAUTHORIZED,
				detail="invalid token scope"
			)
		return user
