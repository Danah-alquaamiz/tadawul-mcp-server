import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("tadawul_mcp_server")


async def fetch_report(company_name: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://www.saudiexchange.sa")

        await page.fill("input[type='search']", company_name)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        result = page.locator("a.company-name", has_text=company_name)
        if await result.count() == 0:
            return {"error": f"Company '{company_name}' not found on Tadawul."}

        await result.first.click()
        await page.wait_for_timeout(2000)

        try:
            await page.get_by_text("Reports").click()
            await page.wait_for_timeout(2000)
        except Exception:
            return {"error": "Reports tab not found."}

        links = page.locator("a[href$='.pdf']")
        count = await links.count()

        for i in range(count):
            el = links.nth(i)
            text = (await el.inner_text()).lower()
            if "sustainability" in text or "esg" in text:
                pdf_url = await el.get_attribute("href")
                await browser.close()
                return {"company": company_name, "report_url": pdf_url}

        await browser.close()
        return {"company": company_name, "report_url": None}


# -------------------------------
# THIS is the NEW MCP tool format
# -------------------------------
@mcp.tool()
async def get_tadawul_sustainability_report(company_name: str):
    """
    Fetch sustainability/ESG report url from Tadawul.
    """
    return await fetch_report(company_name)

print("🚀 MCP Server is starting...")
if __name__ == "__main__":
    mcp.run()

