# Befunde der logischen Prüfung — chat-export

**Erstellt:** 2026-08-22. **Auftrag:** Prüfung des Bereichs `chat-export/` auf Fehler, die eine Fehlfunktion gegenüber dem angestrebten Ziel hervorrufen würden, sortiert nach Schweregrad. Ausdrücklich **nicht** Gegenstand: Qualität und Lücken der Dokumentation.

**Vorgehen:** Implementierungsdoku (einschließlich Segment 2) und beide READMEs vollständig gelesen; `chat_export_convert.py`, `inspect_export.py`, `wegegleichheit_referenz.py` und alle vier Testdateien vollständig gelesen; alle vier Testsuiten ausgeführt, mit und ohne `-O` — **alle grün**. Drei Verdachtsfälle wurden experimentell im Scratchpad nachgestellt (Befunde 1, 2, 7), zwei Randfall-Häufigkeiten an den echten Export-ZIPs unter `tests/test_results/` gemessen (10.779 Nachrichten). Am Bereich wurde nichts geändert; einzige neue Datei ist diese.

**Schweregrade:** *Hoch* = verfälscht Archivinhalt oder verliert Inhalt im Regelbetrieb. *Mittel* = Fehlfunktion in plausiblen Randfällen oder Zustandsverfälschung, die still bleibt oder sich erst spät korrigiert. *Niedrig* = irreführende Ausgaben, tote Pfade, latente Robustheitslücken ohne heutige Fehlfunktion. *Kleinkram* = am Ende in einem Zug erledigbar.

**Kein Befund der Stufe Hoch.** Die Kernpfade — Baumlauf, Dublettenerkennung, Nebendateien, Ersetzen mit Aufräumen, Wegegleichheit ZIP/Bundle, Fensterrechnung — halten dem Quervergleich Code gegen Doku stand und sind durch die Suiten wirksam abgedeckt.

---

## Mittel

### Befund 1: Falsch-positive Hüllen-Erkennung sperrt einen lebenden Chat dauerhaft von Aktualisierungen aus

`conversation_record()` erklärt jeden Chat mit Nachrichten, aber ohne gerenderten Text zur Hülle (`deleted: true`) — Anhänge mit Inhalt werden dabei nicht als Lebenszeichen gewertet ([chat_export_convert.py:719](skills/chat-export/chat_export_convert.py#L719)). Experimentell nachgestellt: Ein Chat aus einer Upload-Nachricht ohne Begleittext plus einer leeren (fehlgeschlagenen) Antwort wird als gelöscht archiviert, obwohl sein Anhang Inhalt trägt; die Metadaten melden zugleich `deleted: true` und `attachments_with_content: 1`, und die `.attachments.json` wird für einen angeblich gelöschten Chat geschrieben.

Folgeschaden, und der wiegt schwerer als die Fehlklassifikation selbst: Der Protokollstatus wird `deleted`, und `update_from_list()` befördert nur `exported`-Einträge nach `stale` ([chat_export_convert.py:983](skills/chat-export/chat_export_convert.py#L983)). Wächst der fälschlich für gelöscht erklärte Chat später an der Quelle weiter, wird er **nie wieder geholt** — still und dauerhaft, kein Kommando meldet es.

Plausibilität am echten Bestand: 22 von 10.779 Nachrichten in den vorliegenden Export-ZIPs haben keinen gerenderten Text, aber einen Anhang mit Inhalt. Die Zutat ist also real; es braucht nur einen Chat, der ausschließlich aus solchen Nachrichten besteht. Die 15 echten Hüllen in den ZIPs tragen erwartungsgemäß keine Anhänge — ein Anhang mit `extracted_content` wäre demnach ein brauchbares strukturelles Gegenindiz zur Hüllen-These.

### Befund 2: `convert` setzt einen stale-Chat auf `exported` zurück, auch wenn die gelieferte Quelle älter ist als der gelistete Stand

`cmd_convert()` setzt nach dem Schreiben bedingungslos `status = exported` ([chat_export_convert.py:1360](skills/chat-export/chat_export_convert.py#L1360)), ohne zu prüfen, ob das `updated_at` der soeben verarbeiteten Quelle den Stand erreicht, dessentwegen der Chat `stale` war. Experimentell nachgestellt: Liste markiert einen gewachsenen Chat als `stale`; wird danach versehentlich das **alte** ZIP konvertiert (z. B. eine ältere Export-Datei im Download-Ordner — genau dort sucht der Skill die ZIP), steht der Chat wieder auf `exported`, `exported_updated_at` fällt auf den alten Stand zurück, und `diff` meldet: nichts offen.

Die Information, dass die Quelle neuer ist, liegt in diesem Moment im Protokoll (`listed_updated_at` > `exported_updated_at`), wird aber weder von `convert` noch von `diff` ausgewertet — erst der nächste `list`-Lauf stellt `stale` wieder her. Bis dahin behauptet das Werkzeug einen Abgleich, den es nicht geleistet hat.

### Befund 3: Die Statistik-Vorlage des Skills verlangt eine Zahl, die kein Skriptlauf liefert

Die Anweisungsdateien verbieten der Instanz jede eigene Zahl („Jede Zahl, die du nennst, stammt aus einem Skriptlauf", [SKILL.de.md:11](skills/chat-export/SKILL.de.md#L11), nochmals [SKILL.de.md:160](skills/chat-export/SKILL.de.md#L160)) — und geben zugleich eine Statistik-Tabelle mit der Spalte „Umfang … ~310 N." vor ([SKILL.de.md:64-67](skills/chat-export/SKILL.de.md#L64-L67), gleichlautend „Scope … ~310 msg." in [SKILL.en.md:64-67](skills/chat-export/SKILL.en.md#L64-L67)). Diese Zahl liefert nichts: Die Web-Chatliste trägt je Chat nur `uuid`, `name`, `created_at`, `updated_at`, `project_uuid`, `model` (so dokumentiert der Skill sie selbst), das Protokoll kennt `turns` erst **nach** der Konvertierung, und weder `list` noch `diff` geben einen Nachrichtenumfang aus.

Eine Instanz, die der Vorlage folgt, muss die Spalte also erfinden oder schätzen — genau der Verstoß, den dieselbe Datei zweimal verbietet — oder stillschweigend von der Vorlage abweichen. Die Anwender-READMEs führen die Tabelle übrigens **ohne** diese Spalte ([README.de.md:89-92](skills/chat-export/README.de.md#L89-L92)); der Widerspruch besteht nur in den SKILL-Dateien.

---

## Niedrig

### Befund 4: `created_after` ist nur exakt, wenn die vorherige Liste vollständig geblättert war — sonst rechnet das Fenster dauerhaft zu kurz, und die Ursache bleibt unsichtbar

Die Fensterrechnung stuft `created_after` als exakt ein („damals war das Projekt gelistet und der Chat nicht dabei, also entstand er später", Doku 2.4; Code in `update_from_list()`/`window_start()`). Diese Herleitung setzt voraus, dass jene frühere Liste vollständig war. Denselben Fall — „die Liste wurde nicht bis zum Ende geblättert" — führt das Vorhaben bei den verschwundenen Chats ausdrücklich als reale Bedienlage; für `created_after` ist er nicht abgefangen: Ein alter Chat, der in einer unvollständigen Liste fehlte und in der nächsten vollständigen erstmals auftaucht, bekommt einen viel zu späten `created_after`. Das Fenster wird zu kurz, der Export erfasst ihn nicht, `convert` meldet ihn zwar als fehlend („an export predating them" wird als Möglichkeit genannt) — aber `list`/`diff` nennen bei jedem weiteren Lauf unbeirrt dieselbe falsche Fenstergrenze, und `created_after` wird nie korrigiert („Wird nur beim ersten Sehen gesetzt und danach nie überschrieben"). Der Nutzer kann in eine Schleife aus immer gleichem, immer zu kurzem Export geraten. Betroffen nur der `--map`-Pfad und unvollständige Web-Listen; die Skill-geführte Web-Liste blättert deterministisch über `pagination`.

### Befund 5: Wachstumserkennung vergleicht Zeitstempel lexikalisch über gemischte Formate — heute zufällig unschädlich

Im echten Protokoll (`tests/test_results/pro-test-1/protokoll.json`) stehen für denselben Zeitpunkt zwei Schreibweisen nebeneinander: `listed_updated_at = …984103+00:00` (aus der Chatliste) gegen `exported_updated_at = …984103Z` (aus dem ZIP). Der `stale`-Vergleich ist ein roher Stringvergleich ([chat_export_convert.py:983](skills/chat-export/chat_export_convert.py#L983), ebenso [wegegleichheit_referenz.py:436-438](tests/wegegleichheit_referenz.py#L436-L438)). Dass der zeitgleiche Fall heute **nicht** als stale kippt, hängt allein daran, dass `+` in ASCII vor `Z` liegt. Zwei Driftrichtungen kippen das: liefert eine Quelle künftig `Z` in der Liste und `+00:00` im Export, wird jeder unveränderte Chat bei jedem `list` fälschlich stale (Dauerschleife „erneut holen"); kürzt eine Quelle die Präzision (Sekunden statt Mikrosekunden), kann Wachstum innerhalb derselben Sekunde still verpasst werden. Eine Normalisierung vor dem Vergleich würde beide Fälle schließen; mindestens gehört der Formatgleichlauf der Quellen als Prüfpunkt in Kapitel 4.

### Befund 6: `inspect_export.py` zählt „file references by name only (content NOT in the export)" ohne den Namens-Join und überzeichnet den Verlust um mehr als das Doppelte

Das Diagnosewerkzeug wirft inhaltslose `attachments` und **sämtliche** `files`-Einträge in einen Zähler ([inspect_export.py:161-168](inspect_export.py#L161-L168)) und beschriftet die Summe mit „content NOT in the export" ([inspect_export.py:180-181](inspect_export.py#L180-L181)). Das ist genau die Verwechslung, gegen die der Konverter mit dem Namens-Join in `file_references()` gebaut wurde: Am Drei-Monats-Export würde das Werkzeug 524 „Verluste" melden, wo nach eigener Messung 205 (nach Entdopplung 200) stehen. Der in Doku 4.2 als kalte Prüfung angekündigte „Anteil der `files`-Einträge mit Namenspartner" wird von keinem Werkzeug berechnet. Folge: Wer den Prüfpunkt 4.2 mit `inspect_export.py` abarbeitet, misst gegen die dokumentierten Zahlen aus 3.1.1 systematisch daneben und schlägt womöglich Alarm, wo nichts gekippt ist.

### Befund 7: Die Waisen-Warnung ist praktisch toter Code — Nachrichten mit fehlendem Elternteil werden kommentarlos zum Nebenzweig

Experimentell nachgestellt: Eine Nachricht, deren `parent_message_uuid` in der Konversation nicht vorkommt, wird von `split_branches()` als Zweigkopf eingesammelt ([chat_export_convert.py:600-611](skills/chat-export/chat_export_convert.py#L600-L611)); die `orphans`-Liste bleibt leer, die Warnung „hang from a parent that is not in this conversation and were not placed" ([chat_export_convert.py:677](skills/chat-export/chat_export_convert.py#L677)) feuert für genau diesen Fall nie. Erreichen kann sie nur ein Elternzyklus — für den ihr Wortlaut dann nicht stimmt. Inhaltlich geht nichts verloren (der Zweig wird mitgenommen, die Integritätsrechnung stimmt), deshalb nur Niedrig; aber ein korruptes Export-Gerüst würde ohne die zugesagte Meldung archiviert, und der Test „an orphan is either placed or reported" ([tests/test_export_convert.py:377-382](tests/test_export_convert.py#L377-L382)) verdeckt das durch sein Oder.

### Befund 8: Der Fallback auf das flache `text`-Feld existiert strukturell nur auf der ZIP-Seite

`message_text()` nimmt bei einer Nachricht ganz ohne `content`-Blöcke das flache `text`-Feld ([chat_export_convert.py:394-395](skills/chat-export/chat_export_convert.py#L394-L395)). Die Web-Form hat dieses Feld nicht — beobachtet und im Test festgehalten („no flat `text`", [tests/test_export_convert.py:1357-1364](tests/test_export_convert.py#L1357-L1364)). Träte eine solche Nachricht real auf, schrieben ZIP-Weg und Web-Weg für denselben Chat **verschiedene Transkripte** — der eine den Text, der andere leer —, was Vorgabe 2.5 gerade ausschließt; der Wegegleichheits-Vergleich in den Tests deckt den Fall nicht ab, weil alle Vergleichs-Fixtures Blöcke tragen. Gemessen an den echten ZIPs: 0 von 10.779 Nachrichten sind blocklos mit Text — heute also rein latent. Festgehalten, weil die Zusage „baulich gleich" an dieser einen Stelle von einem Feld abhängt, das nur eine Quelle hat.

---

## Kleinkram

Gesammelt zur Erledigung in einem Zug, je einzeln zu entscheiden:

- **Befund 9:** Bei Hüllen meldet `metadata.turns` die Länge des Skeletts, während `messages` leer geschrieben wird ([chat_export_convert.py:789](skills/chat-export/chat_export_convert.py#L789) gegen [807-808](skills/chat-export/chat_export_convert.py#L807-L808)) — die Felddefinition „Anzahl importierter Redebeiträge" (Vorgabe 2.2) sagt für diesen Fall etwas anderes.
- **Befund 10:** `load_protocol()`/`save_protocol()` überschreiben eine fremde, auch höhere `protocol_version` beim nächsten Speichern kommentarlos mit `1` ([chat_export_convert.py:931](skills/chat-export/chat_export_convert.py#L931)) — ein von einer neueren Werkzeugfassung geschriebenes Protokoll würde stillschweigend zurückgestempelt.
- **Befund 11:** `report` läuft über alle `*.json` des Verzeichnisses statt über die Protokolleinträge ([chat_export_convert.py:1485-1489](skills/chat-export/chat_export_convert.py#L1485-L1489)) — verwaiste Altdateien (die `diff` eigens meldet) zählen in den Summen mit, doppelt gegenüber der ersetzten Fassung.
- **Befund 12 — kein Befund** (geprüft am 22. August 2026, `befund_pruefung_2026-08-22.md`): `convert` meldet Chats, die in der Quelle liegen, aber nicht pending sind, mit keinem Wort. Beim ZIP ist das gewollt (fremde Projekte). Für das Bundle war die Annahme, ein Überschuss sei ein Fehlerindiz, weil die Chats gezielt für die pending-Liste geholt wurden — das trifft nicht zu: Ein Bundle darf bewusst alle Chats eines Projekts tragen, und `convert` nimmt daraus korrekt nur die wartenden. Kein Fehler, allenfalls ein möglicher Komfort.
- **Befund 13:** Die Dubletten-Erkennung vergleicht nur den Text ([chat_export_convert.py:604-605](skills/chat-export/chat_export_convert.py#L604-L605)) — ein Resend mit gleichem Text, aber abweichendem Anhang würde samt Anhang verworfen und nur gezählt. Konstruierter Fall, der Vollständigkeit halber notiert.
- **Befund 14:** `render()` dedupliziert Verlustverweise je Nachricht über das Label ([chat_export_convert.py:640](skills/chat-export/chat_export_convert.py#L640)) — zwei **verschiedene** namenlose Dateien gleichen Typs in einer Nachricht erscheinen als ein Eintrag „(ohne Namen, typ)", die Verlustzählung untertreibt dann um eins.

---

## Randnotiz außerhalb des Auftrags

Doku-Qualität war nicht zu prüfen; zwei Funde am Rande werden trotzdem genannt, weil sie Tatsachenbehauptungen betreffen, nicht Formulierungen — unbewertet, Entscheidung beim Entwickler:

- Die Skill-READMEs behaupten kategorisch, Anthropic schreibe Denkschritte „seit Ende Juli 2026 nicht mehr" aus und bei älteren Chats seien sie „vollständig vorhanden" ([README.de.md:192](skills/chat-export/README.de.md#L192), [README.en.md:193](skills/chat-export/README.en.md#L193)). Die eigene Messung (Doku 3.1.1) stellt dagegen fest, dass das Verhältnis „innerhalb eines einzigen Chats von Tag zu Tag" wechselte und die Ursache „nicht ermittelt" ist und „auch nicht vermutet" wird.
- Doku 1.4 nennt rechnende Kommandos „plan" und „overview", die das Skript nicht (mehr) hat; von den dreien existiert nur `map` (als `list --map`).
