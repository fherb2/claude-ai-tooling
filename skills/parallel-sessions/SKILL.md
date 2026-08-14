---
name: parallel-sessions
description: Klärt die Zusammenarbeit, wenn mehrere Claude-Code-Instanzen gleichzeitig im selben Repository arbeiten — wer darf schreibende Git-Kommandos ausführen, und wie trennt man die Arbeitsstände sauber über Worktrees. Verwenden, sobald Anzeichen für eine zweite gleichzeitig arbeitende Instanz auftreten oder der Nutzer parallele Arbeit ankündigt, oder wenn der Nutzer /parallel-sessions aufruft.
license: CC0-1.0
---

# Parallel arbeitende Instanzen und Worktrees

## Warum das geklärt werden muss, bevor irgendetwas passiert

Zwei gleichzeitig laufende Claude-Code-Instanzen im selben Repository teilen sich einen einzigen Arbeitsbaum und einen einzigen ausgecheckten Branch. Was die eine committet, nimmt ungefragt mit, was die andere gerade geändert hat; was die eine zurücksetzt, vernichtet die Arbeit der anderen. Das Tückische daran ist nicht der Konflikt — den würde Git melden —, sondern das lautlose Mitwandern.

Deshalb zwei Dinge, in dieser Reihenfolge: erst die Schreibhoheit klären, dann das Arbeitsmodell.

## Schritt 1: Schreibhoheit für Git klären

Sobald erkennbar ist, dass eine zweite Instanz arbeitet, wird der Nutzer gefragt, **welche Instanz eigenständig schreibende Git-Kommandos ausführen darf** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`). Bis zur Antwort führt diese Instanz keines davon aus — lesende Kommandos wie `status`, `diff`, `log` und `fetch` bleiben erlaubt.

Der Nutzer muss das **jeder** Instanz einzeln sagen; eine Instanz kann nicht wissen, was er einer anderen mitgeteilt hat. Hat eine Instanz die Hoheit einmal erhalten, muss sie nicht bei jedem Commit erneut nachfragen. Der Nutzer kann sie im Verlauf umverteilen und meldet sich dafür aktiv.

## Schritt 2: Worktrees als sauberere Alternative anbieten

Ist absehbar, dass die parallele Arbeit länger anhält oder sich auf verschiedene Themen bezieht, wird dem Nutzer das Worktree-Modell vorgeschlagen — kurz und ohne Drängen, denn es ist eine Änderung seiner Arbeitsweise, keine technische Notwendigkeit.

**Was ein Worktree ist:** ein zweiter Arbeitsbaum desselben Repositorys in einem eigenen Verzeichnis, mit eigenem ausgechecktem Branch, aber gemeinsamer Git-Historie. Beide Instanzen arbeiten dann in getrennten Verzeichnissen und können sich nicht mehr gegenseitig überschreiben. Ein Branch kann dabei immer nur in einem Worktree gleichzeitig ausgecheckt sein — das erzwingt Git von sich aus und ist genau die gewünschte Trennung.

**Wie es eingerichtet wird**, zwei Wege:

- **Über Claude Code selbst:** Das Werkzeug `EnterWorktree` legt einen Worktree unter `.claude/worktrees/` an und wechselt die laufende Sitzung hinein. Es erzeugt dabei **immer einen neuen Branch**, nie den bereits ausgecheckten. Als Basis dient standardmäßig `origin/<default-branch>`; über die Einstellung `worktree.baseRef` mit dem Wert `head` wird stattdessen vom aktuellen lokalen HEAD abgezweigt. `ExitWorktree` verlässt ihn wieder, wahlweise unter Beibehalten oder Entfernen.
- **Von Hand:** `git worktree add <pfad> -b <neuer-branch> <basis>` legt ihn an beliebiger Stelle an; `git worktree list` zeigt alle, `git worktree remove <pfad>` räumt auf.

**Was der Nutzer dabei wissen sollte:** Der zweite Weg ist der flexiblere, weil er Ort und Basis frei bestimmt. Der erste ist bequemer, bindet den Worktree aber an das vorgesehene Verzeichnis und leitet ihn ohne die genannte Einstellung vom Default-Branch ab — nicht vom Branch, auf dem gerade gearbeitet wird.

## Was dieser Skill bewusst nicht entscheidet

Arbeitet ein Projekt mit einem festen Branch-Namen für Claudes Arbeitsstand, kollidiert dieser mit dem Worktree-Modell: Mehrere gleichzeitige Worktrees brauchen mehrere Branch-Namen, und derselbe Branch lässt sich nicht zweimal auschecken. Wie das aufgelöst wird — festes Namensschema mit Zusatz, freie Vergabe, oder ein anderer Weg —, ist eine Festlegung des jeweiligen Projekts und gehört in dessen `CLAUDE.md`, nicht in diesen Skill. Ebenso, ob und wie projekteigene Zustandsdateien mit Branch-Bezug bei einem Zusammenführen mitwandern sollen.

Trifft dieser Fall zu, wird er dem Nutzer benannt und ihm die Entscheidung überlassen — nicht stillschweigend ein Schema erfunden.
