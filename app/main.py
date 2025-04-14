import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.auth import router as auth_router
from app.routers.template_routes import router as template_router
from app.routers.api_routes import router as api_router
from app.routers.qr_routes import router as qr_router
from app.routers.admin.admin_routes import router as admin_router
from app.routers.mock_data_api import router as mock_data_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="Farm Monitor API")

# Load environment variables
load_dotenv()

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register routers
app.include_router(auth_router, prefix="/auth")
app.include_router(template_router)
app.include_router(api_router)
app.include_router(qr_router)
app.include_router(admin_router)
app.include_router(mock_data_router)

# Start the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
