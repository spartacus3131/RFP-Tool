"""
Scraper for bidsandtenders.ca RFP listing pages.

Extracts key fields from the public listing page without requiring login
or document download.
"""
import re
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
import httpx
from bs4 import BeautifulSoup


@dataclass
class QuickScanResult:
    """Result of a quick scan from a listing URL."""
    # Source
    url: str
    scraped_at: datetime

    # Core fields
    rfp_number: Optional[str] = None
    client_name: Optional[str] = None
    opportunity_title: Optional[str] = None

    # Dates
    published_date: Optional[str] = None
    question_deadline: Optional[str] = None
    submission_deadline: Optional[str] = None
    contract_duration: Optional[str] = None

    # Details
    scope_summary: Optional[str] = None
    category: Optional[str] = None
    eligibility_notes: Optional[str] = None
    trade_agreements: Optional[str] = None

    # Recommendation
    recommendation: Optional[str] = None  # GO, MAYBE, NO_GO
    recommendation_reasons: Optional[list[str]] = None

    # Errors
    error: Optional[str] = None


class BidsAndTendersScraper:
    """Scraper for bidsandtenders.ca listing pages."""

    SUPPORTED_DOMAINS = [
        "bidsandtenders.ca",
        "durham.bidsandtenders.ca",
        "york.bidsandtenders.ca",
        "peel.bidsandtenders.ca",
        "toronto.bidsandtenders.ca",
        "ottawa.bidsandtenders.ca",
        "hamilton.bidsandtenders.ca",
    ]

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

    async def close(self):
        await self.client.aclose()

    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from a supported bidsandtenders domain."""
        return any(domain in url.lower() for domain in self.SUPPORTED_DOMAINS)

    async def scrape(self, url: str) -> QuickScanResult:
        """Scrape an RFP listing page and extract key fields."""
        result = QuickScanResult(url=url, scraped_at=datetime.utcnow())

        if not self.is_supported_url(url):
            result.error = f"Unsupported URL. Supported domains: {', '.join(self.SUPPORTED_DOMAINS)}"
            return result

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            html = response.text
        except httpx.HTTPError as e:
            result.error = f"Failed to fetch URL: {str(e)}"
            return result

        try:
            soup = BeautifulSoup(html, "lxml")
            self._extract_fields(soup, result)
            self._generate_recommendation(result)
        except Exception as e:
            result.error = f"Failed to parse page: {str(e)}"

        return result

    def _extract_fields(self, soup: BeautifulSoup, result: QuickScanResult):
        """Extract fields from the parsed HTML."""
        # Title - usually in h1 or specific class
        title_elem = soup.find("h1") or soup.find(class_=re.compile(r"tender-title|bid-title", re.I))
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # Often format is "RFP-XXXX-YYYY: Title"
            match = re.match(r"^([A-Z]{2,5}-\d{3,5}-\d{4}):\s*(.+)$", title_text)
            if match:
                result.rfp_number = match.group(1)
                result.opportunity_title = match.group(2)
            else:
                result.opportunity_title = title_text

        # Look for definition list or table with details
        # Common patterns on bidsandtenders.ca
        self._extract_from_detail_rows(soup, result)
        self._extract_from_definition_lists(soup, result)
        self._extract_from_tables(soup, result)

        # Client name - often in breadcrumb or header
        self._extract_client_name(soup, result)

        # Scope/description - look for description section
        self._extract_description(soup, result)

    def _extract_from_detail_rows(self, soup: BeautifulSoup, result: QuickScanResult):
        """Extract from div-based detail rows."""
        # Look for common patterns like "label: value" in divs
        for div in soup.find_all("div", class_=re.compile(r"detail|info|field", re.I)):
            text = div.get_text(strip=True)
            self._parse_field_text(text, result)

    def _extract_from_definition_lists(self, soup: BeautifulSoup, result: QuickScanResult):
        """Extract from <dl> definition lists."""
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                label = dt.get_text(strip=True).lower()
                value = dd.get_text(strip=True)
                self._map_field(label, value, result)

    def _extract_from_tables(self, soup: BeautifulSoup, result: QuickScanResult):
        """Extract from tables with label/value rows."""
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    self._map_field(label, value, result)

    def _extract_client_name(self, soup: BeautifulSoup, result: QuickScanResult):
        """Extract client/organization name."""
        if result.client_name:
            return

        # Try breadcrumbs
        breadcrumb = soup.find(class_=re.compile(r"breadcrumb", re.I))
        if breadcrumb:
            links = breadcrumb.find_all("a")
            for link in links:
                text = link.get_text(strip=True)
                if any(kw in text.lower() for kw in ["region", "city", "county", "township", "municipality"]):
                    result.client_name = text
                    return

        # Try page header/logo area
        header = soup.find("header") or soup.find(class_=re.compile(r"header|banner", re.I))
        if header:
            # Look for organization name in header
            for elem in header.find_all(["h1", "h2", "span", "a"]):
                text = elem.get_text(strip=True)
                if any(kw in text.lower() for kw in ["region", "city", "county"]):
                    result.client_name = text
                    return

    def _extract_description(self, soup: BeautifulSoup, result: QuickScanResult):
        """Extract scope/description text."""
        if result.scope_summary:
            return

        # Look for description section
        desc_section = soup.find(class_=re.compile(r"description|summary|scope|overview", re.I))
        if desc_section:
            result.scope_summary = desc_section.get_text(strip=True)[:1000]
            return

        # Look for paragraphs after title
        main_content = soup.find("main") or soup.find(class_=re.compile(r"content|main", re.I))
        if main_content:
            paragraphs = main_content.find_all("p")
            for p in paragraphs[:3]:
                text = p.get_text(strip=True)
                if len(text) > 50 and not any(kw in text.lower() for kw in ["cookie", "privacy", "login"]):
                    result.scope_summary = text[:1000]
                    return

    def _parse_field_text(self, text: str, result: QuickScanResult):
        """Parse a text string that might contain label: value."""
        # Common patterns
        patterns = [
            (r"bid\s*(?:number|#|no\.?)[\s:]+([A-Z0-9-]+)", "rfp_number"),
            (r"closing\s*(?:date)?[\s:]+(.+?)(?:\s*$|\s+\w+:)", "submission_deadline"),
            (r"published[\s:]+(.+?)(?:\s*$|\s+\w+:)", "published_date"),
            (r"category[\s:]+(.+?)(?:\s*$|\s+\w+:)", "category"),
            (r"duration[\s:]+(.+?)(?:\s*$|\s+\w+:)", "contract_duration"),
        ]
        for pattern, field in patterns:
            match = re.search(pattern, text, re.I)
            if match and not getattr(result, field):
                setattr(result, field, match.group(1).strip())

    def _map_field(self, label: str, value: str, result: QuickScanResult):
        """Map a label/value pair to result fields."""
        label = label.lower().strip()
        value = value.strip()

        if not value:
            return

        field_mapping = {
            # RFP number
            ("bid number", "tender number", "rfp number", "rfp #", "bid #"): "rfp_number",
            # Dates
            ("closing date", "close date", "submission deadline", "due date"): "submission_deadline",
            ("question deadline", "questions due", "inquiry deadline"): "question_deadline",
            ("published", "posted", "issue date", "release date"): "published_date",
            # Details
            ("category", "type", "classification"): "category",
            ("duration", "contract duration", "term"): "contract_duration",
            ("trade agreement", "trade agreements"): "trade_agreements",
            # Status/eligibility
            ("status",): "status",
            ("eligibility", "restrictions", "requirements"): "eligibility_notes",
        }

        for labels, field in field_mapping.items():
            if any(l in label for l in labels):
                if not getattr(result, field, None):
                    setattr(result, field, value)
                return

    def _generate_recommendation(self, result: QuickScanResult):
        """Generate GO/MAYBE/NO_GO recommendation based on available data."""
        reasons = []

        # Check for red flags
        if result.eligibility_notes:
            notes_lower = result.eligibility_notes.lower()
            if "not awarding" in notes_lower and "u.s." in notes_lower:
                reasons.append("Canadian companies prioritized")
            if "prequalified" in notes_lower:
                reasons.append("May require prequalification")
                result.recommendation = "MAYBE"

        # Check category fit (would need firm profile to be meaningful)
        if result.category:
            cat_lower = result.category.lower()
            if any(kw in cat_lower for kw in ["engineering", "consulting", "professional services", "design"]):
                reasons.append("Category matches consulting services")

        # Check timeline
        if result.submission_deadline:
            reasons.append(f"Deadline: {result.submission_deadline}")

        # Default recommendation
        if not result.recommendation:
            if result.error:
                result.recommendation = "UNKNOWN"
            elif result.opportunity_title or result.scope_summary:
                result.recommendation = "MAYBE"
                reasons.append("Quick scan complete - review details to confirm fit")
            else:
                result.recommendation = "MAYBE"
                reasons.append("Limited information extracted - manual review recommended")

        result.recommendation_reasons = reasons


# Singleton instance
scraper = BidsAndTendersScraper()
