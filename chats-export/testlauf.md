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

**Grenzen des Befunds:** Zwei Testtage eines Kontos, 55 Blöcke. Warum die Blöcke versteckt sind — Modellwahl, Rollout, Kontoeinstellung — ist **nicht** ermittelt. Belegt ist allein: In beiden frischen Exporten trägt kein Denkblock Text.

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
