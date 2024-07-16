from fastapi import APIRouter, HTTPException, BackgroundTasks
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pydantic import EmailStr
import os
from typing import Any
from models.users import User
from models.password_resets import PasswordReset
from core.dependencies import db_dependency
from datetime import datetime, timedelta
from core.hashing import get_password_hash

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


# Generate a new password reset token and send it via email
def send_password_reset_email(email: EmailStr, token: str):
    message = Mail(
        from_email="aljunaidanas@gmail.com",
        to_emails=email,
        subject="Password Reset Request",
        html_content=f"Click <a href='http://127.0.0.1:8000/reset-password?token={token}'>here</a> to reset your password.",
    )
    try:
        sg = SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
        sg.send(message)
        return True
    except Exception as e:
        return False


@router.post("/forgot-password", response_model=Any)
async def forgot_password(
    user_email: EmailStr, db: db_dependency, background_tasks: BackgroundTasks
):
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a password reset token (you can use a JWT or a random string)
    import secrets

    token = secrets.token_urlsafe(32)

    reset_password = PasswordReset(
        user_id=user.user_id,
        token=token,
        expires_at=datetime.now() + timedelta(hours=1),
    )

    db.add(reset_password)
    db.commit()

    # Send the password reset email
    background_tasks.add_task(send_password_reset_email, user_email, token)

    return {"msg": "Password reset instructions sent to your email"}


# Route to handle the password reset link clicked in the email
@router.post("/reset-password", response_model=Any)
async def reset_password(token: str, new_password: str, db: db_dependency):
    password_reset = (
        db.query(PasswordReset).filter(PasswordReset.token == token).first()
    )
    if not password_reset or password_reset.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Find the user associated with the user id in the PasswordReset instance
    user = db.query(User).filter(User.user_id == password_reset.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's password
    user.hashed_password = get_password_hash(new_password)
    db.commit()

    db.delete(password_reset)
    db.commit()

    return {"msg": "Password reset successfully"}
