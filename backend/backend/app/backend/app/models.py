from sqlalchemy import Column, Integer, String, Float, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticket_number = Column(Integer)
    symbol = Column(String)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    trade_type = Column(String) # buy/sell
    lot_size = Column(Float)
    profit_loss = Column(Numeric(10, 2))
    commission = Column(Numeric(10, 2), default=0)
    swap = Column(Numeric(10, 2), default=0)
    notes = Column(String, nullable=True)

    attachments = relationship("TradeAttachment", back_populates="trade")

class TradeAttachment(Base):
    __tablename__ = "trade_attachments"
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    file_name = Column(String)
    file_path = Column(String)
    
    trade = relationship("Trade", back_populates="attachments")
