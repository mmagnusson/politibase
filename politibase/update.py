#!/usr/bin/env python3
"""Politibase data update runner.

This is the main tool for keeping Politibase data fresh. It can:
  1. Run all scrapers to check for changes on government websites
  2. Show a freshness report (what's stale, what's current)
  3. Detect upcoming elections and filing deadlines
  4. Run on a schedule via cron

Usage:
    python -m politibase.update check          # Freshness report
    python -m politibase.update scrape         # Run all scrapers
    python -m politibase.update scrape --source moorhead  # Run one scraper
    python -m politibase.update deadlines      # Show upcoming deadlines
    python -m politibase.update crontab        # Print recommended cron schedule

Recommended cron (runs weekly on Sunday at 6am):
    0 6 * * 0 cd /path/to/politibase && python -m politibase.update scrape >> logs/update.log 2>&1
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from politibase.db.database import SessionLocal, init_db
from politibase.models.schema import (
    Candidate,
    Candidacy,
    DataSource,
    Election,
    Jurisdiction,
    Office,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("politibase.update")

# Where we store page snapshots for change detection
SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "data" / "snapshots"


def cmd_check(args):
    """Show data freshness report."""
    db = SessionLocal()

    print("=" * 70)
    print("POLITIBASE DATA FRESHNESS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Data sources and when they were last scraped
    sources = db.query(DataSource).order_by(DataSource.source_name).all()
    print(f"\n{'Source':<45} {'Last Scraped':<20} {'Status'}")
    print("-" * 85)
    for s in sources:
        if s.last_scraped_at:
            age = datetime.utcnow() - s.last_scraped_at
            if age.days > 30:
                status = "STALE (>30 days)"
            elif age.days > 7:
                status = "aging (>7 days)"
            else:
                status = "fresh"
            last = s.last_scraped_at.strftime("%Y-%m-%d %H:%M")
        else:
            status = "NEVER SCRAPED"
            last = "—"
        print(f"  {s.source_name:<43} {last:<20} {status}")

    # Summary stats
    print(f"\n{'Metric':<35} {'Count':>6}")
    print("-" * 45)
    print(f"  {'Jurisdictions':<33} {db.query(Jurisdiction).count():>6}")
    print(f"  {'Offices':<33} {db.query(Office).count():>6}")
    print(f"  {'Elections':<33} {db.query(Election).count():>6}")
    print(f"  {'Candidates':<33} {db.query(Candidate).count():>6}")
    print(f"  {'Candidacies':<33} {db.query(Candidacy).count():>6}")
    print(f"  {'Data Sources':<33} {db.query(DataSource).count():>6}")

    # Candidates with sparse data (missing bio, occupation, etc.)
    sparse = (
        db.query(Candidate)
        .filter(
            (Candidate.bio == None) | (Candidate.bio == ""),  # noqa: E711
            (Candidate.occupation == None) | (Candidate.occupation == ""),  # noqa: E711
        )
        .all()
    )
    if sparse:
        print(f"\n  Candidates needing enrichment: {len(sparse)}")
        for c in sparse[:10]:
            print(f"    - {c.full_name} (id={c.id})")
        if len(sparse) > 10:
            print(f"    ... and {len(sparse) - 10} more")

    db.close()


def cmd_deadlines(args):
    """Show upcoming election filing deadlines and election dates."""
    db = SessionLocal()
    today = date.today()

    print("=" * 70)
    print("UPCOMING ELECTIONS & FILING DEADLINES")
    print(f"As of: {today.isoformat()}")
    print("=" * 70)

    upcoming = (
        db.query(Election)
        .join(Office)
        .join(Jurisdiction)
        .filter(Election.election_date >= today)
        .order_by(Election.election_date)
        .all()
    )

    if not upcoming:
        print("\n  No upcoming elections in the database.")
        print("  TIP: Check county election office websites for newly scheduled elections.")
    else:
        for e in upcoming:
            days_until = (e.election_date - today).days
            print(f"\n  {e.office.jurisdiction.name}")
            print(f"  Office: {e.office.title}")
            print(f"  Election: {e.election_date.isoformat()} ({days_until} days away)")
            if e.filing_deadline:
                fd_days = (e.filing_deadline - today).days
                if fd_days < 0:
                    print(f"  Filing Deadline: {e.filing_deadline.isoformat()} (PASSED)")
                elif fd_days < 14:
                    print(f"  Filing Deadline: {e.filing_deadline.isoformat()} (!! {fd_days} DAYS LEFT !!)")
                else:
                    print(f"  Filing Deadline: {e.filing_deadline.isoformat()} ({fd_days} days)")
            if e.description:
                print(f"  Notes: {e.description}")

            # Show candidates filed so far
            candidacies = (
                db.query(Candidacy)
                .filter(Candidacy.election_id == e.id)
                .join(Candidate)
                .all()
            )
            if candidacies:
                print(f"  Candidates ({len(candidacies)}):")
                for cy in candidacies:
                    print(f"    - {cy.candidate.full_name} [{cy.status}]"
                          f"{' (incumbent)' if cy.is_incumbent else ''}")

    # Also flag elections that might be coming but aren't tracked yet
    print(f"\n{'=' * 70}")
    print("ELECTION CALENDAR REMINDERS")
    print("=" * 70)
    print(f"""
  Minnesota (Clay County / Moorhead):
    - City & school board elections: First Tuesday after first Monday in November (even years)
    - Filing period typically: Late May - Early June (check with Clay County Auditor)
    - Next likely: November 2026

  North Dakota (Cass County / Fargo):
    - City & park district elections: Second Tuesday in June (even years)
    - School board elections: Second Tuesday in June (even years)
    - Filing deadline: Typically early April (check with Cass County Auditor)
    - Next likely: June 2026

  Key contacts:
    - Clay County Auditor (MN elections): (218) 299-5006
    - Cass County Auditor (ND elections): (701) 241-5600
    - MN Secretary of State: sos.mn.gov
    - ND Secretary of State: sos.nd.gov
""")

    db.close()


def cmd_scrape(args):
    """Run scrapers to check for new/changed data."""
    from politibase.scrapers.moorhead import MoorheadCouncilScraper, MoorheadSchoolBoardScraper
    from politibase.scrapers.fargo import FargoCommissionScraper, FargoSchoolBoardScraper

    SCRAPERS = {
        "moorhead_council": MoorheadCouncilScraper,
        "moorhead_school": MoorheadSchoolBoardScraper,
        "fargo_commission": FargoCommissionScraper,
        "fargo_school": FargoSchoolBoardScraper,
    }

    if args.source:
        # Run specific scraper
        matches = {k: v for k, v in SCRAPERS.items() if args.source.lower() in k}
        if not matches:
            print(f"Unknown source '{args.source}'. Available: {', '.join(SCRAPERS.keys())}")
            return
    else:
        matches = SCRAPERS

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    for name, scraper_cls in matches.items():
        print(f"\n{'=' * 50}")
        print(f"Running: {name}")
        print(f"{'=' * 50}")

        try:
            with scraper_cls() as scraper:
                print(f"  Description: {scraper.get_description()}")
                print(f"  Source URL: {scraper.SOURCE_URL}")

                results = scraper.scrape()

                # Save a snapshot for change detection
                snapshot_file = SNAPSHOT_DIR / f"{name}.json"
                new_snapshot = json.dumps(results, default=str, sort_keys=True)
                new_hash = hashlib.sha256(new_snapshot.encode()).hexdigest()[:16]

                if snapshot_file.exists():
                    old_snapshot = snapshot_file.read_text()
                    old_hash = hashlib.sha256(old_snapshot.encode()).hexdigest()[:16]
                    if old_hash == new_hash:
                        print(f"  Result: No changes detected (hash: {new_hash})")
                    else:
                        print(f"  Result: CHANGES DETECTED (old: {old_hash}, new: {new_hash})")
                        print(f"  Review the changes and update seed data if needed.")
                else:
                    print(f"  Result: First scrape (hash: {new_hash})")

                snapshot_file.write_text(new_snapshot)

                if isinstance(results, list):
                    print(f"  Items found: {len(results)}")
                elif isinstance(results, dict):
                    for k, v in results.items():
                        count = len(v) if isinstance(v, (list, dict)) else 1
                        print(f"  {k}: {count} items")

        except Exception as e:
            logger.error("Scraper %s failed: %s", name, e)
            print(f"  ERROR: {e}")

    print(f"\n{'=' * 50}")
    print("Scrape complete. Snapshots saved to data/snapshots/")
    print("If changes were detected, review and update seed data.")


def cmd_crontab(args):
    """Print recommended cron schedule."""
    project_dir = Path(__file__).resolve().parent.parent
    print(f"""# Politibase automated data updates
# Add these to your crontab with: crontab -e

# Run scrapers weekly (Sunday 6am) to detect changes on government websites
0 6 * * 0 cd {project_dir} && python -m politibase.update scrape >> data/logs/scrape.log 2>&1

# Generate freshness report weekly (Monday 7am)
0 7 * * 1 cd {project_dir} && python -m politibase.update check >> data/logs/freshness.log 2>&1

# Check upcoming deadlines monthly (1st of month, 8am)
0 8 1 * * cd {project_dir} && python -m politibase.update deadlines >> data/logs/deadlines.log 2>&1

# Don't forget to create the log directory:
#   mkdir -p {project_dir}/data/logs
""")


def cmd_enrich(args):
    """Find candidates with missing data and suggest enrichment sources."""
    db = SessionLocal()

    print("=" * 70)
    print("CANDIDATE DATA ENRICHMENT OPPORTUNITIES")
    print("=" * 70)

    candidates = (
        db.query(Candidate)
        .order_by(Candidate.last_name, Candidate.first_name)
        .all()
    )

    for c in candidates:
        missing = []
        if not c.bio:
            missing.append("bio")
        if not c.occupation:
            missing.append("occupation")
        if not c.education:
            missing.append("education")
        if not c.website:
            missing.append("website")
        if not c.email:
            missing.append("email")
        if not c.photo_url:
            missing.append("photo")

        if missing:
            print(f"\n  {c.full_name} (id={c.id})")
            print(f"    Missing: {', '.join(missing)}")
            # Suggest search queries
            name_query = f"{c.first_name}+{c.last_name}"
            city = c.residence_city or "Fargo Moorhead"
            print(f"    Search: https://www.google.com/search?q={name_query}+{city.replace(' ', '+')}+candidate")
            print(f"    Ballotpedia: https://ballotpedia.org/{c.first_name}_{c.last_name}")

    # Summary
    total = len(candidates)
    complete = sum(
        1 for c in candidates
        if c.bio and c.occupation
    )
    print(f"\n  {'=' * 50}")
    print(f"  Completeness: {complete}/{total} candidates have bio + occupation")
    print(f"  ({100 * complete // total}% complete)")

    db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Politibase data update runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # check
    subparsers.add_parser("check", help="Show data freshness report")

    # deadlines
    subparsers.add_parser("deadlines", help="Show upcoming election deadlines")

    # scrape
    scrape_parser = subparsers.add_parser("scrape", help="Run scrapers")
    scrape_parser.add_argument(
        "--source", type=str, default=None,
        help="Run a specific scraper (e.g. 'moorhead', 'fargo')",
    )

    # crontab
    subparsers.add_parser("crontab", help="Print recommended cron schedule")

    # enrich
    subparsers.add_parser("enrich", help="Find candidates needing data enrichment")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    init_db()

    commands = {
        "check": cmd_check,
        "deadlines": cmd_deadlines,
        "scrape": cmd_scrape,
        "crontab": cmd_crontab,
        "enrich": cmd_enrich,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
