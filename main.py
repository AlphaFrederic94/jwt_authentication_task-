from fastapi import FastAPI
from auth import router as auth_router
from grades import router as grades_router
from database import create_tables

app = FastAPI()

# Include the routers for different functionality
app.include_router(auth_router)
app.include_router(grades_router)

# Create tables on startup
@app.on_event("startup")
def startup():
    create_tables()

# Run the server using: uvicorn main:app --reload