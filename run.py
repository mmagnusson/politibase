#!/usr/bin/env python3
"""Run the Politibase development server.

Usage:
    python run.py              # Start the web server on port 8000
    python run.py --seed       # Seed the database, then start the server
    python run.py --seed-only  # Seed the database without starting the server
"""

import argparse
import subprocess
import sys
from pathlib import Path


def seed_database():
    print("Seeding database with FM metro data...")
    seed_script = Path(__file__).parent / "data" / "seed" / "fm_metro_seed.py"
    subprocess.run([sys.executable, str(seed_script)], check=True)


def start_server(host="0.0.0.0", port=8000):
    print(f"\nStarting Politibase at http://localhost:{port}")
    print(f"  API docs: http://localhost:{port}/docs")
    print(f"  Ballot lookup: http://localhost:{port}/")
    print(f"  Candidates: http://localhost:{port}/candidates")
    print()
    import uvicorn
    uvicorn.run("politibase.api.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Politibase development server")
    parser.add_argument("--seed", action="store_true", help="Seed the database before starting")
    parser.add_argument("--seed-only", action="store_true", help="Seed the database and exit")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    args = parser.parse_args()

    if args.seed or args.seed_only:
        seed_database()

    if not args.seed_only:
        start_server(host=args.host, port=args.port)
