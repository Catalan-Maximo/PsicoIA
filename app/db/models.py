from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, DateTime, func, Integer

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    hash_id: Mapped[str] = mapped_column(String(64), index=True)
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[DateTime | None]
    initial_state: Mapped[str | None] = mapped_column(String(50))
    risk_score: Mapped[int | None] = mapped_column(Integer)
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(String(10))  # user | assistant | system
    text: Mapped[str] = mapped_column(Text())
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    session = relationship("Session", back_populates="messages")

class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    label: Mapped[str] = mapped_column(String(50))  # leve | moderada | aguda
    probability: Mapped[float | None]
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
