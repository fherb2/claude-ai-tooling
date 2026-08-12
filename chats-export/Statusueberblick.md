# Statusüberblick Chats-Export

**Momentaufnahme vom 2026-08-09** zur Prüfung von Stand und anstehenden Arbeiten. Dieses Dokument ist bewusst **keine** zu pflegende Doku: jede Aussage hat ihr normatives Zuhause in `implementation_doku.md` (im Folgenden „Doku"), hierher sind nur Verweise und der Prüfblick kopiert. Bei Widerspruch gilt die Doku.

---

## 1 Aufgabenstellung

### 1.1 Was war die Aufgabe

Chats aus claude.ai-Projekten sollen **im Zusammenhang ihres Projekts durchsuchbar** werden — nicht fortführbar. Zweck ist das Wiederfinden früher besprochenen Kontexts, primär aus Claude Code heraus (Dateien im Git-Repo des Zielprojekts, per `Read`/`Grep` erreichbar), sekundär im Projektwissen einer claude.ai-Instanz. Es ist ein **wiederkehrender Abgleich**, keine einmalige Migration: neue Chats kommen laufend hinzu, vorhandene laufen weiter. (Doku 1.1, 1.3)

Anthropic bietet dafür keinen Weg: kein Chat-Export je Projekt, kein Import, keine öffentliche API, die claude.ai-Projekte kennt (einzige Ausnahme Compliance-API, nur Enterprise — Doku 4.5). Alles hier ersetzt diesen fehlenden Weg und ruht deshalb überwiegend auf **beobachtetem, nicht zugesichertem** Verhalten.

### 1.2 Welche Komponenten setzen sie um

| Komponente | Rolle |
| --- | --- |
| `source/chat_export_convert.py` | **Hauptweg**: wandelt ein Kontoexport-ZIP in Chatdateien je Quellprojekt, führt das Protokoll. Läuft lokal (Claude Code), wird nie hochgeladen. Kommandos `list`, `convert`, `diff`, `report`, `analyse`. |
| `source/chat_read_store.py` | **Zweitweg**: liest Chats per `read_conversation` direkt in der claude.ai-Instanz. Wird als Einzeldatei hochgeladen, trägt seine ganze Betriebsanleitung im Docstring. Kommandos `plan`, `overview`, `state`, `map`, `ingest`, `status`, `export`. |
| `source/inspect_export.py` | **Schemawache**: beschreibt ein Export-ZIP (Struktur, Zahlen, nie Inhalt) und liefert die Projektliste mit Erstellungsdaten — der Zulieferer für den Sondierungsexport. |
| `source/chat_crawl_store.py` | Vorgänger (Rekonstruktion aus Suchschnipseln). Überholt, wo `read_conversation` existiert; Verbleib ist Fahrplanpunkt 10. |
| `protokoll.json` (je Quellprojekt) | Der **einzige** geteilte Zustand beider Wege: was liegt vor, auf welchem Stand, was fehlt, wie weit muss ein Export zurückreichen. |
| bis zu 4 Dateien je Chat | Gespräch, `.thinking.json`, `.attachments.json`, `.creations.json` — verknüpft über die Nachrichten-UUID. (Vorgabe 2.2) |
| `tests/` (5 Suiten, 588 Checks) | Selbsttests ohne echten Chatinhalt; `test_wegegleichheit.py` ist der Wächter, dass beide Wege identische Dateien und Protokolle erzeugen. |
| `implementation_doku.md` + `fahrplan.md` | Implementierungsdoku (4 Kapitel: Zusammenhänge, Vorgaben, Skripte, Prüfliste) und Aufgabenliste. |

### 1.3 Was zur Beurteilung wichtig ist

Die tragenden Fakten, alle in der Doku belegt bzw. als beobachtet gekennzeichnet:

- **Der Engpass ist die Transkription, nicht die Suche.** Chattext erreicht ein Dateisystem nur über den Kontoexport (ZIP) oder indem eine Instanz ihn ausschreibt. Daraus die zwei Wege. (Doku 1.2)
- **Der Export ist der inhaltlich reichere Weg**: nur er trägt Denkschritte (9,2 Mio Zeichen), Anhänge mit Inhalt (9,6 Mio) und die Erzeugnisse der KI (4,4 Mio) — zusammen mehr als der Gesprächstext (11,3 Mio). Der Lese-Weg sieht davon nichts; was über ihn hereinkommt, bleibt dauerhaft ärmer und ist nur durch Ersetzen reparierbar. (Doku 1.2, 3.2.1)
- **Die Projektzugehörigkeit existiert nur in claude.ai** (`recent_chats`), Konversationen im Export tragen keinen Projektbezug. Deshalb beginnt jeder Vorgang in einem Chat des Quellprojekts. (Doku 1.6)
- **Der Zeitraumfilter des Exports wirkt auf `created_at`, nicht `updated_at`** — ein weitergelaufener Altchat fehlt in einem kurzen Fenster ganz. Die Fensterrechnung (Vorgabe 2.4) existiert genau deshalb. Projektdateien sind vom Filter ausgenommen; ihr `created_at` ist der Projektbeginn und die Untergrenze jedes Fensters. (Doku 3.1.1, 4.2)
- **Beleglage-Disziplin**: belegt / beobachtet / Community, nie vermischt. Vierzehn Annahmen sind dokumentiert gekippt (Doku 1.7); Kapitel 4 ist die Prüfliste gegen Anthropic-Umbauten.

---

## 2 Umsetzung

### 2.1 Der Ablauf, je Weg (wer macht was)

**Export-Weg** (bevorzugt; Doku 1.5): (0) Bei unklarem Zeitraum ein Sondierungsexport über eine kurze Spanne; `inspect_export.py` listet die Projekte nach Erstellungsdatum. (1) Nutzer fordert den Export ab dem errechneten Datum an, lädt das ZIP. (2) Nutzer holt im Quellprojekt die Chatliste (`recent_chats`-Rohblöcke, per Codeblock kopiert). (3) Claude Code lokal: `list` (Protokoll anlegen/abgleichen, meldet die Fenstergrenze), `convert` (Dateien schreiben, ersetzt Veraltetes samt Aufräumen), `diff`/`report` zur Kontrolle. (4) Protokoll zurück ins Projektwissen des Quellprojekts; der von `convert` ausgegebene Anweisungsblock in die Projektanweisungen des **Ziel**projekts.

**Lese-Weg** (für sofort/einzeln; Doku 1.5, 3.2): Skript + Protokoll in den Chat des Quellprojekts hochladen. Erster Handgriff ist `plan` („Was ist neu?"): schreibt nichts, legt die Lage vor und nennt beide Optionen mit Preis — Exportdatum mit Begründung gegen Sofort-Lesen mit dauerhaftem Verlust. Erst nach Nutzerentscheidung: `map`, `ingest` seitenweise, `export` mit bewiesener Vollständigkeit gegen `total_turns`.

**Bewährt**: Export-Weg produktiv gelaufen (211 Chats Gesamtexport; FreeCAD-Projekt mit 22 Chats über zwei ZIPs zusammengeführt, Stichprobe vom Nutzer inhaltlich abgenommen). Wegegleichheit, Ersetzungshygiene, Waisen-Scan, Fensterrechnung und Tippfehlerprüfung sind getestet (588 Checks, auch unter `-O`).

### 2.2 Noch nicht vollständig geklärte Punkte

**a) Der Kreislauf ist end-to-end noch nie gelaufen.** Der größte offene Punkt, und er steht in keinem Fahrplaneintrag: Das FreeCAD-Archiv liegt noch unter `tests/test_results/` (gitignoriert) statt im Zielprojekt-Repo; das Protokoll wurde noch nie ins Projektwissen zurückgelegt; `plan` wurde noch nie von einer echten Instanz im Quellprojekt ausgeführt; der Anweisungsblock steckt in keiner Projektanweisung. Alles Einzelteile sind geprüft — die Übergabestellen zwischen ihnen (Uploads, Rückwege) nur am Schreibtisch.

**b) Docstring-Review vom 2026-08-09, noch unbeauftragt.** Befund: `chat_read_store.py` erklärt die neuen Protokollfelder (`listed_at`, `created_after`, `project_created_at`) nicht — die hochgeladene Datei ist aber alles, was die Instanz hat. `chat_export_convert.py` dokumentiert nur die halbe Geschichte (Anhänge, Erzeugnisse, Fenster/`--project-created`, `protokoll.json` fehlen). Kein Test wacht über Docstring-Drift — dieselbe Sorte Lücke, die schon zweimal durchrutschte. Vorgeschlagen: (A) Wächtertest, (B) Lücken schließen, (C) README neu.

**c) Fahrplanpunkte**: **7** Zuwachs nachladen statt ersetzen — bleibt `page_token` über Tage gültig? Braucht Beobachtung durch den Nutzer; bis dahin gilt Ersetzen als Ganzes (korrekt, nur teurer). **9** `predecessor`/`successor` automatisch bestimmen — unbelegt, Felder bleiben leer. **10** Verbleib von `chat_crawl_store.py`. **13** README neu (derzeit „Nicht benutzen!"-Hinweis, nennt den Lese-Weg noch „bevorzugt"). **14** `diff` soll die Fenstergrenze auch ohne frische Liste nennen (klein, `window_start()` liegt vor).

**d) In der Doku als offen vermerkt**: ob die Projektzuordnung in die Chatdatei gehört oder nur in den Verzeichnisbaum (3.1.8); ob `tool_use`/`tool_result`-**Ergebnisse** je gebraucht werden (entschieden: nur zählen — aber die Entscheidung ruht auf einem Drei-Monats-Befund).

**e) Beobachtungsabhängig, nicht abschließbar** (Kapitel 4): Zeitraumauswahl des Exports ist undokumentiert — fällt sie weg, kippt das Nachpflegen; `batch-0000` im ZIP-Namen (Stückelung nie beobachtet); Archivmitglieder wechseln (`login_history.json` kam binnen zweier Tage hinzu); Cowork unerreichbar; RAG-Schwelle undokumentiert. Dazu: kein Code-Review auf Korrektheit/Effizienz gelaufen — das bisherige Review war ein reines Dokumentations-Review.

**Kein ungeklärter Punkt betrifft bereits geschriebene Archive**: das Dateiformat (Vorgabe 2.2) und das Protokollschema (2.4) sind von beiden Wegen erfüllt und vom Wegegleichheits-Test gedeckt. Die offenen Punkte betreffen Komfort (7, 14), Aufräumen (10, 13), Dokumentation (b) und den Beweis im Echtbetrieb (a).
