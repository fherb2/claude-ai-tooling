---
name: cleaning-up-linux-desktop
description: Räumt einen Linux-Desktop oder -Laptop (Ubuntu, Kubuntu und ähnliche) auf, ohne Arbeitsdaten zu gefährden — Caches, Paket- und Log-Reste, Papierkorb, Docker-Reste, alte Downloads und Installationsdateien. Misst zuerst, zeigt Füllstand und drei Tabellen, löscht Caches nach festen Regeln und Nutzdaten nur nach Auswahl des Nutzers. Sichert vorher auf Wunsch (Snapshot oder Archiv) und führt ein knappes Protokoll, mit dem sich ein abgebrochener Lauf zurückholen und die Sicherung später aufräumen lässt. Entfernt keine installierte Software. Wird ausschließlich auf ausdrücklichen Aufruf mit /cleaning-up-linux-desktop angewendet.
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
7. Was eingehängt ist (Netzfreigabe, anderer Datenträger, Bind-Mount), wird nie gelöscht, nie durchlaufen und nie angefasst, nicht einmal gelesen oder gezählt; Links werden nie verfolgt. Die Skripte setzen das selbst durch, nach dem Namen und vor jedem Zugriff, denn schon die Abfrage einer nicht antwortenden Netzfreigabe blockiert den Prozess. Eingehängte Daten erfasst nur, wer an ihrem echten Ort beginnt, und nur wenn der in der Analyse liegt. Einzige Ausnahme: der Zielort einer Archivsicherung, den der Nutzer wählt; er wird nur beschrieben.
8. Jeder Lauf endet mit einem Ergebnisbericht: was gelöscht wurde, wie groß die entfernte Datenmenge war (nicht der frei gewordene Platz), was nur gemeldet wurde. Für Docker ohne Größe.
9. Eigene Snapshots und Archive tragen den Namenspräfix `cleaning-up-linux-desktop-`. Die Skripte fassen nichts ohne diesen Präfix an und nehmen Dateien mit dem Präfix von allen Löschläufen aus. Davon weichst du nur auf ausdrücklichen Wunsch des Nutzers ab.

## Wo du läufst und wie die Skripte ausgeführt werden

Du startest grundsätzlich keine Skripte und Befehle auf dem System des Nutzers. Du gibst ihm Befehlsblöcke; er führt sie aus, auch alles mit `sudo`. Die Ergebnisse landen als Dateien in `/tmp`.

**Claude Code:** Die Skripte liegen in `${CLAUDE_SKILL_DIR}`. Frage, ob die Sitzung auf dem Rechner läuft, der aufgeräumt werden soll; wenn nicht, beende den Skill mit diesem Hinweis. Die Ergebnisdateien liest du aus `/tmp`. In der Konsole kann der Nutzer mit `/add-dir /tmp` dafür sorgen, dass du sie ohne Einzelfreigabe liest. In der Erweiterung von VS Code gibt es `/add-dir` nicht; dort geht das Lesen im Berechtigungsmodus „auto“ ohne Rückfrage, sonst gibt der Nutzer jeden Zugriff einzeln frei — sag ihm das zu Beginn, damit die Rückfragen nicht überraschen. Aufträge für das Löschskript und Pfadlisten für das Archivskript schreibst du selbst als Datei nach `/tmp/cleanup-orders/`.

Auf ausdrücklichen Wunsch führst du Skripte ohne `sudo` selbst aus; das bietest du nur an, wenn die Sitzung in der Konsole läuft und der Nutzer sie vorher mit `/cd /tmp` dorthin verlegt hat. Alles mit `sudo` bleibt beim Nutzer.

**claude.ai und Claude Desktop (Chat + Cowork):** Der Platzhalter für den Skill-Ordner wird hier nicht ersetzt. Suche den Ordner dieses Skills in deiner Ausführungsumgebung (`ls` unter `/mnt`), kopiere `analyze.py`, `delete.py`, `journal_stats.py`, `snapshots.py` und `backup.py` unverändert nach `/mnt/user-data/outputs` und biete sie als Download an — **nie als Artefakt**, denn ein Artefakt ist eine Abschrift durch dich und kann sich vom Original unterscheiden. Der Nutzer legt sie in einen Ordner seiner Wahl; in den Befehlen steht dieser Ordner statt `${CLAUDE_SKILL_DIR}`. Nach jedem Befehlsblock nennst du die Datei, die er dir hochladen soll. Aufträge, Pfadlisten und das Protokoll gibst du ebenfalls als Download.

Wurde der Skill nicht ausdrücklich mit `/cleaning-up-linux-desktop` aufgerufen — etwa weil er auf claude.ai von selbst geladen wurde —, frage zuerst, ob er jetzt angewendet werden soll. Bei Nein endest du.

## Läuft ein Skript zu lange

Jedes Skript, das Ordner durchläuft, schreibt nach `stderr` eine Zeile, wenn es länger als 5 Sekunden in demselben Ordner steht: `<skript>: still in "<Ordner>" after <n> s, no progress`. Sie wiederholt sich, und beim Weitergehen kommt `moved on after <n> s in "<Ordner>"`. Sage dem Nutzer zu Beginn, dass er diese Zeilen im Terminal sieht und sie dir nennen soll. Die Stillstände stehen auch im Bericht (Liste `stalls`).

Meldet der Nutzer, dass ein Lauf lange dauert, tust du das nie als „dauert halt“ ab. Frage zuerst nach diesen Zeilen; sie nennen den Ordner. Fehlen sie, gib den Block unten (liest nur; die Prozessnummer liefert `pgrep`). Zustand `D` bei kaum CPU und ohne Plattenzugriff heißt: Der Prozess wartet auf ein Gerät, meist eine Netzfreigabe. Ein solcher Prozess lässt sich auch mit `kill -KILL` nicht sofort beenden; rate dem Nutzer nicht zu Gewalt, sondern frage, was an dem genannten Ordner eingehängt ist (`findmnt -R <Ordner>`).

```bash
{ for p in $(pgrep -f '^python3 -I .*cleaning-up-linux-desktop'); do ps -o pid,etime,stat,pcpu,cmd -p "$p"; echo "wchan: $(sudo cat /proc/$p/wchan)"; done; } 2>&1 | tee /tmp/cleanup-hang.txt
```

## Betriebsarten

Der Skill kennt drei: das **Aufräumen** (der normale Lauf, beschrieben ab „Beginn“), das **Aufräumen der Sicherungen** eines früheren Laufs und die **Wiederaufnahme** nach einem abgebrochenen Lauf (beide am Ende dieser Datei). Suche zuerst das Protokoll (Abschnitt „Protokoll“): In Claude Code liest du `~/cleaning-up-linux-desktop-protocol.md`, auf claude.ai bittest du den Nutzer, es hochzuladen. Gibt es nichts, frage, ob es unter einem anderen Namen oder an anderer Stelle liegt, und biete diesen Suchbefehl an. Er läuft ohne `sudo`, durchsucht nur das Home und fasst keinen Einhängepunkt an; liegt das Protokoll auf einem Einhängepunkt, nennt der Nutzer den Pfad:

```bash
python3 -I "${CLAUDE_SKILL_DIR}/analyze.py" --home "$HOME" --find-protocol
```

Er schreibt die gefundenen Pfade nach `/tmp/cleanup-protocol-search.txt`.

Erst danach gilt: kein Protokoll. Schlage dann vor: kein Protokoll heißt Aufräumen; ein offener Schritt (begonnen ohne erledigt, oder Lauf nicht abgeschlossen) heißt Wiederaufnahme; ein abgeschlossener Lauf mit noch vorhandenen Sicherungen heißt Aufräumen der Sicherungen. Der Nutzer entscheidet. „Beginn“ gilt für alle drei Betriebsarten, Schritt 5 nur für das Aufräumen.

## Beginn

1. Nenne den Zweck: unnütze Datenansammlungen löschen, auf große Datenmengen hinweisen, um die der Nutzer sich selbst kümmern muss; keine Software entfernen. Gilt für Linux-Desktops und -Laptops, nicht für Server.
2. Erkläre die Arbeitsweise (vorheriger Abschnitt).
3. Sag ihm: Der Vorgang dauert länger, kann umfangreiche Internetrecherchen umfassen und verbraucht viele Token; für ein gutes Rechercheergebnis empfiehlst du das Modell Opus. Sag ihm außerdem deutlich: Für die Funktion des Skills wird keine Gewähr übernommen, und gelöschte Dateien kommen nur über eine Sicherung zurück. Empfiehl, vor dem ersten Löschen mindestens ein vollständiges Backup oder einen Snapshot anzulegen und zu prüfen, dass es sich zurückspielen lässt. Du machst das an passender Stelle gemeinsam mit ihm (Abschnitt „Sicherung“); wer will, kann es auch schon vorher selbst tun. Sag außerdem: Die Sicherungen lassen sich später mit diesem Skill aufräumen, wenn der Nutzer sich überzeugt hat, dass alles funktioniert.
4. Lass ihn diese Arbeitsweise bestätigen, bevor es weitergeht.
5. Nur beim Aufräumen: Frage alle Angaben ab, die die Analyse braucht, bevor sie startet: die **Größenschwelle** (eine Zahl für große Einzeldateien, Images, Archive und Medien; Vorgabe 150 MiB) und ob auch **allgemeine Archive** (`.zip`, `.tar.*`, `.7z`, `.rar`) bei den Images erfasst werden sollen. Danach läuft die Analyse ohne Rückfrage.

## Umgebung ermitteln

Gib dem Nutzer diesen Block; er schreibt nach `/tmp/cleanup-env.txt`:

```bash
{ echo "DESKTOP=$XDG_CURRENT_DESKTOP"; echo "HOME=$HOME"; for d in DOWNLOAD VIDEOS MUSIC PICTURES DOCUMENTS; do echo "$d=$(xdg-user-dir $d)"; done; grep -h '"browser.download.dir"' ~/.mozilla/firefox/*/prefs.js 2>/dev/null | sed 's/^/FIREFOX /'; for p in ~/.config/google-chrome/*/Preferences; do [ -f "$p" ] && python3 -c 'import json,sys; print("CHROME", json.load(open(sys.argv[1])).get("download", {}).get("default_directory", ""))' "$p"; done; } | tee /tmp/cleanup-env.txt
```

Download-Ziele, die in Firefox oder Chrome vom Standard abweichen (Zeilen `FIREFOX`, `CHROME`), sind weitere Download-Ordner; jeder geht als eigenes `--downloads` in die Analyse. Erfasst wird nur, was im Home liegt. `xdg-user-dir` liefert für einen nicht eingerichteten Ordner das Home selbst. Ein solcher Eintrag gilt als nicht vorhanden: Den Download-Ordner ohne Eintrag meldest du, Medienordner ohne Eintrag lässt du aus dem Aufruf weg — mit dem Home als Medienordner fiele das ganze Home aus 4.10 heraus.

## Analyse

```bash
sudo nice -n 19 ionice -c3 python3 -I "${CLAUDE_SKILL_DIR}/analyze.py" --home "$HOME" --downloads "<Download-Ordner>" [--downloads "<Browser-Ziel>" …] --media-dir "<Videos>" --media-dir "<Musik>" --media-dir "<Bilder>" --media-dir "<Dokumente>" --desktop "$XDG_CURRENT_DESKTOP" --threshold <MiB> [--archives]
```

Das Skript zeigt seinen Fortschritt und schreibt `/tmp/cleanup-analysis.json`. Liegt ein übergebener Download- oder Medienordner auf einem Einhängepunkt, wird er nicht analysiert; das Skript meldet es, und `meta.params.not_read` nennt ihn. Sag dem Nutzer, dass er diesen Ordner an seinem echten Ort selbst aufräumen muss. `meta.other_filesystems` nennt die ausgelassenen Einhängepunkte unter dem Home. Der Inhalt: `fill_level`, `table1` (Bereiche 4.1 bis 4.14 außer 4.11), `software` (Starter-Einträge, Flatpak, Snap, Anwendungsordner mit Vorfilter), `table3`, `safeguards` (btrfs, ZFS, LVM, Timeshift, Snapper: was das System an Sicherungen hergibt). Es liest nur. Sag dem Nutzer vorher, dass du dabei auch prüfst, welche Software Cache- und Download-Ordner mitbringt, und dich im Internet über die Programme informierst.

Danach recherchierst du die erfassten Programme (4.11), bevor du Tabellen zeigst. Am Ende der Analyse nennst du kurz die Software, zu der du bei der Bereinigung Vorschläge machen wirst; Firefox, Chrome und VS Code gehören dazu, wenn sie installiert sind.

## Darstellung

Zuerst der **Füllstand** je lokalem Dateisystem (belegt, Gesamtgröße, Prozent); Netzfreigaben und andere nicht lokale Dateisysteme fehlen darin mit Absicht; gibt es btrfs-Snapshots, ihre Zahl und, wenn bekannt, ihre Belegung; dazu, welche Sicherungsvarianten das System hergibt (`safeguards`). Der Füllstand zeigt, wo Aufräumen etwas bringt.

Dann drei Tabellen, **je Bereich eine Zeile**. Einzellisten, Histogramme und Auswahllisten kommen erst, wenn der Bereich bearbeitet wird — nie alles gleich nach der Analyse.

- **Tabelle 1 — durch Tests gesichert** (Abschnitte 4.1 bis 4.14 außer 4.11). Spalten: Bereich, Fundort, Größe, Behandlung (ohne Rückfrage / mit Rückfrage / nur melden), braucht root, Programm muss beendet sein, Hinweis zur Sicherung. Für 4.5 zwei Zeilen: Log-Files gesamt, Journal gesamt. Die Zeilen 4.5, 4.7 bis 4.10 und 4.14 tragen den Hinweis, dass Gelöschtes nur über Backup oder Snapshot zurückkommt.
- **Tabelle 2 — durch Recherche belegt** (4.11). Spalten: Programm, Ordner, Größe, Belegstufe mit Quelle, Programm muss beendet sein, Kommentar zur Sicherung (die Maßnahme ist nicht getestet).
- **Tabelle 3 — Statistik**, ohne die Bereiche aus Tabelle 1 und 2:
  - Größe je Verzeichnis: oberste Ebene unter Home und Systemverzeichnissen, tiefere nur, wo das Skript sie liefert; im Home zusätzlich der Anteil, der seit über einem Jahr unverändert ist. Kennzeichne Treffer, die einem der offenen Bereiche entsprechen: Suchindex Baloo, Git-Repositories, Vorschaubilder, Claude-Desktop-Zwischenspeicher und Sandbox-Image, Flatpak/Snap/AppImage/Wine, Python-Umgebungen, Toolchains, Syncthing-Versionen, Duplikate, Migrationsreste.
  - Große Einzeldateien: je offenem Bereich eine Zeile mit Zahl und Summe, Übriges als „Sonstiges“.
  - Reste deinstallierter Programme: Anwendungsordner, die du keiner installierten Software, keinem Desktop- oder Systembestandteil und keinem Werkzeug ohne Starter-Eintrag zuordnen kannst, je mit Begründung. Der Vorfilter des Skripts (`prefilter_match`) ist nur ein Hinweis; das Urteil fällst du.
  - Doppelte Dateien: Zahl der Gruppen und überzählige Menge.
  - Reste abgebrochener Git-Abrufe, Caches ohne zugeordnetes Programm, Absturzabbilder (nur wenn vorhanden), Entwicklungsartefakte (je Projekt: Größe, letzte Änderung der Quellen, Abhängigkeitsliste ja/nein).

## Sicherung

Die Analyse liest nur. Gesichert wird **vor dem ersten Löschen** und ein zweites Mal **vor dem Nachgang** zu Tabelle 2 und 3, weil dort Ungetestetes geschieht. Ob statt dessen vor jedem Aufräumschritt gesichert wird, entscheidet der Nutzer; Vorgabe ist einmal je Zeitpunkt. Hat er schon vorher gesichert, trägst du das ins Protokoll ein.

Biete nach der Analyse alle Varianten an, die `safeguards` hergibt, und lass wählen. Wahl, Zielort und alle Namen kommen ins Protokoll:

1. **Eigene Sicherung:** Der Nutzer bestätigt, dass eine aktuelle Sicherung vorliegt, die sich zurückspielen lässt. Du sicherst dann nichts selbst.
2. **Snapshot (btrfs):** nur für Dateisysteme mit `kind: btrfs`. ZFS und LVM (`tested: false`) nennst du, bietest dafür aber keinen Snapshot an: Sie sind ungeprüft, und der Skill enthält keinen Snapshot-Befehl dafür.
3. **Timeshift oder Snapper**, wenn `safeguards.tools` sie als installiert und eingerichtet zeigt: Gib ihre Befehle als Block; den Namen oder die Kennung trägst du ins Protokoll ein. Die Skripte fassen sie nicht an.
4. **Archiv der zu löschenden Dateien (tar oder zip):** für Nutzdaten (4.7 bis 4.10, Download-Ordner, Papierkorb) und für Anwendungsordner, bei denen nicht belegt ist, dass es reine Caches sind (Nachgang). Belegte Caches (Tabelle 1) sicherst du nie. Frage vor jeder Archivsicherung, ob der Nutzer sie wirklich will.

**Snapshot.** Frage, ob der Ort `<Einhängepunkt>/.cleaning-up-linux-desktop-snapshots/` für ihn passt; er kann einen anderen Ort unterhalb des Einhängepunkts wählen (`--base-dir`). Sichere jedes Dateisystem, auf dem gelöscht wird (aus dem Füllstand, meist `/` und `/home`):

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/snapshots.py" create --mount <Einhängepunkt> --label <Bezeichnung> [--base-dir <Ordner>] [--dry-run]
```

Erst Probelauf, dann echt; den Namen nennt `/tmp/cleanup-snapshots-create.json`. Sag dazu: Ein Snapshot hält gelöschte Daten fest, Platz wird erst frei, wenn er entfernt ist.

**Archiv.** Frage nach:
- **Format:** `tar` (Vorgabe) behält Besitzer, ACLs, erweiterte Attribute, Hardlinks und Links; unkomprimiert bei schnellem Ziel (interne SSD), als `tar.gz` bei langsamem (USB-Stick, Netz). `zip` packt dateiweise (Medien nur ablegen, Rest gepackt), behält aber **Besitzer, ACLs, erweiterte Attribute und Hardlinks nicht**. Weise bei zip ausdrücklich darauf hin, zum Beispiel auf die Herkunfts-URL von Downloads sowie Tags und Bewertungen aus Dolphin (nach Wissen, nicht geprüft).
- **Zielort:** Vorgabe `~/`. Frage, ob der Nutzer lieber ein externes Gerät nimmt (Stick, Netzfreigabe). Bei einer Netzfreigabe sag, dass die Übertragung in der Regel deutlich länger dauert als an einem direkt angeschlossenen, ausreichend modernen Speichergerät. Liegt das Ziel auf demselben Dateisystem wie die Daten, wird durch das Aufräumen kein Platz frei, solange das Archiv existiert.
- **Reserve:** Vorgabe ist die größere von 10 % des Ziel-Dateisystems und 10 GiB. Der Nutzer darf sie senken; das Skript hebt sie auf die größere von 5 % und 5 GiB an.
- **Prüfung:** Vorgabe ist der Vergleich mit den Dateien (ein zweites Lesen); nur auf Wunsch die schnelle Prüfung.

Je Sicherungsschritt: (1) Probelauf von `delete.py` mit `--with-paths` — der Bericht nennt unter `candidates` die Pfade (bei Aufträgen `list` sind es die gewählten Pfade); (2) `backup.py create --dry-run` zeigt Menge und Platz; (3) echt; (4) **erst bei `ok: true`** das echte Löschen. Scheitert die Sicherung, löschst du nichts.

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/backup.py" create --list <Liste oder Bericht von delete.py> --target "<Zielordner>" --step <schritt> --format tar|tar.gz|zip [--run <Ordnername des Laufs>] [--reserve-percent P] [--reserve-gib G] [--verify quick] [--dry-run]
```

Der erste Bericht (`/tmp/cleanup-backup-create.json`) nennt den Lauf (`run`); gib ihn für alle weiteren Schritte desselben Laufs mit `--run` an. Jeder Schritt wird eine eigene Datei `NN-<schritt>.tar|.tar.gz|.zip`.

**Zurückholen** geschieht selektiv: nur Fehlendes, nichts wird überschrieben. Aus einem Snapshot: `snapshots.py restore --snapshot <Name> --path <Ordner relativ zum Einhängepunkt> [--dry-run]`; aus einem Archiv: `backup.py restore --target <Ziel> --run <Lauf> --step <schritt> [--path <absoluter Originalpfad>] [--dry-run]`. Ein Zurückrollen eines ganzen Subvolumes machst du nur auf ausdrücklichen Wunsch und mit Warnung: Das Protokoll im Home würde auf den Stand des Snapshots zurückgesetzt. Aus einem zip erhalten neue Dateien den Besitzer ihres Elternordners. Ziele an oder unter einem Einhängepunkt lassen beide Skripte aus und melden sie (`not_restored`); sag dem Nutzer, dass er solche Daten an ihrem Ort selbst zurückspielen muss.

## Protokoll

Das Protokoll ist kurz und dient nur dazu, dass in einer neuen Sitzung ein Rollback möglich ist. Vorgabe: `~/cleaning-up-linux-desktop-protocol.md`; der Nutzer kann Namen und Ort ändern. In Claude Code schreibst du die Datei selbst, auf claude.ai gibst du sie als Download und bittest beim neuen Start um den Upload.

- **Erste Zeile genau:** `# cleaning-up-linux-desktop Protocol` (nur sie als englisches Token); der übrige Text steht in der Sprache des Nutzers, solange er nichts anderes will.
- **Aufbau:** ein Kopf mit den Eckdaten (gewählte Sicherungsvariante, Zielort, Takt der Sicherung, Format), dann das Protokoll je Sitzung mit Datum, dann ein Abschnitt „Sonderbehandlungen“ ohne Protokollcharakter.
- **Einträge:** je Schritt eine Zeile mit Bereich und was getan wurde. Schreibe „begonnen“, **bevor** du den Befehlsblock übergibst, danach „erledigt“ oder „abgebrochen“, so bleibt ein Abbruch mitten im Schritt sichtbar. Je Löschschritt die betroffenen Ordner (nicht jede Datei) und welche Sicherung ihn abdeckt, denn die Berichte unter `/tmp` überstehen keinen Neustart. Übersprungene Schritte (mit dem Nutzer) und Besonderheiten. Jede Sicherung und jedes Entfernen einer Sicherung als eigener Schritt mit Namen und Ort.
- **Sonderbehandlungen:** Frage, ob eine besondere Vereinbarung mit dem Nutzer festgehalten werden soll, zur Wiederverwendung. Beim nächsten Lauf fragst du, ob sie wieder gelten sollen.

## Reihenfolge der Bearbeitung

Schlage vor, Tabelle 1 Schritt für Schritt abzuarbeiten; zuvor sicherst du nach dem Abschnitt „Sicherung“ und legst das Protokoll an. Reihenfolge: 4.1 bis 4.6, 4.12, 4.13, dann 4.9 → 4.7 → 4.8 → 4.10, zuletzt 4.14 (damit alles, was ein früherer Schritt in den Papierkorb verschoben hat, mit erfasst wird). Danach der Ergebnisbericht; mit ihm endet der eigentliche Lauf. Dann bietest du den Nachgang an, zuerst zu Tabelle 2, dann zu Tabelle 3, und davor eine neue Sicherung (Abschnitt „Sicherung“); der Nutzer kann nach jedem Teil aufhören.

Je Bereich: die Einzelheiten zeigen, die Entscheidung des Nutzers einholen, wo eine nötig ist, den Auftrag schreiben, im Protokoll „begonnen“, **Probelauf**, Ergebnis zeigen, bei einer Archivsicherung diese ausführen, nach Bestätigung **echter Lauf**, im Protokoll „erledigt“:

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/delete.py" --home "$HOME" --order /tmp/cleanup-orders/<Bereich>.json --dry-run
sudo python3 -I "${CLAUDE_SKILL_DIR}/delete.py" --home "$HOME" --order /tmp/cleanup-orders/<Bereich>.json
```

Jeder Lauf schreibt `/tmp/cleanup-report-<Bereich>.json` (entfernte Anzahl und Datenmenge, Gruppen, übersprungene Pfade mit Grund, ausgeführte Befehle). Übersprungenes zeigst du dem Nutzer mit Grund. Das Skript verweigert unabhängig vom Auftrag: `/`, das Home, Ordner direkt unter `/` oder dem Home, `/boot`, alles außerhalb von Home, `/var`, `/opt`, `/usr/local`, `/srv`, Einhängepunkte und alles, was einen enthält oder darunter liegt, Links (außer im Papierkorb).

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

**4.9 Download-Ordner** — nach Alter, nicht nach Größe: Im Download-Ordner geht es um die Übersicht. Frage nach der Altersgrenze x in Tagen (Vorgabe 14) und nach Ausnahmen. Gelöscht wird alles direkt im Download-Ordner, dessen Alter größer als x Tage ist, unabhängig von der Größe: eine Datei nach ihrem eigenen Alter; ein Ordner nach seinem jüngsten Element in beliebiger Tiefe (Dateien, Links und Unterordner) — ein einziges jüngeres Element schützt den ganzen Ordner mit allem darin; ein leerer Ordner nach seinem eigenen Datum. Unvollständige Downloads (`.crdownload`, `.part`) fallen unter dieselbe Grenze, Links direkt im Ordner werden nur gemeldet. Auftrag `rule` mit `{"days": x, "folders": [...], "exclude": [...]}`: `folders` sind die Download-Ordner aus `meta.params.downloads` der Analyse, `exclude` die Ausnahmen des Nutzers, von dir anhand von `table1.4.9_downloads` in absolute Pfade direkt unter dem Download-Ordner übersetzt. Das Skript berechnet das Alter beim Lauf; die Alterszahlen der Analyse zählen bei Ordnern nur Dateien und können abweichen. Mach deshalb zuerst den Probelauf und zeige die Übersicht aus seinem Bericht (`removed`, `skipped`): Zahl und Gesamtgröße, jeden Ordner einzeln, Dateien nach Typ gezählt, die größten wenigen, Übersprungenes mit Grund; die vollständige Liste legst du als Datei ab. Der Nutzer bestätigt, dann der echte Lauf. Hinweis: wiederherstellbar nur, wenn der Ordner gesichert wird.

**4.7 .deb-Dateien** — mit Auswahl. Nummerierte Liste der Dateien, deren Paket in gleicher oder neuerer Version installiert ist (`status: same_or_newer_installed`); der Nutzer wählt Nummern oder „alles“. Übrige nur melden. Hinweis: Eine ältere Version lässt sich oft nicht wieder herunterladen. Auftrag `list`.

**4.8 Images und Archive** — mit Auswahl. Treffer nach Größe absteigend, nummeriert. Der Nutzer nennt Nummern, die du genauer ansehen sollst — nach Endung, Name, Ordner und Datum, nicht nach Inhalt; dann die Liste mit deiner Einschätzung erneut, der Nutzer entscheidet. Auftrag `list`.

**4.10 Vagabundierende Medien** — mit Auswahl. Das Skript liefert Mediendateien ab der Schwelle außerhalb der Medienordner, je Fundordner die Endungen der Nachbardateien und ob es ein Projekt oder `.git` ist. Du bewertest das Wesen jedes Ordners (Name, Projektordner, Nachbarendungen als Hinweis auf ein Bearbeitungsprojekt, bewusste Ablage) und zeigst nur, was vergessen abgelegt aussieht. Darstellung und Auswahl wie 4.8. Auftrag `list`.

**4.14 Papierkorb** — zuletzt. Frage nach x Tagen (Vorgabe 14, 0 = alles). Auftrag `rule` mit `{"days": x}`. Nur der Papierkorb im Home wird bearbeitet; Papierkörbe auf anderen Datenträgern (`.Trash-<uid>` an einem Einhängepunkt) fasst der Skill nicht an, der Nutzer leert sie an ihrem Ort selbst — sag ihm das. Maßgeblich ist das Datum des Verschiebens in den Papierkorb; Einträge ohne gültige `.trashinfo` werden nur gemeldet. Hinweis: endgültig weg, ein Backup hilft nur, wenn der Papierkorb gesichert wird.

## Ergebnisbericht

Nach Tabelle 1, vor dem Nachgang, stellst du aus den Berichten der einzelnen Läufe einen Gesamtbericht zusammen: je Bereich, was gelöscht wurde (Anzahl, entfernte Datenmenge; bei Docker die gelöschten Container und Images ohne Größe), was übersprungen wurde und warum, was nur gemeldet wurde. Darunter die Summe der entfernten Datenmenge und die angelegten Sicherungen (Name, Ort, Größe). Sag ausdrücklich, dass das nicht der frei gewordene Platz ist: Snapshots und Archive auf demselben Dateisystem, Kompression und noch geöffnete Dateien können ihn kleiner machen. Nenne, dass sich die Sicherungen später mit diesem Skill aufräumen lassen, und trage den Lauf im Protokoll als abgeschlossen ein.

## Tabelle 2: Anwendersoftware (4.11) und Nachgang

Grundlage sind die erfassten Programme in `software.desktop.included` (die Regeln dafür setzt das Skript um) und die Ordner unter `~/.cache`, die du einem Eigentümer ohne Starter-Eintrag zuordnen kannst (Erweiterung, Kommandozeilenwerkzeug, Bibliothek). Firefox, Chrome und VS Code auf den klassischen Pfaden recherchierst du nicht.

Je Programm suchst du in der Dokumentation genau zwei Dinge:
1. **Cache- und Download-Ordner.** Als Cache gilt ein Ordner nur, wenn die Dokumentation belegt, dass das Programm die Daten darin jederzeit vollautomatisch wiederherstellt und ihr Fehlen bis auf Zeitverlust nichts ändert — wie die Dokumentation ihn nennt, zählt nicht; Nachsehen im Dateisystem allein genügt nicht. Geht nicht hervor, dass das Programm den Verlust im laufenden Betrieb verträgt, löschst du erst, wenn es beendet ist, und forderst den Nutzer dazu auf.
2. **Ordner mit Eingangsdaten** datenverarbeitender Programme. Treffer darin schließt du still aus den Suchläufen 4.8, 4.10 und den großen Einzeldateien und Duplikaten in Tabelle 3 aus — ohne Meldung. Nicht still ausgeschlossen wird bei 4.7, 4.9 und bei der Größe je Verzeichnis.

**Belegstufe** je Zeile: **hoch** — die offizielle Dokumentation sagt es ausdrücklich; **mittel** — nur Entwicklerforum, Issue-Tracker oder Distributions-Wiki. Nur Drittquellen oder Rückschluss gilt als **kein klarer Befund**: Dann nennst du die Daten des Programms nirgends und schließt sie von jedem Löschvorschlag aus (die Größe je Verzeichnis zählt sie trotzdem mit). Ordner unter `~/.cache` ohne zuordenbaren Eigentümer kommen nach Tabelle 3. **Nachgang zu Tabelle 2** (nach dem Ergebnisbericht): Wiederhole die Stellen aus Tabelle 2 und sag dem Nutzer, dass du für diese Posten keine getesteten und belegten Erfahrungen besitzt. Biete an, alle oder einen Teil davon gemeinsam weiter zu klären — Recherchen in der Dokumentation, gemeinsam Strategien zum Aufräumen entwickeln und ausführen. Geh dabei vorsichtig vor und erinnere den Nutzer vor jedem Löschen, was tatsächlich belegt und was Vermutung ist, damit er abschätzen kann, ob wirklich gelöscht werden soll. Das Löschskript nimmt für Tabelle 2 keinen Auftrag an; gelöscht wird im Nachgang wie bei einer zusätzlich angeforderten Suche.

## Nachgang zu Tabelle 3

Nach dem Nachgang zu Tabelle 2, oder wenn der Nutzer ihn auslässt, biete an, die Befunde gemeinsam zu erforschen: Inhalte genauer ansehen, Internetrecherche. Sag dazu: Dafür gibt es keine vorgefertigten Lösungen; sie werden erst erarbeitet, sollten gut belegt sein und sind ungetestet — eine vollständige Sicherung oder ein Snapshot ist dringend zu empfehlen. Vorher räumst du dort nichts auf.

Bittet der Nutzer zusätzlich um eine Suche nach weiteren Dateien, gilt keine der Regeln dieses Skills; die Randbedingungen handelst du mit ihm aus. Für solche Suchen gilt auch der stille Ausschluss nicht.

## Betriebsart: Aufräumen der Sicherungen

Nur, wenn das Protokoll den letzten Lauf als abgeschlossen ausweist; sonst geh zur Wiederaufnahme. Das Aufräumen kann an einem späteren Zeitpunkt liegen, an dem der Nutzer sich überzeugen konnte, dass alles funktioniert. Stelle fest, was von den Namen im Protokoll noch existiert und was es festhält (`snapshots.py list`, `backup.py list --target <Ziel>`; die Berichte liegen als `/tmp/cleanup-snapshots-list.json` und `/tmp/cleanup-backup-list.json`). Der Nutzer entscheidet, was weg soll. Entfernt wird nur, was den Präfix trägt, je Schritt mit Probelauf zuerst:

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/snapshots.py" remove --name <Name> [--dry-run]
sudo python3 -I "${CLAUDE_SKILL_DIR}/backup.py" remove --target "<Zielordner>" --run <Lauf> [--dry-run]
```

Jedes Entfernen ist ein Schritt im Protokoll. Timeshift und Snapper räumst du mit deren Befehlen als Block auf. Danach fragst du, ob das Protokoll gelöscht werden soll; du löschst es nur, wenn der Nutzer es will. Stehen Sonderbehandlungen darin, sag es ihm. Er kann auch nur den Protokollteil dieser und früherer Sitzungen entfernen lassen und die Datei mit den Sonderbehandlungen behalten.

## Betriebsart: Wiederaufnahme nach einem Abbruch

Gilt, wenn das Protokoll einen offenen Schritt oder einen nicht abgeschlossenen Lauf zeigt, etwa nach einem Neustart, bei dem die Sitzung verloren ging. Lies das Protokoll und stelle den Stand dar: was erledigt ist, was begonnen wurde ohne Abschluss. Prüfe, ob die genannten Sicherungen noch vorhanden sind (`snapshots.py list`, `backup.py list`). Schlage dann vor, einen oder alle Schritte zurückzuholen (selektiv, Abschnitt „Sicherung“) oder fortzusetzen; der Nutzer entscheidet. Zurückgeholt wird je Schritt aus der Sicherung, die das Protokoll nennt. Gibt es keine, weise auf die eigene Sicherung des Nutzers hin, die er selbst zurückspielt.
