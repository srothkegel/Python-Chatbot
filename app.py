"""
Gradio ChatInterface für den Pydantic AI Chatbot

Dieses Modul stellt die Benutzeroberfläche bereit und integriert
den Pydantic AI Agenten für die Chat-Funktionalität.
"""

import asyncio
from typing import Generator

import gradio as gr

try:
    from agent import agent
except ImportError as e:
    agent = None
    print(f"Fehler beim Import des Agenten: {e}")
except ValueError as e:
    agent = None
    print(f"Fehler bei der Agent-Konfiguration: {e}")


async def async_chat_handler(
    message: str,
    history: list[dict[str, str]],
) -> str:
    """
    Async Handler-Funktion für die Gradio ChatInterface.
    
    Verarbeitet Benutzereingaben asynchron und gibt die Agent-Antwort zurück.
    
    Args:
        message: Die Benutzereingabe
        history: Die Chat-Historie im OpenAI-Format
        
    Returns:
        str: Die Antwort des Agenten
    """
    if agent is None:
        return (
            "Agent ist nicht verfügbar. "
            "Bitte überprüfen Sie Ihre .env-Datei und stellen Sie sicher, "
            "dass OPENAI_API_KEY gesetzt ist."
        )
    
    try:
        # Normale async Ausführung
        result = await agent.run(message)
        # Pydantic AI Result hat ein .output Attribut (nicht .data)
        return str(result.output)
    except Exception as e:
        return f"Fehler bei der Verarbeitung: {str(e)}"


def chat_handler(
    message: str,
    history: list[dict[str, str]],
) -> str:
    """
    Synchroner Wrapper für die async Handler-Funktion.
    
    Args:
        message: Die Benutzereingabe
        history: Die Chat-Historie im OpenAI-Format
        
    Returns:
        str: Die Antwort des Agenten
    """
    try:
        # Versuche einen vorhandenen Event-Loop zu nutzen
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Falls bereits ein Loop läuft, erstelle einen neuen
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, async_chat_handler(message, history)
                )
                return future.result()
        else:
            return loop.run_until_complete(async_chat_handler(message, history))
    except RuntimeError:
        # Kein Event-Loop vorhanden, erstelle einen neuen
        return asyncio.run(async_chat_handler(message, history))


def create_interface() -> gr.ChatInterface:
    """
    Erstellt die Gradio ChatInterface-Instanz.
    
    Returns:
        gr.ChatInterface: Konfigurierte ChatInterface
    """
    interface = gr.ChatInterface(
        fn=chat_handler,
        title="Chatbot mit Pydantic AI",
        description=(
            "Ein intelligenter Chatbot, der Pydantic AI und OpenAI verwendet. "
            "Der Bot kann Tools verwenden, z.B. die aktuelle Uhrzeit abrufen."
        ),
        examples=[
            "Hallo! Wie geht es dir?",
            "Wie spät ist es?",
            "Was kannst du für mich tun?",
        ],
        fill_height=True,
    )
    
    return interface


def main() -> None:
    """
    Hauptfunktion zum Starten der Gradio-Anwendung.
    """
    if agent is None:
        print(
            "FEHLER: Agent konnte nicht initialisiert werden. "
            "Bitte überprüfen Sie Ihre .env-Datei."
        )
        return
    
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",  # Erlaubt Zugriff von außen
        server_port=7860,  # Standard Gradio Port
        share=False,  # Setze auf True für öffentliche URL
    )


if __name__ == "__main__":
    main()
