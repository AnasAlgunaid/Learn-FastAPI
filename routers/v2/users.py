from fastapi import APIRouter, HTTPException, Depends
from fastapi import status
from pydantic import PositiveInt
import schemas.v1.users as users_schemas
import controllers.users as users_controller
from core.dependencies import db_dependency, user_dependency
import redis
from caching.redis import get_redis_client

router = APIRouter(
    prefix="/users",
    tags=["Users v2"],
)


# Get all users
@router.get("/", response_model=list[users_schemas.ReadUser])
def get_users(
    db: db_dependency,
    limit: PositiveInt = 10,
):
    return users_controller.get_users(db, limit)


# Create a new user
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=users_schemas.ReadUser,
)
def create_user(user: users_schemas.CreateUser, db: db_dependency):
    return users_controller.create_user(user, db)


# Get a user by ID
@router.get("/{user_id}", response_model=users_schemas.ReadUser)
def get_user(
    user_id: int,
    db: db_dependency,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    return users_controller.get_user(user_id, db, redis_client)


# Update a user by ID
@router.put("/{user_id}", response_model=users_schemas.ReadUser)
def update_user(
    user_id: int,
    updated_user: users_schemas.UpdateUser,
    db: db_dependency,
    current_user: user_dependency,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this user"
        )
    return users_controller.update_user(user_id, updated_user, db, redis_client)


# Delete a user by ID
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: db_dependency,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    return users_controller.delete_user(user_id, db, redis_client)


@router.post("/generate-pdf/{user_id}")
def generate_pdf(user_id: int, db: db_dependency):
    return users_controller.generate_pdf(user_id, db)
