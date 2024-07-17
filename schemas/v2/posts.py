from pydantic import BaseModel
from .users import ReadUserFromPost
from datetime import datetime


class CreatePost(BaseModel):
    title: str
    content: str

    class Config:
        from_attributes = True


class ReadPost(BaseModel):
    post_id: int
    title: str
    content: str
    created_at: datetime
    author: ReadUserFromPost

    class Config:
        from_attributes = True
