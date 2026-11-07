# Plan: Clean-up-Skill für Linux-Desktops

Stand: 2026-11-07. Das Dokument hält nur Festlegungen fest. Implementierungssprache der Skripte: Python, nur mit der Standardbibliothek.

## 1 Zweck und Geltung

- Der Skill löscht nur unnütze Datenansammlungen und weist den Nutzer auf Datenmengen hin, um die er sich selbst kümmern muss.
- Er entfernt keine installierte Software, auch nicht, wenn sie vermutlich nicht mehr gebraucht wird. Solche Funde werden nur gemeldet.
- Geltungsbereich: Linux-Desktops und -Laptops (Ubuntu, Kubuntu und ähnliche), keine Server. Er geht nicht vom Istzustand eines einzelnen Rechners aus, sondern misst den Zustand jedes Mal neu.
- Sprache: Der Skill entsteht in einer deutschen und einer englischen Fassung. Zuerst wird die deutsche Fassung samt README fertiggestellt; die englische folgt danach (`work-plan.md`, Schritt 20). Die Sprache steht zu Beginn fest: aus dem bisherigen Kontext des Chats, sonst aus der installierten Fassung. Antwortet der Nutzer in einer anderen Sprache, arbeitet der Skill in dieser weiter. Die Skripte geben ihre Bildschirmmeldungen einheitlich auf Englisch aus; ihre Ergebnisse liest die Instanz und berichtet dem Nutzer in seiner Sprache.

## 2 Grundsätze

1. Nichts ist pauschal. Für jeden Bereich ist einzeln festgelegt, wie der Skill damit umgeht.
2. Drei Arten der Behandlung je Bereich: **löschen ohne Rückfrage**, **vor dem Löschen fragen**, **nur vorschlagen oder melden**.
3. Ein Aufräumbefehl eines Programms wird nur eingesetzt, wenn feststeht, was er genau entfernt. Sammelbefehle wie `docker system prune` sind nicht pauschal erlaubt.
4. Ohne Entscheidung des Nutzers gelöscht werden nur programmeigene Zwischendateien, die rein aus Performance-Gründen angelegt werden und die das Programm entweder nicht mehr benötigt oder jederzeit on-the-fly und vollautomatisch neu erzeugt, wenn sie fehlen. Zustand, Einstellungen, Datenbanken und Nutzdaten bleiben. Zwei Extremfälle grenzen das ab:
   - Dazu gehört ein HTTP-Cache: Er hält nur eine Kopie einer bereits heruntergeladenen Datei vor, damit ein erneuter, langsamer Zugriff ins Internet entfällt.
   - Nicht dazu gehören die Proxy-Dateien eines Videoschnittprogramms: datenreduzierte Fassungen der Quellvideos, mit denen die Vorschau während der Bearbeitung mit wenig Ressourcen rechnet. Sie sind keine bloßen Kopien, sondern veränderte Repräsentanten der eigentlichen Daten, entstehen in einem eigenen Arbeitsschritt und werden nicht on-the-fly neu erzeugt, wenn sie fehlen. Das sind Arbeitsdaten, kein Cache.

   Nutzdaten wie Downloads, Installationsdateien, Images und Medien (Abschnitte 4.7 bis 4.10) löscht der Skill nur nach Entscheidung des Nutzers.
5. Jeder Lauf endet mit einem Ergebnisbericht: was gelöscht wurde, wie groß die entfernte Datenmenge war (nicht der frei gewordene Platz), was nur gemeldet wurde. Wurde gesichert, nennt er die Sicherungen (Name, Ort, Größe) und dass sie Platz festhalten, bis sie entfernt sind; sie lassen sich später mit dem Skill aufräumen (3.9).
6. Nutzereingaben: Was zu erhalten und was zu löschen ist, formuliert allein der Nutzer. Die Instanz bewertet die Angaben und überführt sie in eine schematisch richtige Zuordnung, die dem Skript oder Befehl übergeben wird. Das gilt für alle Nutzereingaben im Skill.
7. Ordnernamen: Sie werden bei der Abarbeitung an die Sprache des Systems und des Desktops des Nutzers angepasst. Namen wie `Downloads`, `Videos`, `Musik`, `Bilder` oder `Dokumente` stehen in keiner Zeichenkette eines Skripts. Die Instanz ermittelt den Pfad auf dem Rechner (XDG-Benutzerverzeichnisse: `~/.config/user-dirs.dirs`, `xdg-user-dir`), prüft im Home, dass der Ordner existiert, und startet erst dann das Skript oder den Agenten. Sie übergibt den aufgelösten Pfad als Parameter. Messbefund: Auf diesem Rechner heißen `Downloads` und `Videos` englisch, `Musik`, `Bilder`, `Dokumente`, `Schreibtisch` deutsch.
8. Eingehängtes und Links: Was eingehängt ist (anderes Dateisystem, Netzfreigabe, Bind-Mount), wird nie gelöscht, nie durchlaufen und nie angefasst — nicht einmal gelesen, gezählt oder mit `stat` abgefragt. Der Grund ist die Netzfreigabe: Schon die Abfrage ihres Wurzelordners blockiert, wenn der Server nicht antwortet, und ein Prozess in diesem Zustand lässt sich auch mit `kill -KILL` nicht sofort beenden (Messbefund vom 7. November 2026, Probelauf zu 4.12 im ersten Lauf des installierten Skills: Zustand `D`, Kernel-Stack `cifs … wait_for_response`). Deshalb entscheiden die Skripte über Einhängepunkte **nach dem Namen**, gegen die Liste in `/proc/self/mountinfo`, bevor ein Systemaufruf auf den Pfad geht; erst danach prüfen sie das Gerät. Die Liste wird höchstens einmal je Sekunde neu gelesen, damit auch eine Einhängung während des Laufs erkannt wird, und das Home wird über `realpath` aufgelöst. Die Abgrenzung:
   - **Im Home** wird nichts angefasst, was auf einem anderen Einhängepunkt liegt als das Home selbst, auch kein fester Pfad (Papierkorb, Cache-Ordner, Download-Ziel) und kein Ziel eines Links.
   - **Benannte Systemquellen** außerhalb des Homes (Journal, `/var/log`, die Analysewurzeln `/var`, `/opt`, `/usr/local`, `/srv`) sind gewollte Ziele; ein Durchlauf, der dort beginnt, überschreitet keine weitere Grenze.
   - **Der Zielort einer Archivsicherung** (3.2), den der Nutzer wählt, auch eine Netzfreigabe, wird nur beschrieben und nie durchlaufen.
   - **Gelesen werden nur lokale Dateisysteme** (Blockgerät oder ZFS) beim Füllstand; Netz-, FUSE- und Speicher-Dateisysteme erscheinen dort nicht.
   - Eingehängte Daten werden nur an ihrem echten Ort erfasst, wenn dieser im Untersuchungsbereich liegt. Will der Nutzer sie aufräumen, geht er an diesen Ort.
   - Beim Zurückholen (3.2, 3.10) werden Ziele an oder unter einem Einhängepunkt ausgelassen und gemeldet; dort wird nichts angesehen.
   - Symbolische Links werden nie verfolgt; auch ihr Ziel wird nicht gelesen. Die einzige Ausnahme sind die Starter-Einträge für Tabelle 2 (4.11): Das Ziel eines Links wird zuerst nur als Text aufgelöst und gelesen, wenn es auf keinem fremden Einhängepunkt liegt; sonst bleibt der Eintrag außen vor und wird mit Grund gemeldet. Gelöscht wird ein Link selbst nur im Papierkorb (4.14), sein Ziel nie.
9. Eigene Sicherungen: Alle Snapshots und Archive, die der Skill anlegt, tragen den Namenspräfix `cleaning-up-linux-desktop-` mit Datum und Uhrzeit. Die Skripte fassen Snapshots und Archive ohne diesen Präfix nie an; davon weicht der Skill nur auf ausdrücklichen Wunsch des Nutzers ab. Dateien mit dem Präfix sind von allen Löschläufen ausgenommen.

Zum Alter einer Datei: Wo dieses Dokument die Anlegezeit nennt (4.2 bis 4.4, 4.9), verwenden die Skripte die Zeit der letzten Statusänderung (`ctime`). Das Anlegedatum liefert Python 3.12 unter Linux nicht. Die Statusänderung ist nie älter als das Anlegen; eine Datei erscheint damit höchstens jünger, als sie ist, und wird im Zweifel nicht gelöscht.

## 3 Ablauf des Skills

### 3.1 Beginn

**Betriebsarten.** Der Skill kennt drei: das Aufräumen (der normale Lauf, dieser Abschnitt und die folgenden), das Aufräumen der Sicherungen eines früheren Laufs (3.9) und die Wiederaufnahme nach einem abgebrochenen Lauf (3.10). Zuerst sucht die Instanz das Protokoll (3.8). Findet sie es im Home nicht, fragt sie, ob es unter anderem Namen oder an anderer Stelle liegt; erst danach gilt: kein Protokoll. Dann schlägt sie die Betriebsart vor: kein Protokoll heißt normaler Lauf, ein offener Schritt führt zur Wiederaufnahme, ein abgeschlossener Lauf mit noch vorhandenen Sicherungen zum Aufräumen der Sicherungen. Der Nutzer entscheidet. Die Schritte 2 bis 7 gelten für alle Betriebsarten, Schritt 8 nur für den normalen Lauf.

1. In Claude Code wird der Skill nur über `/cleaning-up-linux-desktop` aufgerufen (`disable-model-invocation: true`); eine Rückfrage, ob er angewendet werden soll, entfällt dort. Wurde er nicht ausdrücklich aufgerufen — etwa auf claude.ai, wo er von selbst geladen werden kann —, fragt er zuerst, ob er jetzt angewendet werden soll. Bei "nein" endet er.
2. Er nennt, wofür er vorgesehen ist (Abschnitt 1).
3. Er erklärt die Arbeitsweise: Grundsätzlich startet der Skill selbst keine Skripte oder Befehle auf dem System; die Ausnahme regelt Schritt 5. Es gibt zwei Wege, beide mit der Ausführung durch den Nutzer (damit sind auch root-Zugriffe unproblematisch):
   - Der Skill übergibt dem Nutzer einen Codeblock. Der Nutzer führt ihn aus. Dabei entsteht eine Datei im Ordner `/tmp`, die der Skill liest. Dafür braucht er Zugriff auf `/tmp`.
   - Der Skill erstellt ein Skript in `/tmp` oder nutzt ein im Skill vorhandenes und übergibt dem Nutzer den Aufruf. Die Ergebnisse landen wieder in `/tmp` und werden vom Skill ausgewertet.
4. Der Skill ermittelt, wo er läuft:
   - In der Claude-App (claude.ai): Zu jedem Block und jedem Skript sagt er dem Nutzer immer, welche Datei danach hochzuladen ist.
   - Nicht in der Claude-App (Claude Code): Er fragt, ob er auf dem betreffenden System gestartet wurde. Wenn ja und der Nutzer nur will, dass Claude Code die Ergebnisse in `/tmp` liest, gibt er ihm den Befehl `/add-dir /tmp` vor, nicht `/cd`. Dann kann er alle Ergebnisdateien auswerten, ohne dass der Nutzer jedes Mal den Zugriff außerhalb des Arbeitsverzeichnisses freigeben muss. Das gilt für Claude Code in der Konsole. In der Erweiterung von VS Code gibt es `/add-dir` nicht (vom Nutzer geprüft); Lesen in `/tmp` funktioniert dort trotzdem; im Berechtigungsmodus "auto" ohne Rückfrage, sonst muss der Nutzer jeden Zugriff einzeln freigeben (Beobachtung des Nutzers). Der Skill sagt das zu Beginn an, damit die Rückfragen nicht überraschen.
5. Auf ausdrücklichen Wunsch des Nutzers führt der Skill Skripte selbst aus. Diese Variante bietet er nur an, wenn er auf demselben System läuft. Voraussetzung ist, dass der Nutzer die Session vorher mit `/cd /tmp` in diesen Ordner verlegt hat. Root-Zugriffe delegiert er trotzdem an den Nutzer. Eine Prüfung der Claude-Code-Version entfällt, `/cd` gibt es seit mehreren Monaten. `/cd` funktioniert in Claude Code in der Konsole, in der Erweiterung von VS Code nicht (beides vom Nutzer geprüft). Dort ist diese Variante also nicht möglich.
6. Er teilt dem Nutzer mit: Der Vorgang dauert länger, kann umfangreiche Internetrecherchen umfassen und verbraucht zahlreiche Token. Für ein gutes Rechercheergebnis empfiehlt er das Modell Opus. Außerdem sagt er deutlich: Für die Funktion des Skills wird keine Gewähr übernommen, gelöschte Dateien kommen nur über eine Sicherung zurück; er empfiehlt, vor dem ersten Löschen mindestens ein vollständiges Backup oder einen Snapshot anzulegen und zu prüfen, dass es sich zurückspielen lässt. Der Skill macht das an dieser Stelle gemeinsam mit dem Nutzer (3.2); wer will, kann es auch schon vorher selbst tun (sinngleich mit dem Abschnitt „Ohne Gewähr“ der README).
7. Der Nutzer bestätigt diese Arbeitsweise, bevor es weitergeht.
8. Er fragt alle Angaben ab, die die Analyse vom Nutzer braucht, bevor sie startet: die Größenschwelle, eine einzige Zahl für 4.8, 4.10 und die großen Einzeldateien in Tabelle 3 (Vorgabe 150 MiB), und ob in 4.8 auch allgemeine Archivformate erfasst werden. Die Analyse läuft danach ohne weitere Rückfrage.

### 3.2 Sicherung

**Zeitpunkt.** Die Analyse liest nur und braucht keine Sicherung. Gesichert wird vor dem ersten Löschen und ein zweites Mal vor dem Nachgang zu Tabelle 2 und 3 (3.5), weil dort Ungetestetes geschieht. Ob statt dessen vor jedem Aufräumschritt gesichert wird, entscheidet der Nutzer; Vorgabe ist einmal je Zeitpunkt. Die Wahl kommt ins Protokoll (3.8).

**Varianten.** Nach der Analyse bietet der Skill alle an, die das System hergibt, und der Nutzer entscheidet; die Wahl, der Zielort und die Namen kommen ins Protokoll:

1. Eigene Sicherung: Der Nutzer bestätigt, dass eine aktuelle Sicherung vorliegt, die sich zurückspielen lässt. Der Skill sichert dann nichts selbst.
2. Snapshot des Dateisystems, schreibgeschützt: btrfs (getestet). ZFS und LVM werden erkannt und gemeldet, sind aber ungeprüft: Es fehlt ein Testsystem, und der Skill enthält keinen eigenen Snapshot-Befehl dafür. Dort sichert der Nutzer selbst oder wählt das Archiv. Der Ubuntu-24.04-Desktop-Installer bietet ZFS und LVM an, btrfs nicht ([Ubuntu-Dokumentation](https://ubuntu.com/desktop/docs/en/24.04/reference/advanced-disk-setup-features/)); ext4 und xfs ohne LVM kennen keine Snapshots.
3. Timeshift oder Snapper, wenn die Analyse sie erkennt: Der Skill gibt deren Befehle als Block, die Namen oder Kennungen kommen ins Protokoll. Das Skript `snapshots.py` fasst sie nicht an.
4. Archiv der zu löschenden Dateien (unten).

**Erkennung.** Die Analyse (3.3) stellt fest, ob btrfs, ZFS oder LVM vorliegt, ob Timeshift oder Snapper installiert und eingerichtet sind, welche Snapshots es schon gibt und wie viel Platz je Dateisystem frei ist. Snapshots halten gelöschte Daten fest: Platz wird erst frei, wenn sie entfernt sind (3.9).

**Archiv.**

- Umfang: Nutzdaten (4.7 bis 4.10, Download-Ordner, Papierkorb) und Anwendungsordner, für die kein Beleg vorliegt, dass es reine Caches sind (Nachgang zu Tabelle 2 und 3). Belegte Caches (Tabelle 1) werden nicht gesichert. Vor jeder Sicherung fragt der Skill, ob der Nutzer sie wirklich will.
- Formate, der Nutzer wählt:
  - **tar** (GNU tar im pax-Format): behält Besitzer, ACLs, erweiterte Attribute (`--acls --xattrs`), Hardlinks und Links. Nach dem [GNU-tar-Handbuch](https://www.gnu.org/software/tar/manual/html_node/Extended-File-Attributes.html) werden beim Entpacken nur erweiterte Attribute im Namensraum `user` wiederhergestellt. Ein Ordner `cleaning-up-linux-desktop-backup-<Datum>-<Uhrzeit>/` je Lauf, darin je Sicherungsschritt ein tar. Bei schnellem Ziel (interne SSD) unkomprimiert, bei langsamem (USB-Stick, Netz) als `.tar.gz` mit Stufe 1; der Nutzer entscheidet. Vorgabe ist tar, weil die Nutzdaten meist unkomprimierbar sind und nichts verloren geht.
  - **ZIP:** im selben Ordner je Lauf wie beim tar je Sicherungsschritt eine Datei `NN-<Schritt>.zip`. Nicht eine Datei je Lauf: Ein Abbruch beim Anhängen macht auch frühere Schritte unlesbar (am 7. November 2026 ausprobiert: Das ZIP ließ sich danach nicht mehr öffnen). Dateiweise: Video, Audio, Bilder, Archive, Images und `.deb` (nach Dateiendung) werden nur abgelegt, alles andere mit Stufe 3 gepackt. Wer ZIP wählt, erfährt ausdrücklich, was verloren geht: Besitzer, ACLs, erweiterte Attribute (nach meinem Wissen, nicht geprüft, zum Beispiel die Herkunfts-URL von Downloads sowie Tags und Bewertungen aus Dolphin) und Hardlinks; Links werden als Links gespeichert, nie verfolgt. Beim Zurückholen aus einem ZIP erhalten neue Dateien den Besitzer ihres Elternordners.
- Zielort: Vorgabe `~/`. Der Skill fragt, ob der Nutzer lieber ein externes Gerät nimmt (Stick, Netzfreigabe). Bei einer Netzfreigabe weist er darauf hin, dass die Übertragung in der Regel deutlich länger dauert als an einem direkt angeschlossenen, ausreichend modernen Speichergerät. Liegt das Ziel auf demselben Dateisystem wie die Daten, wird durch das Aufräumen kein Platz frei, solange das Archiv existiert.
- Platzprüfung: Vor jedem Sicherungsschritt prüft das Skript, ob der freie Platz am Ziel für die Gesamtmenge reicht (unkomprimiert gerechnet, dazu 2 KiB je Datei, Ordner und Link für Verwaltungsblöcke; gemessen: 560 MB Nutzdaten in 40.000 Einträgen ergaben 630 MB Archiv) und danach eine Reserve bleibt. Vorgabe ist die größere von 10 % des Ziel-Dateisystems und 10 GiB. Der Nutzer darf sie senken, aber nie unter die größere von 5 % und 5 GiB. Reicht der Platz nicht, bricht das Skript ab, und der Skill schlägt ein anderes Ziel vor.
- Ablauf: Probelauf von `delete.py` mit Kandidatenpfaden (`--with-paths`), dann `backup.py` (schreibt das Archiv und verifiziert es: Vorgabe ist der Vergleich mit den Dateien, also ein zweites Lesen; nur auf Wunsch des Nutzers die schnelle Prüfung), erst dann das echte Löschen. Scheitert die Sicherung, wird nichts gelöscht.

**Zurückholen.** Selektiv: nur fehlende Dateien aus der Sicherung zurückkopieren, nichts überschreiben. Ein Zurückrollen eines ganzen Subvolumes oder Dateisystems geschieht nur auf ausdrücklichen Wunsch und mit Warnung: Das Protokoll im Home würde auf den Stand des Snapshots zurückgesetzt.

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

Vor den Tabellen nennt der Skill den Füllstand je lokalem Dateisystem (belegt, Gesamtgröße, Prozent); Netzfreigaben und andere nicht lokale Dateisysteme erscheinen nicht, weil schon ihre Abfrage hängen kann (Grundsatz 8). Gibt es btrfs-Snapshots, nennt er ihre Zahl und, wenn die btrfs-Quotas aktiv sind, ihre Belegung; sonst entfällt diese Angabe. Dazu nennt er, welche Snapshot-Fähigkeiten und -Werkzeuge das System bietet (3.2). Der Füllstand zeigt, auf welchem Dateisystem Aufräumen überhaupt etwas bringt.

Aufbau der Tabellen:

- Die Analyse durchläuft das Dateisystem nur ein einziges Mal und erfasst dabei alles, was die Tabellen brauchen.
- Das Analyseskript liefert maschinenlesbare Daten. Die Tabellen baut die Instanz daraus; in Tabelle 2 ergänzt sie die Ergebnisse der Recherche.
- Jede Tabelle zeigt nur eine Zusammenfassung je Bereich, eine Zeile je Bereich. Die Einzelheiten (Einzellisten, Histogramm, nummerierte Auswahllisten) kommen erst, wenn der Bereich bearbeitet wird. Nach der Datenerfassung wird nicht alles sofort präsentiert.
- Spalten von Tabelle 1: Bereich (mit Abschnitt in diesem Dokument), Fundort, Größe, Behandlung (ohne Rückfrage / mit Rückfrage / nur melden), braucht root, Programm muss beendet sein, Hinweis zur Sicherung.
- Spalten von Tabelle 2: Programm, Ordner, Größe, Belegstufe mit Quelle, Programm muss beendet sein, Kommentar zur Sicherung.
- Inhalt von Tabelle 3 (ermittelt per Test, `tests/table3_probe.py`; jeweils ohne die Bereiche aus Abschnitt 4):
  - Größe je Verzeichnis: die oberste Ebene unter dem Home und den Systemverzeichnissen mit Größe. Tiefere Ebenen nur, wenn ein Unterordner den Elternordner nicht bloß wiederholt. Für Verzeichnisse im Home eine zusätzliche Spalte: Anteil der Daten, die seit über einem Jahr unverändert sind (für Systemverzeichnisse nicht, weil Software Änderungszeiten oft festsetzt). Treffer, die einem Bereich aus Abschnitt 5 entsprechen, sind gekennzeichnet.
  - Große Einzeldateien ab der Größenschwelle, die der Nutzer vor der Analyse angibt (3.1, Schritt 8; dieselbe Zahl wie für 4.8 und 4.10, Vorgabe 150 MiB), soweit 4.7, 4.8 und 4.10 sie nicht abdecken: zusammengefasst je Bereich aus Abschnitt 5 eine Zeile mit Zahl und Summe, alles Übrige als eine Zeile "Sonstiges". Die Einzeldateien zeigt der Skill erst bei der Bearbeitung.
  - Reste deinstallierter Programme: Das Skript liefert die Anwendungsordner im Home (`~/.config`, `~/.local/share`, `~/.cache`, `~/.var/app` und Punkt-Ordner im Home) mit Größe und letzter Änderung, ohne die Bereiche aus Abschnitt 4. Die Instanz ordnet sie der erfassten Anwendersoftware (4.11), Desktop- und Systembestandteilen sowie Werkzeugen ohne Starter-Eintrag zu und zeigt nur die Ordner ohne Zuordnung, je mit Begründung. Ein reiner Namensabgleich taugt nur als Vorfilter (im Test zwei Drittel Fehlalarme). Gelöscht wird nur nach Entscheidung des Nutzers: Ein Rest kann Einstellungen enthalten, die bei einer Neuinstallation wieder gebraucht werden.
  - Doppelte Dateien ab 1 MiB, nur Nutzerdaten im Home: ohne Anwendungsordner, ohne `.git`-Ordner, ohne Entwicklungsartefakte und ohne Systemverzeichnisse (dort sind Kopien programmintern oder, bei Git LFS, systembedingt). Erst nach Größe gruppiert, dann per Inhalt verglichen. Der Vergleich läuft parallel: Ein Pool aus der halben Zahl der physischen Kerne (aufgerundet, wie bei der Journal-Auswertung, 4.5) hasht eine Datei je Aufgabe, zuerst die erste MiB aller Kandidaten, dann den ganzen Inhalt nur dort, wo Größe und Anfang übereinstimmen. Gruppierung und Reihenfolge bleiben im Hauptprozess und entsprechen einem sequentiellen Lauf; ein Pfad, der inzwischen auf einem Einhängepunkt liegt, wird nicht gelesen (Grundsatz 8). Messbefund (Entwicklungsrechner, 8 Kerne, also 4 Worker; die 1.122 bekannten Duplikate mit 8,87 GB, Dateien im Cache): 3,2 s statt 11,7 s nacheinander, mit demselben Ergebnis. In der Tabelle Zahl der Gruppen und überzählige Menge; bei der Bearbeitung je Gruppe alle Fundorte, der Nutzer entscheidet, welche Kopie bleibt.
  - Reste abgebrochener Git-Abrufe (`tmp_pack_*`, `tmp_idx_*`, `tmp_obj_*` innerhalb von `.git`): Zahl und Größe. Die Behandlung folgt mit dem Bereich "Git-Repositories" aus Abschnitt 5.
  - Caches ohne zugeordnetes Programm: Ordner unter `~/.cache`, die die Instanz keinem Eigentümer zuordnen kann (4.11), mit Größe und letzter Änderung.
  - Absturzabbilder: nur `/var/crash` und der Ordner von systemd-coredump; eine Zeile nur, wenn dort etwas liegt. Die Behandlung wird recherchiert, wenn ein Rechner dort etwas hat. Eine Suche nach Dateien namens `core` entfällt (im Test nur Fehltreffer).
  - Entwicklungsartefakte (`.venv` und andere Ordner mit `pyvenv.cfg`, `node_modules`, `build`, `dist`, `target`, Werkzeug-Caches) nur in Projekten im Home, erkannt an einem Projektkennzeichen (`.git`, `pyproject.toml`, `package.json`, `Cargo.toml` u. a.); ohne Anwendungsordner, Punkt-Ordner im Home und Systemverzeichnisse (dort sind es meist Teile installierter Software). Je Projekt eine Zeile: Größe der Artefakte, letzte Änderung an den Quelldateien, ob eine Abhängigkeitsliste vorhanden ist. `__pycache__` gehört nicht hierher, sondern zu 4.12. Ausnahme von der Bindung an Projekte: Python-Umgebungen (Ordner mit `pyvenv.cfg`) zählen auch außerhalb eines Projekts, mit dem übergeordneten Ordner anstelle des Projekts; die allgemeinen Namen (`build`, `dist`, `target` …) bleiben an Projekte gebunden, weil nur bei ihnen Fehltreffer drohen. Anlass: Der erste Lauf des Analyseskripts verlor eine Umgebung mit 2,4 GiB in einem Ordner ohne Projektkennzeichen.
  - Verworfen nach dem Test: Zuwachs in den letzten Tagen (ein einzelner Lauf misst nur geänderte, nicht gewachsene Daten) und Datenmenge je Dateiart (keine neue Handlungsmöglichkeit gegenüber Ort und Größe).

Ausgabe während der Analyse: Dauern einzelne Schritte lange (der Lüfter kann dabei hochdrehen), gibt das Analyseskript, das der Nutzer ausführt, laufend aus, welchen Analyseschritt es gerade ausführt.

Software-Erfassung: Zu Beginn der Analyse erfasst der Skill auch die Anwendersoftware des Nutzers (Abschnitt 4.11). Dem Nutzer sagt er dazu nur, dass er prüft, welche Software Cache- und Download-Ordner mitbringt, und dass er sich im Internet über die Details der Programme informiert. Am Ende der Analyse nennt er dem Nutzer kurz die Software, zu der er bei der Bereinigung noch Vorschläge machen wird. Firefox, Chrome und VS Code stehen in dieser Liste, falls sie installiert sind. Die durch Recherche belegten Ordner dieser Software stehen in Tabelle 2.

### 3.4 Zweite Aufgabe: Tabelle 1

Der Skill schlägt vor, zuerst Tabelle 1 Schritt für Schritt gemeinsam mit dem Nutzer abzuarbeiten und dabei aufzuräumen. Die Empfehlung zur Sicherung hat der Skill schon zu Beginn ausgesprochen (3.1, Schritt 6). Vor dem ersten Löschen sichert er gemeinsam mit dem Nutzer (3.2) und trägt die Sicherung ins Protokoll ein (3.8).

Die Zeilen für Log-Files und Journal (4.5) sowie für Nutzdaten (4.7 bis 4.10) tragen den Hinweis, dass Gelöschtes nur über ein Backup oder einen Snapshot zurückkommt. Getestet ist dort der Löschvorgang; ob eine Datei noch gebraucht wird, entscheidet der Nutzer.

### 3.5 Nachgang zu Tabelle 2

Mit Tabelle 1 und dem Ergebnisbericht (Grundsatz 5) endet der eigentliche Lauf des Skills. Vor dem Nachgang bietet der Skill eine neue Sicherung an (3.2). Danach bietet er einen Nachgang an, zuerst zu Tabelle 2, dann zu Tabelle 3 (3.6); der Nutzer kann nach jedem Teil aufhören. Tabelle 2 kommt vor Tabelle 3, weil für ihre Posten die Recherche schon vorliegt. Für ihre Zeilen gilt:

- Jede Zeile nennt die Einschätzung des Belegs in zwei Stufen:
  - **hoch**: Die offizielle Dokumentation des Programms sagt es ausdrücklich.
  - **mittel**: Es steht nur in einem Entwicklerforum, im Issue-Tracker des Programms oder in einem Distributions-Wiki.
- Ein Ordner, der nur durch Drittquellen oder durch Rückschluss aus mehreren Hinweisen belegt ist, gilt als "kein klarer Befund" (Abschnitt 4.11) und steht in keiner Tabelle.
- Ein Kommentar in der Zeile darf darauf hinweisen, dass ein Backup oder Snapshot angebracht sein kann, weil die Maßnahme nicht getestet ist.
- Für das Löschen gelten die Regeln aus 4.11, insbesondere die Aufforderung, das Programm vorher zu beenden.

Nachgang zu Tabelle 2: Der Skill wiederholt die Stellen aus Tabelle 2 und sagt dem Nutzer, dass er für diese Posten keine getesteten und belegten Erfahrungen besitzt. Er bietet an, alle oder einen Teil davon gemeinsam weiter zu klären: Recherchen in der Dokumentation, gemeinsam Strategien zum Aufräumen entwickeln und ausführen. Dabei geht er gewohnt vorsichtig vor und erinnert den Nutzer vor jedem Löschen daran, was tatsächlich belegt und was Vermutung ist, damit der Nutzer abschätzen kann, ob wirklich gelöscht werden soll. Das Löschskript nimmt für Tabelle 2 keinen Auftrag an; gelöscht wird im Nachgang wie bei einer zusätzlich angeforderten Aufgabe (3.7).

### 3.6 Nachgang zu Tabelle 3

Nach dem Nachgang zu Tabelle 2, oder wenn der Nutzer ihn auslässt, bietet der Skill an, den Rest gemeinsam zu erforschen: Inhalte genauer ansehen, Internetrecherche hinzuziehen. Dabei gilt:

- Der Skill sagt, dass er dafür keine vorgefertigten Anweisungen und Lösungen hat. Sie werden erst erarbeitet.
- Er führt den Nutzer durch die einzelnen Befunde und erarbeitet mit ihm Schritt für Schritt, ob es dort überhaupt etwas zu tun gibt und wie man es angehen würde.
- Vorher wird dort nichts selbständig aufgeräumt.
- Der Skill weist den Nutzer darauf hin, dass die erarbeiteten Maßnahmen möglichst gut belegt sein sollten, damit kein Unfall passiert.
- Er weist darauf hin, dass die hier erarbeiteten Aufräumarbeiten völlig ungetestet sein werden und deshalb eine vollständige Sicherung beziehungsweise der Snapshot-Mechanismus (Abschnitt 3.2) dringend zu empfehlen ist.

### 3.7 Zusätzlich angeforderte Suchen

Bittet der Nutzer den Skill zusätzlich, nach weiteren Dateien zu suchen, und beschreibt er, welche er meint, gilt keine der bisherigen Regeln dieses Plans. Das ist kein Automatismus des Skills, sondern eine zusätzlich angeforderte Aufgabe. Ihre Randbedingungen beruhen nicht auf den Festlegungen des Skills, sondern werden im Einzelnen mit dem Nutzer ausgehandelt.

### 3.8 Protokoll

Zweck: Ein kurzes Protokoll des Laufs, nur damit in einer neuen Sitzung ein Rollback möglich ist.

- **Ort und Name:** Vorgabe im Home, `cleaning-up-linux-desktop-protocol.md`. Beim Start sucht die Instanz dort; gibt es nichts, fragt sie nach einem anderen Namen oder Ort und kann die Datei über ihre erste Zeile suchen lassen: `analyze.py --find-protocol` durchsucht das Home nach Markdown-Dateien mit dieser Zeile, ohne `sudo` und ohne einen Einhängepunkt anzufassen (Befehlsblock für den Nutzer). Liegt das Protokoll auf einem Einhängepunkt, nennt der Nutzer den Pfad.
- **Kopfzeile:** Die erste Zeile lautet genau `# cleaning-up-linux-desktop Protocol`. Nur sie ist als Token englisch; der übrige Text steht in der Sprache des Nutzers, solange er nichts anderes will.
- **Aufbau:** ein Kopf mit den Eckdaten des Laufs (gewählte Sicherungsvariante, Zielort, Takt der Sicherung), dann das Protokoll, je Sitzung mit Datum, und ein eigener Abschnitt „Sonderbehandlungen“ ohne Protokollcharakter.
- **Einträge, kurz:**
  - Je Schritt eine Zeile mit Bereich und was getan wurde. Die Instanz schreibt „begonnen“, wenn sie den Befehlsblock übergibt, und danach „erledigt“ oder „abgebrochen“. So bleibt ein Abbruch mitten im Schritt sichtbar.
  - Je Löschschritt die betroffenen Ordner (nicht jede Datei), damit der Bereich aus der Sicherung zurückgeholt werden kann. Die Berichte unter `/tmp` überstehen keinen Neustart.
  - Übersprungene Schritte (mit dem Nutzer) und Besonderheiten.
  - Jede Sicherung (Snapshot oder Archiv) und jedes Entfernen einer Sicherung als eigener Schritt mit Namen und Ort.
- **Sonderbehandlungen:** Hier steht, was mit dem Nutzer besonders vereinbart wurde, zur Wiederverwendung beim nächsten Lauf. Ob etwas aufgenommen wird, fragt der Skill; beim nächsten Lauf fragt er, ob die Sonderbehandlungen wieder gelten sollen.
- **Schreiben:** In Claude Code schreibt die Instanz die Datei selbst. Auf claude.ai gibt es sie als Download, bei einem neuen Start lädt der Nutzer sie hoch.

### 3.9 Betriebsart: Aufräumen der Sicherungen

- Nur, wenn das Protokoll den letzten Lauf als abgeschlossen ausweist; sonst führt der Weg zu 3.10. Das Aufräumen lässt sich auf einen späteren Zeitpunkt legen, an dem der Nutzer sich überzeugen konnte, dass alles funktioniert; beim normalen Lauf wird ihm das am Ende gesagt.
- Ein lesendes Skript (`snapshots.py`) stellt fest, welche Sicherungen mit dem Präfix noch existieren und was sie festhalten. Zusammen mit dem Stand im Protokoll weiß die Instanz, was aufzuräumen ist.
- Der Nutzer entscheidet, was entfernt wird. Entfernt wird nur, was den Präfix trägt, und jedes Entfernen ist ein Schritt im Protokoll.
- Danach fragt der Skill, ob das Protokoll gelöscht werden soll; es wird nur gelöscht, wenn der Nutzer es will. Stehen Sonderbehandlungen darin, sagt der Skill das. Der Nutzer kann auch nur das Protokoll dieser und früherer Sitzungen entfernen und die Datei mit den Sonderbehandlungen stehen lassen.

### 3.10 Betriebsart: Wiederaufnahme nach einem Abbruch

- Gilt, wenn das Protokoll einen offenen Schritt oder einen nicht abgeschlossenen Lauf zeigt, zum Beispiel nach einem Neustart, bei dem die Sitzung verloren ging.
- Die Instanz liest das Protokoll, stellt den Stand dar (erledigt, begonnen ohne Abschluss) und prüft, ob die genannten Sicherungen noch vorhanden sind (`snapshots.py`).
- Dann schlägt sie vor, einen oder alle Schritte zurückzuholen (selektiv, 3.2) oder fortzusetzen. Der Nutzer entscheidet. Zurückgeholt wird je Schritt aus der Sicherung, die das Protokoll nennt. Gibt es keine, weist die Instanz auf die eigene Sicherung des Nutzers hin, die er selbst zurückspielt.

### 3.11 Stillstand eines Durchlaufs

Ein Skript kann in einem Ordner steckenbleiben, den es nicht umgehen konnte: eine Netzfreigabe, die ohne Einhängepunkt im Namen erreicht wird (zum Beispiel über einen Link), ein Gerät, das nicht antwortet, oder ein schlicht riesiger Ordner. Gegen das Hängen selbst helfen weder Zeitgrenzen noch Signale, solange der Prozess im Kernel wartet (Grundsatz 8); deshalb steht die Vermeidung an erster Stelle. Die Meldung sorgt dafür, dass ein Hänger sofort am Ort sichtbar ist, statt dass jemand minutenlang auf ein Skript wartet, das nichts tut.

- **Wer meldet:** jedes Skript, das Ordner durchläuft (`analyze.py`, `delete.py`, `journal_stats.py`, `backup.py`, `snapshots.py` beim Zurückholen). Ein Hilfsthread läuft neben dem Durchlauf, weil der Hauptfaden im Kernel warten kann.
- **Wann:** Alle 5 Sekunden prüft der Hilfsthread, ob der Durchlauf noch in demselben Ordner steht. Gemeint ist der tiefste Ordner, in dem er gerade liest, nicht der oberste des Auftrags. Verglichen wird dazu ein Schrittzähler, nicht der Pfadtext.
- **Was:** Steht er noch dort, schreibt das Skript eine Zeile nach `stderr` mit dem Ordner und der bisherigen Wartezeit; sie wiederholt sich bei jeder weiteren Prüfung mit der Gesamtzeit. Geht der Durchlauf danach weiter, meldet er das sofort, nicht erst bei der nächsten Prüfung. Die erste Zeile enthält zusätzlich den Hinweis auf einen riesigen Ordner oder ein nicht antwortendes Gerät, damit der Nutzer die Lage deuten kann.
- **Wortlaut** (der Skriptname steht vorn, weil der Nutzer die Zeile in einem Terminal liest und an die Instanz weitergibt):

  ```
  delete.py: still in "/pfad/ordner" after 5 s, no progress (huge folder or unresponsive mount?)
  delete.py: still in "/pfad/ordner" after 10 s, no progress
  delete.py: moved on after 23 s in "/pfad/ordner", now in "/pfad/anderer"
  ```
- **Bericht:** Jeder Stillstand steht außerdem in der Liste `stalls` (Ordner, Sekunden) im Bericht des Skripts, damit die Instanz hinterher sieht, was los war. Bei `analyze.py` steht sie in `meta`, bei `delete.py` im Bericht, bei `journal_stats.py` in `meta`, bei `backup.py` im Plan.
- **Grenze:** Überwacht wird nur das Durchlaufen von Ordnern. Externe Befehle (`journalctl`, `apt-get`, `docker`, `btrfs`, `tar`) werden nicht überwacht.
- **Aufgabe der Instanz:** Meldet der Nutzer, dass ein Lauf lange dauert, fragt sie zuerst nach den Zeilen dieser Meldung. Fehlen sie, lässt sie den Zustand des Prozesses ansehen (`ps -o pid,etime,stat,pcpu,cmd`, dazu `/proc/<pid>/wchan`): Zustand `D` ohne Plattenzugriff heißt, er wartet auf ein Gerät. Sie tut einen solchen Lauf nie als „dauert halt“ ab.

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

Weitere Ordner unter `~/.config/google-chrome` (Shader-, GPU- und Paket-Caches, heruntergeladene Komponenten) werden nicht angefasst. Gemessen auf dem Entwicklungsrechner zusammen rund 190 MiB, zu wenig für Recherche und Test. Ist der Ordner auf einem Rechner auffällig groß, zeigt ihn Tabelle 3 über die Größe je Verzeichnis.

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

**In der Anfangsanalyse (3.3)** erhebt das Analyseskript nur zwei Summen ohne Inhalt: den Speicherbedarf aller Log-Files (Abgrenzung wie unten in Punkt 7) und den des Journals (`/var/log/journal` und das flüchtige `/run/log/journal`). Sie stehen als zwei Zeilen in Tabelle 1. Die Auswertung unten läuft erst, wenn der Bereich bearbeitet wird, mit einem eigenen Skript (`work-plan.md`, Schritt 17).

**Auswertung beim Bearbeiten des Bereichs**

1. Das Skript gibt während der Analyse laufend aus, welchen Schritt es gerade ausführt.
2. Es erzeugt Multiprocessing-Worker, jeden für eine Datei (Journal-Dateien und Log-Files). Die Zahl der Worker ist die Hälfte der physischen Kerne, aufgerundet (ermittelt vor dem Start; logische Prozessoren nur, wenn die Kerntopologie nicht lesbar ist), höchstens so viele wie Dateien. Sie laufen mit niedriger Priorität (`nice`, `ionice`).
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
- Der Skill fragt den Nutzer vor der Analyse (3.1, Schritt 8), ob auch allgemeine Archivformate erfasst werden sollen.
- Der Nutzer gibt vor der Analyse die Größenschwelle an. Vorgabe ist 150 MiB.
- Gesucht wird nur im Home des Nutzers. Ausgenommen sind die Anwendungsordner `~/.config`, `~/.local` und `~/.cache` sowie der Papierkorb, weil dort Dateien liegen, die Anwendungen selbst benutzen (Beispiel: `~/.config/Claude/vm_bundles/…/rootfs.img`).
- Der Skill sammelt die Treffer, sortiert nach Größe absteigend, nummeriert und zeigt sie an.
- Der Nutzer nennt die Nummern, die der Skill vorher genauer untersuchen soll, ob es sich um wichtige Sachen handelt.
- Die Untersuchung beruht auf den üblichen Dateiendungen, auf Namen, Ordner und Datum der Dateien, nicht auf dem Inhalt.
- Der Skill zeigt die Liste mit Status erneut an, und der Nutzer entscheidet. Automatisch löscht der Skill nichts.

### 4.9 Download-Ordner

Dieser Schritt kommt im Ablauf vor 4.7, 4.8 und 4.10.

**Welche Ordner**

- Der Download-Ordner des Nutzers laut XDG-Benutzerverzeichnis (Grundsatz 7), außerdem Ordner, die der Nutzer in einem Browser als Download-Ziel eingestellt hat.
- Die Browser-Ziele liest die Instanz vor der Analyse aus, zusammen mit den XDG-Ordnern: bei Firefox `browser.download.dir` in `prefs.js` jedes Profils, bei Chrome `download.default_directory` in `Preferences` jedes Profils. Jeder gefundene Ordner geht als weiteres `--downloads` an das Analyseskript. Erfasst wird nur, was im Home liegt; Ordner außerhalb durchläuft die Analyse nicht.
- Weitere Download-Ordner ergeben sich aus der Erfassung der Anwendersoftware (Abschnitt 4.11). Der Skill sucht nicht pauschal nach Ordnern mit "Download" im Namen.
- Messbefund: Chrome und Firefox haben hier kein eigenes Download-Ziel eingestellt, sie nutzen den Standard.

**Analyse (im Analyseskript)**

- Für Dateien direkt im Download-Ordner: Größe und Alter. Für jeden Ordner direkt darunter: Größe des gesamten Inhalts über alle Ebenen und das Alter der jüngsten Datei darin, ermittelt über den ganzen Dateibaum.
- Das Alter einer Datei ist die Zeit seit dem späteren von Änderungs- und Statusänderungszeit, in vollen Tagen.
- Diese Zahlen dienen dem ersten Überblick. Maßgeblich für das Löschen ist die Regel unten, die auch Unterordner als Elemente zählt und das Alter erst beim Löschen berechnet. Das Alter eines Ordners kann deshalb in der Analyse vom Löschergebnis abweichen; ein Ordner ohne Datei erscheint in der Analyse gar nicht.
- Unvollständige Downloads (zum Beispiel `*.crdownload` bei Chrome, `*.part`) sind in der Analyse gekennzeichnet. Messbefund: Im Download-Ordner liegen mehrere `*.crdownload` mit 230 bis 671 MiB.

**Regel (Festlegung des Entwicklers vom 7. November 2026)**

Im Download-Ordner geht es um die Übersicht, nicht um die Größe. Ein früherer Entwurf legte die Einträge nach Altersgruppen und Größe sortiert vor und ließ den Nutzer Nummern wählen; im ersten Lauf des installierten Skills wurden so nur die sechs größten von 704 Einträgen gelöscht, der Rest blieb liegen. Deshalb gilt jetzt:

- Der Skill fragt nach der Altersgrenze x in Tagen, Vorgabe 14. Gelöscht wird alles direkt im Download-Ordner, dessen Alter größer als x Tage ist, **unabhängig von der Größe**.
- **Datei:** ihr eigenes Alter.
- **Ordner:** das Alter seines jüngsten Elements in beliebiger Tiefe. Elemente sind Dateien, Links und Unterordner, bei jedem zählt das spätere von Änderungs- und Statusänderungszeit. Ein einziges jüngeres Element, auch ganz unten in der Hierarchie, schützt den ganzen Ordner mit allem darin. Das Alter des Ordners selbst zählt nicht.
- **Leerer Ordner** (ohne Element): sein eigenes Datum zählt.
- **Unvollständige Downloads:** dieselbe Grenze, keine eigene Behandlung; junge bleiben, denn sie können ein laufender Download sein.
- **Links** direkt im Download-Ordner werden nur gemeldet (Grundsatz 8). Ein Link in einem Ordner, der gelöscht wird, geht mit dem Ordner, nie sein Ziel.
- **Zeitpunkt der Berechnung:** Das Löschskript berechnet das Alter beim Lauf aus dem Dateibaum (Auftrag `rule` mit `days`, `folders`, `exclude`) und übernimmt es nicht aus der Analyse. Was seit der Analyse verändert wurde, ist dadurch geschützt, und der Probelauf zeigt genau, was weg wäre.

**Auswahl durch den Nutzer**

- Der Nutzer nennt x und kann Ausnahmen nennen (Namen oder Muster). Die Instanz übersetzt sie anhand der Analyse in absolute Pfade direkt unter dem Download-Ordner (`exclude`, Grundsatz 6). Was erhalten bleibt, formuliert allein der Nutzer.

**Vor dem Löschen**

- Die Instanz führt zuerst den Probelauf aus und baut die Übersicht für den Nutzer aus dessen Bericht, nicht aus der Analyse: Zahl und Gesamtgröße, jeder Ordner einzeln, Dateien nach Typ gezählt, die größten wenigen, dazu was übersprungen wird und warum. Die vollständige Liste legt sie als Datei ab. Der Nutzer bestätigt, danach folgt der echte Lauf.
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
  1. Es zählt jeder Starter-Eintrag (`.desktop`) mit `Type=Application` aus `/usr/share/applications`, `/usr/local/share/applications`, `~/.local/share/applications`, den Flatpak-Exporten und den Snap-Einträgen. AppImages erscheinen dort, wenn sie integriert wurden. Die Flatpak-Exporte sind nach bisherigem Kenntnisstand (am System nicht geprüft) Links auf die Dateien der installierten App; ein Link wird nach Grundsatz 8 nur gelesen, wenn sein Ziel auf keinem fremden Einhängepunkt liegt. Sonst steht der Eintrag in der Liste der ausgeschlossenen mit dem Grund `link_not_followed`.
  2. Nicht, wenn `NoDisplay` oder `Hidden` gesetzt ist oder `OnlyShowIn` oder `NotShowIn` den aktuellen Desktop (`XDG_CURRENT_DESKTOP`) ausschließt.
  3. Nicht, wenn `Terminal=true` (Kommandozeilenprogramme).
  4. Es muss mindestens eine Hauptkategorie vorliegen, die nicht `Settings` und nicht `System` ist. Ein Eintrag, der nur `System` oder `Settings` trägt, fällt heraus.
  5. `Utility` gilt als Anwendersoftware.
- Messbefund (dieser Rechner): 74 Programme erfasst, 4 wegen `Terminal=true` ausgeschlossen, 24 als System oder Einstellungen. Einige Ausreißer (zum Beispiel Emoji Selector) und mehrfache Einträge derselben Software sind in Kauf genommen: Sie kosten nur Zeit und Token, die Bereinigung bleibt auf der sicheren Seite.
- Software, die im Skill bereits untersucht ist (Firefox, Chrome, VS Code; Abschnitte 4.2 bis 4.4), bleibt bei der Recherche außen vor, soweit sie auf einem der getesteten klassischen Pfade installiert ist. Findet die Analyse eines dieser Programme in einem anderen Installationsweg (Snap, Flatpak oder andere), wird es wie jede andere Anwendersoftware recherchiert, und seine Ordner stehen in Tabelle 2. Die Software steht in der Liste am Ende der Analyse, falls sie installiert ist. Der Skill kann später durch weitere Analysen um Software erweitert werden, deren Details bekannt sind.
- Ordner unter `~/.cache`, die zu keiner nach diesen Regeln erfassten Anwendersoftware gehören: Die Instanz ordnet sie ihrem Eigentümer zu (Erweiterung, Kommandozeilenwerkzeug, Bibliothek, Desktop-Bestandteil). Gelingt das, wird der Eigentümer recherchiert wie Anwendersoftware; ist die Behandlung belegt, steht der Ordner in Tabelle 2, mit denselben Regeln für Belegstufe und das Beenden des Programms. Desktop-Bestandteile wie die Vorschaubilder gehören zu ihrem Bereich in Abschnitt 5. Lässt sich ein Ordner nicht zuordnen, steht er in Tabelle 3 als "Cache ohne zugeordnetes Programm". Die XDG-Spezifikation allein genügt als Beleg nicht: Sie nennt `~/.cache` den Ort für "user-specific non-essential (cached) data", sagt aber nicht, dass der Inhalt gelöscht werden darf ([XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/)).

**Grundlage für die Bereinigung: pro Programm genau zwei Dinge**

1. Cache- und Download-Ordner, deren Inhalt gelöscht werden darf, **nur** wenn die Dokumentation im Internet zum Programm belegt, dass dort nur gecacht oder heruntergeladen wird. Als Cache gilt ein Ordner nur, wenn die Dokumentation belegt, dass das Programm die Daten darin jederzeit vollautomatisch wiederherstellt und dass ihr Fehlen den Arbeitsvorgang bis auf Zeitverlust nicht beeinflusst (Grundsatz 4). Wie die Dokumentation den Ordner nennt, zählt nicht. Geht aus der Dokumentation nicht hervor, dass das Programm den Verlust dieser Daten im laufenden Betrieb verträgt, wird erst gelöscht, wenn das Programm beendet ist; der Skill fordert den Nutzer dazu auf. Sie werden dem Nutzer offen mitgeteilt und im Nachgang zur gemeinsamen weiteren Klärung angeboten (3.5). Nachsehen im Dateisystem allein genügt dafür nicht. Das gilt nur für Software, deren Details nicht schon bei der Entwicklung des Skills geklärt wurden. Geklärt sind Firefox, Chrome, VS Code und der Download-Ordner des Nutzers am Desktop; dort gelten die Festlegungen aus 4.2, 4.3, 4.4 und 4.9.
2. Ordner, die bei Programmen, die Daten verarbeiten, typischerweise als Eingangsdaten dienen. Treffer in solchen Ordnern schließt die Instanz stillschweigend aus den Suchläufen aus, weil sie als Arbeitsdaten und nicht als unwichtige Daten gelten. Das geschieht ohne Meldung an den Nutzer. Für diese Zuordnung darf die Instanz auch im Dateisystem nachsehen.

**Kein klarer Befund**

- Kein klarer Befund liegt auch vor, wenn ein Ordner nur durch Drittquellen oder durch Rückschluss aus mehreren Hinweisen belegt ist; für Tabelle 2 zählen nur die Belegstufen hoch und mittel (Abschnitt 3.5).
- Ergibt die Recherche keinen klaren Befund, werden Daten, die ganz offensichtlich solchen Programmen zugeordnet sind, vollständig vom Löschvorschlag ausgeschlossen. Sie werden auch gegenüber dem Nutzer nicht aufgelistet oder genannt.
- Skill-eigene Analysen und Anzeigen (auch Tabelle 3 in 3.3) filtern diese Daten. Ausgenommen ist die Größe je Verzeichnis in Tabelle 3: Sie zählt nur und schlägt nichts zum Löschen vor; ein verschwiegener Ordner verfälschte die Übersicht.
- Ausnahme: Verlangt der Nutzer selbst, Ordnergrößen zu ermitteln und anzuzeigen, oder alle Dateien in einem Bereich des Dateisystems zu erfassen und deren Größe anzuzeigen, gilt der Filter nicht. Das ist eine zusätzlich angeforderte Aufgabe nach 3.7.
- Deshalb ist die Analyse am Anfang, einschließlich der Recherche, sehr umfassend durchzuführen. Der Nutzer erfährt das zu Beginn (3.1, Schritt 6).

**Geltung des stillen Ausschlusses (Punkt 2)**

Der Ausschluss gilt überall dort, wo der Skill einzelne Dateien zur Auswahl für das Löschen vorlegt und dabei nach eigenem Urteil sucht. Er gilt nicht, wo ein objektives Kriterium entscheidet, wo der Nutzer den Ort selbst bestimmt hat oder wo nur gezählt wird.

| Suchlauf | stiller Ausschluss |
|---|---|
| 4.7 .deb-Dateien | nein (objektiver Versionsvergleich) |
| 4.8 Image-Dateien und Archive | ja |
| 4.9 Download-Ordner | nein (Ort vom Nutzer bestimmt) |
| 4.10 Vagabundierende Medien | ja |
| Tabelle 3: große Einzeldateien | ja |
| Tabelle 3: doppelte Dateien | ja |
| Tabelle 3: Größe je Verzeichnis | nein (nur gezählt; ein verschwiegener Ordner verfälschte die Übersicht) |

Fehlt dem Nutzer in einer Liste etwas, kann er eine zusätzliche Suche nach 3.7 anfordern; dort gilt der Ausschluss nicht.

### 4.12 Python-Bytecode-Cache

| Was | Behandlung |
|---|---|
| Ordner `__pycache__` im Home | ganz löschen einschließlich Ordner, ohne Rückfrage |

- Python legt die Dateien bei Bedarf selbst neu an; es ist ein Cache im Sinne von Grundsatz 4.
- Nur im Home. Unter `/usr` und anderen Systemverzeichnissen legt die Paketverwaltung sie an; ein normaler Nutzer kann sie dort nicht neu schreiben.
- Ohne eigenen Test in Tabelle 1 aufgenommen: Das Verhalten ist durch die Python-Spezifikation festgelegt, und das Löschen kann nichts entfernen, was Python nicht selbst neu erzeugt. Belegt in [PEP 3147](https://peps.python.org/pep-3147/): Der Ordner wird beim Import angelegt, und scheitert das Schreiben, "the import will still succeed"; eine `.pyc` aus `__pycache__` wird nur benutzt, wenn die Quelldatei existiert ("Python will not import a pyc file from the cache directory unless the source file exists"). Programme ohne Quelltext legen ihre `.pyc` dorthin, wo die Quelldatei stünde, nicht in `__pycache__`.
- Folge des Löschens: Der erste Start eines Programms dauert etwas länger.

### 4.13 Docker

Gilt für Docker mit Root-Dienst. Podman und Docker im Rootless-Modus werden nur gemeldet. Sammelbefehle wie `docker system prune` und `docker image prune -a` sind ausgeschlossen (Grundsatz 3); `image prune -a` würde auch die Erhalten-Liste übergehen. Mit dem containerd-Snapshotter liegen die Daten unter `/var/lib/containerd`, nicht nur unter `/var/lib/docker`.

**Ablauf**

1. **Build-Cache:** Alles, was nicht jünger als 2 Tage ist, wird gelöscht; der Nutzer kann die Grenze ändern. Mittel: `docker builder prune --all` mit Filter `until` (ohne `--all` entfernt der Befehl nur "dangling" Cache; [Doku](https://docs.docker.com/reference/cli/docker/builder/prune/)). Wie `until` abgrenzt, sagt die Doku nicht; der Test zeigte: nach der letzten Benutzung, nicht nach der Erstellung. Der Cache besteht aus Ketten von Bauschritten (`docker buildx du --verbose` nennt je Eintrag seine Vorgänger), und ein frisch benutzter Endpunkt hält seine ganze Kette fest, auch deren alte Glieder (im Test zwei Ketten mit je über 800 MB, deren Endpunkt der Testbau als benutzt markiert hatte). Die Regel wirkt also je Kette: Gelöscht wird Cache, dessen ganze Kette seit der Grenze nicht benutzt wurde. Diese Erklärung ist aus den Beobachtungen abgeleitet, nicht in der Doku belegt.
2. **Beendete Container:** durchnummeriert vorgelegt (Name, Image, beendet seit, Größe). Der Nutzer wählt, welche nicht mehr gebraucht werden. Gelöscht wird mit `docker rm -v`, also samt ihren anonymen Volumes; benannte Volumes bleiben ("if a volume was specified with a name, it will not be removed", [Doku](https://docs.docker.com/reference/cli/docker/container/rm/)). Laufende Container und ihre Images bleiben und werden nicht aufgeführt.
3. **Compose-Projekte:** Die Analyse sucht im Home die Compose-Dateien (`compose.yaml`, `compose.yml`, `docker-compose.yaml`, `docker-compose.yml`). Für jede bestimmt Compose selbst die Images (`docker compose -f <Datei> config --images`, "Print the image names, one per line", löst Variablen auf; [Doku](https://docs.docker.com/reference/cli/docker/compose/config/)); kein eigenes Parsen. Durchnummeriert vorgelegt: Pfad und Änderungsdatum der Datei, Projektname (aus `docker compose config`), Images, Zustand (läuft / beendet / heruntergefahren). Den Zustand liefert `docker compose ls -a`; ein Projekt, dessen Datei gefunden wurde, das dort aber fehlt, ist heruntergefahren (im Test bestätigt). Für Dienste mit `build:` und ohne `image:` gibt `--images` den Namen des gebauten Images aus (im Test `compose-probe-app`); beim Abgleich ergänzt der Skill `:latest`, wenn kein Tag angegeben ist. Der Nutzer nennt die Projekte, die er nicht mehr braucht; deren Images kommen von der Erhalten-Liste herunter. Die Compose-Dateien selbst fasst der Skill nicht an. Scheitert der Befehl für eine Datei (etwa weil eine `.env` fehlt), bleiben alle Images ohne Container erhalten, und der Skill meldet die Datei. Ein unklarer Fall führt nicht zum Löschen.
4. **Zweite Image-Prüfung:** Alle Images, die jetzt keinem Container mehr zuzuordnen sind, werden einzeln mit `docker rmi` gelöscht, außer denen auf der Erhalten-Liste. Lokal gebaute Images ohne Container und ohne Eintrag in der Erhalten-Liste gehören dazu.
5. **Benannte Volumes** werden nur gemeldet, nie gelöscht (zum Beispiel `vscode`, der Zwischenspeicher der Dev-Container von VS Code).

**Ergebnisbericht:** Für Docker nennt er, was gelöscht wurde, aber keine Größe; ausdrückliche Ausnahme von Grundsatz 5 (Images teilen sich Schichten, eine Größe wird nicht berechnet).

**Tabelle:** Tabelle 1 (Test vom 5./6. November 2026, Protokolle in `tests/test_results/`). Zwei Lücken: Dass `docker rm -v` anonyme Volumes mitlöscht, ist nur durch die Doku belegt (der Testcontainer hatte keine). Dass ganze ruhende Ketten des Build-Caches nach Ablauf der Grenze verschwinden, prüft die Nachprobe (`work-plan.md`, Schritt 14).

**Messbefund (Entwicklungsrechner):** zusammen rund 4,2 GiB (`/var/lib/containerd` 2,7 GiB, `/var/lib/docker` 1,5 GiB), davon Build-Cache 1,96 GB, Volume `vscode` 1,51 GB, ein beendeter Container mit 336 MB.

### 4.14 Papierkorb

Dieser Schritt kommt im Ablauf als letzter aller Bereiche: Was ein früherer Schritt (heute oder künftig) nur in den Papierkorb verschiebt statt zu löschen, wird so mit erfasst.

- Ort nach der [Trash Specification](https://specifications.freedesktop.org/trash/latest/) von freedesktop.org: `$XDG_DATA_HOME/Trash`, meist `~/.local/share/Trash`, mit den Unterordnern `files` (die Dateien) und `info` (je eine `.trashinfo`). Auf anderen eingehängten Dateisystemen gibt es eigene Papierkörbe (`$topdir/.Trash/$uid` oder `$topdir/.Trash-$uid`); sie werden **nicht** erfasst und nicht gelöscht, denn schon ein Blick hinein ist ein Zugriff auf den Einhängepunkt (Grundsatz 8). Der Skill weist darauf hin, dass der Nutzer sie an ihrem Ort selbst leert.
- Analyse (3.3): nur Größe und Zahl der Einträge des Papierkorbs im Home, ohne Inhalt.
- Der Skill fragt nach x Tagen; Vorgabe 14, 0 heißt "alles". Gelöscht werden die Einträge, die länger als x Tage im Papierkorb liegen. Maßgeblich ist der Schlüssel `DeletionDate` der `.trashinfo` ("when the file/directory was trashed", Format `YYYY-MM-DDThh:mm:ss`), nicht die Änderungszeit der Datei. Gelöscht werden jeweils Datei und `.trashinfo` zusammen; die Spezifikation schreibt den Löschvorgang nicht vor, das ist abgeleitet.
- Einträge ohne gültige `.trashinfo` werden nicht gelöscht, nur gemeldet: Ihr Alter ist unbekannt.
- Hinweis an den Nutzer: Was hier gelöscht wird, ist endgültig weg; ein Backup hilft nur, wenn der Papierkorb gesichert wird. Messbefund (Entwicklungsrechner): Dort ist der Papierkorb vom Backup ausgeschlossen.
- Tabelle 1: Der Vorgang ist durch die Spezifikation beschrieben, der Nutzer entscheidet über x.

## 5 Bereiche, für die noch keine Behandlung festgelegt ist

- Suchindex Baloo (`balooctl purge`)
- Git-Repositories (`git gc`, LFS, abgebrochene Abrufe)
- Vorschaubilder
- Zwischenspeicher von Claude Desktop, Sandbox-Image von Claude Desktop
- Flatpak, Snap, AppImage, Wine
- Python-Umgebungen, Toolchains im Home, Syncthing-Versionen
- Doppelte Dateien, Migrationsreste

Festgelegt zur Aufrufart: Der Skill läuft nur auf ausdrücklichen Wunsch des Nutzers. In Claude Code verankert das Frontmatter-Feld `disable-model-invocation: true` das fest: Claude lädt ihn nicht von selbst, die Beschreibung steht nicht im Kontext ([Skills](https://code.claude.com/docs/en/skills)). Ein stiller Trigger entfällt.

Festgelegt zum Aufbau: Name `cleaning-up-linux-desktop`; eine einzige `SKILL.md` ohne nachgeladene Regeldateien. Die Bedingung für eine Teilung (`skill-dev-doc.md`, Kapitel 5.2: die Abwahl ist ein realistischer Ausgang) fällt mit dem ausdrücklichen Aufruf weg, und nur der Körper der `SKILL.md` wird nach einer Verdichtung des Kontexts wieder eingespielt — bei einem langen Lauf ein Grund für eine Datei. Zielwelt: web und code, ein Skilltext mit einem Abschnitt für die Übergabe der Skripte (in Claude Code über `${CLAUDE_SKILL_DIR}`, auf claude.ai als Download, nie als Artefakt).

Die anstehenden Schritte stehen in `work-plan.md`.
