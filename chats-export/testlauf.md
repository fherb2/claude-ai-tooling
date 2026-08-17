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

## Profil-Checkliste (Doku 4.1)

| Merkmal | Stand |
| --- | --- |
| Gabelung | offen |
| Sendewiederholung | offen |
| Anhang mit Inhalt | offen |
| reiner Namensverweis | offen |
| Denkschritte | offen |
| Erzeugnis | offen |
| Hülle | offen |
| langer Chat | offen |
| wachsender Chat | offen |

Der wachsende Chat wird in 21.2 nur **angelegt**; fortgesetzt wird er in 21.9, nach einem Tageswechsel.

## Beobachtungen je Schritt

### 21.2 Testprojekt anlegen und füllen

Am 17. August 2026 angelegt, Angaben oben; in claude.ai sichtbar. Füllen steht aus, zuerst die Erreichbarkeitsprobe über die Chatliste.
