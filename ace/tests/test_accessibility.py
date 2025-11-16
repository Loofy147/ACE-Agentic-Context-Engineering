import asyncio
from playwright.async_api import async_playwright
from axe_playwright_python.async_playwright import Axe
import pytest
import json

class JsonDict(dict):
    def __str__(self):
        return json.dumps(self)


@pytest.mark.asyncio
async def test_homepage_accessibility():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://127.0.0.1:8000")

        axe = Axe()
        results = await axe.run(
            page,
            options=JsonDict(
                {
                    "rules": {
                        "document-title": {"enabled": False},
                        "html-has-lang": {"enabled": False},
                    }
                }
            ),
        )

        violations = results.response.get("violations", [])
        serious_violations = [v for v in violations if v["impact"] == "serious"]

        assert not serious_violations, f"Serious accessibility violations found: {json.dumps(serious_violations, indent=2)}"

        await browser.close()
