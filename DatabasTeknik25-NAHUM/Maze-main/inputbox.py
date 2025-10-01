# Modules/InputBox.py
import pygame

class InputBox:
    def __init__(self, x, y, w, h, font, is_password=False, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.is_password = is_password
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.color_inactive = pygame.Color(180, 180, 180)
        self.color_active = pygame.Color(255, 255, 255)
        self.border_color = self.color_inactive
        self.padding = 10

    def handle_event(self, event):
        submitted = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.border_color = self.color_active if self.active else self.color_inactive
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                submitted = True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Begränsa osynliga kontrolltecken
                if event.unicode.isprintable():
                    self.text += event.unicode
        return submitted

    def value(self):
        return self.text.strip()

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect)  # bakgrund i rutan
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        shown = ("•" * len(self.text)) if (self.is_password and self.text) else (self.text or self.placeholder)
        color = (255, 255, 255) if self.text else (180, 180, 180)
        surf = self.font.render(shown, True, color)
        screen.blit(surf, (self.rect.x + self.padding, self.rect.y + self.padding))
