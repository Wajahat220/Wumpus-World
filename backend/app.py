"""
Wumpus World Agent - FastAPI Backend
Knowledge-Based Agent with Resolution Refutation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Set, Dict, Tuple, Literal
from copy import deepcopy
import random
import uvicorn

# ============== Pydantic Models ==============

class GridSize(BaseModel):
    rows: int = Field(default=4, ge=3, le=10)
    cols: int = Field(default=4, ge=3, le=10)

class MoveRequest(BaseModel):
    direction: Literal["up", "down", "left", "right"]

class SafeCheckRequest(BaseModel):
    row: int = Field(ge=0)
    col: int = Field(ge=0)

class Percepts(BaseModel):
    stench: bool = False
    breeze: bool = False
    glitter: bool = False
    bump: bool = False
    scream: bool = False

class GameState(BaseModel):
    grid_size: GridSize
    agent_pos: Tuple[int, int]
    agent_alive: bool
    gold_pos: Optional[Tuple[int, int]]
    visited: List[Tuple[int, int]]
    safe: List[Tuple[int, int]]
    known_pits: List[Tuple[int, int]]
    known_wumpus: List[Tuple[int, int]]
    inference_steps: int
    percepts: Percepts

# ============== Game Logic ==============

class WumpusWorld:
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.pits: Set[Tuple[int, int]] = set()
        self.wumpus: Optional[Tuple[int, int]] = None
        self.gold: Tuple[int, int] = (0, 0)
        self.agent_pos: Tuple[int, int] = (0, 0)
        self.agent_alive = True
        self.wumpus_alive = True
        self.inference_steps = 0
        self.visited: Set[Tuple[int, int]] = {(0, 0)}
        self.safe: Set[Tuple[int, int]] = {(0, 0)}
        self.known_hazards: Dict[str, Set[Tuple[int, int]]] = {"pits": set(), "wumpus": set()}
        self.kb_clauses: List[List[Tuple]] = []

    def setup_game(self) -> None:
        """Randomly place hazards, ensuring start is safe"""
        self.pits.clear()
        self.known_hazards["pits"].clear()
        self.known_hazards["wumpus"].clear()
        self.kb_clauses.clear()

        # Place pits (20% probability)
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) != (0, 0) and random.random() < 0.2:
                    self.pits.add((r, c))

        # Place Wumpus (not at start)
        while True:
            wumpus_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
            if wumpus_pos != (0, 0) and wumpus_pos not in self.pits:
                self.wumpus = wumpus_pos
                break

        # Place Gold (not at start)
        while True:
            gold_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
            if gold_pos != (0, 0) and gold_pos not in self.pits and gold_pos != self.wumpus:
                self.gold = gold_pos
                break

        # Reset agent
        self.agent_pos = (0, 0)
        self.agent_alive = True
        self.wumpus_alive = True
        self.inference_steps = 0
        self.visited = {(0, 0)}
        self.safe = {(0, 0)}

        # Initial knowledge: Start cell is safe (no pit, no wumpus)
        self.kb_clauses.append([("NOT", ("PIT", 0, 0)), ("NOT", ("WUMPUS", 0, 0))])

    def get_adjacent_cells(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all adjacent cells (north, south, east, west)"""
        r, c = pos
        adjacent = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                adjacent.append((nr, nc))
        return adjacent

    def get_percepts(self, pos: Tuple[int, int]) -> Percepts:
        """Calculate percepts at given position"""
        adjacent = self.get_adjacent_cells(pos)

        return Percepts(
            stench=any(self.wumpus == adj and self.wumpus_alive for adj in adjacent),
            breeze=any(adj in self.pits for adj in adjacent),
            glitter=pos == self.gold,
            bump=False,
            scream=False
        )

    def add_percept_to_kb(self, pos: Tuple[int, int], percepts: Percepts) -> None:
        """Add percept information to Knowledge Base"""
        adjacent = self.get_adjacent_cells(pos)

        if percepts.breeze:
            # Breeze => at least one adjacent cell has a pit
            clause = [("PIT", adj[0], adj[1]) for adj in adjacent if adj not in self.safe]
            if clause:
                self.kb_clauses.append(clause)
        else:
            # No breeze => all adjacent cells are pit-free
            for adj in adjacent:
                if adj not in self.safe:
                    self.kb_clauses.append([("NOT", ("PIT", adj[0], adj[1]))])
                    self.safe.add(adj)

        if percepts.stench:
            # Stench => at least one adjacent cell has wumpus
            clause = [("WUMPUS", adj[0], adj[1]) for adj in adjacent if adj not in self.known_hazards["wumpus"]]
            if clause:
                self.kb_clauses.append(clause)
        else:
            # No stench => all adjacent cells are wumpus-free
            for adj in adjacent:
                if adj not in self.known_hazards["wumpus"]:
                    self.kb_clauses.append([("NOT", ("WUMPUS", adj[0], adj[1]))])

        self.inference_steps += 1

    def are_complementary(self, lit1: Tuple, lit2: Tuple) -> bool:
        """Check if two literals are complementary"""
        if lit1[0] == "NOT" and lit2[0] != "NOT":
            return lit1[1] == lit2
        if lit2[0] == "NOT" and lit1[0] != "NOT":
            return lit2[1] == lit1
        return False

    def resolve(self, clause1: List, clause2: List) -> List[List]:
        """Resolve two clauses"""
        resolvents = []
        for lit1 in clause1:
            for lit2 in clause2:
                if self.are_complementary(lit1, lit2):
                    new_clause = [l for l in clause1 if l != lit1]
                    new_clause.extend([l for l in clause2 if l != lit2])
                    # Remove duplicates
                    seen = set()
                    unique_clause = []
                    for lit in new_clause:
                        key = f"{lit[0]}_{lit[1]}_{lit[2]}"
                        if key not in seen:
                            seen.add(key)
                            unique_clause.append(lit)
                    resolvents.append(unique_clause)
        return resolvents

    def resolution_refutation(self, query: Tuple) -> bool:
        """Resolution Refutation Algorithm"""
        self.inference_steps += 1

        negated_query = ("NOT", query) if query[0] != "NOT" else query[1]
        clauses = deepcopy(self.kb_clauses)
        clauses.append([negated_query])

        for iteration in range(1000):
            new_clauses = []
            added = False

            for i, clause1 in enumerate(clauses):
                for clause2 in clauses[i + 1:]:
                    resolvents = self.resolve(clause1, clause2)
                    for resolvent in resolvents:
                        if not resolvent:
                            return True
                        if resolvent not in clauses and resolvent not in new_clauses:
                            new_clauses.append(resolvent)
                            added = True

            if not added:
                break
            clauses.extend(new_clauses)

        return False

    def is_cell_safe(self, pos: Tuple[int, int]) -> bool:
        """Check if a cell is safe using Resolution Refutation"""
        pit_safe = self.resolution_refutation(("PIT", pos[0], pos[1]))
        wumpus_safe = self.resolution_refutation(("WUMPUS", pos[0], pos[1]))

        if pit_safe and wumpus_safe:
            self.safe.add(pos)
            return True

        if pit_safe:
            self.safe.add(pos)

        return False

    def find_safe_unvisited(self) -> Optional[Tuple[int, int]]:
        """Find a safe unvisited adjacent cell"""
        adjacent = self.get_adjacent_cells(self.agent_pos)
        unvisited = [cell for cell in adjacent if cell not in self.visited]

        safe_cells = [cell for cell in unvisited if cell in self.safe]
        unknown_cells = [cell for cell in unvisited if cell not in self.safe]

        for cell in safe_cells:
            if cell not in self.known_hazards["pits"] and cell not in self.known_hazards["wumpus"]:
                return cell

        for cell in unknown_cells:
            if self.is_cell_safe(cell):
                return cell

        return None

    def move_agent(self, direction: str) -> Dict:
        """Move agent in direction"""
        r, c = self.agent_pos

        if direction == "up" and r > 0:
            self.agent_pos = (r - 1, c)
        elif direction == "down" and r < self.rows - 1:
            self.agent_pos = (r + 1, c)
        elif direction == "left" and c > 0:
            self.agent_pos = (r, c - 1)
        elif direction == "right" and c < self.cols - 1:
            self.agent_pos = (r, c + 1)

        self.visited.add(self.agent_pos)
        percepts = self.get_percepts(self.agent_pos)
        self.add_percept_to_kb(self.agent_pos, percepts)

        if self.agent_pos in self.pits:
            self.agent_alive = False
        if self.agent_pos == self.wumpus and self.wumpus_alive:
            self.agent_alive = False

        return {
            "position": list(self.agent_pos),
            "percepts": percepts.model_dump(),
            "alive": self.agent_alive,
            "visited": list(self.visited),
            "safe": list(self.safe),
            "inference_steps": self.inference_steps
        }

    def auto_move(self) -> Dict:
        """Agent autonomously finds and moves to a safe cell"""
        target = self.find_safe_unvisited()

        if target:
            r, c = self.agent_pos
            if target[0] < r:
                return self.move_agent("up")
            elif target[0] > r:
                return self.move_agent("down")
            elif target[1] < c:
                return self.move_agent("left")
            elif target[1] > c:
                return self.move_agent("right")

        return {
            "position": list(self.agent_pos),
            "percepts": self.get_percepts(self.agent_pos).model_dump(),
            "alive": self.agent_alive,
            "visited": list(self.visited),
            "safe": list(self.safe),
            "inference_steps": self.inference_steps,
            "message": "No safe moves available"
        }

    def get_game_state(self) -> GameState:
        """Get current game state for frontend"""
        return GameState(
            grid_size=GridSize(rows=self.rows, cols=self.cols),
            agent_pos=self.agent_pos,
            agent_alive=self.agent_alive,
            gold_pos=self.gold if self.agent_pos == self.gold else None,
            visited=list(self.visited),
            safe=list(self.safe),
            known_pits=list(self.known_hazards["pits"]),
            known_wumpus=list(self.known_hazards["wumpus"]),
            inference_steps=self.inference_steps,
            percepts=self.get_percepts(self.agent_pos)
        )


# ============== FastAPI App ==============

app = FastAPI(
    title="Wumpus World Agent API",
    description="Knowledge-Based Agent with Resolution Refutation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game: Optional[WumpusWorld] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wumpus World Agent API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Wumpus World Agent API"}


@app.post("/api/game/new")
async def new_game(config: GridSize):
    """Create a new game with specified grid size"""
    global game
    game = WumpusWorld(config.rows, config.cols)
    game.setup_game()
    return {"success": True, "state": game.get_game_state()}


@app.get("/api/game/state")
async def get_state():
    """Get current game state"""
    if game is None:
        raise HTTPException(status_code=400, detail="No game in progress")
    return game.get_game_state()


@app.post("/api/game/move")
async def move(request: MoveRequest):
    """Move agent in specified direction"""
    if game is None:
        raise HTTPException(status_code=400, detail="No game in progress")
    return game.move_agent(request.direction)


@app.post("/api/game/auto")
async def auto_move():
    """Agent makes autonomous move"""
    if game is None:
        raise HTTPException(status_code=400, detail="No game in progress")
    return game.auto_move()


@app.post("/api/game/safe")
async def check_safe(request: SafeCheckRequest):
    """Check if a cell is safe using Resolution"""
    if game is None:
        raise HTTPException(status_code=400, detail="No game in progress")
    pos = (request.row, request.col)
    is_safe = game.is_cell_safe(pos)
    return {
        "position": pos,
        "is_safe": is_safe,
        "inference_steps": game.inference_steps
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)