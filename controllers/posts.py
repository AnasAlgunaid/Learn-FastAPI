from fastapi import HTTPException
from sqlalchemy.orm import Session
import models.posts as posts_models
import schemas.v1.posts as posts_schemas


# Get all posts
def get_posts(db: Session):
    """Get all posts from the database"""
    try:
        res = db.query(posts_models.Post).all()
        if res:
            return res
        raise HTTPException(status_code=404, detail="No posts found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred: " + str(e))


# Get a post by id
def create_post(post: posts_schemas.CreatePost, db: Session, current_user: int):
    """Create a new post in the database"""
    try:
        new_post = posts_models.Post(
            title=post.title,
            content=post.content,
            user_id=current_user,
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred: " + str(e))
