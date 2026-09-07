# vscode-dev-container

*Stand: 2026-09-07*

> English version: [README.en.md](README.en.md)

**Ein Entwicklungscontainer für VS Code, der die Grenze zwischen Agent und Rechner von vornherein richtig zieht** — schmale Einhängungen statt ganzem Home, SSH-Agent statt Schlüsseldatei, Netzsperre auf dem Host. Er bringt einen C-Compiler, Python und Poetry mit und ist als Grundlage gedacht, auf der weiteres aufsetzt.

Dieses Vorhaben liefert die **Rezeptur**, nicht ein fertiges Image: ein Dockerfile, eine `devcontainer.json` und die Randbedingungen, die dazugehören. Gebaut wird lokal, auf dem Rechner, der den Container öffnet.

Die Begründungen stehen nicht hier, sondern in [`../safety-related/vscode-topologies.de.md`](../safety-related/vscode-topologies.de.md) — dort ist auch nachzulesen, welche Konstellation aus Editor, SSH und Container welche Grenze zieht und welche nicht.

## Was drin ist

- **Ubuntu 24.04** mit `build-essential` (C-Compiler) und Git
- **Das System-Python der Distribution (3.12)** als unveränderlicher Sockel für Werkzeuge und Skills
- **Poetry** und **uv**, jeweils in eigener Umgebung über `pipx` — keines von beiden sitzt in einer Projektumgebung
- **`openssh-client`**, damit der weitergeleitete Agent überhaupt einen Client hat — ohne ihn hat Git über SSH kein Transportmittel
- **`bubblewrap` und `socat`**, ohne die Claude Codes eingebaute Sandbox nicht startet
- **Keine Claude-Code-CLI.** Die VS-Code-Erweiterung bringt ihre eigene Kopie mit; ein zusätzlicher Einbau kostete mehrere hundert Megabyte ohne Gegenwert
- Ein Prompt, der Git-Zweig und aktive Python-Umgebung zeigt

Interpreter für einzelne Projekte sind **nicht** eingebacken. Sie werden bei Bedarf geholt — von Poetry anhand der `pyproject.toml` oder von `uv` über `use-python`.

## Voraussetzungen auf dem Rechner, der den Container öffnet

- Docker und die VS-Code-Erweiterung **Dev Containers**
- Ein laufender **SSH-Agent** mit geladenem Schlüssel (`ssh-add -l` zeigt ihn). Ohne gesetztes `SSH_AUTH_SOCK` schlägt die Einhängung des Sockets fehl
- Eine vorhandene `~/.gitconfig` und ein vorhandenes `~/.claude` — beide werden eingehängt, nicht angelegt
- Gesetztes `USER` und `HOME`. Beides ist in einer üblichen Anmeldesitzung vorhanden; fehlt es, greifen die Vorgabewerte des Dockerfiles (`dev`, `/home/dev`), und dann stimmt der Pfad für den Abgleich nicht mehr

Bei Arbeit über **Remote-SSH** ist damit der *entfernte* Rechner gemeint, nicht der Laptop: Dort läuft das Dev-Container-Werkzeug, dort liegen Projekt und `~/.claude`. Der Agent muss folglich per `ForwardAgent` bis dorthin reichen.

## Übernahme in ein Projekt

Die beiden Ordner `.devcontainer/` und `.claude/` in die Wurzel des Projekts kopieren, dann in VS Code **Dev Containers: Reopen in Container**. Beim ersten Mal wird das Image gebaut; das dauert einige Minuten, danach ist es zwischengespeichert.

Die Ordner tragen hier schon die Namen, die sie im Zielprojekt haben — es gibt also nichts umzubenennen und nichts einzeln einzusortieren. `.claude/settings.json` ist der Grund, warum der zweite Ordner dazugehört: Sie schaltet die eingebaute Sandbox für dieses Projekt so, dass sie im Container überhaupt startet (siehe „Welche Claude-Einstellungen im Container tragen").

Wer etwas hinzufügen will — JupyterLab, ein Hersteller-SDK, weitere Bibliotheken —, hängt es an das Dockerfile an oder leitet mit `FROM` davon ab. **Nicht** über den `features`-Block der `devcontainer.json`: Der wird vom Werkzeug erst nachträglich über das Image gelegt und geht beim Ableiten verloren.

## Die Einhängungen

| Was | Ziel im Container | Modus |
| --- | --- | --- |
| Projektordner | `~/git/<Ordnername>` | rw |
| `~/.claude` | derselbe Pfad wie außen | rw |
| `~/.gitconfig` | derselbe Pfad wie außen | **ro** |
| SSH-Agent-Socket | `/ssh-agent` | rw |

Alles andere aus dem Home bleibt draußen — `~/.ssh`, `~/.aws`, `~/.gnupg`, andere Projekte. Das ist der Kern: Was nicht eingehängt ist, existiert für den Container nicht, und keine Regel muss dafür greifen.

`docker.sock` wird **niemals** eingehängt. Das entspräche Root auf dem Wirtsrechner.

### Der Agent-Socket: zwei Eigenheiten aus dem Feldtest

**Der Pfad wird nur beim *Erstellen* des Containers aufgelöst, nicht bei jedem Start.** `${localEnv:SSH_AUTH_SOCK}` friert in die Container-Konfiguration ein. Läuft später ein anderer `ssh-agent` (neue Anmeldung, neues Terminal, Neustart), zeigt die Einhängung auf einen Socket, den es nicht mehr gibt — und Docker verweigert dann den **Neustart des bestehenden** Containers:

```text
Error response from daemon: invalid mount config for type "bind":
bind source path does not exist: /tmp/ssh-XXXXXXXX/agent.NNNN
```

Das ist kein Defekt dieses Bausteins, sondern eine Eigenschaft der Variablenauflösung. Abhilfe: den Container **neu erstellen** statt neu zu starten (Container entfernen, dann „Reopen in Container" — ein bloßes „Reload Window" genügt nicht, weil es die eingefrorene Konfiguration weiterbenutzt).

**Und bei VS Code Desktop gewinnt ohnehin VS Codes eigene Weiterleitung.** Gemessen im Container: `$SSH_AUTH_SOCK` zeigte auf `/tmp/vscode-ssh-auth-….sock`, nicht auf unseren `/ssh-agent`-Mount — VS Code leitet den Agenten selbst weiter und überschreibt unseren `containerEnv`-Wert. Praktisch schadet das nicht (`ssh-add -l` listete die Schlüssel korrekt), aber es heißt: **Unser Mount ist bei VS Code Desktop wirkungslos.** Er bleibt trotzdem richtig, denn er ist der einzige Weg, der auch **ohne** VS Code Desktop trägt — Browser-Client, `devcontainer`-CLI, reines `docker run`.

### Warum der Pfad so gewählt ist

Claude Code legt Sitzungsprotokolle unter `~/.claude/projects/<projektpfad-mit-bindestrichen>/` ab — der Schlüssel entsteht also aus dem **absoluten Pfad des Projekts**. Läge das Projekt im Container unter `/workspace`, bekäme dieselbe Arbeit innen und außen verschiedene Schlüssel, und der Abgleich zwischen Rechnern liefe ins Leere.

Deshalb wird das Projekt auf `~/git/<Ordnername>` normalisiert, unabhängig davon, wo es auf dem Host liegt. Solange die Projekte auf den beteiligten Rechnern ebenfalls unter `~/git/` liegen, ist der Schlüssel innen wie außen und auf jedem Rechner derselbe.

**Die Ausnahme, die man kennen muss:** Liegt ein Projekt auf dem Host *nicht* unter `~/git/`, weicht der Container-Pfad vom nativen ab — dann hat dieses eine Projekt zwei getrennte Verläufe, je nachdem ob mit oder ohne Container gearbeitet wurde.

### Zusammenspiel mit `home-.claude-sharing`

Der Abgleich von `~/.claude` läuft über Syncthing **auf dem Host-Betriebssystem**, nicht im Container. Der Container sieht durch die Einhängung ohnehin den aktuellen Stand.

**Im Container darf kein zweiter Wächter laufen.** Er würde dieselben Dateien beobachten wie der auf dem Host und Konflikte melden, die keine sind.

Und eine Folge, die man bewusst annehmen sollte: Der Container schreibt in ein synchronisiertes Verzeichnis. Sitzungsprotokolle aus dem Container landen damit auf allen beteiligten Rechnern.

**Die zweite Folge ist die unangenehmere, und sie fällt im Feldtest sofort auf:** Eingehängt wird `~/.claude` **ganz**, nicht ein projektbezogener Ausschnitt. Damit liegt im Container die Sitzungshistorie **aller** Projekte und aller Rechner offen — `ls ~/.claude/projects/` zeigte im Test über dreißig Einträge, von fremden Repositories bis zu Scratchpad-Verzeichnissen. Wer die Grenze dieses Containers gegen ein einzelnes Projekt zieht, sollte wissen, dass sie für die Chat-Historie nicht gilt: Ein kompromittierter Prozess im Container könnte dort auch in den Verläufen fremder Projekte lesen, samt allem, was darin einmal besprochen wurde.

Ein projektbezogener Ausschnitt wäre technisch möglich (nur `~/.claude/projects/<schlüssel>/` einhängen statt `~/.claude`), nimmt aber Credentials, Skills und Einstellungen mit weg — also genau das, wofür die Einhängung da ist. Aufgelöst ist dieser Zielkonflikt hier **nicht**; er ist bewusst zugunsten der Brauchbarkeit entschieden und steht als solcher unter „Offen".

## Python im Container

**Der Sockel bleibt unangetastet.** Das System-Python 3.12 ist das, was Skill-Skripte und der Kompaktierungs-Hook aufrufen. Keine Auswahl verändert es.

**Poetry-Projekte** brauchen nichts weiter: Poetry liest die `pyproject.toml`, holt bei Bedarf den passenden Interpreter (`poetry python install`, seit Poetry 2.1, vom Hersteller als experimentell geführt) und aktiviert seine eigene Umgebung.

**Ohne Poetry** dient `use-python`:

```bash
use-python           # zeigt die aktuelle Wahl und die vorbereiteten Umgebungen
use-python 3.11      # holt den Interpreter bei Bedarf, legt die Umgebung an,
                     # merkt sie und aktiviert sie sofort
use-python system    # nimmt die Wahl zurück
```

Die Wahl liegt in `~/.config/devcontainer/python-version`, die Umgebungen unter `~/.venvs/`. Beides liegt in der Container-Schicht: Es übersteht jeden **Neustart** und ist nach einem **Neubau** weg. Neue Shells aktivieren die gemerkte Wahl von selbst; wechselst Du danach in ein Poetry-Projekt, gewinnt Poetry. Der Prompt zeigt immer die tatsächlich aktive Umgebung.

Die automatische Aktivierung greift nur in **interaktiven** Shells, weil sie am Ende der `.bashrc` hängt. Ein nicht-interaktiv gestarteter Task sieht das System-Python.

## Netzgrenze

**Sie gehört auf den Host, nicht in den Container.** Der Container hat passwortloses `sudo`; eine Paketfilterregel in ihm könnte von innen wieder geändert werden. Docker sieht für Nutzerregeln die Kette `DOCKER-USER` vor, die Neustarts des Dienstes übersteht und die übrige Firewall nicht anfasst. Auf dem Rechner, der den Container betreibt:

```bash
iptables -I DOCKER-USER -d 10.0.0.0/8     -j DROP
iptables -I DOCKER-USER -d 172.16.0.0/12  -j DROP
iptables -I DOCKER-USER -d 192.168.0.0/16 -j DROP
iptables -I DOCKER-USER -j RETURN
```

Wirkung: Verkehr in private Adressbereiche wird verworfen, das Internet bleibt offen — Repositories, Paketquellen, Dokumentation sind erreichbar.

**Das ist keine Vorlage zum Übernehmen.** Hängen an einem Rechner Geräte, die zur Aufgabe gehören — Kameras, Messtechnik, ein interner Spiegel —, gehört für jedes eine `ACCEPT`-Zeile **vor** die `DROP`-Zeilen. Die Regel bleibt damit eine Sperrliste mit benannten Ausnahmen, nicht eine Freigabeliste. Diese Ausnahmen sind je Rechner einzeln zu klären.

**Zwei Grenzen dieser Regel:**

Bei `--network host` greift `DOCKER-USER` **nicht** — diese Kette hängt im Weiterleitungspfad für Bridge-Netze, und ein Container im Netz-Namensraum des Hosts läuft daran vorbei. Wer Geräteerkennung über Broadcast braucht und deshalb `--network host` setzt, braucht eine andere Sperre. *Das ist aus der Docker-Netzarchitektur abgeleitet und nicht nachgemessen.*

Und sie schützt nicht gegen das, was der Container über einen **erlaubten** Host erreicht: Eine freigegebene Adresse ist auf allen Ports frei.

## Welche Claude-Einstellungen im Container tragen

Von den beiden Ebenen in [`../safety-related/sandbox-settings.de.md`](../safety-related/sandbox-settings.de.md) trägt im Container nur eine.

**Die Berechtigungsebene (`permissions.*`) wirkt unverändert.** Sie hängt nicht an bubblewrap. Read-Sperren, die Bypass-Sperre und die Ebenenfrage am Sandbox-Ausstieg gehören auch hier gesetzt.

**Die Sandbox-Ebene (`sandbox.*`) läuft im Container geschwächt — aber sie ist nicht redundant.** Diese Unterscheidung ist wichtig genug, um sie auszuschreiben, weil eine frühere Fassung dieser README das Gegenteil behauptete.

Geschwächt ist genau **ein** Punkt. Die Doku benennt ihn: Mit `enableWeakerNestedSandbox` bindet die innere Sandbox das vorhandene `/proc` des Containers ein, statt ein frisches einzuhängen — „it exposes process information to sandboxed commands that a fresh `/proc` mount would hide". Ein sandboxed Kommando sieht also die übrigen Prozesse des Containers. Das ist eine reale Einbuße, und sie ist die einzige dort genannte.

**Nicht** betroffen sind die Dateisperren, die Netz-Allowlist und die geschützten Pfade — die hängen an Bind-Mounts, Proxy und festen Deny-Regeln, nicht an einem frischen `/proc`. Und genau damit leistet die innere Sandbox etwas, das die Container-Grenze nicht leistet: **Der Container entscheidet, was überhaupt erreichbar ist; die innere Sandbox entscheidet, was ein einzelnes Bash-Kommando davon anfassen darf.** Sie verhindert im schon erreichbaren Bereich, dass eine `.claude/settings.json` oder ein Git-Hook geschrieben wird, und kann das Netz pro Kommando enger fassen als die `DOCKER-USER`-Regel. Das ist kein Duplikat der Container-Grenze, sondern eine zweite, feinere Ebene darin.

Deshalb liefert dieser Baustein die Sandbox **eingeschaltet** aus — `.claude/settings.json` setzt `enabled` und `enableWeakerNestedSandbox` — und das Image bringt `bubblewrap` und `socat` mit, ohne die sie gar nicht startet. Wer die Prozesssichtbarkeit höher gewichtet als den Zugewinn, kann sie mit `"enabled": false` in derselben Datei abschalten; das ist eine bewusste Entscheidung, kein Standard.

Da `~/.claude` eingehängt ist, gilt die Konfiguration des Hosts unverändert auch drinnen — samt Skills und Hooks. Deshalb muss das System-Python erreichbar bleiben, unabhängig von der Environment-Wahl.

## Prüfliste

Nach dem ersten Start einmal durchgehen. Keine Zusage gilt, bevor sie abgetastet ist. Die Spalte „geprüft" hält fest, was am 5./7. September 2026 im Feldtest auf zwei Rechnern tatsächlich beobachtet wurde.

| Prüfung | Erwartet | geprüft |
| --- | --- | --- |
| `whoami` | Dein Benutzername (bei lokalem Bau) | ✅ `herbrand` |
| `pwd` | `~/git/<Ordnername>`, identisch zum Host-Pfad | ✅ |
| `echo "$HOME"` | Host-Home-Pfad, nicht `/home/dev` | ✅ |
| `ls ~/.claude/projects/` | enthält den Schlüssel des Projekts | ⚠️ enthält **alle** Projekte, siehe „Zusammenspiel mit `home-.claude-sharing`" |
| `ls ~/.ssh` | existiert nicht | ✅ |
| `ssh-add -l` | listet den Schlüssel — der Agent trägt | ✅ (nach Nachrüsten von `openssh-client`) |
| `use-python` | meldet sich, auch ohne gewählte Version | ✅ `selected: system` |
| Claude-Erweiterung öffnen | Panel startet, Sitzung möglich | ✅ v2.1.263 |
| `git -C <projekt> fetch` | funktioniert ohne Passphrase | offen |
| `curl -s -o /dev/null -w '%{http_code}' https://github.com` | `200` | offen |
| Verbindungsversuch auf eine interne Adresse | scheitert, sobald die `DOCKER-USER`-Regel steht | offen — Regel noch nicht gesetzt |

## Offen

- **Die `DOCKER-USER`-Regel je Rechner festlegen** — mit den Ausnahmen für die dort angeschlossenen Geräte (Kameras, Messtechnik). Ohne sie ist das Firmennetz aus dem Container erreichbar. Das ist der Punkt, an dem der Baustein sein drittes Schutzziel einlöst oder nicht.
- **Der Zielkonflikt bei `~/.claude` ist unaufgelöst.** Die ganze Chat-Historie aller Projekte liegt im Container; ein projektbezogener Ausschnitt nähme Credentials, Skills und Einstellungen mit weg. Bewusst zugunsten der Brauchbarkeit entschieden, nicht gelöst.
- **Der Fall `--network host` ist ungeprüft** (siehe „Netzgrenze").
- **Der Rückkanal des Editors bleibt offen.** Läuft VS Code Desktop als Bedienoberfläche, kann Code aus dem Container über die Fernsteuerungsschnittstelle Kommandos auf dem Rechner auslösen, an dem Du sitzt. Keine Einstellung dieses Containers schließt das; wo es zählt, hilft nur ein Browser-Client. Einzelheiten im Topologie-Bericht.
- **Ein fertig gebautes Image ohne Bauschritt** trägt die Vorgabewerte `dev` und `/home/dev`. Der Abgleich verlangt dann eine Anpassung des Home-Pfads zur Laufzeit, die hier nicht gebaut ist.

### Was der Feldtest erledigt hat

Der erste Bau ist gelaufen, auf zwei Rechnern. Er ist damit **nicht** mehr offen — was dabei auffiel, steckt jetzt in dieser README und im Dockerfile. Drei Punkte, die keine Eigenschaften dieses Bausteins waren, aber Stunden gekostet haben und deshalb hier als Warnzeichen stehen:

- **Abgebrochene Container-Starts hinterlassen laufende Prozesse.** „Abbrechen" in der VS-Code-Oberfläche beendet den `devContainersSpecCLI.js`-Prozess nicht; er läuft weiter und blockiert den nächsten Versuch, ohne Fehlermeldung und ohne Netzverkehr. Zu finden mit `ps aux | grep <projektname>`, zu beenden mit `kill`.
- **`docker buildx` kann fehlen, obwohl das Paket installiert ist.** Auf dem zweiten Rechner gehörte `~/.docker` dem Benutzer `nobody` (UID 65534) mit Rechten `0710` — Docker konnte seine eigene Konfiguration nicht lesen und meldete `unknown command: docker buildx`. Behoben mit `chown`. Woher die falsche Eigentümerschaft kam, ist ungeklärt.
- **Der VS-Code-Server wird bei jedem neuen Container frisch von Microsoft geladen** (rund 230 MB, `update.code.visualstudio.com`). Das steckt nicht im Image und ist bei langsamer Leitung der längste Einzelposten des Starts.
