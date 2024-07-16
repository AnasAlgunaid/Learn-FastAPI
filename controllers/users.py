from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import PositiveInt
import models.users as users_models
import schemas.users as users_schemas
from core.hashing import get_password_hash
from datetime import datetime
from fastapi.responses import FileResponse
import redis
import json
from fastapi.encoders import jsonable_encoder
import logging
from weasyprint import HTML


def get_users(
    db: Session,
    limit: PositiveInt,
):
    res = db.query(users_models.User).limit(limit).all()
    if res:
        return res
    raise HTTPException(status_code=404, detail="No users found")


def get_user(user_id: int, db: Session, redis_client: redis.Redis):
    cache_key = f"user_profile:{user_id}"
    cached_profile = redis_client.get(cache_key)

    if cached_profile:
        return json.loads(cached_profile)

    result = (
        db.query(users_models.User).filter(users_models.User.user_id == user_id).first()
    )

    if result:
        result_dict = jsonable_encoder(result)
        read_user = users_schemas.ReadUser.model_validate(result_dict)
        read_user_dict = jsonable_encoder(read_user)

        redis_client.set(cache_key, json.dumps(read_user_dict), ex=10)
        return result

    raise HTTPException(status_code=404, detail="User not found")


def create_user(
    user: users_schemas.CreateUser,
    db: Session,
):
    try:
        new_user = users_models.User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            username=user.username,
            hashed_password=get_password_hash(user.password),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def update_user(
    user_id: int,
    updated_user: users_schemas.UpdateUser,
    db: Session,
    redis_client: redis.Redis,
):
    # Update the user with the given user_id
    try:
        user = (
            db.query(users_models.User)
            .filter(users_models.User.user_id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update only the provided fields
        if updated_user.name is not None:
            user.name = updated_user.name
        if updated_user.username is not None:
            user.username = updated_user.username
        if updated_user.email is not None:
            user.email = updated_user.email
        if updated_user.phone is not None:
            user.phone = updated_user.phone

        db.commit()
        db.refresh(user)

        # Invalidate the cache
        cache_key = f"user_profile:{user_id}"
        redis_client.delete(cache_key)

        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()  # Rollback any changes if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


def delete_user(user_id: int, db: Session, redis_client: redis.Redis):
    try:
        # Attempt to delete the user with the given user_id
        result = (
            db.query(users_models.User)
            .filter(users_models.User.user_id == user_id)
            .delete(synchronize_session=False)
        )
        db.commit()

        if result == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # Invalidate the cache
        cache_key = f"user_profile:{user_id}"
        redis_client.delete(cache_key)

        return {"msg": "User deleted successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        db.rollback()  # Rollback any changes if an exception occurs
        raise HTTPException(status_code=500, detail="An error occurred: " + str(e))


async def generate_pdf(user_id: int, db: Session):
    # Get the user information
    user = get_user(user_id, db)

    # HTML template for generating PDF
    html_content = f"""
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{user.name}</title>
    <style>
      * {{
        font-family: Arial, sans-serif;
        padding: 0;
        margin: 0;
        box-sizing: border-box;
      }}
      body {{
        padding: 16px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
      }}
      th {{
        background-color: indigo;
        font-weight: bold;
        color: white;
      }}
      th,
      td {{
        border: 1px solid black;
        padding: 16px;
        text-align: left;
      }}

      header {{
        background-color: indigo;
        color: white;
        text-align: center;
        padding: 16px;
        font-size: 12px;
      }}
      footer {{
        text-align: center;
        margin-top: 16px;
        color: #9aa5b1;
      }}
    </style>
  </head>
  <body>
    <header>
      <h1>{user.name}</h1>
    </header>
    <table>
      <tr>
        <th>User ID</th>
        <td>{ user.user_id }</td>
      </tr>
      <tr>
        <th>Username</th>
        <td>{ user.username }</td>
      </tr>
      <tr>
        <th>Email</th>
        <td>{ user.email }</td>
      </tr>
      <tr>
        <th>Phone</th>
        <td>{ user.phone }</td>
      </tr>
      <tr>
        <th>Verified</th>
        <td>{ user.is_verified }</td>
      </tr>
      <tr>
        <th>Created At</th>
        <td>{ user.created_at.strftime("%Y-%m-%d %H:%M:%S") }</td>
      </tr>
    </table>

    <footer>
      <p>Printed at { datetime.now().strftime("%Y-%m-%d %H:%M:%S") }</p>
    </footer>
  </body>
</html>
    """

    # Generate PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()

    # Save the PDF to a temporary file
    pdf_filename = "templates/user_information.pdf"
    with open(pdf_filename, "wb") as f:
        f.write(pdf)

    # Return the PDF file as a response
    return FileResponse(
        pdf_filename,
        media_type="application/pdf",
        filename=user.name.replace(" ", "_") + ".pdf",
    )
