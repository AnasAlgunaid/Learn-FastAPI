from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from core.database import get_db
from auth import auth
from schemas.users import ReadUser

# Dependency
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[ReadUser, Depends(auth.get_current_user)]