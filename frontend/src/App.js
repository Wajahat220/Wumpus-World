import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

// API URL - Update this to your deployed backend URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
const [gameState, setGameState] = useState(null);
const [gridSize, setGridSize] = useState({ rows: 4, cols: 4 });
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [message, setMessage] = useState('');

const startNewGame = useCallback(async () => {
setLoading(true);
setError(null);
setMessage('');
try {
const response = await axios.post(`${API_URL}/api/game/new`, gridSize);
setGameState(response.data.state);
setMessage('New game started! Use the controls to navigate or let AI auto-move.');
} catch (err) {
setError('Failed to connect to backend. Make sure the server is running.');
console.error(err);
} finally {
setLoading(false);
}
}, [gridSize]);

const fetchState = useCallback(async () => {
try {
const response = await axios.get(`${API_URL}/api/game/state`);
setGameState(response.data);
} catch (err) {
console.error('Failed to fetch state:', err);
}
}, []);

const moveAgent = async (direction) => {
setLoading(true);
setError(null);
try {
const response = await axios.post(`${API_URL}/api/game/move`, { direction });
const data = response.data;

setGameState(prev => ({
...prev,
agent_pos: data.position,
percepts: data.percepts,
visited: data.visited,
safe: data.safe,
agent_alive: data.alive,
inference_steps: data.inference_steps
}));

checkGameEnd(data);
} catch (err) {
setError('Move failed. Check if game is running.');
} finally {
setLoading(false);
}
};

const autoMove = async () => {
setLoading(true);
setError(null);
try {
const response = await axios.post(`${API_URL}/api/game/auto`);
const data = response.data;

setGameState(prev => ({
...prev,
agent_pos: data.position,
percepts: data.percepts,
visited: data.visited,
safe: data.safe,
agent_alive: data.alive,
inference_steps: data.inference_steps
}));

if (data.message) {
setMessage(data.message);
}

checkGameEnd(data);
} catch (err) {
setError('Auto move failed. Check if game is running.');
} finally {
setLoading(false);
}
};

const checkGameEnd = (data) => {
if (!data.alive) {
setError('Agent died! Game Over. Click "New Game" to restart.');
setMessage('');
}
};

const getCellColor = (row, col) => {
if (!gameState) return '#9ca3af';

const inVisited = gameState.visited.some(v => v[0] === row && v[1] === col);
const isSafe = gameState.safe.some(s => s[0] === row && s[1] === col);
const isAgent = gameState.agent_pos[0] === row && gameState.agent_pos[1] === col;
const isKnownPit = gameState.known_pits.some(p => p[0] === row && p[1] === col);
const isKnownWumpus = gameState.known_wumpus.some(w => w[0] === row && w[1] === col);
const isGold = gameState.gold_pos && gameState.gold_pos[0] === row && gameState.gold_pos[1] === col;

if (!gameState.agent_alive) return '#6b7280';
if (isAgent) return '#3b82f6';
if (isKnownPit || isKnownWumpus) return '#ef4444';
if (isGold) return '#fbbf24';
if (inVisited) return '#22c55e';
if (isSafe) return '#86efac';
return '#9ca3af';
};

const getCellContent = (row, col) => {
if (!gameState) return '';

const isAgent = gameState.agent_pos[0] === row && gameState.agent_pos[1] === col;
const isKnownPit = gameState.known_pits.some(p => p[0] === row && p[1] === col);
const isKnownWumpus = gameState.known_wumpus.some(w => w[0] === row && w[1] === col);
const isGold = gameState.gold_pos && gameState.gold_pos[0] === row && gameState.gold_pos[1] === col;

if (isAgent) return '🤖';
if (isKnownPit) return '🕳️';
if (isKnownWumpus) return '👹';
if (isGold) return '✨';
return '';
};

const getCellTooltip = (row, col) => {
if (!gameState) return '';

const inVisited = gameState.visited.some(v => v[0] === row && v[1] === col);
const isSafe = gameState.safe.some(s => s[0] === row && s[1] === col);
const isAgent = gameState.agent_pos[0] === row && gameState.agent_pos[1] === col;
const isKnownPit = gameState.known_pits.some(p => p[0] === row && p[1] === col);
const isKnownWumpus = gameState.known_wumpus.some(w => w[0] === row && w[1] === col);

if (isAgent) return 'Agent Position';
if (isKnownPit) return 'Pit (Danger!)';
if (isKnownWumpus) return 'Wumpus (Danger!)';
if (inVisited) return 'Visited (Safe)';
if (isSafe) return 'Safe (from inference)';
return 'Unknown';
};

useEffect(() => {
startNewGame();
}, []);

return (
<div className="app">
<header className="header">
<h1>Wumpus World Agent</h1>
<p>Knowledge-Based Agent with Resolution Refutation | AI2002 Assignment 6</p>
</header>

<main className="main">
<div className="controls">
<div className="control-group">
<label>Grid Size:</label>
<input
type="number"
min="3"
max="10"
value={gridSize.rows}
onChange={(e) => setGridSize({ ...gridSize, rows: parseInt(e.target.value) || 4 })}
disabled={loading}
/>
<span>×</span>
<input
type="number"
min="3"
max="10"
value={gridSize.cols}
onChange={(e) => setGridSize({ ...gridSize, cols: parseInt(e.target.value) || 4 })}
disabled={loading}
/>
</div>
<button onClick={startNewGame} disabled={loading} className="btn btn-primary">
New Game
</button>
</div>

{error && <div className="error-message">{error}</div>}
{message && !error && <div className="success-message">{message}</div>}

{gameState && (
<>
<div className="content-wrapper">
<div className="grid-container">
<h2>Grid World</h2>
<div
className="grid"
style={{
gridTemplateColumns: `repeat(${gameState.grid_size.cols}, 70px)`,
gridTemplateRows: `repeat(${gameState.grid_size.rows}, 70px)`
}}
>
{Array.from({ length: gameState.grid_size.rows }).map((_, row) =>
Array.from({ length: gameState.grid_size.cols }).map((_, col) => (
<div
key={`${row}-${col}`}
className="cell"
style={{ backgroundColor: getCellColor(row, col) }}
title={getCellTooltip(row, col)}
>
<span className="cell-content">{getCellContent(row, col)}</span>
{gameState.agent_pos[0] === row && gameState.agent_pos[1] === col && (
<div className="percepts">
{gameState.percepts.breeze && <span>💨</span>}
{gameState.percepts.stench && <span>🌀</span>}
{gameState.percepts.glitter && <span>✨</span>}
</div>
)}
</div>
))
)}
</div>
</div>

<div className="sidebar">
<div className="metrics">
<div className="metric-card">
<h3>Inference Steps</h3>
<p className="metric-value">{gameState.inference_steps}</p>
</div>
<div className="metric-card">
<h3>Current Percepts</h3>
<div className="percepts-display">
<span className={`percept ${gameState.percepts.breeze ? 'active' : ''}`}>
💨 Breeze
</span>
<span className={`percept ${gameState.percepts.stench ? 'active' : ''}`}>
🌀 Stench
</span>
<span className={`percept ${gameState.percepts.glitter ? 'active' : ''}`}>
✨ Glitter
</span>
</div>
</div>
<div className="metric-card">
<h3>Statistics</h3>
<div className="stats">
<p>Visited: <strong>{gameState.visited.length}</strong></p>
<p>Safe Cells: <strong>{gameState.safe.length}</strong></p>
<p>Known Hazards: <strong>{gameState.known_pits.length + gameState.known_wumpus.length}</strong></p>
</div>
</div>
</div>

<div className="legend">
<h3>Legend</h3>
<div className="legend-item">
<span className="color-box" style={{ backgroundColor: '#3b82f6' }}></span>
<span>Agent</span>
</div>
<div className="legend-item">
<span className="color-box" style={{ backgroundColor: '#22c55e' }}></span>
<span>Visited</span>
</div>
<div className="legend-item">
<span className="color-box" style={{ backgroundColor: '#86efac' }}></span>
<span>Safe (Inferred)</span>
</div>
<div className="legend-item">
<span className="color-box" style={{ backgroundColor: '#ef4444' }}></span>
<span>Hazard Found</span>
</div>
<div className="legend-item">
<span className="color-box" style={{ backgroundColor: '#9ca3af' }}></span>
<span>Unknown</span>
</div>
</div>
</div>
</div>

<div className="controls">
<div className="direction-controls">
<button onClick={() => moveAgent('up')} disabled={loading || !gameState.agent_alive}>
↑
</button>
<div className="row">
<button onClick={() => moveAgent('left')} disabled={loading || !gameState.agent_alive}>
←
</button>
<button onClick={() => moveAgent('right')} disabled={loading || !gameState.agent_alive}>
→
</button>
</div>
<button onClick={() => moveAgent('down')} disabled={loading || !gameState.agent_alive}>
↓
</button>
</div>
<button
onClick={autoMove}
disabled={loading || !gameState.agent_alive}
className="btn btn-success"
>
🤖 Auto Move (AI)
</button>
</div>

<div className="info-section">
<h3>How It Works</h3>
<p>
The agent uses <strong>Resolution Refutation</strong> to deduce safe cells:
</p>
<ul>
<li>When it senses <strong>Breeze</strong> or <strong>Stench</strong>, it adds rules to its Knowledge Base</li>
<li>Before moving, it asks: "Is this cell safe?" using automated theorem proving</li>
<li>Resolution proves safety by finding a contradiction when assuming the cell is unsafe</li>
</ul>
</div>
</>
)}
</main>

<footer className="footer">
<p>Artificial Intelligence</p>
</footer>
</div>
);
}

export default App;
