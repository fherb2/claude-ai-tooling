# linux-desktop-clean-up — einen Linux-Desktop aufräumen, ohne Arbeitsdaten zu gefährden

*Stand: 2026-11-06*

**🚧 In Arbeit.** Skilltext und Skripte sind geschrieben und an einem Entwicklungsrechner geprüft; der vollständige Lauf mit echten Löschungen steht noch aus, ebenso die englische Fassung und die Installationspakete (siehe „Stand und Offenes“). — Für Claude Code und claude.ai.

---

## Überblick

**Der Skill räumt einen Linux-Desktop oder -Laptop auf und löscht dabei nur, was nachweislich unnütz ist.** Er misst zuerst, was auf dem Rechner liegt, zeigt den Füllstand der Dateisysteme und drei Tabellen und arbeitet sie dann gemeinsam mit dem Nutzer ab: Caches von Firefox, Chrome und VS Code, der Paketcache von apt, Log-Files und Journal, der pip-Cache, Python-Bytecode, Docker-Reste, der Download-Ordner, liegengebliebene Installationsdateien, Images und Archive, vergessene Mediendateien und zuletzt der Papierkorb.

Was ohne Rückfrage gelöscht wird, ist eng begrenzt: programmeigene Zwischendateien, die das Programm nicht mehr braucht oder jederzeit vollautomatisch neu erzeugt. Alles, was dem Nutzer gehört — Downloads, Installationsdateien, Medien, der Inhalt des Papierkorbs —, wird nur nach seiner Auswahl gelöscht. Vor jedem Löschen gibt es einen Probelauf, der zeigt, was tatsächlich weg wäre.

**Abgrenzung:** Der Skill entfernt keine installierte Software, auch keine, die vermutlich niemand mehr braucht; er meldet sie nur. Er ist für Desktops und Laptops gedacht (Ubuntu, Kubuntu und ähnliche), nicht für Server. Was eingehängt ist — ein anderes Dateisystem oder ein Bind-Mount —, wird nie durchlaufen und nie gelöscht.

Der Skill wird nur auf ausdrücklichen Aufruf angewendet: `/linux-desktop-clean-up`. Er lädt sich nicht von selbst.

## Installation

### Claude Code

1. **Paket herunterladen.** `downloads/linux-desktop-clean-up_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `linux-desktop-clean-up/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

### claude.ai und Claude Desktop (Chat + Cowork)

1. **Paket herunterladen.** `downloads/linux-desktop-clean-up_de_web.zip`

2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.

## Details

### Wie der Skill arbeitet

Der Skill startet selbst keine Befehle auf dem Rechner. Er gibt dem Nutzer Befehlsblöcke; der Nutzer führt sie aus, auch alles, was `sudo` braucht. Die Ergebnisse landen als Dateien in `/tmp`, wo der Skill sie liest. In Claude Code liegen die drei Skripte im Skill-Ordner; auf claude.ai bekommt der Nutzer sie als Download und lädt die Ergebnisdateien wieder hoch.

Ablauf:

1. Zweck und Arbeitsweise erklären, Bestätigung einholen, die Größenschwelle für große Dateien abfragen (Vorgabe 150 MiB) und ob auch Archive erfasst werden sollen.
2. Umgebung ermitteln: Desktop und die Benutzerordner nach XDG — Ordnernamen wie „Downloads“ oder „Bilder“ setzt der Skill nie selbst ein, sie heißen je nach Sprache anders.
3. Analyse: ein einziger Durchlauf durch Home, `/var`, `/opt`, `/usr/local` und `/srv`, nur lesend.
4. Füllstand und drei Tabellen: **Tabelle 1** — durch Tests gesicherte Bereiche; **Tabelle 2** — Cache-Ordner weiterer Programme, die der Skill zur Laufzeit recherchiert, mit Belegstufe; **Tabelle 3** — Statistik zum gemeinsamen Erforschen (Größe je Verzeichnis, große Dateien, Reste deinstallierter Programme, Duplikate, Entwicklungsartefakte).
5. Bereich für Bereich: Einzelheiten zeigen, Entscheidung einholen, Probelauf, nach Bestätigung echter Lauf.
6. Ergebnisbericht: was gelöscht wurde und wie viel, was übersprungen und was nur gemeldet wurde.

### Die Skripte

| Datei | Aufgabe |
| --- | --- |
| `analyze.py` | die Analyse; schreibt `/tmp/cleanup-analysis.json` |
| `journal_stats.py` | die Auswertung von Journal und Log-Files beim Bearbeiten dieses Bereichs; schreibt `/tmp/cleanup-journal.json` |
| `delete.py` | das Löschen, ein Bereich je Lauf, mit Probelauf (`--dry-run`); schreibt `/tmp/cleanup-report-<Bereich>.json` |

Alle drei brauchen nur Python 3 mit der Standardbibliothek. Ihre Bildschirmmeldungen sind englisch; mit dem Nutzer spricht der Skill in dessen Sprache.

### Was das Löschskript immer verweigert

Unabhängig vom Auftrag löscht `delete.py` nie: `/`, das Home selbst, einen Ordner direkt unter `/` oder direkt unter dem Home, irgendetwas unter `/boot`, etwas außerhalb von Home, `/var`, `/opt`, `/usr/local` und `/srv`, einen Einhängepunkt oder einen Ordner, der einen enthält, und einen symbolischen Link — außer im Papierkorb, und dort nur den Link, nie sein Ziel. Diese Sperre fängt einen Übersetzungsfehler ab, bevor er Schaden anrichtet; sie darf bei einer Vereinfachung nicht wegfallen.

### Was „Cache“ hier heißt

Ein Ordner gilt nur dann als löschbarer Cache, wenn belegt ist, dass das Programm seine Daten jederzeit vollautomatisch wiederherstellt und ihr Fehlen bis auf Zeitverlust nichts ändert. Wie ein Ordner heißt, zählt nicht. Proxy-Dateien eines Videoschnittprogramms etwa sind kein Cache, auch wenn sie in einem Ordner dieses Namens liegen: Sie entstehen in einem eigenen Arbeitsschritt und kommen nicht von selbst zurück.

### Belege und Herkunft der Regeln

Die Festlegungen samt Begründungen und Messbefunden stehen in `plan/concept.md`; die Tests, auf denen die Regeln für Firefox, Chrome, VS Code und Docker beruhen, liegen unter `tests/`. Beides ist Entwicklungsmaterial und reist nicht mit ins Paket.

Das Alter einer Datei bestimmen die Skripte aus der späteren von Änderungs- und Statusänderungszeit; das Anlegedatum liefert Python unter Linux nicht. Eine Datei erscheint damit höchstens jünger, als sie ist, und wird im Zweifel nicht gelöscht.

## Stand und Offenes

**Status:** Skilltext und Skripte sind geschrieben; Analyse, Journal-Auswertung und Probeläufe des Löschskripts sind am Entwicklungsrechner gelaufen, das Löschen ist in einer Simulation geprüft (`tests/test_delete.py`).

**Offen** (Reihenfolge im Fahrplan, `plan/work-plan.md`):

- Der vollständige Lauf mit echten Löschungen als Abschluss.
- Die englische Fassung und die Installationspakete; erst danach entfällt das Baustellenschild.
- Eine Nachprobe zum Docker-Build-Cache.
- Löschen in Tabelle 2 (recherchierte Cache-Ordner weiterer Programme): Das Löschskript nimmt dafür noch keinen Auftrag an.
- Download-Ziele, die ein Browser abweichend vom Standard eingestellt hat: Die Analyse erfasst bisher nur den Download-Ordner nach XDG.
- Die Web-Fassung ist noch nicht erprobt.

**Bewusst offen gelassen:** Für einige Bereiche ist noch keine Behandlung festgelegt — Suchindex Baloo, Git-Repositories, Vorschaubilder, Zwischenspeicher von Claude Desktop, Flatpak, Snap, AppImage und Wine, Python-Umgebungen, Toolchains, Syncthing-Versionen, Duplikate und Migrationsreste. Der Skill zeigt sie in Tabelle 3 und erforscht sie auf Wunsch gemeinsam mit dem Nutzer, löscht dort aber nichts nach eigenen Regeln.
