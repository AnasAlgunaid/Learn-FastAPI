from arrow import get
from sqlalchemy.orm import Session
from core.dependencies import db_dependency
from datetime import datetime
from models.password_resets import PasswordReset
from core.database import get_db


def delete_expired_reset_password_tokens():
    db: Session = next(get_db())  # Obtain the session from the generator
    try:
        tokens_deleted = (
            db.query(PasswordReset)
            .filter(PasswordReset.expires_at < datetime.now())
            .delete()
        )
        db.commit()
        return {"msg": f"{tokens_deleted} expired password reset tokens removed"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete expired tokens: {str(e)}"}
    finally:
        db.close()
