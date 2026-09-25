## 3.8 Die Probe

Stand (2026-09-24): Vorschlag; die Messgrößen und Schwellen sind vom Entwickler bestätigt (vormals Q-28, Kapitel 1.9).

### 3.8.1 Gegenstand

**Wozu die Probe da ist und was ihr Ausgang entscheidet, steht in Kapitel 1.9.** Hier steht, wie sie aufgebaut ist: woran gemessen wird, in welcher Reihenfolge, und bei welchem Wert der Weg abzweigt.

### 3.8.2 Fixture

Eine kleine Doku im Dreiersschema des Vorläufers (Anhang A) mit Rollen: ein Kapitel `relate` mit drei Absätzen und Zitatmarker, zwei Kapitel `building-blocks`, ein Abschnitt `crosscutting`, acht bis zehn Festlegungen — darunter zwei `given`, eine `pinned`, eine mit zwei `friction`-Zeilen, eine `superseded` —, drei geplante Schritte, einer mit `target:`, eine Skill-Parameterdatei mit Standardwerten, ein Code-Ordner mit ID-Kommentaren für `mentions`. Dazu beschädigte Varianten für die Prüffälle (Kapitel 3.6).

### 3.8.3 Ablauf

Je eine Sitzung in der Lage `execute` (ein geplanter Schritt, der zwei Festlegungen berührt) und in der Lage `design` (eine Idee, die eine `decided`- und eine `pinned`-Festlegung verletzt). Beide Sitzungen je einmal mit `impact_model: hops` und mit `weighted`, dazu die drei Kostenfunktionen im Vergleich auf denselben Änderungen. Ein zweiter Durchlauf an einer echten Doku des Entwicklers ist empfohlen, weil die Fixture nicht seine Doku ist.

### 3.8.4 Messgrößen und Schwellen

| Messgröße | Schwelle für „weiter" |
|---|---|
| Marker bei Kontakt gesetzt, ohne Erinnerung durch H1 | mindestens 80 %; mit H1 100 % |
| Fehlalarme des Lints | höchstens einer je zehn Doku-Edits |
| Kandidatenliste `execute` / `design`, Median | höchstens 8 / höchstens 20; die Instanz verwirft mindestens die Hälfte nicht als irrelevant |
| Parken statt Abschuss in `design` | jede Kollision mit `decided` wird geparkt, keine als Ablehnung formuliert |
| Kontext-Mehraufwand auf Doku-Schritten | höchstens 20 % gegenüber demselben Schritt ohne Skill, grob aus dem Kontextverbrauch |
| Inkonsistenzen, die einen Commit überleben | keine |
| Fingerabdruck-Rauschen | höchstens eine Fehlmeldung je zehn kosmetische Edits |

### 3.8.5 Entscheidungstor

Marker- oder Park-Schwelle verfehlt → zurück zu Kapitel 3.1 und 3.2, nicht weiter zu Kapitel 3.9. Kandidaten- oder Lint-Schwelle verfehlt → Skill-Parameter und Graphenparameter justieren, Probe wiederholen. Alle Schwellen erreicht → Entscheidung der Verzweigungen (Kostenfunktion, Fingerabdruck, H3, Zitatmarker außerhalb `relate`) und Freigabe der Migration.

**Befund B-15 (2026-09-25): Die Liste der Verzweigungen ist überholt.** Sie stammt aus der Zeit, als alle vier Punkte noch ganz offen waren; zwei sind es nicht mehr. Beim **Fingerabdruck** ist seit dem 2026-09-24 entschieden, dass es ihn gibt und wie er arbeitet — offen ist allein die Schwelle der Edit-Distanz, unterhalb derer eine Abweichung als bloße Formatierung gilt (Kapitel 3.6.7). Diese Schwelle wird ohnehin über die Messgröße „Fingerabdruck-Rauschen" in der Tabelle oben kalibriert; sie ist also eine Einstellung, keine Verzweigung. Bei **H3** ist die Lage umgekehrt und ungeklärt: Ob er überhaupt gebaut wird, steht als offene Entscheidung in Kapitel 1.7.6 — und der Fahrplan baut ihn in Schritt 6, also vor dieser Probe. Unverändert richtig sind die **Kostenfunktion**, die hier tatsächlich erst entschieden wird (Kapitel 3.6.5), und die **Zitatmarker außerhalb `relate`**. Zu tun: Fingerabdruck von der Verzweigung zur Schwelle umschreiben; H3 entweder hier streichen, weil er vorher entschieden wird, oder im Fahrplan hinter die Probe rücken.

### 3.8.6 Was das Rechenmodell vorab sagt

Das synthetische Modell in Anhang B (acht Kapitel, zufällig verteilte Festlegungen, ein `relate`-Absatz zitiert je vier) ergibt für die Größe der Kandidatenliste je geänderter Festlegung: Tiefe 1 Median 4 bis 5 in jeder Dokugröße; Tiefe 2 Median 7 (40 Festlegungen), 14 (120), 22 (300); gewichtet mit Abbruch 0,40 wie Tiefe 1, mit 0,25 wie Tiefe 2. Das Modell kennt keine Relevanz; deshalb die Messgröße „verwirft mindestens die Hälfte nicht".
