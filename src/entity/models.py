from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from src.auth.models import User


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    email = Column(String(120), unique=True, index=True)
    phone_number = Column(String(20), unique=True, index=True)
    birth_date = Column(Date)
    additional_info = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="contacts")


    def __init__(self, first_name: str, last_name: str, email: str, phone_number: str, birth_date: Date, additional_info: Text = None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.birth_date = birth_date
        self.additional_info = additional_info

    def __repr__(self):
        return f"<Contact(name='{self.first_name} {self.last_name}', email='{self.email}')>"
