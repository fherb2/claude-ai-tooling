## 3.8 Die Probe

Stand (2026-09-17): Vorschlag; die Messgrößen und Schwellen sind vom Entwickler noch nicht bestätigt.

### 3.8.1 Zweck

Die logische und codetechnische Seite des Vorhabens gilt als durchdrungen; was bleibt, ist empirisch und durch Nachdenken nicht zu klären: ob die Instanz die Marken in der Praxis setzt, ob sie Kollisionen parkt statt abzuschießen, wie hoch die Fehlalarmquote des Lints ist, wie lang die Kandidatenlisten werden und was der Skill an Kontext kostet. Die Probe ist das Tor vor der Migration (Kapitel 3.9): Scheitert sie an Marken oder Parken, ist das Design falsch; scheitert sie an Kandidaten oder Lint, werden Parameter justiert.

### 3.8.2 Fixture

Eine kleine Doku im Dreiersschema mit Rollen: ein Kapitel `relate` mit drei Absätzen und Zitatmarken, zwei Kapitel `building-blocks`, ein Abschnitt `crosscutting`, acht bis zehn Festlegungen — darunter zwei `given`, eine `pinned`, eine mit zwei `friction`-Zeilen, eine `superseded` —, drei geplante Schritte, einer mit `target:`, eine Parameterdatei mit Standardwerten, ein Code-Ordner mit ID-Kommentaren für `mentions`. Dazu beschädigte Varianten für die Prüffälle (Kapitel 3.6).

### 3.8.3 Ablauf

Je eine Sitzung in der Lage `execute` (ein geplanter Schritt, der zwei Festlegungen berührt) und in der Lage `design` (eine Idee, die eine `decided`- und eine `pinned`-Festlegung verletzt). Beide Sitzungen je einmal mit `impact_model: hops` und mit `weighted`, dazu die drei Kostenfunktionen im Vergleich auf denselben Änderungen. Ein zweiter Durchlauf an einer echten Doku des Entwicklers ist empfohlen, weil die Fixture nicht seine Doku ist.

### 3.8.4 Messgrößen und Schwellen

| Messgröße | Schwelle für „weiter" |
|---|---|
| Marken bei Kontakt gesetzt, ohne Erinnerung durch H1 | mindestens 80 %; mit H1 100 % |
| Fehlalarme des Lints | höchstens einer je zehn Doku-Edits |
| Kandidatenliste `execute` / `design`, Median | höchstens 8 / höchstens 20; die Instanz verwirft mindestens die Hälfte nicht als irrelevant |
| Parken statt Abschuss in `design` | jede Kollision mit `decided` wird geparkt, keine als Ablehnung formuliert |
| Kontext-Mehraufwand auf Doku-Schritten | höchstens 20 % gegenüber demselben Schritt ohne Skill, grob aus dem Kontextverbrauch |
| Inkonsistenzen, die einen Commit überleben | keine |
| Fingerabdruck-Rauschen | höchstens eine Fehlmeldung je zehn kosmetische Edits |

> **[Q-28] Entscheidungsgrundlage — Messgrößen und Schwellen der Probe**
> Kontext: Die Tabelle in 3.8.4 ist mein Vorschlag. Die Schwellen entscheiden, ob das Vorhaben in die Migration geht oder zurück ins Design. Zu streng heißt Stillstand; zu locker heißt, dass die zwei Fehlbilder zurückkommen.
> Optionen: je Zeile (a) übernehmen, (b) Schwelle ändern, (c) Messgröße streichen oder ergänzen.
> Vorschlag: übernehmen; die Zeile „Kontext-Mehraufwand" ist die unsicherste, weil grob messbar.
> Gewicht: mittel · Blockiert: Fahrplanschritt 8
> Antwort:

### 3.8.5 Entscheidungstor

Marken- oder Park-Schwelle verfehlt → zurück zu Kapitel 3.1 und 3.2, nicht weiter zu Kapitel 3.9. Kandidaten- oder Lint-Schwelle verfehlt → Parameter justieren, Probe wiederholen. Alle Schwellen erreicht → Entscheidung der Verzweigungen (Kostenfunktion, Fingerabdruck, H3, Zitatmarken außerhalb `relate`) und Freigabe der Migration.

### 3.8.6 Was das Rechenmodell vorab sagt

Das synthetische Modell im Anhang (acht Kapitel, zufällig verteilte Festlegungen, ein `relate`-Absatz zitiert je vier) ergibt für die Größe der Kandidatenliste je geänderter Festlegung: Tiefe 1 Median 4 bis 5 in jeder Dokugröße; Tiefe 2 Median 7 (40 Festlegungen), 14 (120), 22 (300); gewichtet mit Abbruch 0,40 wie Tiefe 1, mit 0,25 wie Tiefe 2. Das Modell kennt keine Relevanz; deshalb die Messgröße „verwirft mindestens die Hälfte nicht".
