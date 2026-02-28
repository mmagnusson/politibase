"""Base scraper class with common functionality.

All city/county scrapers inherit from BaseScraper, which provides:
  - Rate-limited HTTP requests
  - Logging
  - Session management for the database
"""

import logging
import time
from abc import ABC, abstractmethod

import requests
from sqlalchemy.orm import Session

from politibase.db.database import SessionLocal

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all Politibase scrapers."""

    # Subclasses should set these
    SOURCE_NAME: str = ""
    SOURCE_URL: str = ""
    SOURCE_TYPE: str = "official"

    # Rate limiting: minimum seconds between requests
    REQUEST_DELAY: float = 2.0

    def __init__(self, db: Session | None = None):
        self.db = db or SessionLocal()
        self._owns_db = db is None
        self._last_request_time: float = 0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Politibase/0.1 (civic data research; https://github.com/mmagnusson/politibase)"
            }
        )

    def close(self):
        if self._owns_db:
            self.db.close()
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fetch(self, url: str) -> requests.Response:
        """Fetch a URL with rate limiting and error handling."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)

        logger.info("Fetching %s", url)
        resp = self.session.get(url, timeout=30)
        self._last_request_time = time.time()
        resp.raise_for_status()
        return resp

    @abstractmethod
    def scrape(self):
        """Run the scraper. Subclasses implement this."""

    @abstractmethod
    def get_description(self) -> str:
        """Human-readable description of what this scraper collects."""
