# 🚧 zotero-use — Idee, noch kein Skill

*Stand: 2026-08-25*

Claude direkt mit der eigenen Zotero-Bibliothek arbeiten lassen: neue Einträge samt PDF anlegen, gezielt in Metadaten und Volltext suchen, Sammlungen umsortieren — ausgehend vom ursprünglichen Wunsch, Literaturfunde schon während der Recherche in einer zotero-fertigen Form festzuhalten, statt sie nachträglich aus einem Chat-Export herauszuklauben.

**Status:** Nur diese README, keine `SKILL.md`. Architektur und Werkzeugkandidaten sind recherchiert und grob geklärt (Chat vom 22. August 2026); das Thema ist derzeit nicht akut, nichts ist implementiert.

## Architektur

Lesen und Schreiben laufen über verschiedene Wege. **Lesen/Suchen** kann lokal gegen die SQLite-Datenbank der Zotero-Desktop-App laufen, ganz ohne Schlüssel — Zotero erlaubt das ausdrücklich, solange nur gelesen wird ([Direct SQLite Database Access](https://www.zotero.org/support/dev/client_coding/direct_sqlite_database_access)). Die Datenbank selbst enthält nur Metadaten (Titel, Autoren, Tags, Notizen) plus für jeden Anhang einen Schlüssel; die eigentliche PDF-Datei liegt separat im Dateisystem unter `storage/<Schlüssel>/dateiname.pdf` im Zotero-Datenverzeichnis ([The Zotero Data Directory](https://www.zotero.org/support/zotero_data)).

**Schreiben** (neuer Eintrag, PDF-Anhang, Sammlungen ändern) darf laut Zotero **nicht** direkt in die SQLite-Datei gehen — Korruptionsgefahr, Umgehung der eigenen Validierung. Der einzige sichere Weg ist Zoteros **Web-API**, mit einem Web-API-Key aus dem eigenen (kostenlosen) zotero.org-Konto. Bestätigt gegen die offizielle Doku ([Write Requests](https://www.zotero.org/support/dev/web_api/v3/write_requests)):

- Ein Item mehreren Sammlungen zuordnen oder verschieben ist nur das Feld `"collections": ["KEY1", "KEY2", ...]` am Item — Zuordnen heißt Key ergänzen, Verschieben heißt Key tauschen.
- Ein neues Item mit PDF-Anhang entsteht, indem das PDF als Kind-Item mit `"parentItem": "<Eltern-Key>"` im selben Request wie das Eltern-Item mitgeschickt wird.

Dieser Web-API-Key ist ein **Zotero-eigener** Schlüssel, erzeugt im zotero.org-Konto — hat nichts mit einem Anthropic-/Claude-API-Key zu tun.

**Zusätzlicher, key-loser Weg für einen Einzelfall:** Das lokale Connector-Protokoll auf Port 23119 (dasselbe, das die offizielle Zotero-Browser-Erweiterung nutzt) kann Items samt PDF-Anhang ganz ohne Key anlegen — passend für „ich sehe mir gerade eine Quelle an und will sie sofort sichern", aber kein Ersatz für die allgemeine API, da es auf das Übersetzen einer gerade offenen Seite/Datei zugeschnitten ist.

## Account und Hosting — Klärung eines Missverständnisses

Ein zotero.org-Konto ist **kostenlos**. Bezahlt wird nur Zoteros eigener Dateispeicher (300 MB gratis, mehr kostet); eine eigene WebDAV-Ablage (hier: die eigene Nextcloud) ersetzt genau diesen Speicher-Teil, kostenlos. Das Konto selbst bleibt trotzdem nötig — es trägt die Metadaten-Synchronisierung zwischen Rechner und Tablet, nicht die Dateien. Selbst hosten (statt zotero.org zu nutzen) geht technisch (offizieller Sync-Server-Kern plus Community-Repos wie `foxsen/zotero-selfhost`), ist aber unreif — schwerer Stack (MySQL, MinIO, Redis, Elasticsearch, Docker-Compose), erst 16 Commits, Web-Bibliothek laut eigenem TODO noch nicht vorhanden. Für dieses Vorhaben nicht empfohlen: Der Aufwand steht in keinem Verhältnis zum Nutzen gegenüber dem kostenlosen Konto plus eigener Nextcloud, das ohnehin schon läuft.

## Werkzeugkandidaten (Stand der Recherche)

| Kandidat | Einordnung |
| --- | --- |
| [`zotero-cli-cc`](https://github.com/Agents365-ai/zotero-cli-cc) | Bevorzugter Startpunkt. Für Claude Code gebaut (CLI, MCP-Server oder fertiger Claude-Code-Skill), liest lokal ohne Key, `add file ./paper.pdf` legt nachweislich ein Item samt lokaler PDF-Datei an. Ob Sammlungs-Management (Umsortieren/Mehrfachzuordnung) schon als Befehl existiert, ist **nicht bestätigt** — offener Prüfpunkt. |
| [`zotero-mcp`](https://github.com/54yyyu/zotero-mcp) (54yyyu) | MCP-Server, lokal ohne Key oder per Web-API. Stärker bei Annotationen und semantischer Suche (wahlweise mit kostenlosem lokalem Embedding-Modell). Dokumentierte Einschränkung: Manche Schreibfunktionen (Tags, Bibliotheks-Änderungen) laufen bei rein lokal erkannten Bibliotheken schlecht — Workaround laut Projekt: die Web-Bibliothek nutzen, was hier ohnehin zutrifft (zotero.org-Konto vorhanden). |
| [`cookjohn/zotero-mcp`](https://github.com/cookjohn/zotero-mcp) | Andere Bauart: läuft als **Plugin in Zotero selbst**, dadurch volles lokales Lesen/Schreiben (Notizen, Tags, Metadaten) ohne Web-API-Key, weil es mit den Rechten der App selbst arbeitet. Interessante Alternative, wenn der reine Web-API-Weg an Grenzen stößt — noch nicht im Detail geprüft. |
| [`kujenga/zotero-mcp`](https://github.com/kujenga/zotero-mcp) | **Geprüft und ausgeschieden**: reines Lesen (Suche, Metadaten, Volltext), keinerlei Schreiben — trotz einer irreführenden Suchmaschinen-Zusammenfassung, die „full write support" behauptete. Nicht weiter verfolgen. |

## Geltungsbereich

Dies ist das erste konkrete Beispiel für ein „Thema jenseits des Codens" im Sinne von `implementation_doku.md`, Kapitel 8.3 — reine Literatur-/Referenzverwaltung, kein Software-Kontext. Ein späterer Skill dazu muss entsprechend deklariert sein, nicht an einen Coding-Trigger gebunden.

**Zur Verpackung:** Skills laufen inzwischen produktübergreifend — dieselbe `SKILL.md` in Claude Code, Claude Desktop und Claude Cowork (Stand August 2026, [Extend Claude with skills](https://code.claude.com/docs/en/skills)). Ein fertiger Skill hier müsste also nicht auf Claude Code beschränkt bleiben.

## Offen

Probelauf, Klärung des Sammlungs-Managements und die anschließende Werkzeug-Entscheidung stehen als Schritte im [Fahrplan](../fahrplan.md). Nicht auf der Tagesordnung, aber festgehalten:

- Frühere Nebenidee, noch unentschieden: Markdown-Chat-Zusammenfassungen als Zotero-Quelle ablegen, um sie später wiederzufinden. Zotero indiziert `.md`-Anhänge derzeit **nicht** (dokumentierter Fehler, [Zotero-Forum](https://forums.zotero.org/discussion/94637/indexing-of-markdown-plain-text-attachments-with-md-extension)) — Workaround: dieselbe Datei als `.txt` anhängen. Eine „Weiterchatten"-Funktion kennt Zotero nicht; das bliebe reine Konvention (Notiz-/Extra-Feld mit Rückverweis).
