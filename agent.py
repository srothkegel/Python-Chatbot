"""
Pydantic AI Agent Definition

Dieses Modul definiert den Chatbot-Agenten mit Tool-Funktionalität.
Der Agent verwendet OpenAI als LLM-Backend und unterstützt Function Calling.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

# Laden der Umgebungsvariablen
# Explizit den Pfad zur .env Datei angeben
env_path = os.path.join(os.path.dirname(__file__), ".env")
# Lade .env Datei
load_dotenv(dotenv_path=env_path, override=True)

# Validierung des API-Keys
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Zusätzliche Debug-Informationen
    env_file_exists = os.path.exists(env_path)
    raise ValueError(
        f"OPENAI_API_KEY ist nicht gesetzt.\n"
        f"  .env Datei existiert: {env_file_exists}\n"
        f"  .env Pfad: {env_path}\n"
        f"Bitte überprüfen Sie Ihre .env-Datei und stellen Sie sicher, "
        f"dass sie den Eintrag 'OPENAI_API_KEY=ihr_key_hier' enthält.\n"
        f"Siehe .env.example für eine Vorlage."
    )


def create_agent() -> Agent[None, str]:
    """
    Erstellt und konfiguriert den Pydantic AI Agenten.
    
    Verwendet 'gpt-4o-mini' als Standardmodell.
    
    Returns:
        Agent: Konfigurierter Pydantic AI Agent
        
    Raises:
        ValueError: Wenn der OPENAI_API_KEY nicht gesetzt ist
    """
    # Pydantic AI verwendet das Format 'openai:model-name'
    model_name: str = "openai:gpt-4o-mini"
    
    system_prompt: str = (
        "Du bist ein hilfsbereiter und freundlicher Assistent. "
        "Du hilfst Benutzern bei ihren Fragen und Aufgaben. "
        "Wenn du Tools verwenden kannst, nutze sie, um präzise Informationen zu liefern."
    )
    
    new_agent: Agent[None, str] = Agent(
        model=model_name,
        system_prompt=system_prompt,
    )
    
    # Registriere Tools mit dem Decorator
    @new_agent.tool_plain
    def get_current_time() -> str:
        """
        Gibt die aktuelle Uhrzeit zurück.
        
        Returns:
            str: Aktuelle Uhrzeit im Format 'YYYY-MM-DD HH:MM:SS'
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return new_agent


# Erstelle den Agenten beim Import
try:
    agent: Agent[None, str] = create_agent()
except Exception as e:
    # Bei Fehlern beim Erstellen des Agenten, setze auf None
    # Die app.py wird dann eine entsprechende Fehlermeldung zeigen
    agent = None  # type: ignore
    print(f"Warnung: Agent konnte nicht erstellt werden: {e}")
