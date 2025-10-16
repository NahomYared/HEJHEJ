## Prerequisites
Python 3.x installerat.

## Set up venv
```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

Run game
./Maze
# eller
python game.py

├── data
│   ├─ game.db           # SQLite-databas för användare, scores, progress
│   ├─ LeastTimes.txt    # Bästa tider (en rad per nivå)
│   └─ path.txt
├── media
│   ├── fonts
│   ├── images
│   ├── sounds
│   └── videos
├── Modules
│   ├── __init__.py
│   └── Authdb           # Databashanterare, läser och skriver till databasen
│   └── Countries.py
│   └── Inbox.py
│   └── Login.py
│   ├── MainMenu.py
│   ├── PlayGame.py
│   ├── Preferences.py
│   └── Scores.py
│   └── Scores.db
├── OtherResources
├── report
├── venv
├── game.py
├── settings.py
├── inputbox.py
├── login.py
└── README.md

