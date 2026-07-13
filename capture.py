from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup


async def capture_image(url: str, selector: str) -> bytes | None:
    if not url:
        return None

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        img_tag = soup.select_one(selector)

        if not img_tag:
            return None

        img_src = img_tag.get("src")
        if not img_src:
            return None

        if img_src.startswith("/"):
            parsed = urlparse(url)
            img_src = f"{parsed.scheme}://{parsed.netloc}{img_src}"
        elif not img_src.startswith(("http://", "https://")):
            img_src = urljoin(url, img_src)

        img_resp = await client.get(img_src)
        img_resp.raise_for_status()
        return img_resp.content
