from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.routes import contacts
from src.auth import routes
from src.database.db import get_db
from asyncio import CancelledError
import uvicorn

app = FastAPI()
app.include_router(contacts.router, prefix='/api')
app.include_router(routes.router, prefix='/auth')


@app.get("/")
def index():
    return {"message": "Contacts API"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except CancelledError:
        print("Запит було скасовано")
        raise HTTPException(status_code=500, detail="Запит було скасовано")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    
if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="localhost", port=8000, reload=True
    )