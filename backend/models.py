from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    winner = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())