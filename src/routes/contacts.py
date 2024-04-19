from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.schema import ContactCreate, ContactUpdate, Contact
from src.repository import crud
from src.auth.routes import Auth
from typing import Optional, List
from datetime import datetime


auth_service = Auth()
router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get("/", response_model=List[Contact])
async def get_contacts(
    user = Depends(auth_service.get_user),
    skip: int = 0, 
    limit: int = 100, 
    first_name: Optional[str] = None, 
    last_name: Optional[str] = None, 
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    contacts = await crud.get_contacts(
        db, 
        skip=skip, 
        limit=limit, 
        first_name=first_name, 
        last_name=last_name, 
        email=email
    )
    return contacts

@router.get("/{contact_id}", response_model=Contact)
async def get_contact(contact_id: int = Path(..., title="The ID of the contact to get"), db: AsyncSession = Depends(get_db)):
    contact = await crud.get_contact(db, contact_id=contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_contact(db=db, contact=contact)

@router.put("/{contact_id}", response_model=Contact)
async def update_contact(contact_id: int = Path(..., title="The ID of the contact to update"), contact: ContactUpdate = Depends(), db: AsyncSession = Depends(get_db)):
    updated_contact = await crud.update_contact(db=db, contact_id=int(contact_id), contact=contact)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact

@router.delete("/{contact_id}", response_model=Contact)
async def delete_contact(contact_id: int = Path(..., title="The ID of the contact to delete"), db: AsyncSession = Depends(get_db)):
    contact = await crud.delete_contact(db=db, contact_id=int(contact_id))
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.get("/upcoming-birthdays", response_model=List[Contact])
async def get_upcoming_birthdays(
    start_date: datetime = Query(datetime.now().date()),
    db: AsyncSession = Depends(get_db)
):
    contacts = await crud.get_upcoming_birthdays(db, start_date=start_date)
    return contacts
