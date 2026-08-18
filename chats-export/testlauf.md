# Testlauf — Protokoll des warmen Tests

Das laufende Protokoll zu Fahrplanpunkt 21: was angelegt wurde, was beobachtet wurde, was noch fehlt. Es steht hier und nicht im Fahrplan, weil der eine reine Aufgabenliste ist, und nicht in der Doku, weil eine laufende Beobachtung noch keine Festlegung ist.

**Diese Datei ist befristet.** Sie endet mit Punkt 21. Was von ihr bleibt, wandert dann dorthin, wo es normativ hingehört: der bestandene Lauf nach `implementation_doku.md` 3.1.7 bzw. 3.2 — dort steht schon der FreeCAD-Lauf —, gekippte Annahmen nach 1.7, geänderte Umgebungstatsachen nach Kapitel 4. Danach wird sie gelöscht.

## Das Testprojekt

| | |
| --- | --- |
| Titel | „Chats-Export, Test 1" |
| Kurzbeschreibung | „Das ist ein Testprojekt, angelegt zum Fahrplanpunkt 21.2" |
| Angelegt | 17. August 2026, gegen 15:20 Uhr |
| Angelegt mit | Claude Desktop, als gewöhnliches Projekt (nicht als Claude-Code-Projekt) |

Das Anlegedatum ist der **Sollwert** für 21.4: Der Sondierungsexport muss für dieses Projekt genau den 17. August 2026 als `created_at` führen. Die Uhrzeit ist dabei nur die Notiz, dass es kein Tageswechsel-Grenzfall war.

**Stand am 17. August 2026:** angelegt, sonst leer — keine Projektanweisung, kein Projektwissen, keine geplanten Aufgaben, kein Chat.

**Bestätigt:** Das Projekt ist in claude.ai im Browser sichtbar. Ein in Claude Desktop angelegtes gewöhnliches Projekt liegt also im Konto, nicht nur lokal.

**Offen und vor dem Füllen zu klären:** ob es für `recent_chats` und `read_conversation` auch **erreichbar** ist. Sichtbarkeit und Erreichbarkeit sind zweierlei; entschieden wird es durch die Chatliste (Doku 1.6 zur Bereichsbindung).

**Beobachtet, bisher nirgends dokumentiert:** Beim Anlegen eines Projekts gibt es **keine** Wahl zwischen Cowork und Nicht-Cowork. Die Unterscheidung fällt erst beim Starten des ersten Chats — dort stehen „Chat" und „Cowork" zur Wahl. Cowork gehört also nicht zum Projekt, sondern zum einzelnen Chat. Für diesen Testlauf werden **alle** Chats als gewöhnlicher Chat angelegt: Cowork-Chats sind über beide Wege unerreichbar, ihre IDs sind keine UUIDs und werden am Format abgewiesen (Doku 1.6, 4.3).

**Daraus eine offene Frage**, die dieser Testlauf beantworten könnte: Erscheint ein Cowork-Chat, der in einem gewöhnlichen claude.ai-Projekt geführt wird, trotzdem in dessen `recent_chats`-Liste? Wenn ja, legte `list` einen Protokolleintrag an, der nie zu holen ist — ein Chat, der dauerhaft als fehlend geführt wird. Wenn nein, fehlt er lautlos. Beides wäre wissenswert, keines ist bisher belegt.

## Das Testprojekt im Pro-Konto

| | |
| --- | --- |
| Titel | „Chats-Export aus Pro, Test 1" |
| „Was Sie erreichen wollen" | „Das ist ein Testprojekt im Pro-Konto." |
| Angelegt | 17. August 2026 |
| Konto | Pro — hier liegt die echte Quellumgebung, und nur hier gibt es den Export |

Dieses Projekt trägt den mehrstufigen Test. Der Sollwert für 21.4 ist der **17. August 2026**; die Uhrzeit spielt keine Rolle, weil der Export nur ein Datum führt.

Die Wahl zwischen „Chat" und „Cowork" beim Anlegen eines Chats erscheint auch hier — sie ist also keine Team-Eigenheit, sondern die Normalform auf allen bezahlten Plänen (belegt, [13455879](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans)). **Jeder Chat dieses Testprojekts wird als „Chat" angelegt**, nie als Cowork.

## Profil-Checkliste (Doku 4.1)

Alle Merkmale sind am 17. August 2026 **erzeugt worden**. Erzeugt heißt hier: Die Handlung ist getan — ob daraus in den Daten wirklich das Merkmal geworden ist, weist erst der Export in 21.7 nach. Bei zwei Merkmalen ist der Ausgang ausdrücklich offen:

| Merkmal | Chat | Stand |
| --- | --- | --- |
| Gabelung | 1 | erzeugt |
| Sendewiederholung | 1 | erzeugt |
| Anhang mit Inhalt | 2 | erzeugt |
| reiner Namensverweis | 2 | **offen im Ausgang** — ob ein Bild als `attachments` mit Inhalt oder als `files` ohne ankommt, ist unbekannt; genau das soll der Lauf klären |
| Denkschritte | 3 | erzeugt, dazu bewusst ein kurzer Block für die 200-Zeichen-Schwelle (3.1.3) |
| Erzeugnis | 4 | erzeugt, mit anschließender Änderung für die `delta`-Kennzeichnung |
| Hülle | 5 | **offen im Ausgang** — vor dem Export gelöscht; ob der Chat als Hülle erscheint oder gar nicht, entscheidet den Widerspruch aus 1.6 gegen [13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data) |
| langer Chat | 6 | erzeugt |
| wachsender Chat | 6 | derselbe Chat; fortgesetzt wird er in 21.9 nach einem Tageswechsel |

**Beobachtung zur Gabelung:** Nach dem Bearbeiten der Frage kam eine neue Antwort, und die bisherige verschwand **im Web-Frontend**. Genau darum geht es bei Regel 2 in 3.1.2: Die Oberfläche zeigt den verworfenen Zweig nicht mehr, der Export soll ihn trotzdem führen. Damit hat 21.7 eine scharfe Erwartung — `analyse` muss für Chat 1 einen Nebenzweig ausweisen. Tut es das nicht, ist entweder die Gabelung anders entstanden als gedacht, oder der Export hält den verworfenen Zweig nicht.

**Langer und wachsender Chat sind derselbe** (Chat 6). Das ist zulässig und spart einen Chat: Ein wachsender Chat, der zugleich lang ist, macht das Ersetzen beim zweiten Export sogar aussagekräftiger. Eine Bedingung gehört dazu — für den Wegegleichheits-Vergleich in 21.13 darf **nicht** dieser Chat genommen werden. Dort müssen beide Wege denselben Stand sehen; ein wachsender Chat wäre ein bewegtes Ziel, und eine Abweichung ließe sich nicht mehr von einem echten Befund unterscheiden.

**Für 21.13 vorgesehen**, und ab jetzt unangetastet: Chat 3 oder 4 als schlichter Grundfall — und **Chat 1 als Härtefall**. Er trägt Gabelung und Sendewiederholung, und beide sieht der Lese-Weg nicht: Er liefert das gerenderte Transkript. Kommen nach Abzug der erlaubten Felder trotzdem zwei identische Transkripte heraus, ist Vorgabe 2.5 an der schwierigsten Stelle bestätigt. Weichen sie ab, haben wir einen Fall gefunden, den die Vorgabe bisher nicht kennt — und das wäre kein Testfehler, sondern der wertvollste Befund des ganzen Laufs.

## 21.3/21.4 Sondierungsexport — bestanden

ZIP vom 17. August 2026, Fenster vor dem Anlegen des Testprojekts. `inspect_export.py` berichtet:

- **Konversationen: 1**, erstellt am 2026-08-15 — aus einem anderen Projekt. **Kein einziger Chat des Testprojekts** ist enthalten; das Fenster schloss sie korrekt aus.
- **44 Projektdateien**, darunter „Chats-Export aus Pro, Test 1" mit `created_at` **2026-08-17** — also mit einem Datum **außerhalb und nach** dem gewählten Fenster.

**Damit ist die Behauptung geprüft, auf der Schritt 0 aus 1.5 ruht:** Projektdateien sind vom Zeitraumfilter ausgenommen. Und zwar gegen einen bekannten Sollwert — der Nutzer hatte das Anlegedatum unabhängig notiert, das Werkzeug liest genau dieses Datum aus einem Archiv, das den Chat des Projekts gar nicht kennt. Vorher waren es 43 Projektdateien, jetzt 44; die eine mehr ist unser Testprojekt.

**Schemawache:** Konversationsschlüssel und Nachrichtenschlüssel decken sich mit 3.1.1, und `project reference: NONE` bestätigt erneut den Befund, der den ganzen Entwurf trägt. `login_history.json` ist vorhanden.

**Eine Lücke in der Vergleichsgrundlage:** Die Schemawache gibt auch die **Blockschlüssel** aus — hier `citations`, `flags`, `start_timestamp`, `stop_timestamp`, `text`, `type`. Doku 3.1.1 führt nur die Block*typen*, nicht die Block*schlüssel*; 3.3 verspricht aber den Vergleich aller drei Schlüsselmengen mit 3.1.1. Für eine der drei fehlt also die Vergleichsgrundlage. Sie lässt sich aus dem Erstlauf-ZIP (21.7) gewinnen, das alle Blocktypen enthält, und gehört dann nach 3.1.1.

## 21.5 Chatliste — bestanden

Im Testprojekt des Pro-Kontos, aus einem frisch angelegten und danach gelöschten Chat. Die Rohausgabe liegt als `tests/test_results/chatliste-pro-test-1_2026-08-17.txt`.

**Fünf Einträge — genau die erwartete Zahl:** sechs angelegte Chats minus den vor dem Export gelöschten Hüllen-Chat. `parse_chat_list` erkennt alle fünf mit UUID, `updated_at` und Titel.

Die Rohausgabe steht hier mit im Dokument, damit der Lauf ohne Handübertragung auf einem anderen Rechner wiederholbar ist — `test_results/` ist gitignoriert und wandert nicht mit. Das ist für **dieses Wegwerf-Testprojekt** unbedenklich: UUIDs, Zeitstempel und Titel, kein Gesprächsinhalt. Für ein echtes Quellprojekt gehörte eine Chatliste **nicht** ins Repo — sie verriete sämtliche Chattitel.

```text
<chat url='https://claude.ai/chat/21670321-898e-413e-a6fd-9091a6bf90f8' updated_at='2026-08-17T14:30:35.984103+00:00'>
Title: Brillenstärken verstehen
</chat>

<chat url='https://claude.ai/chat/1d322d54-0229-41b8-b336-3eb7d5573d13' updated_at='2026-08-17T14:35:58.247417+00:00'>
Title: Erklärung eines Vorgangs
</chat>

<chat url='https://claude.ai/chat/5f8ac1bd-93cf-495d-813c-96527ffdc4a8' updated_at='2026-08-17T14:47:20.774795+00:00'>
Title: Wanderung planen
</chat>

<chat url='https://claude.ai/chat/490dbac1-6ecd-45ef-94fc-d28ecb154a40' updated_at='2026-08-17T14:53:20.739094+00:00'>
Title: Bildgenerierung und Grafikformate
</chat>

<chat url='https://claude.ai/chat/50bd7f40-43f2-45d7-b771-4002eaa96bdd' updated_at='2026-08-17T15:05:14.159994+00:00'>
Title: API-Funktionen und Zeitlesen im Chat
</chat>
```

**Befund, neu:** Ein **gelöschter** Chat erscheint nicht mehr in `recent_chats`. Im Export tauchen gelöschte Chats als Hüllen auf (3.1.3) — in der Liste gar nicht. Wer also nur die Liste kennt, erfährt von ihnen nichts; wer nur den Export kennt, sieht sie als leere Gerüste. Was der Erstlauf-Export mit diesem Chat macht, ist die offene Hälfte des Befunds (21.7).

**Befund, bestätigt:** Auch der Abfragechat selbst fehlt wieder — er wurde ohnehin gelöscht, die Regel aus 1.5 hat sich also gleich beim ersten echten Einsatz bewährt.

## 21.6 Protokoll anlegen — bestanden

Zwei Läufe, absichtlich getrennt:

**Ohne `--project-created`** meldet `list`: *„5 pending chat(s) have no date bound at all — give the project's start date with --project-created … or export everything."* Es rät nicht, sondern fordert an — genau das, was Vorgabe 2.4 mit `unbounded` als eigenem Ergebnis verlangt.

**Mit `--project-created 2026-08-17`**, dem Datum aus dem Sondierungsexport: *„An export has to reach back to 2026-08-17 to cover everything pending (from project)."* Das ist der erwartete Wert, aus der erwarteten Quelle. Die Kette Sondierung → Projektdatum → Fenstergrenze trägt.

**Nebenbei an echten Daten bestätigt:** `diff` nennt dieselbe Fenstergrenze, ohne dass eine frische Liste geholt wurde — die Änderung aus Fahrplanpunkt 14, hier zum ersten Mal im Echtbetrieb.

## Zuordnung der Chats und die Erwartung für 21.7

Vom Nutzer benannt. Damit steht vor dem Export fest, was der Lauf zeigen **muss** — das ist der Unterschied zwischen einer Prüfung und einer Beobachtung.

| Chat | UUID | Merkmal | Erwartung im Export |
| --- | --- | --- | --- |
| Brillenstärken verstehen | `21670321` | Gabelung, Sendewiederholung | mindestens ein Nebenzweig **und** mindestens eine übersprungene Sendewiederholung |
| Erklärung eines Vorgangs | `1d322d54` | Anhänge — eine Python-Datei (`test_docstrings.py`) **und** ein Bild | die Python-Datei als `attachments` **mit** `extracted_content`; das Bild offen — vermutlich `files` als reiner Namensverweis. Beide Anhangsarten in einem Chat, also beide Codewege in einem Lauf |
| Wanderung planen | `5f8ac1bd` | Denkschritte | behaltene Denkblöcke **und** mindestens ein verworfener (unter 200 Zeichen) |
| Bildgenerierung und Grafikformate | `490dbac1` | Erzeugnis | mindestens zwei Werke, davon eines als `delta` gekennzeichnet |
| API-Funktionen und Zeitlesen im Chat | `50bd7f40` | langer und wachsender Chat | deutlich über acht Turns; in 21.9 wächst er weiter |
| *(gelöscht)* | — | Hülle | offen: Hülle im Export oder gar nicht enthalten |

**Zwischenzeitlich als Profillücke vermutet, dann ausgeräumt:** Chat 2 schien nur ein Bild zu tragen, womit `attachments_with_content` im ganzen Lauf null geblieben und der Codeweg für 9,6 Mio Zeichen des echten Exports unberührt geblieben wäre. Das Nachsehen ergab: Am ersten Prompt hängt eine Python-Datei. Beide Anhangsarten sind also gedeckt — und der Chat wird damit zum schärfsten Prüfstück für die Unterscheidung `attachments` gegen `files`, weil beide Fälle in derselben Konversation liegen.

## 21.7 Erstlauf-Export — teils bestanden, mit drei Befunden

Export vom 17. August, Fenster ab 2026-08-17, 7 Konversationen. `convert` schrieb 5 Chatdateien und **eine** Nebendatei.

### Gegen die Erwartungstabelle

| Erwartung | Ergebnis |
| --- | --- |
| Gabelung in „Brillenstärken" | **bestanden** — 1 Nebenzweig mit 2 Nachrichten. Die Oberfläche hatte die verworfene Antwort ausgeblendet, der Export führt sie |
| Sendewiederholung in „Brillenstärken" | **nicht eingetreten** — 0 übersprungene Wiederholungen |
| Anhang mit Inhalt in „Erklärung eines Vorgangs" | **bestanden** — `test_docstrings.py`, 4.481 Zeichen `extracted_content` |
| Bild als reiner Namensverweis | **bestanden** — `Teensy4.1-oben.png` kommt nur als Name |
| behaltene Denkblöcke in „Wanderung planen" | **nicht eingetreten** — 14 Blöcke im ganzen Export, **alle** verworfen, keiner behalten |
| Erzeugnis in „Bildgenerierung" | **nicht eingetreten** — 0 Werke, obwohl 27 `tool_use`-Blöcke vorliegen |
| langer Chat | **bestanden** — 28 Nachrichten |
| Hülle | **bestanden**, s. u. |

### Die drei Fehlschläge liegen an den Rezepten, nicht am Code

**Sendewiederholung.** Zwei identisch abgeschickte Nachrichten stehen als Eltern und Kind hintereinander, nicht als Geschwister an einer Gabelung — der Code sucht aber Geschwister (3.1.2, Regel 2). Das Rezept „dieselbe Nachricht zweimal absenden" erzeugt das Phänomen also gar nicht. Was die 14 gleichlangen Kinder im echten Export erzeugt hat, ist damit weiterhin unbekannt und offenbar nicht auf Zuruf herstellbar.

**Denkschritte.** 14 Blöcke, keiner versteckt, **alle unter 200 Zeichen** — verteilt auf „Wanderung planen" (10), „Bildgenerierung" (3) und „API-Funktionen" (1). Die Schwelle aus 3.1.3 stammt aus einem Bestand mit Medianlänge 682; die Testfragen waren dafür zu leicht. Das Rezept muss eine Aufgabe verlangen, die wirklich Abwägung erzwingt.

**Erzeugnis.** 27 `tool_use`-Blöcke, aber keiner davon `artifacts`, `create_file` oder `str_replace` — der Chat drehte sich um Bildgenerierung, nicht um ein Artefakt. Das Rezept muss ausdrücklich ein **Artefakt** verlangen.

Alle drei sind damit Korrekturen am Profil in Doku 4.1 — und genau dafür war der Lauf da.

### Befund 1: Gelöschte Chats erscheinen als Hüllen, der Widerspruch löst sich auf

Der Export enthält **zwei** Hüllen: den absichtlich gelöschten Chat 5 (8 Nachrichten) und den Abfragechat der Chatliste (2 Nachrichten). Beide wurden vor der Anforderung des Exports gelöscht, beide sind enthalten — mit Gerüst, ohne Text.

Damit ist der vermeintliche Widerspruch aufgelöst: Anthropic schreibt, gelöschte **Inhalte** kämen nicht in später angeforderte Exporte — und genau so ist es. Der Inhalt fehlt (0 Zeichen), das **Gerüst** bleibt. Beide Aussagen stimmen, richtig gelesen; unsere Doku sollte das so sagen.

Nebenbei: Beide Hüllen stehen **nicht** im Protokoll, weil sie in der Chatliste fehlten — `convert` hat sie folgerichtig übergangen. Ein gelöschter Chat ist über die Liste nicht mehr einem Projekt zuzuordnen.

### Befund 2: `files` und `attachments` sind nicht disjunkt

Am Rohmaterial nachgeprüft: Dieselbe Nachricht führt `test_docstrings.py` **zweimal** — einmal unter `attachments` mit `extracted_content` (4.481 Zeichen) und einmal unter `files` mit `file_uuid` und Namen. Das Bild dagegen steht **nur** unter `files`.

Doku 1.6 sagt über die 524 `files`-Einträge des Drei-Monats-Exports: „und **die** sind wirklich verloren." Das ist so nicht haltbar — ein unbekannter Teil davon sind Zweitnennungen von Dateien, deren Inhalt sehr wohl mitkam.

### Befund 3: Daraus ein Defekt im Code

`file_names()` nimmt jeden `files`-Eintrag als Verlust, ohne zu prüfen, ob dieselbe Nachricht die Datei bereits mit Inhalt führt. Folge: `report` meldet `test_docstrings.py` als „mentioned by name only", obwohl der Inhalt in der Anhangsdatei liegt, und das Metadatenfeld `attachments_without_content` überzeichnet den Verlust. Zu beheben, mit Auswirkung auf 1.6 und die dortigen Zahlen.

### Die Blockschlüssel liegen jetzt vor

Der Export trägt alle Blocktypen außer `token_budget` (erwartbar, 1.6). Die Schlüsselmenge umfasst 37 Namen, darunter viele, die 3.1.1 nicht kennt — `structured_content`, `display_content`, `tool_origin`, `is_mcp_app`, `mcp_server_url`, `approval_options` und weitere. Damit ist die Vergleichsgrundlage vorhanden, die 3.3 verspricht und 3.1.1 bisher schuldig blieb.

## 21.9/21.10 Zweiter Abgleich — bestanden, mit einem Befund

Am 18. August: der wachsende Chat fortgesetzt, drei neue Chats angelegt (darunter die Ersatz-Gabelung „Brillenstärke und Brennweite berechnen" sowie die Nacherzeugung von Denkschritten und Erzeugnis), und „Brillenstärken verstehen" gelöscht.

**Vorbereitung, die nötig war:** Das Protokoll trug ein `listed_at` vom heutigen Neuaufbau statt vom echten ersten Abgleich. Diesmal wäre die Schranke zufällig gültig gewesen, aber das Protokoll hätte eine falsche Geschichte erzählt. Neu aufgebaut mit `--now` auf den wahren Zeiten — erster Abgleich 2026-08-17T15:40, Umwandlung 17:47.

**Das Ergebnis des zweiten Abgleichs:**

| Erwartung | Ergebnis |
| --- | --- |
| der fortgesetzte Chat wird `stale` | **bestanden** — „API-Funktionen", gelistet 2026-08-18T09:15 gegen exportiert 2026-08-17T15:05 |
| die neuen sind `listed` mit `created_after` | **bestanden** — vier neue, `created_after` = 2026-08-17T15:40, also der Stand des vorherigen Abgleichs |
| der gelöschte wird nicht entfernt | **bestanden** — das Protokoll führt weiter 9 Chats |
| der gelöschte wird gemeldet | **nicht eingetreten** — s. u. |
| daraus eine neue Fenstergrenze | **bestanden** — 2026-08-17, Quelle jetzt `created_at` statt `project` |

**Der Kern der Konstruktion ist damit vorgeführt:** Der wachsende Chat entstand am 17., wuchs am 18. Das Fenster muss deshalb bis zum **17.** zurückreichen — wer naiv „seit dem letzten Lauf", also ab dem 18., exportiert hätte, hätte ihn verloren, und nichts hätte es gemeldet. Genau dafür gibt es die Tabelle in Vorgabe 2.4, und sie greift: Die Quelle der Grenze wechselte von `project` auf das exakte `created_at` des veralteten Chats.

**Befund: Der Export-Weg meldet verschwundene Chats nicht.** `chat_read_store.py` kennt dafür die Gruppe `vanished` — „a chat the protocol knows and the list no longer offers, which means deleted at the source or moved out of the project" — und `plan` gibt sie aus, ausdrücklich auch dann, wenn sonst nichts ansteht (3.2.3). `chat_export_convert.py` hat davon **nichts**: Weder `list` noch `diff` erwähnt, dass „Brillenstärken verstehen" aus der Quelle verschwunden ist. `diff` zählt ihn unter „4 exported", als wäre alles in Ordnung. Dieselbe Sorte Asymmetrie wie zuvor bei `analyse` gegen `report` — ein Konzept, das nur auf einer Seite gepflegt wurde.

**Beobachtung am Rande:** Die Rohausgabe der Chatliste kam diesmal **ohne** schließende `</chat>`-Tags, beim ersten Mal mit. `parse_chat_list` verarbeitet beides, weil es von einem `<chat`-Beginn bis zum nächsten schneidet und die schließenden Tags gar nicht braucht. Die Formvariation der Instanz ist damit belegt — und die Unempfindlichkeit dagegen auch.

## 21.11 Zweiter Export — bestanden, mit einem Befund über die Umgebung

Export über das errechnete Fenster (ab 17. August), 13 Konversationen, 17. bis 18. August. Über 80 % des Archivs sind Projektdateien — 2.095 KB gepackt gegen 425 KB für die Konversationen. Ein Export hat für dieses Konto also rund 2 MB Bodensatz, unabhängig vom Fenster; das ist dieselbe Eigenschaft, auf der der Sondierungsexport beruht, hier erstmals beziffert.

| Erwartung | Ergebnis |
| --- | --- |
| das Fenster fängt den gewachsenen Altchat ein | **bestanden** — „API-Funktionen" kam mit 32 statt 28 Turns und wurde ersetzt |
| Waisen-Scan meldet nichts | **bestanden** — 9 Chats, alle exportiert, keine Waisen |
| Erzeugnis kommt an | **bestanden** — 7 Werke in „Textdatei an Leerzeilen aufteilen" |
| Gabelung kommt an | **bestanden** — der Ersatzchat trägt einen Nebenzweig |
| Denkschritte kommen an | **nicht eingetreten** — 23 verworfen, 0 behalten |

**Schwach geprüft:** Das Ersetzen lief, das **Aufräumen** nicht. Der Dateistamm blieb gleich (Datum, Slug und UUID unverändert), und die alte Fassung hatte keine Nebendateien — es gab schlicht nichts zu entfernen. Die beiden erzwingenden Fälle aus Vorgabe 2.6, Umbenennung und wegfallende Nebendatei, sind weiterhin nur synthetisch geprüft.

**Nebenbei bestätigt:** Der Abfragechat der Chatliste steht im Export, aber nicht im Protokoll — `convert` hat ihn übergangen, weil die Chatliste ihn nie führte. Genau die dokumentierte Lücke, hier folgenlos, weil es ein Wegwerfchat war.

### Der Befund: Denkschritte werden nicht mehr ausgeschrieben

Die Denkblöcke sind nicht kurz — sie sind **leer**, und zwar alle. Gemessen über vier Exporte desselben Kontos:

| Export | Denkblöcke | davon `thinking_hidden` | `summaries`-Text gesamt |
| --- | --- | --- | --- |
| Nov–Dez 2025 | 513 | 0 (0 %) | 82.271 |
| Mai–Aug 2026 | 4.318 | 788 (18,2 %) | 1.137.052 |
| Testlauf 17.8. | 14 | 14 (**100 %**) | 1.507 |
| Testlauf 17.–18.8. | 41 | 41 (**100 %**) | 6.903 |

Der Anteil versteckter Denkblöcke steigt von null über 18 auf hundert Prozent. In beiden frischen Testexporten trägt **kein einziger** Block Text; an seiner Stelle steht `summaries`, im Median 190 Zeichen je Block.

**Der Code verhält sich dabei richtig:** Die Schwelle aus 3.1.3 verwirft `thinking_hidden`-Blöcke, weil sie leer sind — das war schon immer so und ist weiterhin verlustfrei. Falsch wird dadurch nichts.

**Was kippt, ist eine tragende Aussage der Doku.** 1.2 begründet „der Export ist der inhaltlich reichere Weg" wesentlich mit den Denkschritten — 9,2 Mio Zeichen, etwa so viel wie der Gesprächstext. Für **neue** Chats trifft das nicht mehr zu: Es bleiben Anhänge und Erzeugnisse. Der Export bleibt reicher, aber weniger deutlich.

**Und eine verworfene Entscheidung ist neu zu stellen.** 3.1.1 nennt `summaries` „für ein Archiv wertlos" — das Urteil fiel, als der volle Denktext danebenlag. Jetzt sind sie die einzige Spur. Ein Beispiel aus dem Testlauf: „Abwägung zwischen direkter Skripterstellung und vorheriger Planung." Das ist keine Verlaufsmeldung ohne Gehalt.

**Die Denkschritte waren da, und für alte Chats sind sie es weiterhin.** Gegenprobe am FreeCAD-Archiv, das aus einem Export von Anfang August stammt: 38 Denkblöcke, Median 925 Zeichen, zusammen 54.707 Zeichen echter Text. Die Aussage lautet also nicht „der Export trug nie Denkschritte", sondern „er trägt sie für **neue** Chats nicht mehr".

**Der Umschlag hat ein Datum.** Nach `created_at` der Nachricht ausgezählt, über drei Exporte hinweg:

| Zeitraum | Anteil versteckter Denkblöcke |
| --- | --- |
| bis 20. Juli 2026 | **0 %** — über Wochen, tausende Blöcke, ausnahmslos |
| ab 21. Juli 2026 | 28,8 %, danach stark schwankend |
| 24. bis 28. Juli | 83 bis 100 % |
| 1. August | **0 %** bei 91 Blöcken |
| 2. bis 6. August | 88 bis 100 %, am 5. dagegen 9,1 % |
| 17. und 18. August | 100 % |

**Es ist kein globaler Umschalter.** Am 1. August waren alle 91 Blöcke sichtbar, am 5. August 40 von 44. Etwas variiert also je Chat oder je Nachricht — am ehesten das verwendete Modell. Aus dem Export ist das **nicht** zu belegen: Weder Konversation noch Nachricht führt ein Modellfeld (3.1.1).

**Grenzen des Befunds:** Ein Konto. Die jüngsten Stichproben sind klein — 32 Blöcke am 17. August, 9 am 18. Dass 100 % inzwischen der Normalfall ist, ist damit **nicht** belegt; belegt ist der Umschlag am 21. Juli und die Schwankung danach.

## 21.8 zweite Hälfte: Wirkt der Anweisungsblock? — bestanden

Aufbau: ein Wegwerfordner `~/zielprojekt-test/` **außerhalb** dieses Repos — bewusst außerhalb, weil Claude Code `CLAUDE.md`-Dateien den Verzeichnisbaum hinauf einsammelt und ein Ordner innerhalb des Repos unsere Projektanweisungen mitgeladen hätte; die Instanz hätte dann von diesem Vorhaben gewusst. Darin `.claude/imported_chats/chats-export-aus-pro-test-1/` mit den zwölf Archivdateien und eine `CLAUDE.md`, die **nur** den Anweisungsblock enthält, sonst nichts. Der Versuch lief in einer frischen Sitzung, die von diesem Vorhaben nichts weiß.

**Die Frage war schärfer als die geplante.** Vorgesehen war „Welche Wanderroute hatten wir geplant?" — also eine Frage, deren Antwort im Archiv steht. Gestellt wurde stattdessen eine **neue** Frage zum selben Gebiet: ob es sinnvoll sei, von Severní nach Lobendava zu gehen oder anders herum. Das Archiv war damit nicht die Antwort, sondern der Zusammenhang, den die Instanz von sich aus hätte übersehen können.

**Der Ablauf, aus dem Sitzungstranskript:**

1. Vor jedem Werkzeugaufruf die Ankündigung: „Ich sehe im Chat-Archiv dieses Projekts nach, ob die Wanderung dort schon besprochen wurde." Ungefragt, ohne Hinweis des Nutzers.
2. `ls` über das Archivverzeichnis — sie verschafft sich erst einen Überblick.
3. `grep -ril` über mehrere Ortsnamensvarianten (`Lobendau`, `Lobendava`, `Schluckenau`, …).
4. `wc -c` über die Treffer, bevor sie liest — sie prüft die Größe, statt blind zu öffnen.
5. `Read` auf genau eine Datei: `2026-08-17_wanderung-planen_5f8ac1bd.json`.
6. Antwort mit Quellenangabe: **„Im Archiv gibt es dazu einen Chat: „Wanderung planen" vom 17.08.2026"** — Datum und Titel, genau wie der Block es verlangt —, dazu die Route Oppach → Šluknov → Severní/Lobendava, die zweite Etappe über die Kapelle sv. Anny und der ausdrücklich ausgeschlossene Grenzweg.
7. Erst danach die eigentliche neue Frage, mit Websuche beantwortet.

**Damit ist die Behauptung aus 3.1.6 belegt**, der Block mache die Anweisung dauerhaft wirksam. Sie war bis hierher nie geprüft, und anders als so ist sie nicht prüfbar.

**Drei Entwurfsentscheidungen haben sich dabei nebenbei bewährt:**

- **Die Dateinamen (Vorgabe 2.3).** Datum, Titel-Slug und UUID im Namen erlaubten der Instanz, nach dem `ls` Kandidaten zu wählen, bevor sie eine Datei öffnete.
- **Das flache Verzeichnis je Quellprojekt (2.10).** Ein `grep -ril` über einen Ordner genügte; es gab keine Struktur zu durchdringen.
- **Die Auslagerung der Nebendateien (2.2).** Gelesen wurde allein die Gesprächsdatei. Denk-, Anhangs- und Erzeugnisdatei blieben ungeöffnet — genau die Mengenersparnis, mit der 2.2 begründet ist.

**Eine Beobachtung zum Wortlaut:** Der Block schickt die Instanz zu `Grep` und `Read`. Gesucht hat sie mit `Bash`/`grep`, gelesen mit `Read` — funktional dasselbe. Werkzeugnamen im Block festzuschreiben ist demnach weder nötig noch schädlich; die Instanz wählt ihr Mittel selbst.

## 21.8 erste Hälfte: der Rückweg ins Projektwissen — bestanden, mit einem Nebenbefund

`protokoll.json` ins Projektwissen des Quellprojekts hochgeladen. Drei Fragen an eine Instanz dort, drei Antworten:

| Frage | Soll | Antwort |
| --- | --- | --- |
| Nimmt claude.ai eine `.json` als Projektdatei an? | ja | **ja** |
| Status von „Brillenstärken verstehen"? | `exported` | **`exported`** |
| `project_created_at`? | 2026-08-17 | **2026-08-17** |
| Wie viele Chats führt die Datei? | 9 | **10** |
| `exported_updated_at` von „Brillenstärken verstehen"? | `2026-08-17T14:30:35.984103Z` | **zeichengenau richtig** |

**Die Textextraktion ist verlustfrei.** Der Zeitstempel kam mit Mikrosekunden unverändert zurück — der empfindlichste Prüfstein, den die Datei hergibt, und genau der Wert, an dem die Fensterrechnung hängt. Die Annahme aus 1.7, Textextraktion sei bei JSON verlustfrei, ist damit nicht mehr nur behauptet.

**Aber die Instanz hat sich verzählt: 10 statt 9.** Beide Kopien der Datei sind bitgleich, der Sollwert steht fest. Einen einzelnen Wert nachschlagen gelingt also zuverlässig, das Aufsummieren über die Datei nicht.

**Das bestätigt eine Entwurfsentscheidung, die auch anders hätte ausfallen können.** Doku 1.4 begründet das Protokoll damit, dass eine Instanz zwar eine kleine Datei lesen, aber nicht N Chatdateien durchzählen kann. Der Versuch schärft das: Sie kann nicht einmal die Einträge **einer** kleinen Datei verlässlich zählen. Gefährlich wird das nicht, weil der Entwurf es nie verlangt — `plan`, `overview` und `map` rechnen im **Skript**, das die JSON parst; die Instanz führt es nur aus. Hätte man stattdessen darauf gesetzt, dass die Instanz das Protokoll „einfach liest und weiß, was fehlt", stünde hier jetzt ein stiller Fehler.

## 21.12 erste Hälfte: die fremde Instanz allein am Docstring — bestanden

Skript und Protokoll in einen neuen Chat des Quellprojekts, dazu ein Prompt ohne jede Erklärung: „Im Anhang ein Skript und eine Protokolldatei. Der Docstring des Skripts ist die Arbeitsanweisung. Fang an." Alles Weitere kam von der Instanz.

| Erwartung | Ergebnis |
| --- | --- |
| Upload-Probe, Dateien **kopieren** statt in place arbeiten | **bestanden** — Fundort geprüft, Parsen bestätigt, ins Arbeitsverzeichnis kopiert |
| `plan` vor jedem Lesen | **bestanden**, ausdrücklich benannt |
| frische Chatliste selbst holen | **bestanden** — `recent_chats` mit `n=20` in einem Durchgang |
| verschwundener Chat als Befund, nichts automatisch entfernt | **bestanden** — samt aller drei möglichen Ursachen |
| nicht für den Nutzer entscheiden | **bestanden** — Option A und B mit Preis, dann die Frage |
| kein Umfang erfunden, wo keiner bekannt ist | **bestanden** — „keine ehrliche Kostenschätzung vorab" |

Damit ist die Zusage aus Vorgabe 2.9 belegt: Die hochgeladene Datei allein genügt. Eine Instanz, die von diesem Vorhaben nichts weiß, hat den ganzen Ablauf aus dem Docstring hergeleitet — einschließlich der Stellen, an denen er ihr Zurückhaltung vorschreibt.

**Und ein siebtes, ungeplantes Bestehen:** Auf die Bitte, zwei bestimmte Chats zu lesen, hat die Instanz **nicht** gehorcht, sondern nachgefragt — beide seien laut Protokoll vollständig `exported` und laut `plan` unverändert, ein erneutes Lesen also unnötig; ob wirklich diese gemeint seien oder zwei andere. Sie prüft eine Anweisung gegen das Protokoll, statt sie auszuführen. Das steht in keiner Erwartungstabelle und ist trotzdem genau die Haltung, die der Docstring an anderen Stellen verlangt.

### Drei Befunde aus diesem einen Durchgang

**Der Upload-Ort ist bestätigt.** Der Docstring nennt `/mnt/user-data/uploads` ausdrücklich als Community-Vermutung, die man nicht für gesichert nehmen soll. Die Dateien lagen dort. Nach Vorgabe 2.1 steigt die Beleglage damit von **Community** auf **beobachtet** — durch eigenes Nachstellen.

**Der Prüfbestand ist von selbst gewachsen.** `plan` meldet einen neuen Chat `32b15e4f` „Protokoll-Datei analysieren" — das ist der Chat, in dem wir die erste Hälfte von 21.8 geprüft haben. Arbeit im Projekt erzeugt Chats, und der Abgleich bemerkt sie. Genau der Fall, für den das Werkzeug gebaut ist, hier ungeplant und deshalb besonders glaubwürdig.

**Und eine Verfeinerung, die von der Instanz kam.** Die drei Ursachen eines verschwundenen Chats sind von außen ununterscheidbar — aber eine lässt sich einschränken: Kam die Liste mit `n=20` in einem einzigen Durchgang zurück, **ohne** die zwanzig zu erreichen, dann war sie zu Ende geblättert, und „nicht bis zum Ende paginiert" ist unwahrscheinlich. Die Instanz hat das selbst gefolgert und es trotzdem nicht als sicher gewertet. Der Gedanke steht in keinem unserer Texte und wäre dort gut aufgehoben.

## 21.12 zweite Hälfte: `read_conversation` ist in dieser Umgebung nicht vorhanden

Beim Übergang zum Lesen meldete die Instanz, ihr Werkzeugsatz kenne **nur** `conversation_search` und `recent_chats`. Kein `read_conversation`.

**Was das für den Entwurf bedeutet, wenn es sich bestätigt.** Der ganze Lese-Weg ruht darauf: Turns mit Index, `total_turns` aus dem Envelope, seitenweises Blättern, Vollständigkeit als Rechnung (3.2.1, 3.2.2). Ohne dieses Werkzeug ist `chat_read_store.py` in dieser Umgebung nicht benutzbar — und damit fällt der **zweite von zwei Wegen** aus.

Besonders unangenehm ist die Verkettung mit dem Kontobefund: Für Chats in einem Team-Konto hat ein gewöhnliches Mitglied keinen Export (1.2, 1.6), weshalb der Lese-Weg dort **der einzige** war. Fehlt er auch, bleibt für solche Chats **kein Weg**.

**Es widerspricht früheren Beobachtungen desselben Kontos.** 3.2.1 führt mehrere Befunde zu `read_conversation` als *beobachtet* — wortidentische Turns, Seitengröße durch ein Zeichenbudget, Scope-Bindung im Kontrollversuch. Diese Beobachtungen stammen aus dem August 2026 und können nur von einer claude.ai-Instanz kommen; Claude Code hat dieses Werkzeug nicht. Es war also da und ist es jetzt nicht.

**Gegengeprüft in der zweiten Oberfläche: dasselbe.** Der erste Versuch lief im Browser, der zweite in Claude Desktop, beide im **Pro-Konto** am 18. August 2026. Auch dort kennt die Instanz nur `conversation_search` und `recent_chats`. Zwei Oberflächen, ein Konto, gleiches Ergebnis.

**Zurückgenommen: Die Probe taugt nicht.** Im Konto steht der **Tool-Zugriffsmodus** auf „Tools bei Bedarf laden". Belegt dazu: *„On demand: Connectors aren't loaded until Claude searches for the right one based on your request. Claude finds the most relevant connectors and loads only those"* ([13730515](https://support.claude.com/en/articles/13730515-manage-claude-s-tool-access)); die Alternativen sind **Auto** (Vorgabe) und je Connector „Always available".

Wir haben die Instanz nach ihrem Werkzeugsatz **gefragt**, statt sie ein Werkzeug **benutzen** zu lassen. Bei bedarfsweisem Laden beschreibt eine solche Antwort nur, was gerade geladen ist — nicht, was erreichbar wäre. Beide Versuche, Browser wie Desktop, hängen an diesem Fehler; die Übereinstimmung beweist nichts, weil beide dieselbe Einstellung trafen.

**Was stehen bleibt und wogegen es spricht.** Im ersten Versuch war der Kontext mit `read_conversation` gesättigt — der Docstring nennt es dutzendfach —, und ein besserer Auslöser für ein bedarfsweises Nachladen ist schwer vorstellbar. Das spricht gegen die Erklärung, ist aber kein Gegenbeweis: Ob die Chat-Werkzeuge überhaupt unter diesen Mechanismus fallen, ist unbekannt. Die Hilfeseite zur Chat-Suche nennt weder Werkzeugnamen noch den Lademechanismus, und die Einstellung spricht ausdrücklich von *Connectors*.

**Der Befund ist damit offen, nicht widerlegt.** Was gilt: Mit dieser Kontoeinstellung hat eine Instanz in beiden Oberflächen kein `read_conversation` angeboten. Was nicht gilt: dass es fehlt.

**Zweiter Probenversuch, ebenfalls untauglich — und der Fehler lag im Entwurf der Probe.** Nach Umstellen der Einstellung wurden beide Oberflächen gebeten, einen bestimmten Chat vollständig zu lesen und die Zahl seiner Turns zu nennen; die Turn-Zahl war als Prüfstein gedacht, weil sie sonst nur `read_conversation` liefert. Beide antworteten korrekt „10 Turns" — und beide entnahmen das dem **Projektwissen**: `protokoll.json` führt das Feld `turns` je Chat. Die Antwort lag also neben der Frage, und kein Leserwerkzeug wurde gebraucht. Die Desktop-Instanz prüfte zusätzlich per `conversation_search` gegen, nicht per `read_conversation`.

**Die Lehre für den Prüfentwurf:** Eine Probe taugt nur, wenn **allein** das geprüfte Werkzeug die Antwort hervorbringen kann. Zweimal verfehlt — erst durch Selbstauskunft statt Verhalten, dann durch eine Antwort, die anderswo bereitlag.

**Die dritte Fassung schließt beide Lücken:** gefragt wird nach dem **Wortlaut eines Turns mit bestimmter Nummer** aus einem Chat, den das hochgeladene Protokoll **nicht** kennt. Turn-Nummern vergibt nur `read_conversation`; ein Chat außerhalb des Protokolls entzieht die Abkürzung über das Projektwissen; und Suchschnipsel tragen weder Nummern noch ein Sollmaß.

### Entschieden: Das Werkzeug war da und ist weg

**Es war da.** Der Sitzungsverlauf vom **6. August 2026** enthält den Beweis, und zwar dreifach. Eine claude.ai-Instanz zitierte die Werkzeugbeschreibung wörtlich: *„Retrieve the full content of one past conversation by its UUID, paginated by turn. Reads the live conversation store (fresher than the conversation_search index). Pass a conversation_search result's page_token to open at that chunk's position, or the next_page_token / prev_page_token from a previous call to page through."* Sie erklärte, `page_token` aus einem Suchtreffer werde „consumed by a different tool: `read_conversation`, which takes `conversation_id` and `page_token`". Und sie fügte eine **echte Ausgabe** ein:

```
<chat url="https://claude.ai/chat/d64eea15-…" updated_at="2025-11-13T22:07:44.559082+00:00"
  total_turns="58" turns="0-7" next_page_token="t8"><title>Flattening angled parts …
<turn n="0">Human: Es geht darum, wie man aus einer Baugruppe einen Body auswählt …
```

Der Chat `d64eea15` ist echt — er liegt als `2025-11-13_flattening-angled-parts-in-techdraw-projections_d64eea15.json` im FreeCAD-Archiv. Die Rohausgabe wurde damals im Container unter `/home/claude/read_conversation_raw_d64eea15.txt` abgelegt. Der Name in unserer Doku ist also weder erfunden noch abgeleitet: Er stammt aus der Werkzeugbeschreibung selbst, und das Werkzeug hat gearbeitet.

**Dazu drei Fehlermeldungen aus Kontrollversuchen desselben Tages**, im Wortlaut festgehalten: `Invalid conversation_id: expected a UUID (the trailing path segment of a chat URL).` bei einer Cowork-ID, und `Conversation not found or not accessible.` bei einer gültigen UUID außerhalb des Bereichs, in mehreren Durchgängen. Genau daraus stammen zwei Befunde, die bis heute in der Doku stehen: die Scope-Bindung (3.2.1) und die Formatabweisung von Cowork-IDs (1.6). Drei unterschiedlich formulierte Meldungen, ein Envelope mit passendem echtem Chat und die zitierte Werkzeugbeschreibung sind zusammen ein Verhaltensbild, das sich nicht herbeischreiben lässt.

**Und zur schärfsten Gegenfrage — ob die Instanz den Envelope erfunden haben könnte, weil sie die Chatinhalte ohnehin kannte:** ausgeschlossen, an zwei unabhängigen Werten geprüft. Der Envelope nannte um 16:03 `total_turns="58"` und `updated_at="2025-11-13T22:07:44.559082+00:00"`. Das Export-ZIP traf **um 20:33 desselben Tages** ein, viereinhalb Stunden später, und das daraus erzeugte Archiv führt für denselben Chat 58 Turns und `source_updated_at` 2025-11-13T22:07:44.559082Z — beides deckungsgleich, der Zeitstempel bis auf die Mikrosekunde. `conversation_search` liefert weder Turn-Summen noch Metadaten-Zeitstempel; die Instanz konnte diese Werte nicht anderweitig haben. Eine Zahl und einen mikrosekundengenauen Zeitstempel zu erfinden, die Stunden später ein unabhängig beschaffter Export bestätigt, ist nicht möglich.

**Zur Alternativthese, es sei eine Python-API im Container gewesen:** dagegen spricht dreierlei. Der Verlauf zeigt keinen Code-Aufruf, sondern ein Werkzeugergebnis, das die Instanz anschließend zur Prüfung in eine Datei schrieb. Sie lieferte für `conversation_search` und `recent_chats` vollständige Parameter-Schemata mit Typen, Vorgaben und Min/Max — die Form von Modellwerkzeugen —, und `read_conversation` stand in derselben Aufzählung. Und der Netzzugang des Containers geht nur gegen eine Allowlist, auf der `claude.ai` nicht steht (1.6); eine Container-API hätte dorthin gar nicht durchgekonnt.

**Dass sich im Netz keine Spur findet, wiegt dagegen wenig.** Die nach außen sichtbare Funktion — Claude findet frühere Chats — ist mit `conversation_search` allein dieselbe; der Unterschied fällt nur auf, wer Werkzeuge aufzählt oder darauf baut. Wir selbst haben es zufällig entdeckt, beim Erfragen der Parameter der *anderen* beiden. Ein knapper oder schmaler Rollout hinterlässt so keine öffentlichen Berichte. Vor allem aber: Ein Fehlen von Fremdberichten kann eine **positiv verifizierte** Beobachtung nicht entkräften — die Übereinstimmung von Turn-Zahl und Mikrosekunden-Zeitstempel mit einem Stunden später eingetroffenen Export steht unabhängig davon.

**Zur naheliegenden Gegenfrage, ob es das Werkzeug je gab:** In den öffentlichen Anthropic-APIs ist es nicht zu finden — das ist aber die falsche Stelle. `read_conversation` war ein **eingebautes Werkzeug der claude.ai-Instanz**, so wie `conversation_search` und `recent_chats`, und auch die stehen in keiner öffentlichen API; die Hilfeseite zur Chat-Suche sagt allein, solche Zugriffe erschienen „as tool calls". Das Fehlen einer öffentlichen Dokumentation ist deshalb kein Gegenbeleg.

**Es ist weg.** Am **18. August 2026**, mit auf „alle laden" gestelltem Tool-Zugriffsmodus, in **vier** Anläufen: Browser mit Sonnet, Browser erneut, Desktop mit Sonnet, Desktop mit Opus bei hohem Effort. Alle vier: kein `read_conversation`. Die Opus-Instanz nennt zusätzlich den strukturellen Grund, warum kein Ersatz taugt — `conversation_search` und `recent_chats` *„nehmen auch keine Chat-ID als Parameter – ich kann damit einen bestimmten Chat also weder gezielt adressieren noch komplett auslesen"*. Und sie ordnet den früheren Zufallstreffer richtig ein: *„ein Treffer der Stichwortsuche, kein gezielter Zugriff über die ID"*.

**Auch im Team-Konto nicht.** Dieselbe Frage dort, dasselbe Ergebnis.

**Damit steht:** Zwölf Tage zwischen belegter Nutzung und belegter Abwesenheit, über zwei Konten, zwei Oberflächen und mehrere Modelle. Warum — entfernt, umbenannt, anders freigeschaltet — bleibt offen und ist für die Folgen gleichgültig: Aus der Sicht dieses Nutzers gibt es das Werkzeug nicht mehr.

### Was daran hängt

**Der Lese-Weg ist nicht lauffähig.** `chat_read_store.py` ruht vollständig auf diesem Werkzeug (3.2.1, 3.2.2). Von den zwei Wegen aus 1.2 bleibt einer.

**Fahrplanpunkt 23 ist beantwortet, und zwar ungünstig.** Er sollte klären, ob der Lese-Weg in einem Team-Projekt arbeitet — für Team-Chats war er der einzige Weg, weil ein gewöhnliches Mitglied keinen Export hat (1.2, 1.6). Er arbeitet dort nicht. **Für Chats in einem Team-Konto bleibt damit kein Weg.**

**21.12 ist nicht fortsetzbar, 21.13 blockiert.** Die Wegegleichheit an echten Daten — der schärfste Test dieses Vorhabens — lässt sich nicht durchführen, solange nur ein Weg läuft. Vorgabe 2.5 bleibt synthetisch geprüft.

**Fahrplanpunkt 10 kippt zurück ins Offene.** Eben noch war er beantwortet: Der Crawler bleibt, weil er dort arbeitet, wo `read_conversation` fehlt. Genau dieser Fall ist jetzt eingetreten — nur zeigt die Desktop-Beobachtung, dass `conversation_search` bei einem Chat mit zehn Turns eine **Zusammenfassung** statt Blöcken lieferte. Ein Crawler, der Zusammenfassungen einliest, archiviert eine Nacherzählung und verstößt gegen Vorgabe 2.8. Ob der Rückfallweg überhaupt noch trägt, ist damit selbst fraglich.

**Eine Korrektur an meiner eigenen Folgerung.** Ich hatte geschrieben, für ein Team-Mitglied bliebe damit „kein Weg". Das war ein Sprung: Geprüft wurde ein **Pro**-Konto. Richtig ist der bedingte Satz — *falls* das Werkzeug auch dort fehlt, hätte ein Team-Mitglied weder Export noch Lese-Weg. Genau das entscheidet Fahrplanpunkt 23, und der ist damit von einer Randfrage zur wichtigsten offenen Prüfung geworden.

### Zwei Umgebungsfakten nebenbei, beide neu

**Projektwissen liegt im Container unter `/mnt/project/`.** Die Doku sagt bisher nur, Projektdateien seien im Container erreichbar, „while remaining in context" — der Pfad stand nirgends. Er ist das Gegenstück zu `/mnt/user-data/uploads` für Chat-Anhänge. Dort lag genau eine Datei: die hochgeladene `protokoll.json`. Die Chatdateien liegen erwartungsgemäß nicht dort; sie gehören ins Zielprojekt, nicht ins Quellprojekt.

**`conversation_search` liefert zweierlei.** Bei „Brillenstärke und Brennweite berechnen" (2 Turns) kam ein Treffer mit `kind="conversation"` und dem **vollständigen Wortlaut**; bei „Wanderung planen" (10 Turns) nur `kind="summary"`, eine verdichtete Zusammenfassung. Doku 3.4 kennt bisher nur „feste, nicht überlappende Blöcke". Dass die Suche bei kurzen Chats faktisch den ganzen Chat zurückgibt und bei längeren auf eine KI-Zusammenfassung wechselt, ist neu — und für den Crawler-Weg von einiger Bedeutung: Eine Zusammenfassung ist kein Transkript, und wer sie einliest, archiviert eine Nacherzählung.

**Wie die Instanz damit umging — der eigentliche Prüferfolg.** Bei `128aa097` lieferte `conversation_search` zufällig den ganzen Chat, weil er nur zwei Turns hat. Sie hat das erkannt und **nicht** verwendet: das sei „Glück des kurzen Chats, keine verlässliche, vollständige, paginierte Quelle", und Schnipsel zu verarbeiten hieße „genau die Sorte beschädigter/erfundener Transkripte erzeugen, vor der der Docstring ausdrücklich warnt". Sie hat stattdessen auf `chat_crawl_store.py` verwiesen — hergeleitet aus dem Docstring — und gefragt.

Damit ist Vorgabe 2.8 an der schärfsten denkbaren Stelle bestätigt: Eine fremde Instanz stand vor einer Quelle, die *fast* gepasst hätte, und hat sie verworfen, statt ein plausibles Ergebnis zu erzeugen.

**Und Fahrplanpunkt 10 ist damit beantwortet.** Die Frage lautete, ob `chat_crawl_store.py` bleibt oder wegkommt; 3.4 nennt es „überholt, wo `read_conversation` existiert". Genau dieser Halbsatz trägt die Antwort: Wo es nicht existiert, ist der Crawler das einzige Werkzeug, das arbeiten kann. Er bleibt.

**Folge für den Testlauf:** 21.12 ist ab hier nicht fortsetzbar, und **21.13 — Wegegleichheit an echten Daten — ist blockiert**, weil dafür eine Datei aus dem Lese-Weg gebraucht wird. Beides hängt an der Gegenprüfung.

## Was zum Rechnerwechsel gilt

`tests/test_results/` ist auf diesem Rechner (fwfe41) leer gewesen, weil sein Inhalt gitignoriert ist und **nicht mit dem Repo wandert**. Die älteren ZIPs und das FreeCAD-Archiv liegen auf dem Laptop und sind nicht verloren; eine frühere Notiz hier sprach von Verlust, das war falsch.

**Folge für die Prüfarten:** *kalt* heißt ohne Konto und ohne Netz — aber nicht ohne Voraussetzung. Das Prüfmaterial ist rechnergebunden, dieselbe kalte Prüfung ist auf dem einen Rechner lauffähig und auf dem anderen nicht. Das gehört in die Definition in Doku 4.1.

**Fahrplanpunkt 24** bleibt damit ausführbar — er braucht `freecad/protokoll.json` mit den 22 Chats, und die liegt auf dem Laptop. Nötig ist nur diese eine Datei, nicht das Archiv und nicht die ZIPs.

## Beobachtungen je Schritt

### 21.2 Testprojekt anlegen und füllen

Am 17. August 2026 angelegt, Angaben oben; in claude.ai sichtbar. Füllen steht aus, zuerst die Erreichbarkeitsprobe über die Chatliste.

### 21.5 vorgezogen — die Chatliste

Erster Versuch, gestellt im **ersten** Chat des Projekts: ein **leerer** Codeblock. Die Form stimmte — Codeblock, kein Kommentar, kein Text davor oder danach —, `MAPPING_PROMPT` tut also, was er soll; leer war nur der Inhalt.

Zweiter Versuch, gestellt in einem **zweiten** Chat: genau ein Eintrag, nämlich der erste Chat, mit UUID-förmiger ID und `updated_at`. Damit ist bewiesen, was zu beweisen war — das Projekt ist für `recent_chats` erreichbar, es ist ein gewöhnliches claude.ai-Projekt, und die Rohform passt zu `parse_chat_list`.

**Offen bleibt, warum der jeweils laufende Chat fehlt.** Zwei Erklärungen passen auf beide Beobachtungen gleich gut: Entweder listet `recent_chats` den laufenden Chat grundsätzlich nicht mit, oder ein frisch angelegter Chat ist noch nicht indiziert. Der Unterschied ist nicht akademisch: Gilt das Erste, dann **fehlt jedem Listenlauf systematisch genau der Chat, aus dem er gestartet wurde** — eine dauerhafte Lücke im Archiv, die niemand meldet.

**Entschieden.** Dritter Versuch, gestellt wieder im **ersten** Chat: genau ein Eintrag, nämlich der **zweite** Chat. Aus Chat 1 kommt Chat 2, aus Chat 2 kam Chat 1 — beide inzwischen indiziert, jeder sieht den anderen, keiner sich selbst.

**Beobachtet, nirgends dokumentiert: `recent_chats` listet den laufenden Chat nicht mit.** Zwei symmetrische Beobachtungen, die Indizierungs-Erklärung ist damit widerlegt.

**Die Folge wiegt schwer.** Jeder Listenlauf übergeht genau den Chat, aus dem er gestartet wurde. Das Protokoll erfährt nie von ihm, also fehlt er im Archiv — und `diff` kann ihn nicht als fehlend melden, weil das Protokoll ihn gar nicht kennt. Es ist ein Zuwenig, das keine der eingebauten Kontrollen bemerkt: Der Waisen-Scan meldet nur ein Zuviel, und die Vollständigkeitsrechnung des Lese-Wegs gilt je Chat, nicht für die Menge der Chats.

**Betrifft beide Wege**, denn beide bauen ihr Protokoll aus derselben Liste: `list --map` im ZIP-Weg und `map` im Lese-Weg.

**Gegenmittel ohne Code, vom Nutzer vorgeschlagen und übernommen:** die Liste in einem **eigens dafür angelegten Chat** holen und diesen **danach löschen**. Dann bleibt gar nichts zurück — der fehlende Chat ist der, der nichts enthielt als den Listenabzug, und im Projekt sammeln sich keine Karteileichen. Der zuerst erwogene Weg, immer denselben Abfragechat zu verwenden, ist schlechter: Er ließe die Karteileiche liegen und würde beim nächsten Lauf selbst mitarchiviert.

**Gegenprobe am Altbestand möglich:** Das FreeCAD-Archiv führt 22 Chats. Zeigt die Chatliste des Projekts heute 23, ist einer stillschweigend nie mitgekommen — vermutlich der, aus dem damals die Liste geholt wurde. Das wäre die Bestätigung des Befunds an echten Daten und kostet eine Abfrage.

### Kontolage — Befund mit Folgen über den Test hinaus

Das Testprojekt liegt im **Team-Konto**. Dort gibt es für ein gewöhnliches Mitglied **keinen** Datenexport: *„Data exports are available to individual Claude users on Free, Pro, and Max plans"* (belegt, [9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data)), und für Organisationen *„Individual members of Team and Enterprise organizations do not have a self-serve export option"* — nur der Primary Owner kann exportieren, unter *Organization settings → Data and privacy* (belegt, [13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data)).

Der eigentliche Bedarf des Nutzers ist **Pro → Team**: Quelle ist das Pro-Konto, in dem der Export vorhanden ist. Der Hauptweg ist damit nicht blockiert. Betroffen ist allein der umgekehrte Fall — Chats, die **im** Team-Konto liegen und archiviert werden sollen.

### Cowork als möglicher Ausweg — recherchiert

- Verfügbar auf Pro, Max, Team und Enterprise, über Desktop, Web und Mobile (belegt, [13455879](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans)).
- **Lokale Sitzung:** *„The agent loop runs natively on the device"* — die Unterhaltung bleibt auf dem Gerät. **Pfade und Dateiformat sind nicht dokumentiert** (belegt, [14479288](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview)).
- **Cloud-Sitzung:** läuft in Anthropics Sandbox, *„sessions and files are saved to the member's Claude account"* — und auf **Team-Plänen ist die Cloud-Sitzung standardmäßig eingeschaltet**. Der Ausweg „Cowork legt mir die Dateien lokal hin" gilt dort also nur, wenn ausdrücklich lokal gearbeitet wird.
- Cowork ist über die **Compliance-API** erfasst — die nach 4.5 nur Enterprise offensteht.

**Bewertung:** Cowork und „nur noch Claude Code" retten nichts. Beide ändern, *wo künftig gearbeitet wird*, damit die Daten von vornherein lokal liegen; für Chats, die heute schon im Team-Konto stehen, tun sie nichts. Das ist ein anderer Problemtyp als der, für den dieses Vorhaben gebaut ist. Cowork wird deshalb **beobachtet, nicht gebaut** (Kapitel 4).

### Entscheidung zur Testumgebung

Der mehrstufige Test läuft im **Pro-Konto**: Dort liegt die echte Quellumgebung des Nutzers — sein Bedarf ist Pro → Team —, und nur dort gibt es den Export. Die neun Profilmerkmale entstehen also in einem neuen Projekt dieses Kontos; im Team-Projekt ist bisher nur ein Chat, es geht nichts verloren.

Das Team-Projekt **bleibt stehen** für Fahrplanpunkt 23: die Probe, ob der Lese-Weg dort ebenso arbeitet. Für Team-Chats ist er der einzige Weg, und ob `read_conversation` in einem Team-Projekt greift, ist unbelegt.

**Nicht geprüft wird der Organisationsexport.** Dafür bräuchte es Primary-Owner-Rechte; die zu erwerben wäre kein Prüfaufwand, sondern ein Eingriff in die Organisation. Und selbst mit ihnen bliebe das Verfahren für den laufenden Betrieb untauglich: Ein wiederkehrender Abgleich, der jedes Mal den Administrator braucht, ist keiner.
