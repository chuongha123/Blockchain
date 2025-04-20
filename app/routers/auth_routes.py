import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.model.farm_data import Farm, FarmReport
from app.model.user import User, UserCreate, Token, UserResponse
from app.services.database import get_db
from app.services.security import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
)

router = APIRouter(tags=["authentication"])
templates = Jinja2Templates(directory=os.path.join("app", "templates"))


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    db_user_by_email = db.query(User).filter(User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login and get JWT token"""
    user, error = authenticate_user(db, form_data.username, form_data.password)

    if error:
        error_messages = {
            "not_found": "Incorrect username or password",
            "invalid_password": "Incorrect username or password",
            "inactive": "Your account is inactivated",
        }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_messages.get(error, "Authentication failed"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # This code will only run if authentication succeeds
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    print("user", user.role)
    return {"access_token": access_token, "token_type": "bearer", "user_role": user.role}


@router.get("/users/me", response_class=HTMLResponse)
async def read_users_me(
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get current user information with farms"""
    # Get user's farms using the relationship
    farms = db.query(Farm).filter(Farm.user_id == current_user.id).all()
    farm_reports = {}

    # Get latest farm report for each farm
    for farm in farms:
        latest_report = db.query(FarmReport).filter(
            FarmReport.farm_id == farm.id
        ).order_by(FarmReport.created_at.desc()).first()

        if latest_report:
            farm_reports[farm.id] = latest_report

    # Render template with user and farm data
    return templates.TemplateResponse(
        "pages/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "farms": farms,
            "farm_reports": farm_reports
        }
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, current_user: User = Depends(get_current_active_user)):
    """Logout user by clearing cookies"""
    response.delete_cookie(key="access_token")
    return {"detail": "Successfully logged out"}
