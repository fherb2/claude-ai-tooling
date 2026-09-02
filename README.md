# Claude-AI-Tooling

*Stand: 2026-09-02*

*[English version](README.en.md)*

Werkzeuge / Bausteine rund um die tägliche Arbeit mit Claude — claude.ai, Claude Desktop (Chat + Cowork) und Claude Code. Eigenständige Bausteine, jeder mit eigener Dokumentation in seinem Ordner. Diese Seite ist nur die Übersicht. Nutze die verlinkten READMEs in den Bausteinen.

**Claude Cowork im Einzelnen ist hier noch nicht berücksichtigt.** Die seit Sommer 2026 verfügbare Variante verhält sich in einem entscheidenden Punkt anders als die drei oben genannten: Sie arbeitet über angebundene Ordner direkt auf dem Rechner des Nutzers. Was in diesem Repository steht — Zielwelten, Skills, Arbeitsabläufe — bezieht sich deshalb genau genommen auf claude.ai-Chat, Claude Desktop Chat und Claude Code.

## Was es gibt


| Baustein                                                      | Anliegen                                                                                                                                                                                                                                  |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`pack-source-to-txt/`](pack-source-to-txt/README.md)<br>✅ | **Die ganze Projekt-Codebase als eine Datei**: präziser, aktueller Projektkontext für eine KI ohne Zugriff auf den Rechner.                                                                                                             |
| [`home-.claude-sharing/`](home-.claude-sharing/README.md)<br>⚠️ | **Arbeit über mehrere Rechner hinweg**: Chat-Gedächtnis und Arbeitsanweisungen / Skills statt vieler Einzelner, über die Systeme verteilt: `~/.claude` auf allen Rechnern synchron, Konflikte werden gemeldet und geführt aufgelöst. |
| [`skills/`](skills/README.md)<br>☑ | Statt vieler CLAUDE.md-Anweisungen: **Vorgaben automatisch nachladen lassen**. Erst und nur dann im Kontext, wenn tatsächlich benötigt: Claude-Code-**Skills mit „stillem“ Trigger** — und seit September 2026 auch **garantierte Fähigkeiten mit Hook-Auslöser**.                                                   |
| [`CLAUDE.md-Snippets/`](CLAUDE.md-Snippets/README.md)<br>✅ | **Fertige Textbausteine für Anweisungsdateien**: einzeln herauskopierbare Absätze für die `CLAUDE.md` einer lokalen Installation und für die Stellen, an denen claude.ai Anweisungen aufnimmt. |
| [`safety-related/`](safety-related/)<br>✅ | **Konfigurationen und Hinweise zur sicheren Nutzung von Claude**: fertige `settings.json`-Blöcke für die Bash-Sandbox und die Werkzeug-Berechtigungen, jeder Parameter in einer Zeile erklärt. |

(✅ einsatzbereit · 🚧 in Arbeit · ⚠️ mit Vorbehalt · ☑ abh. vom Skill)

Zwei Dateien in der Projektwurzel begleiten die Entwicklung aller Bausteine: **[`skill-dev-doc.md`](skill-dev-doc.md)** trägt die Vorgaben und das Umgebungswissen für den Bau von Skills — gleich in welchem Ordner sie entstehen —, **[`work-plan.md`](work-plan.md)** die anstehenden Arbeitsschritte. Vorhaben mit eigenem Entwicklungsstand führen daneben ihre eigene Doku und ihren eigenen Arbeitsplan.

### **Anwendungshinweise** weiter unten in dieser README:

* **[Aufbewahrungsdauer von Chats bei Claude Code](#aufbewahrungsdauer-von-chats-bei-claude-code)**

## pack-source-to-txt (nicht auf Claude beschränkt)

**Zweck:** Code-Analyse und -Weiterentwicklung auf Agent Web-Instanzen; Nutzung in schwach gesicherten Bereichen: Kein unmittelbarer Systemzugriff.

**Ein einzelnes, in sich geschlossenes Shell-Skript (`packsrc.sh`), das die Quelldateien eines Projekts in eine strukturierte Textdatei bündelt — bereit zum Hochladen in die Knowledge Base eines Web-KI-Agenten.** Jede Datei steckt in eindeutigen Metadaten-Blöcken mit laufbezogenem Zeitstempel und letztem Änderungsdatum, ein KI-lesbarer Header erklärt dem Agenten die Interpretation. Konfigurierbar sind Quellverzeichnisse, Dateiendungen, explizite Einzeldateien und Verzeichnisausschlüsse; ein Abnahmetest unter `tests/` sichert das Verhalten ab. Braucht nur Bash und die GNU-Werkzeuge, keine weiteren Abhängigkeiten.

**Hinweis:** Standard bei Claude Code ist, Chats nach 30 Tagen wegzuwerfen. Das lässt sich beliebig nach oben drehen.

**Stand:** produktiv — Näheres in der [README des Bausteins](pack-source-to-txt/README.md).

## home-.claude-sharing

**Zweck: Hält den Arbeitszustand von Claude Desktop und Claude Code — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — über Syncthing zwischen mehreren Rechnern synchron. – Rechnerwechsel zwischen Home und Office oder remote und lokal. Benötigt dabei kein VPN oder lokales Netz.**

Vermittelt wird das über einen dauerhaft laufenden NAS-Knoten. Der eigentliche Kern ist der Umgang mit dem, was Syncthing bewusst nicht löst: Gleichzeitig geänderte Dateien werden als Konfliktkopien abgelegt, ein Wächter-Dienst entdeckt sie, meldet sich und führt den Nutzer gemeinsam mit Claude durch die inhaltliche Auflösung. Installationsskripte, Dienstdefinition und eine Einrichtungsanleitung für den Vermittlungsknoten liegen bei.

**Stand:** Im Betrieb beim Entwickler, noch nicht zur Weitergabe freigegeben — Näheres in der [README des Bausteins](home-.claude-sharing/README.md).

## skills

**Zweck: Anweisungen aus CLAUDE.md raus und Aufgabenbeschreibungen wiederverwendbar machen.** Skills starten auch ohne ein passendes „Trigger-Wort“.

Wiederverwendbare Skills für Claude Code, claude.ai und Claude Desktop (Chat + Cowork): Anweisungen, die nicht dauerhaft in `CLAUDE.md`-Dateien Kontext kosten, sondern erst geladen werden, wenn sie gebraucht werden. Jeder fertige Skill liegt als Installationspaket bereit — ein Archiv je Sprache und Zielwelt, im Unterordner `downloads/` des Skills.

Der umfangreichste unter ihnen ist **`chat-export`**: Chats aus Claude.ai zwischen unterschiedlichen Nutzerkonten oder nach Projekten sortiert in eine lokale Claude-Code-Installation zu holen, unterstützt Anthropic derzeit (08/2026) nicht — mit diesem Skill geht es doch, über den angemeldeten Chrome oder aus einem Kontoexport-ZIP. Er ist der einzige Skill mit eigener Implementierungsdoku und eigenem Fahrplan; warum, steht in der [README des Bausteins](skills/README.md).

Dazu das hier erarbeitete Konzept der **stillen Trigger** — Auslöser für Situationen, die niemand ausspricht. Der Anthropic-Standard, einen Skill aktiv vom Nutzer zu starten oder im Skill über `description:` per Trigger-Wörter im Chat automatisch zu starten, erweitert das Konzept der stillen Trigger auch ein Start aus dem Kontext des Chats heraus. Das ist keine Claude-Code-Erweiterung, sondern wird über besondere Formulierungsregeln in CLAUDE.md erreicht. Details zur Nachnutzung in diesem Baustein.

Seit September 2026 leben hier auch **garantierte Fähigkeiten**: Bausteine, deren Auslöser kein stiller Trigger ist, sondern ein **Hook** — ein Ereignis-Einhänger der Claude-Code-Engine, der garantiert läuft, wo ein Skill nur wahrscheinlich lädt. Installiert werden sie genauso (Paket entpacken); nur wandert statt eines CLAUDE.md-Snippets ein Eintrag in die `settings.json`. Erster dieser Art: **`recall-skills-after-compact`** — nach jeder Kontext-Kompression bekommt die Instanz die Liste der zuvor geladenen Skills in den Kontext gespielt und legt sie dem Nutzer vor; der entscheidet, was neu geladen wird.

**Stand:** Der Stand der einzelnen Skills wird in der [zugehörigen README](skills/README.md) einzeln ausgewiesen.

## CLAUDE.md-Snippets

**Zweck: Wiederkehrende Anweisungen nicht jedes Mal neu formulieren.** Fertig ausformulierte Textbausteine, die einzeln in eine Anweisungsdatei kopiert werden — in die `CLAUDE.md` einer lokalen Claude-Code-Installation oder an die Stellen, an denen claude.ai Anweisungen aufnimmt.

Der Schnitt zwischen den drei Dateien ist der **Wirkungsort**, nicht das Thema: Was in beiden Umgebungen wortgleich taugt, steht in `common-snippets`; was nur bei claude.ai oder nur lokal gilt, in der jeweils eigenen Datei. Ein Thema kann deshalb planmäßig in mehreren Dateien vorkommen — beim Memory etwa die Frage, *ob* etwas gespeichert werden darf, getrennt von der Frage, *wohin*.

Nicht zu verwechseln mit den `CLAUDE-snippet.md`-Dateien im Baustein `skills/`: Die sind der stille Trigger eines bestimmten Skills und ohne ihn wirkungslos. Hier stehen Anweisungen, die für sich wirken und keinen Skill hinter sich haben.

**Einen Baustein sollte man immer übernehmen: „Vorrang der Anweisungsebenen“.** Er klärt, welche Ebene gilt, wenn zwei Anweisungen einander widersprechen. Ohne ihn wird in diesem Fall willkürlich eine der beiden Regeln gewählt — belegt für Claude Code, das alle gefundenen `CLAUDE.md`-Dateien aneinanderhängt, statt sie einander überschreiben zu lassen ([memory](https://code.claude.com/docs/en/memory)). Bemerkbar macht sich das als Rückfrage an einer Stelle, an der keine nötig wäre, oder als überraschendes Verhalten. Der Baustein ist vier Zeilen lang und kann nichts kaputt machen.

**Stand:** Einsatzbereit, in beiden Sprachfassungen — Näheres in der [README des Bausteins](CLAUDE.md-Snippets/README.md).

## safety-related

**Zweck: Konfigurationen und Hinweise zur sicheren Nutzung von Claude.** Fertige `settings.json`-Blöcke, die den Zugriff von Claude Code auf Dateisystem und Netz eingrenzen — zum Übernehmen, ohne die Sandbox-Dokumentation querlesen zu müssen.

Abgedeckt sind zwei Wirkungsflächen, die leicht verwechselt werden: die **Bash-Sandbox** (`sandbox.*`), die das Betriebssystem durchsetzt und die Bash samt aller Kindprozesse umschließt, und die **Berechtigungen der Agent-Werkzeuge** (`permissions.*`) für Read, Edit, Write und WebFetch, die an der Sandbox vorbeilaufen. Erst beide zusammen schließen etwa einen Geheimnis-Pfad vollständig. Zu jedem Parameter steht eine Zeile, was er bewirkt.

**Stand:** Einsatzbereit, in beiden Sprachfassungen — [`sandbox-settings.de.md`](safety-related/sandbox-settings.de.md) · [`.en.md`](safety-related/sandbox-settings.en.md). Der Ordner hat bewusst keine eigene README; die beiden Dateien erklären sich selbst.

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
