import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

from app.services.database import engine, Base
from app.routers.auth_routes import router as auth_router
from app.routers.template_routes import router as template_router
from app.routers.api_routes import router as api_router
from app.routers.qr_routes import router as qr_router
from app.routers.admin.admin_routes import router as admin_router
from app.routers.mock_data_api import router as mock_data_router
from app.routers.farm_routes import router as farm_router
from app.routers.user_farm_routes import router as user_farm_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="Farm Monitor API")


# Add exception handler for authentication errors
@app.exception_handler(HTTPException)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    # For other exceptions, let FastAPI handle them
    raise exc


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
app.include_router(user_farm_router)

# Start the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
