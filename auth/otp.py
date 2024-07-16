from fastapi import HTTPException, APIRouter, BackgroundTasks
from models.users import User
import os
from twilio.rest import Client
from core.dependencies import user_dependency, db_dependency

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
service_sid = os.environ["TWILIO_SERVICE_SID"]


client = Client(account_sid, auth_token)

service = client.verify.v2.services.create(friendly_name="Learning FastAPI")


def send_otp_using_twilio(phone: str):
    try:
        verification = client.verify.v2.services(service_sid).verifications.create(
            to=phone, channel="sms"
        )
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")


@router.get("/send-otp")
async def send_otp(current_user: user_dependency, background_tasks: BackgroundTasks):
    if current_user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    background_tasks.add_task(send_otp_using_twilio, current_user.phone)
    return {"msg": "OTP sent successfully"}


@router.post("/verify-otp")
async def verify_otp(code: int, current_user: user_dependency, db: db_dependency):
    try:
        if current_user.is_verified:
            return {"msg": "User is already verified"}

        verification_check = client.verify.v2.services(
            service_sid
        ).verification_checks.create(to=current_user.phone, code=code)

        if verification_check.status == "approved":
            user = db.query(User).filter(User.user_id == current_user.user_id).first()
            user.is_verified = True
            db.commit()
            return {"msg": "Verification successful"}
        else:
            return {"msg": "Invalid OTP code"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify OTP")
