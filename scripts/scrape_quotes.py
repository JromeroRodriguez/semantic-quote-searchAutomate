"""Playwright-based scraper for quotes.toscrape.com.

This is a data preparation process and is never executed during a user search.

Output: data/quotes.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.async_api import async_playwright

from backend.app.utils.text import clean_text

logger = logging.getLogger("scrape_quotes")

BASE_URL = "https://quotes.toscrape.com/"
SOURCE = "quotes.toscrape.com"
QUOTE_SELECTOR = ".quote"
NEXT_SELECTOR = "li.next a"


def is_valid_record(record: dict[str, str]) -> bool:
    """Basic validation: both author and quote must be non-empty."""
    return bool(record.get("author") and record.get("quote"))


def deduplicate(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove records whose normalized quote text was already seen."""
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for record in records:
        key = clean_text(record["quote"]).lower()
        if key in seen:
            logger.debug("dropping duplicate quote: %s", record["quote"][:60])
            continue
        seen.add(key)
        unique.append(record)
    return unique


class QuoteScraper:
    """Crawls the quote site and extracts quotes with authors."""

    def __init__(self, headless: bool = True, channel: str = "chrome") -> None:
        self.headless = headless
        self.channel = channel

    async def scrape(self) -> list[dict[str, str]]:
        """Return a list of ``{author, quote, source}`` records."""
        records: list[dict[str, str]] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel=self.channel, headless=self.headless
            )
            try:
                page = await browser.new_page()
                await page.goto(BASE_URL)

                flag = True
                page_number = 1
                while flag:
                    elements = await page.locator(QUOTE_SELECTOR).all()
                    if not elements:
                        logger.warning("no quotes found on page %s", page_number)
                        break

                    for element in elements:
                        phrase = await element.locator(".text").inner_text()
                        phrase = clean_text(phrase)
                        author = await element.locator(".author").inner_text()
                        author = clean_text(author)
                        records.append(
                            {"author": author, "quote": phrase, "source": SOURCE}
                        )

                    logger.info("extracted %s quotes from page %s", len(elements), page_number)
                    page_number += 1

                    next_button = page.locator(NEXT_SELECTOR)
                    if await next_button.count() == 0:
                        flag = False
                    else:
                        await next_button.click()
            finally:
                await browser.close()
        return records


def export_quotes(
    records: list[dict[str, str]], output_path: Path
) -> list[dict[str, Any]]:
    """Validate, deduplicate and persist records as JSON."""
    valid = [r for r in records if is_valid_record(r)]
    unique = deduplicate(valid)

    quotes = [
        {"id": idx, "author": r["author"], "quote": r["quote"], "source": r.get("source", SOURCE)}
        for idx, r in enumerate(unique, start=1)
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(quotes, fh, ensure_ascii=False, indent=2)

    logger.info(
        "exported %s quotes (raw=%s, valid=%s, duplicates removed=%s)",
        len(quotes),
        len(records),
        len(valid),
        len(valid) - len(unique),
    )
    return quotes


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def _async_main(output_path: Path, headless: bool, channel: str) -> None:
    scraper = QuoteScraper(headless=headless, channel=channel)
    records = await scraper.scrape()
    export_quotes(records, output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape quotes from quotes.toscrape.com")
    parser.add_argument(
        "-o", "--output", default="data/quotes.json", help="Output JSON file path"
    )
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    parser.add_argument("--channel", default="chrome", help="Browser channel (default: chrome)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args(argv)

    setup_logging(args.verbose)
    output_path = Path(args.output).resolve()

    try:
        asyncio.run(_async_main(output_path, headless=not args.headed, channel=args.channel))
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("scraping failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
