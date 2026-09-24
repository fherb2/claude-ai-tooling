## 3.11 Der stille Trigger in `CLAUDE.md`

Stand (2026-09-24): neu angelegt. Wortlaut nach dem Vorbild des Vorläufers (Anhang A.11), an diesen Skill angepasst; konsolidiert aus Kapitel 1.3.5, 1.8, 3.9.1 und 3.9.4.

### 3.11.1 Zweck

> Dieser Text lebt nicht im Skill, sondern in der `CLAUDE.md` des Projekts oder Nutzers — er ist der Auslöser, der zuverlässig feuert, auch wenn der Skill sonst nicht geladen wäre (Kapitel 1.3.5). Ohne ihn liefe der Skill nur bei ausdrücklichem Aufruf.

### 3.11.2 Wortlaut

> **Software-begleitende Dokumentation.** Bevor du in einer Sitzung zum ersten Mal einen Lösungsweg vorschlägst oder zum ersten Mal eine Datei änderst, halte kurz inne und prüfe: Geht die besprochene Software-Änderung über eine einzelne, lokal begrenzte Korrektur hinaus — sind mehrere Stellen betroffen, müssen mehrere Vorgehensweisen gegeneinander abgewogen werden, oder müssen erst Zusammenhänge im bestehenden Code erarbeitet werden, bevor klar ist, was zu ändern ist? Wenn ja, konsultiere sofort den Skill `software-design-doc`.

Der Wortlaut ist bewusst an eine Ankerhandlung gebunden („bevor du zum ersten Mal …"), nicht als Haltungsbeschreibung formuliert — die Begründung dafür steht in Kapitel 1.2 und gilt hier unverändert; sie wird hier nicht wiederholt.

### 3.11.3 Wo der Text steht und was daneben in die `CLAUDE.md` kommt

> Nichts außer diesem einen Absatz. Kein Verweis auf `mode: off`, keine sonstige Skill-Logik — das behandelt der Skill selbst beim Start (Kapitel 3.10), nicht der Trigger. Der Anker feuert immer; ein Ladevorgang mit sofortigem Ende bei `mode: off` ist billiger als zwei Stellen, die zusammenpassen müssten (entschieden am 2026-09-24, vormals Q-31).

Vorbereitet wird der Text in `CLAUDE-snippet.md`, unterhalb einer Trennlinie. Beim Installieren wird alles unterhalb der Trennlinie in die `CLAUDE.md` des Zielorts übernommen; die Snippet-Datei selbst bleibt am Zielort liegen (Kapitel 3.9.4).
