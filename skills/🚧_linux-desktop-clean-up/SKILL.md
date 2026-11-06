---
name: linux-desktop-clean-up
description: Räumt einen Linux-Desktop oder -Laptop (Ubuntu, Kubuntu und ähnliche) auf, ohne Arbeitsdaten zu gefährden — Caches, Paket- und Log-Reste, Papierkorb, Docker-Reste, alte Downloads und Installationsdateien. Misst zuerst, zeigt Füllstand und drei Tabellen, löscht Caches nach festen Regeln und Nutzdaten nur nach Auswahl des Nutzers. Entfernt keine installierte Software. Wird ausschließlich auf ausdrücklichen Aufruf mit /linux-desktop-clean-up angewendet.
license: CC0-1.0
disable-model-invocation: true
---

# Linux-Desktop aufräumen

Dieser Skill läuft lange und in vielen Schritten; sein ganzer Regelteil steht deshalb in dieser einen Datei, damit er eine Verdichtung des Kontexts übersteht. Begründungen und Messbefunde stehen in der README im Ordner dieses Skills — sieh dort nach, wenn der Nutzer nach dem Warum fragt; ihr Dateiname ist nicht verlässlich, sieh im Ordner nach.

## Grundsätze

1. Nichts ist pauschal. Jeder Bereich hat seine eigene Behandlung: **löschen ohne Rückfrage**, **vor dem Löschen fragen** oder **nur melden**.
2. Ohne Entscheidung des Nutzers gelöscht werden nur programmeigene Zwischendateien, die das Programm nicht mehr braucht oder jederzeit vollautomatisch neu erzeugt (Beispiel HTTP-Cache). Was in einem eigenen Arbeitsschritt entsteht, ist Arbeitsdatum, kein Cache (Beispiel: Proxy-Dateien eines Videoschnittprogramms). Zustand, Einstellungen, Datenbanken und Nutzdaten bleiben; Nutzdaten (4.7 bis 4.10) löscht der Skill nur nach Entscheidung des Nutzers.
3. Ein Aufräumbefehl eines Programms wird nur eingesetzt, wenn feststeht, was er entfernt. Sammelbefehle wie `docker system prune` oder `docker image prune -a` sind ausgeschlossen.
4. Installierte Software wird nie entfernt, auch nicht, wenn sie vermutlich nicht mehr gebraucht wird; solche Funde werden gemeldet.
5. Was zu erhalten und was zu löschen ist, formuliert allein der Nutzer. Du übersetzt seine Angaben in einen Auftrag für das Skript und zeigst ihm die Übersetzung vor der Ausführung.
6. Ordnernamen wie Downloads, Videos, Musik, Bilder, Dokumente setzt du nie selbst ein. Du ermittelst sie über die XDG-Benutzerverzeichnisse und übergibst die aufgelösten Pfade.
7. Was eingehängt ist, wird nie gelöscht und nie durchlaufen; Links werden nie verfolgt. Die Skripte setzen das selbst durch.
8. Jeder Lauf endet mit einem Ergebnisbericht: was gelöscht wurde, wie groß die entfernte Datenmenge war (nicht der frei gewordene Platz), was nur gemeldet wurde. Für Docker ohne Größe.

## Wo du läufst und wie die Skripte ausgeführt werden

Du startest grundsätzlich keine Skripte und Befehle auf dem System des Nutzers. Du gibst ihm Befehlsblöcke; er führt sie aus, auch alles mit `sudo`. Die Ergebnisse landen als Dateien in `/tmp`.

**Claude Code:** Die Skripte liegen in `${CLAUDE_SKILL_DIR}`. Frage, ob die Sitzung auf dem Rechner läuft, der aufgeräumt werden soll; wenn nicht, beende den Skill mit diesem Hinweis. Die Ergebnisdateien liest du aus `/tmp`. In der Konsole kann der Nutzer mit `/add-dir /tmp` dafür sorgen, dass du sie ohne Einzelfreigabe liest. In der Erweiterung von VS Code gibt es `/add-dir` nicht; dort geht das Lesen im Berechtigungsmodus „auto“ ohne Rückfrage, sonst gibt der Nutzer jeden Zugriff einzeln frei — sag ihm das zu Beginn, damit die Rückfragen nicht überraschen. Aufträge für das Löschskript schreibst du selbst als Datei nach `/tmp/cleanup-orders/`.

Auf ausdrücklichen Wunsch führst du Skripte ohne `sudo` selbst aus; das bietest du nur an, wenn die Sitzung in der Konsole läuft und der Nutzer sie vorher mit `/cd /tmp` dorthin verlegt hat. Alles mit `sudo` bleibt beim Nutzer.

**claude.ai und Claude Desktop (Chat + Cowork):** Der Platzhalter für den Skill-Ordner wird hier nicht ersetzt. Suche den Ordner dieses Skills in deiner Ausführungsumgebung (`ls` unter `/mnt`), kopiere `analyze.py`, `delete.py` und `journal_stats.py` unverändert nach `/mnt/user-data/outputs` und biete sie als Download an — **nie als Artefakt**, denn ein Artefakt ist eine Abschrift durch dich und kann sich vom Original unterscheiden. Der Nutzer legt sie in einen Ordner seiner Wahl; in den Befehlen steht dieser Ordner statt `${CLAUDE_SKILL_DIR}`. Nach jedem Befehlsblock nennst du die Datei, die er dir hochladen soll. Aufträge für das Löschskript gibst du ebenfalls als Download.

Wurde der Skill nicht ausdrücklich mit `/linux-desktop-clean-up` aufgerufen — etwa weil er auf claude.ai von selbst geladen wurde —, frage zuerst, ob er jetzt angewendet werden soll. Bei Nein endest du.

## Beginn

1. Nenne den Zweck: unnütze Datenansammlungen löschen, auf große Datenmengen hinweisen, um die der Nutzer sich selbst kümmern muss; keine Software entfernen. Gilt für Linux-Desktops und -Laptops, nicht für Server.
2. Erkläre die Arbeitsweise (vorheriger Abschnitt).
3. Sag ihm: Der Vorgang dauert länger, kann umfangreiche Internetrecherchen umfassen und verbraucht viele Token; für ein gutes Rechercheergebnis empfiehlst du das Modell Opus.
4. Lass ihn diese Arbeitsweise bestätigen, bevor es weitergeht.
5. Frage alle Angaben ab, die die Analyse braucht, bevor sie startet: die **Größenschwelle** (eine Zahl für große Einzeldateien, Images, Archive und Medien; Vorgabe 150 MiB) und ob auch **allgemeine Archive** (`.zip`, `.tar.*`, `.7z`, `.rar`) bei den Images erfasst werden sollen. Danach läuft die Analyse ohne Rückfrage.

## Umgebung ermitteln

Gib dem Nutzer diesen Block; er schreibt nach `/tmp/cleanup-env.txt`:

```bash
{ echo "DESKTOP=$XDG_CURRENT_DESKTOP"; echo "HOME=$HOME"; for d in DOWNLOAD VIDEOS MUSIC PICTURES DOCUMENTS; do echo "$d=$(xdg-user-dir $d)"; done; grep -h '"browser.download.dir"' ~/.mozilla/firefox/*/prefs.js 2>/dev/null | sed 's/^/FIREFOX /'; for p in ~/.config/google-chrome/*/Preferences; do [ -f "$p" ] && python3 -c 'import json,sys; print("CHROME", json.load(open(sys.argv[1])).get("download", {}).get("default_directory", ""))' "$p"; done; } | tee /tmp/cleanup-env.txt
```

Download-Ziele, die in Firefox oder Chrome vom Standard abweichen (Zeilen `FIREFOX`, `CHROME`), sind weitere Download-Ordner; jeder geht als eigenes `--downloads` in die Analyse. Erfasst wird nur, was im Home liegt. `xdg-user-dir` liefert für einen nicht eingerichteten Ordner das Home selbst. Ein solcher Eintrag gilt als nicht vorhanden: Den Download-Ordner ohne Eintrag meldest du, Medienordner ohne Eintrag lässt du aus dem Aufruf weg — mit dem Home als Medienordner fiele das ganze Home aus 4.10 heraus.

Gibt es btrfs (das zeigt die Analyse), schlage vor, vor jedem Aufräumschritt einen Snapshot anzulegen und ihn erst zu entfernen, wenn nachweislich alles funktioniert.

## Analyse

```bash
sudo nice -n 19 ionice -c3 python3 -I "${CLAUDE_SKILL_DIR}/analyze.py" --home "$HOME" --downloads "<Download-Ordner>" [--downloads "<Browser-Ziel>" …] --media-dir "<Videos>" --media-dir "<Musik>" --media-dir "<Bilder>" --media-dir "<Dokumente>" --desktop "$XDG_CURRENT_DESKTOP" --threshold <MiB> [--archives]
```

Das Skript zeigt seinen Fortschritt und schreibt `/tmp/cleanup-analysis.json`: `fill_level`, `table1` (Bereiche 4.1 bis 4.14 außer 4.11), `software` (Starter-Einträge, Flatpak, Snap, Anwendungsordner mit Vorfilter), `table3`. Es liest nur. Sag dem Nutzer vorher, dass du dabei auch prüfst, welche Software Cache- und Download-Ordner mitbringt, und dich im Internet über die Programme informierst.

Danach recherchierst du die erfassten Programme (4.11), bevor du Tabellen zeigst. Am Ende der Analyse nennst du kurz die Software, zu der du bei der Bereinigung Vorschläge machen wirst; Firefox, Chrome und VS Code gehören dazu, wenn sie installiert sind.

## Darstellung

Zuerst der **Füllstand** je Dateisystem (belegt, Gesamtgröße, Prozent); gibt es btrfs-Snapshots, ihre Zahl und, wenn bekannt, ihre Belegung. Er zeigt, wo Aufräumen etwas bringt.

Dann drei Tabellen, **je Bereich eine Zeile**. Einzellisten, Histogramme und Auswahllisten kommen erst, wenn der Bereich bearbeitet wird — nie alles gleich nach der Analyse.

- **Tabelle 1 — durch Tests gesichert** (Abschnitte 4.1 bis 4.14 außer 4.11). Spalten: Bereich, Fundort, Größe, Behandlung (ohne Rückfrage / mit Rückfrage / nur melden), braucht root, Programm muss beendet sein, Hinweis zur Sicherung. Für 4.5 zwei Zeilen: Log-Files gesamt, Journal gesamt. Die Zeilen 4.5, 4.7 bis 4.10 und 4.14 tragen den Hinweis, dass Gelöschtes nur über Backup oder Snapshot zurückkommt.
- **Tabelle 2 — durch Recherche belegt** (4.11). Spalten: Programm, Ordner, Größe, Belegstufe mit Quelle, Programm muss beendet sein, Kommentar zur Sicherung (die Maßnahme ist nicht getestet).
- **Tabelle 3 — Statistik**, ohne die Bereiche aus Tabelle 1 und 2:
  - Größe je Verzeichnis: oberste Ebene unter Home und Systemverzeichnissen, tiefere nur, wo das Skript sie liefert; im Home zusätzlich der Anteil, der seit über einem Jahr unverändert ist. Kennzeichne Treffer, die einem der offenen Bereiche entsprechen: Suchindex Baloo, Git-Repositories, Vorschaubilder, Claude-Desktop-Zwischenspeicher und Sandbox-Image, Flatpak/Snap/AppImage/Wine, Python-Umgebungen, Toolchains, Syncthing-Versionen, Duplikate, Migrationsreste.
  - Große Einzeldateien: je offenem Bereich eine Zeile mit Zahl und Summe, Übriges als „Sonstiges“.
  - Reste deinstallierter Programme: Anwendungsordner, die du keiner installierten Software, keinem Desktop- oder Systembestandteil und keinem Werkzeug ohne Starter-Eintrag zuordnen kannst, je mit Begründung. Der Vorfilter des Skripts (`prefilter_match`) ist nur ein Hinweis; das Urteil fällst du.
  - Doppelte Dateien: Zahl der Gruppen und überzählige Menge.
  - Reste abgebrochener Git-Abrufe, Caches ohne zugeordnetes Programm, Absturzabbilder (nur wenn vorhanden), Entwicklungsartefakte (je Projekt: Größe, letzte Änderung der Quellen, Abhängigkeitsliste ja/nein).

## Reihenfolge der Bearbeitung

Schlage vor, Tabelle 1 Schritt für Schritt abzuarbeiten; weise zu Beginn lose darauf hin, dass eine Sicherung oder ein Snapshot sinnvoll sein kann. Reihenfolge: 4.1 bis 4.6, 4.12, 4.13, dann 4.9 → 4.7 → 4.8 → 4.10, zuletzt 4.14 (damit alles, was ein früherer Schritt in den Papierkorb verschoben hat, mit erfasst wird). Danach der Ergebnisbericht; mit ihm endet der eigentliche Lauf. Dann bietest du den Nachgang an, zuerst zu Tabelle 2, dann zu Tabelle 3; der Nutzer kann nach jedem Teil aufhören.

Je Bereich: die Einzelheiten zeigen, die Entscheidung des Nutzers einholen, wo eine nötig ist, den Auftrag schreiben, **Probelauf**, Ergebnis zeigen, nach Bestätigung **echter Lauf**:

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/delete.py" --home "$HOME" --order /tmp/cleanup-orders/<Bereich>.json --dry-run
sudo python3 -I "${CLAUDE_SKILL_DIR}/delete.py" --home "$HOME" --order /tmp/cleanup-orders/<Bereich>.json
```

Jeder Lauf schreibt `/tmp/cleanup-report-<Bereich>.json` (entfernte Anzahl und Datenmenge, Gruppen, übersprungene Pfade mit Grund, ausgeführte Befehle). Übersprungenes zeigst du dem Nutzer mit Grund. Das Skript verweigert unabhängig vom Auftrag: `/`, das Home, Ordner direkt unter `/` oder dem Home, `/boot`, alles außerhalb von Home, `/var`, `/opt`, `/usr/local`, `/srv`, Einhängepunkte und alles, was einen enthält, Links (außer im Papierkorb).

Auftragsformen: `{"area": "<Bereich>", "kind": "rule", "params": {...}}` für Regeln, `{"area": "<Bereich>", "kind": "list", "paths": [...]}` für ausgewählte Pfade (nur 4.7 bis 4.10).

## Die Bereiche

**4.1 apt** — ohne Rückfrage, root. Auftrag `rule`, keine Parameter; führt `apt-get clean` aus. `/var/lib/apt/lists` gehört nicht dazu.

**4.2 Firefox** — ohne Rückfrage, auch bei laufendem Firefox. Regel: Dateien in `cache2/entries` jedes Profils, älter als 3 Tage; `cache2/index` nur, wenn kein Firefox läuft; Ordner nie. Alt-Reste `cache2`/`startupCache` im Profilordner unter `~/.mozilla/firefox`, seit über 30 Tagen unverändert, ganz löschen und im Bericht melden. Übriger Inhalt bleibt. Auftrag `rule`, keine Parameter.

**4.3 Chrome** — ohne Rückfrage. Regel: in jedem Profil unter `~/.cache/google-chrome` Einträge in `Cache/Cache_Data` und `Code Cache/js` älter als 3 Tage; `index` und `index-dir` nur, wenn Chrome nicht läuft; `Code Cache/wasm` und alle Ordner bleiben. Ordner unter `~/.config/google-chrome` werden nicht angefasst.

**4.4 VS Code** — ohne Rückfrage. Regel: Einträge in `Cache/Cache_Data` älter als 3 Tage, Index nur, wenn VS Code nicht läuft; Ordner in `CachedData` außer der installierten Version, älter als 3 Tage; versteckte Nicht-Archive in `CachedExtensionVSIXs`, älter als 3 Tage. `WebStorage/*/CacheStorage` nur melden: große Datenmengen, ob Löschen ratsam ist, ist nicht geklärt.

Die Regeln 4.2 bis 4.4 gelten nur für die klassischen Pfade. Läuft eines dieser Programme als Snap, Flatpak oder anders installiert, behandle es wie Anwendersoftware nach 4.11 (Tabelle 2).

**4.5 Log-Files und Journal** — mit Rückfrage. Starte zuerst die Auswertung:

```bash
sudo nice -n 19 ionice -c3 python3 -I "${CLAUDE_SKILL_DIR}/journal_stats.py" --home "$HOME"
```

Sie schreibt `/tmp/cleanup-journal.json`. Zeige: Gesamtgröße des Journals, das Histogramm (Zeiträume × Stufen, nur so weit das Journal reicht), die stärksten Quellen, die **Spitzen** (Quelle, Tag, Zahl, Median — absteigend nach Überschuss) als Hinweis, Logging-Konfiguration oder Funktion dieser Programme zu untersuchen, und die **auffälligen Log-Gruppen**. Die Ursache zu beheben gehört nicht zum Skill; will der Nutzer es gleich tun, ist das erlaubt, danach fährst du fort. Angebot: alles löschen bis auf die letzten x Tage (Vorgabe 14) — Auftrag `rule` mit `{"days": x}`; das Skript führt `journalctl --vacuum-time` aus und löscht nur archivierte, rotierte Log-Dateien, nie die laufende. Löschen nach Loglevel bietest du nicht an. `MaxLevelStore` nennst du nur als Information: begrenzt künftige Einträge für alle Programme gemeinsam, wirkt nicht auf vorhandene, ändert die Konfiguration.

**4.6 pip-Cache** — immer mit Rückfrage. Zeige Größe und die Einträge ab 50 MiB (Größe, Datum, ohne Namen). Hinweis: Nächste Installationen laden Pakete neu herunter oder bauen sie neu. Bei Zustimmung Auftrag `rule`; führt `pip cache purge` als Eigentümer des Home aus.

**4.12 `__pycache__`** — ohne Rückfrage. Auftrag `rule`; löscht jeden `__pycache__` im Home samt Ordner. Folge: erster Programmstart etwas langsamer.

**4.13 Docker** — nur Docker mit Root-Dienst; Podman und Rootless-Docker nur melden. In dieser Reihenfolge, alles in einem Auftrag `rule`:
1. Build-Cache, der nicht jünger als 2 Tage ist (Nutzer kann die Grenze ändern): `"builder_until_hours": 48`. Sag dazu: Ein frisch benutzter Bauschritt hält seine ganze Kette fest.
2. Beendete Container durchnummeriert vorlegen (Name, Image, beendet seit, Größe); der Nutzer wählt: `"containers": [...]`. Gelöscht wird samt anonymen Volumes; benannte Volumes bleiben.
3. Compose-Projekte durchnummeriert vorlegen (Pfad und Datum der Datei, Projektname, Images, Zustand). Die Images aller Projekte, die der Nutzer behalten will, bilden die Erhalten-Liste `"keep_images": [...]`. Projekte, deren Images Compose nicht bestimmen konnte (`images` ist leer), melden — dann bleiben **alle** Images ohne Container erhalten: lass den Bereich ohne Image-Löschung laufen, indem du alle vorhandenen Images in `keep_images` aufnimmst.
4. Das Skript löscht danach alle Images, die keinem Container mehr zugeordnet und nicht auf der Erhalten-Liste sind. Benannte Volumes nur melden.
Im Bericht keine Größe.

**4.9 Download-Ordner** — mit Auswahl. Gruppen: unter 4 Tagen, 4 bis unter 15 Tagen, ab 15 Tagen, dazu unvollständige Downloads (`.crdownload`, `.part`) als eigene Gruppe; je Gruppe nummeriert, nach Größe absteigend. Alter eines Ordners = Alter seiner jüngsten Datei. Der Nutzer schließt je Gruppe Nummern ein oder aus. Zeige die übersetzte Löschliste (Pfade, Gesamtgröße) zur Bestätigung; Hinweis: wiederherstellbar nur, wenn der Ordner gesichert wird. Auftrag `list`.

**4.7 .deb-Dateien** — mit Auswahl. Nummerierte Liste der Dateien, deren Paket in gleicher oder neuerer Version installiert ist (`status: same_or_newer_installed`); der Nutzer wählt Nummern oder „alles“. Übrige nur melden. Hinweis: Eine ältere Version lässt sich oft nicht wieder herunterladen. Auftrag `list`.

**4.8 Images und Archive** — mit Auswahl. Treffer nach Größe absteigend, nummeriert. Der Nutzer nennt Nummern, die du genauer ansehen sollst — nach Endung, Name, Ordner und Datum, nicht nach Inhalt; dann die Liste mit deiner Einschätzung erneut, der Nutzer entscheidet. Auftrag `list`.

**4.10 Vagabundierende Medien** — mit Auswahl. Das Skript liefert Mediendateien ab der Schwelle außerhalb der Medienordner, je Fundordner die Endungen der Nachbardateien und ob es ein Projekt oder `.git` ist. Du bewertest das Wesen jedes Ordners (Name, Projektordner, Nachbarendungen als Hinweis auf ein Bearbeitungsprojekt, bewusste Ablage) und zeigst nur, was vergessen abgelegt aussieht. Darstellung und Auswahl wie 4.8. Auftrag `list`.

**4.14 Papierkorb** — zuletzt. Frage nach x Tagen (Vorgabe 14, 0 = alles). Auftrag `rule` mit `{"days": x}`, für Papierkörbe auf anderen Dateisystemen zusätzlich `"other_trashes": [...]` aus der Analyse. Maßgeblich ist das Datum des Verschiebens in den Papierkorb; Einträge ohne gültige `.trashinfo` werden nur gemeldet. Hinweis: endgültig weg, ein Backup hilft nur, wenn der Papierkorb gesichert wird.

## Ergebnisbericht

Nach Tabelle 1, vor dem Nachgang, stellst du aus den Berichten der einzelnen Läufe einen Gesamtbericht zusammen: je Bereich, was gelöscht wurde (Anzahl, entfernte Datenmenge; bei Docker die gelöschten Container und Images ohne Größe), was übersprungen wurde und warum, was nur gemeldet wurde. Darunter die Summe der entfernten Datenmenge. Sag ausdrücklich, dass das nicht der frei gewordene Platz ist: Snapshots, Kompression und noch geöffnete Dateien können ihn kleiner machen.

## Tabelle 2: Anwendersoftware (4.11) und Nachgang

Grundlage sind die erfassten Programme in `software.desktop.included` (die Regeln dafür setzt das Skript um) und die Ordner unter `~/.cache`, die du einem Eigentümer ohne Starter-Eintrag zuordnen kannst (Erweiterung, Kommandozeilenwerkzeug, Bibliothek). Firefox, Chrome und VS Code auf den klassischen Pfaden recherchierst du nicht.

Je Programm suchst du in der Dokumentation genau zwei Dinge:
1. **Cache- und Download-Ordner.** Als Cache gilt ein Ordner nur, wenn die Dokumentation belegt, dass das Programm die Daten darin jederzeit vollautomatisch wiederherstellt und ihr Fehlen bis auf Zeitverlust nichts ändert — wie die Dokumentation ihn nennt, zählt nicht; Nachsehen im Dateisystem allein genügt nicht. Geht nicht hervor, dass das Programm den Verlust im laufenden Betrieb verträgt, löschst du erst, wenn es beendet ist, und forderst den Nutzer dazu auf.
2. **Ordner mit Eingangsdaten** datenverarbeitender Programme. Treffer darin schließt du still aus den Suchläufen 4.8, 4.10 und den großen Einzeldateien und Duplikaten in Tabelle 3 aus — ohne Meldung. Nicht still ausgeschlossen wird bei 4.7, 4.9 und bei der Größe je Verzeichnis.

**Belegstufe** je Zeile: **hoch** — die offizielle Dokumentation sagt es ausdrücklich; **mittel** — nur Entwicklerforum, Issue-Tracker oder Distributions-Wiki. Nur Drittquellen oder Rückschluss gilt als **kein klarer Befund**: Dann nennst du die Daten des Programms nirgends und schließt sie von jedem Löschvorschlag aus (die Größe je Verzeichnis zählt sie trotzdem mit). Ordner unter `~/.cache` ohne zuordenbaren Eigentümer kommen nach Tabelle 3. **Nachgang zu Tabelle 2** (nach dem Ergebnisbericht): Wiederhole die Stellen aus Tabelle 2 und sag dem Nutzer, dass du für diese Posten keine getesteten und belegten Erfahrungen besitzt. Biete an, alle oder einen Teil davon gemeinsam weiter zu klären — Recherchen in der Dokumentation, gemeinsam Strategien zum Aufräumen entwickeln und ausführen. Geh dabei vorsichtig vor und erinnere den Nutzer vor jedem Löschen, was tatsächlich belegt und was Vermutung ist, damit er abschätzen kann, ob wirklich gelöscht werden soll. Das Löschskript nimmt für Tabelle 2 keinen Auftrag an; gelöscht wird im Nachgang wie bei einer zusätzlich angeforderten Suche.

## Nachgang zu Tabelle 3

Nach dem Nachgang zu Tabelle 2, oder wenn der Nutzer ihn auslässt, biete an, die Befunde gemeinsam zu erforschen: Inhalte genauer ansehen, Internetrecherche. Sag dazu: Dafür gibt es keine vorgefertigten Lösungen; sie werden erst erarbeitet, sollten gut belegt sein und sind ungetestet — eine vollständige Sicherung oder ein Snapshot ist dringend zu empfehlen. Vorher räumst du dort nichts auf.

Bittet der Nutzer zusätzlich um eine Suche nach weiteren Dateien, gilt keine der Regeln dieses Skills; die Randbedingungen handelst du mit ihm aus. Für solche Suchen gilt auch der stille Ausschluss nicht.
