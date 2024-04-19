from pydantic import BaseModel

class UserCreate(BaseModel):
	username: str
	password: str


class UserDB(BaseModel):
	id: int
	username: str
	hash_password: str

	class Config:
		orm_mode = True


class Token(BaseModel):
	access_token: str
	refresh_token: str
