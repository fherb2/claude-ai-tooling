# Pack Source for AI

*Stand: 2026-08-24*

Ein **Shell-Skript, das die Quelldateien eines Projekts in einer einzigen, strukturierten Textdatei bündelt** – bereit zum Hochladen in die Knowledge Base eines KI-Agenten.

Nützlich für die Arbeit über Web-KI-Agenten bzw. in einer unsicheren Umgebung, in der der KI-Agent keinen direkten Zugriff auf den Rechner haben soll.

**Beispielnutzung** mit Claude:

1. `./packsrc.sh` auf der Kommandozeile.
2. Neues File `project_source.txt` zu Claude.ai in das Projektwissen ziehen.

   Fertig. Der gesamte Quellcode liegt im File; strukturiert durchsuchbar.

> **Hinweis:** Der erzeugte Header in `project_source.txt` beschreibt nur das Format – er richtet sich an keinen bestimmten KI-Agenten und weist auch keinen an, etwas zu tun. Die eigentlichen Anweisungen liegen in `project_source.instructions.md` (Option `-i`), das dort eingetragen wird, wo der Agent seine Anweisungen entgegennimmt. Grund: Mehrere Agenten behandeln den Inhalt hochgeladener Dokumente bewusst als Daten und befolgen darin enthaltene Anweisungen nicht zuverlässig.

---

## Übersicht

`packsrc.sh` sammelt Quelldateien aus einem oder mehreren Projektverzeichnissen in einer einzigen `project_source.txt`. Jede Datei wird in eindeutige Metadaten-Blöcke eingebettet, die es einem KI-Agenten – oder jedem anderen Tool – ermöglichen:

- zu erkennen, welche Dateien enthalten sind und wo sie im Projektbaum liegen,
- aktuelle Index-Ergebnisse anhand eines laufbezogenen Zeitstempels von veralteten, gecachten zu unterscheiden.

Der Hauptanwendungsfall ist das Hochladen von `project_source.txt` als Wissensdokument zu einem KI-Agenten (etwa [Claude](https://claude.ai)), wodurch dieser an einer einzigen Stelle präzisen und aktuellen Kontext über die gesamte Codebase erhält.

**Es lassen sich somit auch mit Web-Versionen von KI-Agenten Softwareentwicklungen vorantreiben oder Code auf Fehler untersuchen und ändern.** Das ist nicht ganz so bequem, als den Code gleich im Projekt vom Agenten lesen und bearbeiten zu lassen, aber weit weniger zeitproblematisch, als man śich es vorstellen würde. Auf diese Weise lässt sich **in sicherheitskritischen Umgebungen** arbeiten, wo der schwach oder nicht überwachte Zugriff auf Systemressourcen unzulässig ist. (Zur weiteren Optimierung dieser Nutzungsart, wird ist ein Skill in Vorbereitung.)

### .gitignore-Eintrag nicht vergessen

Das Ausgabefile enthält den gesamten Quelltext und würde im Git-Repo sinnlos redundanten Speicherplatz kosten. Deshalb den Eintrag (einschließlich des kurzen Beschreibungsfiles) nicht vergessen:

```plaintext
# packaged source code by packsrc script and it's AI instruction file
project_source.txt
project_source.instruction.md
```

---

## Funktionen

Die **Konfigurationen erfolgt im Kopf des Scriptes**, sodass das Script üblicherweise völlig ohne Argumente und ohne Konfigurationsfile im Projekt gestartet wird und das Quellcode-Textfile `project_source.txt` erstellt.

Das Textfile ist **mit Meta-Prefixen** `#!PKSRC: ...` **strukturiert**, und durch einen Header **selbstbeschreibend**. Die Verarbeitung durch einen KI Agenten kann aber mit dem Hilfsfile `project_source.instruction.md` optimiert werden.

- **Mehrere Quellverzeichnisse** — pro Lauf werden ein oder mehrere Quellverzeichnisse gescannt; konfigurierbar über `SOURCE_DIRS`.
- **Rekursiver Gesamt-Scan** — mit `"./"` als `SOURCE_DIRS`-Eintrag wird das gesamte Projekt-Wurzelverzeichnis rekursiv gescannt, statt einzelne Unterverzeichnisse aufzulisten.
- **Konfigurierbare Dateiendungen** — legt fest, welche Suffixe immer eingeschlossen werden; über CLI-Flags (`-md`, `-txt`) lassen sich temporär weitere hinzufügen.
- **Dateien ohne Endung** — ein Leerstring-Eintrag (`""`) in `BASE_EXTENSIONS` erfasst Dateien, die überhaupt keinen Punkt im Namen haben (z. B. `Dockerfile`, `Makefile`).
- **Explizite Dateiliste** — `EXPLICIT_FILES` nimmt einzelne Dateien anhand des exakten Namens oder Pfads statt anhand der Endung auf, sodass unbeteiligte Dateien mit derselben Endung nicht versehentlich mit hineingezogen werden; auch Dateien außerhalb von `SOURCE_DIRS` (einschließlich des Projekt-Wurzelverzeichnisses) lassen sich so ergänzen.
- **Verzeichnisausschluss** — überspringt Build-Artefakte, Caches oder Backup-Ordner anhand des bloßen Verzeichnisnamens, in beliebiger Tiefe, über `EXCLUDE_DIRS`.
- **Standardmäßiger Punkt-Ausschluss** — Dateien und Verzeichnisse, deren Name mit `.` beginnt (z. B. `.git`, `.vscode`, `.env`, `.gitignore`), werden bei `SOURCE_DIRS`-Scans immer übersprungen, sofern sie nicht explizit in `EXPLICIT_FILES` aufgeführt sind.
- **Strukturierte `#!PKSRC`-Metadaten-Marker** — jeder Datei-Block trägt einen laufbezogenen Zeitstempel und den individuellen letzten Änderungszeitpunkt der Datei.
- **Selbstbeschreibender Header** — eine Präambel erklärt in drei einzeln durchsuchbaren Abschnitten (`NOTE_TO_READER`, `FORMAT_DESCRIPTION`, `DATE_TIME_CHECK`), wie die Datei aufgebaut ist und woran sich veraltete Suchergebnisse erkennen lassen. Jeder Abschnitt trägt einen eigenen `#!PKSRC`-Marker, sodass auch ein einzelnes Bruchstück der Datei noch selbsterklärend ist, wenn ein Retrieval-System nur dieses ausliefert.
- **Anweisungsdatei für KI-Agenten** — `-i` schreibt zusätzlich `project_source.instructions.md` mit den eigentlichen Anweisungen. Header und Anweisungsdatei speisen sich aus denselben Textblöcken im Skript und können deshalb nicht auseinanderlaufen.
- **Robuster Umgang mit fehlenden Einträgen** — ein nicht existierender `SOURCE_DIRS`- oder `EXPLICIT_FILES`-Eintrag erzeugt eine Warnung auf stderr; die übrige Ausgabe wird normal erzeugt.
- **Alphabetisch sortierte Ausgabe** — Dateien werden verzeichnisübergreifend nach Pfad sortiert, sodass das Ergebnis deterministisch und leicht zu diffen ist. Dateien mit identischem Namen in unterschiedlichen Verzeichnissen werden NICHT dedupliziert — jede wird einzeln aufgeführt, unterscheidbar anhand ihres Pfads im Block-Header.

---

## Anforderungen


| Anforderung | Hinweise                                             |
| ----------- | ---------------------------------------------------- |
| Bash ≥ 4.0 | Standard unter Linux                                 |
| GNU `find`   | Standard unter Linux; macOS: `brew install findutils` |
| GNU `stat`   | Standard unter Linux; macOS: `brew install coreutils` |
| GNU `date`   | Standard unter Linux; macOS: `brew install coreutils` |

> **Hinweis für macOS:** Das Skript verwendet `stat -c` und `date -d`, beides GNU-Erweiterungen. Installiere unter macOS [coreutils](https://formulae.brew.sh/formula/coreutils) über Homebrew und stelle sicher, dass die GNU-Tools im `PATH` liegen (die Homebrew-Formel erklärt, wie das geht).

---

## Installation

Kopiere das Skript in das Wurzelverzeichnis deines Projekts – weitere Abhängigkeiten sind nicht nötig:

```bash
git clone https://codebase.helmholtz.cloud/FWF/tools/pack-source-for-ai.git
cp pack-source-for-ai/packsrc.sh /path/to/your/project/
chmod +x /path/to/your/project/packsrc.sh
```

Das Skript ist bewusst in sich geschlossen gehalten, sodass es unverändert in jedes beliebige Projekt eingesetzt werden kann (nur der Script-Abschnitt `CONFIGURATION` wird bearbeitet).

---

## Konfiguration

Öffne das Skript und bearbeite den Abschnitt `CONFIGURATION` nahe dem Anfang – alles unterhalb der `DO NOT EDIT`-Zeile wird von diesen Variablen gesteuert:

```bash
# Zu scannende Verzeichnisse (relativ zum Skript, ohne führendes ./)
# Standard: ("source") — behält das klassische Einzelverzeichnis-Layout bei
# "./" scannt statt eines benannten Unterverzeichnisses das gesamte Projekt-Wurzelverzeichnis rekursiv
# Ein paar Beispiele:
SOURCE_DIRS=("source" "shared" "tools" "tests" "submodules")

# Dateiendungen, die bei jedem Lauf eingeschlossen werden (ohne führenden Punkt)
# "" erfasst Dateien, die überhaupt keinen Punkt im Namen haben (z. B. "Dockerfile")
# Der Standard ist ein Beispiel für Python+CUDA-Anwendungsfälle:
BASE_EXTENSIONS=("py" "cu")

# Verzeichnisnamen, die in beliebiger Tiefe innerhalb der gescannten Bäume ausgeschlossen werden
# Beispiel
EXCLUDE_DIRS=("backup" "__pycache__" ".git")

# Einzelne Dateien, die anhand des exakten Namens/Pfads statt der Endung eingeschlossen werden
EXPLICIT_FILES=("Dockerfile.watchdog" "./docker-compose.yml" "~/.config/foo.conf")
```


| Variable          | Standard                   | Beschreibung                                                                                                                                                                                        |
| ----------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SOURCE_DIRS`     | `("source")`               | Zu scannende Verzeichnisse. Relative Pfade, ohne führendes `./`. `"./"` scannt das gesamte Projekt-Wurzelverzeichnis rekursiv. Nicht existierende Einträge werden mit einer Warnung übersprungen. |
| `BASE_EXTENSIONS` | `("py" "cu")`              | Immer eingeschlossene Dateiendungen. `""` erfasst Dateien, die überhaupt keinen Punkt im Namen haben.                                                                                               |
| `EXCLUDE_DIRS`    | `("backup" "__pycache__")` | Verzeichnisnamen, die in jedem gescannten Baum in beliebiger Tiefe ausgeschlossen werden.                                                                                                           |
| `EXPLICIT_FILES`  | `()`                       | Einzelne Dateien, die anhand des exakten Namens/Pfads eingeschlossen werden — siehe unten.                                                                                                         |

### `EXPLICIT_FILES`-Eintragsformen


| Form                             | Beispiel                 | Bedeutung                                                                                                                                                                                |
| -------------------------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reiner Name (kein führendes `/`) | `"Dockerfile.watchdog"`  | Wird anhand des exakten Dateinamens irgendwo innerhalb von `SOURCE_DIRS` gesucht. `EXCLUDE_DIRS` gilt weiterhin; der standardmäßige Punkt-Ausschluss wird für diesen Eintrag umgangen. |
| `./relative/path`                | `"./docker-compose.yml"` | Exakt eine Datei, relativ zum Projekt-Wurzelverzeichnis.                                                                                                                                 |
| `/absolute/path`                 | `"/etc/hosts"`           | Exakt eine Datei, absoluter Pfad auf dem Rechner.                                                                                                                                        |
| `~/path`                         | `"~/.config/foo.conf"`   | Exakt eine Datei, relativ zum Home-Verzeichnis des Benutzers.                                                                                                                            |

Alle drei pfadpräfigierten Formen (`./`, `/`, `~/`) umgehen immer den standardmäßigen Punkt-Ausschluss, da sie jeweils eine einzelne, konkrete Datei explizit benennen.

### Standardmäßiger Punkt-Ausschluss

Jede Datei oder jedes Verzeichnis, deren/dessen bloßer Name mit `.` beginnt (z. B. `.git`, `.vscode`, `.env`, `.gitignore`), wird bei `SOURCE_DIRS`-Scans überall und in beliebiger Tiefe übersprungen – sowohl beim regulären `BASE_EXTENSIONS`-Abgleich als auch bei der Suche nach reinen Namen in `EXPLICIT_FILES`. Das ist immer aktiv und nicht konfigurierbar. Der einzige Weg, eine solche Datei doch einzuschließen, besteht darin, sie explizit in `EXPLICIT_FILES` über die Form `./`, `/` oder `~/` aufzuführen.

---

## Verwendung

```bash
# Standardlauf — verwendet SOURCE_DIRS, BASE_EXTENSIONS, EXCLUDE_DIRS und
# EXPLICIT_FILES aus der Konfiguration
./packsrc.sh

# Für diesen Lauf zusätzlich Markdown-Dateien einschließen (wird nicht in BASE_EXTENSIONS gespeichert)
./packsrc.sh -md

# Für diesen Lauf zusätzlich reine Textdateien einschließen
./packsrc.sh -txt

# Zusätzlich die Anweisungsdatei für KI-Agenten schreiben
./packsrc.sh -i

# Flags kombinieren
./packsrc.sh -md -txt

# Hilfe anzeigen
./packsrc.sh -h
```

**Die Ausgabe** wird immer nach `./project_source.txt` geschrieben, **in das Verzeichnis, aus dem das Skript aufgerufen wird**. Die Datei wird bei jedem Lauf ungefragt überschrieben. Mit `-i` entsteht daneben `./project_source.instructions.md`; deren Inhalt hängt nicht vom Lauf ab, ein erneuter Aufruf schreibt also eine identische Datei.

---

## Ausgabeformat

**`project_source.txt` ist eine reine Textdatei mit folgender Struktur:**

```
#!PKSRC:HEADER:BEGIN | project_source.txt | pksrc_ts: 2025-03-14_10-23-45
#
#!PKSRC:HEADER:NOTE_TO_READER
# < wofür die beiden folgenden Abschnitte da sind >
#
#!PKSRC:HEADER:FORMAT_DESCRIPTION
# < Aufbau der Datei und Bedeutung der Felder >
#
#!PKSRC:HEADER:DATE_TIME_CHECK
# < woran veraltete Suchergebnisse zu erkennen sind >
#
#!PKSRC:HEADER:END

#!PKSRC:FILE:BEGIN | ./source/main.py | pksrc_ts: 2025-03-14_10-23-45 | file_mtime: 2025-03-13_18-42-01
< file contents >

#!PKSRC:FILE:END | ./source/main.py

#!PKSRC:FILE:BEGIN | ./shared/utils.py | pksrc_ts: 2025-03-14_10-23-45 | file_mtime: 2025-03-12_09-15-33
< file contents >

#!PKSRC:FILE:END | ./shared/utils.py
```

### Metadaten-Felder


| Feld         | Geltungsbereich | Beschreibung                                                                        |
| ------------ | --------------- | ----------------------------------------------------------------------------------- |
| `pksrc_ts`   | Laufebene       | Zeitstempel dieses Skriptaufrufs. Identisch für jeden Block innerhalb einer Datei. |
| `file_mtime` | Dateiebene      | Letzter Änderungszeitpunkt der einzelnen Quelldatei zum Zeitpunkt des Laufs.       |

Das Präfix `#!PKSRC` kommt in normalem Python-, CUDA-, Shell- oder Konfigurations-Quellcode nicht vor, wodurch die Marker eindeutig bleiben, selbst wenn die Datei als Volltext-Suchindex verwendet wird.

### Erkennung veralteter Ergebnisse

Der Abschnitt `DATE_TIME_CHECK` im Header beschreibt den Zusammenhang: Jeder Block wiederholt den `pksrc_ts` des Laufs, aus dem er stammt. Antwortet ein Agent aus einem früheren, gecachten Suchergebnis, trägt der zitierte Inhalt einen älteren `pksrc_ts` als die `#!PKSRC:HEADER:BEGIN`-Zeile der aktuell hochgeladenen Datei. Weichen die beiden Werte voneinander ab, ist das Ergebnis überholt.

`file_mtime` erlaubt dir (und der KI) zu überprüfen, ob eine bestimmte Quelldatei bei einem gegebenen Implementierungsschritt tatsächlich angefasst wurde, ohne die Git-Historie nachsehen zu müssen.

### Anweisungsdatei `project_source.instructions.md`

Der Header beschreibt, er weist nicht an. Das ist Absicht: Mehrere KI-Agenten behandeln den Inhalt hochgeladener Dokumente bewusst als Daten und befolgen darin enthaltene Anweisungen nicht zuverlässig — im Extremfall werden sie als Injektionsversuch bewertet. Verlässlich befolgt wird nur, was im dafür vorgesehenen Kanal steht.

`./packsrc.sh -i` schreibt deshalb zusätzlich `project_source.instructions.md`. Deren Inhalt trägst du dort ein, wo dein Agent seine ständigen Anweisungen entgegennimmt — Projektanweisungen bei Claude, das Instructions-Feld eines Gemini-Gems, `AGENTS.md`, `CLAUDE.md` oder der System-Prompt deines eigenen Tooling.

Die beiden Abschnitte `FORMAT_DESCRIPTION` und `DATE_TIME_CHECK` stehen im Skript genau einmal, in den Funktionen `emit_format_description` und `emit_date_time_check`; Header und Anweisungsdatei werden beide daraus gebaut. Wer den Wortlaut ändern will, ändert ihn dort — **nicht** in `project_source.instructions.md`, die beim nächsten `-i`-Lauf überschrieben wird. Die in diesem Repository liegende Fassung ist genau so erzeugt und dient als Vorschau; wer nur `packsrc.sh` in ein eigenes Projekt kopiert, erzeugt sie dort mit `-i` selbst.

---

## Typischer Workflow

1. **Einmal konfigurieren** — `SOURCE_DIRS`, `BASE_EXTENSIONS`, `EXCLUDE_DIRS` und `EXPLICIT_FILES` für dein Projekt festlegen.
2. **Einmal einrichten** — `./packsrc.sh -i` aufrufen und den Inhalt von `project_source.instructions.md` in die ständigen Anweisungen deines KI-Agenten eintragen.
3. **Neu erzeugen** — das Skript nach jedem relevanten Commit oder jeder Arbeitssitzung ausführen.
4. **Hochladen** — `project_source.txt` in die Knowledge Base deines KI-Projekts legen (z. B. als Projektdokument in Claude).
5. **Arbeiten** — die KI verfügt nun über präzisen, zeitgestempelten Kontext für alle Quelldateien und kann veraltete Index-Ergebnisse erkennen.

Es empfiehlt sich, `project_source.txt` in die `.gitignore` aufzunehmen, da es sich um ein generiertes Artefakt handelt.

---

## Entwicklung / Tests

Ein Abnahme-/Regressionstest für dieses Skript liegt in `full_script_test.py` vor.

**Anforderungen:** Python 3.10+, ausschließlich Standardbibliothek — keine Drittanbieter-Pakete, keine virtuelle Umgebung nötig. Getestet gegen das System-Python 3.12 unter Ubuntu 24.04. Sollte ein künftiger Test einmal ein Paket außerhalb der Standardbibliothek benötigen, zuerst eine projektlokale virtuelle Umgebung einrichten (z. B. `python3 -m venv .venv && source .venv/bin/activate`).

**Ausführen:**

```bash
python3 full_script_test.py
```

**Was der Test macht:** Der Test baut unter `./test_project/` einen isolierten Fixture-Baum auf, der die Rolle eines simulierten Projekt-Wurzelverzeichnisses übernimmt (sodass `SOURCE_DIRS=("./")`, `EXPLICIT_FILES`-Einträge auf Projektwurzel-Ebene usw. alle durchgespielt werden können). Für jedes von mehreren Szenarien (benannte `SOURCE_DIRS`-Einträge, der rekursive `"./"`-Eintrag, das `-md`-Flag) erzeugt er eine szenariospezifische *Kopie* von `packsrc.sh` mit angepasstem `CONFIGURATION`-Block, führt diese Kopie aus und vergleicht die resultierende `project_source.txt` mit der erwarteten Dateimenge. **Das echte `packsrc.sh` wird dabei nie verändert.**

- Bei Erfolg werden `test_project/` und `test_results/` wieder gelöscht; es bleibt nur der PASS/FAIL-Bericht in der Konsole.
- Bei einem Fehlschlag (oder einem unerwarteten Fehler) bleiben beide Verzeichnisse zur manuellen Inspektion erhalten, und das Skript gibt ihre Pfade aus.
- In jedem Fall werden beide Verzeichnisse zu *Beginn* jedes Laufs geleert und neu aufgebaut, sodass ein vorheriger fehlgeschlagener Lauf den nächsten nie beeinflussen kann.

Um neue Testfälle hinzuzufügen (Fixture-Dateien oder ganz neue Szenarien), siehe den Modul-Docstring am Anfang von `full_script_test.py` — er dokumentiert beide Erweiterungspunkte im Detail.

Nimm auch `test_project/` und `test_results/` in die `.gitignore` auf, für den Fall, dass ein fehlgeschlagener Lauf sie einmal zurücklässt.

---

## Versionshistorie

- **2026-06-19** — Erste Version.
- **2026-07-03** — `EXPLICIT_FILES`-Konfiguration hinzugefügt (Formen: reiner Name / `./` / `/` / `~/`), Leerstring-Eintrag in `BASE_EXTENSIONS` für Dateien ohne Endung, rekursiver `"./"`-Eintrag in `SOURCE_DIRS`, standardmäßiger Punkt-Ausschluss für versteckte Dateien/Verzeichnisse, Abnahmetest-Suite `full_script_test.py` sowie die Kommandozeilenoptionen `-h`/`--no-cleanup`/`--clean-up`.
- **2026-08-15** – Umgebaut für einen Einsatz mit beliebigen KI Agenten, Selbstbeschreibung verbessert, erstellt ein separates Anweisungsfile für KI Agenten

---

## Lizenz

Der Lizenztext folgt im Original (Englisch), um Übersetzungsungenauigkeiten zu vermeiden.

MIT License

Copyright (c) 2025 Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
