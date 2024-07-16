from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
import controllers.posts as posts_controllers
import schemas.posts as posts_schemas
from core.dependencies import db_dependency, user_dependency


router = APIRouter()


@router.get("/posts", response_model=list[posts_schemas.ReadPost], tags=["Posts"])
def get_posts(db: db_dependency):
    return posts_controllers.get_posts(db)


@router.post("/posts", response_model=posts_schemas.ReadPost, tags=["Posts"])
def create_post(
    post: posts_schemas.CreatePost, db: db_dependency, current_user: user_dependency
):
    if not current_user:
        return {"msg": "Unauthorized"}
    return posts_controllers.create_post(post, db, current_user.user_id)
