"""Scraper for City of Moorhead council meeting minutes and agendas.

Target: https://www.cityofmoorhead.com/government/mayor-city-council/council-meetings
Also: https://moorheadmn.gov/government (newer site)

This scraper collects:
  - Council meeting dates and agendas
  - Attendance records for council members
  - Links to meeting minutes (PDF)
"""

import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

from politibase.models.schema import DataSource, MeetingRecord
from politibase.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class MoorheadCouncilScraper(BaseScraper):
    SOURCE_NAME = "City of Moorhead Council Meetings"
    SOURCE_URL = "https://www.cityofmoorhead.com/government/mayor-city-council/council-meetings"
    SOURCE_TYPE = "official"

    def get_description(self) -> str:
        return "Scrapes Moorhead City Council meeting minutes, agendas, and attendance records."

    def scrape(self):
        """Scrape the council meeting archive page for meeting links and metadata."""
        logger.info("Starting Moorhead council meeting scrape")

        try:
            resp = self.fetch(self.SOURCE_URL)
        except Exception as e:
            logger.error("Failed to fetch Moorhead council page: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        meetings = []

        # Look for meeting links — the Moorhead site typically lists meetings
        # in a table or list format with links to minutes/agendas
        # The exact HTML structure may change; this handles common patterns
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)

            # Match links to minutes PDFs or meeting pages
            if any(
                keyword in text.lower()
                for keyword in ["minutes", "agenda", "meeting"]
            ) or any(
                keyword in href.lower()
                for keyword in ["minutes", "agenda", "sirepub"]
            ):
                meeting_info = {
                    "title": text,
                    "url": href if href.startswith("http") else f"https://www.cityofmoorhead.com{href}",
                }

                # Try to extract date from the link text or surrounding context
                date_match = re.search(
                    r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", text
                )
                if date_match:
                    month, day, year = date_match.groups()
                    if len(year) == 2:
                        year = f"20{year}"
                    try:
                        meeting_info["date"] = datetime(
                            int(year), int(month), int(day)
                        ).date()
                    except ValueError:
                        pass

                meetings.append(meeting_info)
                logger.info("Found meeting: %s", meeting_info.get("title", "unknown"))

        # Record the data source
        ds = DataSource(
            source_name=self.SOURCE_NAME,
            source_url=self.SOURCE_URL,
            source_type=self.SOURCE_TYPE,
            last_scraped_at=datetime.utcnow(),
            notes=f"Found {len(meetings)} meeting links",
        )
        self.db.add(ds)
        self.db.commit()

        logger.info("Moorhead scrape complete: %d meetings found", len(meetings))
        return meetings


class MoorheadSchoolBoardScraper(BaseScraper):
    SOURCE_NAME = "Moorhead Area Public Schools Board"
    SOURCE_URL = "https://www.isd152.org/page/school-board-elections"
    SOURCE_TYPE = "official"

    def get_description(self) -> str:
        return "Scrapes Moorhead school board meeting and election information."

    def scrape(self):
        """Scrape school board election and meeting information."""
        logger.info("Starting Moorhead school board scrape")

        try:
            resp = self.fetch(self.SOURCE_URL)
        except Exception as e:
            logger.error("Failed to fetch Moorhead school board page: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        info = []

        # Extract election information, candidate filing details, etc.
        for section in soup.find_all(["h2", "h3", "p", "li"]):
            text = section.get_text(strip=True)
            if any(
                kw in text.lower()
                for kw in ["election", "candidate", "filing", "term", "seat"]
            ):
                info.append(text)

        ds = DataSource(
            source_name=self.SOURCE_NAME,
            source_url=self.SOURCE_URL,
            source_type=self.SOURCE_TYPE,
            last_scraped_at=datetime.utcnow(),
            notes=f"Extracted {len(info)} relevant sections",
        )
        self.db.add(ds)
        self.db.commit()

        logger.info("Moorhead school board scrape complete: %d items", len(info))
        return info
