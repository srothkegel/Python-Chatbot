"""
Pydantic AI – Deep Research Agent

Dieses Modul definiert einen autonomen Research-Agenten, der ein Thema in
distinkte Blickwinkel zerlegt, gezielt über DuckDuckGo recherchiert und die
Ergebnisse zu einem strukturierten Markdown-Forschungsbericht synthetisiert.

Workflow:
1. Temporal Anchoring – tagesaktuelles Systemdatum bestimmen.
2. Recherche-Planung – Thema in 3–4 Dimensionen zerlegen (Structured Output).
3. Execution – asynchrone DuckDuckGo-Suche pro Dimension.
4. Synthese & Reporting – strukturierter Markdown-Report mit Quellen.
"""

from __future__ import annotations

import asyncio
import os
import urllib.parse
from collections.abc import AsyncGenerator
from datetime import datetime

from ddgs import DDGS
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from scraper import fetch_and_extract_content

# Laden der Umgebungsvariablen aus der .env-Datei (expliziter Pfad)
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path, override=True)

# Validierung des API-Keys
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    env_file_exists = os.path.exists(env_path)
    raise ValueError(
        f"OPENAI_API_KEY ist nicht gesetzt.\n"
        f"  .env Datei existiert: {env_file_exists}\n"
        f"  .env Pfad: {env_path}\n"
        f"Bitte überprüfen Sie Ihre .env-Datei und stellen Sie sicher, "
        f"dass sie den Eintrag 'OPENAI_API_KEY=ihr_key_hier' enthält.\n"
        f"Siehe .env.example für eine Vorlage."
    )

# Modell konfigurierbar via MODEL_NAME (Standard: gpt-4o-mini)
# Pydantic AI erwartet das Format 'openai:model-name'.
_MODEL_ENV: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
MODEL_NAME: str = _MODEL_ENV if ":" in _MODEL_ENV else f"openai:{_MODEL_ENV}"

# Anzahl der DuckDuckGo-Ergebnisse pro Suchanfrage
MAX_RESULTS_PER_QUERY: int = 5
URLS_PER_QUERY: int = 2


# ---------------------------------------------------------------------------
# Datenstrukturen (Pydantic)
# ---------------------------------------------------------------------------
class SearchQueryItem(BaseModel):
    """Ein einzelner Recherche-Blickwinkel mit zugehörigem Suchbegriff."""

    perspective: str = Field(
        description="Name des Blickwinkels/der Dimension (z. B. 'Fundamentaldaten')."
    )
    search_query: str = Field(
        description="Präziser, eigenständiger DuckDuckGo-Suchbegriff für diese Dimension."
    )


class ResearchPlan(BaseModel):
    """Strukturierter Rechercheplan für ein Thema."""

    current_date: str = Field(
        description="Tagesaktuelles Datum im Format 'YYYY-MM-DD'."
    )
    topic: str = Field(description="Das zu recherchierende Thema.")
    queries: list[SearchQueryItem] = Field(
        description="Liste von 3–4 distinkten Recherche-Blickwinkeln."
    )


class SearchResultItem(BaseModel):
    """Ein einzelnes Suchergebnis aus DuckDuckGo."""

    title: str = Field(description="Titel der Fundstelle.")
    snippet: str = Field(description="Text-Snippet/Zusammenfassung der Fundstelle.")
    url: str = Field(description="Quell-URL der Fundstelle.")


class ReadSource(BaseModel):
    """Eine gelesene Quelle inkl. Volltext oder Fallback-Snippet."""
    
    title: str = Field(description="Titel der Fundstelle.")
    url: str = Field(description="Quell-URL der Fundstelle.")
    snippet: str = Field(description="Text-Snippet aus der Suche.")
    content: str | None = Field(description="Extrahierter Volltext, falls erfolgreich.")
    used_fallback: bool = Field(description="True, wenn der Volltext nicht extrahiert werden konnte.")


# ---------------------------------------------------------------------------
# Agenten (Planung & Synthese)
# ---------------------------------------------------------------------------
_PLANNER_SYSTEM_PROMPT: str = (
    "Du bist ein erfahrener Research-Planer. Deine Aufgabe ist es, ein Thema in "
    "3 bis 4 distinkte, sich nicht überschneidende Blickwinkel (Dimensionen) zu "
    "zerlegen – z. B. Fundamentaldaten, Historie, aktuelle Entwicklungen, Risiken "
    "und Ausblick. Für jede Dimension formulierst du einen präzisen, eigenständigen "
    "Web-Suchstring, der ohne Kontext für die DuckDuckGo-Suche funktioniert. "
    "Nutze das bereitgestellte aktuelle Datum, um Aktualität sicherzustellen: "
    "Baue bei News, Kursen oder Quartalszahlen das aktuelle Jahr in die Suchstrings ein. "
    "Antworte ausschließlich in deutscher Sprache."
)

_REPORT_SYSTEM_PROMPT: str = (
    "Du bist ein Senior Research Analyst. Du erhältst ein Thema, das aktuelle Datum "
    "sowie nummerierte Quellen (Titel, URL, und entweder den Volltext oder ein kurzes Snippet). "
    "Erstelle daraus einen hochwertigen, gut strukturierten Forschungsbericht in deutscher "
    "Sprache im Markdown-Format mit folgenden Abschnitten:\n"
    "1. '## Executive Summary' – prägnante Kernaussagen.\n"
    "2. '## Detailanalyse' – pro Blickwinkel eine Unterüberschrift mit Analyse.\n"
    "3. '## Risiken & offene Fragen'.\n"
    "4. '## Fazit'.\n"
    "5. '## Quellenverzeichnis' – nummerierte Liste aller Quellen mit Titel und URL.\n\n"
    "Arbeite konkrete Zahlen, Daten, Zitate, Vorjahresvergleiche und Fakten aus dem Volltext heraus. "
    "Zitiere jede Kernaussage im Fließtext mit der entsprechenden Quellennummer in eckigen Klammern, "
    "z. B. [1]. Kennzeichne es transparent, falls zu einer Quelle nur ein Fallback-Snippet "
    "vorlag und Informationen deshalb dünn sein könnten. Stütze dich ausschließlich auf die "
    "bereitgestellten Inhalte und erfinde keine Fakten. Wenn Informationen fehlen, benenne dies offen."
)

# Planner-Agent liefert strukturierten Output (ResearchPlan)
planner_agent: Agent[None, ResearchPlan] = Agent(
    model=MODEL_NAME,
    output_type=ResearchPlan,
    system_prompt=_PLANNER_SYSTEM_PROMPT,
)

# Synthese-Agent liefert den finalen Markdown-Report als String
report_agent: Agent[None, str] = Agent(
    model=MODEL_NAME,
    output_type=str,
    system_prompt=_REPORT_SYSTEM_PROMPT,
)


# ---------------------------------------------------------------------------
# DuckDuckGo-Suche (async Wrapper)
# ---------------------------------------------------------------------------
async def duckduckgo_search(
    query: str,
    max_results: int = MAX_RESULTS_PER_QUERY,
) -> list[SearchResultItem]:
    """
    Führt eine DuckDuckGo-Textsuche asynchron aus.

    Die synchrone `ddgs`-Bibliothek wird in einem Thread ausgeführt, um den
    Event-Loop nicht zu blockieren.

    Args:
        query: Der Suchbegriff.
        max_results: Maximale Anzahl an Ergebnissen.

    Returns:
        Liste von SearchResultItem. Bei Fehlern eine leere Liste.
    """

    def _search() -> list[dict[str, str]]:
        # DDGS ist synchron; Kontextmanager schließt die HTTP-Session sauber.
        with DDGS() as ddgs:
            return ddgs.text(query, max_results=max_results)

    try:
        raw_results = await asyncio.to_thread(_search)
    except Exception:
        # Einzelne fehlgeschlagene Suche darf die Gesamtrecherche nicht abbrechen.
        return []

    results: list[SearchResultItem] = []
    for item in raw_results:
        results.append(
            SearchResultItem(
                title=item.get("title", "").strip(),
                snippet=item.get("body", "").strip(),
                url=item.get("href", "").strip(),
            )
        )
    return results


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def _build_report_input(
    plan: ResearchPlan,
    results_per_query: list[list[ReadSource]],
) -> tuple[str, list[ReadSource]]:
    """
    Baut den Eingabetext für den Synthese-Agenten und eine globale Quellenliste.

    Args:
        plan: Der Rechercheplan.
        results_per_query: Gelesene Quellen in derselben Reihenfolge wie plan.queries.

    Returns:
        Tuple aus (formatierter Eingabetext, globale Quellenliste mit Nummerierung).
    """
    lines: list[str] = [
        f"Thema: {plan.topic}",
        f"Aktuelles Datum: {plan.current_date}",
        "",
        "Recherche-Ergebnisse (global nummeriert für Zitate):",
    ]

    sources: list[ReadSource] = []
    global_index = 1

    for query_item, results in zip(plan.queries, results_per_query):
        lines.append("")
        lines.append(
            f"### Blickwinkel: {query_item.perspective} "
            f'(Suchbegriff: "{query_item.search_query}")'
        )
        if not results:
            lines.append("- (Keine Ergebnisse gefunden oder gelesen.)")
            continue
        for result in results:
            lines.append(f"[{global_index}] {result.title}")
            lines.append(f"    URL: {result.url}")
            if result.used_fallback:
                lines.append(f"    Inhalt (FALLBACK SNIPPET): {result.snippet}")
            else:
                lines.append(f"    Inhalt (VOLLTEXT): {result.content}")
            sources.append(result)
            global_index += 1

    return "\n".join(lines), sources


# ---------------------------------------------------------------------------
# Orchestrierung – Deep Research Async Generator
# ---------------------------------------------------------------------------
async def run_deep_research(topic: str) -> AsyncGenerator[str, None]:
    """
    Führt die vollständige Deep-Research-Pipeline aus und streamt den Fortschritt.

    Der Generator liefert fortlaufend eine kumulative Markdown-Statusanzeige.
    Der letzte gelieferte Wert ist der finale Forschungsbericht.

    Args:
        topic: Die Anfrage/das Stichwort des Nutzers.

    Yields:
        str: Kumulative Fortschrittsanzeige bzw. am Ende der finale Report.
    """
    progress: list[str] = []

    def _emit(line: str) -> str:
        """Fügt eine Statuszeile hinzu und gibt die kumulierte Anzeige zurück."""
        progress.append(line)
        return "\n\n".join(progress)

    # --- Phase 1: Temporal Anchoring ---------------------------------------
    today: str = datetime.now().strftime("%Y-%m-%d")
    yield _emit(f"**Phase 1/4 – Temporal Anchoring:** Aktuelles Datum ist `{today}`.")

    # --- Phase 2: Recherche-Planung ----------------------------------------
    yield _emit("**Phase 2/4 – Recherche-Planung:** Zerlege das Thema in Dimensionen …")
    planner_prompt = (
        f"Aktuelles Datum: {today}\n"
        f"Thema/Anfrage des Nutzers: {topic}\n\n"
        "Erstelle einen Rechercheplan mit 3–4 distinkten Blickwinkeln und je einem "
        "präzisen DuckDuckGo-Suchstring. Setze current_date exakt auf das obige Datum."
    )
    try:
        plan_result = await planner_agent.run(planner_prompt)
        plan: ResearchPlan = plan_result.output
    except Exception as exc:
        yield _emit(f"**Fehler bei der Recherche-Planung:** {exc}")
        return

    # Sicherstellen, dass das Datum gesetzt ist (Temporal Anchoring erzwingen)
    if not plan.current_date:
        plan.current_date = today

    plan_lines = [f"- **{q.perspective}** → `{q.search_query}`" for q in plan.queries]
    yield _emit(
        "**Rechercheplan erstellt:**\n" + "\n".join(plan_lines)
    )

    # --- Phase 3: Execution (DuckDuckGo Retrieval & Deep Scraping) -------------------------
    yield _emit(f"**Phase 3/4 – Recherche & Deep Reading:** Starte Suchanfragen und lese Artikel …")

    # 3a: DuckDuckGo-Suche
    for q in plan.queries:
        yield _emit(f"🔍 Suche nach: `{q.search_query}`...")

    search_results_per_query: list[list[SearchResultItem]] = await asyncio.gather(
        *(duckduckgo_search(q.search_query) for q in plan.queries)
    )

    # 3b: Deep Scraping
    tasks = []

    async def _process_url(query_index: int, result: SearchResultItem):
        domain = urllib.parse.urlparse(result.url).netloc
        content = await fetch_and_extract_content(result.url)
        
        if content:
            read_source = ReadSource(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                content=content,
                used_fallback=False
            )
            return query_index, read_source, domain, len(content)
        else:
            read_source = ReadSource(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                content=None,
                used_fallback=True
            )
            return query_index, read_source, domain, 0

    for i, results in enumerate(search_results_per_query):
        # Top 2 URLs je Blickwinkel
        for result in results[:URLS_PER_QUERY]:
            tasks.append(_process_url(i, result))

    total_sources = len(tasks)
    if total_sources == 0:
        yield _emit(
            "**Abbruch:** Es konnten keine Web-Quellen gefunden werden. "
            "Bitte formuliere die Anfrage anders oder versuche es später erneut."
        )
        return

    read_sources_per_query: list[list[ReadSource]] = [[] for _ in plan.queries]

    for completed_task in asyncio.as_completed(tasks):
        query_index, read_source, domain, length = await completed_task
        read_sources_per_query[query_index].append(read_source)
        if read_source.used_fallback:
            yield _emit(f"⚠️ Seite blockiert, nutze Snippet: `{domain}`...")
        else:
            yield _emit(f"📖 Lese Quelle: `{domain}` ({length} Zeichen extrahiert)...")

    yield _emit(f"**Lesen abgeschlossen** – {total_sources} Quellen bearbeitet.")

    # --- Phase 4: Synthese & Reporting -------------------------------------
    yield _emit("📝 Verfasse finalen Deep-Dive-Bericht basierend auf den gelesenen Artikeln...")
    report_input, _sources = _build_report_input(plan, read_sources_per_query)
    try:
        report_result = await report_agent.run(report_input)
        report: str = report_result.output
    except Exception as exc:
        yield _emit(f"**Fehler bei der Synthese:** {exc}")
        return

    # Finaler Report inkl. kleiner Kopfzeile mit Thema und Datum
    final_report = (
        f"# Forschungsbericht: {plan.topic}\n\n"
        f"*Stand: {plan.current_date} · {total_sources} ausgewertete Quellen*\n\n"
        f"{report}"
    )
    yield final_report
