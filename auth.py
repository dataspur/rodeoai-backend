from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.config import SECRET_KEY
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# Token settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    tier: str
    daily_usage: int = 0
    api_key: str

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

# Endpoints
@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        api_key=f"rai_{secrets.token_urlsafe(32)}",
        tier="free"
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # Get user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Calculate daily usage
    from sqlalchemy import func
    from app.models import APIUsage
    
    result = await db.execute(
        select(func.count(APIUsage.id))
        .where(APIUsage.user_id == user.id)
        .where(func.date(APIUsage.timestamp) == datetime.utcnow().date())
    )
    daily_usage = result.scalar() or 0
    
    return {
        "id": user.id,
        "email": user.email,
        "tier": user.tier,
        "daily_usage": daily_usage,
        "api_key": user.api_key
    }

# Google OAuth (placeholder for future implementation)
@router.get("/google")
async def google_login():
    raise HTTPException(status_code=501, detail="Google OAuth coming soon")

@router.get("/google/callback")
async def google_callback():
    raise HTTPException(status_code=501, detail="Google OAuth coming soon")

# Apple OAuth (placeholder for future implementation)
@router.get("/apple")
async def apple_login():
    raise HTTPException(status_code=501, detail="Apple OAuth coming soon")

@router.get("/apple/callback")
async def apple_callback():
    raise HTTPException(status_code=501, detail="Apple OAuth coming soon")
