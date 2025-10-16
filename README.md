Maze Countries

Ett litet Pygame-baserat spel där du navigerar i labyrinter, låser upp länder och jagar bästa tiderna.
Autentisering och speldata lagras lokalt i en SQLite-databas (data/game.db). High scores för tre svårighetsgrader sparas i en textfil.

# Innehåll

## Funktioner

## Demo / Screens

## Installation

## Kör spelet

## Kontroller

## Projektstruktur

## Data & beständighet

## Databasschema (rekommenderat)

## High scores

## Inställningar

## Länder & städer


# Funktioner

Labyrinter med tre nivåer (Easy/Medium/Hard) och tidsmätning per försök. Banor genereras rekursivt; spelaren startar längst ned till höger och målet är uppe till vänster. 

## PlayGame

Animerad spelare med WASD/piltangenter. Spelaren renderas med riktade sprites och enkel gånganimation. 

## PlayGame

Huvudmeny, poängvy och preferenser (musik på/av).

Bästa tider per level sparas och visas; tiderna lagras i sekunder i en textfil. 

Scores

Länder som spelinnehåll (t.ex. upplåsningar/urval); lista över länder och större städer finns i källan. 

countries

## Demo / Screens

(Lägg gärna in GIFs eller screenshots här. Filvägarna till sprites och bakgrunder pekas i spelet när resurserna laddas.) 

PlayGame

Installation

Krav: 
- Python 3.10+, 
- Pygame pip install pygame
- Repo & resurser: Klona projektet och säkerställ att mappstrukturen data/, modules/ samt bild-/ljudresurser finns enligt nedan.

## Kör spelet

Normalt startas spelet via Game.py (spelmotorn). Kommando: python(3) game.py

Huvudmenyn ritar knappar och hanterar klick/sound. 

- MainMenu: När spelet körs skapas/genereras en labyrint för vald nivå. 

- PlayGame

Obs: Om du vill köra komponenterna fristående för test:

Maze och gameplay finns i PlayGame.py. 

PlayGame

High scores-hantering i Scores.py. 

Scores

Menyknappar i MainMenu.py. 

MainMenu

Kontroller

Flytta: WASD eller piltangenter

Spelet uppdaterar spelarens riktning/animation när en rörelseriktning hålls inne. 

PlayGame

Projektstruktur
.
├─ data/
│  ├─ game.db           # SQLite-databas för användare, scores, progress
│  ├─ LeastTimes.txt    # Bästa tider (en rad per nivå)
│  └─ path.txt          # (debug/assist) genererad lösningsväg för maze
├─ modules/
│  └─ authdb/           # AuthDB: lagring/hantering av användare (modul)
├─ Game.py              # Spelmotor / app-entry
├─ PlayGame.py          # Maze, spel-loop, rendering, kollisioner
├─ MainMenu.py          # Meny & knappar
├─ Scores.py            # High score-hantering och vy
├─ Preferences.py       # Musik/ljud-preferenser
├─ countries.py         # Länder + huvudstäder/städer (datastruktur)
└─ README.md


MainMenu.py: Renderar knappar, hanterar hover/klick och validerar klick-rektangeln. 

MainMenu

PlayGame.py:

Maze: genererar labyrint med rekursiv carving; stöd för DFS/A* för test & path-dump. 

PlayGame

GamePlay: sköter nivåer (20×20, 30×30, 40×40), rendering av celler (vägg/stig/start/mål), spelartimer och game-over. 

PlayGame

Scores.py: Läser/uppdaterar bästa tider i LeastTimes.txt och ritar dem på skärmen. 

Scores

Preferences.py: Enkel behållare för musikpå/av. 

Preferences

countries.py: Konstant med länder → städer (EU/Europa m.fl.). 

countries

Data & beständighet

SQLite under data/game.db för konton, försök/resultat och progress.

High scores i data/LeastTimes.txt (tre rader: Easy/Medium/Hard). Exempel initialt innehåll:

61
100000
100000


(lägre är bättre; uppdateras vid förbättring) 

LeastTimes

Maze path (debug) skrivs till data/path.txt när en bana genereras och löses (A*) för referens.

Databasschema (rekommenderat)

Följande tabeller matchar användningsfallet “konton → många scores” samt “konton → många upplåsta länder”.

-- users: en rad per användare (autentisering)
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  pw_salt BLOB NOT NULL,
  pw_hash BLOB NOT NULL,
  created_at INTEGER NOT NULL
);

-- scores: flera försök per användare och nivå
CREATE TABLE IF NOT EXISTS scores(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  level INTEGER NOT NULL,
  time_sec INTEGER NOT NULL,       -- varaktighet, inte tidsstämpel
  created_at INTEGER NOT NULL      -- när försöket loggades
);

-- progress: vilka länder användaren låst upp (mängd utan dubbletter)
CREATE TABLE IF NOT EXISTS progress(
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  country_id TEXT NOT NULL,
  PRIMARY KEY(user_id, country_id)
);


Varför så?

users.id är stabil PRIMARY KEY som andra tabeller pekar på via FOREIGN KEY (tydlig 1→N-relation).

scores loggar alla försök; bästa tid kan hämtas med MIN(time_sec) eller materialiseras separat.

progress har sammansatt PK för att göra (user_id, country_id) unikt och idempotent att uppdatera.

High scores

Fil: data/LeastTimes.txt med en rad per nivå (Easy/Medium/Hard). Vid bättre tid skrivs filen om på rätt rad. Rendering görs med en rubrik per nivå och suffix “SEC”.

Inställningar

Preferences håller t.ex. musikläge i minne under körning (boolean). 

Preferences

Länder & städer

Datastrukturen i countries.py mappar land → lista av större städer (ex. “Sweden” → “Stockholm”, “Gothenburg”, “Malmö”). Kan användas för upplåsningar/progression i spelet.
