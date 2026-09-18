# AGENTS.md – Deep Research Agent (Pydantic AI + DuckDuckGo + Gradio)

Dieses Dokument enthält Anweisungen für KI-Agenten, die an diesem Projekt arbeiten.

---

## Projektübersicht

Autonomer **Deep Research Agent** auf Basis von **Pydantic AI** (Backend),
**DuckDuckGo** (Websuche via `ddgs`) und **Gradio** (UI).
Der Agent zerlegt ein Thema in 3–4 Dimensionen, recherchiert gezielt im Web,
synthetisiert die Ergebnisse und liefert einen strukturierten Markdown-Bericht
mit Quellenangaben.
Modell: OpenAI (Standard `gpt-4o-mini`, konfigurierbar via `MODEL_NAME`).
UI läuft lokal unter `http://localhost:7860`.

### Workflow (4 Phasen)

1. **Temporal Anchoring** – tagesaktuelles Systemdatum bestimmen.
2. **Recherche-Planung** – `planner_agent` erzeugt `ResearchPlan` (Structured Output).
3. **Execution & Deep Reading** – asynchrone DuckDuckGo-Suche pro Dimension (`duckduckgo_search`) und anschließendes Scraping der Artikel mit `scraper.fetch_and_extract_content` (Top 2 URLs je Blickwinkel).
4. **Synthese & Reporting** – `report_agent` erstellt den Markdown-Report aus dem gelesenen Volltext; Live-Fortschritt im Chat.

### Dateistruktur

```
Python-Chatbot/
├── agent.py          # Pydantic AI – Datenmodelle, Agenten, DuckDuckGo, run_deep_research
├── app.py            # Gradio ChatInterface – UI & Streaming-Handler
├── scraper.py        # Web-Scraper – Asynchrones Abrufen und Extrahieren (httpx, trafilatura)
├── requirements.txt  # Python-Abhängigkeiten
├── .env              # API-Keys (NICHT in Git commiten!)
├── .env.example      # Vorlage für .env
└── AGENTS.md         # Diese Datei
```

---

## Sprache & Python-Version

- **Python**: 3.14.7 (immer diese Version verwenden)
- **Sprache im Code**: Kommentare und Docstrings auf **Deutsch**
- **Variablen/Funktionsnamen**: Englisch (PEP 8)

---

## Befehle

```bash
# Virtuelle Umgebung erstellen & aktivieren (einmalig)
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# App starten
python app.py

# Abhängigkeiten aktualisieren (nach Änderung an requirements.txt)
pip install -r requirements.txt
```

> **Voraussetzung**: `.env`-Datei mit gültigem `OPENAI_API_KEY` muss existieren.  
> Vorlage: `.env.example` → kopieren zu `.env` und Key eintragen.

---

## Architektur & Konventionen

### `agent.py` – Backend

- **Datenstrukturen (Pydantic):** `SearchQueryItem`, `ResearchPlan`, `SearchResultItem`, `ReadSource`
- **Agenten:** `planner_agent` (`output_type=ResearchPlan`), `report_agent` (`output_type=str`)
- **Suche:** `duckduckgo_search()` – async Wrapper um `ddgs` (`DDGS().text`, via `asyncio.to_thread`)
- **Scraping:** `scraper.py` via `httpx` und `trafilatura` (Deep Reading).
- **Orchestrierung:** `run_deep_research(topic)` – Async-Generator, der die 4 Phasen
  ausführt und kumulative Fortschritts-Strings liefert; letzter Yield = finaler Report
- Modell konfigurierbar via `MODEL_NAME` (Standard `gpt-4o-mini`)
- Vollständig **async** implementieren

```python
# Neuen Blickwinkel/Agent-Baustein ergänzen – Muster (Structured Output):
class MeinModell(BaseModel):
    feld: str = Field(description="Kurze Beschreibung (Deutsch)")
```

### `app.py` – Frontend

- Nutzt `gr.ChatInterface` mit **Streaming** – UI-Änderungen nur hier
- `async_chat_handler` ist ein **Async-Generator**, der `run_deep_research(message)`
  konsumiert und den Fortschritt live yielded
- Port 7860 ist Standard; nur ändern wenn explizit gewünscht

### Wichtige Konventionen

- **Keine hardcodierten API-Keys** – immer `python-dotenv` + `.env`
- **Typ-Annotationen** für alle Funktionsparameter und Rückgabewerte
- **Kein `print()` in Produktionscode** – nur für Fehler/Startup-Logging

---

## Sicherheitsgrenzen

- `.env` **niemals committen** (steht in `.gitignore`)
- Keine `share=True` in `interface.launch()` ohne explizite Aufforderung
- API-Keys niemals in Logs ausgeben oder in Fehlermeldungen anzeigen

---

## Definition of Done

Eine Änderung gilt als fertig, wenn:

- [ ] `python app.py` startet ohne Fehler
- [ ] Der Chat im Browser unter `http://localhost:7860` funktioniert
- [ ] Die Recherche-Pipeline (Planung → DuckDuckGo → Synthese) funktioniert
- [ ] Live-Fortschritt wird im Chat gestreamt, finaler Report enthält Quellen
- [ ] Neue Funktionen haben Typ-Annotationen und deutsche Docstrings
- [ ] `.env` enthält keine Commits / kein API-Key im Code

---

## Generierte & gesperrte Dateien

- `.env` – nicht anfassen, nicht committen
- `venv/` – wird lokal generiert, nicht bearbeiten
- `__pycache__/` – automatisch generiert, ignorieren
