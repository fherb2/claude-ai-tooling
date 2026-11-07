# cleaning-up-linux-desktop — einen Linux-Desktop aufräumen, ohne Arbeitsdaten zu gefährden

*Stand: 2026-11-07*

**🚧 In Arbeit.** Skilltext und Skripte sind geschrieben und an einem Entwicklungsrechner geprüft; der vollständige Lauf des installierten Skills steht noch aus, ebenso die englische Fassung (siehe „Stand und Offenes“). — Für Claude Code und claude.ai.

---

## Überblick

**Der Skill räumt einen Linux-Desktop oder -Laptop auf und löscht dabei nur, was nachweislich unnütz ist.** Er misst zuerst, was auf dem Rechner liegt, zeigt den Füllstand der Dateisysteme und drei Tabellen und arbeitet sie dann gemeinsam mit dem Nutzer ab: Caches von Firefox, Chrome und VS Code, der Paketcache von apt, Log-Files und Journal, der pip-Cache, Python-Bytecode, Docker-Reste, der Download-Ordner, liegengebliebene Installationsdateien, Images und Archive, vergessene Mediendateien und zuletzt der Papierkorb.

Was ohne Rückfrage gelöscht wird, ist eng begrenzt: programmeigene Zwischendateien, die das Programm nicht mehr braucht oder jederzeit vollautomatisch neu erzeugt. Alles, was dem Nutzer gehört — Downloads, Installationsdateien, Medien, der Inhalt des Papierkorbs —, wird nur nach seiner Auswahl gelöscht. Beim Downloads-Ordner gilt eine Altersregel, die der Nutzer bestimmt: Alles, was älter ist als x Tage (Vorgabe 14), geht, unabhängig von der Größe; ein Ordner bleibt mit allem darin, solange irgendetwas in ihm, auch tief verschachtelt, jünger ist. Vor jedem Löschen gibt es einen Probelauf, der zeigt, was tatsächlich weg wäre, und vor dem ersten Löschen eine Sicherung, die der Skill gemeinsam mit dem Nutzer anlegt (Snapshot oder Archiv). Ein knappes Protokoll hält fest, was getan wurde: Damit lässt sich ein abgebrochener Lauf zurückholen, und die Sicherungen lassen sich später mit dem Skill aufräumen.

**Abgrenzung:** Der Skill entfernt keine installierte Software, auch keine, die vermutlich niemand mehr braucht; er meldet sie nur. Er ist für Desktops und Laptops gedacht (Ubuntu, Kubuntu und ähnliche), nicht für Server. Was eingehängt ist — ein anderes Dateisystem oder ein Bind-Mount —, wird nie durchlaufen und nie gelöscht.

Der Skill wird nur auf ausdrücklichen Aufruf angewendet: `/cleaning-up-linux-desktop`. Er lädt sich nicht von selbst.

## Ohne Gewähr

**Für die Funktion dieses Skills wird keine Gewähr übernommen.** Er löscht Dateien, und gelöschte Dateien kommen nur über eine Sicherung zurück. Seine Regeln sind an einem einzelnen Rechner entwickelt und geprüft; auf einem anderen System, mit anderer Software oder in einer späteren Version eines Programms können sie anders wirken. **Lege vor dem ersten Löschen mindestens ein vollständiges Backup oder einen Snapshot an** und prüfe, dass es sich zurückspielen lässt. Der Skill macht das an passender Stelle gemeinsam mit Dir; Du kannst es auch schon vorher tun. Was der Skill anrichtet, verantwortet, wer ihn einsetzt.

## Installation

### Claude Code

1. **Paket herunterladen.** `downloads/cleaning-up-linux-desktop_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `cleaning-up-linux-desktop/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

### claude.ai und Claude Desktop (Chat + Cowork)

1. **Paket herunterladen.** `downloads/cleaning-up-linux-desktop_de_web.zip`

2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.

## Details

### Wie der Skill arbeitet

Der Skill startet selbst keine Befehle auf dem Rechner. Er gibt dem Nutzer Befehlsblöcke; der Nutzer führt sie aus, auch alles, was `sudo` braucht. Die Ergebnisse landen als Dateien in `/tmp`, wo der Skill sie liest. In Claude Code liegen die fünf Skripte im Skill-Ordner; auf claude.ai bekommt der Nutzer sie als Download und lädt die Ergebnisdateien wieder hoch.

Ablauf:

0. Betriebsart wählen: Der Skill sucht zuerst das Protokoll und schlägt vor, ob er aufräumt, die Sicherungen eines früheren Laufs aufräumt oder einen abgebrochenen Lauf wieder aufnimmt.
1. Zweck und Arbeitsweise erklären, Bestätigung einholen, die Größenschwelle für große Dateien abfragen (Vorgabe 150 MiB) und ob auch Archive erfasst werden sollen.
2. Umgebung ermitteln: Desktop, die Benutzerordner nach XDG und abweichende Download-Ziele von Firefox und Chrome — Ordnernamen wie „Downloads“ oder „Bilder“ setzt der Skill nie selbst ein, sie heißen je nach Sprache anders.
3. Analyse: ein einziger Durchlauf durch Home, `/var`, `/opt`, `/usr/local` und `/srv`, nur lesend.
4. Füllstand und drei Tabellen: **Tabelle 1** — durch Tests gesicherte Bereiche; **Tabelle 2** — Cache-Ordner weiterer Programme, die der Skill zur Laufzeit recherchiert, mit Belegstufe; **Tabelle 3** — Statistik zum gemeinsamen Erforschen (Größe je Verzeichnis, große Dateien, Reste deinstallierter Programme, Duplikate, Entwicklungsartefakte).
5. Sichern und Protokoll anlegen (siehe unten).
6. Bereich für Bereich durch Tabelle 1: Einzelheiten zeigen, Entscheidung einholen, Probelauf, nach Bestätigung echter Lauf.
7. Ergebnisbericht: was gelöscht wurde und wie viel, was übersprungen und was nur gemeldet wurde. Damit endet der eigentliche Lauf.
8. Nachgang, auf Wunsch und jederzeit abbrechbar, mit einer neuen Sicherung davor: zuerst Tabelle 2, dann Tabelle 3. Für diese Stellen hat der Skill keine getesteten Erfahrungen; er klärt sie gemeinsam mit dem Nutzer, mit Recherche in der Dokumentation und mit dem ausdrücklichen Hinweis vor jedem Löschen, was belegt und was Vermutung ist. Für Tabelle 2 liegt die Recherche schon aus der Analyse vor, für Tabelle 3 beginnt sie erst. Gelöscht wird im Nachgang mit einem festen Befehlsblock, der je Pfad Einhängepunkte, Links und den Präfix der eigenen Sicherungen prüft und zuerst als Probelauf läuft.

### Die Skripte

| Datei | Aufgabe |
| --- | --- |
| `analyze.py` | die Analyse; schreibt `/tmp/cleanup-analysis.json`; mit `--find-protocol` nur die Suche nach dem Protokoll früherer Läufe |
| `journal_stats.py` | die Auswertung von Journal und Log-Files beim Bearbeiten dieses Bereichs; schreibt `/tmp/cleanup-journal.json` |
| `delete.py` | das Löschen, ein Bereich je Lauf, mit Probelauf (`--dry-run`); schreibt `/tmp/cleanup-report-<Bereich>.json` |
| `snapshots.py` | eigene btrfs-Snapshots: anlegen, auflisten, entfernen, selektiv zurückholen |
| `backup.py` | Archive (tar, tar.gz, zip) der zu löschenden Dateien: anlegen und prüfen, auflisten, selektiv zurückholen, entfernen |

Alle fünf brauchen nur Python 3 mit der Standardbibliothek (`backup.py` ruft für tar zusätzlich GNU `tar` auf). Ihre Bildschirmmeldungen sind englisch; mit dem Nutzer spricht der Skill in dessen Sprache.

### Sicherung und Protokoll

Vor dem ersten Löschen und vor dem Nachgang bietet der Skill an, was das System hergibt, und der Nutzer wählt: eine eigene Sicherung bestätigen, einen **btrfs-Snapshot**, die Befehle von **Timeshift** oder **Snapper**, wenn eines davon eingerichtet ist, oder ein **Archiv** der zu löschenden Dateien als `tar` oder `zip`. Für belegte Caches wird nicht gesichert, für Nutzdaten und für Anwendungsordner ohne Beleg schon, nach Rückfrage.

- **Eigene Sicherungen** tragen den Namenspräfix `cleaning-up-linux-desktop-`. Die Skripte fassen nichts ohne diesen Präfix an, und Analyse wie Löschläufe nehmen Dateien mit dem Präfix aus.
- **Snapshots** liegen standardmäßig in `<Einhängepunkt>/.cleaning-up-linux-desktop-snapshots/`; der Nutzer kann einen anderen Ort unterhalb des Einhängepunkts wählen. Sie sind schreibgeschützt und halten gelöschte Daten fest, bis sie entfernt sind.
- **Archive** liegen in einem Ordner je Lauf, je Sicherungsschritt eine Datei. Vor dem Schreiben prüft das Skript den Platz am Zielort samt Reserve (Vorgabe die größere von 10 % und 10 GiB, nie unter der größeren von 5 % und 5 GiB), danach vergleicht es das Archiv mit den Dateien. Scheitert etwas, wird nichts gelöscht. `tar` behält Besitzer, ACLs und erweiterte Attribute; `zip` behält sie **nicht** (auch keine Hardlinks), packt aber dateiweise schneller.
- **Zurückholen** geschieht selektiv: Es kommt nur zurück, was fehlt, nichts wird überschrieben.
- **ZFS und LVM** erkennt der Skill und meldet sie, bietet dafür aber keinen Snapshot an. Es fehlte ein Testsystem; diese Varianten sind ungeprüft. Dort sichert der Nutzer selbst oder wählt das Archiv.
- **Das Protokoll** `~/cleaning-up-linux-desktop-protocol.md` beginnt mit der Zeile `# cleaning-up-linux-desktop Protocol` und ist kurz: je Schritt „begonnen“ und „erledigt“, die Namen aller Sicherungen als eigene Schritte, übersprungene Schritte und Besonderheiten, dazu ein Abschnitt „Sonderbehandlungen“ zur Wiederverwendung. Der Skill löscht es nur, wenn der Nutzer das will. Er legt es im Home ab; ein Zurückrollen eines ganzen Home-Snapshots würde es auf den Stand des Snapshots zurücksetzen, deshalb ist selektives Zurückholen der Standard.

### Was das Löschskript immer verweigert

Unabhängig vom Auftrag löscht `delete.py` nie: `/`, das Home selbst, einen Ordner direkt unter `/` oder direkt unter dem Home, irgendetwas unter `/boot`, etwas außerhalb von Home, `/var`, `/opt`, `/usr/local` und `/srv`, einen Einhängepunkt, einen Ordner, der einen enthält, und alles, was auf einem liegt, alles mit dem Präfix der eigenen Sicherungen und einen symbolischen Link — außer im Papierkorb, und dort nur den Link, nie sein Ziel. Diese Sperre fängt einen Übersetzungsfehler ab, bevor er Schaden anrichtet; sie darf bei einer Vereinfachung nicht wegfallen.

### Einhängepunkte, Links und hängende Läufe

Was eingehängt ist — eine Netzfreigabe, ein anderer Datenträger, ein Bind-Mount —, fassen die Skripte nicht an: nicht löschen, nicht durchlaufen, nicht einmal lesen oder zählen. Der Anlass war der erste Lauf des installierten Skills: Der Probelauf zu `__pycache__` blieb in einer SMB-Freigabe unter dem Home hängen, deren Server nicht antwortete. Der Prozess stand im Kernel (Zustand `D`) und ließ sich auch mit `kill -KILL` nicht sofort beenden. Deshalb entscheiden die Skripte über Einhängepunkte nach dem Namen, gegen `/proc/self/mountinfo`, bevor sie irgendeinen Zugriff auf den Pfad machen; die Liste wird höchstens einmal je Sekunde neu gelesen. Im Home wird nichts angefasst, was auf einem anderen Einhängepunkt liegt als das Home selbst, auch kein fester Pfad und kein Ziel eines Links. Symbolische Links werden nicht verfolgt; einzige Ausnahme sind die Starter-Einträge für Tabelle 2, deren Linkziel nur gelesen wird, wenn es auf keinem fremden Einhängepunkt liegt. Der Füllstand zeigt nur lokale Dateisysteme, und Papierkörbe auf anderen Datenträgern bleiben unberührt: Der Nutzer leert sie an ihrem Ort. Der Zielort einer Archivsicherung, den der Nutzer wählt, auch eine Netzfreigabe, wird nur beschrieben.

Steht ein Durchlauf länger als 5 Sekunden in demselben Ordner, schreibt das Skript alle 5 Sekunden eine Zeile mit dem Ordner nach `stderr`, und beim Weitergehen sofort eine weitere. Damit ist ein Hänger am Ort sichtbar. Gegen das Hängen selbst helfen Zeitgrenzen nicht, solange der Prozess im Kernel wartet; deshalb steht die Vermeidung an erster Stelle. Die Stillstände stehen auch als Liste `stalls` in den Berichten. Externe Befehle werden nicht überwacht. Die Protokollsuche (`analyze.py --find-protocol`) läuft nach denselben Regeln und braucht kein `sudo`.

### Was „Cache“ hier heißt

Ein Ordner gilt nur dann als löschbarer Cache, wenn belegt ist, dass das Programm seine Daten jederzeit vollautomatisch wiederherstellt und ihr Fehlen bis auf Zeitverlust nichts ändert. Wie ein Ordner heißt, zählt nicht. Proxy-Dateien eines Videoschnittprogramms etwa sind kein Cache, auch wenn sie in einem Ordner dieses Namens liegen sollten: Sie entstehen in einem eigenen Arbeitsschritt und kommen nicht von selbst zurück.

### Belege und Herkunft der Regeln

Applikationsbezogene Regeln wurden bisher erarbeitet für:

- Firefox
- Chrome
- VS Code
- Docker

Beachte, dass die Regeln auch veralten können und verfolge die Arbeit des Agenten aufmerksam.

Die Festlegungen samt Begründungen und Messbefunden stehen in `plan/concept.md`; die Tests, auf denen die Regeln für die Applikationen beruhen, liegen unter `tests/`. Beides ist Entwicklungsmaterial, reist nicht mit ins Paket und verbleibt in der Entwicklungssprache des Autors.

Das Alter einer Datei bestimmen die Skripte aus der späteren von Änderungs- und Statusänderungszeit; das Anlegedatum liefert Python unter Linux nicht. Eine Datei erscheint damit höchstens jünger, als sie ist, und wird im Zweifel nicht gelöscht.

## Stand und Offenes

**Status:** Skilltext und Skripte sind geschrieben. Analyse, Journal-Auswertung, Snapshots (btrfs) und Archive sind am Entwicklungsrechner gelaufen, das Löschen ist in einer Simulation geprüft (`tests/test_delete.py`), die Skripte außerdem in eigenen Tests (`tests/`), darunter `tests/test_mounts.py`, der jeden Dateizugriff auf simulierte Einhängepunkte protokolliert. Noch nicht an einer echten Einhängung geprüft ist der Fall mit `tmpfs`; das folgt in einem Probelauf am Rechner.

**Offen** (Reihenfolge im Fahrplan, `plan/work-plan.md`):

- Der vollständige Lauf des installierten Skills mit echten Löschungen als Abschluss.
- Die englische Fassung; erst danach entfällt das Baustellenschild.
- Eine Nachprobe zum Docker-Build-Cache.
- Die Web-Fassung ist noch nicht erprobt.

**Bewusst offen gelassen:** Für einige Bereiche ist noch keine Behandlung festgelegt — Suchindex Baloo, Git-Repositories, Vorschaubilder, Zwischenspeicher von Claude Desktop, Flatpak, Snap, AppImage und Wine, Python-Umgebungen, Toolchains, Syncthing-Versionen, Duplikate und Migrationsreste. Der Skill zeigt sie in Tabelle 3 und erforscht sie auf Wunsch gemeinsam mit dem Nutzer, löscht dort aber nichts nach eigenen Regeln.
