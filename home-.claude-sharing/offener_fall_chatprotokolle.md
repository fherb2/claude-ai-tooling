# Offener Fall: Konflikte in Chat-Protokollen und ihre Verzweigungen

**Angelegt am 13. August 2026.** Dieser Fall ist **bewusst zurückgestellt**: Er kam während des laufenden Doku-Reviews auf, und es wurde entschieden, den Review zuerst abzuschließen. An der Implementierungsdoku und an allen anderen Dateien wurde deshalb **nichts** geändert — dieses Dokument ist die vollständige Zwischenablage, damit der Faden in einer neuen Sitzung ohne den Gesprächskontext von heute wieder aufgenommen werden kann.

Verweise auf die Implementierungsdoku stehen hier absichtlich als **Überschriftsnamen**, nicht als Kapitelnummern — die Nummern können sich im Review noch verschieben. Die F-Nummern des Fragenkatalogs sind dagegen stabil (dort wird nie umnummeriert).

---

## 1 Was beobachtet wurde

Der Nutzer arbeitete an Rechner **FWFE41** und hatte das Projekt zusätzlich am **Laptop** offen. Beide Rechner gleichen `~/.claude` über die Synology ab, auf beiden läuft der Konflikt-Wächter als Dienst.

Er hatte auf FWFE41 für eine Nebensächlichkeit **einen neuen Chat gestartet** und diesen anschließend **auch am Laptop geöffnet** — als Versuch, was dann passiert. Der Chat war inhaltlich belanglos und ist **inzwischen gelöscht**; der Fall ist daher **nicht mehr an diesem Chat nachvollziehbar**, wohl aber gezielt neu herstellbar (siehe Abschnitt 6).

**Beobachtung 1.** Mit dem Öffnen desselben Chats am zweiten Rechner wurde **sofort ein Konflikt gemeldet, auf beiden Rechnern**.

**Beobachtung 2.** Während der Konfliktlösung stellte sich heraus, dass **inzwischen weitere Konfliktkopien** zu demselben Konflikt entstanden waren — es blieb also nicht bei einer.

**Beobachtung 3.** Der Nutzer entschied, alle Kopien in einem Zug zu bearbeiten statt nacheinander. Die Konfliktsitzung stellte dabei fest, dass **das Gespräch inzwischen einen „Branch" hat**. Der Nutzer wies an, die zuletzt beschriebene Datei zu erhalten und die übrigen zu löschen; die Sitzung bestätigte, dass in der neuesten Datei auch tatsächlich die neuesten Zeilen enthalten seien, und löste den Konflikt genau so auf.

**Beobachtung 4 — der eigentliche Anlass dieses Falls.** Nach dem Schließen und erneuten Öffnen des Chats war **nur noch das Ende der Kommunikation vorhanden**. Der vordere Teil des Gesprächs fehlte.

**Wichtig für die Einordnung:** Der Wächter hat sich in diesem Vorgang korrekt verhalten — er hat erkannt, gemeldet und eskaliert, auf beiden Rechnern. Der Fall betrifft **nicht** den Wächter, sondern die **Auflösungsstrategie** für diesen Dateityp.

---

## 2 Was dokumentiert ist (Doku-Belege mit Quelle)

**Zwei verschiedene Dinge heißen „Verzweigung".** Nur eines davon erzeugt eine neue Datei.

**a) `/branch` und `--fork-session` — Kopie in eine neue Sitzung.** Aus [Manage sessions](https://code.claude.com/docs/en/sessions):

> „Branching creates a copy of the conversation so far and switches you into it, leaving the original intact."
>
> „Sessions created with `/branch` or `--fork-session` get their own session IDs and appear as separate rows."

Neue Sitzungs-ID, neue Datei, Original unverändert. Für den Abgleich der **unkritische** Fall: getrennte Dateien kollidieren nicht.

**b) Rewind — Verzweigung *innerhalb* einer Sitzung.** Aus [Checkpointing](https://code.claude.com/docs/en/checkpointing):

> „Run `/rewind`, or press Esc twice when the prompt input is empty, to open the rewind menu."
>
> „**Restore conversation**: rewind to that message while keeping current code."

Hier bleibt der alte Verlauf in derselben Datei, der neue hängt sich an denselben Punkt. Der Verlauf ist damit ein **Baum**.

**Ablageort und Format.** Aus [Manage sessions](https://code.claude.com/docs/en/sessions):

> „By default, Claude Code stores transcripts as JSONL at `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is your working directory path with non-alphanumeric characters replaced by `-`."
>
> „Each line is a JSON object for a message, tool use, or metadata entry. **The entry format is internal to Claude Code and changes between versions**, so scripts that parse these files directly can break on any release."

**Der Zwei-Terminal-Fall — dokumentiert, aber für *einen* Rechner.** Ebenfalls aus [Manage sessions](https://code.claude.com/docs/en/sessions):

> „If you resume the same session in two terminals without forking, messages from both interleave into one transcript."

Das gilt für zwei Terminals, die sich **eine** Datei teilen. Genau diese Voraussetzung fehlt im synchronisierten Betrieb (siehe Abschnitt 4).

---

## 3 Was am laufenden System gemessen wurde (13. August 2026, Laptop)

Erhoben wurde ausschließlich die **Struktur** der Sitzungsdateien unter `~/.claude/projects/` — Schlüsselnamen, Zeilenarten, Verweisstruktur. **Kein Gesprächsinhalt** wurde gelesen oder ausgegeben.

**Bestand:** 25 Sitzungsdateien.

**Struktur einer Zeile.** Vorhandene Schlüssel (Auswahl): `uuid`, `parentUuid`, `logicalParentUuid`, `leafUuid`, `timestamp`, `type`, `sessionId`, `isSidechain`, `isCompactSummary`, `isMeta`, `retryAttempt`, `maxRetries`, `gitBranch`, `cwd`, `version`. Zeilenarten in einer großen Datei: `assistant`, `user`, `attachment`, `file-history-snapshot`, `file-history-delta`, `queue-operation`, `ai-title`, `last-prompt`, `mode`, `system`.

**Die Datei ist ein Baum, nicht ein Strang.** `uuid` identifiziert die Zeile, `parentUuid` verweist auf die Vorgängerzeile. Eine **Gabelung** liegt vor, wenn zwei Zeilen denselben `parentUuid` tragen.

| Befund | Wert |
| --- | --- |
| Dateien mit mindestens einer Gabelung | **9 von 25** |
| Gabelungen in der größten Datei (6.532 Zeilen) | **23** |
| Dateien mit `parentUuid`, dessen Ziel in der Datei **fehlt** | **1 von 25** |

**Woher die Gabelungen kommen** — an den Kindknoten der 23 Gabelungen der größten Datei abgelesen:

| Anzahl | Kindarten | Ursache |
| --- | --- | --- |
| 12× | `assistant` + `user` | Der Nutzer schrieb, während die Antwort noch entstand (in der betreffenden Sitzung mehrfach vorgekommen) |
| 9× | `assistant` + `system`, mit `retryAttempt` | Wiederholung nach einem Fehler |
| 2× | `assistant` + `assistant` | zwei Antwortstränge an einem Punkt |

**Das ist der wichtigste Messbefund:** Verzweigungen entstehen im **Alltagsbetrieb**, nicht nur durch bewusstes Zurückspulen. Kein einziger dieser 23 Fälle geht auf ein `/rewind` zurück.

**Reproduzierbarkeit der Messung.** Die Zahlen lassen sich jederzeit neu erheben: alle `~/.claude/projects/*/*.jsonl` zeilenweise als JSON lesen, `uuid`-Menge und `parentUuid`-Häufigkeiten bilden; Gabelung = `parentUuid` mit mehr als einem Kind; fehlender Elternteil = `parentUuid`, der in der `uuid`-Menge nicht vorkommt.

---

## 4 Der zweite Fall (13. August, FWFE41): echt, nicht herbeigeführt, vollständig vermessen

Dieser Fall ist der wertvollere, weil ihn **niemand gestellt** hat. Hergang: Der Nutzer öffnete am Laptop das Projekt in VS Code, um den Git-Stand zu prüfen, pushte nach Anweisung und schloss VS Code wieder. Dabei wurde **dieselbe Arbeitssitzung** fortgesetzt, an der auf FWFE41 gerade weitergearbeitet wurde — die VS-Code-Erweiterung setzt beim Öffnen des Projekts die letzte Sitzung von selbst fort (siehe 7.2). Anschließend lag eine Konfliktkopie vor. Der Nutzer vertagte den Dialog auf »Später«; zum Zeitpunkt der Untersuchung schrieb also **niemand** mehr an der Kopie, und die laufende Sitzung war die auf FWFE41 selbst.

**Das Messergebnis** — die Konfliktkopie war das Protokoll der laufenden Arbeitssitzung, 18,8 MB:

| | Original (live) | Konfliktkopie |
| --- | --- | --- |
| Zeilen | 6.724 (wachsend) | 6.618 |
| Zeitraum der Einträge | 05.08. 23:47 – 13.08. **10:09** | 05.08. 23:47 – 13.08. **09:29** |
| `uuid`s, die die andere Datei nicht hat | 66 | **0** |
| `parentUuid` ohne Ziel | 0 | 0 |

**Die Kopie war ein exaktes Byte-Präfix:** Die ersten 6.618 Zeilen zeichengleich, das Original hatte lediglich mehr angefügt. Die Kopie enthielt **nichts**, was nicht auch im Original stand.

**Wie der Konflikt entstand.** Die Instanz am Laptop schrieb beim Öffnen in die Datei — aus ihrem *älteren* Kenntnisstand (bis 09:29), während FWFE41 schon bei 10:09 war. Beide Seiten hatten seit dem letzten gemeinsamen Stand geschrieben, und das genügt Syncthing für einen Konflikt, **auch wenn eine Seite inhaltlich nichts Neues beitrug**. Die Vermutung des Nutzers, dass eine Instanz beim Öffnen eines Chats schreibt, ist damit bestätigt.

**Die Auflösung.** Unmittelbar vor dem Löschen wurde die Enthaltensein-Eigenschaft erneut geprüft (das Original war inzwischen auf 6.742 Zeilen gewachsen, die 6.618 Zeilen der Kopie standen weiterhin zeichengleich am Anfang). Dann wurde **nur die Kopie gelöscht**, das Original nicht angetastet — deshalb war die Auflösung auch bei laufender Sitzung gefahrlos. Kein Verlust, keine verwaisten Verweise.

**Was der Wächter dabei im Produktivbetrieb leistete** (Journal und Zustandsdatei):

- Der Sicherheits-Suchlauf protokollierte den Fund im Viertelstundentakt (`[safety scan] 1 conflict(s)`) — die Journal-Zeile bewährt sich im Alltag.
- Um 12:27 erschien der Dialog erneut, dreißig Minuten nach der Vertagung, wie es die Episodenregel vorsieht.
- **Zenity endete dabei mit Rückgabewert 1 und schrieb `Gtk-CRITICAL`-Meldungen auf die Fehlerausgabe** (»GtkBox reports a minimum height of 257 …«) — ein **anderer** Wortlaut als der auf dem Laptop beobachtete. Die Einordnung anhand von Anzeigefehler-Merkmalen behandelte es korrekt als Vertagung. Eine Regel »Ausgabe heißt Fehler« hätte hier eine Nutzerentscheidung als Anzeigedefekt gelesen und nach fünf statt dreißig Minuten erneut gefragt.
- Nach dem Löschen der Kopie endete die Episode **von selbst** (`conflict_active` auf `false`) — das Löschereignis greift im Produktivbetrieb.

**Was dieser Fall für die Lösung bedeutet:** Nicht jeder Protokollkonflikt ist ein Datenverlust-Kandidat. Der bisher **einzige real beobachtete** Fall war der harmlose: eine Seite ist bloß älter. Ob das der Regelfall ist oder ein Zufall dieses Hergangs, ist offen — genau deshalb steht die Kaskade in 6.2 unter Vorbehalt.

## 5 Schlussfolgerungen

Klar getrennt: Was hier steht, ist **Folgerung**, nicht Beleg.

**5.1 Warum überhaupt ein Konflikt entstand.** Die Dokumentation beschreibt für zwei Terminals eine Verschränkung in *eine* Datei. Im synchronisierten Betrieb gibt es aber **zwei** Dateien: Jeder Rechner hängt an seine eigene Kopie an, die Versionsvektoren laufen auseinander, Syncthing legt eine Konfliktkopie an. Es verschränkt sich nichts. Das erklärt **Beobachtung 1** vollständig.

**5.2 Warum es mehrere Kopien wurden.** Solange beide Seiten weiter anhängen, wiederholt sich der Vorgang bei jeder neuen Divergenz. Das erklärt **Beobachtung 2**.

**5.3 Warum „die neueste Datei behalten" den Verlauf zerlegt hat.** Hier liegt der Kern. Bei gewöhnlichen Textdateien ist eine Konfliktkopie „dieselbe Datei, anders geändert" — Auswählen ist dann eine sinnvolle Entscheidung. Ein anfügendes Baumprotokoll ist etwas anderes: **Jede Kopie enthält eine andere Teilmenge derselben Knotenmenge.**

Wer eine Kopie wählt, verwirft damit Knoten. War unter den verworfenen ein **Elternknoten**, hängen die überlebenden Kinder in der Luft: Ihr `parentUuid` zeigt auf etwas, das die Datei nicht mehr enthält. Darstellbar bleibt dann nur die Teilkette, deren Vorfahren vollständig vorhanden sind — **also genau „nur das Ende der Kommunikation"**. Das erklärt **Beobachtung 4**.

Dass dieser Zustand nicht theoretisch ist, zeigt die Messung: Eine der 25 Sitzungsdateien hatte am 13. August einen `parentUuid` ohne Ziel in derselben Datei.

**5.4 Ein zweiter möglicher Mechanismus, ausdrücklich unbelegt.** Syncthing schiebt empfangene Dateien über eine Zwischendatei an ihren Platz — das Ersetzen erfolgt durch Umbenennen und erzeugt damit eine **neue Inode**. Ein Prozess, der die alte Datei offen hält, schreibt weiter in die abgehängte Inode; seine Zeilen erschienen in der sichtbaren Datei nie. Ob Claude Code einen dauerhaften Schreibgriff hält oder je Schreibvorgang neu öffnet, ist **nicht** untersucht. Falls es so ist, wäre das ein zweiter, unabhängiger Weg zum selben Schadensbild — und er würde auch erklären, warum eine *laufende* Sitzung während der Auflösung gefährlich ist.

**5.5 Bezug zu den offenen Fragen des Projekts.** Dieser Fall ist der erste praktische Beleg für **F3** („Dateien in Benutzung durch die laufende Instanz"): Der Chat war während der Auflösung auf mindestens einem Rechner offen. Und er gehört zu **F7** („Reale Konfliktkandidaten"), denn er benennt erstmals einen Konflikttyp, der im Betrieb wirklich auftrat — herbeigeführt allerdings durch bewusstes Öffnen desselben Chats an zwei Rechnern, nicht von selbst.

**5.6 Was die Doku dazu heute schon sagt.** Das Kapitel **„Konflikte: Entstehung und Gestalt"** warnt bereits: Die Sitzungsprotokolle „kollidieren zwischen zwei Rechnern praktisch nie, **sofern man auf beiden Rechnern nicht gleichzeitig im selben Chat arbeitet**". Der Versuch hat diese Bedingung gezielt verletzt und die Warnung damit **bestätigt**, nicht widerlegt. Was die Doku nicht erklärt, ist die **Mechanik** dahinter — und genau die ist der Grund, warum die naheliegende Auflösung („neueste Datei") hier die falsche ist.

---

## 6 Vorschläge — nicht entschieden, nicht eingearbeitet

**6.1 Auswählen ist falsch — aber die Vereinigung über `uuid` ebenfalls.** Am 13. August wurde der erste Vorschlag dieses Dokuments (»alle Zeilen nehmen, nach `uuid` entdoppeln«) **widerlegt**: Rund **30 % der Zeilen tragen überhaupt keine `uuid`** — gemessen 2.010 von 6.724, nämlich die Arten `queue-operation`, `file-history-snapshot`, `ai-title`, `last-prompt`, `mode`, `file-history-delta`. Eine Entdopplung über `uuid` würde diese Zeilen verlieren oder verdoppeln.

Richtig ist eine Vereinigung **auf Zeilenebene**: identische Zeilen entdoppeln, nach `timestamp` ordnen, wo einer vorhanden ist. Und davor gehört ein Test, der den Regelfall ohne jedes Urteil erledigt — siehe die Kaskade in 6.2.

Auch das verstößt nicht gegen die Vorgabe »keine selbsttätige Zusammenführung«: Es bliebe ein Vorschlag der Konfliktsitzung, den der Nutzer je Datei bestätigt — die Vorgabe kennt »von Hand zusammenfügen« ausdrücklich als eine der drei Entscheidungen.

**Vorbehalte, die dazugehören:**

1. Das Format ist laut Doku **intern und versionsabhängig**. Jede Vereinigung stützt sich auf Annahmen über den Zeilenaufbau — plausibel, aber nicht zugesichert.
2. **Ungeprüft** ist, ob Claude Code eine von Hand vereinigte Datei anstandslos lädt.
3. Vor der Auflösung sollte der betroffene Chat **auf allen Rechnern geschlossen** sein — sonst überschreibt ein laufender Prozess das Ergebnis.

**6.2 Vorgeschlagene Kaskade — Momentaufnahme, keine Festlegung.** Die folgende Abfolge ist aus der Perspektive **dieses einen Falls** entstanden (Abschnitt 4). Sie ist ausdrücklich **kein beschlossenes Rezept**: Vor einer Umsetzung sind weitere Tests nötig, um sie zu erhärten oder weitere Sonderfälle zu finden. Es ist gut möglich, dass sich dabei ein **veränderter Ansatz** ergibt, der mit der Breite der Fälle besser umgeht als eine Kaskade.

1. **Klassifizieren.** Liegt die Kopie unter `projects/` und endet auf `.jsonl`, ist es ein Sitzungsprotokoll — anfügendes Baumprotokoll, Sonderregeln. Alles andere: normales Verfahren.
2. **Ist die Sitzung hier offen?** Mechanisch prüfbar und am 13. August verifiziert: Die offenen Sitzungs-IDs stehen in der Kommandozeile der laufenden Prozesse (`pgrep -af resume`). Wenn ja: das Original **niemals umschreiben**, nur vollständig enthaltene Kopien löschen.
3. **Präfix-Test.** Ist eine Datei ein Byte-Präfix der anderen, enthält sie nichts Eigenes: längere behalten, kürzere löschen. Verlustfrei, kein Urteil nötig — und der bisher einzige real beobachtete Fall.
4. **Erst bei echter Divergenz:** Trennstelle bestimmen, beide Fortsetzungen in Prosa gegenüberstellen, Vereinigung auf Zeilenebene vorschlagen. Nie »die neueste nehmen«.
5. **Nachprüfen:** Enthält das Ergebnis `parentUuid`s ohne Ziel, ist etwas verlorengegangen.

**6.3 Hilfsskript — Umfang bewusst offen.** Ein Hilfsskript, das den mechanischen Teil deterministisch erledigt, ist erwünscht; sein Platz wäre `~/.claude-sync-watch/werkzeuge/`, der genau dafür angelegt und bisher leer ist und der Sitzung schon per `--add-dir` mitgegeben wird. **Was es können und dürfen soll, wird jetzt ausdrücklich nicht festgelegt** — das wird geklärt, wenn die volle Breite der Konfliktmöglichkeiten untersucht ist. Der Gedanke dahinter: Was das Skript rechnet, kann die Sitzung nicht verfransen; was die Sitzung erklärt und fragt, kann das Skript nicht.

**6.4 Wo das hingehörte, wenn es beschlossen wird.**

- Als Sonderregel in die Arbeitsanweisung der Konfliktsitzung (`conflict-resolution.md`, beschrieben im Kapitel **„Arbeitsanweisung für die Konfliktsitzung"**): Bei Konflikten unter `projects/` keine Fassung wählen, sondern die Vereinigung nach `uuid` vorschlagen, und vorher das Schließen des Chats auf allen Rechnern empfehlen.
- Als Zusammenhang in das Kapitel **„Konflikte: Entstehung und Gestalt"**, weil dort die Warnung steht, die dieser Fall erklärt.
- Als Befund in **„Belegführung und Testplan"** sowie bei **F3** und **F7** im Fragenkatalog.

**6.5 Bewusst *nicht* vorgeschlagen:** `projects/` aus dem Abgleich auszuschließen. Genau dieses Verzeichnis ist der Zweck des ganzen Vorhabens — es trägt das Projektgedächtnis.

---

## 7 Einwände und Prämissen des Nutzers (13. August)

Diese Punkte sind Vorgaben für die Lösung, nicht Diskussionsbeiträge — sie schließen Wege aus, die auf dem Papier gut aussehen.

**7.1 Der Wächter führt keinen Fernabschuss aus.** Ein Kanal über den abgeglichenen Ordner darf Informationen austauschen; die Befugnis, auf dem anderen Rechner Prozesse zu beenden, gehört nicht in den Wächter.

**7.2 »Nicht denselben Chat auf beiden Rechnern öffnen« ist praktisch nicht durchsetzbar.** Die VS-Code-Erweiterung setzt beim Öffnen des Projekts die letzte Sitzung fort — das Öffnen des Projekts *ist* damit das Öffnen desselben Chats. Der Fall vom 13. August entstand genau so, ohne Absicht.

**7.3 »Auf dem zweiten Rechner einen neuen Chat beginnen« ist keine akzeptable Lösung.** Sie verlangte, zum Feierabend mit einem Thema fertig zu sein, um den Kontext wegwerfen zu können — wer am Folgetag am anderen Rechner weiterarbeitet, verliert damit genau das, was dieses Vorhaben transportieren soll. Das Problem ist also nicht durch Verhaltensregeln zu umgehen; es braucht eine technische Lösung.

**7.4 »Aufgelöst wird dort, wo der Chat offen war« trägt nicht allgemein.** Es setzt voraus, dass der Nutzer den anderen Rechner erreichen kann. Steht er hinter einer Firewall, geht das nicht — dann bliebe der Konflikt liegen, bis irgendwann jemand vor dem Gerät sitzt. Eine Lösung, die einen Menschen am entfernten Rechner verlangt, ist keine.

**7.5 Die Vorgabe »keine eigenen Dateien in `~/.claude`« ist selbst gesetzt und darf weichen.** Sie stammt von uns, nicht von Claude Code. Mit genügend Erfahrung darüber, wie Claude den Ordner nutzt, kann sie so weit aufgeweicht werden, dass dort eine **Koexistenz für wichtige Nachrichten** möglich ist — der abgeglichene Ordner ist der einzige Kanal, der ohne Zusatzinfrastruktur beide Rechner erreicht.

## 8 Diskussionsvorschläge für den Fernfall (nicht beschlossen)

Für den Fall, dass am entfernten Rechner eine Sitzung läuft und deshalb vor der Auflösung beendet werden muss, stehen zwei Wege zur Diskussion — beide erst zu bewerten, wenn die Breite der Konfliktfälle untersucht ist:

**8.1 Wo Fernzugang besteht (SSH oder Remote-Desktop):** Diesen Weg gehen und dem Nutzer bestenfalls ein kleines Skript mitgeben, mit dem er das Problem schnell löst — VS Code beenden, einschließlich des Servers für Remote-Entwicklung. Zu bedenken: Claude läuft in VS Code in einer eigenen, mitgelieferten Umgebung und nicht über die CLI-Installation des Nutzers; ein Beenden muss also den Editor-Prozess treffen, nicht ein `claude` im Pfad.

**8.2 Wo kein Fernzugang besteht:** Ein **weiterer, eigener Dienst**, der nur auf solchen Rechnern installiert wird. Er überwacht den abgeglichenen Ordner auf eine besondere Anweisungsdatei und beendet daraufhin VS Code. Damit bräuchte es weder Claude auf dem entfernten Rechner noch eine SSH-Sitzung des Nutzers. Ausdrücklich ein **zweiter Dienst**, nicht der Konflikt-Wächter (siehe 7.1) — die Befugnis, Prozesse zu beenden, bleibt vom Beobachten getrennt.

## 9 Nächste Schritte in der neuen Sitzung

**Reihenfolge nach der Prämisse 7.3:** Das Problem ist nicht durch Verhaltensregeln zu umgehen, also ist zuerst die Breite der Fälle zu erkunden und erst danach eine Lösung zu bauen.

1. **Die Breite der Konfliktfälle untersuchen**, statt vom bisher einzigen echten Fall zu verallgemeinern. Offene Fragen dafür: Kommt der Präfix-Fall meist vor oder war er Zufall? Wie sieht ein Konflikt aus, wenn auf **beiden** Rechnern wirklich weitergeredet wurde? Was passiert bei einer Verzweigung durch Rewind auf einer Seite? Wie verhalten sich die Zeilen ohne `uuid` dabei? Welche anderen Dateien unter `~/.claude` kollidieren überhaupt — bisher war es ausschließlich das Sitzungsprotokoll.
2. **Billiger Test, ob eine vereinigte Datei lädt** (siehe 6.1, Vorbehalt 2): Wegwerf-Chat auf beiden Rechnern, beidseitig schreiben, Konflikt entstehen lassen, beide Chats **schließen**, auf Zeilenebene vereinigen, Chat öffnen und prüfen: vollständig, beide Zweige sichtbar, Fehlermeldungen?
3. **Prüfen, ob 5.4 zutrifft** (Inode-Wechsel bei laufendem Prozess). Eingriff in eine laufende Sitzung, braucht eine bewusste Entscheidung.
4. **Erst danach** Rezept und Hilfsskript festlegen (6.2, 6.3) und über den Fernfall entscheiden (8).
5. Unabhängig davon offen: Die Frage des Nutzers nach dem **Nutzen** der Verzweigungen im Arbeitsalltag — technisch beantwortet in 1 und 2, praktisch noch nicht besprochen.

## 10 Was getan wurde und was nicht

**Nicht getan, bewusst:** keine Änderung an der Implementierungsdoku, an `conflict-resolution.md` oder am Wächter. Der Doku-Review soll zuerst zu einem konsistenten Stand kommen; erst danach wird dieser Fall eingearbeitet.

**Getan am 13. August:** Der vorliegende Konflikt wurde aufgelöst — nach Prüfung der Enthaltensein-Eigenschaft **nur die Kopie gelöscht**, das Original unangetastet (Abschnitt 4). Die Messungen waren rein lesend und ohne Gesprächsinhalte.

**Nebenbefunde für die Belegführung der Doku**, die nicht zu diesem Fall gehören, aber beim Untersuchen anfielen und dort noch einzuarbeiten sind: Die Journal-Zeile, die Episodenregel (Dialog nach dreißig Minuten erneut), die Einordnung von `Gtk-CRITICAL`-Rauschen als Vertagung und das Löschereignis, das die Episode beendet, haben sich alle im Produktivbetrieb an einem echten Konflikt bewährt.
