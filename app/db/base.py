# Import all models here for Alembic to detect them
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

from app.db.database import Base

# This ensures all models are imported when base is imported