"""
Gradio ChatInterface für den Deep Research Agent

Dieses Modul stellt die Benutzeroberfläche bereit und integriert die
Deep-Research-Pipeline aus agent.py. Der Fortschritt der Recherche wird
live im Chat-Fenster angezeigt (Streaming), am Ende erscheint der finale
Markdown-Forschungsbericht.
"""

from collections.abc import AsyncGenerator

import gradio as gr

try:
    from agent import run_deep_research

    _AGENT_ERROR: str | None = None
except (ImportError, ValueError) as e:
    run_deep_research = None  # type: ignore[assignment]
    _AGENT_ERROR = str(e)
    print(f"Fehler beim Initialisieren des Research-Agenten: {e}")


async def async_chat_handler(
    message: str,
    history: list[dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    Async Streaming-Handler für die Gradio ChatInterface.

    Startet die Deep-Research-Pipeline und streamt den Fortschritt sowie den
    finalen Bericht in das Chat-Fenster.

    Args:
        message: Die Anfrage/das Stichwort des Nutzers.
        history: Die Chat-Historie im OpenAI-Format (hier nicht verwendet, da
            jede Recherche eigenständig ist).

    Yields:
        str: Fortlaufende Statusanzeige, zuletzt der finale Forschungsbericht.
    """
    if run_deep_research is None:
        yield (
            "Research-Agent ist nicht verfügbar. Bitte überprüfe deine .env-Datei "
            "und stelle sicher, dass OPENAI_API_KEY gesetzt ist.\n\n"
            f"Details: {_AGENT_ERROR}"
        )
        return

    if not message or not message.strip():
        yield "Bitte gib ein Thema oder Stichwort für die Recherche ein."
        return

    try:
        async for update in run_deep_research(message.strip()):
            yield update
    except Exception as exc:  # Absicherung gegen unerwartete Fehler
        yield f"Unerwarteter Fehler bei der Recherche: {exc}"


def create_interface() -> gr.ChatInterface:
    """
    Erstellt die Gradio ChatInterface-Instanz für den Deep Research Agent.

    Returns:
        gr.ChatInterface: Konfigurierte ChatInterface mit Streaming.
    """
    interface = gr.ChatInterface(
        fn=async_chat_handler,
        title="Deep Research Agent",
        description=(
            "Gib ein Thema oder Stichwort ein (z. B. 'Nvidia-Aktie' oder "
            "'Quantencomputing Durchbruch 2026'). Der Agent plant die Recherche, "
            "durchsucht das Web, liest die echten Artikeltexte aus (Deep Reading) "
            "und erstellt einen strukturierten Forschungsbericht mit Quellenangaben."
        ),
        examples=[
            "Nvidia-Aktie",
            "Quantencomputing Durchbruch 2026",
            "Auswirkungen von KI auf den Arbeitsmarkt",
        ],
        fill_height=True,
    )
    return interface


def main() -> None:
    """Hauptfunktion zum Starten der Gradio-Anwendung."""
    if run_deep_research is None:
        print(
            "FEHLER: Research-Agent konnte nicht initialisiert werden. "
            "Bitte überprüfe deine .env-Datei."
        )
        return

    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",  # Erlaubt Zugriff von außen
        server_port=7860,  # Standard Gradio Port
    )


if __name__ == "__main__":
    main()
