import asyncio
import httpx
import trafilatura

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
_TIMEOUT = 6.0

async def fetch_and_extract_content(url: str, max_chars: int = 3500) -> str | None:
    """
    Ruft eine Webseite asynchron ab und extrahiert den Hauptartikeltext.

    Args:
        url: Die URL der abzurufenden Webseite.
        max_chars: Maximale Anzahl an Zeichen für den zurückgegebenen Text (Standard 3500).

    Returns:
        Der extrahierte Text (abgeschnitten auf max_chars) oder None, wenn
        ein Fehler aufgetreten ist (z. B. Timeout, 403, leeres Ergebnis).
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=_TIMEOUT) as client:
            headers = {"User-Agent": _USER_AGENT}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text

        # Trafilatura ist CPU-lastig und synchron -> in einem separaten Thread ausführen
        text = await asyncio.to_thread(
            trafilatura.extract,
            html,
            include_comments=False,
            include_tables=False
        )

        if not text:
            return None

        # Text auf max_chars zuschneiden, um das Kontextfenster nicht zu sprengen
        return text[:max_chars]

    except Exception:
        # Bei jeglichem Fehler (Timeout, Paywall, 403, Netzwerkfehler) None zurückgeben
        return None
