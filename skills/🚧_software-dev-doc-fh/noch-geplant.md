# GIT-LFS

Allgemein sinnvoll ist ein Git-Abschnitt im Skill: EIne Session hatte mir nach der LFS-Installation mitgeteilt:

"Andere Rechner: Dort muss git-lfs ebenfalls installiert sein (sudo apt install git-lfs), sonst siehst Du nach dem Pull nur kleine Pointer-Textdateien statt der Bilder. Ich habe LFS bewusst nur lokal im Repo aktiviert (Deine Regel: keine Änderungen außerhalb der Projektwurzel) — auf jedem weiteren Rechner einmalig git lfs install (global) oder git lfs install --local im Repo ausführen."

Deshalb immer nach Session-Start, wenn das erste mal git in der Session benutzt wird: Prüfen, ob LFS im Projekt vorgesehen ist (.gitattributes vorhanden reicht?), dann prüfen, ob im Projekt installiert. Wenn nicht: Nutzer darauf hinweisen und ihm die Installation anbieten.

# Noch geplant: Fahrplan, Planungsablage und die Dateien eines Entwicklungsvorhabens

*Diese Datei ist Arbeitsmaterial zum Skill, nicht Teil von ihm. Die `SKILL.md` verweist nicht auf sie, sie wird also nie geladen (`implementation_doku.md` 1.2). Sie hält fest, was an diesem Skill noch zu tun ist, bevor er installiert werden kann.*

## Anlass

Am 22. August 2026 wurde in einer Sitzung zum Vorhaben `home-.claude-sharing` ein Arbeitsschritt vorbereitet: eine Dienst-Neuinstallation auf zwei Rechnern. Die Vorbereitung — Befehlsfolge, zwei Fallstricke beim Kopieren, die zu erwartenden Warnungen des Installskripts, zwei Nachweisproben und eine erst dabei entdeckte Vorbedingung — wurde von Claude als ausdetaillierter Plan **in den Fahrplan** vorgeschlagen, an den betreffenden Schritt.

Der Entwickler hat das zurückgewiesen: Der Fahrplan hat **keine Dokumentationsfunktion** und ist **keine Ablage für Planungen**. Solche Planung gehört woanders hin — in die projektbegleitende Implementierungsdoku, in ein eigenes Planungsfile im Projekt oder in den Plan-Ordner der Claude-Engine.

Daraus die Frage, die diese Recherche ausgelöst hat: Liegt es daran, dass die Regel unzureichend beschrieben ist, oder daran, dass der Skill, in dem sie steht, nicht ausgelöst hat? Der Auftrag war, alle Quellen zu suchen, die etwas über den Fahrplan sagen, und zu jeder festzuhalten, was sie sagt.

## Befunde

### 1 Beide vermuteten Ursachen treffen zu — und die zweite wiegt schwerer

**Der Skill konnte nicht auslösen, weil es ihn am Ladeort nicht gibt.** Nachgeprüft: `software-dev-doc-fh` liegt weder unter `~/.claude/skills/` noch unter `.claude/skills/` — letzteres existiert als leeres, nicht versioniertes Verzeichnis. Er wird in keiner der beiden `CLAUDE.md` erwähnt, sein `CLAUDE-snippet.md` mit dem stillen Trigger ist nie an einen Zielort übernommen worden, und in der Skill-Liste der Sitzung taucht er nicht auf. Installiert sind fünf Skills: `chat-export`, `common-code-generation`, `konsistenzpruefung`, `konzept-segmentierung` (registriert als `/segmentierung`) und `temp-debug-code`.

**Wichtiger:** Hätte er ausgelöst, wäre das Verhalten dasselbe gewesen. Sein Abschnitt „Wo ein Plan steht" sagt wörtlich dasselbe wie die automatisch geladene Projekt-`CLAUDE.md` — Plan in den Fahrplan, keine eigenen Plan-Dateien. Das Problem ist also **nicht in erster Linie ein Trigger-Problem, sondern ein Inhaltsproblem**, und der betroffene Inhalt steht dreifach.

### 2 Die Quellen, die beim Chatstart automatisch geladen werden

**`~/.claude/CLAUDE.md`** — elf Fundstellen, die normative Hauptquelle:

- **§2.6 „Fahrplan und Status"**: Fahrplan = „die nächsten Schritte in **aufgabenangemessener Detaillierung**", Erledigtes fliegt raus; Status = ausschließlich abgearbeitete Einträge, keine Entscheidungen.
- **§1.9 „Kontext-Haushalt"**: „Wird der Kontext knapp, ist die nächste Handlung die **Detaillierung des Fahrplans** — vor jeder Komprimierung"; Fahrplan und Status sind „das Übergabemedium zwischen Maschinen und Sessions".
- **§2.5 „Arbeitsschleife"**: „Die Tagesaufgabe kommt aus dem Fahrplan."
- **§2.3 „Dokumentstruktur"**: `fahrplan.md` und `status.md` liegen neben den Segmentdateien, ohne numerisches Präfix.
- **§2.1 „Phasen"**: Der Fahrplan entsteht erstmalig in Phase 3, der Segmentierung.
- **§1.7 „Commits"**: „Der Commit-Body benennt den Fahrplanpunkt bzw. den Plan des Schritts."

**`<projekt>/.claude/CLAUDE.md`** — vierzehn Fundstellen; hier steht der Satz, der das Verhalten unmittelbar ausgelöst hat:

- **„Wo ein Plan steht"**: es gebe „genau zwei Orte, und **keine eigenen Plan-Dateien**" — Review-Befunde in den Doku-Anhang, **alles andere „im Fahrplan, im betreffenden Schritt ausdetailliert"**. Ausdrücklich mit §2.6 und §1.9 begründet: „das ist genau ein Plan." Dazu: höchstens ein unausgeführter Plan gleichzeitig, Zweck ist die Wiederaufnahme ohne Chatkenntnis, nach der Ausführung wird er ersetzt statt ergänzt.
- **„Fahrplan-Nummerierung"**: Nummern werden beim Streichen erledigter Schritte nicht neu vergeben.
- **„`fahrplan.md`, `status.md` und die Implementierungsdoku sind entwicklungszeitlich"**: keine Pflichtausstattung, dürfen nach Fertigstellung entfallen; wo es keinen Fahrplan gibt, trägt die README „den Plan des nächsten Schritts".
- **„Befundlisten abarbeiten"**: welche Befundlisten offen sind, sagt der Fahrplan des jeweiligen Vorhabens.

### 3 Die installierten Skills berühren den Fahrplan nur am Rand

**`konzept-segmentierung`** ist der einzige installierte Skill mit substanzieller Aussage, aber nur für Phase 3: „Fahrplan erstmalig erstellen", die Zuordnungsregel „**offen → Fahrplan** — noch nicht entschieden", der „Fahrplan-Vermerk" für unvollständige Feldlisten und die Kontrollrechnung „Segmente + Fahrplan + obsolet = Gesamtzahl". Der Fahrplan ist dort **Auffangbecken für Unentschiedenes**, nicht Planungsablage — das steht der Auffassung des Entwicklers nicht entgegen.

**`konsistenzpruefung`** nennt ihn dreimal am Rand: Funde zweiter Art wandern „als Vermerk in den Fahrplan", ein Protokoll-Ergebniscode lautet „bereits als Fahrplan-Vermerk erfasst", und der Bearbeitungsstand „gehört vor dem Komprimieren in den Fahrplan".

### 4 Was dieser Skill selbst sagt

`SKILL.md` trägt die vollständigste Fassung: Kapitel „Fahrplan und Status" mit Detaillierungsforderung, Nummernregel und dem Verbot von Entscheidungen im Status — **und wörtlich denselben Abschnitt „Wo ein Plan steht"** wie die Projekt-`CLAUDE.md`. Die `README.md` fasst beides noch einmal zusammen. Damit existiert dieselbe Festlegung an drei Orten in gleichlautender Fassung, was der eigenen Regel dieses Skills widerspricht: „Jede Aussage hat genau ein normatives Zuhause."

### 5 Die eine Stelle, die den Fahrplan bewusst abwählt

`skills/implementation_doku.md` begründet, warum das Vorhaben `skills/` keinen Fahrplan führt: Es entsteht kein zusammenhängender Quellcode, sondern eine Sammlung einzeln nebeneinanderstehender Anweisungstexte; „ein gemeinsamer Fahrplan hätte deshalb nichts zu ordnen". An seine Stelle tritt nach 6.1 eine **„Offen"-Liste in der README des jeweiligen Skills** — „Diese Liste ersetzt den früheren Gesamt-Fahrplan" —, und dort steht dann auch der Plan des nächsten Schritts, höchstens einer, deutlich als unausgeführt gekennzeichnet. Das ist bereits heute ein vierter Ablageort für Planungen, der in keiner der drei anderen Quellen vorkommt.

### 6 Anwendungen ohne Regelcharakter

`home-.claude-sharing/fahrplan.md` trägt eine eigene Präambel mit lokalen Regeln (Dringlichkeitsreihenfolge statt Nummernreihenfolge, Abschnitt „Dauerhaft" für nie Erledigtes). `chat-export/fahrplan.md` führt den Fahrplan ausschließlich als Befundliste. `home-.claude-sharing/files/konfliktloesung.md` stellt ausdrücklich klar, dass die mitgeladene Projektmethodik samt Fahrplan **in der Konfliktsitzung nicht gilt**.

### 7 Nebenbefund zum Trigger-Entwurf

`skills/🚧_softwareaufgabe-erkennen/README.md` hält die Messreihe vom 14. August 2026 fest: Eine **eigenschaftsförmige** Trigger-Fassung feuerte auf Sonnet in keiner von drei Eskalationsstufen. Daraus stammt die Regel, den Trigger an eine Ankerhandlung zu binden. Das `CLAUDE-snippet.md` dieses Skills ist bereits so formuliert („Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder zum ersten Mal eine Datei änderst …") und damit vorgabenkonform — es ist nur nie übernommen worden.

## TODO

### T1 — Die Beschreibung der an der Entwicklung beteiligten Dateien wandert vollständig in diesen Skill

**Das ist die erste und wichtigste Aufgabe, weil alle folgenden davon abhängen.** Solange dieselbe Festlegung an mehreren Orten steht, entstehen Doppelungen, die auseinanderdriften, und Kollisionen, bei denen niemand mehr sagen kann, welche Fassung gilt. Der Befund zeigt das an einem konkreten Fall: „Wo ein Plan steht" existiert in zwei gleichlautenden Fassungen, und eine Änderung an nur einer davon hätte den Widerspruch nicht behoben, sondern verdoppelt.

Umzuziehen ist die Beschreibung **aller** Dateien, die ein Entwicklungsvorhaben begleiten — welche es gibt, was jede trägt, was ausdrücklich **nicht** hineingehört, und was mit ihr geschieht, wenn das Vorhaben fertig ist: die Implementierungsdoku mit ihrer Segmentstruktur, `fahrplan.md`, `status.md`, der Review-Anhang und die künftigen Planungsdateien (T2).

Quellen, aus denen der Inhalt herausgelöst wird, und was dort zurückbleibt:

- **`~/.claude/CLAUDE.md` §2.1 bis §2.6** — der gesamte Abschnitt 2 ist der Sache nach dieser Skill. Zurück bleibt der stille Trigger nach `CLAUDE-snippet.md` und, soweit weiterhin gebraucht, die Abgrenzung aus der Präambel, wann Abschnitt 2 überhaupt gilt.
- **`<projekt>/.claude/CLAUDE.md`** — „Wo ein Plan steht", „Fahrplan-Nummerierung" und der Abschnitt über die entwicklungszeitlichen Dateien. Zurück bleibt nur, was **repo-spezifisch** ist und nicht verallgemeinert werden kann.
- **`skills/implementation_doku.md` 6.1** — die Abwahl des Fahrplans für das Vorhaben `skills/` bleibt dort, sie ist projektspezifisch. Der Skill sollte diesen Fall aber **kennen** und benennen: Ein Vorhaben ohne zusammenhängenden Quellcode darf die Dateistruktur ersetzen, und wo das geschieht, gehört die Abweichung in die Vorgaben des Vorhabens.
- **`konzept-segmentierung` und `konsistenzpruefung`** — beide dürfen den Fahrplan weiter **benutzen**, aber nicht mehr **definieren**. Ihre Sätze sind daraufhin durchzusehen; wo sie eine Eigenschaft des Fahrplans behaupten, wird daraus ein Verweis.

Nach dem Umzug gilt für jede Fundstelle die Probe: Sie nennt den Fahrplan, oder sie beschreibt ihn — beides zugleich darf keine mehr.

### T2 — Was anzupassen ist, wenn im Fahrplan keine detaillierten Planungen mehr stehen

Vorschlag für den Umbau dieses Skills, in der Reihenfolge der Wirkung.

**T2.1 Der Fahrplan wird als reine Schrittliste definiert.** Er trägt, **was** zu tun ist und in welcher Dringlichkeit — nicht, **wie**. Die heutige Formulierung „in aufgabenangemessener Detaillierung" ist die Wurzel des Missverständnisses und muss ersetzt werden: Gemeint war die Präzision des Ziels, gelesen wurde die Ausbreitung des Weges. Ein Fahrplaneintrag beschreibt also das Ziel, den Grund seiner Dringlichkeit und, wo vorhanden, den Verweis auf die Planung.

**T2.2 „Wo ein Plan steht" wird durch eine Entscheidungsregel mit drei Zielorten ersetzt.** Das Verbot eigener Plan-Dateien entfällt — es war die eigentliche Ursache. An seine Stelle tritt eine Entscheidung, die **bei jeder Planung einzeln** zu treffen ist, nicht einmal je Projekt:

1. **Bis rund zehn Sätze** — geschätzt im Moment des Eintragens, nicht nachträglich gemessen — steht die Planung **direkt im Fahrplan**. Für den kurzen Fall ist ein Verweis teurer als der Inhalt.
2. **Trägt die Planung Festlegungen über das System selbst** — Verhalten, Schnittstellen, Struktur, Begründungen, die den Code überdauern —, gehört sie in die **Implementierungsdoku**, an das zuständige Kapitel. Der Fahrplan verweist darauf. Das ist der Regelfall für alles, was auch nach der Ausführung noch gelesen werden muss.
3. **Beschreibt sie nur den Arbeitsweg** — Befehlsfolgen, Reihenfolgen, Fallstricke, Nachweisproben — und ist nach der Ausführung wertlos, entsteht ein **eigenes Planungsfile** im Projekt. Der Fahrplan verweist mit Datei und Abschnitt. Für Planungen, die nicht im Projekt liegen sollen, bleibt der Plan-Ordner der Engine als dritter Weg; er ist aber nicht versioniert und für den Entwickler nicht sichtbar, weshalb die Projekt-`CLAUDE.md` ihn heute schon mit Vorsicht behandelt.

**T2.3 Der Grenzfall braucht eine Regel.** Wächst eine Planung beim Ausarbeiten über die zehn Sätze hinaus, bleibt sie nicht im Fahrplan stehen, sondern wandert an einen der beiden anderen Orte und hinterlässt dort einen Verweis. Ohne diese Regel wandert die Grenze in der Praxis immer nach oben.

**T2.4 Die Ableitung aus dem Kontext-Haushalt ist mitzuändern.** „Detaillierung des Fahrplans vor der Komprimierung" muss lauten: die Planung **an ihrem Ort** vertiefen und im Fahrplan darauf verweisen. Sonst bleibt genau die Aufforderung stehen, die zum Ausbau des Fahrplans führt — und sie greift ausgerechnet dann, wenn der Kontext knapp ist und niemand mehr nachdenkt.

**T2.5 Der Review-Anhang bleibt, verliert aber seinen Sonderstatus.** Ein Befund wird weiterhin im Anhang der Doku bearbeitet. Das ist dann kein Ausnahmefall von der Fahrplan-Regel mehr, sondern der Anwendungsfall von Zielort 2: eine Planung, deren Begründung überdauern muss.

**T2.6 Was nach der Ausführung mit der Planung geschieht, ist zu regeln.** Im Fahrplan wurde der Plan bisher „ersetzt". Für ein eigenes Planungsfile fehlt die Entsprechung, und ohne sie entsteht ein Friedhof unausgeführter Dateien. Vorschlag: Was zur Beurteilung der Ausführung nötig bleibt, wandert in die Doku — Kapitel oder Anhang, nach derselben Grenze, die dieser Skill dafür schon kennt; das Planungsfile wird danach gelöscht, und die Zeile in `status.md` nennt es. Damit bleibt „höchstens ein unausgeführter Plan gleichzeitig" als Regel erhalten, nur nicht mehr auf den Fahrplan beschränkt.

**T2.7 Unberührt bleiben** die Nummernregel, „Erledigtes fliegt raus" und die Trennung von Status und Entscheidung. Sie waren nie das Problem.

**T2.8 Ohne Installation wirkt nichts davon.** Der Skill muss an einen Ladeort kopiert und der stille Trigger aus `CLAUDE-snippet.md` in die `CLAUDE.md` des Zielorts übernommen werden, die Datei danach am Zielort gelöscht (`implementation_doku.md` 5). Erst dann ist die Frage überhaupt beantwortbar, ob er auslöst. Mit dem Umzug aus T1 wächst außerdem sein Gegenstand: Die `description` nennt heute „Fahrplan und Status" beiläufig am Ende — sie ist daraufhin durchzusehen, ob sie den erweiterten Inhalt noch trägt.

### T3 — Diese Datei hat am Ende zu verschwinden

`implementation_doku.md` 5 lässt Zusatzdateien nur zu, wenn die `SKILL.md` auf sie verweist, und 6.1 weist offene Punkte der `README.md` des Skills unter „Offen" zu. Diese Datei steht also neben der Vorgabe; sie ist Arbeitsmaterial für einen Umbau, der mehrere Dateien außerhalb dieses Ordners betrifft, und dafür in der README am falschen Platz. Ist der Umbau ausgeführt, wandert das Verbliebene unter „Offen" in die `README.md`, und diese Datei wird gelöscht.
