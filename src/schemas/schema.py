from pydantic import BaseModel, EmailStr
from datetime import date

class ContactBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_info: str

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactInDBBase(ContactBase):
    id: int

    class Config:
        orm_mode = True

class Contact(ContactInDBBase):
    pass

class ContactInDB(ContactInDBBase):
    pass
