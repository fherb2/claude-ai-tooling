# Chats-Export

*Stand: 2026-08-27*

**Holt Chats aus claude.ai-Projekten und legt sie als durchsuchbare JSON-Dateien in einem Claude-Code-Projekt ab** — zum Wiederfinden früheren Zusammenhangs, nicht zum Fortsetzen an dieser Stelle. (Auf claude.ai lassen sie sich natüprlich fortsetzen und dann im Claude-Code-Projekt wieder aktualisieren.) Anthropic bietet dafür bislang keinen eigenen Weg: Chats lassen sich weder zwischen Konten noch zwischen claude.ai, Claude Desktop und Claude Code verschieben. Dieser Ordner baut die beiden Wege nach, die dafür tatsächlich funktionieren — der Kontoexport und die internen Web-Endpunkte von claude.ai — und ein Skript, das beide gleich behandelt.

## Der Skill

Benutzt wird das über den Skill `chat-export`. Installation und Bedienung stehen vollständig in dessen eigener README:

- [`skills/chat-export/README.md`](skills/chat-export/README.md) (deutsch)
- [`skills/chat-export/README.en.md`](skills/chat-export/README.en.md) (English)

Kopiert wird ausschließlich der Ordner `skills/chat-export/` — alles andere hier gehört zur Entwicklung.

## Stand

**Der Skill ist gebaut, an echten Daten in drei unabhängigen Sitzungen erprobt und einsetzbar** — zuletzt an einem Großlauf über vier reale claude.ai-Projekte mit 171 Chats, deren Ergebnis gegen die tatsächliche Export-ZIP verifiziert wurde (171 von 171 Chats gefunden, keine Abweichung). Beide Wege — Kontoexport und Web-Endpunkte — liefern nachweislich dasselbe Ergebnis.

**Am 22. August 2026 hat eine unabhängige Instanz die Logik gegen die Ziele der Doku geprüft; alle Befunde sind behoben.**

Was diese Fassung **nicht** leistet, steht in [`implementation-doc.md`](implementation-doc.md), Kapitel 1.8 — die praktischen Folgen für die Bedienung im Abschnitt „Wenn du später weitere Chats nachreichen willst" der Skill-README. Kurz gefasst: ein Ordner je Quellprojekt, und der Ordner samt Protokoll ist der Zustand.

Was daraus als nächste Ausbaustufe folgt, umreißt [`work-plan-v2.md`](work-plan-v2.md) — zwei Komplexe, noch ohne Schritte.

Ebenfalls für eine künftige Fassung vorgemerkt (Durchsicht vom 25. August 2026): Die `SKILL.md` des Skills lädt mit 167 Zeilen vollständig und bricht hart ab, wenn die Browser-Werkzeuge nicht an der Nachricht hängen — ein häufiger und damit teurer Ausgang. Eine Abhilfe nach dem Teilungsmuster von `skills/` (dünne Klärung, Regeln nachgeladen) setzt voraus, dass zuerst die Vorgaben **dieses** Vorhabens geprüft werden, statt jenes Muster unbesehen zu übertragen.

Alle Fakten, Belege und Prüfpunkte zu diesem Vorhaben stehen in [`implementation-doc.md`](implementation-doc.md); die Mechanik der Chrome-Anbindung samt ihrer Fallstricke in [`chrome-access.de.md`](chrome-access.de.md) / [`chrome-access.en.md`](chrome-access.en.md).
