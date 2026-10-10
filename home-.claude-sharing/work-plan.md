# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details stehen in `implementation-doc.md`.

Der Mechanismus ist fertig und im Betrieb, in Deutsch und Englisch. Nummern erledigter Schritte werden nicht neu vergeben; die Lücken davor sind gewollt. Offen sind Schritt 6 und Schritt 7.

Am 15. September 2026 abgeschlossen: die Zweiteilung der Ausschlussliste in einen gemeinsamen und einen rechnerspezifischen Teil (`.stignore-local`), der Ausschluss von `backups/`, `plans/`, `debug/`, `image-cache/` und der toten Scratchpad-Projekte, die Entfernung des nie benutzten Werkzeugordners `tools/` samt Schalter `--add-dir`, und das Ausrollen auf die beteiligten Rechner. Der Abgleich läuft danach fehlerfrei; damit ist der Auslieferungsstand erreicht.

## Schritte

6. **Windows-Pendant** entwickeln (Kap. 3.7). Die Zuordnung der plattformabhängigen Bausteine für die Kapselstelle ist dort bereits festgehalten, ebenso die Grenze: Gekapselt sind Dialoge, Terminalstart, Prozessprüfung, der Ablageort der Syncthing-Konfiguration und der Start des Dauerdienstes — alles andere ist plattformneutral (2.4).

7. **Ausschlussliste einzeln ausliefern und ihre Übernahme mechanisieren.** ⚠ **Noch nicht ausgeführter Plan** (Stand 2026-10-10). Inhaltlich besprochen; die Freigabe zur Ausführung von A–F steht noch aus, offen ist außerdem Punkt 2 unten.

   Anlass: `.stignore` wandert nicht mit (Syncthing-Doku „Ignoring Files“, am 10.10. auf den Rechnern bestätigt), meist ändert sich aber nur sie. Ein Update soll dann ohne Neuinstallation gehen, und die Übernahme ins Repo soll weitgehend mechanisch laufen.

   - **A — `scripts/pack_packages.sh`:** legt zusätzlich `downloads/.stignore` als lose Kopie von `files/.stignore` ab und prüft sie per Prüfsumme wie die Archive. Grund: Auch sie ist eine Kopie, die mit `files/` veraltet (2.7).
   - **B — neues `scripts/release_stignore.sh`** (Name vorgeschlagen): liest die Quelle nur (Standard `~/.claude/.stignore`, abweichender Pfad als Argument); gleich → Ende. Schutzprüfung: erstes Muster `.credentials.json`, direkt danach `#include .stignore-local` und `/.stignore-local`, sonst Abbruch ohne Schreiben. Zeigt hinzugekommene und entfallene Muster (ohne Kommentare); mit `--dry-run` Ende hier. Dann Kopie nach `files/.stignore`, Datumszeile beider READMEs auf heute, Aufruf von `pack_packages.sh`. Keine Prüfung gegen 3.9 (siehe E). Ausgaben deutsch, Kopfkommentar mit `@Claude:`-Abschnitt (2.5).
   - **C — Projekt-Skill `.claude/skills/stignore-release/`** (Name vorgeschlagen, bleibt in `dev`): Vorschau zeigen, Skript ausführen, Tabellenprüfung, Commit auf `dev`, nach Freigabe genau die Dateien dieses Commits per Plumbing nach `master`, Push-Befehl nennen, an das Verteilen auf jeden Rechner erinnern.
   - **D — READMEs (de/en, mit Datumszeile):** im Abschnitt zur Aktualisierung ein kurzer Absatz „nur die Ausschlussliste“: Datei in `downloads/`, `curl`-Befehl auf die Raw-Adresse in `master`, Ziel **beide** Orte `~/.claude/` und `~/.claude-sync-watch/` (sonst bietet ein späteres `install_service.sh` die alte Fassung zur Übernahme an, Vorgabe Ja), danach Ordner in Syncthing neu einlesen, Hinweis zum Knoten (Punkt 2). Der Satz „welches Muster warum, sagt Kapitel 3.9“ wird zu: Begründungen als Kommentare in der Liste, für ältere Muster zusätzlich in 3.9.
   - **E — Implementierungsdoku:** Die Pflicht, jede Begründung in 3.9 nachzutragen, entfällt — 1.3 („Welches Muster warum darin steht, sagt 3.9 …“), 2.3 („stehen mit ihrer Begründung in 3.9“) und die Einleitung von 3.9 („Es trägt genau eine Sache: die Begründung je Muster“) entsprechend. Neue Begründungen schreibt der Entwickler schon während der Konfliktlösung als Kommentar in die Liste; Grund: Nach der Auflösung fehlt der Beleg, eine nachträgliche Begründung ruhte nur auf Annahmen. Vorhandene Tabellenzeilen bleiben. In 2.7 die lose `downloads/.stignore` und `release_stignore.sh` ergänzen, in 2.8 („Erzwingen lässt sich das nicht, prüfen schon …“) den leichten Updateweg samt Grund für die zwei Zielorte.
   - **F — dieser Eintrag;** nach der Ausführung durch das Ergebnis ersetzt.

   Danach als eigener Schritt: die am 10.10. aus `~/.claude/.stignore` übernommene Fassung (neu: `/plugins/known_marketplaces.json`) mit dem Werkzeug ausliefern — Datumszeilen, Pakete, lose Kopie.

   **Punkt 2, offen — braucht der Knoten die Liste?** Befund: ja, aus zwei Gründen. Erstens entsteht dort eigener Fremdbestand (`#recycle`, 3.9). Zweitens ist er in der Sterntopologie (1.2) die zweite Wand: Ein Rechner, dem ein neues Muster noch fehlt, schickt die Datei an den Knoten; ignoriert der Knoten sie, erreicht sie die übrigen Rechner nicht — für `.credentials.json` ist das die Absicherung nach 2.3. Vorschlag zur Entscheidung: am Knoten einmalig eine leere `.stignore-local` anlegen; dann gilt die ausgelieferte Datei dort unverändert, und der Sonderfall „ohne `#include`-Zeile“ aus 2.8 entfällt.

   **Quelldatei:** Der Kommentar „Reasoning per pattern in 3.9 of the doc“ in `.stignore` stimmt nach E nicht mehr; zu ändern in `~/.claude/.stignore` selbst, sonst überschreibt die nächste Übernahme die Korrektur.

## Offen, ohne eigenen Schritt

`history.jsonl` und `paste-cache/` tragen projektübergreifende Inhalte — die Prompt-Historie nennt je Eintrag Prompttext, eingefügten Inhalt und Projektpfad — und lassen sich **nicht** projektweise trennen. Für einen Rechner, der unter `projects/` nur eine Auswahl mitnimmt, gibt es dort nur ganz oder gar nicht; der Preis eines Ausschlusses ist belegt: Die Dokumentation führt `history.jsonl` als Grundlage für den Rückruf per Pfeiltaste, die Suche mit `Ctrl+R` und die Vervollständigung von `!`-Shell-Befehlen, `paste-cache/` als „Contents of large pastes". Beide bleiben deshalb im gemeinsamen Teil und werden, wo nötig, örtlich ausgeschlossen.

Ob `history.jsonl` als einzelne, von jedem Rechner beschriebene und wachsende Datei ein Konfliktmagnet ist, ist weiterhin **nicht gemessen**. Im Betrieb ist bisher nichts aufgefallen.
