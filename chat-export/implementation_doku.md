# Implementierungsdokumentation Chats-Export

**Produktiver Stand.** Das Werkzeug ist gebaut, an echten Daten erprobt und benutzbar; die Anwenderdokumentation liegt beim Skill (3.3). Diese Datei beschreibt, **was tatsächlich implementiert ist** — nicht, wie es dazu kam. Die einzige Ausnahme ist 1.7: Dort stehen die Wege, die versucht wurden und nicht getragen haben, damit niemand sie erneut einschlägt.

Was hier steht, ist damit Zusage und nicht Arbeitsstand. Ein Widerspruch **innerhalb dieser Doku** oder zwischen **Doku und Code** ist ein Defekt und wird behoben, nicht erklärt.

---

Vier Teile. **Teil 1** beschreibt, was gebaut wird, wie es zusammenwirkt und wie es benutzt wird. **Teil 2** hält die Vorgaben, die quer über alle Werkzeuge gelten. **Teil 3** hält je Skript die Festlegungen, die dort umgesetzt werden, samt dem Kontext, der dafür erarbeitet wurde. **Teil 4** ist die Prüfliste gegenüber der laufenden Anthropic-Entwicklung. Teil 1 verweist für Details nach 2 und 3 und wiederholt sie nicht.

Die **Beleglage** wird durchgehend ausgewiesen; die drei Stufen und ihre Regeln sind Vorgabe 2.1.

---

# 1 Zusammenhänge

## 1.1 Ziel

Chats aus claude.ai-Projekten sollen **im Zusammenhang ihres Projekts durchsuchbar** sein — nicht fortführbar. Sie dienen dazu, früher besprochenen Kontext wiederzufinden.

Beides ist vorgesehen: der **einmalige Umzug** und das **wiederholte Nachreichen**. Ausgelegt wird auf den zweiten Fall, weil er die härtere Anforderung stellt — neue Chats kommen laufend hinzu, vorhandene können weitergelaufen sein.

Warum Nachreichen der Dauerbetrieb ist und nicht die Ausnahme, liegt an der Rollenteilung der Umgebungen: claude.ai und Claude Desktop sind die Orte für allgemeines Bearbeiten, Recherchieren und Durchdenken; Claude Code ist der Ort des eigentlichen Code-Building-Prozesses, und seine Sitzungen sind an einen dedizierten Rechner gebunden. Wer aus Gründen, die nur er selbst kennt, auf claude.ai weiterchattet, will dieselben Chats trotzdem im Quellcodeprojekt auswertbar haben.

Je Chat entstehen bis zu vier Dateien — Gespräch, Denkschritte, Anhänge, Erzeugnisse (Vorgabe 2.2) —, und daneben gibt es **genau eine** weitere: das Protokoll (1.4). Mehr Zustand gibt es nicht.

## 1.2 Die Wege

Der Engpass ist nicht die Suche, sondern die **Transkription**: Chattext erreicht ein Dateisystem nur, wenn er irgendwie dorthin gelangt, ohne durch den Kontext einer Instanz zu laufen — sonst wird aus Kopieren unweigerlich Nacherzählen (Vorgabe 2.8). Beide benutzbaren Wege umgehen diesen Engpass, und beide bedient dasselbe Skript, `chat_export_convert.py` (3.1).

| | Kontoexport | Web-Weg |
| --- | --- | --- |
| Quelle | ZIP per E-Mail, Zeitraum wählbar | die internen Endpunkte der claude.ai-Weboberfläche |
| Zugang | Konto mit Selbstbedienungs-Export | angemeldeter Chrome plus Browser-Anbindung |
| Wartezeit | Antrag, E-Mail, Download | keine |
| Menge | alles in einem Zug, keine Last je Chat | je Chat ein Abruf, deshalb gebremst |
| Projektbezug | fehlt — braucht eine Chatliste aus claude.ai | `project_uuid` und `created_at` stehen in den Daten |
| Aufruf | `convert --zip` | `list --web`, `convert --bundle` |

**Wann welcher.** Der Kontoexport ist der Anker: Er existiert, weil die Datenschutz-Grundverordnung ihn erzwingt — sein Format kann sich ändern, aber er verschwindet nicht. Der Web-Weg ist die bessere Wahl für **kleine Nachträge** eines Projekts, und für eine Erstmigration oder ganze Chats mit reichlich Anhängen bleibt der Export vorzuziehen: Ein Massenabruf über die Weboberfläche fällt serverseitig auf und kann Captcha- oder Cloudflare-Prüfungen auslösen. Deshalb die Abrufbremse von 4 bis 12 Sekunden je Chat.

**Für Team- und Enterprise-Konten ist der Web-Weg der einzige.** Dort hat ein gewöhnliches Mitglied keinen Selbstbedienungs-Export (1.6); der Primary Owner kann exportieren, aber ein Verfahren, das bei jedem Durchgang den Administrator braucht, ist für einen **wiederkehrenden** Abgleich (1.1) untauglich. Am 22. August 2026 wurde der Web-Weg in einem Team-Konto durchgespielt: Projektliste und Chatlisten kamen vollständig.

Bei den Denkschritten ist die Ausbeute ungewiss — sie **können** enthalten sein, müssen es aber nicht (3.1.1), und zwar in beiden Wegen gleichermaßen, weil die Plattform sie nicht mehr ausschreibt. Anhänge und Erzeugnisse sind davon unberührt.

**Es sind genau diese zwei.** Weitere Quellen wurden geprüft und tragen nicht — welche und warum, steht in 1.7.

**Verbindlich ist die Wegegleichheit** — Wortlaut, erlaubte Abweichungen und ihr Wächter stehen als Vorgabe 2.5. Zwischen beiden Wegen ist sie **baulich** erfüllt, weil sie durch denselben Konverter laufen (3.1); gemessen wird sie gegen eine zweite, unabhängige Umsetzung des Dateiformats unter `tests/`.

## 1.3 Richtungen und Zielorte

**Zwei Richtungen, dasselbe Werkzeug.** Entwickelt wird gegen **claude.ai → Claude Code**; Ziel ist dort das versionierte Repo des Zielprojekts. Die zweite Richtung ist **claude.ai → claude.ai** — ein anderes Projekt, gegebenenfalls unter einem anderen Konto. Dort kann nur das Projektwissen Ziel sein, was unproblematisch ist: Dieselbe Dateistruktur trägt die Durchsuchbarkeit auch da. Entscheidend ist, dass das **kein anderes Werkzeug** ist. Es sind dieselben Dateien aus demselben Lauf; verschieden ist allein, wohin sie gelegt werden. Vorgabe 2.10 setzt das voraus („keine zielabhängige Ausgabeform"), hier steht der Grund.

Primär das Git-Repo eines Claude-Code-Projekts, dort `<projekt>/.claude/imported_chats/`. Die Dateien sind über `Read`/`Grep` erreichbar: kein Projektwissen, kein RAG, kein undokumentierter Schwellwert, kein Kontextverbrauch, bis wirklich gelesen wird.

Sekundär das Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz — mit denselben Dateien, ohne zweite Ausgabeform; die Regeln dazu (ein flaches Verzeichnis je Quellprojekt, dieselben Dateien für beide Ziele) sind Vorgabe 2.10. JSON ist ein belegter Upload-Typ, und Projektdateien werden per Textextraktion verarbeitet.

**Als dritter Zielort** kommt `~/.claude/projects/<projekt>/` in Frage — für Chats, die gerade **nicht** ins geteilte Repo sollen, weil Fremde sie nicht mitlesen dürfen. Sie liegen dann als nebenher geführtes zweites Chat-Projekt neben den Sitzungen, auf die Claude Code ohnehin zugreift, und werden dorthin regelmäßig nachgereicht. Drei Bedingungen gehören untrennbar dazu:

- **Die Aufbewahrungsdauer muss vorher hochgesetzt werden.** Dort wird nach `cleanupPeriodDays` aufgeräumt — *„The default is 30 days and the minimum is 1; setting `0` fails with a validation error"* (belegt, [claude-directory](https://code.claude.com/docs/en/claude-directory)); eine Obergrenze oder ein „aus" ist nicht dokumentiert. Das ist kein Ausschlussgrund, denn dieselbe Frist trifft ohnehin jede Claude-Code-Sitzung desselben Projekts — es ist eine **Nutzerpflicht**, die in die Anwenderdokumentation gehört. Namentlich aufgeräumt werden `projects/<p>/<sitzung>.jsonl` sowie `subagents/` und `tool-results/` je Sitzung; ob die Aufräumung auch **fremde** Dateien in diesem Ordner anfasst, sagt die Dokumentation nicht und bleibt Prüfpunkt (Kapitel 4).
- **`claude project purge` löscht unabhängig von jeder Frist**: *„Transcripts and auto memory under `projects/`"* für ein Projekt (belegt, ebd.). Wer das Kommando benutzt, nimmt ein dort liegendes Archiv mit.
- **§1.2 der Arbeitsanweisungen behält `~/.claude/` der Engine vor.** Ein Lauf, der dorthin schreibt, ist deshalb eine vom Nutzer ausdrücklich angeordnete Ausnahme und nie der Normalfall (Vorgabe 2.10).
- **Der Ordner liegt außerhalb des Arbeitsverzeichnisses.** Eine Claude-Code-Sitzung erreicht ihn nur, wenn er ihr als zusätzliches Verzeichnis freigegeben ist — *„The `--add-dir` flag gives Claude access to additional directories outside your main working directory"* (belegt, [memory](https://code.claude.com/docs/en/memory)). Ein Archiv, das die Instanz nicht öffnen kann, ist kein Archiv; der Anweisungsblock für diesen Zielort sagt es deshalb ausdrücklich (3.1.6).

Dass der Ort nicht versioniert und *„not shared across machines"* ist, spricht hier ausnahmsweise nicht dagegen, sondern dafür — genau das ist der Zweck, während `<projekt>/.claude/` umgekehrt gerade wegen der Versionierung Primärziel ist. Die dortige Ordnernamensstruktur bleibt als Zuordnungshilfe nützlich.

## 1.4 Das Protokoll

Eine Datei je Quellprojekt, neben den Chatdateien. Sie wird **bei der Erstellung der Chatliste angelegt** — in beiden Wegen, bevor ein einziger Chat geholt ist — und ist ab da in jedem Schritt die Referenz. Aufbau, Felder und Statuswerte sind Vorgabe 2.4.

Warum ein Protokoll und nicht der Verzeichnisinhalt: **Innerhalb von claude.ai gibt es kein Verzeichnis zum Ablesen**, dort existiert nur Hochgeladenes. Eine kleine Datei kann eine Instanz lesen, N Chatdateien durchzählen nicht. Die `metadata` in jeder Chatdatei bleibt trotzdem, damit eine einzeln weitergegebene Datei für sich verständlich ist; bei Widerspruch gilt das Protokoll.

**Gezählt wird im Skript, nicht im Kopf der Instanz** — und das ist keine Vorsicht, sondern eine Messung. Am hochgeladenen Protokoll gefragt, gab eine Instanz einen einzelnen Wert zeichengenau wieder, bis auf die Mikrosekunden eines Zeitstempels, nannte aber **zehn** Chats, wo neun eingetragen waren. Nachschlagen gelingt, Aufsummieren nicht. Deshalb rechnen `list` und `diff` in dem Skript, das die JSON parst; die Instanz führt es aus, statt das Protokoll zu überschlagen. Hinge die Entscheidung „was fehlt noch" daran, dass sie richtig zählt, wäre der Fehler still.

Das Protokoll liegt **beim Archiv**, im Zielverzeichnis neben den Chatdateien — dort braucht es jeder Abgleich. Es **zusätzlich** ins Projektwissen des Quellprojekts zu laden, ist möglich und kein Schritt des Ablaufs (1.5): Das Quellprojekt trägt dann selbst die Auskunft, was von ihm archiviert wurde.

Nicht in Artefakte: die kennen keinen JSON-Typ, kein spezifiziertes Downloadformat, und der einzige dokumentierte Rückweg in einen neuen Chat ist manuelles Kopieren (belegt, [9487310](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)).

## 1.5 Ablauf aus Nutzersicht

**Claude Code ist das Frontend**, angeleitet durch den Skill `chat-export` (3.3). Kein Parametrierungswerkzeug: Er stellt fest, welche Projekte betroffen sind und was schon da ist, legt die Lage vor und ruft das Skript auf. Zwei Haltepunkte sind vorgesehen — vor dem ersten Abruf und nach der Statistik; die Wahl des Wegs trifft der Nutzer, nicht der Skill.

**Über den Web-Weg**, der Regelfall für Nachträge:

1. Projektliste holen, Projekt bestimmen, Chatliste über alle Seiten holen. Alles aus einem Tab auf claude.ai heraus, ohne Chat und ohne dass ein Zeichen durch einen Kontext läuft.
2. `list --web` gegen das Protokoll: Was ist neu, was gewachsen, was verschwunden. Die Fenstergrenze braucht hier nichts geschätzt zu werden, denn `created_at` steht je Chat in der Liste.
3. Die fehlenden Chats abrufen, gebremst, alles in **einen** Behälter, **ein** Download.
4. `convert --bundle`: Dateien schreiben, Protokoll fortschreiben, Ersetztes benennen.

**Über den Kontoexport**, für Erstmigration und große Mengen:

1. Zeitraum aus dem Protokoll errechnen lassen (`diff` nennt ihn samt Begründung), Export anfordern, ZIP herunterladen. **Setzt voraus, dass es ihn gibt** — Free, Pro oder Max (1.6); in einem Team-Konto führt dieser Ablauf ins Leere und der Web-Weg ist der einzige. Der Zeitraum filtert `created_at`, nicht `updated_at` (4.2): ein alter Chat, der letzte Woche weiterlief, fehlt in einem kurzen Fenster **ganz**.
2. Die Projektzuordnung fehlt dem Export. Sie kommt entweder aus der Chatliste des Web-Wegs (`list --web`) oder, wo der nicht zur Verfügung steht, aus einem `recent_chats`-Abzug in claude.ai (`list --map`) — dann gilt die Regel unten.
3. `convert --zip`: dieselben Dateien, derselbe Protokollstand wie im Web-Weg.

**Nur wenn die Chatliste aus einem claude.ai-Chat kommt:** Die Abfrage gehört in einen eigens dafür angelegten Chat, der danach gelöscht wird. Grund: `recent_chats` listet den laufenden Chat nicht mit (1.6), also fehlt der Abfragechat in seiner eigenen Liste — und damit im Protokoll und im Archiv, ohne dass irgendetwas es meldet. Ein frischer, hinterher gelöschter Chat macht die Lücke harmlos. Der Web-Weg hat dieses Problem nicht: Er listet ohne Chat und übergeht nichts.

**Das Protokoll ins Projektwissen des Quellprojekts zurückzuladen, ist kein Schritt des Ablaufs**, sondern eine Möglichkeit: Das Quellprojekt sagt dann selbst, was von ihm archiviert wurde. Der Abgleich braucht es nicht — das Protokoll liegt beim Archiv (1.4).

**Das Anlegedatum eines Projekts** kommt aus dem Projekt-Endpunkt des Web-Wegs (2.4). Wer ausschließlich den Export-Weg hat, liest es aus den Projektdateien eines beliebigen Exports, die der Zeitraumfilter nicht erfasst (3.1.1).

**Wie Zuwachs erkannt wird:** Eine frische Chatliste liefert je Chat ein `updated_at`. Ist es neuer als der Stand im Protokoll, wurde weitergechattet. Der Vergleich braucht nichts als das Protokoll und die neue Liste — kein Chatarchiv, kein ZIP, kein Zeichen Chattext (Mechanik in Vorgabe 2.4). Ein veralteter Chat wird **als Ganzes ersetzt**, nicht fortgeschrieben, und das Ersetzen räumt auf — Vorgabe 2.6.

## 1.6 Was die Umgebung erlaubt und verbietet

### Migrationsmatrix, heraus


| Quelle                    | Weg                                 | Format                        | Haken                                                                           |
| ------------------------- | ----------------------------------- | ----------------------------- | ------------------------------------------------------------------------------- |
| claude.ai, alle Chats     | Kontoexport                         | ZIP,`conversations.json`      | kein Projektbezug; Gelöschtes als Hülle; `files` nur als Name; Momentaufnahme |
| claude.ai, ein Projekt    | **interne Web-Endpunkte**           | JSON, Baum vollständig        | undokumentiert, jederzeit änderbar; braucht angemeldeten Browser                |
| claude.ai, ein Projekt    | `recent_chats`                      | UUID, Zeit, Titel             | nur Metadaten, ohne `created_at`; übergeht den laufenden Chat                   |

Die geprüften und verworfenen Quellen — Claude Code CLI, Cowork, Compliance-API und die beiden entfallenen claude.ai-Werkzeuge — stehen samt Grund in 1.7 und nicht hier: Diese Matrix führt, was benutzbar ist.

### Migrationsmatrix, hinein


| Ziel                      | Weg                         | Haken                                            |
| ------------------------- | --------------------------- | ------------------------------------------------ |
| Git-Repo für Claude Code | Datei im Arbeitsverzeichnis | **der gewählte Weg**                            |
| claude.ai-Projekt         | Projektwissen hochladen     | bleibt im Kontext bzw. wird per RAG durchsucht   |
| claude.ai-Chat            | Datei anhängen             | 20 Dateien je Chat                               |
| claude.ai, neuer Chat     | —                          | **kein dokumentierter Mechanismus**              |
| Cowork-Projekt            | Ordner verbinden            | Cowork-Projekte sind lokal, nicht synchronisiert |

**Es gibt kein „Chat als Chat migrieren".** Jeder Weg verwandelt eine Konversation in Dateien. Die zwei echten Sitzungsübergaben (`--teleport`, „Continue in") sind kontobasiert und gehen nie von einer Datei aus.

### Grenzen, die bleiben

- **Cowork ist über keinen Weg erreichbar.** Eigene ID-Welt, kein Export, kein Projektbezug; Lücke, keine Aufgabe. Anthropic baut daran, und ein künftiger Cowork-Weg könnte dieses Vorhaben ganz ablösen — als Beobachtung geführt in Kapitel 4.
- **Gelöschte Chats sind unwiederbringlich.** Der Export enthält sie als Hüllen und sagt nicht, dass es Hüllen sind (3.1). Der scheinbare Widerspruch zur belegten Zusage oben löst sich beim genauen Lesen auf: Nicht enthalten sind die *Inhalte*, der *Eintrag* bleibt. Beide Aussagen stimmen. Und weil die Chatliste den gelöschten Chat nicht mehr führt, kann ihn kein Lauf mehr einem Projekt zuordnen — er kommt im Archiv also gar nicht erst vor.
- **Hochgeladene Dateien: das meiste kommt mit.** Der Export führt sie in zwei Feldern, und die sind **nicht disjunkt** — dieselbe Datei steht oft in beiden. `attachments` tragen `extracted_content` und damit ihren Text — 341 im Drei-Monats-Export, keines leer, zusammen 9.635.919 Zeichen, überwiegend `text/x-python` (238) und Markdown (26). `files` tragen nur `file_uuid` und `file_name` — 524 Stück, aber das ist kein Verlustmaß: Ein Textupload wird **zweimal** verzeichnet, einmal als Dateiobjekt unter `files` und einmal mit seinem Text unter `attachments`. Die Beleglage abgestuft:
  - **Gemessen:** 319 der 524 `files`-Einträge haben ihren Inhalt in derselben Nachricht. Für sie ist nichts verloren.
  - **Gemessen:** 205 haben keinen Namenspartner mit Inhalt; nach Entdopplung innerhalb der Nachricht meldet das Werkzeug 200.
  - **Unsicher:** 24 davon liegen in Nachrichten, die einen **namenlosen** Anhang mit Inhalt tragen (s. 3.1.1). Das sind vermutlich dieselben Uploads — der Name steht nur auf der `files`-Seite, der Inhalt nur auf der `attachments`-Seite —, aber über den Namen lassen sie sich nicht zusammenführen, und einen anderen verbindenden Schlüssel gibt es nicht (3.1.1). Der Code rät hier nicht.
  - **Nicht behauptet** wird, dass die restlichen rund 180 unwiederbringlich sind. Belegbar ist nur: Der Export führt für sie keinen Inhalt. Ob es einen anderen Abrufweg gibt, ist eigener Prüfpunkt (4.3, warm).
- **Die Projektzugehörigkeit gibt es nur in claude.ai.** Der einzige Punkt, an dem die Werkzeuge dort unentbehrlich bleiben, um exportierte Chats einzelnen Projekten zuzuordnen. Ob eine Konversation im Export je einen Projektbezug bekommt, führt Kapitel 4 als Prüfpunkt (4.2, kalt).

### Umgebungsfakten, die den Gesamtentwurf tragen


| Aussage                                                                                                                                                                                     | Beleglage                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Kontoexport unter Settings → Privacy, Link per E-Mail, verfällt nach 24 h — *„available to individual Claude users on Free, Pro, and Max plans"*                                          | belegt ([9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data))                              |
| **In Team und Enterprise hat ein gewöhnliches Mitglied keinen Export**: *„Individual members of Team and Enterprise organizations do not have a self-serve export option"*; nur der Primary Owner exportiert, und zwar unter *Organization settings → Data and privacy* | belegt ([13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data))                    |
| **Der Export lässt einen Zeitraum wählen**                                                                                                                                                | **beobachtet**, in keinem Artikel erwähnt                                                                              |
| Gelöschte Inhalte*„will not be included in data exports initiated after the deletion"*                                                                                                    | belegt ([13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data))                    |
| **Der Löschvorgang nimmt den Inhalt, nicht den Eintrag.** Zwei am 17. August gelöschte Chats standen im danach angeforderten Export als Hüllen — Gerüst da, null Zeichen Text            | beobachtet                                                                                                              |
| **Ein gelöschter Chat verschwindet dagegen aus `recent_chats`** und ist damit keinem Projekt mehr zuzuordnen                                                                              | beobachtet                                                                                                              |
| **`recent_chats` listet den laufenden Chat nicht mit.** Aus Chat A kommt B, aus B kommt A — jeder sieht den anderen, keiner sich selbst                                                    | beobachtet (zwei symmetrische Versuche)                                                                                 |
| Projektdateien: 30 MB je Datei, Anzahl unbegrenzt,*„Text extraction only"*                                                                                                                 | belegt ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude))                               |
| RAG für Projekte schaltet automatisch nahe der Kontextgrenze ein,*„up to 10x"*, Claude nutzt dann ein *project knowledge search tool*; **kein Schwellwert dokumentiert**, nicht steuerbar | belegt ([11473015](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects))    |
| RAG-Schwelle richte sich nach**Dateianzahl**, nicht Größe                                                                                                                                 | Community ([#25759](https://github.com/anthropics/claude-code/issues/25759)), als `invalid` geschlossen                 |
| Projektdateien im Container*„accessible … **while remaining in context**"* — spart **keinen** Kontext                                                                                    | belegt ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude))                  |
| Container-Netzzugang nur gegen eine Allowlist;`claude.ai` steht **nicht** darauf                                                                                                            | belegt (ebd.)                                                                                                           |
| Kontextfenster Opus 5 / Sonnet 5: 1 Mio Token auf bezahlten Plänen                                                                                                                         | belegt ([8606394](https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans)) |
| Ein langes Gespräch bricht nicht ab, sondern**fasst frühere Teile zusammen**                                                                                                              | belegt (ebd.)                                                                                                           |
| Opus 4.7 und spätere Opus-Modelle erhalten**keine** Token-Budget-Tags                                                                                                                      | belegt ([Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows))                       |
| Claude-Code-Transkripte:`~/.claude/projects/<p>/<id>.jsonl`, Format *„internal … changes between versions"*, Aufräumung nach `cleanupPeriodDays` (Standard 30, Minimum 1, einstellbar), **kein Import**                                   | belegt ([sessions](https://code.claude.com/docs/en/sessions))                                                           |
| **`/api/organizations` kann mehrere Organisationen liefern, auch bei einem einzigen Nutzer.** Eine reine API-/Console-Organisation (ohne `"chat"` in `capabilities`) neben der claude.ai-Chat-Organisation ist normal, keine Störung — Chat-Abo und API-Zugriff sind bei Anthropic bewusst getrennte Organisationen, getrennt abgerechnet | belegt ([9876003](https://support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-do-i-have-to-pay-separately-to-use-the-claude-api-and-console)) |
| **Zur Export-Antragsseite führt kein Deep-Link.** Direkte Navigation auf `claude.ai/settings/data-privacy-controls` (o. ä.) rendert nur die gewöhnliche Chat-Oberfläche; die Einstellungen öffnen client-seitig erst nach einem echten Klick durch die Oberfläche (Konto-/Einstellungsmenü → „Datenschutz" → „Daten exportieren") | beobachtet |

Formatnahe Fakten stehen bei dem Skript, das sie verarbeitet — der Aufbau des Export-ZIP in 3.1.1. Was quer über alle Werkzeuge gilt, steht als Vorgabe in Kapitel 2; die Prüfliste gegen Anthropic-Änderungen ist Kapitel 4.

### Widersprüche in der Anthropic-Doku

Benannt, nicht aufgelöst:

- Dateigröße beim Upload: 500 MB ([8241126](https://support.claude.com/en/articles/8241126-upload-files-to-claude)) gegen *„30MB per file for both uploads and downloads"* ([12111783](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)).
- Projektwissen: *„must fit within Claude's context window"* gegen *„you can continue adding knowledge beyond these limits"*.
- RAG-Verfügbarkeit: *„available for all Claude plans"* gegen *„only available to users with paid Claude plans"* ([9517075](https://support.claude.com/en/articles/9517075-what-are-projects)).
- Die Exports-Zip-Files tragen einen batch-Abschnitt mit einer Zahl im Namen, die bei Tests immer auf 0 steht. Möglicherweise werden größere Exports in mehrere Zip-Files aufgeteilt.

## 1.7 Misslungene Ansätze und Versuche

Die Wege, die versucht wurden und nicht getragen haben — damit niemand sie erneut einschlägt. Es geht hier um die **Wege**, nicht darum, wie sie einmal umgesetzt waren; was von ihnen an Umgebungswissen bleibt, steht in 1.6 und in der Prüfliste (Kapitel 4).

**Der Lese-Weg: ein Chat per UUID aus der claude.ai-Instanz.** Ein eingebautes Werkzeug namens `read_conversation` lieferte einen Chat seitenweise mit durchnummerierten Turns und einem Sollmaß, an dem sich Vollständigkeit *rechnen* ließ — das kann keiner der heutigen Wege. Es verschwand am 18. August 2026, zwölf Tage nach belegter Nutzung, ohne Ankündigung und ohne erkennbaren Grund. Inhaltlich wäre es dem Web-Weg ohnehin unterlegen: Es gab nur das gerenderte Transkript, also weder Denkschritte noch Anhänge noch Werkzeugaufrufe. Sein einziger struktureller Vorzug — er brauchte keinen Kontoexport und arbeitete deshalb auch in Team-Konten — ist inzwischen vom Web-Weg übernommen. Mit ihm entfiel auch der Umweg, das Protokoll ins Projektwissen des Quellprojekts zurückzuladen: Das war nötig, solange dort gearbeitet wurde, und ist heute höchstens noch Selbstauskunft.

**Rekonstruktion aus Suchschnipseln.** Der Gedanke war, Chats aus überlappenden Treffern von `conversation_search` zusammenzusetzen, wo kein anderer Weg offensteht. Er scheitert an der Quelle: Die Suche liefert **feste, nicht überlappende** Blöcke — es gibt nichts zu verbinden, und wer sie aneinanderreiht, sammelt Text ohne ihn zusammenzufügen. Erschwerend kommt hinzu, dass sie bei längeren Chats gar keine Schnipsel mehr zurückgibt, sondern eine **Zusammenfassung**; wer die einliest, archiviert eine Nacherzählung und verstößt gegen Vorgabe 2.8. Der Weg ist damit doppelt tot, und die Suche taugt für dieses Vorhaben allein zum Auffinden, nie zum Übertragen.

**Claude Code als Quelle.** Weder `/export` noch die Sitzungsdateien unter `~/.claude/projects/` sind eine brauchbare Quelle: Das eine liefert kein JSON, das andere ein Format, das Anthropic ausdrücklich als intern und zwischen Versionen wechselnd bezeichnet, und beides unterliegt einer Aufbewahrungsfrist. Als **Zielort** ist derselbe Ordner dagegen brauchbar und in 1.3 vorgesehen — die Richtung entscheidet.

**Cowork.** Über keinen Weg erreichbar, und zwar unabhängig von der Umsetzung: eigene ID-Welt ohne UUIDs, kein Export, kein Projektbezug, und weder Auslöser noch Ablage eines Sitzungsexports sind dokumentiert. Das ist eine Lücke, keine Aufgabe; Anthropic baut daran, und ein künftiger Cowork-Weg könnte dieses Vorhaben ganz ablösen (Beobachtung in 4.4).

**Die Compliance-API.** Sie kann genau das, was dieser Ordner nachbaut — programmatischer Zugriff auf Chats, Dateien, Projekte und Nutzer einer Organisation. Sie steht nur Enterprise offen und ist damit unerreichbar. Festgehalten, damit es nicht erneut recherchiert wird: Beleglage, keine Aufgabe.

**Der Container als Abrufweg.** Ein Skript in der Ausführungsumgebung einer claude.ai-Instanz sollte den Export-Link selbst holen. Deren Netzzugang geht nur gegen eine Allowlist, auf der `claude.ai` nicht steht (1.6) — und der Link ist ohnehin sitzungsgebunden.

**Markdown als Archivformat.** Verworfen zugunsten von JSON: Nur dort sind die Sprecherrollen eindeutig, und die Textextraktion beim Upload ist verlustfrei — am echten Fall bestätigt, ein Zeitstempel kam mit Mikrosekunden unverändert zurück.

**Der Sondierungsexport.** Ein absichtlich kurzer Export, nur um das Anlegedatum eines Projekts zu erfahren; er funktionierte, ist aber überflüssig, seit der Projekt-Endpunkt des Web-Wegs dasselbe Datum direkt liefert. Wer ausschließlich den Export-Weg hat, kann ihn weiter benutzen (1.5).

**Und eine Lehre über das Prüfen selbst**, die mehr wert ist als die Einzelbefunde: Zweimal wurde die Abwesenheit eines Werkzeugs falsch geprüft — einmal, indem eine Instanz nach ihrem Werkzeugsatz *gefragt* wurde statt ein Werkzeug *benutzen* zu lassen, einmal mit einer Frage, deren Antwort auch anderswo bereitlag. **Eine Probe taugt nur, wenn allein das geprüfte Werkzeug die Antwort hervorbringen kann.**

---

# 2 Vorgaben

Festlegungen, die quer über alle Werkzeuge dieses Ordners gelten. Aufnahmetest: Man muss auf eine Datei zeigen und sagen können „das verletzt diese Vorgabe". Was so nicht prüfbar ist, steht als Begründung in Kapitel 1 oder als Skript-Eigenheit in Kapitel 3. Weicht ein künftiges Werkzeug bewusst ab, wird die Vorgabe geändert oder das Werkzeug — nie stillschweigend beides gelassen.

## 2.1 Beleglage

Jede Aussage über die Umgebung trägt ihre Beleglage: **belegt** (Anthropic-Dokument, mit Quelle), **beobachtet** (am laufenden System gesehen, nirgends dokumentiert), **Community** (von Dritten berichtet, unbestätigt). Die drei werden nie vermischt, und eine Aufstufung verlangt den jeweiligen Nachweis — eine Community-Aussage wird durch eigenes Nachstellen zur Beobachtung, eine Beobachtung nur durch eine Anthropic-Quelle zum Beleg. Im Lauf dieser Arbeit sind wiederholt Annahmen über die Umgebung gekippt; der Unterschied zwischen den drei Stufen entschied jedes Mal, wie teuer das wurde.

## 2.2 Dateiformat der Chatdateien

Grundlage ist §1.12 der Arbeitsanweisungen: JSON, `messages` mit `role` (`user`/`assistant`) und `content`, dazu ein `metadata`-Objekt. Das dortige Schema ist ausdrücklich ein Beispielschema, also ein Mindestbestand — hier bewusst mit klareren Namen geführt und um zwei Felder unterschritten, aus folgendem Grund.

`predecessor`/`successor` entfallen ganz: §1.11 verlangt für ihre Bestimmung entweder eine Dateinummerierung (haben wir nicht) oder einen inhaltlichen Anhaltspunkt (verstieße gegen Vorgabe 2.7 — Auswahl nie durch Inhalt) oder Nachfragen beim Nutzer je Chat (skaliert nicht). Ein bloßer Zeitstempel reicht nach §1.11 ausdrücklich nicht, und selbst „gleiches Projekt" ist kein verlässliches Indiz — ein Testchat dieses Werkzeugs lag beobachtbar im FreeCAD-Projekt, ohne mit FreeCAD zusammenzuhängen. Chats, die abwechselnd nebeneinander geführt werden, ergeben ohnehin kein sinnvolles Vorgänger/Nachfolger-Schema. Die Rolle, die eine Historie tatsächlich braucht — welche Chats einen älteren, durch andere überholten Stand zeigen — übernimmt `last_updated_at` (s. u.), nicht durch Inhalt, nicht durch den Anlegezeitpunkt, nicht durch einen Zeitstempel je Redebeitrag (den liefert keiner der beiden Wege). §1.12 wird auf dieses Tooling nachgezogen, sobald geklärt ist, wie eine Sitzung in einem fremden Projekt es referenziert; die hier verwendeten Feldnamen sind der Vorschlag dafür.

`chat_date` heißt `created_at` — der Name trifft die Sache, die er meint, und deckt sich mit dem Feld im Rohexport (3.1.1). `source_updated_at` heißt `last_updated_at` — er ist nie ein API-Name gewesen, sondern unsere eigene Benennung, und der alte Name legte fälschlich nahe, er stamme aus der Quelle selbst.

Zusätzliche Metadatenfelder, in dieser Reihenfolge:


| Feld | Wozu |
| --- | --- |
| `chat_uuid`, `url`, `title` | Identität und Auffindbarkeit |
| `imported_at` | Zeitpunkt dieses Laufs — sagt, wie alt die Fassung im Archiv ist, und unterscheidet sie vom Stand der Quelle (`last_updated_at`) |
| `source` | `account-export` oder `web-api` — der Behälter, aus dem der Chat kam |
| `last_updated_at` | Stand der Quelle beim Import — macht Veralten erkennbar; **die** für Historie und Sortierung entscheidende Angabe, s. den Absatz zu `predecessor`/`successor` oben |
| `turns` | Anzahl importierter Redebeiträge |
| `total_turns`, `complete`, `turns_missing` | Vollständigkeit samt Beleg; keiner der beiden Wege hat ein Sollmaß, also durchgehend `null` (2.5) |
| `deleted` | Hülle eines an der Quelle gelöschten Chats; dann ohne `messages` |
| `branches` | mitgenommene Nebenzweige des Nachrichtenbaums (3.1.2); **einziges optionales Feld** — s. 2.5 |
| `dropped_duplicates` | übersprungene Sendewiederholungen |
| `dropped_blocks` | weggelassene Blocktypen je Anzahl, **ohne** `thinking` — das liegt in der Denkdatei und wäre kein Verlust |
| `dropped_thinking` | verworfene Denkblöcke nach den Schwellen in 3.1.3 |
| `attachments_with_content` | Anhänge, deren Text mitkam (Dateien, nicht Nachrichten) |
| `creations` | Erzeugnisse der KI, deren Inhalt mitkam (Artefakte, erstellte Dateien, Änderungen) |
| `attachments_without_content` | Namen der Verweise, deren Inhalt die Quelle nicht hat |

Nachrichten tragen `n`, `role`, `content`. `warnings` ist auf oberster Ebene immer vorhanden, auch leer.

**Bis zu vier Dateien je Chat**, gleicher Stamm; eine Nebendatei entsteht nur, wenn es etwas hineinzuschreiben gibt:

```
2026-06-27_dachluken-steuerung_a1b2c3d4.json              das Gespräch
2026-06-27_dachluken-steuerung_a1b2c3d4.thinking.json     die Denkschritte
2026-06-27_dachluken-steuerung_a1b2c3d4.attachments.json  die Anhänge
2026-06-27_dachluken-steuerung_a1b2c3d4.creations.json    die Erzeugnisse
```

Der Grund für die Auslagerung ist stets dieselbe Rechnung: Denkschritte (9,2 Mio Zeichen), Anhänge (9,6 Mio) und Erzeugnisse (4,4 Mio — von der KI erstellte Artefakte, Dateien und Änderungen, Messung in 3.1.1) übertreffen zusammen den Gesprächstext (11,3 Mio) deutlich. Wer das Gespräch liest, trüge sonst fast das Doppelte — und die Mengenentscheidung fällt erst bei der Benutzung: fürs Repo alles, fürs Projektwissen nur die Gesprächsdateien.

**Verknüpfung über die Nachrichten-UUID**, kein eigener Bezeichner: In der Gesprächsdatei trägt eine Nachricht mit Denkschritten `thinking_ref`, eine mit Anhängen `attachments_ref`, eine mit Erzeugnissen `creations_ref` — jeweils die UUID der Nachricht aus der Quelle. In der Nebendatei trägt jeder Eintrag `ref` mit derselben UUID, dazu die Rückreferenz `chat_uuid`, `chat_file`, `branch` und `turn`. `turn` zählt innerhalb seiner Folge und wiederholt sich zwischen Hauptpfad und Zweig — erst das Paar `(branch, turn)` ist eindeutig, `branch` ist `null` für den Hauptpfad. Damit findet ein Grep der UUID die Stelle in genau einer Nebendatei, und aus der Nebendatei führt der Weg zurück; die Suche über Inhalte funktioniert unabhängig davon.

## 2.3 Dateinamen

`JJJJ-MM-TT_titel-slug_uuid8` plus Endung; das Datum ist das `created_at` der Quelle (sonst `ohne-datum`), der Slug transliteriert Umlaute, kennt nur `a-z0-9-`, ist höchstens 50 Zeichen lang und fällt auf `ohne-titel` zurück. Die acht UUID-Zeichen stehen **immer** im Namen, nicht erst bei Kollision: Zwei Chats teilen im echten Export tatsächlich Datum und Titel, und ein Name, der davon abhängt, was sonst im selben Lauf umgewandelt wird, wäre nicht reproduzierbar.

## 2.4 Das Protokoll

Eine `protokoll.json` je Quellprojekt, neben den Chatdateien. Sie wird mit der Chatliste angelegt — vor jedem Chattext — und ist ab da die Referenz; bei Widerspruch zwischen Protokoll und Verzeichnis gilt das Protokoll. Je Chat:


| Feld | Wozu |
| --- | --- |
| `title`, `created_at` | Auffindbarkeit; `created_at` liefern der ZIP-Weg und die Chatliste des Web-Wegs, ein `recent_chats`-Abzug nicht |
| `created_after` | Untergrenze für Chats ohne `created_at`: der Stand des **vorherigen** Abgleichs beim ersten Sehen — damals war das Projekt gelistet und der Chat nicht dabei, also entstand er später. Wird nur beim ersten Sehen gesetzt und danach nie überschrieben |
| `listed_updated_at` | `updated_at` aus der zuletzt geholten Chatliste |
| `exported_updated_at` | Stand, auf dem der vorliegende Export beruht |
| `turns`, `total_turns` | Umfang beim Export |
| `end_token` | Rest einer blätternden Quelle; kein heutiger Weg schreibt es, nichts hängt daran |
| `file` | Name der Chatdatei, oder leer |
| `side_files` | Namen der Nebendateien, damit sie beim Ersetzen mit entfernt werden (2.6) |
| `status` | s. u. |
| `exported_at` | Zeitpunkt |

Statuswerte: `listed` (aus der Chatliste bekannt), `started` (teilweise gelesen — kein heutiger Weg setzt das, beide schreiben einen Chat immer ganz), `exported`, `stale` (die Quelle ist neuer als der Export), `deleted` (Hülle an der Quelle). `stale` entsteht durch den Vergleich `listed_updated_at` gegen `exported_updated_at`; `updated_at` trägt diese Erkennung, und zwar beobachtet: es liegt in allen Quellen vor — Export, Web-Chatliste, `recent_chats` — und sprang bei gelöschten Chats auf den Löschzeitpunkt.

**Ein Chat, den die frische Liste nicht mehr führt, wird gemeldet und nie automatisch entfernt.** Die Meldung nennt ihn samt Status; das Protokoll behält ihn, und seine Dateien bleiben liegen. Der Grund ist, dass drei sehr verschiedene Fälle von hier aus ununterscheidbar sind: Löschung an der Quelle, Verschieben in ein anderes Projekt — oder eine Chatliste, die der Nutzer nicht bis zum Ende geblättert hat. Beim letzten Fall wäre jede Entfernung ein Datenverlust aus einem Bedienfehler. Die Regel bindet **beide** Wege. Derselbe Wortlaut steht als Konstante `VANISHED_NOTE` auch im Maßstab aus 2.5, der nichts aus dem Konverter importieren darf und ihn deshalb zweimal hält; `tests/test_wegegleichheit.py` sichert die zwei Fassungen gegen Auseinanderdriften.

Auf oberster Ebene trägt das Protokoll `chats` — die Einträge oben, nach Chat-UUID gestellt —, dazu `protocol_version`, `project`, `project_created_at` (Beginn des Quellprojekts — aus dem Projekt-Endpunkt des Web-Wegs oder aus den Projektdateien eines Exports, eingetragen über `list --project-created`), `listed_at` (Zeitpunkt des letzten Listenabgleichs, gesetzt von `list` bzw. `map`) und `order` — eine Bearbeitungsrichtung, die kein heutiger Weg setzt und beide unangetastet erhalten: ein Protokoll, ein Schema.

**Die Fenstergrenze, in einer Tabelle.** Wie weit ein Export zurückreichen muss, damit er einen Chat erfasst, ergibt sich aus drei Quellen unterschiedlicher Güte — genommen wird das Minimum über alle zu holenden Chats:

| Chat-Lage | Fensterstart | Güte |
| --- | --- | --- |
| schon exportiert, aber gewachsen | sein `created_at` aus dem Protokoll | exakt |
| erst beim letzten Abgleich hinzugekommen | sein `created_after` | exakt — vorher existierte er nicht |
| gelistet, aber nie in einem Archiv, ohne `created_after` | `created_at` des Projekts, aus dem Projekt-Endpunkt oder den Projektdateien eines Exports (3.1.1) | exakt, aber projektweit statt chatweise |
| über den Web-Weg gelistet | sein eigenes `created_at` aus der Chatliste | exakt — deshalb braucht dieser Weg kein Projektdatum von außen |
| kein Protokoll (Erstmigration) | ebenso der Projektbeginn | dito |

Der Projektbeginn ist dabei die Untergrenze über alles: kein Chat eines Projekts kann älter sein als das Projekt. Ein zu großzügiges Fenster kostet nur Downloadgröße, ein zu knappes kostet Inhalt — deshalb im Zweifel aufrunden, nach unten.

Umgesetzt als `window_start()` — im Konverter und, zum Vergleich, im Maßstab aus 2.5 —, mit `unbounded` als eigenem Ergebnis: hat ein wartender Chat keine der drei Quellen, wird das **gemeldet statt geschätzt**. Im ZIP-Weg tragen `list` und `diff` das Ergebnis vor, beide über dieselbe Funktion `window_lines()` — zwei Kommandos, die dieselbe Rechnung in eigenen Worten ausgeben, driften auseinander (3.1.6). Der Projektbeginn kommt von außen herein (`--project-created`), weil eine Konversation im Archiv keinen Projektbezug trägt: Im Web-Weg liefert ihn der Projekt-Endpunkt, im reinen Export-Weg liest ihn `inspect_export.py` aus den Projektdateien, sonst kennt ihn nur der Nutzer. Gegen den Tippfehler dabei steht `project_start_warnings()`: ein Chat, der älter ist als sein Projekt, kann nicht zu ihm gehören, also stimmt entweder das Datum oder die Chatliste nicht. Ohne diese Prüfung würde ein falsch getipptes Datum jedes künftige Fenster still verkürzen. Beide Funktionen laufen in `tests/test_wegegleichheit.py` über dieselbe Falltabelle, damit die zwei Implementierungen nicht auseinanderdriften.

Geprüft von `tests/test_wegegleichheit.py`, das auch die Protokolle vergleicht — gleiche Schlüsselmengen, gleiche Kernfelder. Gegen die zweite Umsetzung (2.5) dürfen genau drei Felder abweichen, weil eine Seite sie nicht wissen kann: `created_at`, `total_turns` und `file`, dem dort das Datumssegment fehlt (2.3).

## 2.5 Wegegleichheit

Beide Wege erzeugen für denselben Chat **dieselbe Chatdatei** und **dasselbe Protokoll** (Protokollabgleich in 2.4). Sonst hinge der Inhalt des Archivs davon ab, auf welchem Weg ein Chat hereinkam, und „habe ich diesen Chat?" würde unscharf.

Zwischen Kontoexport und Web-Weg ist das **baulich** erfüllt: Beide laufen durch denselben Konverter, und nur das Auspacken unterscheidet sich (3.1). Ein einziges Metadatenfeld weicht deshalb tatsächlich ab — `source`, der Herkunftsvermerk. Keiner der beiden Wege hat ein **Sollmaß**, an dem sich Vollständigkeit rechnen ließe: `total_turns`, `complete` und `turns_missing` bleiben durchgehend `null`, statt eine Zahl zu behaupten. An echten Daten belegt: Für denselben Chat liefern Web-API und Export-ZIP dieselben Nachrichten-UUIDs.

**Gemessen wird die Zusage trotzdem gegen eine zweite, unabhängige Umsetzung** des Dateiformats: `tests/wegegleichheit_referenz.py`, die allein zu diesem Zweck existiert und nichts aus dem Konverter importiert. Der Grund ist der Wert eines Maßstabs: Prüfte der Konverter nur gegen sich selbst, würde jede Formatänderung automatisch „bestehen". Gegen diese zweite Umsetzung dürfen genau **fünf** Metadatenfelder abweichen — `source`, `created_at`, `total_turns`, `complete`, `turns_missing` — und keines mehr. Wo eine Seite etwas nicht wissen kann, steht `null` statt einer Vermutung.

In den Nachrichten sind `thinking_ref`, `attachments_ref` und `creations_ref` die einzigen erlaubten Zusatzfelder; nach ihrem Entfernen müssen zwei identische Transkripte übrig bleiben. `branches` ist das einzige optionale Feld auf oberster Ebene — eine leere Liste würde einen Befund behaupten, den eine Quelle ohne Baumzugriff nicht treffen kann.

Zur Laufzeit erzwingt das nichts. Der Wächter ist `tests/test_wegegleichheit.py`, und er hat sich bewährt: Er fiel durch, als ein neu hinzugekommenes Feld nur auf einer Seite ankam.

## 2.6 Ersetzen

Ein veralteter Chat wird **als Ganzes ersetzt**, nie fortgeschrieben — das macht den Entwurf von keiner undokumentierten Eigenschaft abhängig, und aus dem ZIP kostet es nichts.

**Ersetzen heißt aufräumen:** Vor dem Schreiben entfernt das Werkzeug alle im Protokoll vermerkten Dateien des vorherigen Eintrags (`file` und `side_files`) und **nennt sie in der Ausgabe** — stilles Löschen wäre die nächste Fehlerquelle. Aufgeräumt wird vor dem Schreiben, weil sich der Dateistamm geändert haben kann. Zwei nachgestellte Fälle erzwingen das: die **Umbenennung** (der Name trägt den Titel-Slug, ohne Aufräumen entsteht ein zweiter Stamm und ein Grep findet beide Fassungen) und die **wegfallende Nebendatei** (die neue Fassung hat kein Denken oder keinen Anhang mehr, die alte Datei bliebe auffindbar).

Die Gegenrichtung gehört dazu: `diff` meldet **Waisen** — Dateien im Verzeichnis, die kein Protokolleintrag beansprucht. Es ist die einzige Stelle, die ein Zuviel statt eines Zuwenig bemerkt, und sie warnt davor, blind zu löschen: das Protokoll ist die Autorität, nicht das Verzeichnis.

## 2.7 Auswahl strukturell, nie inhaltlich

Filterentscheidungen stützen sich auf Struktur — Feldwerte, Längen, Flaggen — und nie auf Inhaltsmerkmale wie Trigger-Wörter: die sind sprachabhängig und brechen, sobald ein Chat die Sprache wechselt. Inhaltssignale sind als **Prüfmaßstab** erlaubt, um einen strukturellen Schwellwert zu validieren, stehen aber nie im Code. Anwendungsfall mit Messung: die Denkblock-Auswahl in 3.1.3.

## 2.8 Transkriptionsdisziplin

Gilt für jeden Weg, auf dem Chattext durch den Kontext einer Instanz läuft. **Auslassen und Umformulieren sind Gegensätze, keine Grade:** Ausgelassenes fehlt sichtbar und ist nachholbar; Umformuliertes landet im Archiv, als wäre es echt — ein erfundener Datensatz, kein beschädigter. Deshalb: nie zusammenfassen, nie „handhabbar machen", nie ein eigenes Auslassungszeichen schreiben. Lieber weniger übertragen, das aber exakt.

Beide heutigen Wege umgehen diese Gefahr baulich, weil der Chattext als Datei am Modell vorbeigeht und nie durch einen Kontext läuft (1.2). Die Vorgabe bleibt trotzdem in Kraft: Sie ist der Grund, warum keine Instanz aufgefordert werden darf, Chattext selbst zu übertragen — und warum die Suchschnipsel-Rekonstruktion verworfen wurde (1.7).

## 2.9 Docstring und Doku müssen zum Code passen

Jedes Skript dieses Ordners trägt seine vollständige Betriebsanleitung im eigenen Docstring. Der Grund: Claude Code liest den Docstring, nicht zwangsläufig diese Doku — und die zweite Umsetzung unter `tests/` (2.5) darf nichts aus diesem Repo importieren, weil sie als einzelne Datei für sich stehen muss. Die Folge ist der Preis von 2.5: Formatgleichheit ist nicht erzwingbar, nur per Test gesichert.

Zweimal ist die Zusage stillschweigend gebrochen worden — ein Feature kam hinzu, der Docstring blieb beim alten Stand. `tests/test_docstrings.py` ist der Wächter dagegen: mechanisch für jedes Kommando und jedes `--Flag` (per Regex aus dem Quelltext gezogen, gegen den eigenen Docstring geprüft), von Hand für Begriffe, die kein Parser findet (Feldnamen, Dateiendungen, Funktionsnamen) — diese Liste muss bei jedem neuen Feature nachgezogen werden, das ist kein Testversehen, sondern der Punkt.
**Dasselbe gilt für diese Doku, und zwar in beiden Richtungen.** Kommandonamen, Flags und Feldnamen sind hier genauso gegen den Code zu halten wie Kapitelverweise — ein Kommandoname ist kein Verweis, deshalb fällt er bei einer Verweisprüfung durch. Am 22. August 2026 hat eine Prüfung 198 Kapitelverweise und 72 Code-Verweise inhaltlich abgearbeitet und dabei übersehen, dass 1.4 zwei Kommandos des entfallenen Lese-Wegs als rechnende Kommandos des Konverters führte.

**Die Gegenrichtung ist die ergiebigere:** Nennt die Doku etwas, das es nicht gibt, stolpert ein Leser darüber. Schreibt der Code ein Feld, das die Doku nicht nennt, hinterlässt das keine Spur im Text und fällt beim Lesen nie auf — so war `imported_at` durchgerutscht, in jeder Chatdatei vorhanden und nirgends dokumentiert. Beide Feldmengen holt man deshalb aus dem **laufenden Code** (`chat_document()` für die Chatdatei, `load_protocol()` und der Eintragsaufbau in `update_from_list()` für das Protokoll) und hält sie gegen die Backtick-Begriffe in 2.2 bzw. 2.4, statt die Doku abzuschreiben.

**Drei Sorten Falsch-Positive** treten dabei zuverlässig auf und sind keine Befunde: Flags fremder Werkzeuge (`--chrome`, `--add-dir`, `--dry-run`, `--teleport`), Feldnamen der claude.ai-Weboberfläche und des Rohexports (`capabilities`, `pagination`, `is_private`, `extracted_content`) und Werkzeugnamen aus den Messungen in 3.1.1 (`bash_tool`, `web_search`, `project_knowledge_search`). Wer sie erneut meldet, hat die Herkunft nicht geprüft.

## 2.10 Zielorte