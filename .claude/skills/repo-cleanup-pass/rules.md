# Tiefenprüfung über die Bereiche

Diese Datei gilt nur, wenn der Nutzer die Tiefenprüfung gewählt hat. **Sie kommt vor dem Datei-Abgleich**, und die aus ihr erwachsenden Korrekturen gehören in den Entwicklungszweig, bevor irgendetwas in den Release-Zweig wandert.

Fünf Etappen, in dieser Reihenfolge. Jede endet mit einem Checkpoint-Commit.

**Nicht geprüft werden** die Skills mit Baustellenschild im Ordnernamen. Sie sind unfertig, und zwar absichtlich; ein Befund über sie ist keiner.

---

## 1 Die Wurzel-READMEs: Vollständigkeit und Genauigkeit

Es gibt zwei, und sie sind in der Wurzel sprachlich vertauscht: `README.md` trägt die englische Fassung, `README.de.md` die deutsche. **Beide werden geprüft und beide nachgezogen** — was in einer geändert wird, wird in der anderen mitgeändert.

**Vollständigkeit:** Jeder Bereichsordner der Projektwurzel muss in der Übersichtstabelle vorkommen. Ein Bereich, den nur der Entwicklungszweig kennt, fehlt in der Tabelle des Release-Zweigs mit — dann ist beides zu richten.

**Genauigkeit — vier Sorten Aussagen veralten hier zuverlässig:**

- **Die Reifezeichen** hinter dem Ordnernamen (`✅` einsatzbereit, `🚧` in Arbeit, `⚠️` mit Vorbehalt, `☑` abhängig vom Skill). Sie sind die kürzeste Aussage der ganzen Seite und die am leichtesten überholte. Ein Vorbehalt, der aufgehoben wurde, muss hier verschwinden.
- **Die Standzeile** je Bereich. Sie nennt Betriebszustand und Freigabe. Steht dort eine Einschränkung, die nicht mehr gilt, ist das keine Ungenauigkeit, sondern eine falsche Aussage über ein Werkzeug, das andere benutzen sollen.
- **Die Sprachverweise.** In der englischen Wurzel-README zeigen alle Bereichsverweise auf die **englische** README des Bereichs. Entsteht eine englische Fassung neu, ist der Verweis nachzuziehen und ein Zusatz wie „(in German)" zu entfernen — sonst bleibt genau ein Bereich zurück, der auf Deutsch verweist.
- **Die Auslieferungsform.** Bekommt ein Bereich Download-Pakete, gehört das in seinen Absatz; die Wurzel-README erfährt davon sonst nie.

**Kein Befund ist**, was die Seite selbst begründet. Fehlt einem Ordner die eigene README und sagt die Wurzel-README, das sei Absicht, dann ist es Absicht.

**Zum Schluss die Datumszeile beider Fassungen nachziehen** (siehe Etappe 3).

---

## 2 Bereichs- und Skill-READMEs: Datumszeile und Sprach-Querverweis

```bash
bash .claude/skills/repo-cleanup-pass/files/readme-audit.sh
```

Das Skript listet jede versionierte README mit ihrem Datum, dem Zustand ihres Querverweises und dem Namen der zweiten Sprachfassung. Zu lesen ist es so:

- **`FEHLT` beim Querverweis ist ein Befund**, `entfaellt` nicht — letzteres heißt, dass es keine zweite Fassung gibt.
- **`KEINS` beim Datum ist immer ein Befund.**

**Die Form des Querverweises** ist die kursive Zeile unmittelbar unter der Datumszeile, vor dem ersten Absatz:

```markdown
*[English version](README.en.md)*
*[Deutsche Fassung](README.md)*
```

Andere Formen — etwa ein Blockzitat — werden angeglichen. Die Regel selbst, dass die deutsche README ganz oben auf die englische verweist, steht in der Projekt-`CLAUDE.md`.

**Vor dem Melden nachsehen, ob der Bereich es anders festgelegt hat.** Ein Vorgabenteil eines Bereichs kann die repo-weite Regel überschreiben; erst wenn er dazu schweigt, ist ein fehlender Verweis ein Verstoß.

**Ein Nebeneffekt, der teuer werden kann:** Bei Skills wandert die README ins Download-Paket. Eine Änderung an ihr macht damit jedes Paket ihrer Sprache veraltet — Etappe 4 ist dann nicht optional, sondern Folge dieser Etappe.

### Der Querverweis in Dateien, die ins Paket wandern

**Festlegung des Entwicklers vom 10. September 2026:** In einer Datei, die als Paketinhalt ausgeliefert wird, zeigt der Sprach-Querverweis auf die **Repo-URL**, nicht auf einen relativen Pfad.

Der Grund ist nicht Ästhetik, sondern eine falsche Aussage: Im Paket heißt die enthaltene README `README.md`, gleich welcher Sprache. Ein relativer Verweis `[Deutsche Fassung](README.md)` in der englischen Fassung zeigt dort auf **sie selbst** — der Leser klickt und bleibt, wo er war. In der deutschen Fassung zeigt `[English version](README.en.md)` ins Leere. Der Verweisprüfer aus Etappe 5 sieht nur den zweiten Fall; der erste ist der schlimmere.

Die Umstellung des Bestands war am 10. September 2026 beschlossen, aber noch nicht überall ausgeführt. Wer diese Etappe fährt, prüft mit.

---

## 3 Datumszeilen nachziehen

```bash
bash .claude/skills/repo-cleanup-pass/files/datelines-since.sh <ref>
```

`<ref>` ist der Stand, gegen den verglichen wird — der Commit vor Beginn des Durchgangs oder der Release-Zweig.

Zwei Regeln entscheiden:

- **Das Datum gehört zur Datei, nicht zum Paar.** Wird nur die englische Fassung inhaltlich geändert, trägt nur sie das neue Datum. Zwei verschiedene Daten in einem Sprachpaar sind richtig, nicht schlampig.
- **Inhaltlich geändert** heißt: mehr als Leerraum. Ein hinzugefügter Querverweis ist eine inhaltliche Änderung.

Die zweite Liste des Skripts — geändert, aber ohne Datumszeile — ist zur Kontrolle da und meistens leer von Befunden: Quelltext, Entwicklungsdateien wie Fahrplan und Implementierungsdoku, Archive und die `CLAUDE.md` selbst tragen keine.

---

## 4 Download-Pakete auf den Stand ihrer Quellen bringen

**Ein Paket ist eine Kopie und veraltet in dem Moment, in dem sich eine seiner Quelldateien ändert.** Von außen ist das nicht zu sehen — deshalb ist diese Etappe Pflicht, sobald Etappe 2 oder 3 eine Datei angefasst hat, die im Paket liegt.

**Zuerst feststellen, ob das Paket vor der eigenen Änderung überhaupt aktuell war.** Sonst nimmt das Neupacken fremde Abweichungen stillschweigend mit auf, und niemand erfährt davon. Praktisch: den Hash der Datei im Paket gegen die Quelle im letzten Commit vor dem Durchgang halten.

**Wenn sich nur die README geändert hat** — der Regelfall dieses Durchgangs:

```bash
bash .claude/skills/repo-cleanup-pass/files/repack-package-readme.sh skills/<skill> <paket>.zip
```

Das Skript baut das Archiv aus **seinem eigenen Inhalt** neu und tauscht allein `README.md` aus. Damit kann der Schritt keinen Eintrag verlieren und keinen hinzufügen — die Gefahr beim Neubau aus einer Dateiliste. Es prüft danach selbst: alle übrigen Einträge unverändert, die enthaltene README zeichengleich mit der Quelle. Sein Rückgabewert ist 1, wenn eines von beidem nicht stimmt.

**Wenn sich die Dateiliste geändert hat** — eine Datei kommt hinzu oder entfällt —, reicht das nicht: Dann wird das Paket mit dem Packer aus `skill-dev-doc.md`, Anhang A.1 neu gebaut, weil nur dort die Zuordnung von Quell- zu Zielnamen samt der Umbenennungen steht. Die Packweise ist in beiden Fällen dieselbe: `zip -9 -o -X`, Einträge sortiert übergeben.

**Die Zeitstempel gehören zur Prüfung.** Vergleicht man `unzip -l` vor und nach dem Packen, darf sich genau die Zeile der ausgetauschten Datei bewegt haben.

**Der Aktualitätsprüfer aus `skill-dev-doc.md` A.3 gilt nur für Skills.** Er vergleicht den Inhalt jedes Archiveintrags gegen die Dateien im **Wurzelordner** des Bereichs — bei einem Skill liegen sie genau dort. `home-.claude-sharing` hält seine Werkzeuge dagegen in `files/`, und dann meldet der Prüfer jedes Paket als veraltet, obwohl keines es ist. Für diesen Bereich beantwortet das die Frage ohnehin nicht mehr von Hand: `home-.claude-sharing/scripts/pack_packages.sh` laufen lassen und danach `git status` ansehen. Das Werkzeug baut beide Archive neu und prüft sie gegen `files/` und die beiden READMEs; **bei unverändertem Bestand sind die Archive byte-identisch** (gemessen am 11. September 2026), ein geändertes Zip im Arbeitsbaum ist also der Nachweis, dass das Paket veraltet war — und gleichzeitig schon die Behebung. Ein „VERALTET" ohne konkrete Abweichung in der Datei ist zuerst ein Verdacht auf diesen Fehlgriff, nicht auf ein altes Paket.

---

## 5 Der Verweisprüfer über alle Pakete

Das Werkzeug steht als Quelltext in `skill-dev-doc.md`, Anhang A.2. Ausgeführt aus `skills/` heraus prüft es jedes Paket jedes Skills und meldet Verweise auf `.md`- und `.py`-Dateien, die im Archiv nicht liegen.

**Seine Meldungen sind nicht alle Fehler. Drei Klassen, und sie werden verschieden behandelt:**

| Klasse | Erkennungsmerkmal | Was zu tun ist |
| --- | --- | --- |
| **Datei fehlt im Paket** | Die Datei existiert im Skill-Ordner | Echte Lücke: Der Nutzer bekommt einen Verweis auf etwas, das er nicht hat. Paket ergänzen — Dateiliste, also Anhang A.1 |
| **Überholter Verweis** | Die Datei existiert nirgends | Der Verweis ist zu entfernen oder richtigzustellen, nicht die Datei zu erfinden |
| **Legitim repo-extern** | Eine Datei des Repositories, die nie mitreist (`skill-dev-doc.md`, `implementation-doc.md`, `CLAUDE.md`) | Kein Befund. Wiederholt sich die Meldung bei jedem Durchgang, gehört der Name in die `EXTERN`-Menge des Prüfers |

**Der Prüfer prüft nur Existenz, nicht Sinn.** Ein Verweis, der im Paket auf die falsche Datei zeigt, gilt ihm als in Ordnung — siehe die Begründung zur Repo-URL in Etappe 2. Wer sich auf ihn allein verlässt, hält den unbelegten Teil für belegt.

---

## Danach

Erst wenn die Befunde dieser fünf Etappen besprochen und die beschlossenen Korrekturen im Entwicklungszweig committet sind, folgt der Datei-Abgleich aus der `SKILL.md`. Er überträgt dann einen Stand, der nicht gleich wieder korrigiert werden muss.
