# Chrome-Zugriff — systematischer Test der Bridge

Diese Datei trägt den vollständigen, systematischen Testweg zur Chrome-Anbindung von Claude Code (VS-Code-Erweiterung) — wie sie tatsächlich zustande kommt und woran sie hängt. Sie wurde für den Skill `chat-export` (Web-Weg) angelegt, ist aber unabhängig von dessen übriger Doku lesbar.

**Rechner:** durchgehend derselbe (Chrome, VS-Code-Erweiterung, `@browser`-Mechanik).

## Stufe 0 (Vortag, 20./21. August): Vorbefunde

Kurz zusammengefasst:

- Eine Nachricht ohne `@browser` liefert keinen Browserkontext — die Werkzeuge sind zwar in der Liste, antworten aber „Browser extension is not connected".
- Der Connector-Schalter auf claude.ai (Einstellungen → Connectors → „Claude in Chrome") muss für das jeweils aktive Konto eingeschaltet sein, sonst kommt „Claude in Chrome is turned off in your settings". Wirkt nicht rückwirkend auf schon offene Tabs.
- Abmelden von claude.ai im Tab: Die Bridge selbst blieb erreichbar (Navigation, Skriptausführung), nur der claude.ai-API-Aufruf schlug mit `account_session_invalid` fehl. Getestet auch auf fremden Domains (gmx.de, example.com) — Bridge funktioniert dort ebenso, ist also nicht auf claude.ai beschränkt.

## Stufe 1 (heute, 22. August): Ausgangslage „überall dasselbe Konto"

**Ausgangslage laut Nutzer:** Vor dem heutigen Test war überall — Chrome, diese Claude-Code-Sitzung, Claude Code CLI — mit demselben Pro-Konto gearbeitet worden.

**1a — Chrome geschlossen, `@browser` in der ersten Nachricht angekündigt, aber noch nicht gesendet.** Kein Zugriffsversuch nötig, reine Ankündigung.

**1b — Chrome läuft (leerer Tab), Nachricht kam ohne `<browser>`-Kontextblock trotz `@browser`-Erwähnung.** `tabs_context_mcp` → „Browser extension is not connected". Auffällig: Der MCP-Server hatte sich laut Systemmeldung neu verbunden, aber das reichte allein nicht — es kam kein nutzbarer Browserkontext mit.

**1c — Chrome läuft, weiterhin kein Zugriff.** Nutzer öffnete das Erweiterungssymbol in Chrome: Die Erweiterung selbst zeigte sich als **nicht angemeldet** (getrennt von der claude.ai-Website-Anmeldung im Tab — es geht um den Login der Erweiterung, sichtbar über „Claude öffnen"). Zwei mögliche Ursachen offen: Anmeldung verfällt beim Schließen von Chrome, nach einer Zeitspanne, oder bei einem Rechner-Neustart. Nicht unterschieden.

**1d — Nutzer meldet sich in der Erweiterung neu an** (vollständiger Anmelde-Turn per E-Mail-Link). Danach `tabs_context_mcp` → **Erfolg**, ein Tab wurde bereitgestellt.

**1e — Erste Navigation nach der Neuanmeldung meldete Erfolg, war aber nicht wirklich passiert.** `navigate` auf `gmx.de` lieferte eine Erfolgsantwort mit Titel „www.gmx.de", aber eine erneute `tabs_context_mcp`-Abfrage zeigte den Tab weiterhin als leeren `chrome://newtab/`. Eine zweite Navigation zum selben Ziel funktionierte dann tatsächlich (vom Nutzer im Tab bestätigt). **Lehre: unmittelbar nach einer Neuanmeldung ist der Werkzeugmeldung nicht ohne Sichtprüfung durch den Nutzer zu trauen — es gibt offenbar eine kurze Verzögerung, bevor die Erweiterung tatsächlich reagiert.**

**Zwischenfazit Stufe 1:** Weder Chrome-Start noch `@browser`-Text allein genügt. Entscheidend war die **Anmeldung der Chrome-Erweiterung selbst**.

## Stufe 2 (heute): claude.ai-Website-Konto wechseln, Erweiterung bleibt angemeldet

**2a — Nutzer meldet sich auf claude.ai im Tab ab** (Pro-Konto). Die Erweiterung selbst bleibt eingeloggt — beim Anklicken des Erweiterungssymbols lässt sich weiterhin ein Chat einblenden, mit dem eine Verbindung besteht.

**2b — Zugriff geprüft:** `tabs_create_mcp` scheiterte zunächst, weil die alte Tab-Gruppe durch das Schließen der Tabs ungültig geworden war („This session's tab group no longer exists"); `tabs_context_mcp --createIfEmpty` legte sofort einen neuen Tab an. **Bridge funktioniert weiterhin trotz Abmeldung auf claude.ai.**

**2c — `gmx.de` aufgerufen und vom Nutzer als geladen bestätigt.** Funktioniert.

**2d — Nutzer meldet sich auf claude.ai im selben Tab mit einem *anderen* Konto an** — dem **Team-Konto** („Dienstkonto"), nicht dem ursprünglichen Pro-Konto.

**2e — Zugriff erneut geprüft:** neuer Tab angelegt, `gmx.de` geladen (vom Nutzer bestätigt), dann `https://claude.ai/api/organizations` aufgerufen:

```json
[{"name": "HZDR - FWF", "uuid": "4efe0308…"}]
```

Das ist das **Team-Konto**, nicht das ursprüngliche Pro-Konto (`e2cea7f9…`, „herbrand@gmx.de's Organization").

**Ergebnis Stufe 2, vorläufig:** Die Bridge folgt offenbar einfach der **aktuellen claude.ai-Websitzung im Tab** — sie liest das gerade gültige Sitzungs-Cookie, unabhängig davon, mit welchem Konto Claude Code oder die Chrome-Erweiterung ursprünglich verbunden wurden. Es scheint **keine feste Kontobindung der Bridge selbst** zu geben; ein Kontowechsel im Tab genügt, um die API-Antworten auf das neue Konto umzustellen.

**Wichtige Einschränkung dieses Befunds:** Die Ausgangslage in Stufe 1 war „überall dasselbe Konto" — die Bridge wurde also ursprünglich mit dem Pro-Konto aufgebaut und der Kontowechsel geschah erst *danach*, an einer schon bestehenden Verbindung. Ob eine Bridge sich auch **von Anfang an** mit einem abweichenden Konto aufbauen lässt — wenn Chrome/die Erweiterung von vornherein mit einem anderen Konto arbeitet als Claude Code selbst —, ist damit noch **nicht** geprüft. Das ist Gegenstand der nächsten Stufe.

## Stufe 3: Rechner-Neustart, Chrome von Beginn an mit dem Team-Konto — durchgeführt, Ergebnis uneindeutig

Ausgangslage: Nutzer bootete den Rechner neu, meldete sich in Chrome von Beginn an mit dem **Team-Konto** an — nicht als nachträglicher Wechsel wie in Stufe 2, sondern als Ausgangszustand vor jedem Verbindungsversuch.

**Vorbefund, unabhängig vom eigentlichen Test:** Die Chrome-Anmeldung selbst überlebt einen Rechner-Neustart. Nach dem Neustart war weiterhin ein Konto in Chrome angemeldet, ohne dass sich der Nutzer aktiv neu anmelden musste — das ist offenbar von Anthropic serverseitig festgelegt (Sitzungsdauer), nicht an den Rechner-Neustart gekoppelt.

**Ablauf, jeder Schritt mit `tabs_context_mcp` geprüft:**

1. Team-Konto in Chrome angemeldet, leerer Tab offen, `@browser` gesetzt → **„Browser extension is not connected."** (Zweifach geprüft, gleiches Ergebnis.)
2. Erweiterungssymbol angeklickt — separates Prompt-Fenster öffnet sich, dort weiterhin angemeldet → **weiterhin „not connected"**.
3. Erweiterungs-Optionen aufgerufen (derselbe Weg, der vorhin in Stufe 1 zum Durchbruch geführt hatte) → **weiterhin „not connected"**.
4. Nutzer meldet sich mit dem **Pro-Konto** neu an, vollständiger E-Mail-Turn (identischer Schritt wie in Stufe 1d, der dort funktionierte) → **weiterhin „not connected"**, auch bei einem zweiten Versuch kurz danach.
5. Nutzer führt einen echten Chat-Turn **innerhalb der Erweiterung selbst** aus (im kleinen Chat-Fenster der Erweiterung) — die Erweiterung spricht damit nachweislich erfolgreich mit claude.ai → **weiterhin „not connected"** für die Bridge zu dieser Claude-Code-Sitzung.
6. Nutzer schickt erneut `@browser` — diesmal meldet die VS-Code-Oberfläche selbst einen Fehler: **„no Files"**, ein dritter, bisher nicht gesehener Fehlermodus. Kein Test mehr durchgeführt, Nutzer kündigt Sitzungsneustart an.

**Vorläufige Deutung.** Anders als in Stufe 1/2 half hier weder ein Kontowechsel noch eine erneute Anmeldung noch ein nachweislich funktionierender Turn innerhalb der Erweiterung selbst. Das spricht dagegen, dass allein die Kontokonstellation die Ursache ist — es deutet stärker darauf hin, dass die Bridge-Verbindung dieser konkreten Claude-Code-Sitzung in einen Zustand geraten war, aus dem sie sich nicht mehr von selbst löste, und dass die Häufung der Fehlversuche mit dem Team-Konto möglicherweise selbst zum Auslöser wurde statt nur ein neutraler Testschritt zu sein. Der abschließende „no Files"-Fehler auf VS-Code-Seite (nicht von der Bridge, sondern von der Oberfläche selbst) stützt das: Er trat auf, *bevor* überhaupt ein neuer Bridge-Versuch stattfand.

**Damit ist Stufe 3 nicht sauber entscheidbar.** Weder eindeutig bestätigt noch widerlegt: ob ein Bridge-Erstaufbau mit einem von Claude Code abweichenden Konto grundsätzlich scheitert. Der Test müsste mit einer frischen, erwiesenermaßen funktionsfähigen Sitzung wiederholt werden, bei der von Beginn an ein abweichendes Konto in Chrome aktiv ist — ohne die Vorgeschichte aus Schritt 1–5, die den Zustand der aktuellen Sitzung verunreinigt haben könnte.

**Nächster Schritt:** Sitzungsneustart durch den Nutzer angekündigt. Fortsetzung nach dem Neustart, mit sauberer Ausgangslage.

**Zwischenschritt (noch mit Pro-Konto):** Sitzungsneustart allein hatte noch nicht geholfen. Danach: Chrome-Neustart, Abmeldung, Neuanmeldung mit dem **Pro-Konto** (diesmal ohne E-Mail-Turn) → Zugriff funktioniert wieder.

## Stufe 3, sauberer Wiederholungsversuch: Team-Konto von Anfang an — bestanden, eindeutig

Nutzer startete danach den **ganzen Rechner** neu (nicht nur Chrome). In Chrome direkt nach dem Neustart eine **neue** Anmeldung auf claude.ai vorgenommen — diesmal mit dem **Team-Konto**, vollständiger E-Mail-Turn. Diese Claude-Code-Sitzung selbst blieb währenddessen mit dem **Pro-Konto** verbunden — die Konten liefen also von Beginn an bewusst auseinander, keine Angleichung.

**Erster `@browser`-Versuch nach dem Rechner-Neustart, `tabs_context_mcp`:** sofortiger Erfolg, Tab bereitgestellt. Kein Fehlschlag, keine Wiederholung nötig.

**Ergebnis, jetzt eindeutig — anders als der frühere, wahrscheinlich verfrühte Stufe-3-Versuch weiter oben:** Der Bridge-Aufbau gelingt **auch dann**, wenn das in Chrome bei claude.ai angemeldete Konto (Team) von Anfang an vom Konto abweicht, mit dem diese Claude-Code-Sitzung selbst arbeitet (Pro). **Die Frage nach übereinstimmenden Konten ist damit geklärt: Eine Übereinstimmung ist nicht erforderlich.**

Was tatsächlich zählt, nach dem gesamten heutigen Test zusammengefasst:

1. Chrome muss laufen und bei claude.ai angemeldet sein (irgendein Konto, mit funktionierendem Connector-Schalter, s. Stufe 0).
2. Die Erweiterung selbst muss arbeiten — erreichbar am funktionierenden Chat-Turn innerhalb der Erweiterung als Testkriterium.
3. Ist beides erfüllt, funktioniert `@browser` in dieser Claude-Code-Sitzung zuverlässig, unabhängig vom jeweiligen Konto.

**Der frühere Stufe-3-Fehlschlag (weiter oben) bleibt damit ungeklärt in seiner Ursache**, ist aber nicht mehr als Beleg gegen den kontounabhängigen Aufbau zu lesen — vermutlich lag dort tatsächlich ein anderer, nicht mehr rekonstruierbarer Sitzungs- oder Erweiterungszustand vor (siehe die dortige Deutung: gehäufte Fehlversuche, „no Files"-Fehler auf VS-Code-Seite).

## Stufe 4: Zugriff auf bestehende Tabs — eigene, isolierte Tab-Gruppe, kein Zugriff auf vom Nutzer geöffnete Tabs

Frage des Nutzers: Kann diese Sitzung einen vom Nutzer bereits geöffneten Chrome-Tab (hier: claude.ai, manuell geöffnet) finden und mitbenutzen, oder muss stets ein eigener, neuer Tab angelegt werden?

**Test.** `tabs_context_mcp` **ohne** `createIfEmpty` meldete zuerst: „No tab group exists for this session." — nicht etwa eine leere Liste, sondern das vollständige Fehlen jeder Sichtbarkeit auf vorhandene Tabs. Danach `tabs_context_mcp` **mit** `createIfEmpty: true`: Es wurde ein **neuer, leerer** Tab angelegt (`chrome://newtab/`) — nicht der vom Nutzer bereits offene claude.ai-Tab.

**Ergebnis: Es gibt keinen Zugriff auf vom Nutzer manuell geöffnete Tabs.** Jede Claude-Code-Sitzung arbeitet in einer eigenen, isolierten „MCP-Tab-Gruppe", die getrennt von den regulären Chrome-Tabs des Nutzers ist. Um mit claude.ai zu arbeiten, muss stets **selbst** dorthin navigiert werden — verlässt sich dabei aber auf dieselbe Chrome-weite Anmeldung/Sitzung, die auch der manuell geöffnete Tab nutzt (s. Stufe 0–3: die Anmeldung ist Chrome-weit, nicht Tab-gebunden).

**Folge für den Skill:** Er kann und muss sich beim Start selbst einen Tab anlegen (`tabs_create_mcp` bzw. implizit über `tabs_context_mcp --createIfEmpty`) und braucht dafür keine Vorbereitung durch den Nutzer außer einer bestehenden Chrome-Anmeldung — ein vom Nutzer vorab geöffneter claude.ai-Tab ist weder nötig noch nutzbar.

**Nachtrag, eigener Fehler geklärt.** Direkt danach ließ sich der angelegte Tab scheinbar nicht ansteuern — das lag aber nicht an der Bridge, sondern daran, dass nur `tabs_context_mcp` geladen war, nicht `navigate`. Mit `navigate` (Tool nachgeladen) funktionierte die Steuerung desselben Tabs sofort und einwandfrei (`navigate` zu `claude.ai` erfolgreich). Kein neuer Befund über die Bridge, nur eine Erinnerung: Für einen angelegten Tab müssen die eigentlichen Aktionswerkzeuge (`navigate`, `computer`, `javascript_tool`, `find`, …) zusätzlich zu `tabs_context_mcp` geladen sein.

## Stufe 5: Sichtbarkeitsverwechslung bestätigt, und ein neuer Chat wird per Oberfläche geschrieben und danach strukturiert ausgelesen

**Direkte Bestätigung der Tab-Isolation aus Stufe 4.** Der Nutzer hatte zusätzlich zu meinem selbst angelegten Tab einen weiteren, manuell geöffneten Tab „Neuer Chat - Claude" in Chrome offen und bat mich, genau diesen zu finden und zu benutzen. `tabs_context_mcp` listete jedoch **nur** meinen eigenen Tab (dieselbe `tabId` wie zuvor), der durch die vorherige Navigation zu `claude.ai` automatisch auf `/new` weitergeleitet worden war und zufällig denselben sichtbaren Titel trug. Beim ersten Tippversuch beobachtete der Nutzer den falschen (den eigenen, manuell geöffneten) Tab und sah dort kein „Hallo!" erscheinen; erst als er auf meinen tatsächlichen Tab wechselte, war der eingetragene Text sichtbar. **Damit ist bestätigt, nicht nur vermutet: Es gibt keinerlei Möglichkeit, versehentlich oder absichtlich in einen vom Nutzer manuell geöffneten Tab zu geraten — die Isolation der MCP-Tab-Gruppe ist vollständig.**

**Ein Chat wurde vollständig über die Oberfläche geschrieben** (Klick ins Eingabefeld über `find` + `computer left_click`, `computer type` für „Hallo!", `computer key Return` zum Absenden) — nicht über die API. Der Nutzer beobachtete den Bildschirm mit und bestätigte jeden Schritt, bevor der nächste erfolgte. Antwort erhalten: „Hallo! Schön, dass Du da bist. Womit kann ich Dir heute helfen?"

**Danach als strukturiertes JSON ausgelesen**, ganz ohne erneute Texterkennung von der sichtbaren Seite: Die Chat-UUID stand nach dem Absenden direkt in der Tab-URL (`https://claude.ai/chat/028964c2-…`), und derselbe Konversations-Endpunkt, den der Web-Weg benutzt, lieferte den vollständigen Turn zurück — `sender: "human"` mit „Hallo!", `sender: "assistant"` mit dem exakten Antworttext, beide mit vollen `content`-Blöcken, Status 200, 2 Nachrichten.

**Nebenbefund zur Kontofrage, an einem dritten unabhängigen Fall bestätigt:** Der Aufruf lief unter dem in Chrome aktiven **Team-Konto** (`HZDR - FWF`) — obwohl der Chat über die normale Bedienoberfläche entstand, nicht über einen gezielten API-Aufruf. Die Bridge liest also durchgehend die jeweils aktuelle claude.ai-Sitzung, unabhängig vom Konto dieser Claude-Code-Sitzung selbst.

**Folge für den Skill, über das bisher Beschriebene hinaus:** Er ist nicht nur in der Lage, vorhandene Chats zu lesen — er könnte grundsätzlich auch selbst einen neuen Chat anlegen (über die Oberfläche oder direkt über den API-Endpunkt) und ihn anschließend strukturiert exportieren. Das ist für dieses Vorhaben nicht vorgesehen, aber technisch belegt möglich.

## Stufe 6: Navigation über die linke Seitenleiste — „Startseite" funktioniert, „Code" führt nicht weiter

Auf Wunsch des Nutzers geprüft: die linke Seitenleiste der claude.ai-Oberfläche, mit den beiden Reitern „Startseite" und „</> Code".

**„Startseite" → Menüpunkt „Projekte":** Klick per Koordinate erfolgreich, Titel/URL wechselten zu „Projects - Claude" (`/cowork/projects`). Sichtbar dieselben fünf Projekte des Team-Kontos, die auch der direkte API-Aufruf (`/api/organizations/<org>/projects`) mit vollen Metadaten (`name`, `uuid`, `created_at`, `updated_at`, `is_private`) lieferte — Bildschirmansicht und JSON-Daten deckungsgleich.

**„Code"-Reiter:** Klick erfolgreich (`/code/family`), zeigt aber **keine** Liste von Code-Projekten, sondern eine allgemeine Werbeseite mit drei Kacheln — Terminal, IDE-Erweiterung, Web. Kein Menüpunkt „Projekte" wie auf der Startseite.

- **Terminal-Kachel:** zeigt nur einen Installationsbefehl (`curl -fsSL …`) für die lokale Installation von Claude Code; kein Start eines Terminals im Browser möglich. Links „Sessions, die du startest, werden hier angezeigt" — leer.
- **Web-Kachel („Claude Code Web starten"):** führt zu einer Onboarding-Seite (`/code/onboarding`) mit Repository-Auswahl und Eingabefeld, aber mit dem Hinweis: *„Für Claude Code im Web ist GitHub-Zugriff erforderlich. Bitte kontaktiere einen Organisationsinhaber."* Für dieses Konto also gesperrt; nicht abgesendet.
- **IDE-Erweiterung:** nicht weiter geprüft (Installationslink in eine IDE, kein Browser-Zugriff zu erwarten).

**Ergebnis: Über den Chrome-Tab lassen sich keine lokal in Claude Desktop (Code-Reiter) angelegten Claude-Code-Projekte erreichen.** Die „Code"-Ansicht in claude.ai ist auf das *Starten* neuer Sitzungen ausgelegt (Terminal-Installation, Web mit GitHub-Anbindung, IDE-Erweiterung), nicht auf das *Auflisten* bestehender lokaler Projekte. Für den Web-Weg heißt das: **Sinnvoll nutzbar ist im Chrome-Tab nur der „Startseite"-Bereich** — Chats und Projekte im herkömmlichen claude.ai-Sinn. Ob sich das künftig ändert (z. B. eine spätere Liste verbundener lokaler Projekte), ist Spekulation und wird hier nicht behauptet.

## Stufe 7: Erster echter Testlauf des Skill-Ablaufs — Team-Konto ohne Selbstbedienungs-Export, abgebrochen an einer Code-Lücke

**Ausgangslage.** Auf Wunsch des Nutzers wurde der geplante Skill-Ablauf erstmals real durchgespielt — nicht nur simuliert —, mit `chat_export_convert.py` als ausführendem Werkzeug, gegen das Team-Konto (`HZDR - FWF`), das in Chrome aktiv angemeldet war.

**Wichtiger Nebenbefund, der so noch nirgends stand:** Das Team-Konto hat **keinen Selbstbedienungs-Export** — anders als die Faustregel „Web-Weg für kleine Nachträge, sonst Kontoexport" nahelegt, ist der Web-Weg hier **die einzige Möglichkeit überhaupt**, nicht nur die bequemere. Deckt sich mit der bereits dokumentierten Kontotyp-Einschränkung (Doku 1.2/1.6: Team-/Enterprise-Mitglieder ohne Primary-Owner-Rechte haben keinen Export). **Folge für den Skill:** Er muss erkennen (oder sich sagen lassen) können, dass für ein Konto kein Export existiert, und darf dann den Export-Weg gar nicht erst als Alternative anbieten.

**Ablauf, Schritt für Schritt:**

1. Erster Haltepunkt gestellt und bestätigt.
2. Konto genannt (`HZDR - FWF`, einzige Organisation) und Projektliste geholt: 5 Projekte per `/api/organizations/<org>/projects`.
3. Nutzer wählte zwei Projekte zum Test: „Chats-Export, Test 1" und „Dresdyn-Kamerasystem-Überarbeitung".
4. Chatlisten beider Projekte geholt (`conversations_v2`): **„Chats-Export, Test 1" → 3 Chats**, **„Dresdyn-Kamerasystem-Überarbeitung" → 0 Chats** (`pagination.total: 0`, also echt leer, kein Abrufproblem).
5. Zweiter Haltepunkt: Web-Weg als **einzige** Option genannt (kein Export verfügbar), Nutzer bestätigte, **und** bat ausdrücklich darum, für das leere Projekt ebenfalls einen — dann leeren — Report/Protokoll anzulegen, statt es zu überspringen.
6. Ausgabeordner angelegt: `tests/test_results/dresdyn-kamerasystem/`, `tests/test_results/chats-export-test-1/` (beide gitignoriert, leer geblieben).
7. Für Dresdyn ein Web-Bundle mit leerer `conversations`-Liste erzeugt und heruntergeladen (`~/Downloads/web-bundle_dresdyn-kamerasystem_list.json`, 127 Bytes, angekommen).
8. `list --web <bundle> --out tests/test_results/dresdyn-kamerasystem` ausgeführt.

**Ergebnis Schritt 8: Abbruch.** `chat_export_convert.py` verweigert die Protokollanlage bei einer leeren Chatliste — Meldung *„No chats found in the given list(s)."*, Exitcode 1. Das ist bestehendes, bewusst geschriebenes Code-Verhalten (Prüfung `if not records: … return 1`), keine Fehlbedienung im Testlauf.

**Die Lücke:** Der Code unterscheidet aktuell nicht zwischen „keine Quelle angegeben" (echter Bedienfehler, Abbruch richtig) und „Quelle angegeben, liefert aber echt null Chats" (legitimer Zustand eines leeren Projekts, sollte einen — leeren — Report erzeugen dürfen, wie vom Nutzer gewünscht). Für das zweite Projekt „Chats-Export, Test 1" (3 Chats) wurde der Test gar nicht erst fortgesetzt, um nicht mit halb inkonsistentem Vorgehen weiterzumachen.

**Auf Wunsch des Nutzers hier abgebrochen, noch keine Entscheidung getroffen und keine Codeänderung vorgenommen** — die passende Lösung (Unterscheidung der beiden Fälle in `cmd_list`/dem `records`-Check) ist noch offen und mit dem Nutzer zu besprechen, bevor sie umgesetzt wird, wie bei jeder Skriptänderung.

**Aufräumstand:** Beide Ausgabeordner leer, keine Datei geschrieben. Der Bundle-Download `~/Downloads/web-bundle_dresdyn-kamerasystem_list.json` liegt außerhalb der Projektwurzel und wurde nicht angefasst — enthält nur Metadaten (Zeitstempel, Organisations-UUID, leere Liste), keinen Chatinhalt.

**Nachgetragen, 21. August (nach Rechner-Neustart, ohne Browser):** Die Lücke ist behoben. `cmd_list` in `chat_export_convert.py` verweigert eine leere Chatliste nicht mehr — die Prüfung `if not records: ... return 1` ist ersatzlos entfernt; nur eine fehlende Quelle (`--map`/`--web` beide leer) bleibt weiterhin ein Fehler. Getestet gegen ein echtes leeres Bundle: Exitcode 0, gültiges, leeres `protocol.json` wird geschrieben. Gegenprobe für den unveränderten Fehlerfall bestanden. Regressionstest in `tests/test_export_convert.py` ergänzt (zwei neue Prüfungen) und per Leerprobe bestätigt — mit zurückgeschriebener alter Prüfung schlägt genau dieser Test an. Alle sechs Suiten grün, auch unter `-O`. Damit ist der zweite Teil von Stufe 7 (Projekt „Chats-Export, Test 1" mit 3 Chats) beim nächsten Browserzugriff nachholbar, ohne an dieser Stelle erneut hängenzubleiben.

## Stufe 8 (22. August): Kontowechsel bei bereits stehender Bridge, kein Auslöser für den Abriss

Der Befund aus Stufe 2 — ein Kontowechsel im Tab bricht eine bereits bestehende Bridge nicht — heute unabhängig reproduziert, ausgelöst durch einen Verdacht, der sich dabei auflöste.

**Der Verdacht:** Über den Nachmittag riss die Verbindung mehrfach ab und kam wieder — mal mit „Browser extension is not connected" auf `tabs_context_mcp`, mal verschwand der MCP-Server `claude-in-chrome` ganz aus der Werkzeugliste, unabhängig von jeder Kontoänderung. Als die Verbindung ausgerechnet kurz nach einer Anmeldung von Chrome am **Pro**-Konto (bis dahin war Chrome am Team-Konto) wieder stand, lag die Vermutung nahe, die Bridge brauche doch dasselbe Konto wie die Claude-Code-Sitzung — im Widerspruch zum Neustart-Befund aus Stufe 3.

**Der Gegenversuch:** Bei weiterhin stehender Bridge (Chrome auf Pro, `/api/organizations` bestätigt) meldete sich der Nutzer in Chrome auf das **Team-Konto** um — bewusst zurück zum Mismatch gegenüber der Pro-Sitzung von Claude Code. `tabs_context_mcp` lieferte sofort den bestehenden Tab, `/api/organizations` im selben Tab lieferte prompt `HZDR - FWF` — keine neue Anmeldung der Bridge nötig, kein Abriss.

**Ergebnis: Der Verdacht ist ausgeräumt.** Die Bridge folgt weiterhin nur der aktuellen claude.ai-Websitzung im Tab, unabhängig vom Konto der Claude-Code-Sitzung — wie in Stufe 2 belegt, jetzt ein zweites Mal und mit vertauschten Rollen (dort Pro→Team, hier Pro→Team nach zwischenzeitlichem Team→Pro). Die Instabilität des Nachmittags war das MCP-Server-Flapping der Beta, keine Kontofrage. Nichts an den Aussagen aus Stufe 2/3 ändert sich; hier steht nur die zweite Reproduktion.

## Abgrenzung: nicht jeder Verbindungsabbruch ist ein Bridge-Befund

Beim Großimport vom 21. August — vier reale Projekte, 171 Chats über den Export-Weg (3.1.7 der Implementierungsdoku) — kam mitten im Gespräch einmal `API Error: Connection lost mid-response`. Das ist die **Modellverbindung** dieser Claude-Code-Sitzung, nicht `claude-in-chrome` — die Bridge selbst war davon nicht betroffen, der Ablauf lief danach ohne erneuten Zugriffsverlust weiter. Nach Angabe des Nutzers hat sein Internetzugang zeitweise mehrminütige Einbrüche; das ist die plausiblere Erklärung als ein Bridge-Fehler. Festgehalten, damit ein künftiger Fund dieser Meldung nicht vorschnell zu den MCP-Server-Aussetzern von Stufe 8 gezählt wird — beides sieht ähnlich aus, sind aber verschiedene Schichten.
