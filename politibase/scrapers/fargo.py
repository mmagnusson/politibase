"""Scraper for City of Fargo commission meetings and data.

Target: https://fargond.gov/city-government/departments/city-commission
Also: https://fargond.gov/city-government/departments/city-commission/agendas-minutes

This scraper collects:
  - Commission meeting dates and agendas
  - Meeting minutes and wrap-up summaries
  - Commissioner information
"""

import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

from politibase.models.schema import DataSource
from politibase.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class FargoCommissionScraper(BaseScraper):
    SOURCE_NAME = "City of Fargo Commission Meetings"
    SOURCE_URL = "https://fargond.gov/city-government/departments/city-commission/agendas-minutes"
    SOURCE_TYPE = "official"

    MEMBERS_URL = "https://fargond.gov/city-government/departments/city-commission/members"
    MINUTES_BASE = "https://fargond.gov/city-government/departments/city-commission/agendas-minutes"

    def get_description(self) -> str:
        return "Scrapes Fargo City Commission meeting minutes, agendas, and commissioner information."

    def scrape(self):
        """Scrape commission meeting information."""
        logger.info("Starting Fargo commission scrape")
        results = {
            "members": self._scrape_members(),
            "meetings": self._scrape_meetings(),
        }
        return results

    def _scrape_members(self):
        """Scrape current commissioner information."""
        try:
            resp = self.fetch(self.MEMBERS_URL)
        except Exception as e:
            logger.error("Failed to fetch Fargo members page: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        members = []

        # Fargo's site typically uses cards or sections for each commissioner
        for heading in soup.find_all(["h2", "h3", "h4"]):
            name = heading.get_text(strip=True)
            if any(
                title in name.lower()
                for title in ["mayor", "commissioner", "deputy"]
            ):
                member_info = {"name": name}
                # Get the following paragraph(s) for bio details
                sibling = heading.find_next_sibling()
                if sibling:
                    member_info["details"] = sibling.get_text(strip=True)
                members.append(member_info)

        logger.info("Found %d Fargo commission members", len(members))
        return members

    def _scrape_meetings(self):
        """Scrape meeting minutes archive."""
        try:
            resp = self.fetch(self.MINUTES_BASE)
        except Exception as e:
            logger.error("Failed to fetch Fargo meetings page: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        meetings = []

        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            href = link["href"]

            if "minutes" in text.lower() or "minutes" in href.lower():
                meeting = {
                    "title": text,
                    "url": href if href.startswith("http") else f"https://fargond.gov{href}",
                }

                # Try to extract date
                date_match = re.search(
                    r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})",
                    text.lower(),
                )
                if date_match:
                    try:
                        meeting["date"] = datetime.strptime(
                            f"{date_match.group(1)} {date_match.group(2)} {date_match.group(3)}",
                            "%B %d %Y",
                        ).date()
                    except ValueError:
                        pass

                meetings.append(meeting)

        ds = DataSource(
            source_name=self.SOURCE_NAME,
            source_url=self.SOURCE_URL,
            source_type=self.SOURCE_TYPE,
            last_scraped_at=datetime.utcnow(),
            notes=f"Found {len(meetings)} meeting links",
        )
        self.db.add(ds)
        self.db.commit()

        logger.info("Fargo scrape complete: %d meetings found", len(meetings))
        return meetings


class FargoSchoolBoardScraper(BaseScraper):
    SOURCE_NAME = "Fargo Public Schools Board of Education"
    SOURCE_URL = "https://www.fargo.k12.nd.us/boardmembers"
    SOURCE_TYPE = "official"

    ELECTION_URL = "https://www.fargo.k12.nd.us/boardelection"

    def get_description(self) -> str:
        return "Scrapes Fargo school board member information and upcoming election details."

    def scrape(self):
        """Scrape school board member and election info."""
        logger.info("Starting Fargo school board scrape")
        results = {
            "members": self._scrape_members(),
            "election_info": self._scrape_election(),
        }
        return results

    def _scrape_members(self):
        """Scrape current board member details."""
        try:
            resp = self.fetch(self.SOURCE_URL)
        except Exception as e:
            logger.error("Failed to fetch Fargo school board page: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        members = []

        for heading in soup.find_all(["h2", "h3", "h4"]):
            name = heading.get_text(strip=True)
            if name and len(name) > 2 and not any(
                skip in name.lower()
                for skip in ["menu", "search", "navigation", "home", "contact"]
            ):
                member = {"name": name}
                sibling = heading.find_next_sibling()
                if sibling:
                    member["details"] = sibling.get_text(strip=True)
                members.append(member)

        logger.info("Found %d Fargo school board members", len(members))
        return members

    def _scrape_election(self):
        """Scrape upcoming election details."""
        try:
            resp = self.fetch(self.ELECTION_URL)
        except Exception as e:
            logger.error("Failed to fetch Fargo election page: %s", e)
            return {}

        soup = BeautifulSoup(resp.text, "lxml")
        info = []

        for element in soup.find_all(["p", "li", "h2", "h3"]):
            text = element.get_text(strip=True)
            if any(
                kw in text.lower()
                for kw in ["election", "filing", "deadline", "candidate", "seat", "june"]
            ):
                info.append(text)

        ds = DataSource(
            source_name=self.SOURCE_NAME,
            source_url=self.ELECTION_URL,
            source_type=self.SOURCE_TYPE,
            last_scraped_at=datetime.utcnow(),
            notes=f"Extracted {len(info)} election-related items",
        )
        self.db.add(ds)
        self.db.commit()

        return {"items": info}
