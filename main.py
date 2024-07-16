from fastapi import FastAPI
from core.database import engine, Base
from routers import users, posts
from auth import auth, otp, reset_password
from middlewares.logger import LoggerMiddleware
from schemas.users import ReadUser
from core.dependencies import user_dependency
from core.metadata import tags_metadata
from jobs.scheduler import scheduler
from caching.redis import get_redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users Management API", openapi_tags=tags_metadata)

# Start the scheduler
scheduler.start()

# Redis client
redis_client = get_redis_client()


# Function to return the Redis client
def get_redis_client():
    return redis_client


# Add routers
app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(reset_password.router)
app.include_router(users.router)
app.include_router(posts.router)

# Logger Middleware
app.add_middleware(LoggerMiddleware)


@app.get("/protected", response_model=ReadUser)
async def protected_route(current_user: user_dependency):
    if current_user:
        return current_user


@app.get("/")
def home():
    return {"msg": "Hello World"}
