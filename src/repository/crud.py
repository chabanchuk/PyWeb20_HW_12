from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from sqlalchemy.sql.operators import ilike_op
from src.entity.models import Contact
from src.schemas.schema import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from typing import Optional

async def get_contacts(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    first_name: Optional[str] = None, 
    last_name: Optional[str] = None, 
    email: Optional[str] = None
):
    query = select(Contact)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_contact(db: AsyncSession, contact_id: int):
    result = await db.execute(select(Contact).where(Contact.id == int(contact_id)))
    return result.scalar_one_or_none()

async def create_contact(db: AsyncSession, contact: ContactCreate):
    db_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birth_date=contact.birth_date,
        additional_info=contact.additional_info
    )
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

async def update_contact(db: AsyncSession, contact_id: int, contact: ContactUpdate):
    db_contact = await get_contact(db, contact_id)
    if db_contact:
        update_data = contact.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        db.add(db_contact)
        await db.commit()
        await db.refresh(db_contact)
    return db_contact

async def delete_contact(db: AsyncSession, contact_id: int):
    db_contact = await get_contact(db, contact_id)
    if db_contact:
        await db.delete(db_contact)
        await db.commit()
    return db_contact

async def get_upcoming_birthdays(db: AsyncSession, start_date: datetime, days: int = 7):
    end_date = start_date + timedelta(days=days)

    query = select(Contact).where(
        func.extract('month', Contact.birth_date) >= start_date.month,
        func.extract('day', Contact.birth_date) >= start_date.day,
        func.extract('month', Contact.birth_date) <= end_date.month,
        func.extract('day', Contact.birth_date) <= end_date.day
    )

    result = await db.execute(query)
    return result.scalars().all()