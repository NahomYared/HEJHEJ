# Modules/ScoresDB.py
import pygame
from . import AuthDB

class HighScores:
    def __init__(self, screen, _csv_path_unused, title_font):
        self.screen = screen
        self.title_font = title_font
        self.is_active = False
        self.isUpdated = False  # sätts i UpdateScore för "NEW HIGH SCORE"

        # mindre font för rader
        self.row_font = pygame.font.Font("media/fonts/ArialRoundedMTBold.ttf", 24)
        self.label_font = pygame.font.Font("media/fonts/MightySouly.ttf", 28)

    def HighScore(self, level: int) -> str:
        rows = AuthDB.top_times(level, limit=1)
        if rows:
            return str(rows[0][1])  # sekunder som sträng
        return "—"

    def UpdateScore(self, time_sec: float, level: int):
        """Används av ditt Game Over-flöde för att avgöra om det blev 'NEW HIGH SCORE'."""
        rows = AuthDB.top_times(level, limit=1)
        best = rows[0][1] if rows else None
        self.isUpdated = (best is None) or (int(time_sec) < int(best))

    def _draw_column(self, x_center: int, level: int, title: str):
        # Rubrik
        title_surf = self.label_font.render(title, True, "White")
        self.screen.blit(title_surf, title_surf.get_rect(center=(x_center, 150)))

        # Top 10 från DB
        rows = AuthDB.top_times(level, limit=10)  # [(username, best), ...]
        y = 190
        rank = 1
        for username, best in rows:
            line = f"{rank}. {username} — {best} s"
            surf = self.row_font.render(line, True, "White")
            rect = surf.get_rect(center=(x_center, y))
            self.screen.blit(surf, rect)
            y += 32
            rank += 1
        if not rows:
            surf = self.row_font.render("Inga tider ännu", True, "White")
            rect = surf.get_rect(center=(x_center, y))
            self.screen.blit(surf, rect)

    def DisplayHighScores(self):
        # Stor titel
        title = self.title_font.render("LEADERBOARD", True, "Yellow")
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width()/2, 80)))

        # Tre kolumner: Easy / Medium / Difficult
        W = self.screen.get_width()
        cols = [W//6, W//2, 5*W//6]
        self._draw_column(cols[0], 1, "EASY (20x20)")
        self._draw_column(cols[1], 2, "MEDIUM (40x40)")
        self._draw_column(cols[2], 3, "DIFFICULT (60x60)")
