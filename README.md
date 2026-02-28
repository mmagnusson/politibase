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
| **Clay County** | Board of Commissioners | MN | 5 districts |
| **Cass County** | Board of Commissioners | ND | 5 districts |
| **Moorhead Area Public Schools (ISD 152)** | School Board | MN | 7 at-large seats |
| **Fargo Public Schools** | Board of Education | ND | 9 at-large seats |

**38 candidates** across **40 offices** and **12 elections** are currently tracked.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Seed the database and start the server
python run.py --seed

# Or seed separately, then start
python data/seed/fm_metro_seed.py
python run.py
```

The app will be available at **http://localhost:8000**.

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
│   ├── scrapers/               # Data collection
│   │   ├── base.py             # Base scraper with rate limiting
│   │   ├── moorhead.py         # Moorhead city council & school board
│   │   ├── fargo.py            # Fargo commission & school board
│   │   └── google_civic.py     # Google Civic Information API
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

## Adding the Google Civic API

The ballot lookup can be enhanced with federal/state data from Google:

```bash
export GOOGLE_CIVIC_API_KEY=your_key_here
```

Get a free key at [Google Cloud Console](https://console.cloud.google.com/) (enable "Google Civic Information API").

## History

Politibase started as a hackathon project in 2014, focused on scraping Moorhead city council meeting minutes. The original scraper code is preserved in the `MoorheadMinutes/` directory.

## License

MIT
