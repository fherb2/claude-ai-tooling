# Zugriffswege zu Claude Code in VS Code: welche Grenze wo wirkt

*Stand: 2026-09-02 · Fünf Konstellationen aus lokalem Editor, SSH-Fernzugriff und Container, jede gegen zwei unabhängige Sicherheitsgrenzen bewertet. Angaben gegen die Claude-Code-Doku, das Bedrohungsmodell von Trail of Bits und eigene Messungen am laufenden System geprüft; Quellen am Ende.*

## Wozu dieser Bericht und was er nicht ist

Wer mit Claude Code in VS Code programmiert, hat mehrere Möglichkeiten, wie Editor, Agent und Projekt auf Rechner verteilt sind: alles lokal, per SSH auf einem anderen Rechner, in einem Container, oder in einer Kette aus beidem. Diese Anordnung — die **Topologie** — entscheidet mit, welche Sicherheitsgrenzen überhaupt existieren. Sie entscheidet mehr als jede Einstellung, und sie wird selten bewusst gewählt: Meist ergibt sie sich daraus, wo das Projekt lauffähig ist.

Dieser Bericht beantwortet eine Frage: **Welche Grenze wirkt in welcher Konstellation, und welche fehlt dort?** Er beantwortet ausdrücklich **nicht**, wie die Einstellungen von Claude Code zu setzen sind — das steht in `sandbox-settings.de.md` im selben Ordner, mit Parameterbeschreibung und vier belegten Bugs der Sandbox. Wer nach Konfigurationsblöcken sucht, ist dort richtig. Wer die Begründung für das ganze Vorhaben sucht, findet sie in `.research/Claude-Code-Sicherheit im Auto-Modus/bericht.md`.

**Die drei Schutzziele**, an denen hier gemessen wird, stammen aus der Praxis des Entwicklers und sind absichtlich schmal — es geht nicht um die sicherste denkbare Umgebung, sondern um Programmieren und Debuggen mit Claude bei vertretbarem Aufwand:

1. **Kein Schreibzugriff** auf beliebige Bereiche des Rechners, sondern nur auf das, was zur Arbeit gehört.
2. **Schlüssel nicht unmittelbar lesbar** — Zugriff auf Remote-Repositories muss weiter funktionieren.
3. **Kein selbsttätiges Vordringen ins Netz**, insbesondere kein Abtasten anderer Rechner im Firmennetz auf Schwachstellen. Internetzugriff auf Repositories, Registries und Dokumentation bleibt uneingeschränkt gewünscht.

## 1 Die zwei Grenzen, die man auseinanderhalten muss

Der häufigste Fehlschluss bei diesem Thema entsteht, weil zwei völlig verschiedene Grenzen denselben Namen tragen: „der Container schützt". Er schützt in einer Richtung und nicht in der anderen, und wer das vermischt, kommt zu widersprüchlichen Urteilen.

**Grenze A — der Wirkraum nach innen.** Sie bestimmt, was ein Prozess, der in der Umgebung läuft, erreichen kann: welche Dateien er liest und schreibt, welche Rechner er über das Netz erreicht. Adressat ist alles, was in der Umgebung ausgeführt wird — Bash-Kommandos, deren Kindprozesse, Hooks, MCP-Server. Diese Grenze zieht ein Container über seine Mounts und seine Netzkonfiguration; ohne Container zieht sie Claude Codes eingebaute Sandbox, in engeren Grenzen.

**Grenze B — der Rückkanal zum Editor.** Sie bestimmt, ob Code aus der Umgebung auf den Rechner zurückwirken kann, auf dem die **Bedienoberfläche** von VS Code läuft. Dieser Kanal hat mit Dateien und Netz nichts zu tun: Er läuft über VS Codes eigene Fernsteuerungsschnittstelle. Weder Mounts noch Firewall noch irgendeine Claude-Einstellung sehen ihn.

Die beiden sind unabhängig. Eine Konstellation kann Grenze A vorbildlich ziehen und Grenze B völlig offen lassen — und genau das ist bei der verbreitetsten Container-Nutzung der Fall. Deshalb ist „mit Container ist es sicherer" ohne Zusatz keine brauchbare Aussage.

## 2 Wo Claude bei einer VS-Code-Fernverbindung überhaupt läuft

Für das Verständnis der Tabellen weiter unten muss man wissen, wie VS Code seine Fernzugriffe baut. Das Programm zerfällt dabei in zwei Teile:

- Die **Bedienoberfläche** — das eigentliche VS-Code-Programm mit Fenster, Menüs und Tastatur. Sie läuft immer auf dem Rechner, an dem der Mensch sitzt.
- Der **Extension-Host** — der Teil, der Erweiterungen ausführt, Dateien liest, Terminals öffnet und Sprachwerkzeuge betreibt. Er läuft dort, wo das Projekt liegt: auf dem Remote-Rechner, im Container, oder lokal.

Beide sprechen über eine Fernsteuerungsverbindung miteinander. Microsoft nennt die Server-Komponente „VS Code Server"; sie ist nicht zu verwechseln mit dem gleichnamig klingenden Fremdprojekt `code-server`, das ein vollständiges VS Code im Browser darstellt (Konstellation 4.5).

**Folge für Claude Code:** Die Claude-Erweiterung und `claude` im eingebauten Terminal laufen im Extension-Host — also dort, wo der Code liegt, nicht dort, wo der Mensch sitzt. Das ist gewollt und richtig: Der Agent sieht dieselben Dateien und Werkzeuge wie der Compiler.

**Folge für Grenze B:** Ein Kommando wie „öffne ein lokales Terminal" wird von der **Bedienoberfläche** ausgeführt, also auf dem Rechner des Menschen. Kann der Extension-Host solche Kommandos auslösen, dann kann Code aus der ferneren Umgebung Befehle auf dem näheren Rechner ausführen. Genau das beschreibt Trail of Bits für den Container-Fall: Der Extension-Host im Container ruft `terminal.newLocal` und schickt anschließend per `sendSequence` Zeichen hinein. Microsoft behandelt das als beabsichtigtes Verhalten, nicht als Fehler — es gibt daher keinen Schalter, der es abstellt.

Entscheidend ist deshalb nicht, wie viele SSH-Sprünge oder Container dazwischenliegen, sondern **welches Programm die Bedienoberfläche ist**: ein lokal installiertes VS Code Desktop (Kanal vorhanden, Ziel ist dieser lokale Rechner) oder ein Browser-Tab (Kanal nicht vorhanden, weil eine Webseite kein lokales Terminal öffnen kann).

## 3 Die fünf Konstellationen

### 3.1 Klassisch lokal — VS Code und Claude auf einem Rechner

Alles auf demselben Gerät, keine Fernverbindung, kein Container.

- **Wo Claude läuft:** lokal, mit den Rechten des angemeldeten Nutzers.
- **Grenze A, Dateisystem:** allein Claude Codes Sandbox und die Berechtigungsregeln. Die **Schreibseite wirkt** — erlaubt sind nur Arbeitsverzeichnis, Session-Temp und ausdrücklich hinzugefügte Verzeichnisse, alles andere ist gesperrt, ohne Aufzählung. Die **Leseseite ist schwach**: Der Default erlaubt Lesen auf dem ganzen Rechner, und die Gegenmaßnahme `sandbox.filesystem.denyRead` gilt als nicht zuverlässig durchgesetzt (#61208). Was hier trägt, sind `permissions.deny`-Read-Regeln — aber die verlangen eine vollständige Aufzählung aller Geheimnisorte, und die Pflege dieser Liste bleibt dauerhaft beim Menschen.
- **Grenze A, Netz:** stark gegen Abtasten, schwach gegen gezielten Zugriff. Sandboxed Bash läuft in einem eigenen Netzwerk-Namespace ohne Netzschnittstelle und ohne Route; Portscans und ICMP sind dort mechanisch unmöglich. Der einzige Ausweg ist ein Proxy, der Hostnamen gegen eine Allowlist prüft — und dessen Listen **keine Adressbereiche (CIDR) kennen**, sondern nur einzelne Namen und Adressen. Ein Firmennetz „als Bereich" lässt sich damit nicht sperren.
- **Grenze B:** **entfällt vollständig.** Es gibt keinen entfernten Extension-Host, also auch keinen Rückkanal aus einer weniger vertrauten Umgebung.
- **Innere Sandbox:** voll wirksam — mit einer wichtigen Ausnahme: **In Verbindung mit git-Worktrees scheitern alle git-Kommandos** (#80278, offen und von Maintainern reproduziert). Wer nach dem Worktree-Modell arbeitet, kann die Sandbox derzeit nicht dauerhaft einschalten.
- **Fazit:** Die Konstellation ohne Grenze-B-Problem, aber mit der schwächsten Dateigrenze und ohne brauchbares Mittel gegen Bereichszugriffe im Netz.

### 3.2 Lokal mit Container — VS Code Desktop, „Reopen in Container"

Der Container läuft auf demselben Rechner; VS Code Desktop hängt sich an ihn.

- **Wo Claude läuft:** im Container.
- **Grenze A, Dateisystem:** **stark und unbedingt.** Was nicht gemountet ist, existiert für Claude nicht. Das ist qualitativ besser als jede Deny-Liste: Eine Regel muss greifen, ein fehlender Mount muss nichts greifen. Der Preis ist Disziplin bei den Mounts — wer das ganze Home hineinreicht, gibt genau diesen Vorteil wieder auf.
- **Grenze A, Netz:** hier liegt der eigentliche Gewinn. Container-Egress lässt sich über Dockers `DOCKER-USER`-Kette **bereichsweise** filtern, also genau das, was die Domain-Allowlist der Sandbox nicht kann. Ohne solche Regel erreicht der Container jedoch alles, was der Host routet — Firmennetz und VPN eingeschlossen.
- **Grenze B:** **vorhanden, und das Ziel ist derselbe Rechner**, dessen Home man gerade durch schmale Mounts geschützt hat. Das ist der dokumentierte Fall von Trail of Bits.
- **Innere Sandbox:** **degradiert.** In einem unprivilegierten Container kann bubblewrap kein frisches `/proc` mounten; die Sandbox läuft nur mit `enableWeakerNestedSandbox` und dann erklärt geschwächt — oder sie startet nicht und läuft per Default ungeschützt weiter.
- **Fazit:** Starke Dateigrenze und brauchbare Netzgrenze, aber der Rückkanal zielt auf genau das Gerät, das man schützen wollte.

### 3.3 SSH auf einen Remote-Rechner, ohne Container

VS Code Desktop lokal, per Remote-SSH auf einen anderen Rechner; das Projekt liegt dort, kein Container.

- **Wo Claude läuft:** auf dem Remote-Rechner, im Home des dortigen Kontos.
- **Grenze A, Dateisystem:** wie 3.1, nur auf dem Remote-Rechner — Sandbox-Schreibseite wirkt, Leseseite schwach, Aufzählung nötig. Ein Vorteil in der Praxis: Auf einem dedizierten Rechner liegt oft wenig mehr als die Projekte und die Git-Konfiguration, der mögliche Schaden ist also kleiner als im eigenen Home.
- **Grenze A, Netz:** wie 3.1 — Abtasten mechanisch verhindert, gezielter Zugriff über den Proxy möglich, kein Mittel für Adressbereiche. Das ist hier besonders relevant, weil solche Rechner häufig an Gerätenetzen hängen.
- **Grenze B:** **vorhanden, Ziel ist der lokale Rechner.** Der Extension-Host läuft auf dem Remote-Rechner und ist mit der Bedienoberfläche auf dem lokalen verdrahtet. *Diese Einordnung ist abgeleitet, nicht gemessen:* Trail of Bits hat den Weg für den Container-Fall belegt; dass die Architektur bei Remote-SSH dieselbe ist, folgt aus dem Aufbau, ist aber nicht eigens geprüft.
- **Innere Sandbox:** voll wirksam, mit demselben Worktree-Vorbehalt wie 3.1.
- **Fazit:** Verlagert das Risiko auf ein Gerät, dessen Verlust weniger schmerzt, ohne die Grenzen selbst zu verbessern.

### 3.4 SSH auf einen Remote-Rechner, dort ein Container — der Hauptfall

VS Code Desktop lokal, per SSH auf den Remote-Rechner, dort an einen Container angehängt; der VS Code Server läuft im Container. Diese Kette entsteht regelmäßig, wenn ein Projekt nur im Container lauffähig ist und die dafür nötige Hardware auf einem dedizierten Rechner steht.

- **Wo Claude läuft:** im Container auf dem Remote-Rechner.
- **Grenze A, Dateisystem:** stark wie 3.2 — Mounts entscheiden.
- **Grenze A, Netz:** bereichsfähig wie 3.2 über `DOCKER-USER`, und hier am wichtigsten, weil der Remote-Rechner im Firmennetz steht.
- **Grenze B:** **vorhanden, Ziel ist der lokale Rechner** — nicht der Remote-Rechner. Das ist der kontraintuitive Punkt: Zwei Zwischenstationen ändern nichts daran, dass die Bedienoberfläche lokal läuft und dort Terminals öffnet.
- **Innere Sandbox:** degradiert wie 3.2.
- **Fazit:** Die Konstellation mit den besten Grenzen nach innen. Sie löst alle drei Schutzziele, wenn die Mounts schmal sind, der Schlüsselzugriff über den Agenten läuft und der Container-Egress gefiltert ist. Offen bleibt allein Grenze B.

### 3.5 Container mit Browser-Client — die Variante ohne Grenze B

Wie 3.2 oder 3.4, aber die Bedienoberfläche ist ein Browser-Tab: Im Container läuft `code-server` oder `openvscode-server`, der Port wird per SSH weitergeleitet und im Browser geöffnet. Kein lokal installiertes VS Code Desktop ist beteiligt.

- **Grenzen A:** unverändert stark wie 3.2 und 3.4.
- **Grenze B:** **entfällt strukturell.** Eine Webseite kann kein Terminal auf dem Rechner des Betrachters öffnen; der Angriffsweg existiert nicht, statt nur unwahrscheinlich zu sein.
- **Innere Sandbox:** degradiert wie in jedem Container.
- **Praktische Kosten:** Die Claude-Erweiterung ist für diesen Weg verfügbar — sie liegt neben dem Microsoft-Marktplatz auch in der Open-VSX-Registry, aus der `code-server` standardmäßig bezieht. Es entfallen jedoch Bequemlichkeiten des Desktop-Programms, und die Einrichtung ist einmalig aufwendiger.
- **Fazit:** Die einzige Konstellation, die alle drei Schutzziele erreicht **und** Grenze B schließt. Der richtige Weg für Projekte, die viel ungeprüften fremden Inhalt verarbeiten.

## 4 Vergleich

| Konstellation | Grenze A Dateisystem | Grenze A Netz (Bereiche sperrbar?) | Grenze B | Innere Bash-Sandbox |
|---|---|---|---|---|
| 3.1 Klassisch lokal | schwach beim Lesen, Aufzählung nötig | nein — nur Namen/Einzeladressen | entfällt | voll, aber bricht git-Worktrees |
| 3.2 Lokal + Container (Desktop) | stark, über Mounts | ja, über `DOCKER-USER` | vorhanden, Ziel: derselbe Rechner | degradiert |
| 3.3 SSH, ohne Container | schwach, aber auf fremdem Gerät | nein | vorhanden (abgeleitet), Ziel: lokaler Rechner | voll, Worktree-Vorbehalt |
| 3.4 SSH + Container | stark, über Mounts | ja, über `DOCKER-USER` | vorhanden, Ziel: lokaler Rechner | degradiert |
| 3.5 Container + Browser | stark, über Mounts | ja, über `DOCKER-USER` | **entfällt** | degradiert |

## 5 Die Frage: sollte der klassische lokale Fall in einen Container wechseln?

Die naheliegende Antwort wäre „ja, der Container ist die stärkere Grenze". Sie ist zu kurz, denn der Wechsel von 3.1 auf 3.2 ist ein **Tausch**, kein Gewinn:

**Man gewinnt** eine unbedingte Dateigrenze — Mounts statt einer Aufzählung, die man dauerhaft pflegen und nach jeder Softwareinstallation nachziehen müsste — und erstmals ein Mittel, Adressbereiche im Netz zu sperren. Man gewinnt außerdem, dass Hooks und MCP-Server mit eingehegt sind; die eingebaute Sandbox erfasst sie nicht, weil sie nur Bash-Kindprozesse umfasst.

**Man verliert** die voll wirksame innere Sandbox, die im Container nur geschwächt läuft. Und man **holt sich Grenze B ins Haus**, die in 3.1 gar nicht existierte — mit dem lokalen Rechner als Ziel, also genau dem Gerät, dessen Home man durch die schmalen Mounts eben geschützt hat. Für diesen Kanal gibt es keine Konfiguration, nur Architektur.

**Damit lautet die Antwort: nicht 3.2, sondern 3.5.** Wer die Container-Grenze im lokalen Fall haben will, sollte den Browser-Client nehmen — dann sind beide Gewinne echt und der Verlust entfällt. Wer beim Desktop-Programm bleiben möchte, fährt mit 3.1 plus einer gepflegten Berechtigungsebene nicht schlechter, weil er den Rückkanal gar nicht erst öffnet.

Ein projektspezifischer Zusatz verschiebt diese Abwägung: **Wer nach dem git-Worktree-Modell arbeitet, kann die Sandbox in 3.1 derzeit nicht dauerhaft einschalten** (#80278). Dann verliert 3.1 auch noch seine wirksame Schreibgrenze, und der Container wird zur klar besseren Wahl — weiterhin mit 3.5 als der vernünftigen Bauform.

## 6 Was in den Container-Konstellationen zu konfigurieren ist

Drei Bausteine, je einer pro Schutzziel. Die Settings-Ebene von Claude Code bleibt daneben nützlich, ist aber in diesen Konstellationen nicht das tragende Mittel; ihre Blöcke stehen in `sandbox-settings.de.md`.

**Erstes Ziel, kein Schreibzugriff außerhalb der Arbeit — schmale Mounts.** Nicht das Home hineinreichen, sondern nur, was gebraucht wird. Für Sitzungskontinuität und Skill-Konfiguration genügt `~/.claude`; zu beachten ist, dass der Anmeldezustand in `~/.claude.json` **außerhalb** dieses Ordners liegt, weshalb `CLAUDE_CONFIG_DIR` auf den gemounteten Pfad zu setzen ist — sonst muss man sich nach jedem Neubau erneut anmelden:

```jsonc
"mounts": [
  "source=/home/BENUTZER/.claude,target=/home/BENUTZER/.claude,type=bind",
  "source=/home/BENUTZER/.gitconfig,target=/home/BENUTZER/.gitconfig,type=bind,readonly"
],
"containerEnv": { "CLAUDE_CONFIG_DIR": "/home/BENUTZER/.claude" }
```

Wer `~/.claude` über mehrere Rechner synchron hält, braucht dafür keinen Mechanismus im Container: Der Abgleich läuft auf dem Host-Betriebssystem, und der Container sieht durch den Mount ohnehin den aktuellen Stand.

**Zweites Ziel, Schlüssel nicht unmittelbar lesbar — Agent-Weiterleitung statt Schlüssel-Mount.** Statt `~/.ssh` hineinzureichen, wird nur der Socket des SSH-Agenten weitergegeben. Damit kann der Container signieren, also `git clone` und `git push` ausführen, aber die private Schlüsseldatei liegt nie in ihm:

```jsonc
"mounts": [
  "source=${localEnv:SSH_AUTH_SOCK},target=/ssh-agent,type=bind"
],
"containerEnv": { "SSH_AUTH_SOCK": "/ssh-agent" }
```

Das ist strikt besser als der Mount des Schlüsselordners: Ein kompromittierter Container kann den Schlüssel **benutzen**, aber nicht **lesen und mitnehmen**.

**Drittes Ziel, kein Abtasten im Netz — gefilterter Container-Egress.** Docker legt für Nutzerregeln eine eigene, sonst leere iptables-Kette an, die Neustarts des Dienstes übersteht und die übrige Firewall nicht anfasst. Auf dem Rechner, der den Container betreibt:

```bash
iptables -I DOCKER-USER -d 10.0.0.0/8     -j DROP
iptables -I DOCKER-USER -d 172.16.0.0/12  -j DROP
iptables -I DOCKER-USER -d 192.168.0.0/16 -j DROP
iptables -I DOCKER-USER -j RETURN
```

Wirkung: Container-Verkehr in private Adressbereiche wird verworfen, das Internet bleibt vollständig offen. **Das ist keine allgemeingültige Vorlage.** Sobald an einem Rechner Geräte hängen, die zur Aufgabe gehören — Kameras, Messtechnik, ein interner Registry-Mirror —, gehört für jedes eine `ACCEPT`-Zeile **vor** die `DROP`-Zeilen. Die Regel bleibt damit eine Sperrliste mit benannten Ausnahmen und nicht eine Freigabeliste, die „Internet frei" zerstören würde. Diese Ausnahmen sind je Rechner einzeln zu klären; eine pauschale Fassung gibt es nicht.

**Und ein Vorbehalt zur inneren Sandbox:** Im Container ist `sandbox.enableWeakerNestedSandbox` nötig, weil bubblewrap dort reduziert läuft. Das schwächt die Isolation erklärt und ist nur zu vertreten, weil der Container die eigentliche Grenze ist. Außerhalb von Containern gehört diese Einstellung nicht gesetzt.

## 7 Messbefunde vom 2. September 2026

Alle Werte in einer laufenden Sitzung der VS-Code-Erweiterung auf Linux erhoben, mit aktiver Sandbox. Sie sind nachprüfbar und stützen die Bewertungen oben.

**Die Sandbox wirkt in der Erweiterung.** `SANDBOX_RUNTIME` war gesetzt, `~`, `/etc` und `/usr/bin` waren nur lesbar, schreibbar allein das Projekt und das Sitzungs-Temp. Damit sind zwei Fehlerberichte, die das Gegenteil behaupten (#32814 für die Sandbox, #29159 für die Berechtigungen, beide Februar bis März 2026 und beide ohne Bearbeitung geschlossen), für den gemessenen Stand widerlegt.

**Die Leseseite ist offen, wo sie nicht aufgezählt ist.** `~/.ssh` war wirksam gesperrt — null sichtbare Einträge —, weil es in den Berechtigungsregeln und in `sandbox.credentials` steht. Dagegen waren **19 Einträge unter `~/git`**, also alle übrigen Projekte, ohne Weiteres lesbar, ebenso `~/.bashrc`. Das ist der Preis der Aufzählung in reiner Form.

**Netz, direkter Weg: mechanisch zu.** Der Namespace hatte nur `lo` und eine **leere Routing-Tabelle**. Verbindungsversuche auf `10.0.0.1`, `172.16.0.1` und `192.168.1.1` scheiterten binnen 0 ms mit „Netzwerk ist nicht erreichbar", ohne dass ein Paket entstand. ICMP war unmöglich (kein `CAP_NET_RAW`), Namensauflösung im Namespace fand nicht statt. Portscans sind auf diesem Weg ausgeschlossen.

**Netz, Proxy-Weg: offen.** Es lauschten genau zwei Sockets, ein HTTP-Proxy und ein SOCKS-Proxy. Über den HTTP-Proxy wurde von einem VPN-internen Host **eine echte Seite geladen — HTTP 200, 1964 Byte**, übereinstimmend mit dem, was derselbe Host auf direkte Abfrage des Nutzers lieferte. `CONNECT`-Tunnel auf dessen Ports 22, 80 und 443 wurden aufgebaut; Port 3389 wurde abgelehnt, und zwar durch den Klassifikator des Auto-Modus, nicht durch eine Grenze. **Damit ist gezeigt: Der Proxy-Weg erlaubt gezieltes Erreichen interner Hosts und, über `CONNECT` auf verschiedene Ports, auch ein Abtasten von Diensten.** Der Namespace allein verhindert das nicht.

**Eine Fehldeutung, die dabei auffiel und hier festgehalten wird, damit sie nicht wiederkehrt:** Ein erster Versuch gegen einen Host im lokalen Heimnetz lief stumm in eine Zeitüberschreitung, was zunächst als Sperre privater Adressbereiche durch den Proxy gedeutet wurde. Das war falsch — der Host war wegen der aktiven VPN-Verbindung schon für den Wirtsrechner nicht erreichbar. **Der Proxy sperrt private Bereiche nicht.** Ein stummer Zeitablauf ist kein Beleg für eine Sperre; ein Vergleichsziel gehört immer dazu.

**Erlaubte Ziele sind vollwertig erreichbar.** Ein `CONNECT` auf einen erlaubten Host mit ungewöhnlichem Port (8443) wurde durchgelassen. Die Allowlist ist eine Host-, keine Dienstgrenze — ein einziger interner Eintrag öffnet diesen Rechner auf allen Ports.

## 8 Einordnung: was neu ist und was nicht

Ein Einwand des Entwicklers gehört in diesen Bericht, weil er das Maß setzt: **Auch Handarbeit war nie geschützt.** Wer selbst programmiert, kann mit einem falschen Befehl ebenso Daten vernichten oder ein fremdes System stören; niemand hat dafür je eine Sandbox verlangt. Ein Sicherheitsbericht, der den Agenten an einem Maßstab misst, den der Mensch daneben nie erfüllen musste, ist unredlich.

**Was tatsächlich hinzukommt, ist dreierlei — und nur das Dritte ist eine neue Art von Risiko:**

- **Geschwindigkeit.** Der Agent führt in Minuten aus, was von Hand Stunden dauert. Das vergrößert nicht die Art des Fehlers, aber seine Reichweite, bevor jemand eingreift.
- **Entschiedene Handlungen ohne vorherige Prüfung.** Die Inferenz wählt selbst, welcher Befehl als nächstes läuft. Das entspricht dem Menschen, der sich vertippt — mit dem Unterschied, dass niemand die Absicht gegengelesen hat.
- **Fremde Absicht im eigenen Werkzeug.** Das ist der Punkt ohne Vorbild in der Handarbeit: Inhalte, die der Agent liest — eine Abhängigkeit, ein fremdes Repository, eine Webseite, ein Fehlerbericht —, können Anweisungen enthalten, die er befolgt. Ein Mensch, der eine Dokumentationsseite liest, führt sie nicht aus.

Für die hier betrachteten Anwendungsfälle folgt daraus eine klare Gewichtung, die sich mit der Einschätzung des Entwicklers deckt: **Die eigenen Fehlgriffe sind das kleinere Problem** — dagegen hilft dieselbe Vorsicht wie bei Handarbeit, plus Versionskontrolle. **Das größere ist das selbsttätige Vordringen auf andere Systeme**, weil dort fremde Absicht und Geschwindigkeit zusammenkommen und der Schaden nicht mehr das eigene Projekt betrifft.

**Mit einer Einschränkung, die ausdrücklich dazugehört:** Wo andere Systeme **Bestandteil der Aufgabe** sind — die Kamera am Messrechner, der Datenbankserver, die Anlage —, muss der Agent sie erreichen, und dort schützt auch den Menschen nichts. Diese Ziele gehören benannt und freigegeben, nicht gesperrt. Genau deshalb ist die Netzregel in Abschnitt 6 eine Sperrliste mit Ausnahmen und keine Freigabeliste: Sie verhindert das Abschweifen, nicht die Arbeit.

## 9 Befunde an der eigenen Konfiguration

Zwei konkrete Funde aus der Durchsicht am 2. September 2026. Beide sind noch nicht behoben und liegen in Dateien, über die der Entwickler entscheidet.

**Befund 1 — Schlüssel im falschen Abschnitt, dadurch wirkungslos.** In der Benutzer-`settings.json` sind die Einträge aus Block A2 von `sandbox-settings.de.md` (`denyWrite`, `denyRead` gegen Selbst-Rechteausweitung) unter `sandbox.credentials` eingehängt statt unter `sandbox.filesystem`. Offenbar sind beim Zusammenführen der Blöcke A1 und A2 die Schlüssel in den falschen Abschnitt gerutscht. **Bestätigt durch die wirksame Sitzungsrichtlinie:** In deren Lese-Sperrliste erscheinen alle Pfade aus den Berechtigungsregeln und aus `credentials.files`, aber `~/.claude.json` fehlt — der `denyRead`-Eintrag ist also nicht angekommen. Ein ergänzender Leseversuch bestätigte, dass die Datei lesbar ist. Praktische Folge gering, weil Claude Code die Schreibseite dieser Pfade ohnehin selbst schützt; die Leseseite von `~/.claude.json` bleibt jedoch offen.

**Befund 2 — falscher Dateiname im Snippet.** Block A2 in `sandbox-settings.de.md` nennt `~/.claude/credentials.json`. Die tatsächliche Datei heißt `~/.claude/.credentials.json`, mit führendem Punkt. Der Eintrag würde also auch an der richtigen Stelle sein Ziel verfehlen. Zu prüfen ist bei der Korrektur, ob die Hersteller-Referenz, aus der der Block stammt, denselben Fehler trägt oder ob er beim Übernehmen entstand.

## 10 Offene Prüffragen

- **Grenze B bei Remote-SSH.** Belegt ist der Weg für „Reopen in Container". Dass er bei Remote-SSH ohne Container gleichermaßen besteht, folgt aus der Architektur, ist aber nicht gemessen. Solange das offen ist, sollte man ihn in beiden Fällen als vorhanden behandeln.
- **Eigener Proxy statt Firewall.** Claude Code kann seinen Sandbox-Verkehr über einen selbst betriebenen Proxy leiten. Ein solcher Proxy versteht Adressbereiche und löst Namen auf, könnte also auch interne Namen erfassen — und käme ohne Firewall-Eingriff aus. Ungeklärt ist, ob er den eingebauten Proxy ersetzt oder sich hinter ihn schaltet; davon hängt ab, ob er allein die Grenze bildet. Prüfbar mit demselben `CONNECT`-Versuch aus Abschnitt 7.
- **Die Sandbox unter macOS.** Alle Netzbefunde stammen von Linux, wo ein Netzwerk-Namespace die Grenze zieht. Unter macOS arbeitet ein anderes Verfahren ohne Namespace; dass rohe Verbindungen ins lokale Netz dort ebenso scheitern, ist **nicht** belegt.
- **Wirksamkeit jedes Lese-Verbots.** Wegen der bekannten Unzuverlässigkeit von `denyRead` gilt kein Eintrag als wirksam, bevor er durch einen Leseversuch abgetastet wurde. Das betrifft jede Ergänzung der Geheimnis-Inventur.

## 11 Quellen

**Claude-Code-Doku:** [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Sandbox-Umgebungen im Vergleich](https://code.claude.com/docs/en/sandbox-environments) · [Development containers](https://code.claude.com/docs/en/devcontainer) · [VS Code](https://code.claude.com/docs/en/vs-code) · [Berechtigungsmodi](https://code.claude.com/docs/en/permission-modes) · [Settings-Referenz](https://code.claude.com/docs/en/settings-reference)

**Bedrohungsmodell und Referenzkonfigurationen:** Trail of Bits, [claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer) — dort auch die Beschreibung des Rückkanals · The Red Guild, [Leveraging VSCode internals to escape containers](https://blog.theredguild.org/leveraging-vscode-internals-to-escape-containers/) · Microsofts Einordnung als beabsichtigtes Verhalten: [vscode-remote-release #6608](https://github.com/microsoft/vscode-remote-release/issues/6608#issuecomment-1112960548)

**Bug-Reports:** [#40941](https://github.com/anthropics/claude-code/issues/40941) Doku-Empfehlung zum Sperren des Homes bricht das Arbeitsverzeichnis · [#61208](https://github.com/anthropics/claude-code/issues/61208) `denyRead` nicht durchgesetzt · [#80278](https://github.com/anthropics/claude-code/issues/80278) Sandbox bricht git-Worktrees, offen · [#32814](https://github.com/anthropics/claude-code/issues/32814) und [#29159](https://github.com/anthropics/claude-code/issues/29159) Erweiterung wende Einstellungen nicht an — durch die Messung in Abschnitt 7 für den geprüften Stand widerlegt

**Im selben Ordner:** `sandbox-settings.de.md` — die Settings-Ebene mit Parameterbeschreibung und den vier belegten Sandbox-Einschränkungen. **Im Projekt:** `.research/Claude-Code-Sicherheit im Auto-Modus/bericht.md` — die Begründung der Schichtung aus Regularium, Verfahren, Mechanik und Struktur.
