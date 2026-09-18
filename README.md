# Chatbot mit Pydantic AI und Gradio

Eine moderne Chatbot-Applikation, die Pydantic AI für die Backend-Logik und Gradio für die Benutzeroberfläche verwendet.

## Features

- 🤖 **Intelligenter Chatbot**: Nutzt OpenAI GPT-Modelle (gpt-5-mini mit Fallback auf gpt-4o-mini)
- 🛠️ **Tool-Unterstützung**: Demonstriert Function Calling mit einem `get_current_time` Tool
- ⚡ **Asynchron**: Vollständig asynchrone Implementierung für optimale Performance
- 🎨 **Moderne UI**: Nutzt Gradio's `ChatInterface` für eine intuitive Chat-Erfahrung
- 🔒 **Sicher**: API-Keys werden über `.env` Dateien verwaltet

## Voraussetzungen

- Python 3.12.10 oder höher
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

- **Einfache Frage**: "Hallo! Wie geht es dir?"
- **Tool-Nutzung**: "Wie spät ist es?" (nutzt das `get_current_time` Tool)
- **Allgemeine Fragen**: "Was kannst du für mich tun?"

## Projektstruktur

```
chatbot/
├── requirements.txt      # Python-Abhängigkeiten
├── .env.example         # Vorlage für Umgebungsvariablen
├── .env                 # Deine Umgebungsvariablen (nicht in Git)
├── agent.py             # Pydantic AI Agent Definition
├── app.py               # Gradio Benutzeroberfläche
└── README.md            # Diese Datei
```

## Technische Details

### Architektur

- **Backend (`agent.py`)**: 
  - Definiert den Pydantic AI Agenten
  - Konfiguriert System-Prompt und Tools
  - Vollständig asynchron implementiert

- **Frontend (`app.py`)**:
  - Gradio ChatInterface für die UI
  - Async-Handler für Agent-Kommunikation
  - Unterstützt Streaming (falls verfügbar)

### Tools

Der Bot verfügt aktuell über ein Tool:
- `get_current_time()`: Gibt die aktuelle Uhrzeit zurück

Weitere Tools können einfach in `agent.py` hinzugefügt werden.

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

## Entwicklung

### Weitere Tools hinzufügen

1. Öffne `agent.py`
2. Definiere ein neues Tool mit dem `@Tool` Decorator:
```python
@Tool
async def mein_tool(param: str) -> str:
    """Beschreibung des Tools"""
    # Tool-Logik hier
    return "Ergebnis"
```
3. Füge das Tool zur Agent-Konfiguration hinzu:
```python
agent = Agent(
    model=model_name,
    system_prompt=system_prompt,
    tools=[get_current_time, mein_tool],  # Neues Tool hinzufügen
)
```

### System-Prompt anpassen

Ändere den `system_prompt` in der `create_agent()` Funktion in `agent.py`.

## Lizenz

Dieses Projekt ist für Bildungs- und Entwicklungszwecke erstellt.

## Support

Bei Fragen oder Problemen:
1. Überprüfe die Fehlerbehebung oben
2. Stelle sicher, dass alle Abhängigkeiten korrekt installiert sind
3. Überprüfe die OpenAI API Dokumentation
