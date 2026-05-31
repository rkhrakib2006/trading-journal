from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import User, Trade, TradeAttachment
from app.parser import parse_mt5_file
from typing import List
import os

app = FastAPI(title="Trading Journal API")

# Create DB
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.post("/upload-history/")
async def upload_history(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Parse MT5 File
    content = await file.read()
    try:
        parsed_trades = parse_mt5_file(content, file.filename)
    except Exception as e:
        return {"error": f"Could not parse file: {str(e)}"}

    # User ID 1 is hardcoded for MVP (Assume 1 user)
    user_id = 1 
    
    saved_trades = []
    for t in parsed_trades:
        new_trade = Trade(
            user_id=user_id,
            ticket_number=t.get('ticket_number'),
            symbol=t['symbol'],
            entry_time=t['entry_time'],
            exit_time=t['exit_time'],
            trade_type=t['trade_type'],
            lot_size=t['lot_size'],
            profit_loss=t['profit_loss'],
            commission=t.get('commission', 0)
        )
        db.add(new_trade)
        saved_trades.append(new_trade)
    
    db.commit()
    return {"message": f"Imported {len(saved_trades)} trades successfully"}

@app.get("/trades/")
def get_trades(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    trades = db.query(Trade).offset(skip).limit(limit).all()
    return trades

@app.get("/analytics/")
def get_analytics(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    
    total_pnl = sum([float(t.profit_loss) for t in trades])
    wins = [t for t in trades if float(t.profit_loss) > 0]
    losses = [t for t in trades if float(t.profit_loss) <= 0]
    
    win_rate = (len(wins) / len(trades)) * 100 if trades else 0
    
    # Calculate Profit Factor
    gross_profit = sum([float(t.profit_loss) for t in wins])
    gross_loss = abs(sum([float(t.profit_loss) for t in losses]))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    # Simple Drawdown calc (Peak-to-Trough)
    running_pnl = 0
    peak_pnl = 0
    max_drawdown = 0
    for t in trades:
        running_pnl += float(t.profit_loss)
        if running_pnl > peak_pnl:
            peak_pnl = running_pnl
        drawdown = peak_pnl - running_pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            
    return {
        "total_trades": len(trades),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": round(max_drawdown, 2
