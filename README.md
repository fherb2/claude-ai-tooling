# Claude-AI-Tooling

*[English version](README.en.md)*

Werkzeuge / Bausteine rund um die tägliche Arbeit mit Claude — claude.ai, Claude Desktop und Claude Code. Eigenständige Bausteine, jeder mit eigener Dokumentation in seinem Ordner. Diese Seite ist nur die Übersicht. Nutze die verlinkten READMEs in den Bausteinen.

## Was es gibt


| Baustein                                                      | Anliegen                                                                                                                                                                                                                                  |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`pack-source-to-txt/`](pack-source-to-txt/README.md)<br>✅ | **Die ganze Projekt-Codebase als eine Datei**: präziser, aktueller Projektkontext für eine KI ohne Zugriff auf den Rechner.                                                                                                             |
| [`chat-export/`](chat-export/README.de.md)<br>✅ | **Chats aus Claude.ai zwischen unterschiedlichen Nutzerkonten bzw. nach Projekten sortiert in lokale Claude-Instanzen** (Claude Code) **übertragen** — was Anthropic bisher nicht bietet.                                            |
| [`home-.claude-sharing/`](home-.claude-sharing/README.md)<br>⚠️ | **Arbeit über mehrere Rechner hinweg**: Chat-Gedächtnis und Arbeitsanweisungen / Skills statt vieler Einzelner, über die Systeme verteilt: `~/.claude` auf allen Rechnern synchron, Konflikte werden gemeldet und geführt aufgelöst. |
| [`skills/`](skills/README.md)<br>☑ | Statt vieler CLAUDE.md-Anweisungen:**Vorgaben automatisch nachladen lassen**. Erst und nur dann im Kontext, wenn tatsächlich benötigt: Claude-Code-**Skills mit "stillem" Trigger**.                                                   |

(✅ einsatzbereit · 🚧 in Arbeit · ⚠️ mit Vorbehalt · ☑ abh. vom Skill)

### **Anwendungshinweise** weiter unten in dieser README:

* **[Aufbewahrungsdauer von Chats bei Claude Code](#aufbewahrungsdauer-von-chats-bei-claude-code)**

## pack-source-to-txt (nicht auf Claude beschränkt)

**Zweck:** Code-Analyse und -Weiterentwicklung auf Agent Web-Instanzen; Nutzung in schwach gesicherten Bereichen: Kein unmittelbarer Systemzugriff.

**Ein einzelnes, in sich geschlossenes Shell-Skript (`packsrc.sh`), das die Quelldateien eines Projekts in eine strukturierte Textdatei bündelt — bereit zum Hochladen in die Knowledge Base eines Web-KI-Agenten.** Jede Datei steckt in eindeutigen Metadaten-Blöcken mit laufbezogenem Zeitstempel und letztem Änderungsdatum, ein KI-lesbarer Header erklärt dem Agenten die Interpretation. Konfigurierbar sind Quellverzeichnisse, Dateiendungen, explizite Einzeldateien und Verzeichnisausschlüsse; ein Abnahmetest unter `tests/` sichert das Verhalten ab. Braucht nur Bash und die GNU-Werkzeuge, keine weiteren Abhängigkeiten.

**Hinweis:** Standard bei Claude Code ist, Chats nach 30 Tagen wegzuwerfen. Das lässt sich beliebig nach oben drehen.

**Stand:** produktiv — Näheres in der [README des Bausteins](pack-source-to-txt/README.md).

## chat-export

**Zweck:** **Chats aus Claude.ai zwischen unterschiedlichen Nutzerkonten bzw. nach Projekten sortiert und in lokale Claude-Instanzen (Claude Code) zu importieren**, unterstützt Anthropic derzeit (08/2026) nicht. – Mit diesem Tooling geht's doch.

Die vorhandene Datenexport-Schnittstelle ist dazu nicht unmittelbar geeignet und wird mit diesem Tooling nur mittelbar benutzt. Das Hilfsmittel unterstützt den Import nach Projekten getrennt und erlaubt auch das "Nachladen" bereits beim letzten Import begonnener Chats. Keine simple 1-klick-Lösung. – Statt dessen überhaupt erst mal eine Lösung.

Bedient wird es über den Claude-Code-Skill `chat-export`, der durch beide Wege führt — den Kontoexport und die internen Web-Endpunkte von Claude.ai über den angemeldeten Chrome.

**Stand:** Einsatzbereit. An echten Daten in mehreren unabhängigen Sitzungen erprobt, zuletzt an vier realen Projekten mit 171 Chats — Ergebnis gegen die tatsächliche Export-ZIP verifiziert. Am 22. August 2026 zusätzlich von einer unabhängigen Instanz gegen die Doku-Ziele geprüft; alle Befunde behoben. Näheres in der [README des Bausteins](chat-export/README.de.md).

## home-.claude-sharing

**Zweck: Hält den Arbeitszustand von Claude Desktop und Claude Code — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — über Syncthing zwischen mehreren Rechnern synchron. – Rechnerwechsel zwischen Home und Office oder remote und lokal. Benötigt dabei kein VPN oder lokales Netz.**

Vermittelt wird das über einen dauerhaft laufenden NAS-Knoten. Der eigentliche Kern ist der Umgang mit dem, was Syncthing bewusst nicht löst: Gleichzeitig geänderte Dateien werden als Konfliktkopien abgelegt, ein Wächter-Dienst entdeckt sie, meldet sich und führt den Nutzer gemeinsam mit Claude durch die inhaltliche Auflösung. Installationsskripte, Dienstdefinition und eine Einrichtungsanleitung für den Vermittlungsknoten liegen bei.

**Stand:** Im Betrieb beim Entwickler, noch nicht zur Weitergabe freigegeben — Näheres in der [README des Bausteins](home-.claude-sharing/README.md).

## skills

**Zweck: Anweisungen aus CLAUDE.md raus und Aufgabenbeschreibungen wiederverwendbar machen.** Skills starten auch ohne ein passendes "Trigger-Wort".

Wiederverwendbare Skills für Claude Code: Anweisungen, die nicht dauerhaft in `CLAUDE.md`-Dateien Kontext kosten, sondern erst geladen werden, wenn sie gebraucht werden.

Dazu das hier erarbeitete Konzept der **stillen Trigger** — Auslöser für Situationen, die niemand ausspricht. Der Anthropic-Standard, einen Skill aktiv vom Nutzer zu starten oder im Skill über `description:` per Trigger-Wörter im Chat automatisch zu starten, erweitert das Konzept der stillen Trigger auch ein Start aus dem Kontext des Chats heraus. Das ist keine Claude-Code-Erweiterung, sondern wird über besondere Formulierungsregeln in CLAUDE.md erreicht. Details zur Nachnutzung in diesem Baustein.

**Stand:** Der Stand der einzelnen Skills wird in der [zugehörigen README](skills/README.md) einzeln ausgewiesen.

## Anwendungshinweise

### Aufbewahrungsdauer von Chats bei Claude Code

Claude Code legt Chats und die zugehörigen Daten und Sicherungskopien von zu ändernden Files in `~/.claude/` ab. **Die Aufbewahrungsdauer ist standardmäßig nur 30 Tage. Wer später auf Wissen aus diesen Chats zurückgreifen will, hat keine Chance.**

Die Aufbewahrungsdauer lässt sich in `~/.claude/settings.json` mit dem Schlüssel `cleanupPeriodDays` **umkonfigurieren**.

**Beispiel für 3 Jahre:**

```json
{
  "cleanupPeriodDays": 1095
}

```

Der Schlüssel ist prinzipiell in allen Settings-Ebenen zulässig — `~/.claude/settings.json` (Nutzer), `<projekt>/.claude/settings.json`, `<projekt>/.claude/settings.local.json`.

**Ausgenommen sind aber einige Pfade** — vor allem `history.jsonl` (jeder je getippte Prompt mit Zeitstempel und Projektpfad) und das Auto-Memory unter `projects/<projekt>/memory/`. Die bleiben unbefristet liegen. Wer also die Aufbewahrungsdauer als Datenschutz-Stellschraube liest, greift mit `cleanupPeriodDays` allein zu kurz; die Doku nennt dafür zusätzlich `CLAUDE_CODE_SKIP_PROMPT_HISTORY` und `claude project purge`.

## Lizenz

Dieses Repository legt keine gemeinsame Lizenz fest. Jeder Baustein regelt seine Nutzungslizenz einzeln in seiner eigenen README — dort steht auch, was zur Weitergabe / Nutzung freigegeben ist.
