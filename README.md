Prerequisites
Note: It is assumed that Python is already installed.

Setting up venv
If you want to set up a python virtual environment for the project, follow the below instructions:

python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

To run the game, use the Maze executable.
./Maze


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
└── settings.py
└── inputbox.py
└── login.py
└── README.md


