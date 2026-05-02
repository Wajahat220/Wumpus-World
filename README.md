# Wumpus World Agent

# Wumpus World Agent - AI2002 Assignment 06

A web-based **Knowledge-Based Agent** that navigates a Wumpus World using **Propositional Logic** and **Resolution Refutation Algorithm**.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (Deployed on Vercel)                      │
│                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ Grid View   │    │ Metrics      │    │ Controls   │ │
│  │             │    │ Dashboard    │    │            │ │
│  └─────────────┘    └──────────────┘    └────────────┘ │
└──────────────────────────┬──────────────────────────────┘
                           │ REST API
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                          │
│                (Deployed on Railway)                      │
│                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ Game Logic  │    │ Knowledge    │    │ Resolution │ │
│  │             │    │ Base         │    │ Engine     │ │
│  └─────────────┘    └──────────────┘    └────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Features

- Dynamic grid sizing (3×3 to 10×10)
- Real-time grid visualization
- Resolution Refutation algorithm for safe cell detection
- Knowledge Base management with propositional logic
- Autonomous agent navigation
- Live inference step counter
- Percept display (Breeze, Stench, Glitter)

## Tech Stack

### Frontend
- React 18
- Axios (API calls)
- CSS3 (Modern styling)

### Backend
- FastAPI (Modern Python web framework)
- Uvicorn (ASGI server)
- Pydantic (Data validation)

## Quick Start

### 1. Backend Setup (Local Development)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Backend runs on: `http://localhost:5000`
API Documentation: `http://localhost:5000/docs`

### 2. Frontend Setup (Local Development)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: `http://localhost:3000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Root endpoint |
| `GET /api/health` | GET | Health check |
| `POST /api/game/new` | POST | Start new game with grid size |
| `GET /api/game/state` | GET | Get current game state |
| `POST /api/game/move` | POST | Move agent (up/down/left/right) |
| `POST /api/game/auto` | POST | Autonomous agent move |
| `POST /api/game/safe` | POST | Check if cell is safe |

## Algorithm: Resolution Refutation

### How It Works

1. **Knowledge Base (KB)**: Stores propositional logic clauses
2. **Percept Processing**: When receiving Breeze or Stench, adds rules to KB
   - Breeze ⇒ ∃ adjacent pit
   - Stench ⇒ ∃ adjacent wumpus
3. **Safety Check**: Before moving, uses Resolution Refutation:
   - Assume cell has pit (P_2,2) OR wumpus (W_2,2)
   - Add negated query to KB
   - Apply resolution repeatedly
   - If empty clause (contradiction) found → cell is safe

### Example

```
KB: {B_1,1 ⇒ P_0,0 ∨ P_1,1, B_1,1}
Query: Is (0,0) safe? (¬P_0,0 ∧ ¬W_0,0)

1. Add ¬P_0,0 to KB
2. Resolution finds P_0,0 and ¬P_0,0 → contradiction
3. Therefore P_0,0 is false → cell is safe
```

## Deployment

### Backend: Railway (Free Tier)

1. Create GitHub repository for backend
2. Connect to Railway at railway.app
3. Deploy from GitHub
4. Note the deployment URL

### Frontend: Vercel (Free Tier)

1. Update `vercel.json` with Railway URL
2. Create GitHub repository for frontend
3. Connect to Vercel at vercel.com
4. Deploy from GitHub

## Live Demo

- **Frontend**: https://wumpus-world.vercel.app
- **Backend**: https://wumpus-world-api.railway.app
- **API Docs**: https://wumpus-world-api.railway.app/docs

## Project Structure

```
wumpus_world_app/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── Procfile           # Railway deployment config
├── frontend/
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styles
│   │   ├── index.js       # Entry point
│   │   └── index.css      # Global styles
│   ├── package.json       # Node dependencies
│   ├── vercel.json        # Vercel config
│   └── .env              # Environment variables
└── README.md             # This file
```

## License

MIT License

## Author

AI2002 - Artificial Intelligence Assignment 06

