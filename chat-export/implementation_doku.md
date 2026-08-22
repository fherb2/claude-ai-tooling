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
| `turns` | Anzahl der Redebeiträge, die der Chat trägt. Bei einer Hülle bleibt `messages` leer, `turns` nennt aber weiter die Länge des Gerüsts — die Auskunft, wie groß der Chat vor seiner Löschung war |
| `total_turns`, `complete`, `turns_missing` | Vollständigkeit samt Beleg; keiner der beiden Wege hat ein Sollmaß, also durchgehend `null` (2.5) |
| `deleted` | Hülle eines an der Quelle gelöschten Chats; dann ohne `messages` |
| `branches` | mitgenommene Nebenzweige des Nachrichtenbaums (3.1.2); **einziges optionales Feld** — s. 2.5 |
| `dropped_duplicates` | übersprungene Sendewiederholungen |
| `dropped_blocks` | weggelassene Blocktypen je Anzahl, **ohne** `thinking` — das liegt in der Denkdatei und wäre kein Verlust |
| `dropped_thinking` | verworfene Denkblöcke nach den Schwellen in 3.1.3 |
| `attachments_with_content` | Anhänge, deren Text mitkam (Dateien, nicht Nachrichten) |
| `creations` | Erzeugnisse der KI, deren Inhalt mitkam (Artefakte, erstellte Dateien, Änderungen) |
| `attachments_without_content` | Namen der Verweise, deren Inhalt die Quelle nicht hat. Ein **Name** ist ein Schlüssel: Derselbe Name im `files`-Feld und in einem inhaltslosen `attachments`-Eintrag ist eine Datei, zweimal aufgeführt, und zählt einmal. Ein **fehlender** Name ist kein Schlüssel — der Behelf nennt nur den Dateityp, nicht die Datei —, deshalb zählt dort jedes Vorkommen. Zusammengefasst wird je Nachricht, nicht über den Chat: derselbe Name in zwei Nachrichten sind zwei Verweise |

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
| `created_after` | Untergrenze für Chats ohne `created_at`: der Stand des **vorherigen** Abgleichs beim ersten Sehen — damals war das Projekt gelistet und der Chat nicht dabei, also entstand er später. Wird nur beim ersten Sehen gesetzt und danach nie überschrieben. Die Herleitung setzt eine **vollständige** vorherige Liste voraus (s. u.) |
| `listed_updated_at` | `updated_at` aus der zuletzt geholten Chatliste |
| `exported_updated_at` | Stand, auf dem der vorliegende Export beruht |
| `turns`, `total_turns` | Umfang beim Export |
| `end_token` | Rest einer blätternden Quelle; kein heutiger Weg schreibt es, nichts hängt daran |
| `file` | Name der Chatdatei, oder leer |
| `side_files` | Namen der Nebendateien, damit sie beim Ersetzen mit entfernt werden (2.6) |
| `status` | s. u. |
| `exported_at` | Zeitpunkt |

Statuswerte: `listed` (aus der Chatliste bekannt), `started` (teilweise gelesen — kein heutiger Weg setzt das, beide schreiben einen Chat immer ganz), `exported`, `stale` (die Quelle ist neuer als der Export), `deleted` (Hülle an der Quelle). `stale` entsteht durch den Vergleich `listed_updated_at` gegen `exported_updated_at`; `updated_at` trägt diese Erkennung, und zwar beobachtet: es liegt in allen Quellen vor — Export, Web-Chatliste, `recent_chats` — und sprang bei gelöschten Chats auf den Löschzeitpunkt.

**Zeitstempel werden über `is_newer()` verglichen, nie als reine Zeichenketten.** Die Quellen schreiben denselben Zeitpunkt unterschiedlich: Eine Chatliste endet auf `+00:00`, ein Archiv auf `Z`, und die Genauigkeit der Sekundenbruchteile schwankt. Ein roher Stringvergleich geht für den identischen Zeitpunkt nur deshalb gut aus, weil `+` in ASCII vor `Z` liegt — und er ordnet falsch, sobald die Bruchteile abweichen: `…00.5+00:00` sortiert vor `…00Z`, obwohl es später liegt. Die eine Funktion, die das entscheidet, verhindert außerdem, dass ein Aufrufer den Vergleich verdreht; die Fenstergrenze sortiert über denselben Schlüssel.

**Ein `deleted`-Eintrag wird wieder `stale`, wenn die Liste ihn mit neuerem Stand führt.** Das ist kein Grenzfall, sondern ein Widerspruch: Ein an der Quelle gelöschter Chat fällt aus der Chatliste heraus (1.6), kann dort also keinen neueren Stand bekommen. Führt die Liste ihn dennoch, hat die Hüllen-Erkennung fehlgegriffen — und die Beförderung nach `stale` lässt diesen Fehler von selbst heilen, statt den Chat dauerhaft aus der Aktualisierung zu nehmen. Ein unveränderter Stand lässt ihn `deleted`, sonst würde jeder Listenlauf jeden gelöschten Chat erneut holen.

**Eine Quelle, die älter ist als die Chatliste, macht einen Chat nicht `exported`.** Wird ein als `stale` geführter Chat aus einem veralteten Archiv umgewandelt — der realistische Fall sind mehrere Export-ZIPs in einem Download-Ordner —, dann wird die Datei geschrieben, denn sie ist, was diese Quelle hergibt; der Eintrag bleibt aber `stale`, und der Lauf sagt es unter Nennung beider Zeitstempel. Ohne diese Prüfung fiele `exported_updated_at` auf den alten Stand zurück und `diff` meldete „nichts offen" — ein Abgleich, den niemand geleistet hat.

**Ein Chat, den die frische Liste nicht mehr führt, wird gemeldet und nie automatisch entfernt.** Die Meldung nennt ihn samt Status; das Protokoll behält ihn, und seine Dateien bleiben liegen. Der Grund ist, dass drei sehr verschiedene Fälle von hier aus ununterscheidbar sind: Löschung an der Quelle, Verschieben in ein anderes Projekt — oder eine Chatliste, die der Nutzer nicht bis zum Ende geblättert hat. Beim letzten Fall wäre jede Entfernung ein Datenverlust aus einem Bedienfehler. Die Regel bindet **beide** Wege. Derselbe Wortlaut steht als Konstante `VANISHED_NOTE` auch im Maßstab aus 2.5, der nichts aus dem Konverter importieren darf und ihn deshalb zweimal hält; `tests/test_wegegleichheit.py` sichert die zwei Fassungen gegen Auseinanderdriften.

Auf oberster Ebene trägt das Protokoll `chats` — die Einträge oben, nach Chat-UUID gestellt —, dazu `protocol_version`, `project`, `project_created_at` (Beginn des Quellprojekts — aus dem Projekt-Endpunkt des Web-Wegs oder aus den Projektdateien eines Exports, eingetragen über `list --project-created`), `listed_at` (Zeitpunkt des letzten Listenabgleichs, gesetzt von `list` bzw. `map`) und `order` — eine Bearbeitungsrichtung, die kein heutiger Weg setzt und beide unangetastet erhalten: ein Protokoll, ein Schema.

**Die Fenstergrenze, in einer Tabelle.** Wie weit ein Export zurückreichen muss, damit er einen Chat erfasst, ergibt sich aus drei Quellen unterschiedlicher Güte — genommen wird das Minimum über alle zu holenden Chats:

| Chat-Lage | Fensterstart | Güte |
| --- | --- | --- |
| schon exportiert, aber gewachsen | sein `created_at` aus dem Protokoll | exakt |
| erst beim letzten Abgleich hinzugekommen | sein `created_after` | exakt, **sofern die vorherige Liste vollständig war** — s. u. |
| gelistet, aber nie in einem Archiv, ohne `created_after` | `created_at` des Projekts, aus dem Projekt-Endpunkt oder den Projektdateien eines Exports (3.1.1) | exakt, aber projektweit statt chatweise |
| über den Web-Weg gelistet | sein eigenes `created_at` aus der Chatliste | exakt — deshalb braucht dieser Weg kein Projektdatum von außen |
| kein Protokoll (Erstmigration) | ebenso der Projektbeginn | dito |

Der Projektbeginn ist dabei die Untergrenze über alles: kein Chat eines Projekts kann älter sein als das Projekt. Ein zu großzügiges Fenster kostet nur Downloadgröße, ein zu knappes kostet Inhalt — deshalb im Zweifel aufrunden, nach unten.

**Die Grenze von `created_after` ist so gut wie die Liste, aus der sie stammt.** War jene frühere Liste unvollständig — nicht bis zum Ende geblättert, denselben Fall führt diese Vorgabe bei den verschwundenen Chats als reale Bedienlage —, dann fehlte ein alter Chat dort nicht, weil er noch nicht existierte, sondern weil niemand ihn gesehen hat. Er bekommt beim ersten Sehen ein zu spätes `created_after`, das Fenster wird zu kurz, und weil der Wert nie überschrieben wird, bleibt es bei jedem weiteren Lauf zu kurz. `convert` meldet ihn zwar als fehlend, aber die Fenstergrenze korrigiert sich nicht von selbst; wer den Fall vermutet, setzt sie einmal von Hand weiter zurück. Betroffen ist praktisch nur der `--map`-Pfad: Der Web-Weg blättert deterministisch über `pagination.has_more`, dort kann eine Liste nicht unbemerkt unvollständig sein.

Umgesetzt als `window_start()` — im Konverter und, zum Vergleich, im Maßstab aus 2.5 —, mit `unbounded` als eigenem Ergebnis: hat ein wartender Chat keine der drei Quellen, wird das **gemeldet statt geschätzt**. Im ZIP-Weg tragen `list` und `diff` das Ergebnis vor, beide über dieselbe Funktion `window_lines()` — zwei Kommandos, die dieselbe Rechnung in eigenen Worten ausgeben, driften auseinander (3.1.6). Der Projektbeginn kommt von außen herein (`--project-created`), weil eine Konversation im Archiv keinen Projektbezug trägt: Im Web-Weg liefert ihn der Projekt-Endpunkt, im reinen Export-Weg liest ihn `inspect_export.py` aus den Projektdateien, sonst kennt ihn nur der Nutzer. Gegen den Tippfehler dabei steht `project_start_warnings()`: ein Chat, der älter ist als sein Projekt, kann nicht zu ihm gehören, also stimmt entweder das Datum oder die Chatliste nicht. Ohne diese Prüfung würde ein falsch getipptes Datum jedes künftige Fenster still verkürzen. Beide Funktionen laufen in `tests/test_wegegleichheit.py` über dieselbe Falltabelle, damit die zwei Implementierungen nicht auseinanderdriften.

Geprüft von `tests/test_wegegleichheit.py`, das auch die Protokolle vergleicht — gleiche Schlüsselmengen, gleiche Kernfelder. Gegen die zweite Umsetzung (2.5) dürfen genau drei Felder abweichen, weil eine Seite sie nicht wissen kann: `created_at`, `total_turns` und `file`, dem dort das Datumssegment fehlt (2.3).

## 2.5 Wegegleichheit

Beide Wege erzeugen für denselben Chat **dieselbe Chatdatei** und **dasselbe Protokoll** (Protokollabgleich in 2.4). Sonst hinge der Inhalt des Archivs davon ab, auf welchem Weg ein Chat hereinkam, und „habe ich diesen Chat?" würde unscharf.

Zwischen Kontoexport und Web-Weg ist das **baulich** erfüllt: Beide laufen durch denselben Konverter, und nur das Auspacken unterscheidet sich (3.1). Ein einziges Metadatenfeld weicht deshalb tatsächlich ab — `source`, der Herkunftsvermerk. Keiner der beiden Wege hat ein **Sollmaß**, an dem sich Vollständigkeit rechnen ließe: `total_turns`, `complete` und `turns_missing` bleiben durchgehend `null`, statt eine Zahl zu behaupten. An echten Daten belegt: Für denselben Chat liefern Web-API und Export-ZIP dieselben Nachrichten-UUIDs.

**Gemessen wird die Zusage trotzdem gegen eine zweite, unabhängige Umsetzung** des Dateiformats: `tests/wegegleichheit_referenz.py`, die allein zu diesem Zweck existiert und nichts aus dem Konverter importiert. Der Grund ist der Wert eines Maßstabs: Prüfte der Konverter nur gegen sich selbst, würde jede Formatänderung automatisch „bestehen". Gegen diese zweite Umsetzung dürfen genau **fünf** Metadatenfelder abweichen — `source`, `created_at`, `total_turns`, `complete`, `turns_missing` — und keines mehr. Wo eine Seite etwas nicht wissen kann, steht `null` statt einer Vermutung.

**Eine bekannte Grenze dieser baulichen Gleichheit:** Der Text einer Nachricht ohne `content`-Blöcke kommt aus dem flachen `text`-Feld — und das gibt es nur im Kontoexport, nicht in der Web-Form. Eine solche Nachricht ist bisher nie aufgetreten (0 von 10.779 in den vorliegenden Archiven), aber falls doch, schrieben die beiden Wege für denselben Chat verschiedene Transkripte. Festgehalten, weil die Zusage an dieser einen Stelle von einem Feld abhängt, das nur eine Quelle hat.

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

Primärziel ist `<projekt>/.claude/imported_chats/` im versionierten Repo des Zielprojekts. **Dieselben Dateien** dienen unverändert auch dem Projektwissen einer claude.ai-/Desktop-/Cowork-Instanz; es gibt keine zielabhängige Ausgabeform. Ein Verzeichnis je Quellprojekt, **flach** — Projektwissen kennt keine Unterordner. Ein **dritter** Zielort ist `~/.claude/projects/<projekt>/`, für Chats, die nicht ins geteilte Repo dürfen — aber nur auf ausdrückliche Anordnung des Nutzers und nur unter den drei Bedingungen aus 1.3 (hochgesetzte Aufbewahrungsdauer, bewusst erteilte Ausnahme von §1.2 der Arbeitsanweisungen, Kenntnis von `claude project purge`). Ohne diese Anordnung schreibt kein Lauf dorthin.

Diese Vorgabe gilt den **Archivdateien**. Der Anweisungsblock, den `convert` am Ende ausgibt (3.1.6), ist keine Archivdatei, sondern Konsolenausgabe für den Nutzer — er ist bewusst zielabhängig, weil die drei Zielorte sich im Suchmittel und im Einsetzort unterscheiden.

## 2.11 Tests ohne echten Chatinhalt

Prüfstücke werden synthetisch gebaut; echter Chatinhalt gehört nie in Tests oder Fixtures. Echte Exporte liegen ausschließlich unter `test_results/`, deren Inhalte die `.gitignore` vom Repo fernhält. Diagnosewerkzeuge (3.2) geben Struktur und Zahlen aus, nie Inhalt — ihre Ausgabe muss unbedenklich in eine Konversation kopierbar sein.


# 3 Skripte

## 3.1 `chat_export_convert.py` — der Weg über den Kontoexport und über die Web-Endpunkte

**Status: gebaut, geprüft durch `tests/test_export_convert.py`, auch unter `-O`. Am Drei-Monats-Export mit 211 Chats gelaufen.**

Wandelt Chats in Dateien je Quellprojekt um und führt das Protokoll. Läuft lokal, wird nie hochgeladen. Es liegt in `skills/chat-export/` — es ist das eine Skript, das der Skill mitbringt (3.3), und der Ordner trägt genau die Struktur, die er am Zielort haben wird.

**Zwei Quellen, ein Konverter.** Die Chats kommen entweder aus einem Kontoexport-ZIP (`--zip`) oder aus einem **Web-Behälter** (`--bundle`) — der Datei, die ein Browserschritt aus den claude.ai-Endpunkten schreibt. Beide führen dieselben Feldnamen je Konversation, weshalb sich der Unterschied auf das Auspacken beschränkt: Ab `conversation_record()` ist der Code geteilt. Am 19. August 2026 am echten Fall bestätigt — für denselben Chat nannten Web-API und Export-ZIP nicht nur dieselben Zahlen, sondern **dieselben Nachrichten-UUIDs**. Am 21. August 2026 an einem zweiten, größeren Fall wiederholt: ein Großimport aus vier realen Projekten mit 171 Chats über den Export-Weg, alle 171 Protokoll-UUIDs gegen die tatsächliche Export-ZIP verifiziert — 171 von 171 gefunden, keine Abweichung (3.1.7).

Damit ist die Wegegleichheit (Vorgabe 2.5) hier **baulich** gegeben statt bloß geprüft. Abweichen darf genau ein Feld: Die Chatdatei nennt als Herkunft `web-api` statt `account-export`, und `source` ist eines der fünf erlaubten. Dass sonst nichts abweicht, vergleicht `tests/test_export_convert.py` Datei für Datei — an einem Prüfbestand, der alle drei Nebendateiarten und einen Nebenzweig trägt, damit der Vergleich etwas aussagt.

Die Chatliste des Web-Behälters trägt außerdem `created_at` je Chat. Das ist der Grund, warum `list --web` kein Projektdatum von außen braucht: Die Fenstergrenze steht exakt in den Daten, statt über den Projektbeginn genähert zu werden (Vorgabe 2.4).

### 3.1.1 Aufbau des Export-ZIP

Alles beobachtet, nichts davon dokumentiert.

```
users.json                    uuid, full_name, email_address, verified_phone_number
projects/<uuid>.json  (n×)    uuid, name, description, is_private,
                              is_starter_project, prompt_template,
                              created_at, updated_at, creator, docs
memories.json
login_history.json            erst im zweiten Export vorhanden, s. u.
conversations.json            Liste von Konversationen
```

**Die Mitgliederliste ist nicht stabil.** `login_history.json` fehlte im Export vom 6. August 2026 und war im Export vom 8. August enthalten — zwei Tage Abstand, gleiches Konto. Der Fund kam von der Schemawache (3.2), die das Archiv gegen diese Liste hält; Konversations-, Nachrichten- und Blockschlüssel waren unverändert, der Zuwachs also harmlos. Folgerung für den Entwurf: Ein Werkzeug darf sich nie darauf verlassen, **welche** Mitglieder ein Archiv hat, sondern nur darauf, dass `conversations.json` darunter ist. Weiteres in 4.2.

Projektdateien enthalten **keine Chats** — nur Projektanweisungen und Wissensdokumente. Die Chats liegen ausschließlich in `conversations.json`.

**Die Projektdateien sind vom Zeitraumfilter ausgenommen, und ihr `created_at` ist der Projektbeginn.** Zwei Exporte mit verschiedenen Zeiträumen enthielten dieselben 43 Projektdateien, jede mit `created_at`, ältestes 2025-06-18 — der Filter wirkt auf `conversations.json`, nicht auf `projects/`. Daraus folgt eine Rechnung, die den Entwurf trägt: **kein Chat eines Projekts kann älter sein als das Projekt**, also ist dessen `created_at` die garantierte Untergrenze für jedes Exportfenster. Gegengeprüft am echten Fall: Projekt `FreeCAD-Bedienung` trägt `created_at` 2025-11-10, und der älteste Chat darin wurde am 2025-11-10 erstellt. Praktische Folge in 1.5: **ein Kurzzeitraum-Export von einer Woche liefert alle Projektdaten** (5 MB statt 58) und damit das Datum, ab dem der eigentliche Export gehen muss.

Eine Konversation hat genau sieben Felder: `uuid`, `name`, `summary`, `created_at`, `updated_at`, `account`, `chat_messages`. **Kein Projektbezug.**

Eine Nachricht: `uuid`, `text`, `content`, `sender` (`human`/`assistant`), `created_at`, `updated_at`, `attachments`, `files`, `parent_message_uuid`.

**`attachments` und `files` sind nicht dasselbe**, und die Verwechslung kostet Inhalt:

| Feld | Zahl | Felder | Inhalt |
| ------------- | ---- | ------------------------------------------------------------- | ------ |
| `attachments` | 341  | `file_name`, `file_size`, `file_type`, **`extracted_content`** | **da** |
| `files`       | 524  | `file_uuid`, `file_name`                                      | fehlt  |

Keiner der 341 ist leer, zusammen 9.635.919 Zeichen, Median 13.265, größter 169.818. Dateitypen überwiegend `text/x-python` (238), dazu `text/markdown` (26), `txt` (22), `x-shellscript` (11). Bei **22** ist der `file_name` leer, der Inhalt aber vorhanden — mehrere Kilobyte Code; ein Fragezeichen als Name würde das verstecken.

**Die beiden Felder sind nicht disjunkt.** Am Testlauf vom 17. August direkt beobachtet: Dieselbe Nachricht führt `test_docstrings.py` zweimal — unter `attachments` mit 4.481 Zeichen `extracted_content` und unter `files` mit `file_uuid` und Namen. Ein angehängtes Bild dagegen steht **nur** unter `files`. Der Export verzeichnet also jeden Upload als Dateiobjekt und legt den extrahierten Text daneben, wenn er einen gewinnen konnte. Am Drei-Monats-Export nachgemessen: 319 der 524 `files`-Einträge haben ihren Inhalt in derselben Nachricht, 205 nicht (Beleglage und Rest in 1.6). Verbindender Schlüssel ist allein der Name — `files` trägt eine `file_uuid`, `attachments` keine —, weshalb die 22 namenlosen Anhänge oben genau die Fälle sind, die sich nicht zuordnen lassen.

Blocktypen in `content`: `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`. Bei `token_budget` war `remaining` in allen Fällen `null`. Nichts war als `truncated` oder `cut_off` markiert.

**Die Blockschlüssel, als Vergleichsgrundlage.** 3.2 verspricht, die Vereinigung aller Konversations-, Nachrichten- **und Blockschlüssel** gegen diesen Abschnitt zu halten; für die dritte Menge fehlte sie bisher. Beobachtet am Testexport vom 17. August 2026, der alle Blocktypen außer `token_budget` enthielt:

```
alternative_display_type, approval_key, approval_key_legacy, approval_options,
citations, citations_grouping_mode, content, context, cut_off, display_content,
flags, hidden, hidden_in_chat, icon_name, id, input, integration_icon_url,
integration_name, is_error, is_mcp_app, mcp_server_url, message, meta, name,
signature, start_timestamp, stop_timestamp, structured_content, summaries, text,
thinking, thinking_hidden, tool_identifier, tool_origin, tool_use_id, truncated,
type
```

Es ist die Vereinigung über **alle** Blocktypen, nicht die Feldliste eines einzelnen: `thinking`, `thinking_hidden` und `summaries` gehören zum Denkblock, `input`, `name` und `tool_use_id` zum Werkzeugaufruf, die `mcp_*`- und `approval_*`-Namen zu dessen neueren Spielarten. Ein **fehlender** Name ist das Warnsignal, ein hinzugekommener meist nur ein Ausbau — dieselbe Lesart wie bei den Archivmitgliedern oben.

**Der Werkzeugverkehr, vermessen.** `tool_result` ist mit 28,6 Mio Zeichen der größte Einzelposten des Exports — 2,5× der Gesprächstext —, aber überwiegend fremd oder redundant: `project_knowledge_search` 9,2 Mio (Treffer aus dem eigenen Projektwissen, also Duplikate vorhandener Doku), `web_search` 8,5 Mio (fremde Snippets), `view` 4,9 Mio (Wiederanzeigen ohnehin erfasster Dateien), `bash_tool` 2,9 Mio (Kommandoausgaben). In `tool_use` (5,9 Mio input) stecken dagegen die **Erzeugnisse der KI**, das Gegenstück zu den Anhängen: `artifacts` create/rewrite/update mit 1,79 Mio Zeichen Inhalt (240 Aufrufe), `create_file.file_text` mit 2,44 Mio (218 Dateien: 88× md, 50× py, 35× json), `str_replace` mit 0,13 Mio Änderungstext — zusammen **4,4 Mio Zeichen**, bei Chats ohne begleitendes Repo die einzige Kopie dieser Werke. Messhinweis: `create_file` trägt den Inhalt im Feld `file_text`, nicht `content`.

**Die Denkschritte, vermessen.** 4.318 `thinking`-Blöcke, Länge Median 682, Mittel 2.153, größter 66.488 Zeichen — keine Statusnotizen. Sie sind auch **nicht redundant**: über 1.840 Nachrichten mit substanziellem Denken *und* sichtbarer Antwort verglichen, taucht nur ein **Median von 9 %** des Denk-Vokabulars in der Antwort wieder auf; in 1.824 Fällen unter 40 %, in keinem über 80 %. **42 %** der Blöcke (1.809) enthalten Abwägungen — Diagnosen, verworfene Alternativen samt Grund, Ursachenlisten. URLs kommen dagegen kaum vor (13 Blöcke), Dateinamen in 1.067.

Das Feld `summaries` (in 3.788 Blöcken, Median 241 Zeichen) ist **keine Zusammenfassung der Schlüsse**, sondern eine Verlaufsmeldung dessen, was gerade durchdacht wird — für ein Archiv wertlos.

**Denken kann dabei sein, muss aber nicht.** Ein Denkblock kommt in zwei Ausprägungen: mit Text, oder als `thinking_hidden` mit null Zeichen. Beide stehen nebeneinander, und das Verhältnis schwankt erheblich — im Drei-Monats-Export 788 versteckte unter 4.318, in den Testexporten vom 17. und 18. August 2026 ausschließlich versteckte, und innerhalb **eines einzigen** Chats wechselte es von Tag zu Tag. Woran es hängt, ist nicht ermittelt und wird hier auch nicht vermutet.

**Ein Export ohne Denktext ist deshalb kein Befund über das Format.** Wer in einem frischen Archiv keine Denkdatei findet, hat eine Stichprobe gezogen, mehr nicht; der Schluss „der Export führt keine Denkschritte" wäre falsch und ist hier schon einmal beinahe gezogen worden. Ist Denktext vorhanden, wird er unverändert genutzt; fehlt er, ist nichts zu holen, und das Verwerfen leerer Blöcke nach 3.1.3 bleibt verlustfrei.

Drei strukturelle Befunde, die die Auswahl tragen; die Festlegung, die daraus folgt, steht in 3.1.3:

| Merkmal                        | Blöcke      | Volumen        | mit Abwägungsmarker |
| ------------------------------ | ----------- | -------------- | ------------------- |
| `thinking_hidden=True`         | 788 (18 %)  | **0 Zeichen**  | 0 %                 |
| kürzer als 200 Zeichen         | 1.367 (32 %)| 71.784 (0,8 %) | 2 %                 |
| Rest (nicht hidden, ≥200)      | 2.951 (68 %)| 9.227.033 (99,2 %) | 60 %            |

Die Medianlänge trennt dabei deutlicher als jedes Verhältnis: mit Marker 2.537 Zeichen, ohne 176 — Faktor 14. Ein `summaries` existiert außerdem **nicht immer** (530 Blöcke ohne), ein Verhältnis wäre für die also gar nicht bildbar.

**Das flache `text`-Feld enthält die Denkschritte.** Gemessen am Drei-Monats-Export: Summe über `text` 20.810.589 Zeichen, Summe der Textblöcke 11.266.956 — die Differenz von 9,5 Mio sind die `thinking`-Inhalte. In einem Beispiel beginnt `text` mit dem Wortlaut des Denkblocks, während der erste Textblock nur ein Leerzeichen enthält. Das eigentliche Gesprächsvolumen ist also **11,3 Mio Zeichen**, nicht 20,8. Wer `text` nimmt, schreibt Claudes interne Überlegungen ins Archiv; wer die Textblöcke nimmt, bekommt das Gesagte. Auch die Blockreihenfolge ist nicht schematisch — beobachtet wurde `['text', 'thinking', 'text']` —, weshalb die Textblöcke in ihrer Reihenfolge aneinandergehängt werden und nicht etwa „alles nach dem Denken".

### 3.1.2 Der Nachrichtenbaum

Die Nachrichten eines Chats bilden **keine Kette, sondern einen Baum**: jede zeigt per `parent_message_uuid` auf ihre Vorgängerin. Hängen an *einer* Vorgängerin mehrere Nachrichten, gabelt sich der Chat — weil eine Frage nachbearbeitet, eine Antwort neu erzeugt oder eine Nachricht mehrfach gesendet wurde.

Befund am Drei-Monats-Export: **20 Gabelungen in 13 von 211 Konversationen.** Kein Randfall.

**Regel 1: Gefolgt wird dem Pfad zur neuesten Nachricht im ganzen Baum** — nicht dem jüngsten Kind an der Gabelung. Die beiden Regeln fallen fast immer zusammen, aber nicht immer, und der Unterschied kostet Inhalt. Gegenbeispiel aus „Home-Verzeichnis zurück synchronisieren":

| Kind | Zeit | Nachfahren |
| --------- | -------- | -------------- |
| `019efe1f` | 09:31:50 | **29** |
| `019efe20` | 09:33:55 | 1 |

Hier trägt das **ältere** Kind das Gespräch. „Jüngstes Kind" hätte 29 Nachrichten weggeworfen und eine Sackgasse ins Archiv geschrieben. Der Pfad zur neuesten Nachricht greift in allen 20 Fällen richtig.

**Regel 2: Verworfene Zweige kommen mit, in ein eigenes Feld — außer wenn sie mit dem gewählten Geschwister in allem übereinstimmen, was mitwandert.** Was in den verworfenen Zweigen steckt, zeigen dieselben Daten:

- **Meist Dubletten.** Bei „Dell DA300 Dockingstation" hängen **14 Kinder** an derselben Stelle, alle mit **exakt 440 Zeichen**, im Abstand von Sekunden bis Minuten — ein Sende-Sturm. Ebenso 10× 37 Zeichen und 5× 553 Zeichen in anderen Chats. Ohne die Ausnahme in Regel 2 stünden allein dort 13 Kopien derselben Nachricht im Archiv.
- **Manchmal Fehlversuche.** Bei „Negativform Bajonett-Kurven" zwei Assistant-Kinder: eines mit **0 Zeichen**, eines mit 41.077. Das leere ist eine fehlgeschlagene Antwort.
- **Selten echter Inhalt.** Bei „Technische 2D-Zeichnung" sind die verworfenen Kinder 113 und 149 Zeichen — umformulierte Fragen, inhaltlich redundant. Im Gegenbeispiel oben hängen am verworfenen Zweig zwei echte Nachrichten.

**Gleichheit am Text allein reicht dafür nicht.** Sie ist genau die Prüfung, die bei der Hüllen-Erkennung schon zu eng war (3.1.3): Eine Nachricht kann aus einem Upload ohne ein einziges Begleitwort bestehen — 22 von 10.779 Nachrichten über alle vorliegenden Archive, davon 9 im Drei-Monats-Export und 13 in einem weiteren. Zwischen zwei solchen entscheidet der Textvergleich nichts, weil beide Texte leer sind; das Geschwister gälte als Sendewiederholung, und sein Anhang fiele mit ihm weg, gezählt als Dublette und in keiner anderen Zahl genannt. Wer eine Upload-Nachricht nachbearbeitet und die Datei austauscht, erzeugt genau dieses Paar. Verglichen werden deshalb dieselben vier Merkmale, die auch eine Hülle von einem Chat unterscheiden: Gesprächstext, Anhang mit Inhalt, Erzeugnis, behaltener Denkblock. Alle vier sind strukturell (Vorgabe 2.7), und die Reihenfolge folgt den Kosten — der Text ist der billigste und trennschärfste Vergleich, die Anhangsinhalte werden nur angefasst, wenn die Texte schon gleich sind.

Deshalb mitnehmen statt zählen: Das Ziel des Archivs ist Wiederfinden, nicht die Rekonstruktion des Gesprächsverlaufs. Wer sucht, will den Satz finden, egal auf welchem Zweig er stand. Eine bloße Zahl („1 Zweig verworfen") verschweigt, ob darin zwei oder vierzig Nachrichten lagen.

**Regel 3: Was sich nicht einordnen lässt, wird gemeldet.** Das ist der vierte Ausgang der Integritätsrechnung (3.1.7) und trifft genau **einen** Fall: einen **Zyklus in den Elternzeigern abseits des gewählten Pfads**. Jedes Mitglied zeigt auf ein anderes Mitglied, hat also einen Elternteil innerhalb des Chats, der nicht auf dem Pfad liegt — keines wird damit je Zweigkopf, und keines ist von einem Zweigkopf aus erreichbar. Gemessen an gestellten Fällen: ein solches Paar → 2 von 4 Nachrichten platziert, 2 gemeldet; mit einem angehängten Kind → 2 von 5, 3 gemeldet.

Zwei Fälle sehen ähnlich aus und sind es nicht. Ein Elternteil, der **gar nicht** in dieser Konversation vorkommt, macht seine Nachricht zum Zweigkopf — sie kommt vollständig mit, es gibt nichts zu melden. Und ein Zyklus, der **auf** dem Pfad liegt, wird von der Pfadsuche über ihren Besuchsschutz einmal abgelaufen und mitgenommen; auch dort geht nichts verloren. Nur die Kombination aus Zyklus und Abseitslage verliert wirklich Inhalt, und dann ist der Export beschädigt — in keinem der vorliegenden Archive kommt das vor. Die Meldung bleibt trotzdem, denn sie ist das Einzige, was diesen Verlust überhaupt bemerkt; die Nachrichten selbst mitzunehmen wäre bei einem Zyklus keine sinnvolle Reihenfolge mehr.

Nicht zu verwechseln mit der **Waise** aus Vorgabe 2.6: Das ist eine Datei im Verzeichnis ohne Protokolleintrag, also ein Zuviel auf der Ablageseite — hier geht es um eine Nachricht, die im Baum keinen Platz findet.

### 3.1.3 Festlegungen und ihr Grund


| Festlegung                                             | Grund                                                                                                                                                                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Baum ablaufen statt nach`created_at` sortieren, Regeln in **3.1.2** | Sortieren nach Zeit schreibt nachbearbeitete Fragen doppelt ins Transkript und mischt Zweige, die nie aufeinander folgten |
| `content`-Blöcke statt `text`                         | `text` **enthält die Denkschritte** (Messung in 3.1.1) — es zu verwenden würde das Archiv mit internen Überlegungen fluten                                                                                                |
| Hüllen mit`deleted: true` und ohne `messages`         | Die Existenz bleibt erhalten, ohne ein leeres Transkript vorzutäuschen                                                                                                                                            |
| Zuordnung aus rohem`recent_chats`-Dump                 | Kein Formatieren von Hand nötig                                                                                                                                                                                   |
| Jede zugeordnete UUID gegen das ZIP prüfen            | Ein vertippter Wert würde einen Chat still falsch einordnen                                                                                                                                                       |
| Denkschritte und Anhänge in eigene Dateien nach Vorgabe **2.2** | Diagnosen und verworfene Alternativen erreichen die Antwort nie (9 % Vokabelüberlappung, Messung 3.1.1); getrennt gelegt bleibt das Gespräch schlank und die Mengenentscheidung fällt bei der Benutzung |
| Denkblöcke verwerfen, wenn`thinking_hidden` oder kürzer als 200 Zeichen | Verlustfrei bzw. nahezu: die hidden-Blöcke sind leer, die kurzen tragen 0,8 % des Inhalts und nur 2 % von ihnen einen Marker. Ein Drittel der Einträge fällt weg, das Volumen bleibt — Filtern schafft Ordnung, nicht Platz. Auswahl strukturell nach Vorgabe **2.7**; die Marker waren nur der Prüfmaßstab |
| Erzeugnisse in die vierte Datei, `tool_result` nur zählen | Die Auswahl ist strukturell (Werkzeugname + Feld, Vorgabe 2.7): `artifacts`-, `create_file`- und `str_replace`-Aufrufe tragen die Werke der KI (4,4 Mio Zeichen, Messung 3.1.1) — oft die einzige Kopie. `tool_result` (28,6 Mio) ist überwiegend fremd oder Duplikat und bliebe Ballast. Änderungen (`update`, `str_replace`) sind Deltas ohne Basis und werden als solche gekennzeichnet |

Das Ersetzen eines veralteten Chats samt Aufräumen der Vorgängerdateien ist Vorgabe **2.6**; beide erzwingenden Fälle — Umbenennung, wegfallende Nebendatei — sind dort benannt und hier nachgestellt worden.

**Hüllen erkennen:** Nachrichten vorhanden, aber **nichts, was mitwandert** — kein Gesprächstext, kein Anhang mit Inhalt, kein Erzeugnis, kein behaltener Denkblock. Das sind gelöschte Chats — im Browser gegengeprüft, sie existieren nicht mehr. Der Gesprächstext allein wäre ein zu enger Test: Ein Chat kann aus einem Upload ohne Begleitworte und einer fehlgeschlagenen Antwort bestehen und seinen Anhang trotzdem vollständig tragen. Alle vier Merkmale sind strukturell (Vorgabe 2.7). Der Zeitstempel unterscheidet zwei Löschwege: bei einer Massenlöschung tragen mehrere Chats sekundengleich dasselbe `updated_at`, bei einzeln gelöschten folgt es der eigenen letzten Nachricht. Der Unterschied ist unerklärt und praktisch belanglos.

**Das Löschen nimmt den Inhalt, nicht den Eintrag.** Am eigenen Testlauf nachgestellt: Zwei Chats wurden gelöscht, der Export **danach** angefordert — beide standen darin, mit Gerüst und null Zeichen Text. Anthropic sagt zu, gelöschte *Inhalte* kämen nicht in später angeforderte Exporte, und genau das trifft zu (1.6); der Eintrag selbst bleibt. In die Chatliste kommen sie dagegen nicht mehr, weshalb kein Lauf sie einem Projekt zuordnen kann — eine Hülle im Archiv entsteht also nur für einen Chat, der **zwischen** Listenabgleich und Export gelöscht wurde.

### 3.1.4 Dateiformat der Chatdateien

Format, Felder, Dateinamen und die Referenzmechanik sind die Vorgaben **2.2** und **2.3**; hier steht nur, was dieser Weg davon besonders macht.

Der ZIP-Weg ist der einzige, der `branches`, `dropped_duplicates`, `dropped_blocks`, `dropped_thinking` und die beiden `attachments_*`-Felder je mit Inhalt füllen kann — nur er sieht den Nachrichtenbaum und die Blockstruktur (2.5). Beim Drei-Monats-Export entstanden so 211 Gesprächs-, 145 Denk-, 62 Anhang- und 71 Erzeugnisdateien.


### 3.1.5 Aufbau des Protokolls

Das Protokoll ist Vorgabe **2.4**. Weder `end_token` noch `total_turns` werden gefüllt — es gibt kein Sollmaß (2.5) —, und `started` kommt nie vor: Ein Chat wird immer ganz geschrieben.


### 3.1.6 Kommandos

- `list --map <dump> | --web <behälter> --out <verzeichnis> [--project <name>]` — Protokoll anlegen oder ergänzen aus einer Chatliste. `--map` nimmt den rohen `recent_chats`-Abzug, `--web` die Liste aus dem Web-Behälter; letztere bringt `created_at` je Chat mit und braucht deshalb kein Projektdatum von außen. Fehlt beides, bricht der Aufruf ab. `--project` sollte immer mitgegeben werden: Ohne diese Angabe bleibt das Feld `project` im Protokoll leer, obwohl der Ordnername den Projektnamen längst trägt — beobachtet am Großlauf vom 21. August 2026. Neue Chats `listed`, vorhandene gegen `exported_updated_at` geprüft und ggf. `stale`. Meldet die Fenstergrenze (Vorgabe 2.4) und warnt vor einem unplausiblen Projektdatum. Meldet außerdem den umgekehrten Fall — Chats, die das Protokoll kennt und die Liste nicht mehr führt (Vorgabe 2.4); entfernt wird dabei nichts. **Der erste Schritt jedes Laufs**, vor jedem Chattext.

  Der Rohtext für `--map` kommt nicht von hier: er entsteht in einem Chat des Quellprojekts über das dort eingebaute `recent_chats` — und zwar in einem eigens dafür angelegten, danach gelöschten Chat, weil der laufende Chat in seiner eigenen Liste fehlt (Begründung in 1.5). `MAPPING_PROMPT` (Modulkonstante, siehe Docstring) ist der dafür wörtlich vorgegebene Prompt — nur im Codeblock ausgegeben bleibt er intakt, sonst verschluckt der Markdown-Renderer die `<chat>`-Tags als HTML (beobachtet).
- `convert --zip <datei> | --bundle <datei> --out <verzeichnis>` — die als `listed` oder `stale` geführten Chats aus der angegebenen Quelle holen, Baum ablaufen, Dateien schreiben, Protokoll fortschreiben. **Genau eine** Quelle, nie beide: Zwei Angaben oder keine bricht mit einer Meldung ab, statt sich eine auszusuchen. Ist die Quelle älter als der gelistete Stand, bleibt der Eintrag `stale` und der Lauf sagt es (Vorgabe 2.4).

  Der **Web-Behälter** ist eine JSON-Datei mit zwei je nach Schritt gefüllten Teilen — `conversations` mit den Kopfdaten je Chat für `list --web`, `chats` mit den vollständigen Konversationen für `convert --bundle`; dazu `fetched_at` und `organization` als Herkunftsvermerk. Gelesen von `load_bundle()`, ausgepackt von `bundle_records()` und `bundle_conversations()`. Ein Behälter ohne den gebrauchten Teil bricht mit einer Meldung ab und rät nicht.
- `diff --out <verzeichnis>` — Stand aus dem Protokoll: fehlend, veraltet, gelöscht, unbekannt. Braucht weder ZIP noch Chatdateien. Dazu **die Fenstergrenze** (Vorgabe 2.4) samt der Warnung vor einem unplausiblen Projektdatum — dieselben Sätze, die `list` ausgibt, hier aber ohne frische Chatliste: „was fehlt noch" und „wie weit muss der nächste Export zurückreichen" sind eine Frage, zweimal gestellt. Dazu der Waisen-Scan nach Vorgabe 2.6 — das Einzige, was ein Zuviel statt eines Zuwenig meldet.
- `report --out <verzeichnis>` — was ein bestehender Bestand an Verlusten trägt. Es liest dazu **die Dateien im Verzeichnis**, nicht die Protokolleinträge: Es beschreibt, was dort liegt. Eine Waise zählt daher in seinen Summen mit — das ist folgerichtig und nicht dasselbe wie `diff`, das über das Protokoll läuft und die Waise als Zuviel meldet (Vorgabe 2.6). Genannt werden: Hüllen, übersprungene Dubletten, weggelassene Blocktypen, verworfene Denkblöcke, `files`-Verweise ohne Inhalt. Was mitkam, steht als Gegengewicht daneben — Nebenzweige, Denkblöcke, Anhänge mit Inhalt, Erzeugnisse —, damit sichtbar ist, dass ein Chat nicht linear verlief bzw. wie viel an ihm hing. Die behaltenen Denkblöcke werden dabei aus den Nebendateien gezählt: die Gesprächsdatei führt nur die verworfenen, und ein zusätzliches Metadatenfeld dafür würde das Dateiformat beider Wege ändern (Vorgaben 2.2 und 2.5) — zu viel für eine Berichtszeile.

- `analyse --zip <datei> [--map <dump>]` — beschreibt, was der Leser aus einem Archiv macht, ohne etwas zu schreiben: gewählter Pfad, Nebenzweige, Umfang, und bei gegebener Zuordnung die UUIDs, die das Archiv nicht kennt. Es nennt **beide Seiten** — was mitkäme (Denkblöcke, Anhänge mit Inhalt, Erzeugnisse) und was wegfiele (verworfene Denkblöcke, Blocktypen, Hüllen, Sendewiederholungen, Namensverweise). Beantwortet eine andere Frage als 3.2 — das beschreibt den Rohexport, dieses die *Deutung*.

Der Unterschied zu `report` ist die Blickrichtung, nicht der Inhalt: `report` läuft über einen **fertigen Bestand**, `analyse` über das **ZIP** und schreibt nichts — es ist die Vorschau vor dem Lauf. Beide nennen deshalb dieselben Posten, und dass sie dieselben Zahlen liefern, sichert `tests/test_export_convert.py` über drei Prüfbestände ab. Der Grund für die Absicherung ist eine erlebte Drift: Anhänge kamen zuerst, Denkschritte und Erzeugnisse später, `report` wurde nachgezogen und `analyse` nicht — die Vorschau verschwieg damit zwei der drei Nebendateiarten und mit ihnen den größten mitgenommenen Posten überhaupt (Denkschritte, 9,2 Mio Zeichen gegen 9,6 der Anhänge und 4,4 der Erzeugnisse, Messung in 3.1.1).

Dazu ein fertig einfügbarer Textblock für das **Zielprojekt**: dass ein Chatarchiv vorliegt, wo es liegt, und dass es vor einer Rückfrage zu älterem Zusammenhang zu konsultieren ist. Damit wirkt die Anweisung dauerhaft — er ist die einzige Stelle, an der dieses Werkzeug im Zielprojekt fortwirkt; ohne ihn liegt das Archiv da und wird nie gelesen.

**Drei Fassungen, weil die Zielorte sich in genau dem unterscheiden, was der Block sagen soll** — wo das Archiv liegt und womit die Instanz es erreicht (1.3). Gewählt wird über `convert --target`; es steuert **nur** den Wortlaut, nicht eine geschriebene Datei (Vorgabe 2.10).

| `--target` | Zielort | Suchmittel | einzusetzen in |
| --- | --- | --- | --- |
| `repo` (Vorgabe) | `<projekt>/.claude/imported_chats/` | `Grep` und `Read` | die `CLAUDE.md` des Zielprojekts |
| `knowledge` | Projektwissen einer claude.ai-Instanz | Projektwissen bzw. Kontext | die Projektanweisungen dort |
| `home` | `~/.claude/projects/<projekt>/` | `Grep` und `Read` | die `CLAUDE.md` des Zielprojekts |

Die `home`-Fassung trägt zusätzlich die Zugänglichkeitsbedingung aus 1.3 und die Anweisung, ihr Fehlen zu melden statt das Archiv für leer zu halten.

**Nicht** in eine `CLAUDE.md` unterhalb von `.claude/imported_chats/`: Eine solche Datei lädt erst, wenn dort schon gelesen wird, und überlebt keine Kompaktierung — sie wäre genau dann stumm, wenn sie gebraucht wird (Begründung in der Repo-`CLAUDE.md`).

**Pfad und Dateiarten kommen aus dem Lauf**, nicht aus einer festen Liste: der Pfad aus `--out`, die genannten Nebendateien aus den `side_files` des Protokolls. Ein Lauf ohne Anhänge kündigt keine `.attachments.json` an — sonst suchte die Instanz nach etwas, das es nicht gibt.

### 3.1.7 Prüfung

- **Wegegleichheit:** `tests/test_wegegleichheit.py` — der Wächter der Vorgabe 2.5. Stellt dieselbe Konversation dem Konverter und dem Maßstab aus 2.5 hin und vergleicht Dokument gegen Dokument, dann die geschriebenen Dateien und die Protokolle; prüft, dass genau die fünf erlaubten Metadatenfelder abweichen und dass nach Entfernen der Referenzfelder zwei identische Transkripte bleiben. 73 Prüfungen.
- Synthetisches ZIP als Prüfstück: Verzweigung, abweichendes `text`, Hülle, null Nachrichten, Dateiverweise, alle Blocktypen — ohne echten Chatinhalt (Vorgabe 2.11).
- `diff` gegen einen Bestand mit bekannter Lücke und einem veralteten Chat.
- Vertippte UUID in einer Zuordnungsdatei wird gemeldet, nicht verschluckt.
- **Integrität:** jede Nachricht landet auf dem gewählten Pfad, in einem Nebenzweig, in der Dublettenzählung — oder, nur bei einem beschädigten Export, in der Warnung über nicht platzierbare Nachrichten (3.1.2). Am Drei-Monats-Export: 7.393 im Export, 7.393 abgelegt oder gezählt, der vierte Ausgang leer. Die Prüfung rechnet ihn ausdrücklich mit, damit die Summe auch für den beschädigten Fall aufgeht statt ihn auszunehmen.
- Lauf gegen ein echtes ZIP: **erledigt**. 211 Chats in gut einer Sekunde, 37 MB — davon 13 MB Gespräch, 9,9 MB Denkschritte, 9,9 MB Anhänge, 4,9 MB Erzeugnisse; 211 Gesprächs-, 145 Denk-, 62 Anhang- und 71 Erzeugnisdateien. Die Verteilung bestätigt die Rechnung aus Vorgabe 2.2 am geschriebenen Ergebnis: Wer nur das Gespräch liest, trägt gut ein Drittel statt des Ganzen. Alle Summen deckungsgleich mit unabhängig gemessenen: 5 Hüllen, 29 Sendewiederholungen, 1.367 verworfene Denkblöcke, 18 Nebenzweige, 341 Anhänge mit Inhalt, 524 reine Namensverweise.
- Lauf gegen ein **Quellprojekt**: das FreeCAD-Projekt mit 22 Chats, aus **zwei** ZIPs verschiedener Zeiträume zu einem Verzeichnis zusammengeführt. Die Stichprobe hat der Nutzer inhaltlich abgenommen — der bislang einzige Beleg, dass ein Mensch das Ergebnis auf Inhalt und nicht nur auf Zahlen geprüft hat.
- **Realdaten-Großlauf (21. August 2026):** vier echte claude.ai-Projekte, 171 Chats, über den Export-Weg geholt. Alle 171 Protokoll-UUIDs gegen die tatsächliche Export-ZIP gehalten — 171 von 171 gefunden, keine Abweichung. Stärkster verfügbarer Beleg für die Wegegleichheit (2.5) und die Integritätsrechnung an echten Daten in dieser Größenordnung.

### 3.1.8 Offen

- **Gehört die Projektzuordnung in die Chatdatei oder nur in den Verzeichnisbaum?** Offene Entwurfsfrage, aus dem Vorhandenen nicht entscheidbar: Sie braucht den Kontext eines echten Ablaufs. Sinnvoll am mehrstufigen Test zu klären, der beide Varianten praktisch vorführt.

## 3.2 `inspect_export.py` — Diagnose eines Export-ZIP

**Status: gebaut, eigener Selbsttest, auch unter `-O`.** Die Scratchpad-Fassung ging beim Sitzungswechsel verloren und wurde aus dem Verlauf rekonstruiert — der Beleg, dass flüchtige Ablagen keine Werkzeuge halten.

Liest ein Kontoexport-ZIP ohne zu entpacken und berichtet Struktur und Zahlen, **nie Chatinhalt** (Vorgabe 2.11 — der Selbsttest weist mit Markertexten nach, dass nichts davon in der Ausgabe erscheint; Titel erscheinen bewusst, sie identifizieren die Chats). Aufruf: `inspect_export.py <export.zip>`.

Beim Verlust zählt es **nicht** jeden `files`-Eintrag: Ein Name, dessen Inhalt als `attachments`-Eintrag derselben Nachricht daneben liegt, ist keiner. Die Verbindung geht über den Namen, den einzigen gemeinsamen Schlüssel — dieselbe Regel wie `file_references()` im Konverter, bewusst zweimal gehalten statt importiert (Vorgabe 2.9).

Prüft: Archivinhalt; **die Projekte nach Erstellungsdatum** — das ist der Zulieferer für `--project-created` (Vorgabe 2.4), und der Grund, warum dafür ein Export beliebigen Zeitraums genügt; Anzahl, Zeitraum und Umfang der Konversationen; ausgehöhlte Konversationen samt der Löschungs-Erklärung aus 3.1.3; Verzweigungen je Chat; Blocktypen und Wahrheitsflaggen; die `text`-Blöcke-Abweichung (das flache Feld trägt die Denkschritte); **`attachments` mit `extracted_content` getrennt von reinen Namensverweisen** — der Prüfpunkt aus 4.2; und als Schemawache die Vereinigung aller Konversations-, Nachrichten- **und Blockschlüssel** zum Vergleich mit 3.1.1.

Es beantwortet eine andere Frage als `analyse` (3.1.6): dieses beschreibt den Rohexport, jenes die Deutung.

## 3.3 Der Skill `chat-export` — das Frontend

**Status: Am echten Lauf erprobt** — über drei unabhängige Sitzungen mit kaum Zutun des Nutzers, zuletzt an vier realen Projekten mit 171 Chats, gegen die tatsächliche Export-ZIP gegengeprüft (Testlauf, Abschnitte „27c", „Großimport", „Nachfüll-Lauf"). Die `README.md` ist geschrieben, reine Anwenderdokumentation ohne Statushinweis und ohne Entwicklungsangaben — bewusst abweichend von `skills/skill_vorgaben.md` 6.1, begründet in Fahrplan 27.

Der Skill ist die Klammer um das Skript: Er führt den Nutzer durch beide Wege, ohne ihm die Entscheidung abzunehmen. Er liegt in `skills/chat-export/` und enthält `chat_export_convert.py`, die Anwenderdokumentation `README.md` sowie die Anweisungsdatei in zwei Sprachfassungen, `SKILL.de.md` und `SKILL.en.md` — am Zielort wird genau eine davon zu `SKILL.md` (Konvention aus `skills/skill_vorgaben.md` 5.1). **Das ist alles, was ein Nutzer kopiert**; die übrigen Skripte dieses Ordners gehören zur Entwicklung und kommen in der Anweisungsdatei nicht vor.

Drei Festlegungen tragen den Entwurf, und alle drei stehen dort normativ:

- **Die Instanz deutet und ordnet zu, das Skript zählt und vergleicht.** Projektnamen mit Tippfehlern auf die echte Liste abbilden oder auf „zeig mir einfach alle" sinnvoll reagieren — das kann eine Instanz besser als jedes Skript. Aufsummieren kann sie nicht verlässlich (1.4). Der Ablauf folgt dieser Trennung durchgehend.
- **Genau zwei Haltepunkte.** Einer vor dem ersten Abruf, der alles Lesende abdeckt; einer nach der Statistik für die Wahl des Wegs. Der Hinweis danach nennt die Zahl der zu ersetzenden Chats und zu entfernenden Dateien, weil das Löschen ist. Zwei Fälle zählen ausdrücklich **nicht** als dritter Haltepunkt, weil sie keine Lese- oder Wegentscheidung sind, sondern eine Vorbedingung: Bündelt das Zielrepo mehrere eigenständige Vorhaben und passt keines zum gewählten claude.ai-Projekt, wird einmal nach dem Zielordner gefragt; und bleibt nach dem Ausfiltern reiner API-Organisationen mehr als eine Chat-Organisation übrig, wird zuerst selbst per `/projects` geprüft, wo die genannten Projekte liegen, bevor gefragt wird (beobachtet am Nachfüll-Lauf vom 21. August 2026).
- **Ausdrücklicher Ton und expliziter Abschluss.** Ein Lauf, der nach dem letzten Schritt kommentarlos verstummt, lässt den Nutzer im Unklaren, ob noch etwas aussteht — beobachtet am Nachfüll-Lauf: ein bloßes „Erledigt." zwang den Nutzer nachzufragen, ob die Instanz fertig sei. Seither verlangt die Anweisungsdatei einen freundlichen Satz je Zwischenschritt und einen ausdrücklichen Schlusssatz nach dem letzten.

**Voraussetzungen, die der Nutzer herstellen muss** und die der Skill nicht umgehen kann: angehängte Browser-Werkzeuge (in der VS-Code-Erweiterung `@browser` je Nachricht), ein laufender und bei claude.ai angemeldeter Chrome mit eingeschalteter Erweiterung, und in Chrome ausgeschaltetes Nachfragen nach dem Speicherort — ein Dateidialog blockiert die Anbindung vollständig. Die Kontobindung ist dabei **keine** Bedingung: Chrome und Claude Code dürfen an verschiedenen Konten hängen (belegt, `chrome-zugriff.de.md`/`chrome-access.en.md`). Was der Skill sieht, ist immer die Sitzung, die im Tab gerade aktiv ist — deshalb **nennt** er das erkannte Konto, statt eines vorauszusetzen.

Das angestrebte Verhalten ist in `SKILL.de.md`/`SKILL.en.md` und der `README.de.md`/`README.en.md` des Skills umgesetzt (Anwenderdokumentation, Bedienung und Hintergrund getrennt). Die Mechanik der Browser-Anbindung samt ihrer Fallstricke steht dauerhaft in `chrome-zugriff.de.md`/`chrome-access.en.md` — nicht befristet, weil sie sich bei jeder künftigen Anthropic-Änderung an der Bridge wieder als Nachschlagewerk eignet.

**Der Anweisungsblock für die `CLAUDE.md` des Zielprojekts bleibt bewusst außerhalb der Skill-README.** Das Durchsuchen eines vorhandenen Archivs ist eine eigene Aufgabe und bekommt einen eigenen Skill; `SKILL.md` und das Skript sehen den Block noch vor, was daraus wird, entscheidet sich mit jenem Skill.

---

# 4 Projektpflege — Anthropic-Entwicklung

Anthropic baut an Export, Werkzeugen und Plattform laufend um; nichts hiervon ist zugesichert, das meiste nur beobachtet (2.1). Dieses Kapitel ist die **Prüfliste**: alles, was regelmäßig zu kontrollieren ist, gesammelt an einem Ort.

**Was hier steht und was nicht.** Kapitel 4 sagt, **was zu prüfen ist und wie**. Die Festlegung selbst hat ihr normatives Zuhause anderswo und wird hier nur so knapp wiedergegeben, dass die Liste für sich lesbar bleibt; bei Widerspruch gilt die verlinkte Stelle, nicht die Wiedergabe. Verfahren, die drei Prüfarten und die Übersicht über alle Punkte stehen in 4.1.

## 4.1 Verfahren und Übersicht

**Ziel:** Ein Satz kleiner Prüfwerkzeuge, mit denen sich vor einem Lauf schnell feststellen lässt, ob **(a)** das Kontoexport-Format, **(b)** die internen Web-Endpunkte und **(c)** `recent_chats` noch den hier dokumentierten Beobachtungen entsprechen — als Frühwarnung, bevor eine Änderung still Falsches produziert. Der Web-Weg ist dabei der empfindlichste: undokumentiert und ohne Ankündigung änderbar.

Vorhandener Baustein ist `inspect_export.py` (3.2) als Schemawache des Exports. **Die Lücke ist die warme Seite:** Für den Export gibt es ein Werkzeug, für die Web-Endpunkte und `recent_chats` nur Proben von Hand. Das bleibt das offene Ziel dieses Abschnitts.

**Das Profil des Testprojekts.** Für die warme Seite gibt es kein Werkzeug, aber eine **Prüfvorlage**: ein eigens angelegtes claude.ai-Projekt, dessen Inhalt bewusst gewählt ist. Zwei Randbedingungen stehen dabei gegeneinander. Es muss **klein** bleiben — ein kleiner Export ist schneller da, und jedes Merkmal muss von Hand erzeugt werden. Und es muss trotzdem **jedes strukturelle Merkmal** tragen, auf das der Code reagiert: Ein fehlendes Merkmal lässt seinen Codeweg ungeprüft, ohne dass es auffällt — der Lauf meldet dann nicht etwa eine Lücke, sondern schlicht nichts.

Das Profil steht hier und nicht bei den erledigten Schritten, weil es sich nicht verbraucht: Nach jeder Anthropic-Änderung, die eine Prüfung aus 4.2 oder 4.3 anschlagen lässt, wird dieselbe Vorlage wieder gebraucht. Es ist eine Prüf**vorlage**, kein Prüf**punkt** — die Übersicht weiter unten führt die Punkte, hier steht das Material, an dem man sie durchspielt.

| Merkmal | Wie es entsteht | Was es prüft |
| --- | --- | --- |
| Gabelung | eine bereits gestellte Frage nachträglich bearbeiten | Baumlauf und Regel 1 (3.1.2) — **erprobt**, erzeugt zuverlässig einen Nebenzweig |
| Anhang mit Inhalt | eine **Textdatei** hochladen (`.py`, `.md`) | `attachments` mit `extracted_content` (3.1.1) — **erprobt** |
| reiner Namensverweis | ein **Bild** hochladen | `files` ohne Inhalt (1.6) — **erprobt**: Bilder werden nicht textextrahiert |
| Denkschritte | eine Aufgabe, die **wirklich** Abwägung erzwingt — mehrere Ansätze unter Nebenbedingungen gegeneinander stellen und die Wahl begründen lassen; dazu eine banale Frage für den kurzen Block | Denkdatei und die Schwellen aus 3.1.3 |
| Erzeugnis | ausdrücklich ein **Artefakt** erstellen lassen und danach ändern | Creations-Datei (3.1.3) |
| Sendewiederholung | **kein bekanntes Rezept** — s. u. | Dublettenerkennung, Regel 2 (3.1.2) |
| ausgetauschter Upload | eine Upload-Nachricht **ohne Begleittext** nachbearbeiten und dabei die Datei wechseln | die andere Hälfte von Regel 2 (3.1.2): dass zwei textlose Geschwister *nicht* als Dublette gelten und beide Anhänge mitkommen |
| Hülle | einen Chat anlegen und wieder löschen | Erkennung gelöschter Chats (3.1.3) |
| langer Chat | einer mit vielen Nachrichten | Baumlauf über eine lange Kette und die Integritätsrechnung (3.1.2, 3.1.7) |
| wachsender Chat | einer, der Tage später fortgesetzt wird | `stale`, Ersetzen (2.6) und die Fensterrechnung (2.4) |

Die Zeile zum wachsenden Chat ist die einzige mit Vorlaufzeit: Der Zeitraumfilter des Exports arbeitet auf Tagesebene, also muss zwischen Anlegen und Fortsetzen mindestens ein Tageswechsel liegen.

**Die Rezepte für Denkschritte und Erzeugnis sind bereits einmal fehlgeschlagen** — zu leichte Fragen, und ein Chat über Bildgenerierung, der keinen der drei Werkzeugnamen aus 3.1.3 erzeugt. Beide Lehren stehen oben in der Tabelle; deshalb ist sie dort so ausführlich formuliert.

**Für die Sendewiederholung gibt es kein Rezept.** Zwei identisch abgeschickte Nachrichten stehen als Eltern und Kind hintereinander, der Code sucht aber **Geschwister ohne Nachfahren** an einer Gabelung. Belegt ist das Phänomen nur aus echten Daten (14 Kinder mit je 440 Zeichen, 3.1.2); herstellen konnten wir es nicht. Dieser Codeweg bleibt damit ungeprüft — ausdrücklich vermerkt statt stillschweigend als abgedeckt geführt. Betroffen ist allerdings nur die Hälfte, die *verwirft*: Dass zwei textlose Geschwister eben **keine** Dublette sind, lässt sich mit dem Rezept eine Zeile darunter sehr wohl live erzeugen, weil dafür nur eine Gabelung nötig ist — und die ist erprobt.

**Drei Prüfarten.** Jeder Punkt trägt genau eine:

- **kalt** — prüfbar mit dem, was auf der Platte liegt: die heruntergeladenen Export-ZIPs unter `tests/test_results/` und ein Arbeitsordner. Kein Netz, kein Konto, kein fremder Zustand; beliebig oft wiederholbar. Eine Einschränkung, die leicht übersehen wird: Das Prüfmaterial ist **rechnergebunden**, weil `test_results/` gitignoriert ist und nicht mitwandert — dieselbe kalte Prüfung ist auf dem einen Rechner lauffähig und auf dem anderen nicht.
- **warm** — nur mit Zugriff auf ein echtes Konto: ein angemeldeter Browser für die Web-Endpunkte (der Regelfall, Voraussetzungen in `chrome-zugriff.de.md`), ein claude.ai-Projekt für `recent_chats`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.
- **Beobachtung** — nicht prüfbar, nur bemerkbar, wenn es kippt: Die Sache ist undokumentiert und durch keinen Versuch auslösbar. Sie „warm" zu nennen verspräche eine Prüfung, die es nicht gibt.

Ein warmer Punkt kann **mangels Rechten unerreichbar** sein, ohne deshalb eine Beobachtung zu werden: Er wäre prüfbar, nur nicht von uns. Das wird dazugeschrieben statt stillschweigend umgewidmet — sonst sieht ein späterer Leser eine Prüfung, die nie jemand vorhatte durchzuführen.

**Was eine Prüfung ist.** Drei Teile: was man tut, woran man erkennt, dass die dokumentierte Aussage noch stimmt, und was folgt, wenn nicht. Der letzte Teil ist immer derselbe — betroffene Zeile in 1.6 bzw. Kapitel 3 korrigieren und prüfen, was daran hing. Ein Punkt ohne erkennbares Kriterium ist keine Prüfung, sondern eine Beobachtung.

**Übersicht.** Alle Punkte mit ihrem normativen Zuhause und ihrer Art — bewusst nur Zeiger, damit diese Tabelle nicht neben den Abschnitten herdriften kann:

| Prüfpunkt | Zuhause | Art |
| --- | --- | --- |
| Verfügbarkeit des Exports je Kontotyp | 4.2, 1.6 | warm |
| Aufbau des Organisationsexports (Primary Owner) | 4.2 | warm, mangels Rechten unerreichbar |
| Zeitraumauswahl des Exports | 4.2 | warm beim Anfordern, danach kalt |
| Zeitraumgrenze wirkt auf `created_at`, nicht `updated_at` | 4.2 | kalt |
| Projektdateien vom Zeitraumfilter ausgenommen | 4.2 | kalt |
| Archivmitglieder und Schlüsselmengen | 4.2, 3.1.1 | kalt |
| `attachments` mit Inhalt gegen `files` ohne | 4.2, 3.1.1 | kalt |
| Hüllen gelöschter Chats | 4.2, 3.1.3 | kalt |
| Bekommt eine Konversation je einen Projektbezug? | 4.2, 1.6 | kalt |
| Stückelung großer Exporte (`batch-0000`) | 4.2 | Beobachtung |
| Web-Endpunkte: Pfade, Felder, Paginierung | 4.3, 1.2 | warm |
| Bleibt der Browser-Zugriff ohne Captcha-Prüfung möglich? | 4.3 | warm |
| Chatliste über `recent_chats` | 4.3 | warm |
| Übergeht `recent_chats` weiterhin den laufenden Chat? | 4.3, 1.6 | warm |
| Gibt es für `files` einen Abrufweg? | 4.3, 1.6 | warm |
| RAG-Schwelle des Projektwissens | 4.4 | Beobachtung |
| Container-Allowlist ohne `claude.ai` | 4.4 | warm |
| Räumt die Aufräumung fremde Dateien in `~/.claude/projects/` mit weg? | 4.4, 1.3 | kalt |
| Was nimmt `claude project purge` mit? | 4.4, 1.3 | kalt, destruktiv |
| Cowork über beide Wege unerreichbar | 4.4, 1.6 | Beobachtung |

## 4.2 Kontoexport — was verwendet wird und zu prüfen ist

- **Wer überhaupt exportieren darf, hängt am Kontotyp** (1.6): Selbstbedienung nur auf Free, Pro und Max; in Team und Enterprise allein der Primary Owner, unter *Organization settings → Data and privacy*. Fällt das weg oder ändert es sich, ändert sich, für wen der Hauptweg überhaupt existiert. *Prüfung: in den Einstellungen des jeweiligen Kontos nachsehen — warm.*
- **Der Organisationsexport des Primary Owner ist ungeprüft.** Ob sein ZIP denselben Aufbau trägt wie das persönliche — Mitgliederliste, `conversations.json`, Projektdateien mit `created_at` —, ist unbelegt, und der ganze Konverter hängt daran. *Prüfung: `inspect_export.py` über ein solches Archiv laufen lassen — warm, uns mangels Owner-Rechten derzeit nicht möglich. Der Rechteerwerb dafür wäre kein Prüfaufwand, sondern ein Eingriff in die Organisation, und für den laufenden Betrieb hilft er ohnehin nicht (1.2).*
- **Kein Deep-Link zur Antragsseite** (1.6): eine direkte Navigation auf die Einstellungs-URL rendert nur die gewöhnliche Chat-Oberfläche, nicht den Dialog. Der Skill muss über die Oberfläche gehen — Konto-/Einstellungsmenü, „Datenschutz", „Daten exportieren". *Prüfung: den Deep-Link erneut versuchen — ändert sich das Routing, wird der Skill einfacher, nicht komplizierter. Warm.*
- Anforderung unter **Settings → Privacy → Export data**, Lieferung als Link per E-Mail, Link verfällt nach 24 h (belegt). **Die Zeitraumauswahl ist nirgends dokumentiert** — sie ist beobachtet und praktisch wichtig, denn auf ihr beruht das Nachpflegen (1.5). Fällt sie weg, wird jeder Lauf zum Vollexport. Zwei Läufe mit verschiedenen Grenzen haben sie inzwischen bestätigt: `created` vom 1.5. bis 6.8.2026 (211 Konversationen) und vom 1.11. bis 1.12.2025 (78). Die Grenze wirkt auf `created_at`, nicht auf `updated_at` — ein alter Chat, der letzte Woche weiterlief, ist im Kurzzeitraum also **nicht** enthalten. Wer über diesen Weg nachpflegt, muss den Zeitraum daher weit genug zurück legen, um weitergelaufene Altchats mitzunehmen; genau dafür rechnet das Werkzeug die Fenstergrenze aus (Vorgabe 2.4). Der Web-Weg holt einen einzelnen gewachsenen Chat dagegen gezielt per UUID (1.2). *Prüfung: beim nächsten Antrag sehen, ob die Auswahl noch angeboten wird — warm; die tatsächlich gelieferte Spanne danach am ZIP gegenprüfen — kalt.*
- Dateiname `data-<uuid>-…-batch-0000.zip`; die batch-Zahl war bisher immer 0 — möglicherweise stückeln größere Exporte, nie beobachtet. *Beobachtung: durch keinen Versuch auslösbar, bemerkbar erst an einem hinreichend großen Export.*
- **Projektdateien sind vom Zeitraumfilter ausgenommen** (3.1.1) — beobachtet an zwei Exporten mit verschiedenen Zeiträumen, beide mit denselben 43 Projektdateien. Darauf beruht, dass ein Export beliebigen Zeitraums den Projektbeginn hergibt — der Rückfallweg für Konten ohne Browser-Anbindung (1.5); fällt es weg, muss der Projektbeginn dort anders beschafft werden. *Prüfung: die beiden vorliegenden ZIPs mit verschiedenen Zeiträumen gegeneinander halten — dieselbe Projektliste heißt, es gilt noch. Kalt.*
- Archivaufbau: `users.json`, `projects/<uuid>.json`, `memories.json`, `conversations.json`, dazu wechselnd `login_history.json` (3.1.1). Projektdateien enthalten **keine** Chats. **Die Mitgliederliste wächst:** `login_history.json` kam zwischen zwei Exporten im Abstand von zwei Tagen hinzu — ein neues Mitglied ist deshalb allein kein Alarm, ein fehlendes `conversations.json` schon. *Prüfung: `inspect_export.py` laufen lassen und Mitglieder- wie Schlüsselmengen mit 3.1.1 vergleichen — kalt.*
- Konversation: genau sieben Felder, **kein Projektbezug** — die Chatliste aus dem Projekt ist die einzige Zuordnungsquelle (1.6). *Prüfung: käme je ein Projektfeld hinzu, entfiele der ganze Umweg über die Chatliste — am nächsten ZIP ablesbar, kalt.*
- Nachricht: `parent_message_uuid` macht die Nachrichten zum **Baum** (3.1.2); `sender` `human`/`assistant`; das flache `text` enthält die Denkschritte (3.1.1); `content`-Blocktypen `text`, `thinking`, `tool_use`, `tool_result`, `token_budget`. *Prüfung: Nachrichten- und Blocktypmengen aus `inspect_export.py` gegen 3.1.1 — ein neuer Blocktyp fiele dort sofort auf. Kalt.*
- **`attachments` tragen `extracted_content`, `files` nur Namen — und beide oft dieselbe Datei** (3.1.1, 1.6). Die Unterscheidung entscheidet, was das Archiv behalten kann; die Überschneidung entscheidet, wie viel Verlust überhaupt zu melden ist. *Prüfung: `inspect_export.py` gibt drei Zahlen getrennt aus — `files` mit Inhaltspartner in derselben Nachricht samt Anteil, `files` ohne Partner, und `attachments` ohne extrahierten Inhalt. Die erste Zahl ist kein Verlust; wer alle zusammenzählt, überzeichnet ihn um mehr als das Doppelte. Kalt. Ob es für die übrigen einen Abrufweg gibt, ist eigener Punkt in 4.3.*
- Gelöschte Chats erscheinen als Hüllen: Gerüst da, Inhalt leer (3.1.3). *Prüfung: `inspect_export.py` weist sie aus — kalt.*
- **Denkschritte können enthalten sein oder fehlen** (3.1.1); der Anteil leerer `thinking_hidden`-Blöcke schwankt bis hin zu „alle". *Prüfung: den Anteil in jedem vorliegenden Archiv auszählen — kalt. Ein Nullbefund ist dabei kein Formatbefund, sondern eine Stichprobe; nicht daraus schließen, der Export führe keine Denkschritte mehr.*
- Erste Anlaufstelle bei Verdacht: `inspect_export.py` (3.2) laufen lassen und die Schlüsselmengen mit 3.1.1 vergleichen.

## 4.3 Werkzeuge der Claude-Instanz — was verwendet wird und zu prüfen ist

- **Die internen Web-Endpunkte** (1.2) sind die empfindlichste Stelle des ganzen Entwurfs: undokumentiert, von Dritten rückentwickelt, ohne Ankündigung änderbar. Gebraucht werden `/api/organizations` (Konto und Organisations-UUID ohne Vorwissen), `…/projects` (Projekte mit `created_at`), `…/projects/<p>/conversations_v2` (Chatliste mit `pagination`) und `…/chat_conversations/<c>?tree=True&rendering_mode=messages&render_all_tools=true` (vollständiger Baum, keine Paginierung). *Prüfung: die vier Pfade aus einem angemeldeten Tab aufrufen und Feldnamen sowie Antwortgröße gegen 1.2 halten — warm. Fällt einer weg, trägt nur noch der Kontoexport, und in Team-Konten gar nichts mehr.*
- **`/api/organizations` liefert mehr als eine Organisation liefern kann, ohne dass das ein Fehler ist** (1.6): eine reine API-/Console-Organisation ohne `"chat"` in `capabilities` gehört ausgefiltert, nicht nachgefragt. Bleibt danach mehr als eine Organisation mit Chat-Fähigkeit übrig, ist ein Blick in deren `/projects` billiger als eine Rückfrage. *Prüfung: das Feld `capabilities` ist weiterhin vorhanden und trägt weiterhin `"chat"` bei einer Chat-Organisation — kalt, am nächsten Aufruf ablesbar.*
- **Captcha- und Cloudflare-Prüfungen** sind der zweite Grund, warum der Web-Weg gebremst ist. Bisher trat keine auf; die Anbindung würde anhalten und fragen. *Prüfung: nicht auslösbar ohne genau das zu provozieren, was vermieden werden soll — bemerkbar allein am Anhalten während eines Laufs. Warm.*
- `recent_chats(n≤20, sort_order, before, after)` — Zeit-Cursor, liefert die Chatliste; einzige Quelle der Projektzugehörigkeit; **listet den laufenden Chat nicht mit** (1.6). *Prüfung: Liste in einem Projekt abrufen und die Form des Rohblocks gegen das halten, was `MAPPING_PROMPT` verlangt (3.1.6) — warm. Die Auslassung des laufenden Chats gegenprüfen, indem dieselbe Liste aus zwei verschiedenen Chats geholt wird: Fällt sie weg, kann der Abfragechat wieder ein beliebiger sein und die Regel aus 1.5 entfällt — warm.*
- **Gibt es für `files` einen Abrufweg?** Der Export trägt zu ihnen nur `file_uuid` und `file_name`, ihr Inhalt fehlt (1.6). *Prüfung: Werkzeugbeschreibungen und Doku sichten, dann in einer Instanz einen Abruf versuchen — warm.*

## 4.4 Plattformverhalten claude.ai — was den Entwurf trägt

- Kontextfenster 1 Mio Token (Opus 5/Sonnet 5, bezahlte Pläne, belegt); lange Chats werden **zusammengefasst statt abgebrochen**, und die Instanz erhält kein Kontextsignal (Opus ohne Budget-Tags). Darauf beruht mit, dass kein Weg dieses Vorhabens Chattext durch einen Kontext führt (1.2, Vorgabe 2.8).
- Projektwissen: Textextraktion; RAG schaltet ab undokumentierter Schwelle automatisch (Community: Dateianzahl); Projektdateien im Container *„while remaining in context"* — Containerzugriff spart keinen Kontext (1.6). *Beobachtung: die Schwelle ist undokumentiert und nicht steuerbar; bemerkbar allein daran, dass eine Instanz zu suchen beginnt, statt zu lesen.*
- Chat-Upload: 20 Dateien je Chat, JSON belegt zulässig — trägt die Übergabe der Protokolldatei (1.4/1.5).
- Container-Netzzugang nur gegen Allowlist, `claude.ai` steht nicht darauf — ein Skript im Container kann den Export-Link nicht laden (1.7). *Prüfung: einen Abruf aus dem Container versuchen — warm.*
- Claude-Code-Seite: `~/.claude/projects/…` wird nach `cleanupPeriodDays` aufgeräumt — Standard 30 Tage, Minimum 1, `0` ist ein Validierungsfehler, eine Obergrenze ist nicht dokumentiert (belegt). Namentlich betroffen sind `<sitzung>.jsonl` sowie `subagents/` und `tool-results/` je Sitzung; **ob fremde Dateien in diesem Ordner mit weggeräumt werden, sagt die Dokumentation nicht** — offener Prüfpunkt. Zweiter Löschweg: `claude project purge` entfernt *„Transcripts and auto memory under `projects/`"* für ein Projekt, unabhängig von der Frist. Beides trägt die Bedingungen des dritten Zielorts (1.3, Vorgabe 2.10). *Prüfung: eine fremde Datei mit zurückdatiertem Zeitstempel dort ablegen und einen Start abwarten — kalt. `claude project purge` nur mit `--dry-run` oder in einer Wegwerf-Umgebung — kalt, aber destruktiv.*
- Cowork: eigene ID-Welt, über beide Wege unerreichbar (1.6) — Anthropic könnte hier den Umzugsweg schaffen, der dieses Werkzeug ablöst. *Beobachtung: nicht auslösbar, nur zu bemerken.*
