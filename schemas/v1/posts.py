from pydantic import BaseModel
from .users import ReadUser


class CreatePost(BaseModel):
    title: str
    content: str

    class Config:
        from_attributes = True


class ReadPost(BaseModel):
    post_id: int
    title: str
    content: str
    author: ReadUser

    class Config:
        from_attributes = True
