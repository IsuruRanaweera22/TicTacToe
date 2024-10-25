import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TicTacToe = () => {
  const [board, setBoard] = useState(Array(9).fill(null));
  const [isXNext, setIsXNext] = useState(true);
  const [winner, setWinner] = useState(null);
  const [gameOver, setGameOver] = useState(false);
  const [gameResults, setGameResults] = useState([]);

  useEffect(() => {
    fetchGameResults();
  }, []);

  const fetchGameResults = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/game/results`);
      setGameResults(response.data);
    } catch (error) {
      console.error('Error fetching game results:', error);
    }
  };

  const handleClick = async (i) => {
    if (gameOver || board[i]) return;

    const newBoard = [...board];
    newBoard[i] = isXNext ? 'X' : 'O';
    setBoard(newBoard);
    setIsXNext(!isXNext);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/game/move`, {
        board: newBoard,
        is_x_next: !isXNext,
      });
      const { board: updatedBoard, winner: newWinner, game_over: newGameOver } = response.data;
      setBoard(updatedBoard);
      setWinner(newWinner);
      setGameOver(newGameOver);
    } catch (error) {
      console.error('Error making move:', error);
    }
  };

  const renderSquare = (i) => (
    <button className="square" onClick={() => handleClick(i)}>
      {board[i]}
    </button>
  );

  const resetGame = () => {
    setBoard(Array(9).fill(null));
    setIsXNext(true);
    setWinner(null);
    setGameOver(false);
    fetchGameResults();
  };

  let status;
  if (winner) {
    status = `Winner: ${winner}`;
  } else if (gameOver) {
    status = 'Draw';
  } else {
    status = `Next player: ${isXNext ? 'X' : 'O'}`;
  }

  return (
    <div className="tic-tac-toe">
      <div className="status">{status}</div>
      <div className="board">
        <div className="board-row">
          {renderSquare(0)}
          {renderSquare(1)}
          {renderSquare(2)}
        </div>
        <div className="board-row">
          {renderSquare(3)}
          {renderSquare(4)}
          {renderSquare(5)}
        </div>
        <div className="board-row">
          {renderSquare(6)}
          {renderSquare(7)}
          {renderSquare(8)}
        </div>
      </div>
      <button className="new-game" onClick={resetGame}>New Game</button>
      <div className="game-results">
        <h3>Game Results</h3>
        <ul>
          {gameResults.map((result) => (
            <li key={result.id}>
              Winner: {result.winner}, Time: {new Date(result.timestamp).toLocaleString()}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TicTacToe;
