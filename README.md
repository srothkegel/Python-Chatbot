# Deep Research Agent mit Pydantic AI und Gradio

Eine moderne Chatbot-Applikation, die Pydantic AI für die Backend-Logik und Gradio für die Benutzeroberfläche verwendet. Der Agent führt eine strukturierte Web-Recherche durch und wertet Artikel via "Deep Reading" aus.

## Features

- 🤖 **Deep Research**: Zerlegt komplexe Themen in unterschiedliche Blickwinkel.
- 🔍 **Web-Suche**: Nutzt DuckDuckGo zur gezielten Suche von Informationsquellen.
- 📖 **Deep Reading**: Ruft gefundene Webseiten auf und extrahiert den Hauptartikeltext asynchron mittels `httpx` und `trafilatura`.
- ⚡ **Asynchron**: Vollständig asynchrone Pipeline (Recherche, Scraping und Streaming).
- 🎨 **Moderne UI**: Nutzt Gradio's `ChatInterface` für eine intuitive Chat-Erfahrung mit Live-Statusupdates.
- 🔒 **Sicher**: API-Keys werden über `.env` Dateien verwaltet.

## Voraussetzungen

- Python 3.14.7 (oder kompatible Version)
- OpenAI API Key ([Hier erhalten](https://platform.openai.com/api-keys))

## Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Virtuelle Umgebung erstellen (empfohlen)**:
```bash
python -m venv venv
```

3. **Virtuelle Umgebung aktivieren**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Abhängigkeiten installieren**:
```bash
pip install -r requirements.txt
```

5. **Umgebungsvariablen konfigurieren**:
   - Kopiere `.env.example` zu `.env`:
     ```bash
     copy .env.example .env  # Windows
     cp .env.example .env     # Linux/Mac
     ```
   - Öffne `.env` und füge deinen OpenAI API Key ein:
     ```
     OPENAI_API_KEY=dein_api_key_hier
     ```

## Verwendung

### Anwendung starten

```bash
python app.py
```

Die Anwendung startet lokal und ist unter `http://localhost:7860` erreichbar.

### Im Browser öffnen

Nach dem Start öffnet sich automatisch ein Browser-Fenster. Falls nicht, navigiere zu:
```
http://localhost:7860
```

### Chat verwenden

1. Gib deine Frage oder Nachricht in das Eingabefeld ein
2. Drücke Enter oder klicke auf "Send"
3. Der Bot antwortet asynchron und nutzt bei Bedarf Tools (z.B. für die aktuelle Uhrzeit)

### Beispiel-Interaktionen

- "Nvidia-Aktie"
- "Quantencomputing Durchbruch 2026"
- "Auswirkungen von KI auf den Arbeitsmarkt"

## Projektstruktur

```
Python-Chatbot/
├── requirements.txt     # Python-Abhängigkeiten
├── .env.example         # Vorlage für Umgebungsvariablen
├── .env                 # Deine Umgebungsvariablen (nicht in Git)
├── agent.py             # Pydantic AI Agent Definition, DuckDuckGo-Suche & Orchestrierung
├── app.py               # Gradio Benutzeroberfläche
├── scraper.py           # Web-Scraper für Deep Reading
└── README.md            # Diese Datei
```

## Technische Details

### Architektur

- **Backend (`agent.py` & `scraper.py`)**: 
  - Definiert den Pydantic AI Planner- und Synthese-Agenten.
  - Führt eine asynchrone Suche (via DuckDuckGo) und ein asynchrones Scraping der Resultate (Deep Reading) aus.
  - Generiert einen fundierten Bericht auf Basis echter Webseiten-Inhalte.

- **Frontend (`app.py`)**:
  - Gradio ChatInterface für die UI.
  - Async-Handler konsumiert den Generator aus `run_deep_research` und streamt Live-Status sowie den finalen Report.


## Fehlerbehebung

### "OPENAI_API_KEY ist nicht gesetzt"

- Stelle sicher, dass eine `.env` Datei im Projektverzeichnis existiert
- Überprüfe, dass der Key korrekt eingetragen ist (ohne Anführungszeichen)
- Starte die Anwendung neu

### "Agent konnte nicht erstellt werden"

- Überprüfe deinen OpenAI API Key
- Stelle sicher, dass du genügend Credits auf deinem OpenAI Account hast
- Prüfe deine Internetverbindung

### Port bereits belegt

Falls Port 7860 bereits verwendet wird, kannst du in `app.py` den Port ändern:
```python
interface.launch(server_port=7861)  # Anderen Port verwenden
```


## Lizenz

Dieses Projekt ist für Bildungs- und Entwicklungszwecke erstellt.

## Support

Bei Fragen oder Problemen:
1. Überprüfe die Fehlerbehebung oben
2. Stelle sicher, dass alle Abhängigkeiten korrekt installiert sind
3. Überprüfe die OpenAI API Dokumentation
