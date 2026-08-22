# Chats-Export

**Holt Chats aus claude.ai-Projekten und legt sie als durchsuchbare JSON-Dateien in einem Claude-Code-Projekt ab** — zum Wiederfinden früheren Zusammenhangs, nicht zum Fortsetzen. Anthropic bietet dafür bislang keinen eigenen Weg: Chats lassen sich weder zwischen Konten noch zwischen claude.ai, Claude Desktop und Claude Code verschieben. Dieser Ordner baut die beiden Wege nach, die dafür tatsächlich funktionieren — der Kontoexport und die internen Web-Endpunkte von claude.ai — und ein Skript, das beide gleich behandelt.

## Der Skill

Benutzt wird das über den Skill `chat-export`. Installation und Bedienung stehen vollständig in dessen eigener README:

- [`skills/chat-export/README.de.md`](skills/chat-export/README.de.md) (deutsch)
- [`skills/chat-export/README.en.md`](skills/chat-export/README.en.md) (English)

Kopiert wird ausschließlich der Ordner `skills/chat-export/` — alles andere hier gehört zur Entwicklung.

## Stand

**Der Skill ist gebaut, an echten Daten in drei unabhängigen Sitzungen erprobt und einsetzbar** — zuletzt an einem Großlauf über vier reale claude.ai-Projekte mit 171 Chats, deren Ergebnis gegen die tatsächliche Export-ZIP verifiziert wurde (171 von 171 Chats gefunden, keine Abweichung). Beide Wege — Kontoexport und Web-Endpunkte — liefern nachweislich dasselbe Ergebnis.

**Am 22. August 2026 hat eine unabhängige Instanz die Logik gegen die Ziele der Doku geprüft; alle Befunde sind behoben.**

Alle Fakten, Belege und Prüfpunkte zu diesem Vorhaben stehen in [`implementation_doku.md`](implementation_doku.md); die Mechanik der Chrome-Anbindung samt ihrer Fallstricke in [`chrome-zugriff.de.md`](chrome-zugriff.de.md) / [`chrome-access.en.md`](chrome-access.en.md).
