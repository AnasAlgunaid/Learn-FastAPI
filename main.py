from fastapi import FastAPI, Request
from core.database import engine, Base
from routers.v1 import users as users_v1, posts as posts_v1
from routers.v2 import users as users_v2, posts as posts_v2

from auth import auth, otp, reset_password
from schemas.v1.users import ReadUser
from core.dependencies import user_dependency
from core.metadata import tags_metadata
from jobs.scheduler import scheduler
from caching.redis import get_redis_client
from middlewares.logger import log_requests

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Users Management API",
    description="This is a simple API to manage users",
    version="1.0.0",
)

# Start the scheduler
scheduler.start()

# Redis client
redis_client = get_redis_client()

# Middleware to log each request
app.middleware("http")(log_requests)


# Function to return the Redis client
def get_redis_client():
    return redis_client


# Add routers
app.include_router(users_v1.router, prefix="/v1")
app.include_router(posts_v1.router, prefix="/v1")
app.include_router(users_v2.router, prefix="/v2")
app.include_router(posts_v2.router, prefix="/v2")
app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(reset_password.router)


@app.get("/protected", response_model=ReadUser)
async def protected_route(current_user: user_dependency):
    if current_user:
        return current_user


@app.get("/")
def home():
    return {"msg": "Hello World"}
