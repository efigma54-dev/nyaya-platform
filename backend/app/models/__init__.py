# backend/app/models/__init__.py
from app.models.legal import Act, ActType, Amendment, LawCategory, Section
from app.models.user import User
from app.models.analytics import QueryLog

__all__ = [
    "Act",
    "Section",
    "Amendment",
    "ActType",
    "LawCategory",
    "User",
    "QueryLog",
]
