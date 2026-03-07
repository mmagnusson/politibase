# Politibase

**Local election candidate research platform for the Fargo-Moorhead metro area.**

The goal of Politibase is to provide an easy-to-use repository of political candidate information for local elections that would otherwise receive little coverage or interest, but which have a disproportionate impact relative to their coverage.

School boards decide what your children learn. City councils decide how your tax dollars are spent. County commissions manage everything from public health to election administration. Yet most voters go to the polls knowing little about the candidates running for these offices.

## Current Coverage

Politibase currently covers the Fargo-Moorhead metro area across two states:

| Jurisdiction | Type | State | Seats Tracked |
|---|---|---|---|
| **City of Moorhead** | City Council | MN | Mayor + 8 ward-based members |
| **City of Fargo** | City Commission | ND | Mayor + 4 at-large commissioners |
| **Clay County** | Commissioners + Officials | MN | 5 districts + elected officials |
| **Cass County** | Commissioners + Officials | ND | 5 districts + elected officials |
| **Moorhead Area Public Schools (ISD 152)** | School Board | MN | 7 at-large seats |
| **Fargo Public Schools** | Board of Education | ND | 9 at-large seats |
| **MN 7th Judicial District** | Judges | MN | District court seats |
| **ND East Central Judicial District** | Judges | ND | District court seats |
| **Clay SWCD** | Soil & Water Conservation | MN | 5 supervisor seats |
| **Cass SCD** | Soil Conservation | ND | 5 supervisor seats |
| **Fargo Park District** | Park Board | ND | 5 commissioners |
| **West Fargo Park District** | Park Board | ND | 5 commissioners |

**72 candidates** across **78 offices** and **23 elections** are currently tracked.

## Quick Start

### Prerequisites

- **Python 3.10+** ([python.org/downloads](https://www.python.org/downloads/))
- **Git** ([git-scm.com](https://git-scm.com/))

### Windows 11

1. **Install Python** from [python.org](https://www.python.org/downloads/). During install, check **"Add Python to PATH"**.

2. **Clone and set up** — open PowerShell or Command Prompt:

```powershell
git clone https://github.com/mmagnusson/politibase.git
cd politibase

# Create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database and start the server
python run.py --seed
```

3. Open **http://localhost:8000** in your browser.

To run again later:

```powershell
cd politibase
venv\Scripts\activate
python run.py
```

### Linux / macOS

```bash
git clone https://github.com/mmagnusson/politibase.git
cd politibase

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database and start the server
python run.py --seed
```

The app will be available at **http://localhost:8000**.

To run again later:

```bash
cd politibase
source venv/bin/activate
python run.py
```

### Data Update Tools

Check data freshness, run scrapers, and monitor for changes:

```bash
# Check data freshness and completeness
python -m politibase.update check

# Show upcoming election deadlines
python -m politibase.update deadlines

# Run all scrapers (with change detection)
python -m politibase.update scrape

# Find candidates with missing data
python -m politibase.update enrich

# Show recommended cron schedule (Linux)
python -m politibase.update crontab
```

### Optional: Google Civic API

Enhance ballot lookup with federal/state data:

```bash
# Linux/macOS
export GOOGLE_CIVIC_API_KEY=your_key_here

# Windows (PowerShell)
$env:GOOGLE_CIVIC_API_KEY="your_key_here"

# Windows (Command Prompt)
set GOOGLE_CIVIC_API_KEY=your_key_here
```

Get a free key at [Google Cloud Console](https://console.cloud.google.com/) (enable "Google Civic Information API").

### Production Deployment (Linux)

For a Linux host, a simple systemd service works well:

```bash
# /etc/systemd/system/politibase.service
[Unit]
Description=Politibase
After=network.target

[Service]
User=politibase
WorkingDirectory=/opt/politibase
ExecStart=/opt/politibase/venv/bin/uvicorn politibase.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Set up
sudo useradd -r -s /bin/false politibase
sudo cp -r . /opt/politibase
cd /opt/politibase
sudo -u politibase python3 -m venv venv
sudo -u politibase venv/bin/pip install -r requirements.txt
sudo -u politibase venv/bin/python data/seed/fm_metro_seed.py

# Enable and start
sudo systemctl enable politibase
sudo systemctl start politibase
```

Add a cron job for automated monitoring:

```bash
# /etc/cron.d/politibase
0 6 * * * politibase cd /opt/politibase && venv/bin/python -m politibase.update check >> /var/log/politibase-check.log 2>&1
0 7 * * 1 politibase cd /opt/politibase && venv/bin/python -m politibase.scrapers.monitor >> /var/log/politibase-monitor.log 2>&1
```

Put a reverse proxy (nginx/Caddy) in front for HTTPS in production.

## Features

- **Ballot Lookup** — Enter your address to see all local offices and current officeholders
- **Candidate Profiles** — Bios, education, occupation, election history, positions, endorsements
- **Election Calendar** — Upcoming elections with filing deadlines
- **Jurisdiction Browser** — Browse all tracked cities, counties, and school districts
- **REST API** — Full JSON API at `/api/` with interactive docs at `/docs`
- **Side-by-Side Comparison** — Compare candidates via the API (`/api/candidates/compare?ids=1&ids=2`)

## Architecture

```
politibase/
├── politibase/                 # Python package
│   ├── models/schema.py        # SQLAlchemy data models
│   ├── db/database.py          # Database engine & session management
│   ├── update.py               # CLI: check, scrape, deadlines, enrich, crontab
│   ├── scrapers/               # Data collection
│   │   ├── base.py             # Base scraper with rate limiting
│   │   ├── moorhead.py         # Moorhead city council & school board
│   │   ├── fargo.py            # Fargo commission & school board
│   │   ├── google_civic.py     # Google Civic Information API
│   │   └── monitor.py          # Page change detector (12 gov websites)
│   └── api/                    # FastAPI application
│       ├── main.py             # App entry point
│       ├── pages.py            # Server-rendered HTML pages
│       └── routes/             # JSON API endpoints
├── frontend/                   # Jinja2 templates + CSS/JS
│   ├── templates/              # HTML templates
│   └── static/                 # CSS, JS
├── data/
│   ├── politibase.db           # SQLite database (created on first run)
│   └── seed/fm_metro_seed.py   # Seed data for FM metro area
├── MoorheadMinutes/            # Original hackathon scraper (2014)
├── run.py                      # Development server
└── requirements.txt
```

## Data Model

- **Jurisdiction** — A city, county, school district, or state
- **Office** — A seat that can be held (e.g., "Mayor", "Council Member Ward 1")
- **Election** — A specific election event for an office
- **Candidate** — A person who runs for office
- **Candidacy** — Links a candidate to an election (filed / active / winner / loser)
- **Position** — A candidate's stated stance on an issue
- **Endorsement** — An organization or person endorsing a candidate
- **FinanceRecord** — Campaign contributions and expenditures
- **MeetingRecord** — Incumbent attendance and votes at public meetings

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/jurisdictions/` | List jurisdictions (filter by `type`, `state`) |
| `GET /api/jurisdictions/{id}` | Jurisdiction detail with offices |
| `GET /api/candidates/` | List candidates (filter by `jurisdiction_id`, `office_level`, `search`) |
| `GET /api/candidates/{id}` | Full candidate profile |
| `GET /api/candidates/compare?ids=1&ids=2` | Side-by-side comparison |
| `GET /api/elections/` | List elections (filter by `jurisdiction_id`, `upcoming=true`) |
| `GET /api/elections/{id}` | Election detail with candidates |
| `GET /api/ballot/lookup?address=...` | Address-based ballot lookup |

## Data Sources

All data comes from publicly available sources:

- Official city, county, and school district websites
- County election offices (Clay County MN, Cass County ND)
- Minnesota Secretary of State / North Dakota Secretary of State
- Google Civic Information API (optional, requires API key)
- Ballotpedia
- Local news (InForum, WDAY, Valley News Live)

## History

Politibase started as a hackathon project in 2014, focused on scraping Moorhead city council meeting minutes. The original scraper code is preserved in the `MoorheadMinutes/` directory.

## License

MIT
