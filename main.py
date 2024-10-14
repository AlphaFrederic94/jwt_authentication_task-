from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from grades import router as grades_router
from database import create_tables

app = FastAPI()

origins = [
    "http://localhost:3000",  # Frontend URL 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all or specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Include the routers for different functionality
app.include_router(auth_router)
app.include_router(grades_router)

# Create tables on startup
@app.on_event("startup")
def startup():
    create_tables()

# Run the server using: uvicorn main:app --reload