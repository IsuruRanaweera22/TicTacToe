from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

from database import get_db, engine
import models

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class GameState(BaseModel):
    board: List[str]
    is_x_next: bool

class GameResultCreate(BaseModel):
    winner: str

class GameResultResponse(GameResultCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

def check_winner(board):
    lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]
    for line in lines:
        if board[line[0]] and board[line[0]] == board[line[1]] == board[line[2]]:
            return board[line[0]]
    return None

def is_board_full(board):
    return all(cell is not None for cell in board)

def get_ai_move(board):
    prompt = f"Given the Tic Tac Toe board: {board}, where should 'O' play next? Respond with only the index (0-8) of the best move."
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.5,
    )
    move = int(response.choices[0].text.strip())
    return move

def insert_game_result(db: Session, winner: str):
    game_result = models.GameResult(winner=winner)
    db.add(game_result)
    db.commit()
    db.refresh(game_result)
    return game_result

def get_game_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.GameResult).order_by(models.GameResult.timestamp.desc()).offset(skip).limit(limit).all()

@app.post("/game/move")
def make_move(game_state: GameState, db: Session = Depends(get_db)):
    board = game_state.board
    is_x_next = game_state.is_x_next

    if not is_x_next:
        # AI's turn
        ai_move = get_ai_move(board)
        if board[ai_move] is None:
            board[ai_move] = 'O'
        else:
            raise HTTPException(status_code=400, detail="Invalid AI move")

    winner = check_winner(board)
    if winner:
        game_result = insert_game_result(db, winner)
        return {"board": board, "winner": winner, "game_over": True, "game_result": GameResultResponse.from_orm(game_result)}

    if is_board_full(board):
        game_result = insert_game_result(db, "Draw")
        return {"board": board, "winner": "Draw", "game_over": True, "game_result": GameResultResponse.from_orm(game_result)}

    return {"board": board, "winner": None, "game_over": False}

@app.get("/game/results", response_model=List[GameResultResponse])
def get_game_results_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    results = get_game_results(db, skip, limit)
    return results
