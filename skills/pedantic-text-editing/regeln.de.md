# Regeln der pedantischen Textbearbeitung

Diese Regeln gelten ab jetzt für die gesamte Sitzung und ausschließlich für die Dateien, die nach Abschnitt 2 dazugehören.

**Eine Runde** ist ein Durchgang von der Vorlage der Funde über die Freigabe bis zur ausgeführten Änderung samt Gegenprobe — eine Befunddatei, ein Commit-Paar. Sie ist **nicht** ein Turn im Chat: Eine Runde kann sich über viele Nachrichten und über mehrere Sitzungen erstrecken, und nicht jeder Fund muss dabei gemeinsam durchgegangen werden.

## 1 Was vor dem ersten Schritt geklärt wird

1. **Welche Datei oder Dateien** bearbeitet werden (Abschnitt 2).
2. **Welches Rechtschreibregelwerk und welche Varietät** gelten — etwa die amtliche Regelung in de-DE, de-AT oder de-CH. Bei mehreren Texten darf das je Text verschieden sein; halte fest, was für welchen gilt.
3. **Ob und womit der Verlauf versioniert wird.** Liegt der Text in einem Git-Repository, gilt Abschnitt 11. Nennt der Nutzer ein anderes Verfahren, prüfe, ob Du es bedienen kannst, und benutze dann dieses. Gibt es keines, weise **einmal je Sitzung** darauf hin, dass ein Tracking im Fehlerfall den Rückweg eröffnet, und arbeite nach dem Absatz „Ohne Versionierung“ in Abschnitt 11.
4. **Ob der Ausgangsstand sauber ist** — keine uncommitteten Änderungen an der Textdatei. Ist er es nicht, beginnt keine Runde: Ohne festen Ausgangspunkt sind Nachweis und Rückweg wertlos.
5. **Wie groß eine Runde sein darf.** Ohne andere Angabe des Nutzers: höchstens 30 Änderungsstellen.

Die Antworten gelten für die Sitzung.

## 2 Welche Dateien dazugehören

Es gelten nur die ausdrücklich benannten Dateien. Eine Ausnahme: Ist erkennbar, dass ein Text auf mehrere Dateien verteilt ist oder im Lauf der Arbeit verteilt wird, gehören diese ebenfalls dazu — frage vorher, bevor Du sie zuordnest. Ist bei einer neuen Datei noch nicht klar, ob sie Teil desselben Textes ist, merke sie Dir und beobachte sie; bis zur Klärung ist sie ausgeschlossen.

Legt der Nutzer eine Datei an, die nicht zu dieser Ausnahme gehört, fragst Du **nicht** nach. Er muss sie Dir von sich aus benennen. Da das Zufügen von Dateien immer in Abstimmung mit Dir geschieht, weiß er jederzeit, welche dazugehören und welche er benennen müsste — deshalb ist das Verfahren auch dann abgesichert, wenn Du nicht nachfragst, und Du musst nur so handeln, wie hier beschrieben.

## 3 Drei Klassen von Funden, drei Behandlungen

- **Regelverstoß** — eindeutig falsch nach dem vereinbarten Regelwerk: Rechtschreibung, Grammatik, Zeichensetzung, ein fehlendes Wort, das den Satz ungrammatisch macht. Kommt als Korrektur in die Korrekturliste.
- **Sachfrage** — Zahl, Datum, Name, Verweis, Widerspruch im Text, zweifelhafte Behauptung. Wird **nie** korrigiert, sondern als Frage vorgelegt, getrennt von der Korrekturliste. Auch dann, wenn Du sicher zu sein glaubst.
- **Geschmack** — Ausdruck, Wortwahl, Satzrhythmus, Straffung, ein Wort, das den Satz nur runder machen würde. Nur, wenn der Nutzer das ausdrücklich verlangt hat. Dann in einer eigenen Kategorie, und die inhaltliche Aussage der Passage muss unverändert bestehen bleiben.

**Sachfragen sind zweierlei, und nur die erste Sorte gehört ungefragt zum Auftrag.** *Formale* Sachfragen betreffen die Schreibweise eines Wertes — Dezimalzeichen, Tausendertrennung, Datumsform, die Zielangabe eines Verweises (Abschnitt 5). Sie kommen in die Korrekturliste wie jeder andere Fund. *Inhaltliche* Sachfragen gehen darüber hinaus: Widersprüche im Text, unklare Aussagen, zweifelhafte Behauptungen. Sie gehören nur dann zum Auftrag, wenn der Nutzer sie ausdrücklich einbezieht — für eine inhaltliche Prüfung wird meist ein eigener Auftrag erteilt. Gehören sie nicht dazu, werden sie **nicht vorgelegt**: Was beim Lesen dennoch ins Auge fiel, kommt ausschließlich in den Kopf der Befunddatei, unter den Bedingungen von Abschnitt 8.

Eine Zeile der Korrekturliste gehört zu genau einer Klasse. Bündle nie eine Geschmacksänderung mit einer Korrektur in derselben Zeile — sonst gibt der Nutzer beispielsweise mit dem Komma auch den umgeschriebenen Halbsatz frei.

## 4 Detailtreue: was sich nie ändert

**Außerhalb der freigegebenen Stellen ändert sich kein Zeichen.** Das ist der Zweck dieses Skills, und es hört bei nichts auf, das nach einer Verbesserung aussieht.

Nichts davon geschieht nebenbei:

- Absätze neu umbrechen, Zeilenlängen angleichen, Leerraum normalisieren, Leerzeilen zufügen oder entfernen, das Dateiende ändern.
- Anführungszeichen, Apostrophe, Binde- und Gedankenstriche oder Auslassungspunkte umwandeln — auch nicht „nur typografisch“.
- Abschwächungen, Verstärkungen und Modalpartikeln tilgen („etwa“, „wohl“, „nur“, „durchaus“, „ja“). Sie tragen Bedeutung, auch wenn sie wie Füllwörter aussehen.
- Sätze verschmelzen oder teilen unter dem Etikett Grammatik.
- Begriffe über den Text hinweg angleichen. Vereinheitlichung ist ein eigener, ausdrücklich beschlossener Durchgang, keine Nebenwirkung einer Korrektur.
- Überschriften, Nummerierungen, Listenzeichen und Formatierungen anfassen, solange sie nicht selbst Gegenstand einer freigegebenen Zeile sind.

Zwei Regeln zur Autorität über den Wortlaut:

- **Die im Text erkennbar durchgehaltene Konvention hat Vorrang** vor jeder äußeren Vorliebe. Wer durchgehend eine ältere oder eigenwillige Schreibung benutzt, wird nicht stillschweigend modernisiert; frage einmal, ob sie so bleiben soll.
- **Wo das Regelwerk beide Formen zulässt, ist keine Korrektur fällig.** Eine erlaubte Variante ist kein Fehler.

**Unantastbar** — auffällig gewordene Stellen werden gemeldet, nie korrigiert: wörtliche Zitate, Eigennamen, Werktitel, Literaturangaben, fremdsprachige Passagen, bewusst altertümliche oder mundartliche Stellen, Code-Spannen und Links. Was der Nutzer hier einmal entschieden hat, steht danach im Glossar der Entscheidungsdatei und wird nicht erneut zur Entscheidung gestellt (Abschnitt 9).

## 5 Zahlen, Sachdaten und Verweise

Betroffen sind Werte in Tabellen, Bildunterschriften und Beispielen, Verweise innerhalb des Textes („siehe Abschnitt 4“, „Tabelle 3“, „S. 42“), Literaturangaben, URLs und DOI, Werte aus fremden Quellen sowie Gleichungen samt ihren Einfügestellen und Beschriftungen.

- **Der Wert selbst ist immer Sachfrage** (Abschnitt 3) — nie ändern, vorlegen. Auch wenn er offensichtlich falsch aussieht.
- **Die Schreibweise des Wertes** — Dezimalzeichen, Tausendertrennung, Leerzeichen vor der Einheit, Datumsform — folgt der im Text durchgehaltenen Konvention. Abweichungen davon sind ein Regelverstoß, kommen aber als eigene Kategorie in die Korrekturliste und nie mit einer Prosakorrektur in derselben Zeile.
- **Fremde Werte prüfst Du nicht gegen Dein Gedächtnis.** Entweder liegt die Quelle vor, oder es bleibt eine Frage. Eine einmal geklärte Frage steht in der Entscheidungsdatei und wird nicht erneut gestellt (Abschnitt 9).
- **Verschiebt eine freigegebene Änderung eine Nummerierung, einen Verweis oder eine Seiten- oder Zeilenangabe**, wird die Folgestelle nicht automatisch mitgeändert. Melde sie und lege sie als eigene Zeile vor.
- **Bei Abbildungen** unterliegen Link, Bildunterschrift und Beschreibung diesen Regeln; das Bild selbst nicht. **Bei Gleichungen** ist der Inhalt Sachfrage, ihre Beschriftungen und die Verweise darauf sind Prosa.

## 6 Wie die Funde im Chat vorgelegt werden

Gliedere die Ausgabe nach **Fundort und Kategorie** — als Zwischenüberschriften, nicht als Tabellenspalten. Die Tabelle selbst bleibt schmal, sonst wird die Freigabe zur Zumutung:

| ID | Zeile |  | Änderung |
| --- | --- | --- | --- |
| 1 | 42 | Vorh | `dass er dass sagte` |
|  |  | Nach | `dass er das sagte` |

**Ein Fund bekommt so viele Tabellenzeilen, wie er braucht.** Die erste trägt ID, Zeilennummer und das Vorher-Stück; die folgenden lassen ID und Zeilennummer leer und tragen das Nachher-Stück und, falls nötig, die Begründung. Die Beschriftung steht in einer **eigenen, schmalen Spalte** und abgekürzt — `Vorh`, `Nach`, `Begr` —, damit der Text darunter überall an derselben Stelle beginnt und sich die Unterschiede mit einem Blick erfassen lassen. Die Spalte trägt keine Überschrift. **Kein `<br>` und kein echter Zeilenumbruch in einer Zelle:** Ein echter Umbruch zerlegt die Tabelle, und `<br>` wird nicht überall umgesetzt — im Frontend von Claude Code erscheint es als sichtbarer Text (beobachtet am laufenden System, 25. August 2026). Über mehrere Zeilen verbundene Zellen kennt Markdown nicht; die leeren Zellen sind deshalb die einzige Form, die überall gleich aussieht.

- **Die ID** ist je Runde fortlaufend und wird nicht neu vergeben. Über sie spricht der Nutzer die Zeilen an.
- **Die Zeilennummer** ist zulässig und hilfreich, weil die Datei bis zur Freigabe unverändert bleibt. Enthält eine Zeile einen ganzen Absatz, findet der Nutzer die Stelle über die Suchfunktion seines Editors — dafür genügt das Vorher-Stück.
- **`Vorh` und `Nach`** stehen so in der Beschriftungsspalte, immer in dieser Reihenfolge und mit diesen Kürzeln.
- **Eine Begründung** nur, wo sie nicht auf der Hand liegt — dann als weitere Zeile mit `Begr` in der Beschriftungsspalte.
- **Bei längeren Passagen keine Tabelle.** Dort entfällt die Beschriftungsspalte und die Wörter werden ausgeschrieben, weil sich ohne Spalten nichts ausrichten lässt: je Eintrag beginne immer mit „<ID> – <ZEILENNUMMER><ZEILENUMBRUCH>Vorher: “  und „Nachher:“ ebenfalls nach einem Zeilenumbruch. Sind viele kleine Passagen mit einzelnen längeren Passagen vermischt, so unterbrich die Tabellendarstellung für die längere Passage(n) und setze danach die Tabelle fort.
- **Zeige nur so viel Text, wie die Entscheidung braucht** — nicht den ganzen Absatz, wenn drei Wörter reichen.
- **Höchstens 30 Änderungsstellen je Runde**, sofern der Nutzer keinen anderen Wert genannt hat. Wird es mehr, teile die Arbeit und sage vorher, wie Du teilst. Ergibt sich die Teilung schon aus dem Abschnitt, in dem Du gerade bist, folge dieser.

**Die Länge des Vorher-Stücks richtet sich nach der Entscheidung, nicht nach der Datei.** Zwei Dinge muss der Nutzer daran können: die Stelle in seinem Text schnell finden, und über die Änderung befinden, ohne den Kontext ringsum selbst zusammensuchen zu müssen. Beides zusammen gibt das Maß. Reicht der Kontext vor Ort dafür nicht — oder zieht er sich über einen längeren Bereich —, gib eine Begründung dazu, statt den Ausschnitt aufzublähen. Der **gespeicherte** Ausschnitt folgt einer anderen Regel: Er muss in der Datei eindeutig sein (Abschnitt 8). Beide dürfen sich in der Länge unterscheiden.

Sachfragen (Abschnitt 3) stehen in einer **eigenen Liste** unter der Korrekturliste, nie darin, sind immer zu begründen und nicht als Tabelle darzustellen.

## 7 Die Freigabe

- Der Nutzer gibt über die IDs frei — einzeln, „alle“ oder „alle außer 7 und 12“. Was nicht freigegeben ist, wird nicht ausgeführt.
- **Ein abgelehnter Vorschlag wandert in die Entscheidungsdatei und wird nicht erneut vorgeschlagen**, solange die Stelle im Wortlaut unverändert ist (Abschnitt 9). Das gilt über die Sitzung hinaus. Zurück bringt ihn nur der Nutzer.
- Bietet der Nutzer **weitergehende Freiheiten** an, gelten sie nur für die dabei benannte Kategorie und die dabei benannte Datei, gelten für die Sitzung und decken nie eine Sachfrage und nie eine Geschmacksänderung. Schränkt der Nutzer dabei die Nutzungszeit der weitergehenden Freiheiten mit einer eigenen Formulierung ein, z.B. nur für eine einzelne Aufgabe oder einen Aufgabenkomplex, dann gilt der sich daraus und aus dieser Anweisung ergebende kürzeste Nutzungsbereich als Maß, z.B. nie über die Sitzung hinaus, auch wenn in der Sitzung die Aufgabe noch nicht beendet ist. Die Korrekturliste entfällt dabei nicht — sie wird zum Bericht **nach** der Ausführung, und Befunddatei und Nachweis nach Abschnitt 11 bleiben vollständig.

## 8 Die Befunddatei einer Runde

Sie liegt **neben der Textdatei** und heißt `editing-findings_<basisname der textdatei>_<JJJJ-MM-TT_hh-mm>.md`. Beginnen zwei Runden in derselben Minute, zähle die Minute hoch. **Der Stamm `editing-findings_` wechselt nicht mit der Sprache dieses Skills** — sonst fände eine später installierte Fassung die Runden der früheren nicht wieder. Dasselbe gilt für die Marken in den Commit-Nachrichten (Abschnitt 11); frei in der Sprache sind allein die Beschriftungen innerhalb der Datei.

**Der Kopf steht vor einer Trennlinie `---` und trägt den Auftrag**, aus dem die Befunde hervorgegangen sind: welche Datei untersucht wurde, welches Regelwerk und welche Varietät galten, welche Klassen einbezogen waren — und ausdrücklich, **was nicht untersucht wurde**, etwa inhaltliche Sachfragen nach Abschnitt 3. Darunter Datum und Uhrzeit. Erst unter der Trennlinie stehen die Befunde. Der Kopf ist der Teil, der später die Frage beantwortet, warum eine Stelle damals nicht auffiel; ohne ihn ist das nicht mehr zu rekonstruieren.

**Zurückgestellte Funde aus ausgeschlossenen Klassen** dürfen im Kopf notiert werden — aber nur, was beim Durchgang ohnehin aufgefallen ist: kein eigener Suchdurchgang, **keine Sollzahl**, null ist ein normales Ergebnis. Notiert wird vollständig oder gar nicht — eine gekürzte Liste sähe wie ein Inventar aus, das sie nicht ist. (Vier von vier Runden ohne ausdrückliche Anweisung lieferten exakt zwei zurückgestellte Funde, die erste ohne jede Vorlage vor sich — Eigenproduktion des Modells, nicht Fortschreibung; beobachtet am laufenden System, 25. August 2026.)

Je Fund ein **Block**, keine Tabellenzeile. Grund: Die Textstücke müssen zeichengenau sein, und Editoren richten Markdown-Tabellenzeilen beim Speichern neu aus und fressen dabei Leerraum — ein Nachweis, der unbemerkt verfälscht wird, ist keiner. „Vorher“ und „Nachher“ stehen deshalb in eigenen Codeblöcken, die den Leerraum bewahren:

```markdown
### 1 — Zeile 42 — Rechtschreibung — freigegeben

Vorher:

    dass er dass sagte

Nachher:

    dass er das sagte

Begründung: Konjunktion und Artikel verwechselt.
```

- **Das Vorher-Stück ist wörtlich und in der Datei eindeutig.** Ist es das nicht, verlängere es, bis es eindeutig ist.
- Die Datei hält den **freigegebenen** Stand, einschließlich der abgelehnten Einträge mit ihrer Entscheidung.
- **Gelöscht wird sie nicht von selbst.** Sie darf weg, sobald ihre dauerhaften Anteile in der Entscheidungsdatei stehen (Abschnitt 9). Weist der Nutzer das Löschen an, prüfe das vorher nach und trage Fehlendes nach, statt zu löschen und es zu verlieren.

## 9 Die Entscheidungsdatei

Sie heißt `editing-data_<basisname der textdatei>.md`, liegt neben der Textdatei, wächst mit der Arbeit und wird **nie** gelöscht. Sie ist das Gegenstück zur Befunddatei: Die Befunddatei ist eine Runde, die Entscheidungsdatei ist das Gedächtnis. Vier Abschnitte:

- **Unantastbar** — das Glossar: der Wortlaut, seine Klasse (Zitat, Eigenname, Werktitel, Literaturangabe, fremdsprachige oder mundartliche Stelle) und die Entscheidung.
- **Geklärte Sachfragen** — die Fundstelle im Wortlaut, die Frage, die Antwort des Nutzers.
- **Abgelehnte Vorschläge** — das Vorher-Stück und das, was vorgeschlagen und abgelehnt wurde.
- **Protokoll** — je Runde eine Zeile: der Kopf der Befunddatei, der Prüfzeitpunkt und die Bytegröße der untersuchten Datei zu diesem Zeitpunkt. Verbindlich für den Textstand sind die Commits der Runde (Abschnitt 11); die Bytegröße ist eine Lesehilfe für den Menschen, kein Beweis.

**Geschrieben wird sie am Ende jeder Runde**, nicht erst beim Aufräumen. Sonst löscht ein Aufräumen zur falschen Zeit unverdaute Befunde.

Drei Regeln, die das Verfahren tragen:

- **Der Schlüssel ist der Wortlaut** — nie die Zeilennummer, nie die ID. Ändert sich die Passage später, greift der Eintrag nicht mehr, und dieselbe Frage darf wieder gestellt werden: Dann ist es eine andere Stelle. Deshalb bleiben die IDs rundenlokal und brauchen kein Gedächtnis über die Runde hinaus.
- **Ein Eintrag ändert die Vorgabe, nicht die Meldung.** Ein Glossartreffer kommt weiterhin in die Korrekturliste, aber in eigener Kategorie und mit „nicht ändern“ als Vorgabe. Der Nutzer entscheidet damit nur noch dort, wo das Glossar danebenliegt.
- **Die jüngste Eintragung gilt.** Wurde eine Passage in einer früheren Runde für unantastbar erklärt und später revidiert, sagt das allein die Reihenfolge. Suche rückwärts von der neuesten.

**Welche Entscheidungsdateien herangezogen werden, ist offenzulegen.** Herangezogen werden **alle** `editing-data_*`-Dateien des Ordners, in dem die Textdatei liegt — ob zwei Dateien wirklich zu einem Text gehören oder nur zufällig nebeneinanderliegen, ist von außen nicht sicher zu erkennen, und ein zu enger Zuschnitt ließe das Glossar zerfallen. Sag dem Nutzer, welche Dateien Du benutzt; er kann einzelne ausdrücklich ein- oder ausschließen.

**Beim Beginn einer Runde**, und zwar sparsam: Suche **gezielt nach dem Wortlaut** jedes einzelnen Fundes, statt die Dateien vollständig zu lesen — sonst wächst der Aufwand mit jeder Runde. Liegen Befunddateien früherer Runden im Ordner, sag das und schlage vor, sie aufzuräumen.

## 10 Ausführen

- Geändert werden ausschließlich die freigegebenen Stellen, jede als exakte Ersetzung des Vorher-Stücks durch das Nachher-Stück. Findet sich das Vorher-Stück nicht wörtlich, ändere nichts und melde es.
- **Deutsche Prosa wird mit den Datei-Werkzeugen geschrieben, nie über ein Skript mit Heredoc, `sed` oder `awk`.** Anführungszeichen und Gedankenstriche im Text beenden dort die Zeichenketten vorzeitig, und der Lauf bricht mitten in der Datei ab.
- Kein Formatierer, kein Linter, kein Werkzeug, das die Datei nebenbei umbricht oder normalisiert.

## 11 Der Nachweis und die Gegenprobe

Je Runde zwei Commits, in dieser Reihenfolge, jeweils nur mit den betroffenen Pfaden (`git add -- <textdatei> <befunddatei> <entscheidungsdatei>`) und nie mit dem ganzen Baum:

1. **Die freigegebene Befunddatei**, die Textdatei darin noch unverändert. Der Betreff trägt die Marke `Findings:` und den Dateinamen.
2. **Die ausgeführte Textänderung samt der fortgeschriebenen Entscheidungsdatei.** Der Betreff trägt die Marke `Text correction:`.

Die Marken machen die Runden über `git log --grep` auffindbar; die übrige Form der Commit-Nachricht richtet sich nach den Gepflogenheiten des Projekts. Aus dem Paar ergibt sich beides: Die Befunde stehen im ersten Commit, und die Differenz zwischen beiden ist genau das, was ausgeführt wurde.

**Die Gegenprobe vor dem zweiten Commit ist Pflicht.** Sieh Dir `git diff -- <textdatei>` an und halte die geänderten Stellen gegen die freigegebenen IDs. Stimmt die Zahl nicht, oder steht im Diff etwas, das zu keiner freigegebenen ID gehört: nichts committen, die überzählige Änderung zurücknehmen, dem Nutzer melden. Dies ist die einzige Stelle, an der eine unbemerkte Änderung überhaupt auffällt — sie entfällt nie, auch nicht bei einer einzigen Korrektur.

**Ohne Versionierung:** Lege vor der Runde eine Kopie der Textdatei in einem Arbeitsverzeichnis außerhalb des Projekts an und führe die Gegenprobe mit `diff` gegen diese Kopie. Der Nachweis fehlt dann, die Gegenprobe nicht.

**Nach der ausgeführten Änderung: schlage einen Prüflauf vor**, wenn das Protokoll der Entscheidungsdatei seit dem letzten mehrere Runden zeigt. Ein Prüflauf ist kein eigener Modus, sondern eine gewöhnliche Runde über einen schon bearbeiteten Text — dieselben Klassen, dieselbe Liste, dieselbe Freigabe. Sein Eigenwert liegt darin, dass er findet, was frühere Korrekturen erst hineingetragen haben. Verlangt der Nutzer sinngemäß dieselbe Prüfung noch einmal, **ist** das der Prüflauf; ein zweiter ist dann nicht nötig. Vergisst Du den Vorschlag, geht nichts kaputt — er ist eine Erinnerung, keine Bedingung.

## 12 Frühere Runden nachschlagen

Nie aus dem Gedächtnis. Der erste Blick geht in den Ordner, denn dort liegen die Befunddateien, solange sie nicht aufgeräumt wurden — nach Namen sortiert stehen sie in zeitlicher Reihenfolge, und **die neueste gilt**. Sind sie aufgeräumt, hält die Historie sie:

```bash
ls editing-findings_<basisname>_*.md                    # noch vorhandene Runden
git log --oneline --grep=Findings -- <textdatei>        # alle Runden
git log --oneline --diff-filter=D -- <befunddatei>      # eine aufgeraeumte Runde
git show <commit>^:<befunddatei>                        # ihre Befunde
git diff <commit>^ <commit> -- <textdatei>              # was sie geaendert hat
```

Brauchst Du mehrere Stände nebeneinander, schreibe sie mit `git show <commit>:<pfad>` in Dateien eines Arbeitsverzeichnisses außerhalb des Projekts und vergleiche sie dort. Das Projekt bleibt dabei unberührt.

## 13 Mutmaßliche eigene Fehler

Fällt Dir eine Stelle auf, die aus einem früheren Bearbeitungsschritt falsch hervorgegangen sein könnte, korrigiere sie nicht stillschweigend. Schlage zuerst nach (Abschnitt 12), was damals freigegeben war — die Befunde jener Runde sagen es genauer als jede Erinnerung, und ihr Kopf sagt, was damals überhaupt untersucht wurde. Lege die Stelle dann wie jeden anderen Fund zur Freigabe vor.

## 14 Grenzen

- Der Skill setzt Dateien voraus, die als Text gelesen und geschrieben werden können (`.md`, `.txt`, `.tex`, `.rst`, `.html` und Ähnliches). Bei `.docx`, `.odt` oder PDF sag es: Ohne verlustfreies Zurückschreiben gibt es weder Detailtreue noch Nachweis. Zwei Wege bleiben — der Nutzer exportiert in ein Textformat, oder die Korrekturliste bleibt im Chat und er überträgt sie selbst. Welcher davon, entscheidet er.
- Steht der Text nur im Chat und in keiner Datei, gelten die Klassen (3), die Detailtreue (4) und die Form der Vorlage (6). Befunddatei, Entscheidungsdatei, Commits und Gegenprobe entfallen, weil es keine Datei gibt. Sag das einmal.
