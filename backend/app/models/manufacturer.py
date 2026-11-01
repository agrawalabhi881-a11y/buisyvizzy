from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.distributor import Distributor


class Manufacturer(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "manufacturers"

    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(40))

    distributors: Mapped[list[Distributor]] = relationship(
        back_populates="manufacturer"
    )
