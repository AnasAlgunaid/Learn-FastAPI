from apscheduler.schedulers.background import BackgroundScheduler

from .jobs import delete_expired_reset_password_tokens


scheduler = BackgroundScheduler()

scheduler.add_job(delete_expired_reset_password_tokens, "interval", hours=6)
