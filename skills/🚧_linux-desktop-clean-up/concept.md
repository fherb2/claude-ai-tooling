# Plan: Clean-up-Skill für Linux-Desktops

Stand: 2026-11-05. Das Dokument hält nur Festlegungen fest. Implementierungssprache (Bash oder Python) ist nicht festgelegt.

## 1 Zweck und Geltung

- Der Skill löscht nur unnütze Datenansammlungen und weist den Nutzer auf Datenmengen hin, um die er sich selbst kümmern muss.
- Er entfernt keine installierte Software, auch nicht, wenn sie vermutlich nicht mehr gebraucht wird. Solche Funde werden nur gemeldet.
- Geltungsbereich: Linux-Desktops und -Laptops (Ubuntu, Kubuntu und ähnliche), keine Server. Er geht nicht vom Istzustand eines einzelnen Rechners aus, sondern misst den Zustand jedes Mal neu.

## 2 Grundsätze

1. Nichts ist pauschal. Für jeden Bereich ist einzeln festgelegt, wie der Skill damit umgeht.
2. Drei Arten der Behandlung je Bereich: **löschen ohne Rückfrage**, **vor dem Löschen fragen**, **nur vorschlagen oder melden**.
3. Ein Aufräumbefehl eines Programms wird nur eingesetzt, wenn feststeht, was er genau entfernt. Sammelbefehle wie `docker system prune` sind nicht pauschal erlaubt.
4. Ohne Entscheidung des Nutzers gelöscht werden nur programmeigene Zwischendateien, die rein aus Performance-Gründen angelegt werden und die das Programm entweder nicht mehr benötigt oder jederzeit on-the-fly und vollautomatisch neu erzeugt, wenn sie fehlen. Zustand, Einstellungen, Datenbanken und Nutzdaten bleiben. Zwei Extremfälle grenzen das ab:
   - Dazu gehört ein HTTP-Cache: Er hält nur eine Kopie einer bereits heruntergeladenen Datei vor, damit ein erneuter, langsamer Zugriff ins Internet entfällt.
   - Nicht dazu gehören die Proxy-Dateien eines Videoschnittprogramms: datenreduzierte Fassungen der Quellvideos, mit denen die Vorschau während der Bearbeitung mit wenig Ressourcen rechnet. Sie sind keine bloßen Kopien, sondern veränderte Repräsentanten der eigentlichen Daten, entstehen in einem eigenen Arbeitsschritt und werden nicht on-the-fly neu erzeugt, wenn sie fehlen. Das sind Arbeitsdaten, kein Cache.

   Nutzdaten wie Downloads, Installationsdateien, Images und Medien (Abschnitte 4.7 bis 4.10) löscht der Skill nur nach Entscheidung des Nutzers.
5. Jeder Lauf endet mit einem Ergebnisbericht: was gelöscht wurde, wie groß die entfernte Datenmenge war (nicht der frei gewordene Platz), was nur gemeldet wurde.
6. Nutzereingaben: Was zu erhalten und was zu löschen ist, formuliert allein der Nutzer. Die Instanz bewertet die Angaben und überführt sie in eine schematisch richtige Zuordnung, die dem Skript oder Befehl übergeben wird. Das gilt für alle Nutzereingaben im Skill.
7. Ordnernamen: Sie werden bei der Abarbeitung an die Sprache des Systems und des Desktops des Nutzers angepasst. Namen wie `Downloads`, `Videos`, `Musik`, `Bilder` oder `Dokumente` stehen in keiner Zeichenkette eines Skripts. Die Instanz ermittelt den Pfad auf dem Rechner (XDG-Benutzerverzeichnisse: `~/.config/user-dirs.dirs`, `xdg-user-dir`), prüft im Home, dass der Ordner existiert, und startet erst dann das Skript oder den Agenten. Sie übergibt den aufgelösten Pfad als Parameter. Messbefund: Auf diesem Rechner heißen `Downloads` und `Videos` englisch, `Musik`, `Bilder`, `Dokumente`, `Schreibtisch` deutsch.

## 3 Ablauf des Skills

### 3.1 Beginn

1. Der Skill wird mitunter beim Nachdenken von selbst geladen. Er fragt deshalb zuerst, ob er jetzt überhaupt angewendet werden soll. Bei "nein" endet er. Bei "ja" geht es weiter.
2. Er nennt, wofür er vorgesehen ist (Abschnitt 1).
3. Er erklärt die Arbeitsweise: Grundsätzlich startet der Skill selbst keine Skripte oder Befehle auf dem System; die Ausnahme regelt Schritt 5. Es gibt zwei Wege, beide mit der Ausführung durch den Nutzer (damit sind auch root-Zugriffe unproblematisch):
   - Der Skill übergibt dem Nutzer einen Codeblock. Der Nutzer führt ihn aus. Dabei entsteht eine Datei im Ordner `/tmp`, die der Skill liest. Dafür braucht er Zugriff auf `/tmp`.
   - Der Skill erstellt ein Skript in `/tmp` oder nutzt ein im Skill vorhandenes und übergibt dem Nutzer den Aufruf. Die Ergebnisse landen wieder in `/tmp` und werden vom Skill ausgewertet.
4. Der Skill ermittelt, wo er läuft:
   - In der Claude-App (claude.ai): Zu jedem Block und jedem Skript sagt er dem Nutzer immer, welche Datei danach hochzuladen ist.
   - Nicht in der Claude-App (Claude Code): Er fragt, ob er auf dem betreffenden System gestartet wurde. Wenn ja und der Nutzer nur will, dass Claude Code die Ergebnisse in `/tmp` liest, gibt er ihm den Befehl `/add-dir /tmp` vor, nicht `/cd`. Dann kann er alle Ergebnisdateien auswerten, ohne dass der Nutzer jedes Mal den Zugriff außerhalb des Arbeitsverzeichnisses freigeben muss. Das gilt für Claude Code in der Konsole. In der Erweiterung von VS Code gibt es `/add-dir` nicht (vom Nutzer geprüft); wie der Skill dort die Ergebnisse liest, ist offen (`work-plan.md`, Schritt 10).
5. Auf ausdrücklichen Wunsch des Nutzers führt der Skill Skripte selbst aus. Diese Variante bietet er nur an, wenn er auf demselben System läuft. Voraussetzung ist, dass der Nutzer die Session vorher mit `/cd /tmp` in diesen Ordner verlegt hat. Root-Zugriffe delegiert er trotzdem an den Nutzer. Eine Prüfung der Claude-Code-Version entfällt, `/cd` gibt es seit mehreren Monaten. `/cd` funktioniert in Claude Code in der Konsole, in der Erweiterung von VS Code nicht (beides vom Nutzer geprüft). Dort ist diese Variante also nicht möglich.
6. Er teilt dem Nutzer mit: Der Vorgang dauert länger, kann umfangreiche Internetrecherchen umfassen und verbraucht zahlreiche Token. Für ein gutes Rechercheergebnis empfiehlt er das Modell Opus.
7. Der Nutzer bestätigt diese Arbeitsweise, bevor es weitergeht.

### 3.2 Snapshots

Gleich zu Beginn der Untersuchung prüft der Skill, ob das System Snapshots anbietet (zum Beispiel btrfs). Wenn ja, schlägt er dem Nutzer vor, diesen Mechanismus in den einzelnen Aufräumschritten jeweils zu nutzen. Die Snapshots werden erst später entfernt, wenn nachweislich alles funktioniert.

### 3.3 Erste Aufgabe: allgemeine Untersuchung

Der Skill untersucht das System auf Stellen, die sich aufräumen lassen:

- bekannte Stellen: solche, für die der Skill konkrete Lösungsbeschreibungen und Löschskripte enthält (Abschnitt 4),
- Cache- und Download-Ordner der Anwendersoftware, die die Recherche zur Laufzeit belegt (Abschnitt 4.11),
- zusätzlich systemweite Statistiken.

Das Ergebnis übergibt er in drei Tabellen:

| Tabelle | Inhalt |
|---|---|
| 1 | Bekannte, im Skill beschriebene und durch Tests gesicherte Stellen (Abschnitt 4 außer den Rechercheergebnissen aus 4.11): was gefunden wurde und was sich mit dem Skill direkt und in kurzer Zeit säubern lässt |
| 2 | Durch Recherche belegte Stellen (Abschnitt 4.11), je Zeile mit der Einschätzung, wie sicher der Beleg ist |
| 3 | Auswertung der Statistiken: Größe je Verzeichnis und große Einzeldateien außerhalb der bekannten Bereiche, wo möglicherweise weitere Aufräummöglichkeiten bestehen |

Vor den Tabellen nennt der Skill den Füllstand je eingehängtem Dateisystem (belegt, Gesamtgröße, Prozent). Gibt es btrfs-Snapshots, nennt er ihre Zahl und, wenn die btrfs-Quotas aktiv sind, ihre Belegung; sonst entfällt diese Angabe. Der Füllstand zeigt, auf welchem Dateisystem Aufräumen überhaupt etwas bringt.

Aufbau der Tabellen:

- Die Analyse durchläuft das Dateisystem nur ein einziges Mal und erfasst dabei alles, was die Tabellen brauchen.
- Das Analyseskript liefert maschinenlesbare Daten. Die Tabellen baut die Instanz daraus; in Tabelle 2 ergänzt sie die Ergebnisse der Recherche.
- Jede Tabelle zeigt nur eine Zusammenfassung je Bereich, eine Zeile je Bereich. Die Einzelheiten (Einzellisten, Histogramm, nummerierte Auswahllisten) kommen erst, wenn der Bereich bearbeitet wird. Nach der Datenerfassung wird nicht alles sofort präsentiert.
- Spalten von Tabelle 1: Bereich (mit Abschnitt in diesem Dokument), Fundort, Größe, Behandlung (ohne Rückfrage / mit Rückfrage / nur melden), braucht root, Programm muss beendet sein, Hinweis zur Sicherung.
- Spalten von Tabelle 2: Programm, Ordner, Größe, Belegstufe mit Quelle, Programm muss beendet sein, Kommentar zur Sicherung.
- Inhalt von Tabelle 3 (ermittelt per Test, `tests/table3_probe.py`; jeweils ohne die Bereiche aus Abschnitt 4):
  - Größe je Verzeichnis: die oberste Ebene unter dem Home und den Systemverzeichnissen mit Größe. Tiefere Ebenen nur, wenn ein Unterordner den Elternordner nicht bloß wiederholt. Für Verzeichnisse im Home eine zusätzliche Spalte: Anteil der Daten, die seit über einem Jahr unverändert sind (für Systemverzeichnisse nicht, weil Software Änderungszeiten oft festsetzt). Treffer, die einem Bereich aus Abschnitt 5 entsprechen, sind gekennzeichnet.
  - Große Einzeldateien ab 150 MiB, soweit 4.7, 4.8 und 4.10 sie nicht abdecken: zusammengefasst je Bereich aus Abschnitt 5 eine Zeile mit Zahl und Summe, alles Übrige als eine Zeile "Sonstiges". Die Einzeldateien zeigt der Skill erst bei der Bearbeitung.
  - Reste deinstallierter Programme: Das Skript liefert die Anwendungsordner im Home (`~/.config`, `~/.local/share`, `~/.cache`, `~/.var/app` und Punkt-Ordner im Home) mit Größe und letzter Änderung, ohne die Bereiche aus Abschnitt 4. Die Instanz ordnet sie der erfassten Anwendersoftware (4.11), Desktop- und Systembestandteilen sowie Werkzeugen ohne Starter-Eintrag zu und zeigt nur die Ordner ohne Zuordnung, je mit Begründung. Ein reiner Namensabgleich taugt nur als Vorfilter (im Test zwei Drittel Fehlalarme). Gelöscht wird nur nach Entscheidung des Nutzers: Ein Rest kann Einstellungen enthalten, die bei einer Neuinstallation wieder gebraucht werden.
  - Doppelte Dateien ab 1 MiB, nur Nutzerdaten im Home: ohne Anwendungsordner, ohne `.git`-Ordner, ohne Entwicklungsartefakte und ohne Systemverzeichnisse (dort sind Kopien programmintern oder, bei Git LFS, systembedingt). Erst nach Größe gruppiert, dann per Inhalt verglichen. In der Tabelle Zahl der Gruppen und überzählige Menge; bei der Bearbeitung je Gruppe alle Fundorte, der Nutzer entscheidet, welche Kopie bleibt.
  - Reste abgebrochener Git-Abrufe (`tmp_pack_*`, `tmp_idx_*`, `tmp_obj_*` innerhalb von `.git`): Zahl und Größe. Die Behandlung folgt mit dem Bereich "Git-Repositories" aus Abschnitt 5.
  - Absturzabbilder: nur `/var/crash` und der Ordner von systemd-coredump; eine Zeile nur, wenn dort etwas liegt. Die Behandlung wird recherchiert, wenn ein Rechner dort etwas hat. Eine Suche nach Dateien namens `core` entfällt (im Test nur Fehltreffer).
  - Entwicklungsartefakte (`.venv` und andere Ordner mit `pyvenv.cfg`, `node_modules`, `build`, `dist`, `target`, Werkzeug-Caches) nur in Projekten im Home, erkannt an einem Projektkennzeichen (`.git`, `pyproject.toml`, `package.json`, `Cargo.toml` u. a.); ohne Anwendungsordner, Punkt-Ordner im Home und Systemverzeichnisse (dort sind es meist Teile installierter Software). Je Projekt eine Zeile: Größe der Artefakte, letzte Änderung an den Quelldateien, ob eine Abhängigkeitsliste vorhanden ist. `__pycache__` gehört nicht hierher, sondern zu 4.12.
  - Verworfen nach dem Test: Zuwachs in den letzten Tagen (ein einzelner Lauf misst nur geänderte, nicht gewachsene Daten) und Datenmenge je Dateiart (keine neue Handlungsmöglichkeit gegenüber Ort und Größe).

Ausgabe während der Analyse: Dauern einzelne Schritte lange (der Lüfter kann dabei hochdrehen), gibt das Analyseskript, das der Nutzer ausführt, laufend aus, welchen Analyseschritt es gerade ausführt.

Software-Erfassung: Zu Beginn der Analyse erfasst der Skill auch die Anwendersoftware des Nutzers (Abschnitt 4.11). Dem Nutzer sagt er dazu nur, dass er prüft, welche Software Cache- und Download-Ordner mitbringt, und dass er sich im Internet über die Details der Programme informiert. Am Ende der Analyse nennt er dem Nutzer kurz die Software, zu der er bei der Bereinigung noch Vorschläge machen wird. Firefox, Chrome und VS Code stehen in dieser Liste, falls sie installiert sind. Die durch Recherche belegten Ordner dieser Software stehen in Tabelle 2.

### 3.4 Zweite Aufgabe: Tabelle 1

Der Skill schlägt vor, zuerst Tabelle 1 Schritt für Schritt gemeinsam mit dem Nutzer abzuarbeiten und dabei aufzuräumen. Zu Beginn weist er lose darauf hin, dass eine vorherige Sicherung (oder ein Snapshot) sinnvoll sein kann. Der Hinweis ist nicht dringend formuliert, weil die Maßnahmen in Tabelle 1 bereits belegt und getestet sind.

Die Zeilen für Log-Files und Journal (4.5) sowie für Nutzdaten (4.7 bis 4.10) tragen den Hinweis, dass Gelöschtes nur über ein Backup oder einen Snapshot zurückkommt. Getestet ist dort der Löschvorgang; ob eine Datei noch gebraucht wird, entscheidet der Nutzer.

### 3.5 Dritte Aufgabe: Tabelle 2

Ist Tabelle 1 erledigt, schlägt der Skill vor, Tabelle 2 ebenso Schritt für Schritt abzuarbeiten. Dabei gilt:

- Jede Zeile nennt die Einschätzung des Belegs in zwei Stufen:
  - **hoch**: Die offizielle Dokumentation des Programms sagt es ausdrücklich.
  - **mittel**: Es steht nur in einem Entwicklerforum, im Issue-Tracker des Programms oder in einem Distributions-Wiki.
- Ein Ordner, der nur durch Drittquellen oder durch Rückschluss aus mehreren Hinweisen belegt ist, gilt als "kein klarer Befund" (Abschnitt 4.11) und steht in keiner Tabelle.
- Ein Kommentar in der Zeile darf darauf hinweisen, dass ein Backup oder Snapshot angebracht sein kann, weil die Maßnahme nicht getestet ist.
- Für das Löschen gelten die Regeln aus 4.11, insbesondere die Aufforderung, das Programm vorher zu beenden.

### 3.6 Vierte Aufgabe: Tabelle 3

Ist Tabelle 2 erledigt, bietet der Skill an, den Rest gemeinsam zu erforschen: Inhalte genauer ansehen, Internetrecherche hinzuziehen. Dabei gilt:

- Der Skill sagt, dass er dafür keine vorgefertigten Anweisungen und Lösungen hat. Sie werden erst erarbeitet.
- Er führt den Nutzer durch die einzelnen Befunde und erarbeitet mit ihm Schritt für Schritt, ob es dort überhaupt etwas zu tun gibt und wie man es angehen würde.
- Vorher wird dort nichts selbständig aufgeräumt.
- Der Skill weist den Nutzer darauf hin, dass die erarbeiteten Maßnahmen möglichst gut belegt sein sollten, damit kein Unfall passiert.
- Er weist darauf hin, dass die hier erarbeiteten Aufräumarbeiten völlig ungetestet sein werden und deshalb eine vollständige Sicherung beziehungsweise der Snapshot-Mechanismus (Abschnitt 3.2) dringend zu empfehlen ist.

### 3.7 Zusätzlich angeforderte Suchen

Bittet der Nutzer den Skill zusätzlich, nach weiteren Dateien zu suchen, und beschreibt er, welche er meint, gilt keine der bisherigen Regeln dieses Plans. Das ist kein Automatismus des Skills, sondern eine zusätzlich angeforderte Aufgabe. Ihre Randbedingungen beruhen nicht auf den Festlegungen des Skills, sondern werden im Einzelnen mit dem Nutzer ausgehandelt.

## 4 Festgelegte Bereiche

### 4.1 apt

| Was | Behandlung |
|---|---|
| Heruntergeladene Pakete im Paketcache (`apt-get clean`) | löschen ohne Rückfrage; braucht root-Rechte |

Nur `apt-get clean`. `/var/lib/apt/lists` gehört nicht dazu.

### 4.2 Firefox

`<Profil>`: jedes Profilverzeichnis des Nutzers mit Inhalt, sowohl unter `~/.cache/mozilla/firefox/` (Cache-Ordner) als auch unter `~/.mozilla/firefox/` (Profilordner), nicht nur das aktive. Leere Verzeichnisse werden übersprungen.

| Was | Behandlung |
|---|---|
| `~/.cache/mozilla/firefox/<Profil>/cache2/entries`: Dateien, deren Anlege- und Änderungszeit älter als 3 Tage ist | löschen ohne Rückfrage, auch wenn Firefox läuft |
| `cache2/index` jedes Profils | läuft irgendein Firefox: alle stehen lassen; läuft keiner: mitlöschen |
| Verzeichnisse `cache2`, `entries`, `doomed` | nie löschen, nur Dateien darin |
| Übriger Inhalt von `~/.cache/mozilla/firefox/<Profil>/` (`remote-settings`, `startupCache`, `safebrowsing`, `personality-provider`, `ads-client.sqlite*`, `thumbnails`, `settings`, `activity-stream.*.json`) | nicht anfassen |
| `cache2` oder `startupCache` unter `~/.mozilla/firefox/<Profil>/` (Profilordner, nicht `~/.cache`), seit mehr als 30 Tagen unverändert | ganz löschen einschließlich Ordner, ohne Rückfrage, im Ergebnis melden; auch bei laufendem Firefox |

Die Schwelle von 30 Tagen für "lange unverändert" ist bestätigt.

Diese Regeln gelten nur für die getesteten klassischen Pfade. Andere Installationswege (Snap, Flatpak und andere) behandelt Abschnitt 4.11.

### 4.3 Chrome

`<Profil>`: jedes Verzeichnis unter `~/.cache/google-chrome/` (zum Beispiel `Default`, `System Profile`), nicht nur das aktivste. Verzeichnisse ohne Cache (leer oder nicht vorhanden) werden übersprungen.

| Was | Behandlung |
|---|---|
| `~/.cache/google-chrome/<Profil>/Cache/Cache_Data`: Entry-Dateien (Name aus 16 Hexzeichen, `_` und Rest), deren Anlege- und Änderungszeit älter als 3 Tage ist | löschen ohne Rückfrage, auch wenn Chrome läuft |
| `Cache_Data/index` und Ordner `Cache_Data/index-dir` | läuft Chrome: stehen lassen; läuft er nicht: mitlöschen |
| `~/.cache/google-chrome/<Profil>/Code Cache/js`: Entry-Dateien (gleiches Namensmuster), deren Anlege- und Änderungszeit älter als 3 Tage ist | löschen ohne Rückfrage, auch wenn Chrome läuft |
| `Code Cache/js/index` und Ordner `Code Cache/js/index-dir` | läuft Chrome: stehen lassen; läuft er nicht: mitlöschen |
| `Code Cache/wasm` | nicht getestet, nicht anfassen |

Die Ordner `Cache`, `Cache_Data`, `Code Cache`, `js` und `wasm` selbst werden nie gelöscht.

Noch zu ermitteln: Behandlung weiterer Chrome-Ordner (`~/.config/google-chrome`: `component_crx_cache`, `GPUCache` u. a. waren nur für das Backup als Cache eingestuft).

Diese Regeln gelten nur für die getesteten klassischen Pfade. Andere Installationswege (Snap, Flatpak und andere, auch Chromium) behandelt Abschnitt 4.11.

### 4.4 VS Code

| Was | Behandlung |
|---|---|
| `~/.config/Code/WebStorage/*/CacheStorage` | nicht löschen. Der Skill weist nur darauf hin, dass dort große Datenmengen liegen (hier bis zu 6,8 GiB je Ordner) und dass nicht eindeutig ist, ob eine Löschung ratsam ist. |
| `~/.config/Code/Cache/Cache_Data`: Entry-Dateien (16 Hexzeichen, `_`, Rest), deren Anlege- und Änderungszeit älter als 3 Tage ist | löschen ohne Rückfrage, auch wenn VS Code läuft |
| `Cache_Data/index` und Ordner `Cache_Data/index-dir` | läuft VS Code: stehen lassen; läuft er nicht: mitlöschen |
| Ordner in `~/.config/Code/CachedData` außer der installierten Version (Commit aus `/usr/share/code/resources/app/product.json`), älter als 3 Tage | löschen ohne Rückfrage, auch wenn VS Code läuft |
| `~/.config/Code/CachedExtensionVSIXs`: Pakete mit Namen nach Erweiterung und Version | nicht anfassen; VS Code hält darin selbst höchstens 20 Pakete, je Erweiterung die neueste Version |
| `~/.config/Code/CachedExtensionVSIXs`: versteckte Dateien (Name beginnt mit `.`, danach UUID), die kein gültiges Archiv sind und älter als 3 Tage | löschen ohne Rückfrage, auch wenn VS Code läuft |

Diese Regeln gelten nur für die getesteten klassischen Pfade. Andere Installationswege (Snap, Flatpak und andere) behandelt Abschnitt 4.11.

### 4.5 Log-Files und System-Journal

Dieser Schritt umfasst die Log-Files und das System-Journal. Im Skill heißt er so.

**Analyse (Teil des Analyseskripts, Abschnitt 3.3)**

1. Das Skript gibt während der Analyse laufend aus, welchen Schritt es gerade ausführt.
2. Es erzeugt Multiprocessing-Worker, jeden für eine Datei (Journal-Dateien und Log-Files). Es sind höchstens 4 Worker, bei weniger Kernen entsprechend weniger, und sie laufen mit niedriger Priorität (`nice`, `ionice`).
3. Journal-Histogramm als Tabelle:
   - Es nennt zuerst die aktuelle Gesamtgröße des Journals. Auf die Zahl der Dateien kommt es nicht an.
   - Zeilen sind Zeiträume (Bins), Spalten sind die Loglevel 0 bis 7. Einträge ohne Stufe oder außerhalb von 0 bis 7 stehen in einer eigenen Spalte. Jeder Eintrag zählt in genau einem Bin.
   - Die letzten 14 Tage sind je ein Tag breit. Danach folgen: 2 Wochen (Tag 15 bis 28), 4 Wochen (Tag 29 bis 56), 12 Wochen (Tag 57 bis 140), Rest bis 365 Tage, älter.
   - Ein Bin wird nur so weit gerechnet, wie das Journal zeitlich reicht.
4. Im selben Durchlauf werden je Eintrag Zeit, Loglevel und Quelle (Programm oder Dienst) gezählt. Meldungstexte werden nicht gelesen.
5. Auffälligkeiten: Spitzen einzelner Programme oder Dienste. Eine Spitze liegt vor, wenn eine Quelle an einem Tag mindestens 10.000 Einträge meldet und mehr als das Zehnfache ihres Median-Tageswerts. Der Median wird nur über Tage mit Einträgen gebildet. Der Skill nennt die Spitzen dem Nutzer absteigend nach der Zahl der Einträge über dem Median, als Hinweis, die Logging-Konfiguration oder die Funktion dieser Programme zu untersuchen.
6. Die Ursache selbst zu beheben, gehört nicht zum Skill. Will der Nutzer das beim Abarbeiten gleich erledigen, ist das erlaubt. Danach fährt der Skill fort.
7. Log-Files allgemein: Es geht nicht nur um das Journal, sondern um alle Log-Files, die in kurzer Zeit auffällig groß geworden sind.
   - Die Analyse wertet nur Zeit- und Datumsangaben sowie Größen der einzelnen Log-Files der verschiedenen Dienste und Programme aus, nicht den Inhalt.
   - Als Log-Files gelten alle Dateien unter `/var/log` rekursiv sowie im Home nur in den Anwendungsordnern `~/.config`, `~/.local/share`, `~/.cache` und `~/.var`: Dateien mit `*.log*` im Namen und Ordner namens `log` oder `logs`. Projekt- und Quellcode-Ordner bleiben draußen; der Test zu Tabelle 3 hat mit einer Regel über das ganze Home Git-Reflogs (`.git/logs`) und Quellcode-Ordner getroffen.
   - Auffällig ist ein stark ungleichmäßiger Verlauf mit sehr großen Datenmengen in wenigen Tagen oder Stunden. Konkret: Aufeinanderfolgende, rotierte Dateien eines Programms haben zusammen mindestens 100 MiB, und mehr als die Hälfte davon liegt in einem Zeitfenster von höchstens zwei Tagen (nach Änderungszeit). Zusätzlich gilt jede Einzeldatei ab 50 MiB als auffällig.
   - Die Ergebnisse stehen in einer eigenen Liste für alle Log-File-Analysen. Den Ursachen geht der Nutzer nach.

**Angebote des Skills**

- Alles löschen bis auf die letzten x Tage. x ist standardmäßig 14, der Nutzer kann den Wert ändern. Der Skill wendet das auf die jeweils passenden Dateien an:
  - Journal: `journalctl --vacuum-time=<x>`. Laut Manpage entfernt es nur archivierte Journal-Dateien und braucht root-Rechte.
  - Log-Files außerhalb des Journals: nur archivierte, rotierte Dateien (Name mit Ziffer, Datum, `.gz` oder `.old`), nach Dateidatum, nie die laufende Datei. Für Dateien unter `/var/log` braucht das root-Rechte.
- Löschen nach Loglevel (info, debug und darunter) entfällt als Angebot. Beim Journal ist es technisch nicht möglich: `--vacuum-*` kennt nur Alter, Größe und Dateianzahl, keine Stufe (Manpage). Hinweis für den Nutzer, nicht Angebot: `MaxLevelStore` in `journald.conf` begrenzt künftige Einträge auf eine Stufe, wirkt nicht auf vorhandene Einträge und ändert die Konfiguration.

**Messbefunde, auf denen das beruht (dieser Rechner)**

- Im Journal kommen die Stufen 3 bis 7 vor, kein Eintrag ohne Stufe.
- 97,8 % der Info-Einträge stammen von einer Quelle, dem urbackup-Client, und fallen auf drei Tage. Dieselben Meldungen stehen dreifach: im Journal, in dessen eigener Logdatei und in `/var/log/syslog` (550 MiB; per Zeilenzählung). Das Aufräumen eines Orts hilft den anderen nicht.

**Hinweise**

- Die Schwellen (10.000 Einträge, Faktor 10, 100 MiB, 50 MiB, zwei Tage, x = 14) sind Vorgaben ohne Messbelege über diesen Rechner hinaus und können nachjustiert werden.
- `MaxLevelStore` wird nur als Information genannt, nicht als Angebot. Der Wert gilt für alle Programme gemeinsam und würde auch Info-Meldungen anderer Dienste verwerfen.
- Wie Programme Stufen wie trace auf die Journal-Stufen abbilden, ist nicht geprüft. Das Handbuch kennt nur die Werte 0 bis 7. Der Skill zählt alles andere in der eigenen Spalte.

### 4.6 pip-Cache

- Der Cache liegt je Benutzer unter `~/.cache/pip` (`pip cache dir`), nicht je Python-Version. Auch verschiedene pip-Versionen nutzen denselben Ordner (belegt: pip-Dokumentation; hier gemessen mit pip 24.0 und 26.1.2).
- Der Skill ermittelt Größe und Orte mit `pip cache info`.
- Vor dem Löschen führt er die Einträge ab 50 MiB einzeln auf (Größe und Datum, ohne Namen).
- Danach fragt er immer, ob der Cache komplett gelöscht werden darf. Ohne Zustimmung löscht er nichts.
- Befehl bei Zustimmung: `pip cache purge` (laut Dokumentation leert er HTTP- und Wheel-Cache).
- Hinweis an den Nutzer: Nächste Installationen laden Pakete neu herunter oder bauen sie neu, besonders spürbar in wechselnden Netzen.
- Messbefund: 986 MiB, fast alles im HTTP-Cache (`http-v2`); zwei Einträge ab 50 MiB (591 MiB und 63 MiB). `pip cache list` zeigt nur die selbst gebauten Wheels (1,8 MiB), nicht die Einträge des HTTP-Caches. Die Paketnamen der großen Einträge ließen sich über die Metadatendateien per einfacher Textsuche nicht ermitteln.

### 4.7 .deb-Dateien

Reihenfolge im Ablauf: erst das Aufräumen des Download-Ordners (Abschnitt 4.9), danach 4.7, danach 4.8, danach 4.10. Dann ist die Trefferwahrscheinlichkeit gering.

- Der Skill sucht `*.deb` im Download-Ordner des Nutzers (Grundsatz 7) und im Home bis Tiefe 5, ohne Papierkorb und `~/.cache`. Hintergrund: Wer `.deb`-Dateien per Hand mit `dpkg -i` installiert, lässt sie oft liegen.
- Je Datei liest er Paketname und Version aus dem Paket (`dpkg-deb -f`) und vergleicht mit der installierten Version (`dpkg-query`, `dpkg --compare-versions`).
- Nummerierte Liste der Kandidaten: gleiche oder neuere Version desselben Pakets ist installiert. Der Skill löscht nicht automatisch. Der Nutzer wählt per Nummer oder "alles".
- Dateien, deren Paket nicht oder nur in älterer Version installiert ist, werden nur gemeldet und nicht zum Löschen angeboten.
- Messbefund: `code_1.135.0` und `code_1.134.0` (je 227 MiB) im Download-Ordner, installiert ist `code 1.145.0`.
- Hinweis an den Nutzer: Eine ältere Version lässt sich oft nicht wieder herunterladen.

### 4.8 Image-Dateien und Archive

Reihenfolge wie in 4.7: nach dem Aufräumen des Download-Ordners.

- Gemeint sind Image-Dateien, meist `*.img`, zum Beispiel zum Schreiben auf Datenträger, Sticks oder SD-Karten, sowie Archive, die zum Packen mehrerer Dateien dienen.
- Endungen: Images `*.img`, `*.iso`; Archive `*.zip`, `*.tar`, `*.tar.gz`, `*.tgz`, `*.tar.xz`, `*.tar.bz2`, `*.7z`, `*.rar`.
- Der Skill fragt den Nutzer vorher, ob auch allgemeine Archivformate erfasst werden sollen.
- Der Nutzer gibt vorher die Größenschwelle an. Vorgabe ist 150 MiB.
- Gesucht wird nur im Home des Nutzers. Ausgenommen sind die Anwendungsordner `~/.config`, `~/.local` und `~/.cache` sowie der Papierkorb, weil dort Dateien liegen, die Anwendungen selbst benutzen (Beispiel: `~/.config/Claude/vm_bundles/…/rootfs.img`).
- Der Skill sammelt die Treffer, sortiert nach Größe absteigend, nummeriert und zeigt sie an.
- Der Nutzer nennt die Nummern, die der Skill vorher genauer untersuchen soll, ob es sich um wichtige Sachen handelt.
- Die Untersuchung beruht auf den üblichen Dateiendungen, auf Namen, Ordner und Datum der Dateien, nicht auf dem Inhalt.
- Der Skill zeigt die Liste mit Status erneut an, und der Nutzer entscheidet. Automatisch löscht der Skill nichts.

### 4.9 Download-Ordner

Dieser Schritt kommt im Ablauf vor 4.7, 4.8 und 4.10.

**Welche Ordner**

- Der Download-Ordner des Nutzers laut XDG-Benutzerverzeichnis (Grundsatz 7), außerdem Ordner, die der Nutzer in einem Browser als Download-Ziel eingestellt hat.
- Weitere Download-Ordner ergeben sich aus der Erfassung der Anwendersoftware (Abschnitt 4.11). Der Skill sucht nicht pauschal nach Ordnern mit "Download" im Namen.
- Messbefund: Chrome und Firefox haben hier kein eigenes Download-Ziel eingestellt, sie nutzen den Standard.

**Analyse (im Analyseskript)**

- Für Dateien direkt im Download-Ordner: Größe und Alter.
- Für jeden Ordner direkt darunter: Größe des gesamten Inhalts über alle Ebenen, und das Alter der jüngsten geänderten oder erstellten Datei darin, ermittelt über den ganzen Dateibaum.
- Das Alter einer Datei ist die Zeit seit dem späteren von Änderungs- und Anlegezeit, in vollen Tagen.
- Die Ausgabe erfolgt getrennt in drei Gruppen nach Alter: unter 4 Tagen, 4 bis unter 15 Tagen, ab 15 Tagen.
- Unvollständige Downloads (zum Beispiel `*.crdownload` bei Chrome, `*.part`) bilden eine eigene Gruppe, unabhängig von den drei Zeitgruppen. Messbefund: Im Download-Ordner liegen mehrere `*.crdownload` mit 230 bis 671 MiB.
- In jeder Gruppe wird nummeriert und nach Größe absteigend sortiert.

**Auswahl durch den Nutzer**

- Der Nutzer kann je Gruppe Nummern ein- oder ausschließen. Die Formulierung, was erhalten und was gelöscht wird, bleibt ihm vorbehalten.
- Die Instanz überführt die Angaben in die Löschliste, die das Löschskript erhält (Grundsatz 6).

**Vor dem Löschen**

- Die Instanz zeigt die übersetzte Löschliste (Pfade, Gesamtgröße), und der Nutzer bestätigt sie.
- Der Skill weist darauf hin, dass gelöschte Dateien nur wiederherstellbar sind, wenn der Ordner gesichert wird.
- Messbefund (Entwicklungsrechner): Dort ist der Download-Ordner vom Backup ausgeschlossen.

### 4.10 Vagabundierende Medien

Dieser Schritt kommt im Ablauf als letzter dieser Gruppe: nach dem Download-Ordner (4.9), den .deb-Dateien (4.7) und den Image-Dateien und Archiven (4.8).

- Der Skill listet Mediendateien, die nicht unterhalb der Ordner für Videos, Musik, Bilder und Dokumente des Nutzers liegen (Grundsatz 7) und die offensichtlich auch nicht in Ordnern liegen, in denen Programme solche Daten bearbeiten.
- Das ist nicht nur ein Suchlauf, sondern eine nachfolgende Filterung durch die Instanz: Sie bewertet vorab das Wesen des Ordners, in dem die Daten liegen. Übrig bleiben "vagabundierende" Medien, die irgendwohin gelegt und vergessen wurden.
- Welche Dateien als Medien zählen, richtet sich nach der Dateiendung: Video, Audio und Bilder.
- Größenschwelle: wie in 4.8, vom Nutzer vorab anzugeben, Vorgabe 150 MiB.
- Die Instanz bewertet das Wesen eines Ordners, ohne den Inhalt der Dateien zu lesen, nach: Ordnername, Ablage in Anwendungsordnern (`~/.config`, `~/.local`, `~/.cache`), Projektordner (`~/git`, Ordner mit `.git`) und den Endungen der übrigen Dateien im selben Ordner (Hinweis auf ein Bearbeitungsprojekt).
- Darstellung: nummeriert nach Größe, Auswahl wie in 4.8.

### 4.11 Anwendersoftware: Cache- und Download-Ordner

**Erfassung (zu Beginn der Analyse, Abschnitt 3.3)**

- Die Instanz ermittelt die Anwendersoftware des Nutzers und stellt fest, bei welchen Programmen und wo Cache- und Download-Dateien liegen können. Quellen: Dokumentation im Internet oder Nachsehen im Dateisystem.
- Als Anwendersoftware gilt jedes Programm mit Starter-Eintrag, das nicht zum Betriebssystem unmittelbar gehört. Die Regeln (Quelle: Desktop Entry Specification und Desktop Menu Specification von freedesktop.org):
  1. Es zählt jeder Starter-Eintrag (`.desktop`) mit `Type=Application` aus `/usr/share/applications`, `/usr/local/share/applications`, `~/.local/share/applications`, den Flatpak-Exporten und den Snap-Einträgen. AppImages erscheinen dort, wenn sie integriert wurden.
  2. Nicht, wenn `NoDisplay` oder `Hidden` gesetzt ist oder `OnlyShowIn` oder `NotShowIn` den aktuellen Desktop (`XDG_CURRENT_DESKTOP`) ausschließt.
  3. Nicht, wenn `Terminal=true` (Kommandozeilenprogramme).
  4. Es muss mindestens eine Hauptkategorie vorliegen, die nicht `Settings` und nicht `System` ist. Ein Eintrag, der nur `System` oder `Settings` trägt, fällt heraus.
  5. `Utility` gilt als Anwendersoftware.
- Messbefund (dieser Rechner): 74 Programme erfasst, 4 wegen `Terminal=true` ausgeschlossen, 24 als System oder Einstellungen. Einige Ausreißer (zum Beispiel Emoji Selector) und mehrfache Einträge derselben Software sind in Kauf genommen: Sie kosten nur Zeit und Token, die Bereinigung bleibt auf der sicheren Seite.
- Software, die im Skill bereits untersucht ist (Firefox, Chrome, VS Code; Abschnitte 4.2 bis 4.4), bleibt bei der Recherche außen vor, soweit sie auf einem der getesteten klassischen Pfade installiert ist. Findet die Analyse eines dieser Programme in einem anderen Installationsweg (Snap, Flatpak oder andere), wird es wie jede andere Anwendersoftware recherchiert, und seine Ordner stehen in Tabelle 2. Die Software steht in der Liste am Ende der Analyse, falls sie installiert ist. Der Skill kann später durch weitere Analysen um Software erweitert werden, deren Details bekannt sind.

**Grundlage für die Bereinigung: pro Programm genau zwei Dinge**

1. Cache- und Download-Ordner, deren Inhalt gelöscht werden darf, **nur** wenn die Dokumentation im Internet zum Programm belegt, dass dort nur gecacht oder heruntergeladen wird. Als Cache gilt ein Ordner nur, wenn die Dokumentation belegt, dass das Programm die Daten darin jederzeit vollautomatisch wiederherstellt und dass ihr Fehlen den Arbeitsvorgang bis auf Zeitverlust nicht beeinflusst (Grundsatz 4). Wie die Dokumentation den Ordner nennt, zählt nicht. Geht aus der Dokumentation nicht hervor, dass das Programm den Verlust dieser Daten im laufenden Betrieb verträgt, wird erst gelöscht, wenn das Programm beendet ist; der Skill fordert den Nutzer dazu auf. Sie werden dem Nutzer offen mitgeteilt und zum Aufräumen angeboten. Nachsehen im Dateisystem allein genügt dafür nicht. Das gilt nur für Software, deren Details nicht schon bei der Entwicklung des Skills geklärt wurden. Geklärt sind Firefox, Chrome, VS Code und der Download-Ordner des Nutzers am Desktop; dort gelten die Festlegungen aus 4.2, 4.3, 4.4 und 4.9.
2. Ordner, die bei Programmen, die Daten verarbeiten, typischerweise als Eingangsdaten dienen. Treffer in solchen Ordnern schließt die Instanz stillschweigend aus den Suchläufen aus, weil sie als Arbeitsdaten und nicht als unwichtige Daten gelten. Das geschieht ohne Meldung an den Nutzer. Für diese Zuordnung darf die Instanz auch im Dateisystem nachsehen.

**Kein klarer Befund**

- Kein klarer Befund liegt auch vor, wenn ein Ordner nur durch Drittquellen oder durch Rückschluss aus mehreren Hinweisen belegt ist; für Tabelle 2 zählen nur die Belegstufen hoch und mittel (Abschnitt 3.5).
- Ergibt die Recherche keinen klaren Befund, werden Daten, die ganz offensichtlich solchen Programmen zugeordnet sind, vollständig vom Löschvorschlag ausgeschlossen. Sie werden auch gegenüber dem Nutzer nicht aufgelistet oder genannt.
- Skill-eigene Analysen und Anzeigen (auch Tabelle 3 in 3.3) filtern diese Daten.
- Ausnahme: Verlangt der Nutzer selbst, Ordnergrößen zu ermitteln und anzuzeigen, oder alle Dateien in einem Bereich des Dateisystems zu erfassen und deren Größe anzuzeigen, gilt der Filter nicht. Das ist eine zusätzlich angeforderte Aufgabe nach 3.7. Keine der im Skill definierten Aufgaben ist von dieser Art.
- Deshalb ist die Analyse am Anfang, einschließlich der Recherche, sehr umfassend durchzuführen. Der Nutzer erfährt das zu Beginn (3.1, Schritt 6).

Offen, wird später genau diskutiert:
- Für welche Suchläufe der stille Ausschluss gilt. Vorschlag: für 4.7, 4.8 und 4.10, nicht für den Download-Ordner (4.9).

### 4.12 Python-Bytecode-Cache

| Was | Behandlung |
|---|---|
| Ordner `__pycache__` im Home | ganz löschen einschließlich Ordner, ohne Rückfrage |

- Python legt die Dateien bei Bedarf selbst neu an; es ist ein Cache im Sinne von Grundsatz 4.
- Nur im Home. Unter `/usr` und anderen Systemverzeichnissen legt die Paketverwaltung sie an; ein normaler Nutzer kann sie dort nicht neu schreiben.
- Ohne eigenen Test in Tabelle 1 aufgenommen: Das Verhalten ist durch die Python-Spezifikation festgelegt, und das Löschen kann nichts entfernen, was Python nicht selbst neu erzeugt. Belegt in [PEP 3147](https://peps.python.org/pep-3147/): Der Ordner wird beim Import angelegt, und scheitert das Schreiben, "the import will still succeed"; eine `.pyc` aus `__pycache__` wird nur benutzt, wenn die Quelldatei existiert ("Python will not import a pyc file from the cache directory unless the source file exists"). Programme ohne Quelltext legen ihre `.pyc` dorthin, wo die Quelldatei stünde, nicht in `__pycache__`.
- Folge des Löschens: Der erste Start eines Programms dauert etwas länger.

## 5 Bereiche, für die noch keine Behandlung festgelegt ist

- Docker: Container, Images, Build-Cache, Volumes; Dev-Container-Zwischenspeicher-Volume
- Suchindex Baloo (`balooctl purge`)
- Git-Repositories (`git gc`, LFS, abgebrochene Abrufe)
- Papierkorb, Vorschaubilder
- Zwischenspeicher von Claude Desktop, Sandbox-Image von Claude Desktop
- Flatpak, Snap, AppImage, Wine
- Python-Umgebungen, Toolchains im Home, Syncthing-Versionen
- Doppelte Dateien, Migrationsreste

Festgelegt zur Aufrufart: Der Skill läuft nur auf ausdrücklichen Wunsch des Nutzers. Ob sich das fest im Skill verankern lässt, ist unklar; deshalb bleibt die Rückfrage in Abschnitt 3.1 Schritt 1 der erste Schritt.

Name des Skills, `README.md` und die Aufteilung in `SKILL.md` und Zusatzdateien werden im Moment nicht bearbeitet.

Die anstehenden Schritte stehen in `work-plan.md`.
