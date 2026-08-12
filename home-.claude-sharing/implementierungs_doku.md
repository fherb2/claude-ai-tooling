# Implementierungsdokumentation: Syncthing-Sync für `~/.claude`

Dieses Dokument ist die Konzeption des Vorhabens und wird mit Beginn der Implementierung parallel zum Code weitergepflegt. Es besteht aus drei Segmenten: **Segment 1** erklärt das System entlang der Abläufe, wie sie der Nutzer erlebt, und ist zugleich die Quelle der späteren Anwenderdokumentation. **Segment 2** enthält die projektweiten Vorgaben, die quer über den gesamten Code gelten und an denen sich jede einzelne Datei messen lassen muss. **Segment 3** beschreibt die Einheiten — Skripte, Anweisungsdateien, Datenstrukturen — jede in einem eigenen, in sich geschlossenen Kapitel. Ein **Anhang** sammelt die vor der Implementierung zu klärenden Fragen.

Es gilt die Prosa-Code-Grenze: Dieses Dokument enthält keinen Implementierungscode. Kommandos, Dialogtexte und Dateinamen sind Schnittstellen-Fakten; endgültig beschlossene Funktionssignaturen werden erst nach ihrer Festlegung hier eingetragen — derzeit gibt es keine.

Arbeitsregeln der Entwicklung: Geschrieben wird ausschließlich im Arbeitsordner des Vorhabens (`home-.claude-sharing/` im Git-Repository `claude-ai-tooling`). Das reale `~/.claude` verändert im Normalbetrieb nur Syncthing; Entwicklungs- und Funktionstests laufen gegen eigene Testordner, nie gegen `~/.claude` (siehe 3.8). Aussagen, die noch nicht geklärt sind, tragen die Markierung **Offen** oder stehen als Frage im Anhang. Die Einrichtung von Server und Geräten ist nicht Teil dieses Dokuments — sie steht in der fortbestehenden `Syncthing-Synology-Konfigurationsanleitung-allgemein.md`.

---

# 1 Zusammenhänge

@Claude: Dieses große Kapitel 1 ist inhaltlich vom Entwickler geprüft und redigiert. Hier bitte Änderung nur in intensiver Absprache mit dem Entwickler vornehmen. Idealerweise dem Entwickler die EInarbeitung von Änderungen vorgeben.

@Claude: In diesem Kapitel gibt es noch ein Update der Kapitelnummerierung durchzuführen. Das schließt auch eine Überarbeitung der Kapitelnummern in Verweisen ein. Diese Überarbeitung darf automatisch erfolgen, nachdem der Entwickler dem Anpassungsvorschlag von Dir explizit zugestimmt hat. Dabei sind keine Änderungen an Worten vorzunehmen. Nur die Kapitelnummern sind anzupassen. Die Verweise auf die Kapitel 1.x sind dabei auch in allen anderen Teilen des Dokuments zu korrigieren, wo auf das Segment 1 verwiesden wird. Nach der vollständigen Aktualisierung der Kapitelnummern ist dieser Absatz zu entfernen.

@Claude: In diesem Kapitel gibt es HTML-Kommentare zur Klärung ob die Details in einigen Absätzen noch identisch zum Code sind. Diese einzelnen Stellen sind mit dem Entwickler und einem Code-Review zu klären. Wenn die jeweiligen Absätze geklärt wurden, ist der jeweils zugehörige HTML-Kommentar zu entfernen. Nachdem alle Stellen überarbeitet wurden, wird dieser Absatz entfernt.

## 1.1 Ziel und Nutzen

Claude Code, Claude Desktop und die VSCode Extension Claude Code (anthropic.claude-code) halten ihren gesamten Arbeitszustand — Konfiguration teilweise, Sitzungsprotokolle, vor allem aber das Projektgedächtnis — im Verzeichnis `~/.claude` des jeweiligen Rechners. Wer an mehreren Rechnern arbeitet, hat dadurch mehrere voneinander unabhängige Gedächtnisse. Dieses Vorhaben hält `~/.claude` über Syncthing und einen dauerhaft laufenden Vermittlungsknoten, z.B. auf einem Synology NAS, zwischen den beteiligten Rechnern synchron, sodass derselbe Kontext überall zur Verfügung steht.

Die Synchronisation selbst leistet Syncthing vollständig und ereignisgesteuert im Hintergrund. Dafür wird nichts implementiert / bereitgestellt, abgesehen von einem passend zu ~/.claude erstellten und getesteten Ignore-File für die Sysnchronisation (.stignore) und einer beispielhaften Installations- und Konfigurationsanleitung für Syncthing.

**Die Eigenleistung dieses Vorhabens liegt vor allem in einer umfassende *Konfliktbehandlung*, wenn ein einfaches Synchronisieren in Ausnahmefällen versagt: Syncthing führt beidseitig geänderte Dateien absichtlich nie inhaltlich zusammen, sondern legt die unterlegene Fassung als Konfliktkopie neben das Original (1.5). Ein selbst gebauter *Konflikt-Wächter*, installiert als Hintergrunddienst, (3.1) entdeckt solche Kopien, meldet sie dem Nutzer und bietet den Einstieg in eine geführte Lösung mit Claude (1.7, 1.8).**

## 1.2 Die Landschaft: Geräte, Knoten, Ist-Stand

Drei Geräte in Sterntopologie: Die **Synology** als beispielhafter Sync-Server, über den sich die betreffenden Clients synchronisieren, trägt den dauerhaft laufenden Vermittlungsknoten (Installation als SynoCommunity-Paket) mit einer vollständigen Kopie des Ordners. In unserem Beispiel kennen **Rechner A** (Laptop im Home-Office) und **Rechner B** (Büro-Rechner) jeweils nur die Synology, nicht einander; sie müssen nie gleichzeitig eingeschaltet sein — der Datenfluss ist A → Synology → B und umgekehrt. (Server auf Synology: Die Option „Introducer" bleibt überall aus, damit der Knoten die Rechner einander nicht bekannt macht.)

Ist-Stand der Beispielanwendung: Synology und Rechner A und B sind eingerichtet und synchronisieren `~/.claude` bereits produktiv. Der Watcher ist als Dienst (user-Basis) installiert und läuft erfolgreich. Konfliktsituationen wurden per Hand herbeigeschaffen, um zu testen. Im Betrieb selbst gab es bisher keine Konfliktsituationen.

Eine Implementation des Überwachungsdienstes für Windows (1.11) wurde noch nicht erstellt.

Einrichtung, Ports, Rechte und Betriebsdetails des Knotens: siehe `Syncthing-Synology-Konfigurationsanleitung-allgemein.md`. Dieses Dokument setzt eine danach eingerichtete Umgebung voraus.

## 1.3 Was mitwandert — und was nicht

Abgeglichen wird grundsätzlich der gesamte Inhalt von `~/.claude`, einschließlich der Sitzungsprotokolle und Chats unter `projects/` — sie sind der eigentliche Zweck des Vorhabens.

Ausgeschlossen wird über die Datei `.stignore` im `~/.claude`-Ordner selbst. Sie wandert **nicht** mit und muss auf jedem Gerät einzeln gepflegt werden, **bevor** der Ordner dort erstmals verbunden wird (verbindliche Regel in 2.3). Der aktuelle Inhalt ist in `files/.stignore` abgelegt und kann als Vorgabe verwendet werden

`.credentials.json` ist ein sicherheitskritische und anmeldungsbedingter Eintrag und wird bei der Synchronisierung ausgeschlossen.

**Im Betrieb bestätigt:** Ein Wechsel des **Claude-Kontos** — abmelden und mit einem anderen Konto anmelden, in Claude Desktop wie in der VSCode-Erweiterung — verlief ohne jede Störung durch den Abgleich und ohne eine einzige Konfliktkopie. Das ist keine glückliche Fügung, sondern die Folge davon, wo Kontozustand liegt: in `.credentials.json`, die ausgeschlossen ist, und in `~/.claude.json`, die **außerhalb** des abgeglichenen Ordners liegt (1.3). Beide Orte sind dem Abgleich entzogen, also ist ein Kontowechsel eine rein örtliche Angelegenheit — er kann weder Konflikte erzeugen noch versehentlich eine Anmeldung auf den anderen Rechner tragen. Dass es sich so verhält, ist es beobachtet und damit belegt.

### Was außerhalb des Ordners liegt und deshalb nie mitwandert

Der Ordner `~/.claude` ist **nicht** der gesamte Zustand von Claude Code. Daneben liegt die Datei `~/.claude.json`, und der Schnitt zwischen beiden verläuft nach Art der Daten, nicht nach Oberfläche (belegt, [Settings](https://code.claude.com/docs/en/settings)):

> *„User settings are defined in `~/.claude/settings.json` and apply to all projects."*
>
> *„Other configuration is stored in `~/.claude.json`. This file contains your OAuth session, MCP server configurations for user and local scopes, per-project state (allowed tools, trust settings), and various caches."*

Beide gehören Claude Code gemeinsam; auch VS-Code-Erweiterung, JetBrains-Plugin und Desktop-App schreiben nach `~/.claude/` (belegt, [Advanced setup](https://code.claude.com/docs/en/setup)). Der Inhalt der Datei auf Rechner A bestätigt die Beschreibung (beobachtet, nur Schlüssel gelesen): `oauthAccount`, `projects`, `machineID`, `userID` und rund ein Dutzend `*Cache`-Schlüssel.

**Für dieses Vorhaben ist das günstig, nicht hinderlich.** Was dort liegt, soll ohnehin rechnergebunden bleiben: die Anmeldesitzung (genau das, was 2.3 für `.credentials.json` ausschließt), die `machineID`, die Vertrauensentscheidungen je Projekt und flüchtige Zwischenspeicher. Weil die Datei **außerhalb** von `~/.claude` liegt, kann sie gar nicht versehentlich in den Abgleich geraten — hätte sie darin gelegen, bräuchte 2.3 einen weiteren Ausschluss.

**Ein Rest bleibt und ist zu wissen: MCP-Server-Konfiguration im User- und Local-Scope wandert nicht mit.** Wer sich auf einem Rechner einen MCP-Server einrichtet, hat ihn auf dem anderen nicht und muss ihn dort erneut eintragen. Die drei Ablageorte laut Doku (belegt, [MCP](https://code.claude.com/docs/en/mcp)):


| Scope           | gilt für                         | liegt in                         | wandert mit dem Abgleich                  |
| --------------- | --------------------------------- | -------------------------------- | ----------------------------------------- |
| Local (Vorgabe) | nur das aktuelle Projekt          | `~/.claude.json`                 | nein                                      |
| User            | alle Projekte des Benutzers       | `~/.claude.json`                 | nein                                      |
| Project         | nur das aktuelle Projekt, geteilt | `.mcp.json` in der Projektwurzel | entfällt — wandert mit dem Projekt-Repo |

Für den Project-Scope ist das kein Verlust, sondern der vorgesehene Weg: Die Datei gehört in die Versionsverwaltung des jeweiligen Projekts. Zu tragen ist nur der User- und Local-Scope, und dort wiegt es leicht, weil ein einmal eingerichteter Server selten wechselt.

## 1.4 Der Normalbetrieb: ereignisgesteuerter Abgleich

Es gibt keinen Abgleich-Zyklus und kein Sync-Skript. Besteht die Verbindung zum Knoten, ist eine Änderung typischerweise binnen Sekunden dort. Syncthing wird durch das Betriebssystem bei Dateiänderungen im Synchronisationsordner gtriggert. Ist der Rechner aus, holt er beim nächsten Start selbsttätig nach.

### Zwei Erkennungswege, die nebeneinander laufen

Syncthing erkennt Änderungen auf **zwei voneinander unabhängigen Wegen**, die gleichzeitig aktiv sind. Das ist keine Entweder-oder-Einstellung, und beide Schalter liegen in der Oberfläche unter Ordner → Bearbeiten → Erweitert:


| Einstellung                                         | Vorgabe | Wirkung                                                                                                  |
| --------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------- |
| `fsWatcherEnabled` („Auf Änderungen achten")      | **an**  | Dateisystem-Überwachung des Betriebssystems (unter Linux inotify) — meldet Ereignisse praktisch sofort |
| `fsWatcherDelayS`                                   | 10 s    | Sammelfrist, bevor aus erkannten Ereignissen ein Suchlauf wird                                           |
| `rescanIntervalS` („Vollständiges Suchintervall") | 3600 s  | Vollständiger Suchlauf als Sicherheitsnetz                                                              |

Die ereignisgesteuerte Erkennung ist also die Vorgabe und muss nicht eingeschaltet werden. Der stündliche vollständige Suchlauf ist **nicht** der Abgleichtakt, sondern der Auffangmechanismus für Ereignisse, die die Überwachung verpasst hat — was bei Netzlaufwerken, hoher Systemlast oder erschöpften inotify-Kontingenten vorkommt. Die Doku rät ausdrücklich, ihn neben der Überwachung aktiviert zu lassen: *„Even with watcher enabled it is advised to keep regular full scans enabled, as it is possible that some changes aren't picked up by it."* Sein tatsächlicher Abstand streut zufällig zwischen dem 0,75- und 1,25-fachen des eingestellten Werts, damit nicht alle Ordner gleichzeitig loslaufen.

`fsWatcherTimeoutS = 0` bedeutet nicht „abgeschaltet", sondern „wird aus der Sammelfrist berechnet"; dieser Wert erzwingt bei einer *fortlaufend* wachsenden Datei irgendwann einen Suchlauf, obwohl sie nie zur Ruhe kommt.

**Festlegung:** Alle drei Werte bleiben auf den Vorgaben (siehe auch 2.2). Bei 22 MB kostet der stündliche Suchlauf praktisch nichts und ist der einzige Schutz gegen verpasste Ereignisse; eine kürzere Sammelfrist würde bei den wachsenden Protokolldateien nur häufiger unfertige Zwischenstände übertragen, ohne das Konfliktfenster nennenswert zu verkleinern.

Für den Alltag folgen daraus zwei Verhaltensregeln (normativ in 2.2): **Syncthing soll vor der schreibenden Anwendung laufen** — nach dem Einschalten erst den Abgleich ankommen lassen, dann mit Claude arbeiten —, und **ein Rechner soll nicht ausgeschaltet werden, solange die Oberfläche noch „Syncing" zeigt**. Beides verkleinert das Zeitfenster, in dem beidseitige Änderungen entstehen können: Das Konfliktfenster ist bei abwechselnd betriebenen Rechnern nicht die Sekunden-Verzögerung der Übertragung, sondern die Zeit zwischen letzter Änderung auf dem einen und erstem Nachholen auf dem anderen Rechner.

**Ist-Stand auf Rechner A** (aus der laufenden Konfiguration abgelesen, Ordner `~/.claude`): `fsWatcherEnabled="true"`, `fsWatcherDelayS="10"`, `rescanIntervalS="3600"`, `fsWatcherTimeoutS="0"`, Typ `sendreceive` — entspricht damit den Festlegungen dieses Kapitels und 2.1.

## 1.5 Konflikte: Entstehung und Gestalt

Ein Konflikt entsteht, wenn dieselbe Datei auf zwei Geräten geändert wurde, bevor der Abgleich die jeweils andere Änderung zustellen konnte. Syncthing erkennt das über Versionsvektoren und entscheidet **nie inhaltlich**: Die Fassung mit dem jüngeren Änderungszeitpunkt bleibt unter dem Originalnamen, die andere wird umbenannt zu `<name>.sync-conflict-<datum>-<zeit>-<gerätekennung>.<endung>` und als gewöhnliche Datei **auf alle Geräte verteilt**. Beide Fassungen liegen damit überall nebeneinander; nichts geht verloren, aber zusammengeführt hat auch niemand — genau das ist die gewollte Arbeitsteilung (Kern-Invariante in 2.1): Das Werkzeug transportiert, die inhaltliche Entscheidung treffen Nutzer und in diesem Projekt der Nutzer mit Unterstützung von Claude (1.8).

Wie oft das praktisch vorkommt, hängt am Dateimix: Die Sitzungsprotokolle unter `projects/` tragen je Sitzung eindeutige Namen und kollidieren zwischen zwei Rechnern praktisch nie, sofern man auf beiden Rechnern **nicht gleichzeitig im selben Chat** arbeitet. Kandidaten sind die wenigen wirklich geteilten, beidseitig veränderten Dateien — `settings.json`, `CLAUDE.md` und ähnliche. In den ersten Betriebswochen zeigt sich, dass beim Synchronisieren von ~/.claude keine Konflikte zustande kommen. Eine Überwachung mit Hilfe des Dienstes in diesem Projekt ist trotzdem nicht verkehrt: Wenn Anthropic weiter entwickelt können zukünftig vielleicht doch Konflikte dazu kommen, die aktuell (08/2026) noch nicht aufgetreten sind.

Eine bekannte Eigenheit für wachsende Protokolldateien: Es gibt keinen Mechanismus, der die Übertragung zurückstellt, bis eine Datei zur Ruhe kommt. Übertragen wird der Zwischenstand zum Zeitpunkt des Suchlaufs; die Gegenseite erhält dank temporärer Datei plus Umbenennen stets eine technisch vollständige Datei, deren letzte Zeile aber inhaltlich abgeschnitten sein kann. Für reine Anhänge-Protokolle heilt das der nächste Abgleich; ob es in der Praxis stört, klärt der Testplan (3.8).

## 1.6 Konflikterkennung: der Wächter

Konfliktkopien sind bei Syncthing gewöhnliche Dateien mit einem festen Namensbestandteil — **sie lassen sich zuverlässig maschinell finden**, aber niemand meldet sie von sich aus. Genau diese Lücke füllt der **Konflikt-Wächter** (3.1): ein als Dienst laufendes Skript, das den Ordner nach `*.sync-conflict-*` durchsucht (unter Auslassung von `.stversions/`, wo archivierte Altfassungen liegen können).

### Der Abgleich läuft dabei weiter — und das ist Absicht

Naheliegend wäre, bei einem Konfliktfund den Abgleich anzuhalten: Der Zustand ist in dem Moment ja tatsächlich fragwürdig. Dass Dateien unter einer laufenden Anwendung ausgetauscht werden, ist in diesem Entwurf zugemutet und hingenommen — erträglich aber nur unter der Unterstellung, dass die Änderungen von **einer** Seite stammen und der eingehende Stand in sich stimmig ist. Eine Konfliktkopie ist der Beweis, dass genau diese Unterstellung verletzt wurde: Danach liegt eine Mischung vor, die es auf keinem der beteiligten Rechner je gab.

**Trotzdem wird nicht angehalten**, und zwar aus einem Grund, der schwerer wiegt: Das Anhalten würde nicht nur das Entstehen weiterer Konflikte bremsen, sondern **auch die Verteilung der Lösung blockieren** — also genau den Mechanismus abschalten, der das Problem von selbst aufräumt.

Denn die Konfliktkopie ist eine gewöhnliche Datei. Löscht die Sitzung sie und schreibt das Ergebnis ins Original, wandern beide Vorgänge mit: Aktualisierung **und** Löschung. Wer den Konflikt an einem Rechner löst, räumt ihn damit überall auf, ohne dass am anderen Gerät jemand etwas tun müsste. Ist der andere Rechner ausgeschaltet, erfährt er von dem Konflikt sogar nie etwas — er holt sich beim nächsten Start nur das fertige Original.

Prüft man die drei Argumente fürs Anhalten einzeln nach, greifen sie zudem **alle nur dann**, wenn der andere Rechner gerade aktiv mitsynchronisiert:


| Argument fürs Anhalten                    | greift nur, wenn …                            |
| ------------------------------------------ | ---------------------------------------------- |
| Der Mischzustand wird schlimmer            | … von der Gegenseite noch etwas nachkommt     |
| Stabiler Arbeitsgrund während der Lösung | … sich der Bestand überhaupt verändern kann |
| Die Lösung könnte sofort neu kollidieren | … die Gegenseite gleichzeitig schreibt        |

Im vorgesehenen Betrieb wird jedoch wechselweise an **einem** Rechner gearbeitet; der andere ist entweder aus oder rödelt allein vor sich hin. Dann liegt der Nutzen des Anhaltens vollständig brach, während sein Preis voll anfällt: blockierte Verteilung der Lösung, ein Rückstau, der beim Wiedereinschalten auf einen Schlag abzuarbeiten wäre, und die Gefahr, dass eine vergessene Pause den Abgleich unbemerkt dauerhaft stilllegt. Hinzu käme ein Sonderfall, den es sonst gar nicht gibt: Stünde derselbe Konflikt auf zwei angehaltenen Rechnern zur Lösung an, verlangte er dort zweimal eine Entscheidung — und fiele sie unterschiedlich aus, wäre ein neuer Konflikt gebaut.

**Der Wächter greift deshalb überhaupt nicht steuernd ein** (verbindlich in 2.1): Er beobachtet, meldet und eskaliert, mehr nicht.

Anhalten bleibt trotzdem möglich — es ist in Syncthings Oberfläche einen Klick entfernt und muss von diesem Vorhaben nicht nachgebaut werden. Die Arbeitsanweisung gibt der Sitzung deshalb mit, es dem Nutzer **zu empfehlen**, wenn die Lage unübersichtlich wird: viele Konflikte auf einmal, oder erkennbar beide Rechner aktiv mit Dateiänderungen (3.4). Dann ist es eine bewusste Einzelfallentscheidung statt eines Automatismus, der im Regelfall mehr kostet als nützt.

**Remote-Arbeit ändert daran nichts.** Der Wächter läuft unabhängig je Rechner, gebunden an dessen eigene grafische Sitzung (3.5) — nicht an die Sitzung, von der aus gerade gearbeitet wird. Wird über VSCode Remote-SSH auf Rechner A gearbeitet, während man physisch an Rechner B sitzt, zeigt A seinen Dialog nur, wenn A selbst eine aktive grafische Sitzung hat; sonst wartet der Konflikt dort, genau wie bei einem ausgeschalteten Rechner. Es reicht, dass irgendein am Abgleich beteiligter Rechner mit aktiver grafischer Sitzung meldet — das muss nicht der sein, auf dem gerade gearbeitet wird. Sitzt man dagegen an einem Rechner C, der selbst gar nicht am Abgleich teilnimmt, poppt dort nichts auf; die Meldung erscheint erst, wenn wieder an einem tatsächlich synchronisierten Rechner mit aktiver grafischer Sitzung gesessen wird.

**Zwei Wächter, ein Konflikt.** Läuft der Wächter auf beiden Rechnern, meldet ihn jeder für sich — die Kopie liegt ja auf beiden. Gelöst wird an **einem** Rechner (verbindlich in 2.1, Begründung oben); die Auflösung wandert dann als gewöhnlicher Datei- und Löschvorgang zum anderen. Dort verschwindet der Anlass damit von selbst, aber **nicht** der schon offene Dialog: Ein Fenster, das auf Eingabe wartet, weiß nichts davon. Es schließt sich nach fünfzehn Minuten selbst (3.3), und der nächste Durchgang findet nichts mehr und schweigt. Wer den veralteten Dialog vorher noch anklickt, bekommt eine Sitzung, die leer ausgeht und genau das sagt (3.4, Schritt 1) — unnötig, aber harmlos. Was dagegen **nicht** passieren passieren sollte, ist paralleles Lösen an beiden Rechnern durch den Nutzer: Fallen die Entscheidungen unterschiedlich aus, entsteht ein neuer Konflikt.

## 1.6a Mehr als 2 Rechner

<!-- Dieses Kapitel 1.6a ist noch zu 1.7 umzubenennen, alle folgenden Kapitelnummern um 0.1 hoch zu zählen und gleichzeitig alle Verweise in diesem Dokument, die damit auf ein falsches Kapitel weisen würden, zu überarbeiten. -->

Das Verfahren wird hier explizit immer an 2 Rechnern demonstriert. Da jeder Rechner allein für sich arbeitet und nur Syncthing die Daten und damit auch die Konflikte und Konfliktlösungen verteilt, ist es möglich, beliebig viele Rechner auf die gleiche Art untereinander zu synchronisieren, wie hier an zwei Rechnern beschrieben. Dazu ist keinerlei Änderung der Projektdaten hier oder des Wächterdienstes notwendig.

## 1.7 Meldung und Einstieg

Findet der Wächter Konfliktkopien, erscheint ein Zenity-Frage-Dialog: Er nennt die betroffenen Dateien und erklärt vorab, dass sich zur Bearbeitung eine Claude-Code-Sitzung in einem Terminal öffnet und dafür gegebenenfalls ein Terminal-Programm auszuwählen ist. Antworten: „Jetzt lösen" / „Später". Bricht der Nutzer die anschließende Terminal-Auswahl ab, wird nicht stillschweigend ein Terminal gewählt, sondern erneut gefragt — Wiederholung oder Abbruch; bei Abbruch meldet sich die Episode regulär wieder. Diese gesamte Dialogstrecke samt Terminal-Erkennung ist in Vorversuchen erprobt und abgenommen (Belege in 3.8, Einzelheiten in 3.3).

### Stündliche Betriebsmeldung

Ein still funktionierender Hintergrunddienst hat ein Vertrauensproblem: Man sieht ihm nicht an, ob er arbeitet oder seit Tagen klemmt. Deshalb meldet sich der Wächter mit einer knappen Betriebsmeldung, frühestens eine Stunde nach der vorigen — gezeigt wird sie beim ersten Durchgang danach, also bis zu eine Viertelstunde später, denn die Meldung hat keinen eigenen Takt (3.1). Sie sieht dann so aus: „abgeglichen: 0.8 MB hoch, 0.3 MB herunter; kein Konflikt seit 74 Stunde(n)".

**Stehen Konflikte offen, tritt an die Stelle der Statistik ein deutlicher Hinweis darauf** — „3 Konflikt(e) seit 9 Stunde(n) ungelöst". Damit gerät eine vertagte Lösung nicht in Vergessenheit. Den Dialog ersetzt die Meldung aber nicht: Solange Konfliktkopien liegen bleiben, erscheint der Konflikt-Dialog nach einer Vertagung frühestens nach dreißig Minuten erneut (2.9); die Meldung ist die leise Erinnerung dazwischen, nicht ihr Ersatz.

Hat der Nutzer den Abgleich von Hand angehalten (etwa auf Empfehlung der Sitzung, 1.6), gehört auch das in die Meldung — eine vergessene, selbst gesetzte Pause legt den Abgleich sonst unbemerkt still. Der Wächter erkennt sie am `paused`-Feld, das er ohnehin liest; er verändert es nicht (2.1).

Dafür ist bewusst **keine** Zenity-Meldung vorgesehen, sondern eine gewöhnliche Desktop-Benachrichtigung (`notify-send`) — das kurze Einblenden im Benachrichtigungsbereich. Der Grund, aus dem sie für die Konflikteskalation verworfen wurde, greift hier nicht: Dort musste die Meldung zuverlässig **anklickbar** sein, was je nach Benachrichtigungsdienst nicht zugesichert ist; eine reine Betriebsanzeige will niemand anklicken. Umgekehrt wäre ein Zenity-Fenster für eine stündliche Belanglosigkeit zu aufdringlich (verbindliche Abgrenzung in 2.9).

Die Zahlen holt der Wächter aus Syncthings lokaler REST-Schnittstelle (Einzelheiten in 3.1). Bleibt sie unerreichbar, entfällt die Meldung stillschweigend — sie ist Beiwerk, kein Betriebsmittel. Mit **einer** Ausnahme, die den Charakter der Meldung genau bestimmt: Stehen Konflikte offen, erscheint der Hinweis darauf auch dann, wenn die Schnittstelle nichts liefert. Beiwerk sind die Zahlen, nicht die Eskalation.

**Inhalt und Anzeigedauer** (Entscheidung zu F10). Gemeldet werden die je Richtung übertragenen Bytes als Lebenszeichen und, wenn vorhanden, der **Rückstand** — wie viele Dateien noch auf Übertragung warten. Der Rückstand ist die eigentliche Warnung: „Rückstand: 7 Datei(en)" heißt, dass etwas klemmt, und davon erfährt man sonst nie etwas. Die Zahl übertragener Dateien wird bewusst **nicht** gemeldet; sie sagt neben den Bytes nichts Neues.

Die Bytes wechseln die Einheit schon bei einem Zehntel der nächsten: über 0,1 kB in kB, über 0,1 MB in MB. Dadurch bleibt die Zahl kurz und auf einen Blick lesbar — um den Preis, dass 500 kB als „0.5 MB" erscheinen. Das ist gewollt: Die Meldung soll eine Größenordnung zeigen, nicht eine Messung.

**Die Anzeigedauer richtet sich nach dem Inhalt**, und das ist die eigentliche Festlegung: Eine gute Nachricht darf kurz sein — wenige Sekunden, denn „alles in Ordnung" ist mit einem Blick erfasst, und genau darin liegt ihr Wert als Lebenszeichen. Alles, was Aufmerksamkeit verlangt, bleibt zwölf Sekunden stehen: offene Konflikte, ein Rückstand, eine von Hand angehaltene Freigabe, oder gar keine Verbindung zum Abgleich. **Vorbehalt:** Ob die gewünschte Dauer eingehalten wird, entscheidet der Benachrichtigungsdienst des Desktops — Plasma befolgt sie, GNOME Shell übergeht sie.

<!-- Auch in den folgenden zwei Absätzen mit dem Code prüfen. Es gilt, was der Code sagt. -->

**Keine Verbindung** erhält keinen eigenen Meldungsweg, sondern dieselbe Meldung mit klarem Vorspann („keine Verbindung zum Abgleich seit …"). Ein zweiter Kanal wäre ein zweiter Ort, an dem etwas veralten kann.

**Und eine Frist wird nur genannt, wenn sie stimmt.** Fehlt der Bezugspunkt, steht „Zählung neu begonnen" statt einer Stundenzahl. Dieser Satz deckt zwei Lagen gleichzeitig: eine verlorene Zustandsdatei (3.2) und eine frische Installation, die noch nie einen Konflikt gesehen hat. Von außen sind beide nicht unterscheidbar, und für beide ist er wahr — eine erfundene Null wäre für beide falsch.

Stündlich bleibt es. Geht alles gut, ist die Meldung nur kurz zu sehen und sagt sinngemäß genau eines: Der Wächter lebt.

## 1.8 Die Konfliktsitzung

**Die Konfliktlösung mit Claude statt einem Diff-Tool** durchzuführen, soll die Konfliktlösung transparenter machen, da der Nutzer unmittelbar mit dem Wissen von Claude und dessen Tools, insbesondere der Internetrecherche, eine für ihn unklare Konfliktsituation leichter erforschen kann.

Entscheidet sich der Nutzer für „Jetzt lösen", öffnet sich ein Terminal, darin startet `claude` mit Arbeitsverzeichnis `~/.claude` — das Arbeitsverzeichnis kommt zwingend vom aufrufenden Prozess, einen Startschalter dafür kennt Claude Code nicht. **Die Claude Code Sitzung nutzt automatisch das auf dem Rechner angemeldete Konto.**

Die Sitzung bekommt **alle zu diesem Zeitpunkt anstehenden Konfliktpaare auf einmal** übergeben und arbeitet sie in einem Zug ab — nicht eines je Dialog.

Der Abgleich läuft dabei weiter (1.6). Im vorgesehenen Betrieb kommt während der Arbeit nichts hinzu, weil am anderen Rechner niemand sitzt; sollte doch etwas eintreffen, nimmt die Sitzung es in dieselbe Runde auf und empfiehlt bei unübersichtlicher Lage, von Hand anzuhalten (3.4).

Die Prüfung und die Darstellung der Konflikte übernimmt Claude selbständig, ohne ihm ein konkretes Diff-Tool zur Verfügung zu stellen. Die automatisch mit übergebenen Arbeitsanweisungen (`konfliktloesung.md`) enthalten eine ausführliche Beschreibung, wie Claude Code vorzugehen hat.

**Gelöst wird immer nur an einem Rechner.** Löschung der Konfliktkopie und Aktualisierung des Originals wandern als gewöhnliche Dateisynchronisationsvorgänge mit — wer hier löst, räumt damit überall auf. Ein eingeschalteter zweiter Rechner sieht seine Kopien von selbst verschwinden, ein ausgeschalteter erfährt von dem Konflikt nie etwas.

Die Sitzung folgt einer mitgegebenen schriftlichen Arbeitsanweisung (3.4) und geht die Konfliktpaare **nacheinander gemeinsam mit dem Nutzer** durch. Je Paar liegen Original (die im Abgleich siegreiche Fassung) und Konfliktkopie (die unterlegene) als zwei gewöhnliche Dateien nebeneinander — die Sitzung vergleicht sie, erklärt den Unterschied und holt die Entscheidung ein: **Original behalten** (Konfliktkopie löschen), **Kopie übernehmen** (deren Inhalt ins Original schreiben, Kopie löschen) oder **zusammenfügen** (neue Fassung ins Original, Kopie löschen). Es gibt kein Einbuchen und keinen Commit: Schreiben und Löschen genügen, Syncthing verteilt beides von selbst an alle Geräte.

Ergibt die Lösung, dass eine Datei künftig gar nicht mehr abgeglichen werden soll, gehört die Anpassung der Ausschlussliste in `.stignore` dazu — und zwar auf **jedem** Gerät, da diese Syncthing-eigene Datei nie beim Synchronisieren mitwandert (2.3).

Zwei Regeln binden die Sitzung unbedingt (2.2): Keine Datei wird überschrieben und keine Konfliktkopie gelöscht ohne ausdrückliche Zustimmung des Nutzers zur konkreten Entscheidung; und am Ende berichtet die Sitzung, welche Paare es gab, wie je Paar entschieden wurde und was geschrieben oder gelöscht wurde.

## 1.9 Betriebsrahmen, Versionierung und Notfall-Rückgriff

Auf den Rechnern läuft Syncthing als systemd-**Benutzerdienst** (im Falle von Linux), der Wächter ebenfalls als Benutzerdienst, dauerhaft und ereignisgesteuert (3.5). Der Wächter braucht die grafische Sitzung, weil er Dialoge zeigt. Auf der Synology läuft das Paket als Dienst des DSM.

**Was das beim Abmelden bedeutet** — am eingerichteten System geprüft, weil es die Reichweite des ganzen Mechanismus bestimmt: `Linger` ist für den Benutzer **nicht** eingeschaltet, also endet mit der letzten Sitzung des Benutzers auch dessen Benutzerdienst-Verwaltung — und damit **Syncthing selbst**, nicht nur der Wächter. Ein abgemeldeter Rechner gleicht nichts ab, empfängt nichts und ändert nichts. Änderungen des anderen Rechners warten auf der Synology, bis wieder angemeldet wird; dann startet Syncthing, holt sie, und der Suchlauf beim Start des Wächters findet, was dabei an Konfliktkopien entstanden ist.

Daraus folgt die **eine** Lage, in der Konfliktkopien unbemerkt entstehen können: eine Anmeldung **ohne** grafische Sitzung, etwa über SSH oder eine Konsole. Dann läuft die Benutzerdienst-Verwaltung und mit ihr Syncthing, aber `graphical-session.target` fehlt und damit der Wächter (3.5). Kopien können also eintreffen, ohne dass jemand gefragt wird. Verloren geht dabei nichts: Der Suchlauf beim nächsten Start des Wächters, also bei der nächsten grafischen Anmeldung, holt sie nach. Es ist der bewusst getragene Rest, der bleibt, wenn man Dialoge an einen Bildschirm bindet.

Die **Dateiversionierung** ist eingeschaltet und dient in diesem Vorhaben genau einem Zweck: dem Notfall-Rückgriff. Sie archiviert eintreffende Fremdänderungen vor dem Überschreiben — wohlgemerkt nur auf dem *empfangenden* Gerät; lokale Änderungen archiviert Syncthing prinzipbedingt nicht. Der wirksamste Aufbewahrungsort ist damit die Synology, die von allen Rechnern empfängt.

**Festlegung:** Auf der Synology „Staggered" mit einer Höchstdauer nach Bedarf — sie empfängt von allen Rechnern und ist damit der ergiebigste Ort für einen Rückgriff. Auf den Arbeitsrechnern genügt „Trash Can" oder „Simple"; beides ist zweckmäßig, „Simple" behält mehrere Fassungen je Datei, „Trash Can" nur die zuletzt ersetzte. Auf Rechner A ist derzeit „Simple" gesetzt.

**Notfall-Rückgriff**. Der Rückgriff ist ein Eingeständnis, dass das Verfahren versagt hat — er gehört protokolliert und ins Projekt zurückgespielt, nicht stillschweigend wiederholt.

**Woran der Notfall zu erkennen ist:** Claude Code startet nicht mehr, verlangt eine erneute Anmeldung, findet ein Projekt nicht mehr, oder eine Einstellung ist verschwunden. Wobei hier natürlich auch andere Gründe als die Synchronisation vorliegen können! **Kein** Notfall ist eine inhaltlich unschön aufgelöste Datei — die wird normal nachgearbeitet. Die Unterscheidung ist wichtig, weil der Rückgriff selbst Schaden anrichten kann.

**Der typische Notfall-Ablauf des Nutzers**, und die Reihenfolge ist der eigentliche Inhalt der Festlegung:

1. **Alle Claude-Sitzungen ordentlich schließen** (`/exit`), die im Terminal wie die in VSCode. Die Sitzungen auf dem **anderen** Rechner erst dann, wenn das Schließen hier nichts gebracht hat — sonst wird ohne Not in einen laufenden Arbeitsplatz eingegriffen.
2. **Hängengebliebene Prozesse beenden:** `sudo pkill claude` (`pkill -u $USER claude` genügt, da es eigene Prozesse sind). Der Wächter läuft als `python3` und ist davon nicht betroffen; er muss es auch nicht sein, er beobachtet nur.
3. **Sitzung neu öffnen.** Läuft sie wieder, ist hier Schluss: **kein Notfall**, nichts zurückholen. Offenbar lag ein anderes Problem vor, das nichts mit der Synchronisation zu tun hat.
4. Erst wenn es weiter kaputt ist: **Sicherung anlegen**, `cp -a ~/.claude ~/.claude.kaputt-<Datum>`.
5. **Abgleich pausieren**, nur für den Ordner `~/.claude`, in Syncthings Oberfläche.
6. **Einzelne Dateien** zurückholen — zuerst lokal aus `~/.claude/.stversions/`, als Rückfall der „Staggered"-Bestand auf der Synology.
7. **Prüfen, und zwar auf beiden Rechnern.** Möglicherweise ist auf einer oder auf beiden Seiten eine erneute Claude-Anmeldung nötig. Erst wenn beide Seiten laufen: **Abgleich wieder einschalten.**
8. **Sicherung aus Punkt 4 aufbewahren**, bis geklärt ist, was schiefging — sie ist die einzige Quelle dafür.

Warum die Schritte 1 bis 3 vor allem anderen stehen: Eine laufende Claude-Instanz hält ihren Stand im Speicher und schreibt beim Beenden Dateien zurück. War während einer Auflösung eine Sitzung offen, kann sie die Lösung unbemerkt überschrieben haben — dann ist nicht der Bestand kaputt, sondern nur überschrieben, und ein Rückgriff aus `.stversions` würde bei laufender Sitzung gleich wieder zunichte gemacht. Erst die Sitzungen beenden, dann urteilen. Die Sicherung steht vor dem Pausieren, weil Pausieren nur die Weiterverbreitung aufhält: Wer beim Zurückholen daneben greift, hat ohne Sicherung auch den kaputten Stand verloren — und der ist die einzige Quelle, um zu verstehen, was geschah.

## 1.10 Rechner B erstmalig anschließen

Rechner B trägt ein eigenständig gewachsenes `~/.claude`, das nicht überschrieben werden darf. In ihm sind alle Chats aufbewahrt, die zu den lokalen Projekten odere Claude Desktop geführt wurden.

### Anbindung eines Rechners im normalen Betrieb

Hier ist nur die nachfolgend als Phase 2 beschriebene Vorgehensweise anzuwenden.

### Testphase während Evaluierung / Tests dieses Projekts

Die Anbindung eines 2. Rechners während der Erstellung dieses Projekts geschieht in zwei Phasen (Verfahren in 3.6):

**Phase 1 — Hilfsordner:** B wird mit der Synology gekoppelt und synchronisiert zunächst ausschließlich einen eigenen Testordner. Daran läuft der komplette Testplan (3.8): einseitige Änderungen, Vermittlung bei abwechselndem Betrieb, absichtliche Konflikte, Ausschlussmuster, Zeitverhalten, Erstverbindung nicht-leerer Ordner. `~/.claude` auf B bleibt so lange unangetastet.

**Phase 2 — echter Bestand:** Erst wenn Phase 1 bestanden ist und der Watcher-Dienst läuft: 1) Sicherung des B-Standes, 2) `.stignore` auf B anlegen (vor der Verbindung!), 3) dann den Ordner mit Syncthing auf dem Server (hier eine Synology) teilen. **Beim Erstabgleich zweier nicht-leerer Bestände vereinigt Syncthing auf Dateiebene: Was nur auf einer Seite existiert, wird verteilt; was auf beiden Seiten existiert und sich unterscheidet, erzeugt Konfliktkopien**. Die anschließende, vermutlich umfangreiche Konfliktlösung ist keine Störung, sondern der geplante Zusammenführungsschritt — geführt durch dieselbe Sitzung wie im Regelbetrieb (1.8).

## 1.11 Windows-Ausblick

Zurückgestellt, bis der Betrieb auf Linux-Rechnern eindeutig stabil und Konfliktfrei oder -arm läuft. Die Grundlage ist günstig: Syncthing läuft nativ unter Windows, Claude Code legt seinen Zustand strukturell identisch unter `%USERPROFILE%\.claude` ab, und die Zugangsdaten liegen dort ebenso als Klartextdatei — der Ausschluss aus 2.3 gilt unverändert. Anzupassen sind allein die gekapselten Bausteine des Wächters: Dialoge (statt Zenity), Terminalstart (statt X11-Terminal-Erkennung), Zeitsteuerung (Aufgabenplanung statt systemd). Einzelheiten in 3.7.

---

# 2 Vorgaben

## 2.1 Keine selbsttätige Zusammenführung

Kein Werkzeug dieses Vorhabens führt beidseitig geänderte Dateien selbsttätig inhaltlich zusammen, und keine Einstellung darf Syncthings Konfliktkopie-Mechanismus unterlaufen. Inhaltliche Entscheidungen über kollidierende Fassungen treffen ausschließlich Nutzer und Claude gemeinsam in der Konfliktsitzung. Verletzt ist diese Vorgabe durch jeden automatischen Merge-Schritt im Abgleichweg, durch `maxConflicts = 0` (schaltet Konfliktkopien ab) und durch den Ordnertyp „Receive Only" auf einem der Geräte (unterdrückt die Verteilung der Konfliktkopien) — alle Geräte bleiben auf „Send & Receive".

**Der Wächter greift nicht steuernd in Syncthing ein.** Er liest über die REST-Schnittstelle (Zustand, Zahlen für die Betriebsmeldung), schreibt dort aber nichts — insbesondere hält er den Abgleich nicht an und nimmt eine bestehende Pause nicht zurück. Begründung in 1.6: Ein Anhalten blockierte auch die Verteilung der Lösung und schüfe den Sonderfall desselben Konflikts auf zwei angehaltenen Rechnern. Anhalten bleibt eine bewusste Handlung des Nutzers in Syncthings Oberfläche. Verletzt ist diese Vorgabe durch jede schreibende Operation des Wächters über die REST-Schnittstelle.

## 2.2 Führungsprinzip und Zustimmungspflichten

Der Abgleich läuft vollständig werkzeuggesteuert; Claude wird ausschließlich zur Konfliktlösung hinzugezogen. Die Konfliktsitzung überschreibt keine Datei und löscht keine Konfliktkopie ohne ausdrückliche Zustimmung des Nutzers zur konkreten Entscheidung; die Zustimmung zum Öffnen der Sitzung („Jetzt lösen") ist keine Zustimmung zu irgendeiner Auflösung.

Für den Alltagsbetrieb gelten zwei Verhaltensregeln: Syncthing läuft vor der schreibenden Anwendung (nach dem Einschalten erst ankommen lassen, dann arbeiten), und ein Rechner wird nicht ausgeschaltet, solange der Abgleich sichtbar offen ist.

Für die Erkennungseinstellungen gilt: Dateisystem-Überwachung **an**, vollständiger Suchlauf **an**, beide Vorgabewerte unverändert (Begründung in 1.4). Verletzt ist diese Vorgabe insbesondere durch ein Abschalten des vollständigen Suchlaufs — er ist nicht redundant, sondern fängt verpasste Ereignisse auf — und durch ein Absenken der Sammelfrist, das bei wachsenden Protokolldateien nur die Zahl unfertig übertragener Zwischenstände erhöht.

## 2.3 Sicherheitsausschlüsse

Die Datei `.credentials.json` wird niemals synchronisiert; `telemetry/` und `cache/` ebenfalls nicht. Durchgesetzt wird das über die lokale `.stignore` **jedes** Geräts, deren Einträge wörtlich vorhanden sein müssen, **bevor** der Ordner dort erstmals verbunden wird — die Datei wandert nicht mit, und der `#include`-Umweg ist für Zugangsdaten untauglich, weil die eingebundene Datei ein neues Gerät erst durch den Abgleich erreicht. Nach jeder Änderung an den Mustern und bei jeder Neuanbindung ist die Wirksamkeit zu prüfen (3.8). Verletzt ist diese Vorgabe durch jedes Gerät, das ohne diese Einträge verbunden wird, und durch jedes Werkzeug, das Zugangsdaten kopiert.

## 2.4 Plattformstrategie und Kapselung

Der Wächter ist eine einzige Codebasis in Python für Linux und Windows: Pfade über `pathlib`, externe Programme über `subprocess`. Alles Plattformspezifische — Dialogwerkzeug, Terminalstart, Zeitsteuerung — liegt hinter einer gemeinsamen, austauschbaren Stelle im Code, nicht verstreut in Ad-hoc-Verzweigungen. Verletzt durch jede Betriebssystem-Abfrage außerhalb der Kapselstelle und jede parallele Zweitimplementierung.

## 2.5 Code- und Skriptkonventionen

Jedes Skript trägt einen Kopfkommentar, der seine Nutzung beschreibt. Skripte und Anweisungsdateien, die von Claude gelesen oder ausgeführt werden sollen, tragen zusätzlich einen eigenen `@Claude:`-Abschnitt: wie zu benutzen, was beim Nutzer nachzufragen ist, was anschließend zu berichten ist. Bezeichner, Kommentare und Kopfkommentare sind englisch; die Dokumentation des Vorhabens ist deutsch. Verletzt durch jedes Skript ohne Kopfkommentar, jedes claude-gerichtete Artefakt ohne `@Claude:`-Abschnitt und jede Sprachmischung.

## 2.6 Ausgabedisziplin

Der Wächter berichtet im Dienstbetrieb knapp: **eine** Zeile je Durchgang, der etwas gefunden hat (Anlass, Anzahl, Ordner). Ein leerer Befund schweigt, sonst füllt der Sicherheits-Suchlauf das Journal mit „nichts" (3.5). Befunde führen zu Dialogen nach 2.9, nicht zu Konsolenzeilen. Fehler und Ausnahmen werden **immer** ausgegeben, damit sie im systemd-Journal sichtbar bleiben — auch die Meldung eines Dialogs, der nicht gezeigt werden konnte (3.3). Verletzt durch Gesprächigkeit bei leerem Befund und durch verschluckte Fehler.

Sichtbar wird der Wächter gegenüber dem Nutzer damit an genau zwei Stellen: dem Konfliktdialog und der stündlichen Betriebsmeldung (1.7). Beides sind bewusst gesetzte Meldungen, keine Nebenwirkungen — jede weitere Sichtbarkeit ist zu begründen oder zu unterlassen.

## 2.7 Ablageorte

Alles, was dieses Vorhaben mitbringt, liegt in **einem** Ordner: `~/.claude-sync-watch/`.

```
~/.claude-sync-watch/
├── claude_sync_watchd.py     Dienst (3.1) — das „d" für Daemon
├── claude-sync-watch.service Vorlage der Dienstdefinition (3.5)
├── install_service.sh        richtet den Dienst ein (3.5)
├── uninstall_service.sh      meldet den Dienst wieder ab (3.5)
├── konfliktloesung.md        Arbeitsanweisung (3.4)
├── .stignore                 maßgebliche Ausschlussliste (2.8)
├── werkzeuge/                per --add-dir freigegebenes Verzeichnis, vorerst leer
└── zustand.json              Merker (3.2)
```

Bewusst **nicht** aufgeteilt über `~/.local/bin`, `~/.local/share` und `~/.local/state`: Das ist die Ablage für Systempakete; ein persönliches Hilfsmittel aus vier Dateien wird dort im Ernstfall nicht gesucht. Auffindbarkeit geht hier vor Konvention.

**Im Repo liegen dieselben Dateien unter `home-.claude-sharing/files/`** — genau der Satz, der auf einem Zielrechner nach `~/.claude-sync-watch/` gehört, versioniert an einer Stelle. Nicht dabei ist `zustand.json`: die entsteht erst zur Laufzeit und ist Merker, kein Bestandteil des Werkzeugs.

**Der Ort auf dem Zielrechner ist Vorschrift, nicht Empfehlung.** Die Unit verweist fest auf `%h/.claude-sync-watch/`, und `install_service.sh` ermittelt den Ordner, in dem es selbst liegt — unabhängig vom Aufrufverzeichnis —, vergleicht ihn mit `$HOME/.claude-sync-watch` und bricht sonst mit Verschiebeanweisung ab. Damit bleibt die Unit eine statische Datei ohne Pfadersetzung (Begründung in 3.5). Für Testläufe kann der Wächter seinen eigenen Ordner per `--tool-dir` verlegen; das ist ausschließlich dafür da, damit eine Erprobung keine echte Installation berührt.

Der Ordner liegt **neben** `~/.claude`, nicht darin — was den Abgleich betreibt, darf nicht selbst Gegenstand des Abgleichs sein. In `~/.claude` liegt außer dem Synchronisationsgut nur, was Syncthing dort verlangt (`.stignore`, `.stfolder`).

Verletzt ist diese Vorgabe durch jedes Werkzeug und jede Merkerdatei innerhalb von `~/.claude` und durch jede Ablage außerhalb von `~/.claude-sync-watch/`.

## 2.8 Gleichheit der Rechner

Der Mechanismus wird auf jedem beteiligten Rechner identisch eingerichtet: gleiches Wächter-Skript, gleiche Ablageorte, gleiche Dienstdefinition, inhaltsgleiche `.stignore`. Rechnerspezifisch sind allein die Claude-Anmeldung, die Geräte-ID und der zwischengespeicherte Terminal-Befehl. Verletzt durch jede Sonderkonfiguration, die einen Rechner anders behandelt. **Offen** (Anhang F8): wie die Inhaltsgleichheit der `.stignore` über die Zeit gesichert wird.

**Die Ausschlussliste hat eine maßgebliche Fassung** (Entscheidung zu F8). `.stignore` wandert nicht mit dem Abgleich; Abweichungen zwischen den Rechnern fallen deshalb nie von selbst auf, und die gefährliche Richtung ist eindeutig — fehlt auf einem Rechner die Zeile für die Zugangsdaten, wandern sie von dort aus los. Verbindlich gilt daher: Die Fassung im Werkzeugordner (`~/.claude-sync-watch/.stignore`) ist maßgeblich, sie liegt versioniert im Repo unter `files/`, und die wirksame Datei `~/.claude/.stignore` wird von dort kopiert — nicht umgekehrt gepflegt.

Erzwingen lässt sich das nicht, prüfen schon: `install_service.sh` vergleicht beide Fassungen und zeigt den Unterschied samt Kopierbefehl an. Absichtlich nur eine **Warnung** und kein Abbruch — eine abweichende Ausschlussliste ist ein Mangel, aber kein Grund, den Wächter nicht einzurichten; ohne Wächter wäre man schlechter dran. Fehlt die wirksame Datei ganz, ist die Warnung entsprechend deutlicher, denn dann ist gar nichts ausgeschlossen. Eine laufende Überwachung der Gleichheit ist bewusst **nicht** vorgesehen: Der Wächter sieht die Datei des anderen Rechners nicht und könnte nur die eigene mit der Vorlage vergleichen — das leistet die Installationsprüfung schon, und ein zweiter Ort für dieselbe Prüfung wäre die Art Redundanz, die auseinanderläuft.

## 2.9 Regeln für die grafische Interaktion

**Für alles, was eine Entscheidung des Nutzers verlangt, werden Zenity-Dialoge verwendet, niemals Desktop-Benachrichtigungen** — deren Anklickbarkeit hängt vom Benachrichtigungsdienst ab und ist nicht zugesichert; eine übersehene oder nicht anklickbare Konfliktmeldung wäre ein stiller Ausfall der Eskalation. **Für reine Betriebsanzeigen ohne Handlungsbedarf gilt das Umgekehrte:** Dort ist `notify-send` das Mittel der Wahl (stündliche Betriebsmeldung, 1.7), weil ein modaler Dialog für eine Belanglosigkeit unangemessen aufdringlich wäre. Trennlinie ist also nicht das Werkzeug, sondern die Frage, ob eine Reaktion nötig ist.

Der Konflikt-Dialog erscheint einmal je Konflikt-Episode und nach Vertagung frühestens nach dreißig Minuten erneut; das Verschwinden aller Konfliktkopien beendet die Episode. Ein Dialog-Abbruch führt nie zu einer stillschweigenden Ersatzentscheidung — insbesondere wählt ein abgebrochener Auswahldialog niemals heimlich den ersten Kandidaten, sondern führt zur Rückfrage (3.3). Zenity-Meldungen auf dem Fehlerkanal über das Erscheinungsbild (GTK-Warnungen) sind kosmetisch und dürfen nicht als Fehlerkennzeichen ausgewertet werden. Verletzt durch `notify-send`, Dialoge außerhalb der Episodenregel, stille Ersatzwahlen und Fehlerauswertung anhand des GTK-Rauschens.

---

# 3 Einheiten

## 3.1 Konflikt-Wächter

Das einzige neu zu bauende Kernstück: `~/.claude-sync-watch/claude_sync_watchd.py` (Ablage nach 2.7). Er läuft als **dauerhafter Dienst** und wird vom Betriebssystem über Dateiänderungen benachrichtigt, statt in festen Abständen nachzusehen.

### Warum ereignisgesteuert und ohne Verzögerung

Je früher der Nutzer von einem Konflikt erfährt, desto eher kann er ihn lösen — und desto geringer die Wahrscheinlichkeit, dass er sich beim Weiterarbeiten mit weiteren überlagert. Eine künstliche Sammelfrist würde das ohne Gegenwert verzögern.

Eine Entprellung wäre nötig, wenn ein Konfliktname auch als Zwischenzustand auftreten könnte — und das tut er. Eingehende Übertragungen schreibt Syncthing in eigene Zwischendateien (`.syncthing.<name>.tmp`, unter Windows `~syncthing~…`) und schiebt sie erst nach vollständigem Empfang an ihren Platz. Dieser Zwischenname **enthält den Zielnamen**: Kommt eine Konfliktkopie an — und sie kommt an, weil Kopien auf alle Geräte wandern (1.6) —, dann steckt `.sync-conflict-…` mitten in einem Zwischennamen. Das ist nicht die Ausnahme, sondern auf jedem Gerät außer dem, wo der Konflikt auffiel, der Regelfall.

Gelöst wird das **nicht** über eine Wartezeit, sondern am Namen: Der Suchlauf lässt aus, was mit `.syncthing.` oder `~syncthing~` beginnt und auf `.tmp` endet. Damit bleibt die Aussage, auf die es ankommt, gültig — ein Name, der den Filter passiert, ist stets ein fertiger Befund und kein Zwischenstand —, aber sie ruht jetzt auf dem Filter statt auf einer falschen Annahme. Ohne ihn meldete der Wächter ein Paar, dessen Original es nie gegeben hat (gemessen, 3.8). Dass wiederholte Ereignisse nicht wiederholt Runden auslösen, stellt weiterhin der Episoden-Merker sicher (3.2), nicht eine Wartezeit.

**Auf beide Entstehungswege ist zu achten:** lokal entsteht die Kopie durch *Umbenennen*, auf den übrigen Geräten dadurch, dass sie als gewöhnliche Datei ankommt und aus der Zwischendatei *hereingeschoben* wird. Der Wächter muss deshalb sowohl auf Anlegen als auch auf Hereinschieben reagieren.

**Und auf das Verschwinden.** Eine Kopie, die gelöscht wird, beendet die Episode (3.2) — im Mehrrechnerbetrieb ist das der Regelfall, weil die Auflösung von einem anderen Gerät hereinwandert (1.6) und nicht durch eine Sitzung auf diesem Rechner geschieht. Ohne das Löschereignis würde der Merker bis zum nächsten Sicherheits-Suchlauf auf „offen" stehen bleiben, also bis zu fünfzehn Minuten, und die stündliche Betriebsmeldung könnte in dieser Zeit einen längst gelösten Konflikt als ungelöst ausweisen. Der Wächter reagiert daher auf **drei** Ereignisarten: Anlegen, Verschieben, Löschen.

**Der Preis der rekursiven Beobachtung**, gemessen im Betrieb und hier festgehalten, damit die Zahl später niemanden erschreckt: Der Suchlauf selbst ist mit rund zwei Millisekunden über 868 Dateien belanglos, und Durchgänge werden ohnehin nur angestoßen, wenn der Ereignispfad den Marker enthält. Rechenzeit kostet das **Durchreichen** der übrigen Ereignisse: Claude Code schreibt fortlaufend in `~/.claude`, alle Verzeichnisse darunter werden rekursiv beobachtet, und jedes einzelne Ereignis läuft durch Python, auch wenn es sofort verworfen wird. In einer knapp zweistündigen Sitzung waren das rund 47 Sekunden CPU-Zeit, im Mittel 0,8 Prozent eines Kerns, bei 17 MB Speicher. Das ist kein Defekt, sondern der Preis dieser Bauart; die Zahl wächst mit der Schreiblast im Ordner, nicht mit der Zahl der Konflikte. Wer sie eines Tages senken muss, hat nur einen wirksamen Hebel: weniger Verzeichnisse beobachten, also mehr aus dem Abgleich ausschließen (2.3).

### Ablauf

Ausgelöst wird ein Durchgang durch ein Dateiereignis, durch den Sicherheits-Suchlauf oder durch den Start des Dienstes:

1. **Suchen.** Den abgeglichenen Ordner rekursiv nach Dateien mit dem Namensbestandteil `.sync-conflict-` durchsuchen. Ausgelassen werden `.stversions/` (archivierte Altfassungen) und `.stfolder/`. Das Suchmuster stützt sich bewusst nur auf den dokumentierten, festen Literalteil — das genaue Format von Datum, Zeit und Gerätekennung im Namen ist nicht zugesichert.
2. **Zuordnen.** Jede gefundene Kopie ihrem Original zuordnen (Namensableitung). Ein Original kann mehrere Kopien haben (`maxConflicts`-Vorgabe: 10 je Datei — bleibt unverändert, keinesfalls 0, siehe 2.1). Der Namensbestandteil `<modifiedBy>` wird mitgeführt und in Dialog und Übergabe als **Gerätekennung** genannt, ohne Richtungsaussage: Er gehört einem der beiden beteiligten Geräte, seine Rolle ist nicht verlässlich ableitbar. Zwei Gründe, jeder allein hinreichend. Erstens entscheidet Syncthing anhand der Änderungszeit, welche Fassung Original bleibt (bei Gleichstand anhand der größeren Gerätekennung) — der Ausgang ist beliebig und beim nächsten Mal womöglich umgekehrt. Zweitens wird der Name genau **einmal** gebildet, dort wo der Konflikt auffiel, und die Kopie wandert danach als gewöhnliche Datei auf alle Geräte (1.6): Auf dem einen Rechner steht darin die fremde Kennung, auf dem anderen die eigene, bei bitgleichem Inhalt beider Dateien. Eine Prüfung „ist das meine Kennung?" wäre deshalb auf einem der beiden Rechner regelmäßig falsch. Die Zuordnung, welche Fassung von welchem Rechner stammt, kommt daher nicht aus dem Namen, sondern aus Inhalt und Änderungszeit — oder aus einer Frage an den Nutzer (3.4).

   Anzumerken ist ein Widerspruch (§1.10): Syncthings eigene Dokumentation nennt `<modifiedBy>` „the device ID of the device that modified the file being renamed", also den Verlierer. Die Messung am echten Konflikt widerlegt das (3.8), und der Quellcode stützt die Messung — `moveForConflict(name, file.ModifiedBy.String(), …)` wird mit der **eingehenden**, siegreichen Fassung aufgerufen, umbenannt wird die lokale (`lib/model/folder_sendrecv.go`). Aufgelöst wird der Widerspruch hier nicht, sondern umgangen: Die Umsetzung verlässt sich auf keine der beiden Lesarten.
3. **Laufende Sitzung erkennen.** Steht in der Zustandsdatei die PID einer gestarteten Sitzung und existiert dieser Prozess noch, wird **kein** Dialog gezeigt — der Nutzer arbeitet gerade. Erprobt: `konsole` hält den gestarteten Prozess offen, die PID taugt damit als Signal. Manche Emulatoren (`gnome-terminal`) reichen den Auftrag jedoch an einen Server weiter und beenden sich sofort; dort ist die PID sofort tot. Deshalb gilt zusätzlich eine Zeitspanne von dreißig Minuten ab Start als Ruhezeit. Wo die PID trägt, ist die Erkennung exakt; wo nicht, verhält sich der Wächter wie ohne sie — ein Dialog kann dann früher wiederkehren, aber die Eskalation geht nie verloren.
4. **Episode führen und eskalieren.** Kein Fund: Episode beenden (3.2). Fund und Dialog nach der Episodenregel aus 2.9 fällig: Dialogstrecke aus 3.3 anstoßen; bei „Jetzt lösen" die Konfliktsitzung starten, ihr **alle** derzeit anstehenden Paare übergeben und die PID des gestarteten Prozesses vermerken.
5. **Betriebsmeldung.** Ist sie fällig, zusammenstellen und zeigen — bei offenen Konflikten als Hinweis darauf statt als Statistik (1.7).

Der Wächter greift dabei zu keinem Zeitpunkt steuernd ein (2.1): Er hält den Abgleich nicht an und nimmt eine vom Nutzer gesetzte Pause nicht zurück. Verschwinden die Konfliktkopien — weil sie hier gelöst wurden oder weil die andernorts hergestellte Lösung eingetroffen ist —, endet die Episode von selbst; die zweite Möglichkeit ist der Regelfall, wenn an einem anderen Rechner gelöst wurde (1.6).

### Auslöser und Sicherheitsnetze

Beobachtet wird über die Dateiänderungs-Schnittstelle des Betriebssystems (unter Linux inotify, unter Windows `ReadDirectoryChangesW`). Als Kapselung dafür ist `watchdog` vorgesehen — sie bedient beide Systeme über dieselbe Schnittstelle und entspricht damit 2.4; als Distributionspaket verfügbar. Die Beobachtungsgrenzen sind unkritisch: `~/.claude` umfasst derzeit 49 Verzeichnisse bei über 255.000 verfügbaren Beobachtungsstellen.

Zwei Ergänzungen sind zwingend, weil Ereignisse allein nicht genügen:

- **Suchlauf beim Start.** Konfliktkopien, die entstanden sind, während der Dienst nicht lief, erzeugen kein Ereignis mehr und blieben sonst dauerhaft unentdeckt.
- **Sicherheits-Suchlauf alle 15 Minuten.** Ereignisse können verlorengehen — die Warteschlange ist begrenzt (hier 16.384 Einträge), und bei neu angelegten Verzeichnissen besteht ein kurzes Wettrennen, bis deren Beobachtung steht. Syncthing selbst behält aus demselben Grund seinen vollständigen Suchlauf trotz Beobachter bei.

Damit ist der Dienst gegen ausgefallene Benachrichtigungen ebenso abgesichert wie gegen eigene Neustarts.

Der Wächter verändert nie Ordnerinhalt und trifft nie inhaltliche Entscheidungen (2.1). Er ist bewusst zustandsarm: Alles, was er wissen muss, steht im Ordner (die Kopien) und in der kleinen Zustandsdatei (3.2).

### Stündliche Betriebsmeldung

Zusätzlich zur Konfliktsuche stellt der Wächter einmal je Stunde die Betriebsmeldung aus 1.7 zusammen und zeigt sie per `notify-send`. Fällig ist sie, wenn seit der letzten Meldung eine Stunde vergangen ist (Zeitstempel in der Zustandsdatei); sie hängt damit am selben Durchgang wie die Konfliktsuche und braucht keinen eigenen Takt.

**Datenquellen** — Syncthings lokale REST-Schnittstelle auf `127.0.0.1:8384`, geprüft und lieferfähig:


| Aufruf                        | liefert                                                                      |
| ----------------------------- | ---------------------------------------------------------------------------- |
| `/rest/system/connections`    | je Gerät`inBytesTotal`, `outBytesTotal`, `startedAt`, `connected`, `type`   |
| `/rest/stats/folder`          | `lastFile` (Zeitpunkt und Name der zuletzt eingetroffenen Datei), `lastScan` |
| `/rest/db/status?folder=<id>` | Bestandszahlen sowie`needFiles`/`needBytes` — der noch offene Rückstand    |

**Fünf Punkte, die bei der Umsetzung zu beachten sind:**

1. **Die Byte-Zähler sind kumulativ seit Verbindungsaufbau und springen bei jedem Neuverbinden auf null.** Für eine Stundenangabe muss der Wächter Vorwert **und** `startedAt` in der Zustandsdatei mitführen und die Differenz nur bilden, wenn `startedAt` unverändert ist; andernfalls beginnt die Zählung neu. Ohne diese Prüfung meldet der Wächter nach jedem Verbindungsabriss negative oder unsinnige Werte.
2. **Zugriff braucht den API-Schlüssel** aus `configuration/gui/apikey` der Syncthing-Konfiguration. Der Schlüssel gewährt vollen Zugriff auf die Syncthing-Steuerung: Er wird zur Laufzeit gelesen, nie protokolliert, nie in eine Meldung geschrieben und liegt außerhalb des abgeglichenen Ordners (2.7).
3. **Die Meldung ist Beiwerk.** Ist die Schnittstelle nicht erreichbar, der Schlüssel nicht auffindbar oder eine Antwort unerwartet geformt, entfällt die Meldung stillschweigend — die Konfliktsuche, die eigentliche Aufgabe, läuft davon unberührt weiter und darf daran nie scheitern.
4. **Der Rückstand ist Bestandteil der Meldung** (Entscheidung zu F10, Wortlaut und Dauer in 1.7). `needFiles` wird je Freigabe abgefragt, wofür der Wächter den überwachten Ordner erst auf Syncthings Freigabe-Kennung abbilden muss — über die Konfiguration, per Pfadvergleich, weil dort auch „~/.claude" statt eines absoluten Pfades stehen kann. Findet er keine Freigabe, entfällt allein die Rückstandszahl und die Meldung erscheint trotzdem. Aus derselben Antwort kommt das Feld `paused`: Eine vom Nutzer von Hand gesetzte Pause der Freigabe wird gemeldet (Wortlaut in 1.7) — gelesen, nie geschrieben (2.1). **Pause und Rückstand werden neben offenen Konflikten mitgenannt, nicht statt ihrer:** Beides ändert, was der Nutzer tun sollte, und die Ruheform, in der sie sonst erschienen, kommt bei offenen Konflikten gar nicht vor. Der Wortlaut des Rückstands liegt dafür an **einer** Stelle im Code, weil er in zwei Meldungen auftritt (2.4). Ein angehaltenes **Gerät** braucht dafür keine eigene Behandlung: Es erscheint als fehlende Verbindung, weil Syncthing die Verbindung dabei trennt. Am echten Bestand geprüft: `paused` steht sowohl auf der Freigabe als auch je Gerät und je Verbindung.
5. **Die Anzeigedauer hängt vom Inhalt ab** (5 s im Normalfall, 12 s bei offenen Konflikten, Rückstand oder fehlender Verbindung; Begründung in 1.7). Übergeben wird sie als `notify-send -t` in **Millisekunden**; ob sie befolgt wird, entscheidet der Benachrichtigungsdienst. Der Zustand führt dafür zusätzlich mit, wann zuletzt überhaupt eine Verbindung bestand — ohne diesen Bezugspunkt ließe sich „seit …" nicht sagen (3.2). Dieser Merker wird **nur beim Zusammenstellen der Meldung** aktualisiert, also höchstens einmal je Stunde. Die Angabe „seit …" ist damit auf Stunden genau und nicht genauer — passend zum Takt der Meldung, aber es heißt auch: Nach einer frischen Installation steht bis zur ersten Meldung noch kein Bezugspunkt in der Zustandsdatei, und ein sofortiger Verbindungsverlust wäre dann ohne Zeitangabe zu melden. Beabsichtigt: Ein zusätzlicher REST-Aufruf je Durchgang wäre Aufwand für eine Genauigkeit, die niemand braucht.

**Bezug zu F4:** Wird die REST-Schnittstelle für die Betriebsmeldung ohnehin angebunden, verliert das Gegenargument gegen einen ereignisgesteuerten Auslöser („Kopplung an die lokale API samt Schlüssel") seine Kraft — beide Fragen sind deshalb zusammen zu entscheiden.

Nicht verwendet wird Syncthings eigener Ereignisstrom (`/rest/events`) als Auslöser, obwohl die REST-Anbindung ohnehin besteht: Ein eigener Ereignistyp für Konflikte ist dort nicht vorgesehen, sodass ebenfalls nach dem Dateinamensmuster gefiltert werden müsste — der semantische Vorteil entfällt, während Ereignis-Nummernverwaltung und Wiederverbindungslogik hinzukämen. Die Beobachtung über das Betriebssystem ist einfacher und unabhängig davon, ob Syncthing sein Ereignisschema ändert.

## 3.2 Zustandsdaten

Eine kleine JSON-Datei `~/.claude-sync-watch/zustand.json` mit diesen Angaben:

- ob eine Konflikt-Episode aktiv ist,
- wann der Konflikt-Dialog zuletzt gezeigt wurde (Dreißig-Minuten-Regel),
- der zwischengespeicherte Terminal-Befehl (3.3),
- wann die letzte Betriebsmeldung erschien, sowie die Vergleichswerte dafür: die Byte-Zähler je Gerät samt zugehörigem `startedAt` (siehe 3.1),
- wann zuletzt überhaupt eine Verbindung zu einem Gerät bestand — der Bezugspunkt für „keine Verbindung seit …" in der Meldung (1.7). Fehlt das Feld, weil die Datei von einer älteren Fassung stammt, bleibt sie lesbar und die Angabe entfällt,
- wann zuletzt eine Konfliktkopie gefunden wurde — Grundlage für die Angabe „kein Konflikt seit … Stunden",
- PID und Startzeitpunkt einer gestarteten Konfliktsitzung — Grundlage für die Ruhezeit aus 3.1 Schritt 3.

Eine unlesbare Zustandsdatei gilt als leer; der Wächter stürzt darüber nicht. Für die Betriebsmeldung bedeutet das lediglich, dass die Zählung neu beginnt — auch hier gilt: Beiwerk, kein Betriebsmittel.

Der Zeitpunkt des letzten Konfliktfundes ist die einzige Angabe, die einen Neustart der Zählung sichtbar verfälschen würde („kein Konflikt seit 0 Stunden", obwohl seit Wochen Ruhe herrscht). **Offen** (F10): ob das hinzunehmen ist oder die Angabe dann entfallen soll.

Dazu eine einfache Sperre gegen überlappende Wächter-Läufe (ein Lauf ist kurz; eine simple Existenz-Sperre mit Altersgrenze genügt). Die laufende Konfliktsitzung weist sie **nicht** aus — dafür dienen PID und Startzeitpunkt (3.1 Schritt 4).

Ein Verlust der Zustandsdatei ist folgenlos für den Bestand: Alles Wesentliche steht im Ordner selbst. Neu beginnen lediglich die Zählungen der Betriebsmeldung, und ein zu diesem Zeitpunkt laufender Dialog kann einmal zusätzlich erscheinen.

## 3.3 Eskalationsstrecke: Dialoge und Terminalstart

Vollständig aus Vorversuchen übernommen und dort erprobt (Belege: 3.8); hier die Festlegungen:

**Konflikt-Dialog (Zenity-Frage):** Titel „Claude-Sync: Konflikt", Text nennt die betroffenen Originale und erklärt vorab, dass sich zur Bearbeitung eine Claude-Code-Sitzung in einem Terminal öffnet und dafür gegebenenfalls ein Terminal-Programm auszuwählen ist. Antworten „Jetzt lösen" / „Später". Der genaue Wortlaut wird bei der Implementierung an die Syncthing-Begriffe angepasst; Struktur und Zweistufigkeit sind gesetzt.

Ein Frage-Dialog hat **drei** Ausgänge, nicht zwei: Zustimmung, Ablehnung und **„konnte nicht gezeigt werden"**. Der Rückgabewert trennt sie **nicht** — gemessen, nicht angenommen: Zenity ohne erreichbare Anzeige endet mit `1`, genau wie ein Abbruch, und schreibt `Failed to open display` auf die Fehlerausgabe. Unterschieden wird deshalb an der Meldung, und weil deren Wortlaut keine zugesicherte Schnittstelle ist, gilt die Absicherung: **Jede** nicht-leere Fehlerausgabe geht ins Journal, unabhängig von der Einordnung — ein falsch eingeordneter Fall ist dann wenigstens sichtbar statt stumm. Dass eine Meldung auf der Fehlerausgabe **kein** Fehlersignal ist, ist dabei nicht Vorsicht, sondern gemessen: Auf dem Entwicklungsrechner warnt ein vollkommen erfolgreicher Zenity-Dialog jedes Mal über einen fremden Schlüssel in seiner eigenen GTK-Konfiguration. Eine Regel „Ausgabe heißt Fehler" hätte dort **jeden** Dialog als kaputt eingeordnet. Diese Trennung verhindert den schlimmsten Ausgang für einen Wächter, der ausschließlich zum Eskalieren existiert: Ein Desktop ohne Anzeigeverbindung sähe im Zustand genauso aus wie ein Nutzer, der vertagt hat — aus einem Defekt würde Stille. Deshalb gilt: Die Fehlermeldung von Zenity geht ins Journal statt verworfen zu werden, ein gescheiterter Versuch zählt **nicht** als Vertagung, und für den nächsten Versuch gilt statt der halben Stunde aus 2.9 eine kurze Wartezeit von fünf Minuten. Die Wartezeit ist nicht Rücksicht auf den Nutzer — er hat nichts gesehen —, sondern verhindert, dass ein kaputter Desktop das Journal im Takt der Dateiereignisse füllt. Der Fund kam aus dem Dienst-Test (3.8), wo genau diese Ungewissheit nur durch Nachfrage beim Nutzer aufzulösen war.

**Der Dialog schließt sich nach fünfzehn Minuten selbst** (`--timeout`, Rückgabewert `5`). Grund ist der Mehrrechnerbetrieb: Läuft der Wächter auf beiden Rechnern und wird der Konflikt an einem gelöst, bleibt der Dialog am anderen sonst stehen, bis jemand klickt — er nennt dann Dateien, die es längst nicht mehr gibt, und ein späterer Klick auf „Jetzt lösen" startet eine Sitzung, die nichts vorfindet (dafür 3.4, Schritt 1). Mit Zeitablauf verschwindet er von selbst, und der nächste Durchgang bewertet die Lage neu: Ist nichts mehr da, schweigt er. Zeitablauf gilt als **Vertagung**, nicht als Fehler — niemand saß davor, also greift die reguläre halbe Stunde aus 2.9, nicht die kurze Wiederholung. Zweiter, kleinerer Gewinn: Ein Durchgang hält seine Laufsperre nun höchstens für die Dauer der Dialogstrecke statt unbegrenzt.

Die Zeitangabe ist in **Sekunden** zu machen (`--timeout=900`). Eine Dauerangabe wie `15m` weist Zenity mit Rückgabewert `255` ab — was die Einordnung oben als Fehlschlag lesen würde, womit jeder Dialog als kaputt gälte. Gemessen, nicht angenommen (3.8); das Prüfskript nagelt die Einheit fest.

**Terminal-Erkennung:** Zuerst `xdg-terminal-exec` (distributionsübergreifende freedesktop-Lösung mit eigener Zwischenspeicherung); fehlt es, eine Prioritätenliste bekannter Emulatoren (`x-terminal-emulator`, `gnome-terminal`, `konsole`, `xfce4-terminal`, `alacritty`, `kitty`, `xterm`). Genau ein Fund wird verwendet; mehrere Funde führen zu einem Zenity-Auswahldialog, kein Fund zu einer Freitexteingabe. Das Ergebnis wird in der Zustandsdatei zwischengespeichert und verwendet, solange der Befehl existiert. Erprobt: Die Auswahl liefert den Kandidatennamen als Klartext mit Zeilenumbruch; Abbruch liefert leere Ausgabe und Rückgabewert eins.

**Abbruchverhalten:** Ein Abbruch der Auswahl führt zu einem zweiten Frage-Dialog („Zur Bearbeitung des Konflikts wird ein Terminal für die Claude-Sitzung benötigt. Auswahl erneut versuchen?" — „Erneut versuchen" / „Abbrechen"). Abbruch dort beendet die Strecke ohne weitere Rückfrage; die Episode meldet sich regulär wieder. Beide Wege sind durchgespielt.

**Start der Sitzung:** Das gewählte Terminal wird mit folgendem Aufruf gestartet — jeder Bestandteil ist am laufenden System geprüft:


| Bestandteil                                                           | Zweck                                                                                                                  |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `/usr/bin/claude`                                                     | **absoluter** Pfad; ein systemd-Benutzerdienst startet mit karger Umgebung und fände `claude` sonst nicht im Suchpfad |
| `--add-dir ~/.claude-sync-watch/werkzeuge`                            | Zugriff auf spätere Hilfsskripte                                                                                      |
| `--append-system-prompt-file ~/.claude-sync-watch/konfliktloesung.md` | die Arbeitsanweisung als Rahmen der gesamten Sitzung                                                                   |
| Übergabetext                                                         | nennt**den zu durchsuchenden Ordner** sowie die Konfliktpaare samt Gerätekennung                                      |

**Die Reihenfolge dieser Bestandteile ist tragend, nicht kosmetisch.** `--add-dir` ist variadisch (`--add-dir <directories...>`) und verschlingt jedes folgende Argument als weiteres Verzeichnis. Stand der Übergabetext dahinter, startete die Sitzung **ohne jeden Prompt** — im Betriebstest beobachtet: Sie zeigte den Willkommensschirm, statt zu arbeiten. Nachgestellt und bestätigt: `claude --add-dir /tmp "Text" -p` antwortet mit `Error: Input must be provided either through stdin or as a prompt argument`. Der Übergabetext gehört deshalb hinter `--append-system-prompt-file`, das genau einen Wert nimmt.

**Der Ordner steht im Übergabetext, nicht in der Arbeitsanweisung.** Ein fest verdrahteter Pfad in `konfliktloesung.md` führte im Test dazu, dass die Sitzung im Produktivordner `~/.claude` suchte, obwohl der Testordner gemeint war. Die Anweisung nennt seither keinen Pfad mehr; der Wächter setzt ihn zur Laufzeit ein. Eine Angabe, zwei Orte — das war die Driftquelle.

**Die Umgebung des Kindprozesses wird bewusst gebaut, nicht geerbt.** Die karge systemd-Umgebung ist nur die eine Hälfte des Problems; die andere ist eine Umgebung, die *zu viel* enthält. Wird der Wächter aus einer laufenden Claude-Code-Sitzung heraus gestartet (wie beim Testen), erbt das Kind deren Kennungen — beobachtet waren `CLAUDECODE`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_CHILD_SESSION` und sieben weitere — und läuft ins Erst-Start-Gespräch, statt die vorhandene Anmeldung zu nutzen. Ebenso wird `TERM` **entfernt** statt gesetzt: Ein geerbtes `TERM=dumb` machte die Sitzung unlesbar; über den Wert entscheidet der Terminal-Emulator für sein eigenes Kind.

Zur Wahl von `--append-system-prompt-file` statt eines langen Anfangs-Prompts: Der Anfangs-Prompt ist eine gewöhnliche Nutzernachricht — eine Gesprächsrunde unter vielen, die bei einer langen Sitzung mit vielen Dateien durch Zusammenfassung des Verlaufs an Gewicht verlieren kann. Die System-Prompt-Ergänzung bleibt dagegen durchgehend Rahmen. Die `-file`-Varianten sind in der Hilfeausgabe nicht eigens aufgeführt, existieren aber nachweislich (ein Aufruf mit falschem Pfad antwortet mit `Error: Append system prompt file not found: …`); ein Vermerk, dass sie auf `--print` beschränkt wären, fehlt — andere Optionen tragen einen solchen ausdrücklich. **Nicht** verwendet wird `--system-prompt-file`: Es *ersetzt* den eingebauten System-Prompt, womit die Sitzung ihr Wissen über das eigene Werkzeugverhalten verlöre.

Das Arbeitsverzeichnis des Terminalprozesses ist der überwachte Ordner — der einzige Weg, es zu bestimmen, da Claude Code es ausschließlich vom aufrufenden Prozess übernimmt ([CLI-Referenz](https://code.claude.com/docs/en/cli-reference.md)). Erprobt: Die drei auf Rechner A vorhandenen Emulatoren reichen mehrteilige Übergabetexte mit Leerzeichen, Anführungszeichen und Apostroph unverändert durch. Der Prozess wird vom Wächter entkoppelt gestartet.

**Die Terminal-Fassung muss angemeldet sein — das ist eine eigene Voraussetzung.** Dass `/usr/bin/claude` existiert, sagt nichts darüber, ob es benutzbar ist: Auf Rechner A war es zunächst nicht angemeldet, obwohl `~/.claude/.credentials.json` vorlag und die VS-Code-Erweiterung arbeitete. Die Sitzung zeigte dann Theme- und Anmeldefragen statt der Konfliktarbeit. `install_service.sh` prüft das deshalb (3.5), und die einmalige Abhilfe ist ein Handstart von `claude` mit `/login`.

**Widerspruch zwischen Doku und Beobachtung, nicht aufgelöst:** `claude --bare -p …` meldet eine vorhandene Anmeldung als `Not logged in`, während derselbe Aufruf ohne `--bare` normal antwortet. Die Beschreibung von `--bare` nennt als übersprungene Dinge nur *„hooks, skills, plugins, MCP servers, auto memory, and CLAUDE.md"* — von Authentifizierung ist dort keine Rede. Für die Anmeldeprüfung ist `--bare` deshalb unbrauchbar; sie läuft ohne. (Beobachtet an 2.1.220.)

**Nebenwirkung des Arbeitsverzeichnisses:** Claude Code lädt beim Start die `CLAUDE.md`-Dateien vom Arbeitsverzeichnis aufwärts — also auch `~/.claude/CLAUDE.md` mit der benutzerweiten Projektmethodik (Plan vor Ausführung, Fahrplan- und Commit-Regeln). Für eine Konfliktlösung ist das nicht nur überflüssig, sondern irreführend. Umgehen lässt es sich nicht; die Arbeitsanweisung stellt deshalb ausdrücklich klar, dass jene Regeln hier nicht gelten (3.4).

## 3.4 Arbeitsanweisung für die Konfliktsitzung

Die Konfliktsitzung folgt einer schriftlichen Arbeitsanweisung: `~/.claude-sync-watch/konfliktloesung.md`, beim Start als System-Prompt-Ergänzung mitgegeben (3.3). Sie trägt einen `@Claude:`-Abschnitt nach 2.5.

**Zwei Klarstellungen gehören an ihren Anfang**, weil sie sonst aus dem Arbeitsverzeichnis heraus falsch beantwortet würden: dass die aus `~/.claude/CLAUDE.md` mitgeladene Projektmethodik (Plan vor Ausführung, Fahrplan, Commits, Segmentstruktur) für diese Sitzung **nicht** gilt; und dass der Zweck der Sitzung eng begrenzt ist — Konfliktpaare auflösen, sonst nichts.

Das Verfahren:

**Voraussetzung:** Der Abgleich läuft während der Sitzung weiter (Begründung in 1.6). Der Bestand kann sich also verändern — im Regelfall geschieht das nicht, weil am anderen Rechner niemand arbeitet, aber die Sitzung muss darauf gefasst sein. Sie erhält alle beim Start anstehenden Paare auf einmal.

1. **Lage erheben.** Unabhängig von der überreichten Liste selbst frisch nach `*.sync-conflict-*` suchen und die Paare Original ↔ Kopie(n) bilden. Ein **leerer** Befund schon beim ersten Suchen ist kein Fehler, sondern im Mehrrechnerbetrieb der Normalfall: Der Konflikt wurde am anderen Rechner gelöst und die Auflösung ist hierher gewandert (1.6). Die Sitzung sagt das in einem Satz und endet — sie sucht nicht weiter und weicht in keinen anderen Ordner aus. Die Gerätekennung im Namen wird dabei **nicht** zur Zuordnung „hier/entfernt" verwendet (Begründung in 3.1, Schritt 2); wessen Fassung welche ist, erschließt die Sitzung aus Inhalt und Änderungszeit oder erfragt es.

   **Erscheinen dabei deutlich mehr Konflikte als übergeben, oder kommen während der Arbeit weitere hinzu**, arbeitet offenbar gerade der andere Rechner mit. Dann ist dem Nutzer zu **empfehlen**, den Abgleich in Syncthings Oberfläche von Hand anzuhalten, bevor weitergearbeitet wird — und ihn nach getaner Arbeit wieder einzuschalten. Das ist eine Empfehlung, keine Automatik: Im Regelfall ist Anhalten unnötig und würde nur die Verteilung der Lösung blockieren (1.6).
2. **Je Paar gemeinsam entscheiden.** Beide Fassungen vergleichen, dem Nutzer den Unterschied verständlich erklären — einschließlich der Angabe, welche Fassung von welchem Gerät stammt und welche im Abgleich „gewonnen" hat —, dann die Entscheidung einholen: Original behalten / Kopie übernehmen / von Hand zusammenfügen.
3. **Umsetzen — nur mit Zustimmung.** Je nach Entscheidung die Konfliktkopie löschen, deren Inhalt ins Original schreiben, oder die von Hand gebaute Fassung ins Original schreiben und die Kopie löschen. Jede dieser Aktionen erst nach ausdrücklicher Zustimmung zur konkreten Datei (2.2). Kein weiterer Schritt nötig: Syncthing verteilt Schreiben wie Löschen selbsttätig.

   Geschrieben wird **nur**, was der Konflikt erfordert — kein Ausbessern von Leerraum, Einrückung, Zeilenenden, Reihenfolge oder Schreibfehlern, auch wenn es eine Verbesserung wäre. Begründung: Jede unnötige Byte-Änderung wandert auf alle Geräte (1.6) und kann dort zum nächsten Konflikt werden, und in manchen Dateien trägt der Leerraum Bedeutung. Ist eine solche Entscheidung beim Zusammenfügen unvermeidlich, wird sie vor der Zustimmung benannt. Anlass ist eine Beobachtung aus dem Vollzug (3.8): Die Sitzung hatte Leerzeilen normalisiert — offengelegt und abgesegnet, aber ungeregelt.
4. **Endkontrolle.** Erneut suchen; erst ein leerer Befund beendet die Bearbeitung. Sind während der Arbeit neue Kopien hinzugekommen, gehören sie in dieselbe Runde. Ergibt eine Entscheidung, dass eine Datei oder ein Ordner künftig gar nicht mehr abgeglichen werden soll, ist die Ausschlussliste jetzt anzupassen — und zwar auf **jedem** Gerät, da sie nicht mitwandert (2.3).
5. **Aufräumen.** Wurde auf Empfehlung aus Schritt 1 von Hand angehalten, den Nutzer daran erinnern, den Abgleich wieder einzuschalten. Bestehen Zweifel, ob die Lösung trägt, ist Angehaltenlassen die richtige Wahl — dann greift der Notfall-Rückgriff aus 1.9.
6. **Berichten.** Betroffene Paare, Entscheidung je Paar, was geschrieben und gelöscht wurde, ob Ausschlüsse geändert wurden. **Offen** (Anhang F6): Form des Berichts und ob eine Erfolgsmeldung folgt.

**Zum Zusammenspiel mehrerer Rechner:** Löschung der Kopie und Aktualisierung des Originals wandern als gewöhnliche Dateivorgänge mit. Wer hier löst, räumt damit überall auf — auf einem eingeschalteten zweiten Rechner verschwinden die Kopien von selbst und seine Episode endet, ein ausgeschalteter erfährt von dem Konflikt nie etwas. **Deshalb wird immer nur an einem Rechner gelöst**, sinnvollerweise dem, an dem gerade gearbeitet wird.

Zur Einordnung von Schritt 2: Es stehen **zwei** Fassungen zur Verfügung, kein gemeinsamer Vorfahre. Für die typischen Kandidaten (Konfigurationsdateien, Markdown) genügt der direkte Vergleich; die Versionierung ist ausdrücklich **kein** Werkzeug der Konfliktlösung, sondern nur der Notfall-Rückgriff aus 1.9.

**Offen** (Anhang F3): Verhalten bei Dateien, die die laufende Claude-Instanz selbst benutzt.

## 3.5 Dienstdefinition und Einrichtung

### Die Unit

**Eine** Definition im Benutzer-Kontext (`--user`), seit dem 11. August 2026 auf beiden Rechnern installiert und laufend: `claude-sync-watch.service`, ein dauerhaft laufender Dienst, der `claude_sync_watchd.py` startet. Ein Timer entfällt — der Wächter beobachtet selbst und führt seinen Sicherheits-Suchlauf intern aus (3.1).

Festgelegte Eigenschaften:

- **`PartOf=graphical-session.target`** — die Dialoge brauchen die grafische Sitzung. Ohne sie läuft kein Wächter; Konflikte warten dann auf die nächste Anmeldung, der Abgleich selbst läuft unabhängig davon weiter, und der Suchlauf beim Start holt Versäumtes nach.
- **`WantedBy=graphical-session.target`** — startet beim Anmelden von selbst, wie Syncthing auch. Kein Handstart nötig.
- **`Restart=on-failure`** — ein Dauerdienst darf nicht unbemerkt sterben.
- **Absoluter Interpreterpfad `/usr/bin/python3`** im `ExecStart`, aus demselben Grund, aus dem auch `/usr/bin/claude` absolut steht: Ein Dienst startet mit fremdem `PATH`. Auf einem Rechner, dessen interaktive Shell ein Virtualenv voranstellt, wären „das `python3` des Nutzers" und „das `python3` des Dienstes" zwei verschiedene Interpreter — und nur einer sieht die Distributionspakete. Die Prüfung im Installationsskript trifft deshalb **denselben** Pfad; sonst prüft man den einen und startet den anderen. Beobachtet, siehe 3.8.
- Pfadangaben über den Platzhalter **`%h`** für das Benutzer-Home (belegt: löst in Benutzer-Units auf das Home des ausführenden Benutzers auf). Dadurch braucht die Unit **keine** Pfadersetzung bei der Installation und kann als statische Datei ausgeliefert werden.
- Die Installationsprüfung vergleicht zusätzlich `~/.claude/.stignore` gegen die maßgebliche Fassung im Werkzeugordner und zeigt Unterschiede samt Kopierbefehl an — Warnung, kein Abbruch (Begründung in 2.8).
- Diagnose über `journalctl --user`; Einrichtung auf jedem Rechner identisch (2.8). Im Journal landet **eine Zeile je Durchgang, der etwas gefunden hat** (Anlass, Anzahl, Ordner). Ein leerer Befund schweigt bewusst: Der Sicherheits-Suchlauf läuft alle fünfzehn Minuten und würde das Journal sonst mit „nichts" füllen. Zuvor war die Zeile an den Trockenmodus gebunden, der Dienst also vollständig stumm — im Vollzug aufgefallen (3.8).

### Warum eine Vorlagendatei und kein erzeugter Text

Die Unit liegt als eigene Datei `claude-sync-watch.service` im Werkzeugordner und wird beim Einrichten nach `~/.config/systemd/user/` kopiert — sie wird **nicht** vom Installationsskript per Textausgabe erzeugt. Gründe: Eine Unit ist eine Beschreibung, kein Ablauf; sie in Shell-Anführungszeichen zu verpacken, verlangte zusätzliches Schützen von `%h` und `$` und erzeugt Fehler, die erst beim Dienststart auffallen. Als eigene Datei bleibt sie lesbar und lässt sich gegen die installierte Fassung vergleichen. Da `%h` die Pfadersetzung überflüssig macht, entfällt der einzige Vorteil der Erzeugungsvariante.

### `install_service.sh`

Prüft zuerst die Vorbedingungen und bricht bei Fehlbefund mit klarer Meldung ab:

- Das Skript ermittelt seinen eigenen Ordner — unabhängig vom Verzeichnis, aus dem es aufgerufen wird — und prüft, dass dieser exakt `$HOME/.claude-sync-watch` ist. Andernfalls abbrechen mit der Anweisung, den Ordner dorthin zu verschieben. Der Ort ist damit **keine Empfehlung, sondern Vorschrift**: Die Unit verwendet `%h/.claude-sync-watch/…` fest (s. o.); jeder andere Ort würde eine Anpassung der Unit nötig machen, und genau das soll die statische Vorlagendatei vermeiden.
- `/usr/bin/claude` vorhanden (sonst kann keine Konfliktsitzung starten)
- **und benutzbar**: ein `claude -p "ok"` darf nicht `Not logged in` melden. Vorhandensein allein genügt nicht (Begründung in 3.3) — ohne diese Prüfung richtet sich der Dienst ein, zeigt brav Dialoge und öffnet Terminals, in denen nichts Sinnvolles passiert. Der Aufruf kostet einen Bruchteil eines Cent an Tokens und einen Netzzugriff; das ist der Preis dafür, einen stillen Ausfall auszuschließen. **Ohne `--bare`** — das meldet eine vorhandene Anmeldung fälschlich als fehlend (3.3). Antwortet der Aufruf gar nicht, wird nur gewarnt und fortgesetzt: eine hängende Leitung ist kein Beweis für eine fehlende Anmeldung.
- Python-Beobachtungsbibliothek (`watchdog`) verfügbar
- Syncthing läuft und der zu überwachende Ordner ist konfiguriert
- `konfliktloesung.md` vorhanden

Danach: Unit kopieren, `systemctl --user daemon-reload`, `systemctl --user enable --now claude-sync-watch.service`, abschließend den Status ausgeben.

**Das Skript installiert nichts nach.** Fehlt eine Voraussetzung, nennt es den passenden Befehl und bricht ab — Pakete zu installieren ist zustimmungspflichtig, und ein Installationsskript ist kein Ort, das zu umgehen.

### `uninstall_service.sh`

`systemctl --user disable --now`, Unit entfernen, `daemon-reload`. **Ordner, Zustandsdatei und Arbeitsanweisung bleiben unangetastet** — das Skript meldet den Dienst ab, es deinstalliert nicht das Vorhaben. Wer alles loswerden will, löscht anschließend `~/.claude-sync-watch/` von Hand.

Beide Skripte tragen einen Kopfkommentar nach 2.5; einen `@Claude:`-Abschnitt brauchen sie nicht, da sie vom Nutzer ausgeführt werden.

## 3.6 Anbindung eines weiteren Rechners

Einmaliger Vorgang je Rechner, zweiphasig (Begründung in 1.10). **Stand:** Für FWFE41 sind beide Phasen durchlaufen — Testordner erprobt, `~/.claude` angebunden; es fehlt dort nur noch der Wächter. Das Verfahren bleibt hier stehen, weil es für jeden weiteren Rechner erneut gilt; was davon belegt ist, steht in 3.8.

**Phase 1 — Hilfsordner:** Gerät mit der Synology koppeln (Introducer aus). Einen eigenen Testordner (z. B. `~/syncthing-test`) mit eigener Folder-ID teilen. Den Testplan aus 3.8 vollständig durchlaufen. `~/.claude` bleibt unberührt.

**Phase 2 — echter Bestand:**

1. Sicherung des lokalen `~/.claude` (Kopie oder Umbenennung — es ist die einzige Rückfalllinie dieses Schrittes).
2. `.stignore` mit den Einträgen aus 1.3 in `~/.claude` anlegen — **vor** dem Teilen (2.3).
3. Den Ordner mit derselben Folder-ID wie auf den übrigen Geräten teilen und den Erstabgleich abwarten. Erwartung: Einseitig vorhandene Dateien werden verteilt; beidseitig vorhandene, inhaltlich verschiedene erzeugen Konfliktkopien — je nach Divergenz viele. Das ist der geplante Zusammenführungsmechanismus, kein Fehler.
4. Konfliktsitzung (3.4) durchführen, bis der Befund leer ist. Bei Protokolldateien gleichen Namens (unwahrscheinlich, siehe 1.5) gilt: im Zweifel beide Stände sichern und zusammenfügen statt verwerfen.
5. Wächter als Dienst einrichten (3.5), Ausschlusstest fahren (3.8), Sicherung nach angemessener Beobachtungszeit auflösen.

**Erstabgleich-Verhalten in Phase 1 ausdrücklich testen** (Testpunkt T7): Das beschriebene Vereinigungsverhalten zweier nicht-leerer Bestände ist doku-basiert erwartet, aber noch nicht selbst belegt — Phase 2 beginnt erst, wenn T7 es bestätigt hat.

## 3.7 Windows-Pendant (Platzhalter)

Ausgearbeitet erst nach stabilem Betrieb auf beiden Linux-Rechnern. Festgehaltene Zuordnung für die Kapselstelle aus 2.4: PowerShell-Dialogfenster oder Toast-Benachrichtigungen statt Zenity; `wt.exe`/PowerShell statt der X11-Terminal-Erkennung; Aufgabenplanung statt systemd-Benutzerdienst. Syncthing selbst läuft nativ (Autostart über Aufgabenplanung oder Autostart-Ordner, siehe Konfigurationsanleitung Abschnitt 11); `%USERPROFILE%\.claude` ist strukturell identisch, der Zugangsdaten-Ausschluss gilt unverändert.

## 3.8 Belegführung und Testplan

**Aus Vorversuchen erprobt** (manuell ausführbare Skripte im Ordner `tests/`): das Zenity-Auswahlverhalten bei Auswahl und Abbruch (`test_zenity_list.py`), die Terminal-Erkennung samt unveränderter Argumentdurchreichung durch `konsole`, `x-terminal-emulator` und `xterm` (`test_detect_terminal.py` mit harmlosem Ersatzprogramm statt `claude`), und die zweistufige Dialog-Rückkehrschleife (`test_conflict_terminal_loop.py`). Diese Bausteine gehen unverändert in 3.3 ein.

Diese drei Skripte bleiben dauerhaft erhalten, obwohl der Code, für den sie geschrieben wurden, ersetzt ist: Sie prüfen nicht ein Skript, sondern **das Verhalten von Zenity und den Terminal-Emulatoren des Systems**, implementieren die Kaskade dafür eigenständig nach und importieren nichts. Damit sind sie die Belegführung für die Zusagen in 3.3 — und sie prüfen etwas, das der Wächter über sich selbst nicht prüfen kann: ob wirklich ein Fenster aufgeht und ob der Übergabetext mit Anführungszeichen und Apostroph unverändert ankommt. Das braucht ein Auge, keine Zusicherung im Code.

**Automatisch prüfbar** (`tests/test_dialog_and_naming.py`, aufzurufen mit `/usr/bin/python3`): die Einordnung jedes Dialog-Ausgangs, die beiden Wartezeiten und die Namensableitung. Das Skript braucht **keine** Anzeige, kein Zenity, kein Syncthing und kein Netz — Zenity ist durch eine Attrappe ersetzt, die Namen sind feste Zeichenketten —, läuft in unter einer Sekunde und endet mit Rückgabewert 1 bei der ersten Abweichung; damit taugt es als Schranke vor einem Commit. Es lädt den Wächter über seinen Pfad, ohne ihn irgendwo zu installieren.

Es prüft genau die zwei Stellen, an denen eine falsche Annahme **unsichtbar** bleibt, und beide sind keine Erfindung, sondern schon einmal falsch gewesen. Erstens die Dialog-Einordnung: Zenity endet bei Abbruch und bei fehlender Anzeige gleichermaßen mit `1`, die Unterscheidung hängt an der Fehlermeldung (3.3) — also an etwas, das kein zugesicherter Vertrag ist und das eine spätere Vereinfachung gutgläubig wegräumt. Der Fall „abgebrochen, aber das Toolkit hat trotzdem auf die Fehlerausgabe geschrieben" steht ausdrücklich mit drin, weil daran eine naive Regel „Ausgabe heißt Fehler" zerbricht. Zweitens die Namensableitung: Sie ist auf den **einen** bisher beobachteten echten Syncthing-Namen festgenagelt, dazu auf Namen mit Leerzeichen und Zusatzpunkt sowie auf einen ohne Endung, und schließlich darauf, dass die Anzeigezeile die Kennung nennt, **ohne** eine Herkunft zu behaupten — genau die Behauptung, die aus drei Stellen entfernt werden musste (3.1, Schritt 2). Ändert ein künftiges Syncthing das Format, fällt es hier auf und nicht erst im Ernstfall.

Nicht abgedeckt und bewusst den Handproben überlassen: Eskalation als Ganzes, Episodenregel, Terminalstart. Die brauchen einen Bildschirm und einen Menschen. Ebenso ungeprüft bleibt die Aussagekraft eines Prüfskripts selbst — deshalb wurde es einmal mit absichtlich verfälschter Erwartung laufen gelassen und meldete die Abweichung mit Rückgabewert 1; ein Prüfskript, das nie anschlägt, ist wertlos.

**Am gebauten Wächter geprüft** (synthetische Konfliktkopien in einem Testordner, ohne echte Daten): Fund in Unterordnern, zwei Kopien desselben Originals getrennt geführt, Auslassung von `.stversions/`, ein unparsbarer Kopiename gemeldet statt verschwiegen (ohne Gerätekennung), Lesen echter Syncthing-Zähler über REST, Überleben einer unlesbaren Zustandsdatei, und die Laufsperre unter zwanzig gleichzeitigen Zugriffen — genau einer kam durch.

**Betriebstest gegen einen echten Syncthing-Ordner** (`~/SyncThingTest`, auf Laptop und FWFE41 abgeglichen; Konfliktkopie von Hand nachgebaut, weil der Wächter ausschließlich am Namen erkennt und einen echten von einem nachgebauten Fund nicht unterscheiden kann):

Die Episodenregel aus 2.9 vollständig, jeder Fall einzeln nachgestellt — erste Erkennung zeigt den Dialog; ein sofort folgender Lauf zeigt keinen; nach zurückdatierter Sperre erscheint er wieder; das Verschwinden aller Kopien beendet die Episode ohne Zutun; eine neue Kopie bei frischer Sperre meldet trotzdem. Bei „Später" wird nichts gestartet. Die Ruhezeit aus 3.1 Schritt 3 greift ebenfalls: Ein Lauf während einer noch als offen geführten Sitzung schweigt.

Die Konfliktsitzung selbst, vom Nutzer am Bildschirm abgenommen und danach unabhängig am Dateibestand geprüft: Sie suchte im richtigen Ordner, stellte beide Fassungen in Prosa gegenüber statt als rohen Diff, nannte die Gerätekennung, deutete die Absicht hinter beiden Änderungen, empfahl begründet — und **fragte**, statt zu handeln. Die Wahl des Nutzers wich von der Empfehlung ab und wurde befolgt. Danach war das Original geschrieben, die Kopie gelöscht, der Ordner leer an Konflikten, und der nächste Wächterlauf beendete die Episode. Die Nicht-Konflikte im Ordner (`Textdatei (1).txt`) wurden **genannt, aber nicht angefasst**. Von Fahrplan, Plan-vor-Ausführung oder Commits war keine Rede — die beiden Klarstellungen am Anfang von 3.4 tragen.

**Echter Syncthing-Konflikt** (T3/T4, dieselben zwei Rechner): Eine auf beiden Seiten vorhandene Datei wurde nach dem Pausieren des Ordners auf **einem** der Rechner beidseitig geändert; nach dem Fortsetzen legte Syncthing die Kopie selbst an — `Konflikttest.sync-conflict-20260811-175245-3PDLNDG.txt`. Das Ergebnis: Das Suchmuster erkennt den echten Namen, zerlegt ihn vollständig (`stem`, Datum, Zeit, siebenstellige Gerätekennung, Endung `.txt` hinter der Kennung) und leitet das richtige Original ab, das auch existiert. Der Trockenlauf berichtete genau ein Paar. Damit ist die Annahme aus 3.1 Schritt 1 belegt und nicht mehr nur nachgebaut.

Der eigentliche Gewinn des Tests war aber ein anderer: Er hat den Irrtum über `<modifiedBy>` aufgedeckt (3.1, Schritt 2). Die Kopie enthielt die **Laptop**-Fassung, im Namen stand jedoch `3PDLNDG` — und der Laptop ist `AQKZ6SD`. Die Kennung war in der Geräteliste des Laptops überhaupt nicht zu finden, weil FWFE41 nur über die Synology (`274QPHP`) angebunden ist; durch Ausschluss der drei beteiligten Geräte bleibt FWFE41, also die **siegreiche** Seite. Eine Auflösung der Kennung zu einem Klarnamen ist damit lokal grundsätzlich nicht möglich. Anweisung, Dialogtext und Doku sind daraufhin auf eine richtungsfreie Aussage umgestellt worden. Merksatz für künftige Prüfungen: Der Test hat nicht bestätigt, was wir erwarteten, sondern eine Aussage widerlegt, die zuvor an drei Stellen gleichlautend und gleich falsch stand.

**Vollzug am echten Konflikt** — dieselbe Kopie, die Syncthing selbst angelegt hatte, wurde anschließend über die ganze Kette aufgelöst: Erkennung, Dialog, Wahl „Jetzt lösen", Sitzung im Terminal, Auflösung, Episodenende. Alle Glieder waren zuvor einzeln oder mit nachgebauter Kopie geprüft; hier lief erstmals nichts Gestelltes mehr mit. Der Übergabetext nannte den richtigen Ordner und die Gerätekennung in der neuen, richtungsfreien Form. Die Sitzung stellte beide Fassungen gegenüber, empfahl das Zusammenfügen, bot die drei Möglichkeiten **mit einer Vorschau des jeweiligen Ergebnisses** an — das steht nicht in der Anweisung, ist aber genau die Verständlichkeit, die 3.4 Schritt 2 verlangt — und fragte einzeln vor dem Überschreiben und vor dem Löschen. Danach unabhängig am Dateibestand geprüft: Kopie gelöscht, Original mit beiden Zufügungen **und** der Streichung der Gegenseite, kein Fund mehr, `conflict_active` zurückgesetzt. Die Nicht-Konflikte im Ordner blieben unangetastet, und der Abschlusssatz aus F6 kam.

Der Beleg für die Korrektur an 3.1 Schritt 2 fiel dabei mit: Die Sitzung schrieb von sich aus, sie habe die Gerätekennung „dafür nicht verwendet", und erschloss die Zuordnung aus dem Inhalt — mitsamt der Feststellung, dass die in **beiden** Fassungen stehende Zeile „Diese Fassung stammt von FWFE41." nichts unterscheidet und daher nichts beweist. Die Anweisung wirkt also nicht nur als Verbot, sie liefert auch den brauchbaren Ersatzweg. Zwei Ungeregeltes zeigte derselbe Lauf: die stumme Bilanzzeile (3.5) und die eigenmächtige Normalisierung von Leerzeilen (3.4 Schritt 3) — beide behoben.

**Dienstbetrieb, Stufe A** — geprüft ohne jede Einrichtung: `systemd-run --user` startet das Skript als echte, flüchtige Unit, mit der kargen Umgebung eines Dienstes, aber ohne eine Datei außerhalb der Projektwurzel anzulegen. So bleibt die Messung echt und die Regel aus 1.2 unangetastet. Vorbedingung geklärt: `graphical-session.target` ist in der Sitzung aktiv, die Bindung der Unit greift also überhaupt. Die Umgebung einer Benutzer-Unit umfasst 65 statt 103 Variablen, enthält aber `DISPLAY=:0`, `XAUTHORITY`, `DBUS_SESSION_BUS_ADDRESS` und `XDG_RUNTIME_DIR`; `WAYLAND_DISPLAY` fehlt zu Recht, die Sitzung ist X11. **Der Dialog erschien tatsächlich** — vom Nutzer am Bildschirm bestätigt, Antwort „Später", danach wie vorgesehen kein Start. Die Bilanzzeile stand als Ausgabe der Unit da: der erste Nachweis der Journal-Zeile im Produktivpfad. Damit ist die Sorge hinter Fahrplan 3 — ein Dienst ohne Anzeigeverbindung und damit eine wirkungslose Eskalation — entkräftet.

Zwei Defekte hat dieselbe Stufe aufgedeckt, beide behoben:

- **Prüfung und Ausführung trafen verschiedene Interpreter.** Die interaktive Shell des Rechners führt ein Virtualenv (`~/venv3.12`) ohne Zugriff auf Distributionspakete; `python3 -c 'import watchdog'` im Installationsskript hätte deshalb „fehlt" gemeldet, obwohl das Paket installiert und der Dienst lauffähig war — und das empfohlene `apt install` hätte dem Virtualenv nicht geholfen. Eine Sackgasse, in der der Nutzer die Schuld bei sich gesucht hätte. Innerhalb der Unit löst `python3` auf `/usr/bin/python3` auf, wo `watchdog` vorhanden ist. Beides ist jetzt derselbe, absolut benannte Pfad (3.5). Merksatz: Eine Prüfung, die einen anderen Interpreter trifft als die Ausführung, prüft das Falsche und meldet mit vollem Nachdruck das Falsche.
- **Ein gescheiterter Dialog war von einem vertagten nicht zu unterscheiden.** `ask_question` gab nur wahr/falsch zurück und verwarf die Fehlerausgabe; ob überhaupt ein Fenster erschienen war, ließ sich am Zustand nicht ablesen und musste beim Nutzer erfragt werden. Genau daran wäre im Betrieb ein Anzeigedefekt unbemerkt geblieben. Drei Ausgänge und die Behandlung stehen jetzt in 3.3.

**Zenity-Verhalten, eigens belegt** (ein Dialog, der eine Sekunde aufblitzte, mit Ankündigung gestartet): Zeitablauf endet mit Rückgabewert `5`. `--timeout` nimmt ausschließlich Sekunden — `15m` wird mit `255` abgewiesen, also mit einem Wert, den der Wächter als Fehlschlag einordnet; die naheliegende Schreibweise hätte jeden Dialog als kaputt gelten lassen. Und der aufschlussreichste Nebenbefund: Der **erfolgreiche** Dialog schrieb selbst eine GTK-Warnung über einen fremden Schlüssel in `~/.config/gtk-4.0/settings.ini` auf die Fehlerausgabe, und zwar bei jedem Aufruf. Der Fall „Abbruch trotz Geschwätz auf der Fehlerausgabe", der vorsorglich ins Prüfskript geschrieben worden war, ist auf diesem Rechner also der Normalfall. Vorsorge, die sich als Notwendigkeit entpuppt, ist ein Hinweis darauf, wie wenig die Rückgabewerte allein tragen.

**Dienstbetrieb, Stufe B** — `watch_forever` als dauerhafte Benutzer-Unit, gemessen im Trockenmodus. Der Trockenmodus ist hier nicht Bequemlichkeit, sondern Voraussetzung der Messung: Ein echter Dialog blockiert den Durchgang, **bevor** er seine Bilanzzeile schreibt, womit die Reaktionszeit nicht mehr ablesbar wäre. Dass der Dialog aus einer Unit heraus erscheint, ist in Stufe A belegt; hier geht es allein um das Ereignis. Ergebnis: Der Startlauf lief unmittelbar (`[startup scan] 0 conflict(s)`), und zwischen dem Anlegen der Konfliktkopie (21:01:15.4725) und der Protokollzeile des Wächters (21:01:15.4743, `[event:created] 1 conflict(s)`) lagen **1,8 Millisekunden**. Der Sicherheits-Suchlauf wurde also gar nicht gebraucht; die Ereignisbeobachtung trägt unter systemd. Die Unit ließ sich sauber anhalten.

Damit ist Fahrplanpunkt 3 in der Sache erledigt: Anzeigeverbindung, Dialog, Ereignisse und Journal sind im Dienstkontext belegt.

Nachgezogen wurde später die **dritte** Ereignisart: Der Wächter behandelte Anlegen und Verschieben, aber nicht das Löschen — eine verschwundene Kopie beendete die Episode erst beim Sicherheits-Suchlauf. Als Dienst geprüft: Nach dem Anlegen stand `conflict_active` auf `True`, nach dem Löschen binnen zwei Sekunden auf `False`, im Journal `[event:deleted] 0 conflict(s)`. Aufgefallen ist der Mangel nicht im Betrieb, sondern beim Nachsehen wegen einer ganz anderen Zahl — der Rechenzeit des Dienstes (3.1).

**Dienst installiert und im Betrieb** (Rechner A, 11. August 2026): `install_service.sh` lief ohne Beanstandung durch — Anmeldeprüfung, Interpreterprüfung, Einrichtung, `enable --now`. Erster Betriebsbefund, unmittelbar danach erhoben: Das Journal enthält **nur** die Startzeile, weil der Startlauf nichts fand und ein leerer Befund bewusst schweigt (3.5) — genau die Entscheidung, die sich in einem Ordner bezahlt, in den Claude Code laufend schreibt. Die Zustandsdatei liegt in `~/.claude-sync-watch`, also **außerhalb** des abgeglichenen Ordners; läge sie darin, wäre sie der erste Kandidat für einen Dauerkonflikt, da jeder Rechner sie anders schreibt. Die REST-Anbindung arbeitet am echten Bestand: Sie hat die Verbindung zur Synology mit Zählerstand und `startedAt` als Vorwert erfasst. Keine Neustarts, 2,2 MB Speicher. Zur ersten Betriebsmeldung: Sie kann nur Nullen zeigen, weil ein Zuwachs einen Vorwert braucht — der entsteht erst mit ihr.

**Pause-Meldung — kalt geprüft, im Vollzug offen.** Dass eine von Hand gesetzte Pause gemeldet wird, ist die Umsetzung einer Zusage, die Kapitel 1 schon enthielt, während der Code das Feld gar nicht las (aufgefallen im Kapitel-1-Review des Entwicklers, nicht in einem Test). Geprüft ist sie bisher **ohne Eingriff in den laufenden Betrieb**, in zwei Stufen: fünf Fälle im Prüfskript mit vorgetäuschter REST-Antwort — Pause allein, Pause neben offenen Konflikten, ohne Pause kein Zusatz, angehaltenes Gerät als fehlende Verbindung —, und der echte Lesepfad gegen die laufende Syncthing-Instanz, rein lesend: Freigabe gefunden, `paused` gelesen, Kennzahlen vollständig. Am echten Bestand bestätigt ist außerdem, dass `paused` auf Freigabe, Gerät und Verbindung steht.

**Damit bleibt ein eigenständiger Handtest offen** — er lässt sich nicht kalt führen, weil er einen echten Eingriff verlangt: Freigabe `~/.claude` in Syncthings Oberfläche **anhalten**, die nächste fällige Betriebsmeldung abwarten (bis zu eine Stunde, siehe 1.7) und prüfen, dass sie „Abgleich für diesen Ordner angehalten …" zeigt und zwölf Sekunden stehen bleibt; danach fortsetzen und prüfen, dass die nächste Meldung wieder die Ruheform hat. Wer dabei zusätzlich einen Konflikt offen hat, sieht die zweite Form, in der die Pause **neben** der Konfliktzahl steht. Solange dieser Test nicht gelaufen ist, gilt: Der Weg ist geprüft, die Wirkung am Bildschirm nicht. Ebenso ungeprüft bleibt, ob der Dienst mit dieser Fassung überhaupt läuft — die Änderung ist bewusst **nicht** in die laufende Installation kopiert worden (Stand vom 12. August 2026).

**Offen bleibt** in diesem Bereich nur noch Kleinkram, jeweils mit dem Grund, warum es offen ist: der Sicherheits-Suchlauf alle fünfzehn Minuten (beobachtbar nur durch fünfzehn Minuten Warten; die Schleife selbst ist trivial), `Restart=on-failure` (verlangt ein herbeigeführtes Absterben), und die **eigentliche** Installation nach `~/.config/systemd/user/` samt `~/.claude-sync-watch` — die liegt beim Nutzer, weil 1.2 Änderungen außerhalb der Projektwurzel verbietet und `install_service.sh` bewusst nichts an seiner Stelle einrichtet (3.5).

Auch die **Verteilung der Kopie samt Namen** ist damit belegt und nicht mehr nur doku-gestützt: Dieselbe Datei `Konflikttest.sync-conflict-20260811-175245-3PDLNDG.txt` lag anschließend auf FWFE41 — also unter einem Namen, der dort die **eigene** Kennung trägt. Das ist genau der Fall, an dem eine Prüfung „ist das meine Kennung?" gescheitert wäre.

**Doku-belegt, aber noch nicht selbst geprüft** (Quellen in der Konfigurationsanleitung): die `.stignore`-Semantik, die Versionierungsregeln, das Zeitverhalten.

**Betrieb auf beiden Rechnern, vom Nutzer bestätigt** (11. August 2026). Der Dienst ist auch auf FWFE41 installiert und läuft; damit gilt die Zwei-Wächter-Lage aus 1.6 nicht mehr als Entwurf, sondern als Betriebszustand. Der Testordner ist auf beiden Rechnern gelöscht und seine Freigabe entfernt — die Restpunkte der Testreihe waren dort verortet und sind unten neu zugeordnet.

Drei Aussagen, die vorher nur doku-belegt waren, sind damit am echten Bestand geprüft:

- **Weitergabe einer Löschung.** Nach der Auflösung auf dem Laptop war die Konfliktkopie auf FWFE41 ebenfalls verschwunden. Das ist der Beleg für die vollständige Argumentation in 1.6 gegen das selbsttätige Anhalten: Sie steht und fällt damit, dass Löschung und Schreiben von selbst mitwandern.
- **Selbstschließender Dialog.** Der Dialog auf FWFE41 schloss sich — und zwar, wie vorhergesagt, fünfzehn Minuten nach seinem **Erscheinen**, nicht nach der Auflösung: Zum Zeitpunkt der Auflösung fehlten noch zwei Minuten. Danach kein Fund, keine Meldung. Genau der Ablauf aus 1.6 und 3.3.
- **Ausschlussmechanik.** Eine neu angelegte `testfile.log` erschien auf dem anderen Rechner nicht, auch nicht nach von Hand ausgelöstem Abgleich an allen drei Geräten über die Weboberfläche. Damit ist T5 vollständig: der Index-Befund zu `.credentials.json` (unten) belegt den Bestand, dieser Versuch den Vorgang.
- **T7 beantwortet, und F7 hat seinen ersten Befund.** Bei der Erstverbindung der beiden nicht-leeren `~/.claude` entstanden **keine** Konfliktkopien. Und weitergehend: Bis heute ist **kein einziger** Konflikt von den Claude-Instanzen selbst erzeugt worden — der Konflikt, an dem die Kette geprüft wurde, musste vom Nutzer herbeigeführt werden. Was `.stignore` übriglässt, kollidiert im gelebten Betrieb also bislang nicht. Das ist eine gute Nachricht mit einer unangenehmen Kehrseite: Der Wächter wird selten anspringen, und ein Mechanismus, der selten läuft, ist genau der, dessen Defekte niemand bemerkt. Es ist der Grund, warum die Belegführung hier so ausführlich ist und warum das Prüfskript existiert.

**Zwischendateien beim Empfang — ein Defekt, den keine Messung gefunden hat, sondern die Frage danach.** Zur Vorbereitung des T8a-Versuchs war zu erklären, wie man ihn durchführt; beim Formulieren fiel auf, dass die Behauptung in 3.1 („Zwischenzustände entsprechen nie dem Suchmuster") nicht haltbar ist. Der Zwischenname enthält den Zielnamen, also enthält er bei einer eingehenden Konfliktkopie auch den Marker. Nachgestellt ohne Syncthing, in einem Wegwerfordner: Der Wächter meldete `.syncthing.Konflikttest.txt.tmp (Gerätekennung 3PDLNDG)` — ein Paar, dessen Original nie existiert hat.

Bemerkenswert ist, wo der Widerspruch lag: **im übernächsten Absatz derselben Sektion**, der schon richtig beschrieb, dass die Kopie auf den übrigen Geräten „aus der Zwischendatei hereingeschoben" wird. Zwei benachbarte Absätze, einer die Widerlegung des anderen, monatelang unbemerkt — weil die Behauptung so plausibel war, dass niemand sie nachrechnete. Behoben durch einen Namensfilter (3.1); der Schaden wäre begrenzt gewesen, weil die Sitzung laut Anweisung selbst neu sucht und die überreichte Liste nur orientiert (3.4, Schritt 1) — die Sicherung an anderer Stelle hätte den Fehler also verdeckt, statt ihn auffallen zu lassen.

**Testplan T1–T8, abgeglichen** (Stand: Dienst auf Rechner A installiert). Die Reihe war für die Hilfsordner-Phase gedacht. Da `~/.claude` inzwischen angebunden **ist**, wird sie nicht mehr der Reihe nach abgearbeitet, sondern nach verbleibendem Nutzen sortiert: Was trägt eine Aussage, auf die sich Code oder Doku stützen, und was ist bloß eine Zahl?

**Belegt:**

- **T1 Einseitige Änderung** — vollständig. Anlegen und Ändern im Testordner beidseitig beobachtet; die Weitergabe einer **Löschung** ist am echten Bestand bestätigt (oben). Letzteres trägt die Argumentation in 1.6 gegen das Anhalten.
- **T3 Konflikt** — durchgeführt, in der Pausen-Variante statt „beide Rechner offline". Gleichwertig, weil Syncthing über Versionsvektoren entscheidet und nicht über Uhrzeiten (1.5); die Pause auf **einem** Rechner genügt, um die Divergenz herzustellen.
- **T4 Maschinelle Auffindbarkeit** — durchgeführt, reales Namensformat protokolliert und im Prüfskript festgenagelt. Der Test hat dabei mehr geleistet als bestätigt: Er hat den Irrtum über `<modifiedBy>` aufgedeckt (oben, 3.1 Schritt 2).
- **T5 Ausschlusstest** — vollständig. Der Vorgang ist mit `testfile.log` bestätigt (oben), der Bestand über den Index, und zwar ohne eine Datei anzulegen: `~/.claude/.credentials.json` existiert lokal (509 Bytes, `rw-------`), ist in Syncthings Index aber **überhaupt nicht vorhanden** — gelesen über `/rest/db/file`, rein lesend. Gegenprobe an derselben Freigabe: `CLAUDE.md`, `settings.json` und `history.jsonl` stehen dort als abgeglichen, die Freigabe arbeitet also. Syncthing hat 21 Muster fehlerfrei geladen.

  Eine Feinheit, die man kennen muss, um solche Befunde künftig richtig zu lesen: Ausgeschlossen heißt **nicht** zwangsläufig „nicht im Index". `telemetry` und `shell-snapshots` **stehen** im Index, markiert als `ignored` und `invalid` (letzteres zusätzlich als `deleted`) — sie sind vom Transport ausgenommen, aber als Eintrag vorhanden. „Gar nicht im Index" ist der starke Fall, „als ignoriert markiert" der übliche. Wer nur nach dem Namen sucht und ihn findet, zieht sonst den falschen Schluss.

**Die drei Restpunkte sind erledigt**, aber nicht so, wie geplant — was der Bemerkung wert ist:

- **Löschweitergabe** und **T5-Mechanik** hat der Nutzer am echten Bestand bestätigt (oben), nicht im Testordner; der ist inzwischen gelöscht.
- **T8a** ist nicht durch Beobachtung erledigt, sondern durch das Gegenteil: Die Frage „wie prüfen wir das?" hat die zugrunde liegende Behauptung widerlegt. Nachgestellt wurde der Fall dann synthetisch, weil er sich ohne Syncthing vollständig herstellen lässt.

**Was dabei ungeprüft bleibt und benannt werden muss:** Der **reale** Zwischenname ist nie gesehen worden. Der Filter stützt sich auf das dokumentierte Format (`.syncthing.<name>.tmp`, unter Windows `~syncthing~…`) und auf die synthetische Nachbildung — nicht auf eine Beobachtung am laufenden System. Benennt eine künftige Syncthing-Fassung ihre Zwischendateien anders, greift der Filter nicht mehr, und der Fehler kehrt zurück. Das einmal im Betrieb zu sehen — beim Empfang einer größeren Datei nach `~/.claude` schauen, ob dort kurz eine `.syncthing.*`-Datei auftaucht — ist der letzte offene Handgriff dieser Reihe. Er ist billig und gehört in die Beobachtungsphase.

**Offen und entbehrlich**, mit Grund — damit später niemand meint, hier sei etwas vergessen worden:

- **T2 Vermittlung** — die Topologie ist ein Stern über die Synology, jede Übertragung läuft ohnehin über den Knoten. Der zusätzliche Aussagegehalt wäre allein „geht auch, während A aus ist"; darauf stützt sich nichts im Entwurf.
- **T6 Zeitverhalten** — eine Zahl, keine Annahme. Der Wächter reagiert auf das, was ankommt, wann immer es ankommt.
- **T7 Erstverbindung nicht-leerer Bestände** — von der Wirklichkeit überholt: `~/.claude` wurde auf FWFE41 tatsächlich erstverbunden. Ob dabei Konfliktkopien entstanden, ist beim Nutzer zu **erfragen**, nicht nachzustellen.
- **T8 Wachsende Datei** — bleibt interessant für F7, aber keine Entscheidung im Code hängt daran.

Nebenbefund für F7: `history.jsonl` wird abgeglichen und ändert sich fortlaufend — der erste Kandidat für reale Konfliktkopien.

---

# Anhang: Fragenkatalog

Vor Implementierungsbeginn zu klären (Fahrplan-Punkt 1). Je Frage: Entscheidung treffen, Ergebnis in das zuständige Kapitel einpflegen, Frage hier streichen.

*(F1 und F2 sind entschieden und in 1.6, 1.7, 1.8, 2.1, 3.1, 3.2 und 3.4 eingearbeitet: kein selbsttätiges Anhalten des Abgleichs — Begründung samt verworfener Gegenposition in 1.6 —, Übergabe aller Konflikte auf einmal, Lösung immer nur an einem Rechner, Anhalten als Empfehlung der Sitzung im Ausnahmefall, Sitzungserkennung über die PID. Die Nummerierung der übrigen Fragen bleibt unverändert.)*

**F3 — Dateien in Benutzung durch die laufende Instanz.** *Zurückgestellt: nicht gelöst, Verhalten bei der Nutzung zu beobachten, möglicherweise gar nicht einschlägig.*

Die Konfliktsitzung ist selbst eine laufende Claude-Instanz mit `~/.claude` als Arbeitsverzeichnis. Der Abgleich steht zu diesem Zeitpunkt bereits (1.6), die Frage ist also **rein lokal**: Kann das Überschreiben einer Datei die Instanz stören, die zeitgleich in demselben Ordner arbeitet?

Für den größten Teil des Ordners ist das unwahrscheinlich — was die Instanz selbst anlegt (ihr eigenes Sitzungsprotokoll, Sitzungs- und Schnappschussdateien) trägt je Sitzung eigene Namen und kann mit einer Konfliktkopie kaum zusammentreffen. Für die wenigen gemeinsam genutzten Dateien im Ordnerkopf ist es offen.

Zwei Beobachtungspunkte für die Nutzungsphase, damit später klar ist, worauf zu achten war:

- Stört das Überschreiben einer Datei die laufende Sitzung sichtbar?
- Schreibt die Instanz beim Beenden eine der aufgelösten Dateien aus einem eigenen Zwischenstand zurück und verwirft damit die Lösung unbemerkt?

Tritt eines von beidem auf, wäre eine Reihenfolge-Regel (kritische Dateien zuletzt, danach Neustart der Sitzung) der naheliegende Ansatz. Bis dahin wird nichts vorgesehen. Gemeinsam mit F7 in der Beobachtungsphase zu klären. (Betrifft 3.4.)

*(F4 ist entschieden und in 3.1 und 3.5 eingearbeitet: dauerhafter Dienst mit Beobachtung über das Betriebssystem via `watchdog`, verzögerungsfreier Eingriff, Suchlauf beim Start, Sicherheits-Suchlauf alle 15 Minuten, kein Timer.)*

*(F5 ist entschieden und in 2.7, 3.1, 3.3, 3.4 und 3.5 eingearbeitet: alles in einem Ordner `~/.claude-sync-watch/`, Übergabe der Arbeitsanweisung per `--append-system-prompt-file`, Hilfsmittelverzeichnis per `--add-dir`, Aufruf mit absolutem Pfad `/usr/bin/claude`.)*

*(F6 ist durch den Betriebstest entschieden und in 3.4 eingearbeitet: **kein** Zenity-Erfolgsdialog — der Bericht steht schon vor dem Nutzer, ein Fenster obendrauf wäre die Aufdringlichkeit, die 2.9 vermeiden will. Stattdessen schließt die Sitzung mit einem ausdrücklichen Satz, dass die Bearbeitung beendet ist und das Fenster geschlossen werden kann. Im Test war genau dessen Fehlen die einzige offene Stelle: Der Bericht kam, danach stand die Sitzung stumm, und der Nutzer konnte nicht wissen, ob noch etwas folgt. Die Berichtsform selbst — betroffene Paare, Entscheidung je Paar, Geschriebenes und Gelöschtes, Ausschlüsse — hat sich unverändert bewährt.)*

**F7 — Reale Konfliktkandidaten.** In den ersten Betriebswochen beobachten, welche Dateien tatsächlich Konfliktkopien erzeugen (auch: ob `file-history/` kollidieren kann), und daraus ableiten, ob weitere Ausschlüsse (1.3 Offen-Punkt) oder Sonderbehandlungen nötig sind. (Betrifft 1.3, 1.5.)

Erste Befunde aus dem Betrieb, bevor die Wochen gezählt sind: Bei der Erstverbindung zweier nicht-leerer `~/.claude` entstand **keine** Konfliktkopie; ein Wechsel des Claude-Kontos in Desktop und VSCode-Erweiterung erzeugt ebenfalls keine (Begründung in 1.3: Kontozustand liegt ausgeschlossen oder außerhalb des Ordners); und bis zum 12. August 2026 hat **keine** Claude-Instanz von sich aus einen Konflikt erzeugt. Der Konflikt, an dem die Kette geprüft wurde, musste herbeigeführt werden. Das verschiebt die Frage: Nicht „welche Dateien kollidieren?" ist bisher das Thema, sondern ob überhaupt je eine kollidiert — und wie man einen Mechanismus vertrauenswürdig hält, der monatelang nichts tut (3.8).

*(F8 ist entschieden und in 2.8 sowie 3.5 eingearbeitet: maßgebliche Fassung im Werkzeugordner, versioniert im Repo, Vergleich mit Warnung bei der Installation, keine laufende Überwachung.)*

*(F9 ist entschieden und in 1.9 eingearbeitet: Erkennungsmerkmale, achtstufiger Ablauf, Sitzungen zuerst beenden und erst dann urteilen, Sicherung vor dem Pausieren, einzelne Dateien statt ganzer Ordner, Prüfung auf beiden Rechnern vor dem Wiedereinschalten.)*

*(F10 ist entschieden und in 1.7, 3.1 und 3.2 eingearbeitet: Bytes je Richtung und Rückstand, Einheitenwechsel bei einem Zehntel, Anzeigedauer nach Inhalt (5 s bzw. 12 s), fehlende Verbindung im selben Meldungsweg mit Vorspann, keine Frist ohne Bezugspunkt, stündlich unverändert.)*
