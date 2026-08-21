# Testlauf — Protokoll der warmen Tests

Das Protokoll zu Fahrplanpunkt 21: was angelegt wurde, was beobachtet wurde, was daraus folgte. Es steht hier und nicht im Fahrplan, weil der eine reine Aufgabenliste ist, und nicht in der Doku, weil eine Beobachtung noch keine Festlegung ist.

**Diese Datei ist befristet.** Punkt 21 ist abgeschlossen; sie fällt mit Fahrplanpunkt 13, sobald geprüft ist, dass alles Bleibende in der Doku steht.

**Was hier absichtlich kurz ist.** Läufe, deren Prüfansatz sich als nicht tragfähig erwies, und Läufe, die ein Szenario prüften, das der heutige Entwurf nicht mehr braucht — vor allem alles am entfallenen Lese-Weg —, stehen nur noch als Halbsatz da: was geprüft wurde und warum es nicht trägt. In vollem Wortlaut bleibt, was die heutige Lösung verifiziert: den Kontoexport-Weg, den Web-Weg und den Rückweg ins Zielprojekt.

## Die Testumgebung

### Das Testprojekt im Pro-Konto — Träger des mehrstufigen Tests

| | |
| --- | --- |
| Titel | „Chats-Export aus Pro, Test 1" |
| „Was Sie erreichen wollen" | „Das ist ein Testprojekt im Pro-Konto." |
| Angelegt | 17. August 2026 |
| Konto | Pro — hier liegt die echte Quellumgebung, und nur hier gibt es den Export |

Der Sollwert für 21.4 ist der **17. August 2026**; die Uhrzeit spielt keine Rolle, weil der Export nur ein Datum führt.

**Jeder Chat wird als „Chat" angelegt, nie als Cowork.** Die Wahl zwischen beidem erscheint erst beim Anlegen eines Chats, nicht beim Anlegen des Projekts — und auf allen bezahlten Plänen (belegt, [13455879](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans)). Cowork-Chats sind über jeden Weg unerreichbar, ihre IDs sind keine UUIDs und werden am Format abgewiesen (Doku 1.6, 4.3). Cowork wird deshalb beobachtet, nicht gebaut (Kapitel 4).

### Das Testprojekt im Team-Konto

Angelegt am 17. August 2026 als „Chats-Export, Test 1", ursprünglich als Prüfstück für Fahrplanpunkt 23 — die Frage, ob der Lese-Weg in einem Team-Projekt arbeitet. Der Punkt ist gestrichen, das Projekt trägt heute den Skill-Lauf aus Punkt 27c. Bestätigt hat es nebenbei, dass ein in Claude Desktop angelegtes gewöhnliches Projekt im Konto liegt und nicht nur lokal.

### Kontolage — Befund mit Folgen über den Test hinaus

Im Team-Konto gibt es für ein gewöhnliches Mitglied **keinen** Datenexport: *„Data exports are available to individual Claude users on Free, Pro, and Max plans"* (belegt, [9450526](https://support.claude.com/en/articles/9450526-export-your-claude-data)), und für Organisationen *„Individual members of Team and Enterprise organizations do not have a self-serve export option"* — nur der Primary Owner kann exportieren, unter *Organization settings → Data and privacy* (belegt, [13346720](https://support.claude.com/en/articles/13346720-export-your-organization-s-data)).

Der eigentliche Bedarf des Nutzers ist **Pro → Team**: Quelle ist das Pro-Konto, in dem der Export vorhanden ist. Betroffen ist allein der umgekehrte Fall — Chats, die **im** Team-Konto liegen. Für die trägt heute der Web-Weg, und nur er (Doku 1.2).

**Nicht geprüft wird der Organisationsexport.** Dafür bräuchte es Primary-Owner-Rechte; die zu erwerben wäre kein Prüfaufwand, sondern ein Eingriff in die Organisation. Und selbst mit ihnen bliebe das Verfahren für den laufenden Betrieb untauglich: Ein wiederkehrender Abgleich, der jedes Mal den Administrator braucht, ist keiner.

### Das Prüfprofil

Die neun Merkmale und ihre Rezepte stehen normativ in **Doku 4.1** — als Prüfvorlage, die sich nicht verbraucht. Drei Rezepte scheiterten im Erstlauf und sind dort korrigiert; welche und warum, steht unten bei 21.7.

**Beobachtung zur Gabelung:** Nach dem Bearbeiten der Frage kam eine neue Antwort, und die bisherige verschwand **im Web-Frontend**. Genau darum geht es bei Regel 2 in 3.1.2: Die Oberfläche zeigt den verworfenen Zweig nicht mehr, der Export soll ihn trotzdem führen. Damit hatte 21.7 eine scharfe Erwartung — `analyse` muss für Chat 1 einen Nebenzweig ausweisen.

**Langer und wachsender Chat sind derselbe** (Chat 6). Das ist zulässig und spart einen Chat: Ein wachsender Chat, der zugleich lang ist, macht das Ersetzen beim zweiten Export sogar aussagekräftiger.

## 21.3/21.4 Sondierungsexport — bestanden

ZIP vom 17. August 2026, Fenster vor dem Anlegen des Testprojekts. `inspect_export.py` berichtet:

- **Konversationen: 1**, erstellt am 2026-08-15 — aus einem anderen Projekt. **Kein einziger Chat des Testprojekts** ist enthalten; das Fenster schloss sie korrekt aus.
- **44 Projektdateien**, darunter „Chats-Export aus Pro, Test 1" mit `created_at` **2026-08-17** — also mit einem Datum **außerhalb und nach** dem gewählten Fenster.

**Damit ist die Behauptung geprüft, auf der Schritt 0 aus 1.5 ruht:** Projektdateien sind vom Zeitraumfilter ausgenommen. Und zwar gegen einen bekannten Sollwert — der Nutzer hatte das Anlegedatum unabhängig notiert, das Werkzeug liest genau dieses Datum aus einem Archiv, das den Chat des Projekts gar nicht kennt. Vorher waren es 43 Projektdateien, jetzt 44; die eine mehr ist unser Testprojekt.

Der Sondierungsexport selbst ist inzwischen der Rückfall: Der Projekt-Endpunkt des Web-Wegs liefert `created_at` je Projekt direkt. Die geprüfte Eigenschaft trägt weiter — sie ist der Grund, warum ein Export für ein Konto ohne Browser-Anbindung überhaupt eine Fenstergrenze hergibt.

**Schemawache:** Konversationsschlüssel und Nachrichtenschlüssel decken sich mit 3.1.1, und `project reference: NONE` bestätigt erneut den Befund, der den ganzen Entwurf trägt. `login_history.json` ist vorhanden. Die **Blockschlüssel** gab die Wache ebenfalls aus, ohne dass 3.1.1 dafür eine Vergleichsgrundlage hatte — geschlossen mit 21.7, s. u.

## 21.5 Chatliste — bestanden

### Wie der Befund zum laufenden Chat entstand

Erster Versuch, gestellt im **ersten** Chat des Projekts: ein **leerer** Codeblock. Die Form stimmte — Codeblock, kein Kommentar, kein Text davor oder danach —, `MAPPING_PROMPT` tut also, was er soll; leer war nur der Inhalt.

Zweiter Versuch, gestellt in einem **zweiten** Chat: genau ein Eintrag, nämlich der erste Chat, mit UUID-förmiger ID und `updated_at`. Damit ist bewiesen, was zu beweisen war — das Projekt ist für `recent_chats` erreichbar, es ist ein gewöhnliches claude.ai-Projekt, und die Rohform passt zu `parse_chat_list`.

Zwei Erklärungen passten gleich gut: Entweder listet `recent_chats` den laufenden Chat grundsätzlich nicht mit, oder ein frisch angelegter Chat ist noch nicht indiziert. Dritter Versuch, gestellt wieder im **ersten** Chat: genau ein Eintrag, nämlich der **zweite** Chat. Aus Chat 1 kommt Chat 2, aus Chat 2 kam Chat 1 — beide inzwischen indiziert, jeder sieht den anderen, keiner sich selbst.

**Beobachtet, nirgends dokumentiert: `recent_chats` listet den laufenden Chat nicht mit.** Zwei symmetrische Beobachtungen, die Indizierungs-Erklärung ist damit widerlegt.

**Die Folge wiegt schwer.** Jeder Listenlauf übergeht genau den Chat, aus dem er gestartet wurde. Das Protokoll erfährt nie von ihm, also fehlt er im Archiv — und `diff` kann ihn nicht als fehlend melden, weil das Protokoll ihn gar nicht kennt. Es ist ein Zuwenig, das keine der eingebauten Kontrollen bemerkt: Der Waisen-Scan meldet nur ein Zuviel.

**Gegenmittel ohne Code, vom Nutzer vorgeschlagen und übernommen:** die Liste in einem **eigens dafür angelegten Chat** holen und diesen **danach löschen**. Dann bleibt gar nichts zurück — der fehlende Chat ist der, der nichts enthielt als den Listenabzug, und im Projekt sammeln sich keine Karteileichen. Der zuerst erwogene Weg, immer denselben Abfragechat zu verwenden, ist schlechter: Er ließe die Karteileiche liegen und würde beim nächsten Lauf selbst mitarchiviert.

Nötig ist das nur noch dort, wo die Chatliste aus claude.ai kommt — bei `list --map`. Der Web-Weg holt sie am Endpunkt und hat die Lücke nicht.

### Der Lauf selbst

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

**Befund, neu:** Ein **gelöschter** Chat erscheint nicht mehr in `recent_chats`. Im Export tauchen gelöschte Chats als Hüllen auf (3.1.3) — in der Liste gar nicht. Wer also nur die Liste kennt, erfährt von ihnen nichts; wer nur den Export kennt, sieht sie als leere Gerüste.

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

Doku 1.6 sagte über die 524 `files`-Einträge des Drei-Monats-Exports: „und **die** sind wirklich verloren." Das ist so nicht haltbar — ein unbekannter Teil davon sind Zweitnennungen von Dateien, deren Inhalt sehr wohl mitkam.

### Befund 3: Daraus ein Defekt im Code

`file_names()` nahm jeden `files`-Eintrag als Verlust, ohne zu prüfen, ob dieselbe Nachricht die Datei bereits mit Inhalt führt. Folge: `report` meldete `test_docstrings.py` als „mentioned by name only", obwohl der Inhalt in der Anhangsdatei liegt, und das Metadatenfeld `attachments_without_content` überzeichnete den Verlust. Behoben, mit Auswirkung auf 1.6 und die dortigen Zahlen.

### Die Blockschlüssel liegen jetzt vor

Der Export trägt alle Blocktypen außer `token_budget` (erwartbar, 1.6). Die Schlüsselmenge umfasst 37 Namen, darunter viele, die 3.1.1 nicht kannte — `structured_content`, `display_content`, `tool_origin`, `is_mcp_app`, `mcp_server_url`, `approval_options` und weitere. Damit ist die Vergleichsgrundlage vorhanden, die 3.3 verspricht.

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

**Befund: Der Export-Weg meldete verschwundene Chats nicht.** Weder `list` noch `diff` erwähnte, dass „Brillenstärken verstehen" aus der Quelle verschwunden ist; `diff` zählte ihn unter „4 exported", als wäre alles in Ordnung. Dieselbe Sorte Asymmetrie wie zuvor bei `analyse` gegen `report` — ein Konzept, das nur auf einer Seite gepflegt wurde. Behoben.

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

**Was kippt, ist eine tragende Aussage der Doku.** 1.2 begründete „der Export ist der inhaltlich reichere Weg" wesentlich mit den Denkschritten — 9,2 Mio Zeichen, etwa so viel wie der Gesprächstext. Für **neue** Chats trifft das nicht mehr zu: Es bleiben Anhänge und Erzeugnisse.

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

Aufbau: ein Wegwerfordner `~/zielprojekt-test/` **außerhalb** dieses Repos — bewusst außerhalb, weil Claude Code `CLAUDE.md`-Dateien den Verzeichnisbaum hinauf einsammelt und ein Ordner innerhalb des Repos unsere Projektanweisungen mitgeladen hätte; die Instanz hätte dann von diesem Vorhaben gewusst. Darin `.claude/imported_chats/chat-export-aus-pro-test-1/` mit den zwölf Archivdateien und eine `CLAUDE.md`, die **nur** den Anweisungsblock enthält, sonst nichts. Der Versuch lief in einer frischen Sitzung, die von diesem Vorhaben nichts weiß.

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

**Das bestätigt eine Entwurfsentscheidung, die auch anders hätte ausfallen können.** Doku 1.4 begründet das Protokoll damit, dass eine Instanz zwar eine kleine Datei lesen, aber nicht N Chatdateien durchzählen kann. Der Versuch schärft das: Sie kann nicht einmal die Einträge **einer** kleinen Datei verlässlich zählen. Gefährlich wird das nicht, weil der Entwurf es nie verlangt — die Zählungen rechnet das **Skript**, das die JSON parst; die Instanz führt es nur aus. Hätte man stattdessen darauf gesetzt, dass die Instanz das Protokoll „einfach liest und weiß, was fehlt", stünde hier jetzt ein stiller Fehler.

## 21.12 erste Hälfte: die fremde Instanz allein am Docstring — bestanden

Skript und Protokoll in einen neuen Chat des Quellprojekts, dazu ein Prompt ohne jede Erklärung: „Im Anhang ein Skript und eine Protokolldatei. Der Docstring des Skripts ist die Arbeitsanweisung. Fang an." Alles Weitere kam von der Instanz — Upload-Probe mit Kopie statt Arbeit in place, `plan` vor jedem Lesen, frische Chatliste selbst geholt, der verschwundene Chat als Befund samt aller drei möglichen Ursachen, Optionen mit Preis statt einer Entscheidung für den Nutzer, und kein erfundener Umfang, wo keiner bekannt ist. Auf die Bitte, zwei bestimmte Chats zu lesen, hat sie **nicht** gehorcht, sondern nachgefragt: beide seien laut Protokoll vollständig `exported`, ein erneutes Lesen also unnötig.

**Was davon heute trägt:** die Zusage aus Vorgabe 2.9 — eine Instanz, die von diesem Vorhaben nichts weiß, leitet den ganzen Ablauf aus dem Docstring her, einschließlich der Stellen, die ihr Zurückhaltung vorschreiben. Darauf ruht heute die `SKILL.md`. Das damals geprüfte Skript selbst ist nicht mehr lauffähig (s. u.), das Szenario „Instanz führt ein hochgeladenes Skript aus" braucht der Entwurf nicht mehr — deshalb steht der Lauf hier nur noch in dieser Kurzform.

## `read_conversation` — war da, ist weg

**Belegt genutzt am 6. August 2026.** Eine claude.ai-Instanz zitierte die Werkzeugbeschreibung wörtlich, erklärte die Verkettung mit `page_token` und lieferte eine echte Ausgabe für den FreeCAD-Chat `d64eea15` mit `total_turns="58"` und `updated_at="2025-11-13T22:07:44.559082+00:00"`. Ein Export-ZIP, das viereinhalb Stunden später eintraf, bestätigte beide Werte — die Turn-Zahl und den Zeitstempel bis auf die Mikrosekunde. Erfunden sein kann das nicht.

**Am 18. August 2026 nicht mehr vorhanden**, in vier Anläufen über zwei Konten (Pro und Team), zwei Oberflächen und mehrere Modelle, mit auf „alle laden" gestelltem Tool-Zugriffsmodus. Warum — entfernt, umbenannt, anders freigeschaltet — bleibt offen und ist für die Folgen gleichgültig.

**Zwei Proben davor taugten nicht**, und die Lehre daraus gilt weiter: Wir haben zuerst nach dem Werkzeugsatz **gefragt** statt ein Werkzeug **benutzen** zu lassen, und danach eine Frage gestellt, deren Antwort auch im Projektwissen stand. Eine Probe taugt nur, wenn **allein** das geprüfte Werkzeug die Antwort hervorbringen kann.

**Was daran hing.** `chat_read_store.py` ist nicht lauffähig; es liegt bei den Tests, die es allein noch anfassen. Fahrplanpunkt 23 — arbeitet der Lese-Weg in einem Team-Projekt? — ist damit gestrichen; für Team-Konten trägt der Web-Weg. Und 21.13, die Wegegleichheit an echten Daten, ist durch den Vergleich ZIP gegen Web-Behälter ersetzt und dort schärfer belegt. Die gekippte Annahme steht in Doku 1.7.

**Ein Befund aus diesen Läufen, der bleibt:** `conversation_search` liefert bei einem Chat mit zwei Turns den vollständigen Wortlaut, bei einem mit zehn Turns eine **Zusammenfassung**. Die fremde Instanz hat den fast passenden Treffer deshalb **verworfen** — das sei „Glück des kurzen Chats, keine verlässliche, vollständige, paginierte Quelle", und Schnipsel zu verarbeiten hieße „genau die Sorte beschädigter/erfundener Transkripte erzeugen, vor der der Docstring ausdrücklich warnt". Vorgabe 2.8 ist damit an der schärfsten denkbaren Stelle bestätigt: Eine Quelle, die *fast* gepasst hätte, wurde verworfen, statt ein plausibles Ergebnis zu erzeugen. Die Folge für den Crawler entscheidet Fahrplan 10 (Doku 3.4, 4.3).

**Zwei Umgebungsfakten nebenbei**, sonst nirgends festgehalten: Chat-Anhänge liegen im Container unter `/mnt/user-data/uploads` — bisher nur Community-Vermutung, damit **beobachtet** (Vorgabe 2.1) —, Projektwissen unter `/mnt/project/`.

## Der Web-Weg: wie er gefunden wurde

Bei der Suche nach Spuren zu `read_conversation` aufgetaucht: eine Community-Skill (`getclaudeskills.com`, „Read Claude.ai Web Conversation") liest vollständige Transkripte, indem sie JavaScript in der angemeldeten Browsersitzung ausführt und dort die internen Endpunkte der Weboberfläche anspricht. Nachgeprüft an zwei eigenen HAR-Mitschnitten (Firefox, Netzwerkansicht) über die Projekt-Chatliste und fünf gezielt gewählte Chats; ausgewertet wurden nur Pfade, Parameter- und Schlüsselnamen.

**Was die Mitschnitte zeigten** — durchweg bestätigt und schärfer nachgemessen in Punkt 26, s. u.: Der Baum kommt vollständig (`tree=True`), Anhänge kommen mit `extracted_content`, `tool_use` und `tool_result` sind da, Denkschritte tragen Text, wo der Export ihn auch trägt, und es gibt keine Paginierung je Chat. Dazu drei Felder, die dieses Vorhaben mühsam ersetzt hatte: **`project_uuid`** je Chat (die dem Kontoexport fehlende Projektzugehörigkeit), **`created_at`** je Chat (Grundlage der Fensterrechnung aus Vorgabe 2.4) und **`model`**, `effective_thinking_mode` und `effort_level` — genau die Angaben, die beim Denkschritte-Befund fehlten, um die Ursache zu bestimmen.

Die beiden HAR-Mitschnitte sind gelöscht. Sie enthielten Sitzungs-Cookies und den Wortlaut von fünf Chats; für eine Wiederholung genügt ein neuer Mitschnitt.

Die Wegewahl, die daraus folgte — Kontoexport als Anker, Web-Weg für kleine Nachträge und als einziger Weg für Team-Konten, Abrufbremse, ein Behälter und ein Download — steht normativ in Doku 1.2, 1.5 und 3.5. Die Herleitung stand hier und ist entbehrlich geworden.

## Fahrplanpunkt 26: die Probe über Chrome — bestanden, in allen drei Schritten

Am 19. August 2026 auf dem Rechner `xps`, im Pro-Konto, über die Chrome-Anbindung von Claude Code. In VS Code heißt der Schalter **`@browser`** im Eingabefeld, nicht `/chrome`; das Kommando gibt es dort nicht. Der Nutzer stößt damit jeden Schritt an, die Werkzeuge kommen pro Nachricht dazu.

**Der Zugriff funktioniert, und zwar auf zwei Wegen.** Ein Tab, den man direkt auf einen API-Pfad navigiert, liefert das JSON als Seitentext. Und aus einer geöffneten claude.ai-Seite heraus arbeitet `fetch` gleichursprünglich gegen dieselben Pfade — Status 200, ohne Navigation. Der zweite Weg ist der, den ein Skript ginge.

**Die Mengenfrage ist beantwortet, und großzügiger als erwartet.** Der längste Chat des Archivs kam mit **607.083 Zeichen in einer einzigen Antwort** und ließ sich vollständig parsen — nicht 124 KB, sondern rund 593. Keine Paginierung, keine Kürzung. Die Sorge, ein Werkzeug für Seitentext könne die Antwort abschneiden, hat sich nicht bestätigt.

**Kein Captcha, keine Cloudflare-Prüfung** bei diesen wenigen Abrufen.

### Was die Endpunkte liefern

Drei statt der zwei bekannten. Die Organisations-UUID braucht dafür **keinen Mitschnitt**: Sie steht im Dateinamen jedes Export-ZIP (`data-<org>-…-batch-0000.zip`) und ließ sich gegen die Netzwerkansicht bestätigen.

| Endpunkt | liefert |
| --- | --- |
| `/api/organizations/<org>/projects` | alle Projekte mit `uuid`, `name`, `description`, **`created_at`**, `updated_at`, `is_private` |
| `…/projects/<projekt>/conversations_v2?limit&offset` | je Chat `uuid`, `name`, `summary`, **`model`**, **`created_at`**, `updated_at`, **`project_uuid`**, `effective_thinking_mode`, `current_leaf_message_uuid`; Hülle aus `data` und `pagination` |
| `…/chat_conversations/<chat>?tree&rendering_mode&render_all_tools` | Kopfdaten plus `chat_messages` mit `content`-Blöcken, `sender`, `parent_message_uuid`, `attachments`, `files` |

**Die Paginierung muss nicht geraten werden.** Der Listen-Endpunkt gibt ein `pagination`-Objekt mit `has_more`, `limit`, `offset` und `total` zurück. Die Vermutung, man erkenne das Ende daran, dass eine Seite weniger als `limit` liefert, ist damit überholt — es steht ausdrücklich da.

### Gegen bekannte Werte geprüft

Nicht auf Plausibilität, sondern gegen Sollwerte, die vorher feststanden:

| Prüfung | Sollwert | Ergebnis |
| --- | --- | --- |
| `created_at` des FreeCAD-Projekts | 2025-11-10 (Doku 3.1.1) | **2025-11-10T18:46:28** |
| `created_at` des Testprojekts | 2026-08-17 | **2026-08-17T14:07:28** |
| `updated_at` von `d64eea15` | 2025-11-13T22:07:44.559082 aus dem `read_conversation`-Envelope vom 6. August | **2025-11-13T22:07** |
| Anhang in `1d322d54` | `test_docstrings.py`, 4.481 Zeichen `extracted_content` | **zeichengenau gleich** |
| das Bild im selben Chat | nur `files`, ohne Inhalt | **bestätigt** |
| ältester Chat des FreeCAD-Projekts | nicht älter als das Projekt | 2025-11-10, **gleich dem Projektbeginn** |

**Der Denktext fehlt auch hier**, wo er im Export fehlt, und ist da, wo er im Export da ist — der Wegfall ist also keine Eigenschaft des Exports, sondern der Plattform. Das bestätigt den Befund aus 21.11 an einer zweiten Quelle.

### Die Dreifachprobe am längsten Chat

Sie war als Mengentest gedacht und wurde nebenbei zur schärfsten Übereinstimmungsprüfung des ganzen Vorhabens. Für `2bb99eef` „Technical drawings from FreeCAD parts":

- **Web-API:** 187 Nachrichten, 95 human, 92 assistant, alle mit `parent_message_uuid`.
- **Export-ZIP, roh nachgezählt:** 187 Nachrichten, 95 human, 92 assistant, 2 Gabelungen mit 2 und 4 Kindern.
- **Unser heutiger Konverter:** 142 auf dem gewählten Pfad **plus 45 in 4 Nebenzweigen** — zusammen 187.

Drei unabhängige Quellen, dieselbe Zahl. Die Regeln aus 3.1.2 greifen also an echten Daten, und die Integritätszusage aus 3.1.7 hält auch hier.

**Ein Nebenbefund daraus:** Das auf der Platte liegende FreeCAD-Archiv führt für diesen Chat nur die 142 und meldet **keine** Nebenzweige. Es stammt aus der Zeit vor der Nebenzweig-Funktion. Kein Defekt, aber ein veralteter Bestand — wer ihn als Sollwert nimmt, vergleicht gegen einen alten Stand.

### Zwei Funde, die über die Probe hinausreichen

**Der Sondierungsexport wird gegenstandslos**, wo der Web-Weg zur Verfügung steht. Der Projekt-Endpunkt liefert jedes Projekt mit `created_at` — genau das, wofür 1.5 Schritt 0 einen eigenen Export anfordert. Zusammen mit `created_at` und `project_uuid` je Chat entfallen damit auch die Fensterrechnung als Notbehelf und die Chatliste als einzige Zuordnungsquelle.

**Fahrplanpunkt 24 ist faktisch beantwortet.** Der Listen-Endpunkt zeigt für das FreeCAD-Projekt **23** Chats, unser Protokoll führt **22**. Genau die stille Lücke, die der Befund zum laufenden Chat vorhergesagt hat. Welcher Chat es ist, steht noch aus und kostet einen lokalen Vergleich.

### Der Weg auf die Platte — geprüft, einschließlich des Härtefalls

Noch am selben Tag nachgezogen. Das Verfahren: Ein Tab auf `claude.ai`, von dort `fetch` je Chat, alles in **ein** Objekt, daraus ein Blob, eine Objekt-URL und ein angeklickter Link mit `download`-Attribut. Chrome legt die Datei im Download-Ordner ab, ein lokales Skript nimmt sie auf. Weder Erweiterung noch eingespritztes Fremdskript nötig — `javascript_tool` der Chrome-Anbindung genügt.

**Zwei kurze Chats, ein Download:** 12.051 Zeichen erzeugt, 12.199 Bytes auf der Platte, gültiges JSON, beide Chats vollständig mit gesetztem `parent_message_uuid`. Die Abrufbremse lief mit, gemessene Wartezeit 5,4 s. **Kein Dialog** — die Anbindung blieb ansprechbar.

**Der Härtefall, derselbe Weg:** `2bb99eef` mit 607.083 Zeichen Antwort, Abrufdauer **953 ms**, 619.023 Bytes auf der Platte. Vollständig.

**Und daraus die schärfste Gegenprobe des ganzen Vorhabens.** Die heruntergeladene Datei gegen dasselbe Gespräch im Export-ZIP gehalten:

| | Nachrichten | human / assistant | Gabelungen |
| --- | --- | --- | --- |
| Web-API-Download | 187 | 95 / 92 | 2 und 4 Kinder |
| Export-ZIP | 187 | 95 / 92 | 2 und 4 Kinder |

**Die Mengen der Nachrichten-UUIDs sind identisch** — null Nachrichten nur in der einen, null nur in der anderen Quelle. Nicht bloß gleiche Zahlen, sondern dieselben Nachrichten. Die Wegegleichheit (Vorgabe 2.5) ist damit an der Quelle belegt, bevor überhaupt ein Konverter läuft.

**Nebenbefund zum kurzen Chat:** `128aa097` liefert 4 Nachrichten (2 human), unser Archiv führt 2. Der Unterschied ist der Nebenzweig aus der nachträglich geänderten Frage — genau das, was beim Anlegen des Prüfstücks vermerkt wurde. Kein Fehler, sondern der Baum.

**Was damit offen bleibt:** nichts Technisches mehr an diesem Weg.

## Wie die Chrome-Brücke funktioniert — Gesamtergebnis

Über zwei Tage (20./21. August 2026) systematisch geprüft, mit vielen Anläufen und Fehlversuchen, die hier nicht mehr im Einzelnen stehen — sie waren zeitweise selbst von Verbindungsproblemen zwischen dieser Sitzung und der Erweiterung überlagert, deren Ursache nicht gefunden wurde. Der vollständige Testweg liegt in `chrome-zugriff.md`; hier nur das Ergebnis.

**Der Aufbau, belegt** ([chrome](https://code.claude.com/docs/en/chrome)). Claude Code spricht nicht selbst mit Chrome, sondern über die **Erweiterung** „Claude in Chrome" und einen **Native-Messaging-Host** — eine Konfigurationsdatei, über die Chrome einem lokalen Programm erlaubt, mit einer Erweiterung zu reden. Claude Code bietet die Browserwerkzeuge als MCP-Server `claude-in-chrome` an. Die Erweiterung öffnet eigene Tabs und *„shares your browser's login state"*.

**Was tatsächlich zählt, am Ende auf drei Punkte reduziert:**

1. **Jede Nachricht, die den Browser braucht, beginnt mit `@browser`.** In der VS-Code-Erweiterung gibt es `/chrome` nicht; die Werkzeuge stehen zwar auch ohne `@browser` in der Liste, antworten dann aber „Browser extension is not connected" — das klingt nach kaputtem Aufbau, heißt aber nur, dass diese eine Nachricht die Anbindung nicht angefordert hat.
2. **Chrome muss laufen und bei claude.ai angemeldet sein**, mit eingeschaltetem Connector-Schalter für das jeweilige Konto (Einstellungen → Connectors → „Claude in Chrome"). Ohne das: `"Claude in Chrome is turned off in your settings"`. Die Einstellung wirkt nicht rückwirkend auf schon offene Tabs.
3. **Die Erweiterung selbst muss angemeldet sein** — das ist von der claude.ai-Websitzung im Tab getrennt. Erkennbar am funktionierenden Chat-Turn direkt in der Erweiterung.

**Ist das erfüllt, funktioniert `@browser` zuverlässig — und zwar unabhängig vom Konto.** Zwei Ebenen sind dabei sauber getrennt und geprüft: Die **Bridge** (Chrome ↔ Claude Code) blieb auch nach Abmelden von claude.ai voll funktionsfähig auf fremden Domains (gmx.de, example.com); nur der claude.ai-eigene API-Aufruf braucht dafür zusätzlich eine gültige **Websitzung** im Tab. Und die **Kontofrage ist geklärt**: Ein sauberer Test nach vollständigem Rechner-Neustart zeigte, dass die Bridge sich auch aufbaut, wenn Chrome von Anfang an mit einem *anderen* Konto bei claude.ai angemeldet ist (Team) als die Claude-Code-Sitzung selbst (Pro) — eine Kontoübereinstimmung ist **nicht** erforderlich.

**Folge für den Skill:** Er darf sich nicht darauf verlassen, dass Chrome dasselbe Konto verwendet wie die Claude-Code-Sitzung — er muss das erkannte Konto nennen, nicht voraussetzen (so schon in der Zielvorlage, Abschnitt 2.3). Und seine Voraussetzungen sind die drei Punkte oben, nicht „Erweiterung installiert" allein — das gehört in seine README.

## Aufgeräumt und was zum Rechnerwechsel gilt

Der Wegwerf-Ordner `~/zielprojekt-test/` ist nach bestandener Prüfung gelöscht; alle zwölf Dateien darin waren inhaltsgleiche Kopien aus `tests/test_results/pro-test-1/` und wurden vor dem Löschen einzeln dagegen verglichen. Wer 21.8 wiederholen will, baut ihn in zwei Minuten neu auf — Ordner, `.claude/imported_chats/<quellprojekt>/`, und die `CLAUDE.md` mit dem Block aus `convert --target repo`.

`tests/test_results/` ist gitignoriert und **wandert nicht mit dem Repo**; die älteren ZIPs und das FreeCAD-Archiv liegen auf dem Laptop. Daraus die Einschränkung, die in Doku 4.1 und im Fahrplan-Kopf steht: *kalt* heißt ohne Konto und ohne Netz, aber nicht ohne Voraussetzung — dieselbe kalte Prüfung ist auf dem einen Rechner lauffähig und auf dem anderen nicht. **Fahrplanpunkt 24** bleibt ausführbar; er braucht nur `freecad/protokoll.json` mit den 22 Chats, nicht das Archiv und nicht die ZIPs.
