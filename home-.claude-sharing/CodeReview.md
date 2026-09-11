# Code-Review `home-.claude-sharing` — 11. September 2026

**Anlass:** Besichtigung vor dem ersten heißen Test nach der Umstellung auf Mehrsprachigkeit. **Geprüfter Stand:** Zweig `dev`, letzter Commit `c9a6e27`; der Arbeitsbaum war laut Sitzungsstart sauber (nicht selbst per Git geprüft, weil kein Kommando ausgeführt werden durfte).

**Vorgehen:** rein lesend. Keine Datei des Vorhabens wurde verändert, kein Test gelaufen, kein Dienst berührt. Die einzige geschriebene Datei ist diese. Ausgeführt wurden nach ausdrücklicher Freigabe genau zwei lesende Kommandos: die Dateiliste des Ordners (`find … -type f`) und die Rechte in `files/` (`ls -la`); ihr Ergebnis steht als Nachtrag in Abschnitt VI. Geprüft wurden die Dateien, die 2.7, 3.8 und die README benennen — die Liste bestätigt, dass es keine weiteren gibt.

**Geprüft wurde:** `files/claude_sync_watchd.py` (1864 Zeilen) vollständig gegen die Kapitel 2.1–2.9 und 3.1–3.5; `files/messages.py`, `files/messages_de.py`, `files/messages_en.py` gegeneinander und gegen jeden `T(...)`-Aufruf im Wächter; `files/install_service.sh` und `files/uninstall_service.sh` gegen 3.5; `files/claude-sync-watch.service`; `files/.stignore` gegen 3.9; `files/conflict-resolution.de.md` und `.en.md` gegen 3.4 und gegeneinander; `scripts/pack_packages.sh` gegen 2.7; `tests/test_dialog_and_naming.py` (2063 Zeilen) gegen 3.8 und gegen den Wächter; `README.md` und `README.en.md` gegeneinander und gegen die Dateinamen; Anhang B vollständig, damit kein erledigter oder abgelehnter Befund erneut aufgeführt wird.

**Nicht geprüft:** die drei Handproben-Skripte in `tests/` samt ihrem Helfer `echo_test_helper.sh` (sie importieren den Wächter nicht, 3.8), die Konfigurationsanleitung, `offener_fall_chatprotokolle.md`, der Inhalt der beiden Zip-Pakete, das Verhalten realer Terminal-Emulatoren, und alles, was einen Lauf braucht.

**Kennzeichnung** wie im Review vom 13. August: `[A]` Doku anpassen, `[C]` Code anpassen, `[A+C]` beides. Neu je Befund: eine **Schwere** (kritisch / hoch / mittel / niedrig) und die Angabe, ob er **vor dem heißen Test** behoben sein sollte. Wo ich aus Wissen über Fremdsoftware schließe statt am Code zu lesen, steht **Vermutung** und dazu, wie es zu prüfen wäre. Zeilennummern sind Zusatzmarker zum Stand `c9a6e27`; die Adresse ist der genannte Funktions- oder Kommentarname.

---

## Überblick

| Nr. | Befund | Schwere | Vor dem Test beheben? |
| --- | --- | --- | --- |
| 1 | `session_running` wirft `TypeError`, sobald eine Konfliktsitzung länger als dreißig Minuten läuft und ihr Terminal noch lebt | **kritisch** | **ja** |
| 2 | Die Laufsperre kann nach einem Rechnerneustart dauerhaft einem fremden Prozess gehören — der Wächter steht dann still, ohne Journalzeile | hoch | nicht zwingend; die Journalzeile für abgewiesene Durchgänge empfohlen |
| 3 | Fehlender Meldungskatalog endet mit Rückgabewert 1 und damit in der Neustartschleife, die 3.5 mit dem Wert 78 gerade verhindert | mittel | empfohlen (wenige Zeilen) |
| 4 | `notify` fängt nur `FileNotFoundError`; jeder andere Fehler des Aufrufs bricht den Durchgang ab und hält die Meldung dauerhaft fällig | mittel | nein |
| 5 | `xdg-terminal-exec --`: der Trenner ist ungeprüft und möglicherweise falsch (Vermutung) | mittel | nur auf einem Rechner, der `xdg-terminal-exec` hat |
| 6 | Erschöpfte inotify-Kontingente ließen `observer.schedule` mit einer Ausnahme scheitern — Rückgabewert 1, Neustartschleife (Vermutung zur Wahrscheinlichkeit, nicht zum Weg) | niedrig | nein |
| 7 | Das Installskript liest jeden Rückgabewert 1 von `--check-folder` als „Ordner nicht abgeglichen“ — auch einen Programmabsturz | niedrig | nein |
| 8 | Zenity deutet `--text` als Pango-Markup; ein `&` oder `<` in einem Dateinamen verstümmelt den Dialogtext (Vermutung) | niedrig | nein |
| 9 | Die Entdoppelung der Terminal-Kandidaten greift auf Debian für `gnome-terminal` und `xfce4-terminal` nicht, weil die Alternative auf `*.wrapper` zeigt | niedrig | nein |
| 10 | Der Hinweis bei fehlender Arbeitsanweisung verweist auf `files/` im Repo statt auf das Paket, mit Grammatikfehler im Deutschen | niedrig | nein |
| 11 | Die Unit nennt als `Documentation=` eine interne GitLab-Adresse, ausgeliefert in beiden Paketen | niedrig | nein |
| 12 | Beide Arbeitsanweisungen nennen „Vorgabe 2.9“, obwohl 3.4 festlegt, dass das Artefakt keine Kapitelnummern kennt | niedrig | nein |
| 13 | `README.en.md` sagt, die zitierten Wortlaute seien die englischen, und zeigt dann den deutschen Meldungsblock | niedrig | nein |
| 14 | Die Prüfliste in 3.5 nennt „Syncthing läuft“ vor dem `.stignore`-Vergleich; das Skript prüft umgekehrt | niedrig | nein |
| 15 | Das Prüfskript setzt Python ≥ 3.10 voraus (`str \| None` in einer Signatur), ohne es zu sagen | niedrig | nein |
| 16 | Das Prüfskript ist für Befund 1 blind, weil `check_session_detection` nur zonenlose Stempel verwendet | mittel (Prüfdeckung) | **ja, zusammen mit 1** |
| 17 | Die Umstellung auf Mehrsprachigkeit hat keinen Eintrag in Anhang B, obwohl Code und Prüfskript sie als „Etappe 3“ zitieren | niedrig (Doku) | nein |
| 18 | Aktualisierung einer bestehenden Installation ist nirgends beschrieben; zwei Kataloge nebeneinander machen den Wächter deutsch, ohne dass das Installskript es sagt | niedrig | nein |

## Empfehlung vor dem heißen Test, in dieser Reihenfolge

1. **Befund 1 beheben und Befund 16 gleich mit.** Ohne 1 liefert eine Konfliktsitzung, die länger als eine halbe Stunde dauert — der in 3.1 Schritt 3 ausdrücklich als Normalfall benannte —, bei jedem Durchgang einen Traceback ins Journal, und der Test misst dann diesen Fehler statt des Mechanismus.
2. **Befund 3 mitnehmen**, weil er wenige Zeilen kostet und dieselbe Vorbedingungsklasse betrifft, die 3.5 begründet.
3. **Das Prüfskript laufen lassen** (`/usr/bin/python3 tests/test_dialog_and_naming.py`; braucht Freigabe des Entwicklers, schreibt nur unter `/tmp`). Nach der Korrektur von 1 muss die Gruppe „Sitzungserkennung“ mit zonentragenden Stempeln fallen, bevor sie steht — das ist die Leerprobe.
4. **Auf dem Testrechner den Dateisatz prüfen:** `messages.py`, `messages_de.py`, `conflict-resolution.de.md` und `tools/` müssen in `~/.claude-sync-watch/` liegen; danach `install_service.sh` laufen lassen, damit der Dienst mit **dieser** Fassung neu startet (3.5, Neustart ist Vorschrift). Im Journal muss danach der Startlauf ohne Traceback stehen.
5. **Während des Tests das Journal mitlesen** (`journalctl --user -u claude-sync-watch.service -f`). Ein Traceback mit `can't subtract offset-naive and offset-aware datetimes` ist Befund 1; eine ausbleibende Bilanzzeile bei sichtbar vorhandenen Kopien ist ein Hinweis auf Befund 2.

Befund 2 ist der schwerste **nach** dem Test: Er tritt nicht im Testablauf auf, sondern erst, wenn ein Rechner bei offenem Dialog heruntergefahren wird. Wer den Test mit einem Neustart des Rechners bei offenem Dialog verbinden will, behebt ihn vorher.

---

## I. Zwingend vor dem Test

### 1. [C] `session_running` wirft `TypeError`, sobald eine Sitzung länger als dreißig Minuten läuft und ihr Terminal noch lebt

**Schwere:** kritisch. **Vor dem Test:** ja.

Fundstelle: `files/claude_sync_watchd.py`, Methode `WatchState.session_running`, letzte Zeile `return abs(started - recorded) <= PID_START_TOLERANCE` (Zeile 755); dazu `_boot_time` (`datetime.datetime.fromtimestamp(int(line.split()[1]))`, Zeile 641) und `_now` (`datetime.datetime.now().astimezone().isoformat()`, Zeile 769).

Betrifft: 3.1 Konflikt-Wächter (Ablauf, Schritt 3); 3.2 Zustandsdaten (Zonenangabe); 2.6 Ausgabedisziplin.

Befund: Seit der Bearbeitung von Befund 33 schreibt `_now()` Zeitstempel **mit** Zonenangabe, und `session_started` wird in `escalate` genau damit gesetzt. `process_running_since` liefert dagegen eine **zonenlose** Zeit: `_boot_time` baut sie aus `fromtimestamp(btime)` ohne Zone, und die Addition der Prozess-Ticks ändert daran nichts. In `session_running` wird `recorded` mit `fromisoformat` aus dem zonentragenden Stempel gelesen — und dann `started - recorded` gerechnet. Zonenlos minus zonentragend wirft in Python `TypeError: can't subtract offset-naive and offset-aware datetimes`. Das `try/except (ValueError, TypeError)` zwei Zeilen darüber umschließt nur `fromisoformat`, nicht die Subtraktion.

Der Weg dahin ist genau der, den 3.1 Schritt 3 schützen will: `session_started` gesetzt, Ruhezeit von dreißig Minuten abgelaufen, `session_pid` vorhanden, und `/proc/<pid>/stat` weist den Prozess als lebend und nicht als Zombie aus — also eine Konfliktsitzung in einem Terminal, das die PID hält (konsole, xterm; nicht gnome-terminal), die länger als eine halbe Stunde dauert. 3.1 nennt das „die lange Sitzung … der Normalfall“, und B.2 zum Befund 25–29 begründet die ganze Startzeit-Lösung mit diesem Fall.

Die Ausnahme steigt aus `run_pass` (dort wird `session_running` vor jeder anderen Entscheidung befragt) durch das `finally` mit `release_lock` nach oben. Im Dienstbetrieb fängt `guarded_pass` sie und schreibt „Durchgang … mit einem Fehler abgebrochen“ samt Traceback ins Journal — bei jedem Sicherheitslauf und bei jedem Dateiereignis mit Konfliktmarke, solange die Sitzung läuft. `save_state` wird nicht erreicht, `maybe_notify` auch nicht: keine Betriebsmeldung während der Sitzung. Ein Handlauf mit `--once` oder `--dry-run` bricht in derselben Lage laut ab. Sobald das Terminal geschlossen ist, liefert `process_running_since` `None`, und der Wächter fängt sich von selbst.

Warum es nicht aufgefallen ist: Befund 33 war der letzte bearbeitete, und die Sitzungserkennung lag zu dem Zeitpunkt schon fertig da. Das Prüfskript deckt die Lage nicht — Befund 16. Am laufenden System fällt es erst bei der nächsten Sitzung über dreißig Minuten auf.

Wirkung: Der heiße Test würde in genau der Lage, die er prüfen soll, bei jedem Durchgang einen Traceback erzeugen. Die Eskalation ist dabei zufällig richtig unterdrückt (der Durchgang kommt gar nicht bis zur Frage), aber aus dem falschen Grund; Betriebsmeldung und Episodenführung fallen für die Dauer der Sitzung aus, und das Journal füllt sich mit Rückverfolgungen — die Gesprächigkeit, die 2.6 ausschließt, hier als Programmierfehler.

Vorschlag: C, zwei Zeilen. `_boot_time` liefert eine zonentragende Zeit (`fromtimestamp(...).astimezone()`), womit `process_running_since` ebenfalls zonentragend wird; und `session_running` normalisiert `recorded` wie `_age` es tut — ist `recorded.tzinfo` leer, `recorded = recorded.astimezone()` —, damit auch ein Stempel aus einer Zustandsdatei von vor Befund 33 weiter gelesen wird. Dazu Befund 16 im Prüfskript. Doku: 3.2 sagt „Alle Zeitstempel tragen ihre Zonenangabe“; ein Halbsatz, dass das auch für die aus `/proc` errechnete Startzeit gilt, hält die Regel künftig zusammen.

---

## II. Hoch

### 2. [C] Die Laufsperre kann nach einem Rechnerneustart dauerhaft einem fremden Prozess gehören — und ein abgewiesener Durchgang hinterlässt im Dienstbetrieb keine Spur

**Schwere:** hoch. **Vor dem Test:** nicht zwingend; die Journalzeile für abgewiesene Durchgänge empfohlen, damit ein Stillstand während des Tests nicht als Ruhe gelesen wird.

Fundstelle: `files/claude_sync_watchd.py`, `acquire_lock` (`if holder is not None and process_alive(holder): return False`, Zeile 861–862); `process_alive` (`except PermissionError: … return True`, Zeile 659–661); `run_pass` (`if not acquire_lock(): return -1`, Zeile 1581–1582); `watch_forever` (nur `except KeyboardInterrupt`, Zeile 1755; kein `signal`-Import in der Datei).

Betrifft: 3.2 Zustandsdaten („Über die Sperre entscheidet ihr Halter, nicht die Uhr“); 2.6 Ausgabedisziplin; 1.8 (der stille Ausfall als schlimmster Ausgang).

Befund: Drei Stücke, die zusammen einen stillen Totalausfall ergeben.

Erstens bleibt die Sperre bei einem harten Ende liegen. `systemd` beendet den Dienst beim Abmelden (`PartOf=graphical-session.target`) und beim `restart` mit `SIGTERM`. Python hat für `SIGTERM` keinen Handler; der Prozess endet sofort, `finally`-Blöcke laufen nicht. Steht in dem Moment ein Dialog offen — und der steht bis zu fünfzehn Minuten, die Strecke bis zu fünfundvierzig —, dann bleibt `.lauf.lock` mit der PID des alten Dienstes zurück.

Zweitens entscheidet über eine liegengebliebene Sperre allein die Frage, ob **irgendein** Prozess mit dieser Nummer lebt. Nach einem `restart` innerhalb derselben Sitzung ist die alte Nummer frei, die Sperre wird als Überrest erkannt und entfernt — das ist der in 3.2 beschriebene und richtige Weg. Nach einem **Neustart des Rechners** beginnt die Nummernvergabe von vorn. Der Wächter startet beim Anmelden, seine PID liegt deshalb regelmäßig im Bereich der Boot- und Anmeldeprozesse, und genau dort sind nach dem nächsten Start viele langlebige Prozesse zu Hause. Trifft die alte Nummer einen davon, sagt `process_alive` „lebt“ — bei einem Systemprozess sogar über den `PermissionError`-Zweig, der ausdrücklich „lebt“ zurückgibt —, und 3.2 legt fest: „Lebt er, ist die Sperre gültig — **unabhängig vom Alter**.“ Die Altersgrenze greift nur bei unlesbarer PID. Die Sperre gehört damit auf Dauer einem Fremden. (Wie wahrscheinlich die Wiederverwendung ist, ist **abgeschätzt**, nicht gemessen; der Mechanismus ist am Code gelesen.)

Drittens ist das unsichtbar. `run_pass` gibt bei abgewiesener Sperre `-1` zurück; `guarded_pass` wertet den Rückgabewert nicht aus, und die Zeile „Ein anderer Durchgang läuft gerade“ erscheint nur im `--once`-Handlauf. Im Dienstbetrieb steht also **nichts** im Journal: kein Startlauf, keine Bilanzzeile, keine Betriebsmeldung — der Wächter sieht aus wie ein Wächter in einer ruhigen Woche. Erkennbar ist die Lage nur am Ausbleiben der stündlichen Meldung, das die README zwar als Befund benennt, das aber Tage dauern kann, bis es jemandem auffällt.

Wirkung: Ein Rechner, der bei offenem Konflikt-Dialog heruntergefahren wurde, hat nach dem nächsten Start mit einer nicht kleinen Wahrscheinlichkeit einen Wächter, der nie wieder etwas tut, bis jemand `~/.claude-sync-watch/.lauf.lock` von Hand löscht. Für ein Werkzeug, dessen Zweck das Eskalieren ist, ist das der Ausgang, den 1.8 und 3.1 Schritt 1 als den schlechtesten benennen. Vor dem ersten Test tritt er nicht ein; er ist ein Betriebsrisiko danach.

Vorschlag: C, drei Bausteine, jeder allein schon nützlich. (a) Den Halter nicht nur auf Existenz prüfen, sondern auf **Identität**: Die Sperrdatei trägt bereits den Zeitstempel ihrer Anlage (`pid <n> <_now()>`), und `process_running_since` liefert die Startzeit des Prozesses — ein Prozess, der **nach** dem Sperrzeitpunkt gestartet wurde, kann die Sperre nicht angelegt haben und ist ein Fremder; die Sperre ist dann ein Überrest. `lock_holder` müsste dafür beide Felder zurückgeben. Das ist dieselbe Logik, mit der 3.1 Schritt 3 die wiederverwendete Sitzungs-PID entlarvt, und sie kostet keinen zusätzlichen Systemaufruf, den der Wächter nicht schon kennt. (b) Einen `SIGTERM`-Handler setzen, der `SystemExit` auslöst — dann laufen die `finally`-Blöcke, `release_lock` räumt auf, und `observer.stop()` wird erreicht; die Sperre bleibt nur noch bei einem echten Absturz liegen. (c) Eine Journalzeile, wenn ein Durchgang abgewiesen wird — nicht je Durchgang (das käme im Takt der Dateiereignisse), sondern beim **Zustandswechsel** wie bei `scan_incomplete` oder einmal je Dienstlauf. Nach 2.6 ist ein dauerhaft abgewiesener Durchgang ein Fehler, und Fehler werden immer ausgegeben. Doku: 3.2 um die Identitätsprüfung und die Journalzeile ergänzen; der Satz „unabhängig vom Alter“ bleibt richtig, bekommt aber die Bedingung „sofern er die Sperre auch angelegt haben kann“.

### 3. [A+C] Ein fehlender Meldungskatalog endet mit Rückgabewert 1 — und damit in der Neustartschleife, die 3.5 mit dem Wert 78 verhindert

**Schwere:** mittel (im Betrieb nur nach nachträglichem Entfernen einer Datei). **Vor dem Test:** empfohlen, weil klein.

Fundstelle: `files/claude_sync_watchd.py`, `main` (`messages.use(args.lang)`, Zeile 1836, ohne Absicherung); `import messages` (Zeile 75); `files/messages.py`, `use` (`raise FileNotFoundError(...)`, Zeile 58–60); `files/claude-sync-watch.service` (`RestartPreventExitStatus=78`, Zeile 35).

Betrifft: 3.1 Konflikt-Wächter (Schalter, Absatz „Die Sprache wird genau einmal aufgelöst“); 3.5 Dienstdefinition (`RestartPreventExitStatus=78`, Trennlinie).

Befund: 3.1 sagt: „Liegt **keiner**, verweigert der Wächter den Start **wie bei einer fehlenden Bibliothek**.“ Die fehlende Bibliothek endet mit `EXIT_PRECONDITION` (78), und 3.5 begründet ausführlich, warum: Bei `RestartSec=30` greift systemds Startraten-Begrenzung nie, ein Dienst mit Rückgabewert 1 startet alle dreißig Sekunden neu und erreicht nie `failed`. Der fehlende Katalog nimmt diesen Weg aber nicht: `messages.use` wirft `FileNotFoundError`, `main` fängt sie nicht, Python endet mit Traceback und **Rückgabewert 1** — die Schleife aus dem alten Befund 32, nur mit anderer Ursache. Dasselbe gilt für ein fehlendes `messages.py`: `import messages` scheitert vor `main` mit `ImportError`, Rückgabewert 1.

Beide Dateien prüft `install_service.sh` bei der Einrichtung. Die Begründung von Befund 32 gilt aber unverändert: Eine Vorbedingung kann später wegfallen — hier etwa durch ein Aufräumen des Werkzeugordners oder ein unvollständiges Überspielen einer neuen Fassung. Die Trennlinie aus 3.5 („Nur **strukturelle** Vorbedingungen bekommen die 78“) ordnet den Katalog eindeutig ein: Ohne Texte heilt kein Warten.

Wirkung: Journal im Halbminutentakt, Dienststatus „aktiviert, startet immer wieder“ statt eines klaren Fehlschlags — genau das Bild, das 3.5 als abgestellt beschreibt.

Vorschlag: C — `messages.use` in `main` gegen `FileNotFoundError` absichern, eine englische Zeile ausgeben (ein Katalog fehlt, also gibt es keinen Katalogtext dafür; 2.5 deckt das als strukturelle Verweigerung) und `EXIT_PRECONDITION` zurückgeben. Für `import messages` dasselbe am Modulanfang mit `try/except ImportError`. A — in 3.1 den Satz „wie bei einer fehlenden Bibliothek“ um „mit demselben Rückgabewert 78“ ergänzen und in 3.5 den Katalog neben der Bibliothek als zweite strukturelle Vorbedingung nennen; das Prüfskript hat für die Bibliothek schon eine Gruppe, der Katalog gehört daneben.

---

## III. Mittel

### 4. [C] `notify` fängt nur `FileNotFoundError`; jeder andere Fehler des Aufrufs bricht den Durchgang ab und hält die Meldung dauerhaft fällig

**Schwere:** mittel. **Vor dem Test:** nein.

Fundstelle: `files/claude_sync_watchd.py`, `notify` (`_require_linux("Desktop notification")` außerhalb des `try`, Zeile 328; `except FileNotFoundError`, Zeile 345); `maybe_notify` (`notify(T("notify.summary"), text, seconds)` außerhalb des `try`, Zeile 1572; `state.notice_last_shown = _now()` nur im Speicher, Zeile 1549).

Betrifft: 3.1 Konflikt-Wächter (Fünf Punkte, Punkt 3); 2.6 Ausgabedisziplin; 2.4 Kapselung.

Befund: Der Docstring von `notify` sagt „Never raises“, der von `maybe_notify` „Never lets a failure propagate“. Beides gilt nicht für zwei Wege. Erstens: Ein `notify-send`, das vorhanden ist, aber nicht startet — `PermissionError` (Rechte verstellt), `OSError` mit `ENOEXEC` (beschädigte Datei) —, wirft aus `subprocess.run` eine andere Ausnahme als `FileNotFoundError`; sie verlässt `notify`, dann `maybe_notify` (dessen `try` nur `build_notice` umschließt), dann `run_pass` **vor** `save_state`. Der Stempel `notice_last_shown` steht damit nur im Speicher und geht mit dem Abbruch verloren; die Meldung bleibt in der Zustandsdatei fällig, und der Traceback kommt beim nächsten Durchgang wieder — im Takt der Dateiereignisse, also genau die Flut, die 3.1 Punkt 3 mit dem frühen Stempeln verhindert. Zweitens: `_require_linux` steht **vor** dem `try`; auf einer nicht bedienten Plattform ist die Verweigerung eine `NotImplementedError`, die `maybe_notify` nur um `build_notice` herum kennt — hier käme sie stündlich als Programmierfehler mit Rückverfolgung ins Journal, an genau der Stelle, die B.2 zu Befund 5 „wahrheitsfähig“ gemacht hat. Heute ohne Wirkung, weil nur Linux läuft; aber 3.7 zählt darauf, dass die Kapsel an ihren Aufrufen verweigert und nicht abstürzt.

Wirkung: Auf Linux selten (ein kaputtes `notify-send` ist kein Alltagsfall), aber die Folge ist die falsche Klasse: ein Fehler des Beiwerks bricht den Durchgang ab, statt still zu entfallen.

Vorschlag: C — in `notify` `OSError` insgesamt fangen (mit Journalzeile samt Fehlertext, ohne Meldungsinhalt, wie beim Rückgabewert), und `_require_linux` in denselben Schutz nehmen oder den `notify`-Aufruf in `maybe_notify` in dessen bestehende Ausnahmebehandlung ziehen, wo `NotImplementedError` schon richtig eingeordnet wird. Ein Prüffall mit einer `PermissionError`-Attrappe gehört in „Verschluckte Fehler (2.6)“.

### 5. [C] `xdg-terminal-exec --`: der Trenner ist ungeprüft und möglicherweise falsch — **Vermutung**

**Schwere:** mittel, weil dieser Weg jeden anderen Kandidaten verdrängt, sobald das Programm vorhanden ist. **Vor dem Test:** nur auf einem Rechner, der `xdg-terminal-exec` installiert hat.

Fundstelle: `files/claude_sync_watchd.py`, `detect_terminal` (`chosen = ["xdg-terminal-exec", "--"]`, Zeile 1072–1075).

Betrifft: 3.3 Eskalationsstrecke (Terminal-Erkennung); 3.8 Belegführung („Nicht geprüft: … `xdg-terminal-exec`“).

Befund: `xdg-terminal-exec` steht in der Erkennung an erster Stelle und gewinnt ohne Frage, wenn es existiert. Das Ergebnis wird zwischengespeichert. Der Aufruf lautet dann `xdg-terminal-exec -- /usr/bin/claude …`. Nach meinem Wissen über die Referenzimplementierung nimmt `xdg-terminal-exec` den Befehl direkt als Argumente (`xdg-terminal-exec [command [args]]`) und reicht ihn an den Emulator hinter dessen `-e`/`--` weiter; ob es ein vorangestelltes `--` selbst verschluckt oder als ersten Befehlsbestandteil an das Terminal durchreicht, kann ich am Code nicht entscheiden. Im zweiten Fall versuchte das Terminal `--` auszuführen, und die Sitzung startete nie — auf jedem Rechner, der das Programm hat, bei jedem Konflikt, mit gespeichertem Befehl. 3.8 hält fest, dass das Programm auf keinem der Entwicklungsrechner installiert war; die Zeile ist damit der einzige Terminalweg, der nie gelaufen ist.

Wirkung: Heute keine (kein Rechner des Entwicklers hat es). Auf einer aktuellen Distribution, die das Programm mitbringt, wäre die Eskalation komplett blockiert, mit einem Terminalfenster, das aufblitzt und verschwindet — derselbe unsichtbare Ausgang wie beim alten Befund 29.

Prüfen: `xdg-terminal-exec -- /bin/sh -c 'echo ok; sleep 3'` gegen `xdg-terminal-exec /bin/sh -c 'echo ok; sleep 3'` auf einem Rechner mit dem Programm; dazu die Spezifikation des `xdg-terminal-exec`-Entwurfs auf freedesktop.org. Vorschlag: C — das `--` entfernen, falls es nicht ausdrücklich unterstützt ist, und in 3.8 vermerken, wo und wie geprüft wurde; solange ungeprüft, den Weg in 3.3 als ungeprüft kennzeichnen.

### 6. [C] Erschöpfte inotify-Kontingente ließen `observer.schedule` scheitern — Rückgabewert 1, Neustartschleife (**Vermutung** zur Wahrscheinlichkeit, nicht zum Weg)

**Schwere:** niedrig bis mittel. **Vor dem Test:** nein.

Fundstelle: `files/claude_sync_watchd.py`, `watch_forever` (`observer.schedule(ConflictHandler(), str(watch_dir), recursive=True)` / `observer.start()`, Zeile 1740–1742, ohne Absicherung).

Betrifft: 3.1 Konflikt-Wächter (Auslöser und Sicherheitsnetze); 3.5 (Trennlinie der Rückgabewerte).

Befund: Der rekursive Beobachter belegt je Verzeichnis unter `~/.claude` einen inotify-Watch — auch unter `file-history/`, `projects/` und `.stversions/`, die vom Suchlauf ausgelassen werden, nicht aber von der Beobachtung. `file-history/` trägt einen Ordner je Sitzung, und bei einer Aufbewahrungsfrist von drei Jahren (README, `cleanupPeriodDays`) wächst das auf Tausende. Reicht das Kontingent `fs.inotify.max_user_watches` nicht, wirft `watchdog` beim Einrichten eine `OSError`; sie ist nicht gefangen, der Dienst endet mit Rückgabewert 1, und `Restart=on-failure` startet ihn alle dreißig Sekunden neu — der Startlauf läuft dann jedes Mal, die Beobachtung nie. Ob das Kontingent auf den vier Rechnern erreicht wird, kann ich nicht wissen; moderne Kernel setzen es hoch. Der Weg im Code ist aber sicher, und er ist strukturell im Sinne von 3.5: Warten heilt ihn nicht.

Prüfen: `sysctl fs.inotify.max_user_watches` gegen `find ~/.claude -type d | wc -l` auf dem Rechner mit dem größten Bestand. Vorschlag: C — `schedule`/`start` gegen `OSError` sichern, den Fehler samt Kontingenthinweis ins Journal schreiben und mit `EXIT_PRECONDITION` enden; A — in 3.1 unter „Der Preis der rekursiven Beobachtung“ das Kontingent neben der Warteschlange nennen.

---

## IV. Niedrig, kosmetisch, Doku

### 7. [C] Das Installskript liest jeden Rückgabewert 1 von `--check-folder` als „Ordner nicht abgeglichen“

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `files/install_service.sh`, Block „Checking whether Syncthing synchronises“ (`case "$folder_state" in 0) … 1) warn "WARNING: $folder_check …" …`, Zeile 391–404).

Befund: Der Wächter antwortet mit 0, 1 oder 2. Ein Python-Absturz — nicht abgefangene Ausnahme — endet ebenfalls mit 1. Das Skript zeigt dann den Traceback als Text der Warnung „this folder does not take part in the synchronisation“ und empfiehlt, den Ordner in Syncthing zu teilen. Die eigenen Dateien sind zuvor geprüft, ein fehlender Katalog ist also ausgeschlossen; übrig bleibt ein Programmierfehler im Wächter, den die Einrichtung dann falsch benennt. Vorschlag: `check_folder` einen eigenen Wert für „nicht konfiguriert“ geben, der mit keinem Absturzwert kollidiert (etwa 3), oder im Skript zusätzlich auf das Wort „Traceback“ prüfen und dann die neutrale Meldung aus dem `*)`-Zweig geben.

### 8. [C] Zenity deutet `--text` als Pango-Markup — **Vermutung**, prüfbar

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `files/claude_sync_watchd.py`, `ask_question` (`f"--text={text}"`, Zeile 388), gleichartig in `show_message`, `pick_from_list`, `ask_text`.

Befund: Nach meinem Wissen wertet Zenity den Text der Frage-, Fehler- und Listendialoge als Pango-Markup aus, sofern nicht `--no-markup` gesetzt ist. Ein Originalname mit `&`, `<` oder `>` — in `~/.claude` nicht die Regel, aber ein Projektname mit `&` ist nicht abwegig — erzeugt dann eine Markup-Warnung auf der Fehlerausgabe (die dank `zenity_outcome` wenigstens im Journal steht) und einen verstümmelten oder leeren Dialogtext. Prüfen: `zenity --question --text 'a & b <c>'`. Vorschlag: `--no-markup` an die vier Aufrufe hängen oder die Namen mit `html.escape` maskieren; ein Prüffall mit einem solchen Namen im Übergabetext gehört dazu.

### 9. [A] Die Entdoppelung der Terminal-Kandidaten greift auf Debian für `gnome-terminal` und `xfce4-terminal` nicht

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `files/claude_sync_watchd.py`, `_distinct_terminals` (`if target not in seen or target.name == binary`, Zeile 1051); 3.3, Absatz „Welcher der beiden Namen bleibt“; B.2 zu Befund 22 („Zeigt die Verknüpfung auf `gnome-terminal` — auf einem GNOME-System der Normalfall“).

Befund: Debians Alternative `x-terminal-emulator` zeigt bei `gnome-terminal` und `xfce4-terminal` nicht auf das Programm, sondern auf `/usr/bin/gnome-terminal.wrapper` bzw. `xfce4-terminal.wrapper` — Hüllskripte, die xterm-artige Schalter übersetzen. `target.name` ist dann `gnome-terminal.wrapper` und gleicht keinem Kandidaten; beide Zeilen bleiben stehen, der Auswahldialog zeigt weiter zwei Zeilen für ein Programm. Harmlos, denn die Hülle versteht `-e`, also startet die Zeile `x-terminal-emulator` das Terminal richtig — der in B.2 befürchtete Fall „falscher Schalter“ tritt gerade wegen der Hülle nicht ein. Nur die Aussage „auf einem GNOME-System der Normalfall“ trifft so nicht zu; dort greift die Entdoppelung schlicht nicht. Vorschlag: A — in 3.3 nennen, dass die Entdoppelung nur bei direkter Verknüpfung wirkt (konsole) und bei Hüllskripten die Doppelzeile bleibt, gutartig. Wer sie auch dort haben will (C), vergleicht `target.name` nach Abschneiden von `.wrapper`.

### 10. [C] Der Hinweis bei fehlender Arbeitsanweisung verweist auf `files/` im Repo statt auf das Paket

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `files/messages_de.py`, Eintrag `dialog.no_instruction.text` („Bitte den Inhalt des files/-Ordner aus der Repo-Quelle … kopieren“, Zeile 83–89); `files/messages_en.py`, derselbe Eintrag (Zeile 80–85); `files/install_service.sh`, `MISSING_FILES_HINT` („Please copy the folder 'files/' from the repository here in full“, Zeile 200–201).

Befund: Seit 2.7 ist das Paket unter `downloads/` der Auslieferungsweg, und die README kennt keinen anderen. Wer das Paket entpackt hat, kennt keinen Ordner `files/` und keine „Repo-Quelle“. Beide Texte stammen aus der Zeit vor den Paketen. Im Deutschen dazu ein Grammatikfehler („des files/-Ordner“ statt „des files/-Ordners“) und „das fehlende File“ als Anglizismus in einem sonst deutschen Text. Vorschlag: beide Texte auf „das Paket erneut nach `~` entpacken“ umstellen und im Deutschen „Datei“ statt „File“; die Fälle sind nach 3.8 nur von Hand geprüft, also bleibt der Wortlaut frei.

### 11. [C] Die Unit nennt als `Documentation=` eine interne GitLab-Adresse

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `files/claude-sync-watch.service` (`Documentation=https://codebase.helmholtz.cloud/FWF/tools/claude-ai-tooling.git`, Zeile 13).

Befund: Die Unit liegt in beiden Paketen und damit bei jedem Anwender. Die Adresse ist die eines institutionsinternen GitLab; die README verweist auf `github.com/fherb2/claude-ai-tooling`, und die Projekt-CLAUDE.md nennt GitHub als den einzigen international gehosteten Ort. `systemctl status` zeigt die Zeile jedem Anwender an. Vorschlag: auf die GitHub-Adresse des Ordners umstellen. Kein Verhalten hängt daran.

### 12. [C] Beide Arbeitsanweisungen nennen „Vorgabe 2.9“

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `files/conflict-resolution.de.md`, Schritt 6 („… die Aufdringlichkeit, die Vorgabe 2.9 vermeiden will“, Zeile 69); `files/conflict-resolution.en.md`, Schritt 6 („determination 2.9“, Zeile 69).

Befund: 3.4 legt zu Schritt 5 fest, der Hinweis erfolge „der Sache nach und ohne Kapitelnummer, denn das Artefakt kennt keine“, und B.2 zu Befund 18 wiederholt das als Grundsatz. Zwei Absätze weiter steht in beiden Fassungen eine Kapitelnummer, die die Sitzung nicht auflösen kann — sie hat die Doku nicht vor sich. Vorschlag: den Halbsatz auf die Sache kürzen („… die Aufdringlichkeit, die hier vermieden werden soll“). Wirkung im Betrieb: keine; die Sitzung liest über die Nummer hinweg.

### 13. [A] `README.en.md` widerspricht sich bei den zitierten Wortlauten

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `README.en.md`, Absatz „A note on language“ („The strings quoted below are the English ones, verbatim“, Zeile 11) gegen den Meldungsblock unter „Once an hour the watcher reports in“ (deutsche Zeilen `abgeglichen: …` / `kein Konflikt seit …`, Zeile 111–112, mit englischer Übersetzung in Klammern darunter).

Befund: Der Block ist offenbar aus der deutschen README übernommen und übersetzt kommentiert, der Absatz oben verspricht das Gegenteil. Die vier Aufmerksamkeitsformen darunter sind dagegen englisch und stimmen mit `messages_en.py` wörtlich überein (geprüft: `conflict(s) for … hour(s) unresolved`, `backlog: … file(s)`, `Sync paused for this folder — …`, `no connection to the sync for …`, `counters reset`, `counting started afresh`). Vorschlag: den Block auf die englischen Zeilen `synced: 0.8 MB up, 0.3 MB down` / `no conflict for 74 hour(s)` umstellen und die Klammer streichen — oder den Satz oben streichen. Die deutsche README ist in diesem Punkt in Ordnung.

### 14. [A] Die Prüfliste in 3.5 nennt „Syncthing läuft“ vor dem `.stignore`-Vergleich; das Skript prüft umgekehrt

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `implementation-doc.md`, 3.5, Liste unter „Prüft zuerst die Vorbedingungen, **in dieser Reihenfolge**“ (Punkte „Syncthing läuft“ und „`~/.claude/.stignore` gegen die maßgebliche Fassung“); `files/install_service.sh`, Block „Exclusion list“ (Zeile 406–469) vor `pgrep -x syncthing` (Zeile 471–475).

Befund: Die Liste erhebt die Reihenfolge ausdrücklich zur Aussage. Sie stimmt bis auf dieses Paar. Sachlich ist die Skriptreihenfolge die bessere: Der Hinweis auf ein nicht laufendes Syncthing steht dann unmittelbar vor der Installation, wo er hingehört. Vorschlag: A — die beiden Punkte in 3.5 tauschen.

### 15. [C] Das Prüfskript setzt Python ≥ 3.10 voraus, ohne es zu sagen

**Schwere:** niedrig. **Vor dem Test:** nein.

Fundstelle: `tests/test_dialog_and_naming.py`, `check_stignore_offer`, innere Funktion `run_block(antwort: int, vorhanden: str | None)` (Zeile 1618); Rückgabe-Annotationen wie `-> tuple[int, str]` (Zeile 1445, 1511); kein `from __future__ import annotations` in der Datei.

Befund: Der Wächter trägt `from __future__ import annotations` und läuft ab Python 3.8. Das Prüfskript nicht — Signatur-Annotationen werden dort beim Definieren ausgewertet, und `str | None` wirft unter Python 3.9 `TypeError`. Auf den Entwicklungsrechnern ist das ohne Belang; 3.8 nennt aber `/usr/bin/python3` als vorgeschriebenen Interpreter, und ein Rechner mit älterem Systempython bekäme statt eines Prüfergebnisses einen Absturz beim Laden. Vorschlag: `from __future__ import annotations` an den Anfang des Prüfskripts, oder die Untergrenze im Kopfkommentar nennen.

### 16. [C] Das Prüfskript ist für Befund 1 blind

**Schwere:** mittel als Prüfdeckung. **Vor dem Test:** ja, zusammen mit Befund 1.

Fundstelle: `tests/test_dialog_and_naming.py`, `check_session_detection` (`now = datetime.datetime.now()`, `long_ago = (now - …).isoformat()`, `recent = …`, Zeile 997–999; `session_started=own_start.isoformat()`, Zeile 1023).

Befund: Alle Stempel dieser Gruppe sind zonenlos: `datetime.datetime.now()` ohne `astimezone()`, und `own_start` kommt aus `process_running_since`, das selbst zonenlos liefert. Damit rechnet `session_running` im Prüfskript ausschließlich zonenlos gegen zonenlos und trifft den Betriebsfall — `session_started` aus `_now()`, also zonentragend — nie. Die Gruppe „Uhrensprünge (3.2)“ prüft zwar, dass `_now()` eine Zone trägt, aber keine Gruppe führt einen `_now()`-Stempel durch die Sitzungserkennung. Genau das ist die Lücke, die 3.8 als Zweck der Leerproben benennt: Ein Prüffall, der nicht anschlägt, ist wertlos — hier schlug er bei einer echten Regression nicht an. Vorschlag: die Stempel der Gruppe aus `w._now()` bzw. aus einer zonentragenden Rechnung bilden und den Fall „passende Startzeit, zonentragender Stempel“ ausdrücklich hinzufügen; vor der Korrektur von Befund 1 muss er fallen (Leerprobe am Rückgabewert des Prüflaufs, wie B.2 zu Befund 33 lehrt).

### 17. [A] Die Umstellung auf Mehrsprachigkeit hat keinen Eintrag in Anhang B

**Schwere:** niedrig (Doku-Prozess). **Vor dem Test:** nein.

Fundstelle: `implementation-doc.md`, Anhang B endet mit dem Eintrag zu Befund 33 (Zeile 1611–1630); `tests/test_dialog_and_naming.py` verweist auf „Etappe 3 of the multilingual conversion“ (Kommentar in `check_notice`, Zeile 634); `scripts/pack_packages.sh` begründet sich mit „Until the multilingual conversion“ (Zeile 15).

Befund: Die Kapitel 1–3 sind auf den mehrsprachigen Stand gebracht — 2.5, 2.7, 3.1, 3.3, 3.4 tragen ihn durchgehend. Der Anhang, der laut seinem eigenen Vorwort „die Wissensbasis eines künftigen Reviews“ ist, kennt die Umstellung nicht: keine Etappen, keine verworfenen Wege (etwa: warum Katalog je Datei statt `gettext`, warum `str.format` statt einer Pluralmaschine — die Entscheidung steht heute nur als Kommentar im Katalog), keine Leerproben. Der nächste Review muss die Entscheidungen aus Kommentaren rekonstruieren. Die Projekt-CLAUDE.md verlangt für jede Bearbeitung einen Bericht; ob die Umstellung als Befundbearbeitung oder als Fahrplanschritt lief, ändert daran nichts. Vorschlag: einen kurzen Abschnitt B.3 „Umstellung auf Mehrsprachigkeit“ mit den Entscheidungen und ihren Gründen, in der Länge, die die CLAUDE.md vorsieht.

### 18. [A+C] Aktualisierung einer bestehenden Installation ist nicht beschrieben; zwei Kataloge nebeneinander machen den Wächter stillschweigend deutsch

**Schwere:** niedrig. **Vor dem Test:** nein — aber relevant, falls der Testrechner noch den einsprachigen Stand trägt.

Fundstelle: `README.md`, Abschnitt „Installation“ (nur der Erstanschluss); `files/messages.py`, `use` (bei mehreren Katalogen entscheidet `preferred`, sonst `de`, Zeile 61–68); `files/install_service.sh`, Block „2. Own files“ (prüft „mindestens eine“ Datei je Muster, Zeile 209–213); `files/claude-sync-watch.service` (`ExecStart` ohne `--lang`).

Befund: Drei Dinge, die zusammengehören. Erstens beschreibt keine README, wie eine **bestehende** Installation auf den neuen Stand kommt: `unzip … -d ~` über einen vorhandenen Ordner fragt je Datei nach dem Überschreiben, lässt `conflict-resolution.md` ohne Sprachkürzel und `werkzeuge/` liegen (das Installskript kennt nur den zweiten Fall) und startet den Dienst nicht neu — das tut erst `install_service.sh`, was nur in den Erstanschluss-Schritten steht. Zweitens: Wer statt des Pakets den Ordner `files/` aus dem Repo kopiert — so wurde vor den Paketen installiert, und so liegen die vier Rechner des Entwicklers vermutlich vor —, hat beide Kataloge und beide Anweisungen; der Wächter spricht dann Deutsch, und das ist für den Entwickler richtig, für einen Anwender des englischen Pakets aber eine Überraschung, wenn er beides gemischt hat. Drittens sagt das Installskript nichts dazu: Es prüft „mindestens einen“ Katalog und meldet nicht, wenn es mehr als einen findet. Vorschlag: A — ein kurzer Abschnitt „Aktualisieren“ in beiden READMEs (Paket mit `unzip -o` entpacken, `install_service.sh` laufen lassen, alte Dateien nennen). C — `install_service.sh` meldet, wenn mehr als ein Katalog vorliegt, und nennt die Sprache, die der Wächter dann spricht (dieselbe Zeile, die `--check-folder` ohnehin in der Wächtersprache ausgibt, verrät sie schon — nur benennt niemand, dass das die Entscheidung ist).

---

## V. Bestätigt in Ordnung

Alles Folgende ist gelesen, nicht ausgeführt. Wo eine Aussage über die Wirkung eines Laufs steht, ist sie aus dem Code erschlossen.

**Meldungskataloge (1.8, 2.5, 3.1):** Beide Kataloge tragen denselben Schlüsselsatz — 75 Schlüssel, von Hand gezählt und Eintrag für Eintrag abgeglichen —, in derselben Reihenfolge und mit denselben Platzhaltern je Schlüssel. Jeder `T(...)`-Aufruf im Wächter nennt einen vorhandenen Schlüssel mit den Feldern, die der Eintrag verlangt; kein Aufruf bildet den Schlüssel berechnet. Kein Katalogeintrag ist ohne Verwendung. Die beiden Pausenfassungen liegen nebeneinander, der Trenner `CLAUSE_BREAK` steht im Wächter und nicht im Katalog. Die englische Fassung übersetzt die Festlegungen: „Affected originals“ steht als Überschrift, die Anlässe tragen den gemeinsamen Präfix `Event:`, die Pluralklammer ist erhalten. `[dry-run]` bleibt in beiden Katalogen englisch (2.5).

**Sprachauflösung (3.1):** `messages.use` entscheidet nach vorhandenen Katalogen, bei einem nach diesem, bei mehreren nach `--lang` mit Rückfall auf Deutsch, bei keinem mit Verweigerung — bis auf den Rückgabewert (Befund 3) wie festgelegt. `main` löst die Sprache vor der ersten Meldung auf; `instruction_file()` bildet den Namen der Anweisung zur Laufzeit aus dem aufgelösten Kürzel (3.3, 3.4). Der Kopfkommentar des Wächters und `messages.py` erklären den Ladeweg über den Dateipfad, den das Prüfskript nutzt.

**Sitzungsaufruf (3.3):** Reihenfolge `Terminal → claude_binary() → --add-dir <tools> → --append-system-prompt-file <Anweisung> → Übergabetext`, absoluter Pfad, Arbeitsverzeichnis der überwachte Ordner, Umgebung ohne `CLAUDE_CODE_*`, `CLAUDECODE` und drei weitere, `TERM` entfernt. Fehlende Anweisung: keine PID, Journalzeile, Meldefenster; gescheiterter Start: dasselbe. Beides im Prüfskript festgenagelt (`check_launch_argv`, `check_launch_failure`).

**Dialoge (2.9, 3.3):** Alle vier Fenster laufen über `zenity_outcome`; Rückgabewerte 0/1/5 und die Anzeige-Merkmale werden wie 3.3 beschreibt eingeordnet, jede nicht-leere Fehlerausgabe geht ins Journal, `--timeout` steht als Sekundenzahl an allen Fenstern der Strecke. Die Vertagung wird an jedem Ausstieg neu gestempelt, der nicht gezeigte Dialog behält den frühen Stempel. Die Rückfrageschleife ist unbegrenzt, wie 3.3 es will. Die Freitexteingabe wird mit `shlex` zerlegt, das erste Wort im Suchpfad gesucht, der Schalter angehängt und nicht verdoppelt.

**Episodenführung und Suchlauf (3.1, 3.2):** `find_conflicts` trennt Fund, leeren Befund und unvollständige Sicht; die drei Zweige in `run_pass` behandeln sie wie B.2 zu Befund 11 nachträgt (der unvollständige lässt den Zustand unberührt). `conflict_since` wird nur beim Übergang gesetzt und beim Ende geleert. Zwischendateien des Empfangs werden am Namen ausgelassen. Der Trockenmodus hat genau eine `save_state`-Wache, und die beiden anderen Aufrufe liegen hinter früheren `DRY_RUN`-Ausstiegen — die Begründung im Kommentar trifft zu.

**Laufsperre (3.2):** `O_CREAT|O_EXCL`, PID in der Datei, eigene Freigabe nur bei eigener PID, Altersgrenze nur als Rückfall bei unlesbarer PID, Journalzeile beim Entfernen eines Überrests und beim Antreffen einer fremden Sperre. Bis auf Befund 2 wie festgelegt.

**Zeit (3.2, 1.8):** `_now` mit Zone, `_age` liest beide Formen und rechnet die Zonengrenze exakt, `_hours_since` klemmt auf null, die Schleife des Sicherheits-Suchlaufs nimmt die monotone Uhr, das Sperrenalter ist geklemmt. Bis auf die eine ungeschützte Subtraktion (Befund 1) durchgehend.

**Betriebsmeldung (1.8, 3.1 Punkte 1–5):** Byte-Differenz nur bei unverändertem `startedAt` und nur, wenn jedes Gerät einen Vorwert hatte; „Zähler neu gesetzt“ statt Nullen; API-Schlüssel nur gelesen; Rückstand als Funktion in allen drei Formen; Pause vor Verbindung; Anzeigedauer nach Inhalt in Millisekunden; Konflikthinweis auch ohne Schnittstelle; Fälligkeit vor dem Versuch gestempelt; `NotImplementedError` vor `Exception` behandelt. `notify` meldet Rückgabewert und Fehlertext ohne Meldungsinhalt, fehlendes `notify-send` einmal je Dienstlauf.

**Kapselung (2.4):** Genau eine Plattformabfrage (`_is_windows`), acht Verweigerungen, die vier plattformabhängigen Datenfunktionen liegen im Kapselabschnitt, `terminal_run_flags` dazu. Kein `sys.platform`, kein `platform.` außerhalb.

**`install_service.sh` (3.5):** Alle vierzehn Punkte der Prüfliste sind im Skript vorhanden, mit der in 3.5 genannten Härte (Abbruch/Warnung/Rückfrage); die drei Marken für das Prüfskript stehen an den beschriebenen Stellen; `ask_yes_no` liest von `/dev/tty`, die Vorgaben sind „nein“ für Pakete und „ja“ für die Ausschlussliste; nach echter Übernahme die Empfehlung zum Neueinlesen; Neustart statt `enable --now`; die Anmeldeprüfung entscheidet am Inhalt, die Zeitüberschreitung wird gesondert erkannt. Das Skript ist einsprachig englisch (2.5). Einzige Abweichung: Befund 14.

**`uninstall_service.sh` (3.5):** Entscheidung am Ausgabewort von `is-active`, Unit nur bei nachweislich beendetem Dienst entfernt, Meldung von `disable` nicht verschluckt.

**Unit (3.5):** `%h`, absoluter Interpreter, `PartOf`/`After`/`WantedBy=graphical-session.target`, `Type=simple`, `Restart=on-failure`, `RestartSec=30`, `RestartPreventExitStatus=78` gleich `EXIT_PRECONDITION` (das Prüfskript nagelt das Paar fest).

**`.stignore` (3.9, 2.3):** zwölf Muster, jedes in der Tabelle von 3.9, kein Tabelleneintrag ohne Muster; `.credentials.json` ohne führenden Schrägstrich, `/cache` und `/telemetry` wörtlich (2.3). Die Dateikommentare verweisen auf 3.9 und 1.3, wie B.2 zu Befund 21 festhält.

**`pack_packages.sh` (2.7):** Dateisatz je Paket = sechs gemeinsame Dateien + `README.md` + Katalog und Anweisung je Sprache; `NOT_IN_PACKAGE` deckt `tools`, `__pycache__`, `zustand.json`, `.claude`; drei Prüfrichtungen wie 2.7 beschreibt; die README wird als einzige umbenannt, Katalog und Anweisung behalten ihr Kürzel. Der `@Claude:`-Abschnitt ist vorhanden (2.5). Ob die Archive im Repo dem Stand von `files/` entsprechen, konnte ich nicht prüfen (Abschnitt VI).

**Arbeitsanweisungen (3.4):** Beide Fassungen tragen die zwei Klarstellungen am Anfang, die sechs Schritte mit allen Feinheiten aus 3.4 einschließlich des Notfall-Hinweises samt Verbot der Archivsuche (Befund 18 alt) und die sechs Grenzen. Die englische Fassung übersetzt sinngleich; nirgends steht ein Pfad. Einzige Abweichung: Befund 12.

**READMEs:** Deutsche und englische Fassung führen dieselben Schritte in derselben Reihenfolge; Paketname und Anweisungsdatei tragen je Sprache das richtige Kürzel; der Handstart-Befehl in Schritt 6 nennt in beiden die Datei, die das jeweilige Paket enthält. Die Datumszeilen stehen und sind aktuell. Einzige Abweichung: Befund 13.

**Frühere Befunde (Anhang B):** Von den 33 Befunden des Reviews vom 13. August habe ich die Bearbeitung der Nummern 1–6, 10–15, 17, 19, 20, 22, 25–33 am Code nachgeprüft; keiner ist erneut offen, und kein abgelehnter Befund wird hier wieder aufgeführt. Befund 2 dieses Reviews ist kein Rückfall des alten Befundes 25 — dort ging es um eine zu kurze Altersgrenze, hier um die Identität des Halters, die die neue Lösung nicht prüft.

---

## VI. Was ungeprüft blieb, und Fragen an den Entwickler

**Nachtrag nach der freigegebenen Dateiliste** (`find … -type f` und `ls -la files/`, ausgeführt am 11. September 2026 nach Freigabe des Entwicklers; Zip-Inhalte, Prüfskript und Git-Stand blieben ohne Freigabe und sind weiter ungeprüft):

- **Der Dateisatz ist der festgelegte.** `files/` enthält genau die sechs gemeinsamen Dateien, je zwei Kataloge und Anweisungen, `tools/.gitkeep` und ein `__pycache__` — nichts, was `pack_packages.sh` nicht in `COMMON`, `PER_LANGUAGE` oder `NOT_IN_PACKAGE` führt; die dritte Prüfrichtung des Packwerkzeugs würde also durchlaufen. `downloads/` trägt beide Pakete, `scripts/` nur das Packwerkzeug.
- **`tests/` hat fünf Dateien**, nicht vier: neben den vier Skripten aus 3.8 liegt `tests/echo_test_helper.sh` — das „harmlose Ersatzprogramm statt `claude`“, das 3.8 für `test_detect_terminal.py` nennt. B.1 zählt „die fünf Dateien in `tests/`“ und stimmt damit. Inhalt der Handproben-Skripte und des Helfers weiterhin nicht gelesen.
- **Ausführungsrechte im Repo:** `install_service.sh`, `uninstall_service.sh` und `claude_sync_watchd.py` tragen `rwxrwxr-x`; die übrigen Dateien `rw-rw-r--`. Ob die Rechte in den Archiven erhalten sind (`cp -p` und `zip` sollten sie halten), bleibt ungeprüft — `unzip -Z` je Paket zeigt es.
- **Zeitstempel:** `.stignore` und die Unit vom 10. September, alle übrigen Dateien in `files/` vom 11. September 15:37 — der Stand nach der Umstellung, wie erwartet. Die `.pyc`-Dateien tragen `cpython-312`: Auf diesem Rechner läuft das Prüfskript unter Python 3.12; Befund 15 ist hier ohne Wirkung und bleibt eine Portabilitätsnotiz.
- **Weiter ungeprüft:** ob `__pycache__` per `.gitignore` ausgeschlossen ist (B.1 sagt ja; ohne `git status` nicht bestätigbar); ob die Zip-Pakete dem Stand von `files/` entsprechen (das belegt ein Lauf von `scripts/pack_packages.sh` oder `unzip -Z`); ob `c9a6e27` wirklich der geprüfte HEAD ist.

**Das Prüfskript ist nicht gelaufen** — die Freigabe wurde nicht erteilt. Aufruf: `/usr/bin/python3 home-.claude-sharing/tests/test_dialog_and_naming.py`; es schreibt nur unter `/tmp`, braucht keinen Bildschirm, kein Zenity, kein Syncthing, etwa drei Sekunden, und endet mit Rückgabewert 1 bei der ersten Abweichung. Erwartung: heute grün — auch mit Befund 1, denn die Gruppe ist blind (Befund 16). Nach der Korrektur von 1 und 16 muss die Gruppe „Sitzungserkennung“ mit zonentragenden Stempeln erst fallen und dann stehen.

**Drei Fragen:**

1. Tragen die vier Rechner bereits den mehrsprachigen Stand (`messages.py`, `messages_de.py`, `conflict-resolution.de.md`), und wurde der Dienst danach über `install_service.sh` neu gestartet? Falls nicht, ist der heiße Test zugleich die erste Aktualisierung einer bestehenden Installation — dann gilt Befund 18 vor dem Test.
2. Welcher Terminal-Emulator ist auf dem Testrechner der zwischengespeicherte (`terminal_cmd` in `zustand.json`)? Bei konsole oder xterm trifft Befund 1 nach dreißig Minuten sicher; bei gnome-terminal nicht, weil die PID dort von Anfang an tot ist — dann würde der Test Befund 1 nicht zeigen, und er bliebe offen.
3. Darf ich, nach Freigabe, lesend per Shell die Dateiliste, die Paketinhalte und das Prüfskript nachziehen und die Ergebnisse als Nachtrag an dieses Dokument anfügen? Dann stünde in Abschnitt VI nichts Ungeprüftes mehr.
