from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base for all application database models."""


from app import models as _models  # noqa: F401
