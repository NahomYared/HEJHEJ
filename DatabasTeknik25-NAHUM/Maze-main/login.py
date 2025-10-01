# Modules/Login.py
import pygame, json, os
from .inputbox import InputBox

USERS_FILE = "data/users.json"

def _load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

class Login:
    def __init__(self, screen, buttons_font_inactive, buttons_font_active, button_image, title_font, mm_button_sound):
        self.screen = screen
        self.is_active = False
        self.result = None  # "login_ok" eller None
        self.message = ""   # feedbacktext

        self.buttons_font_inactive = buttons_font_inactive
        self.buttons_font_active = buttons_font_active
        self.button_image = button_image
        self.title_font = title_font
        self.button_sound = mm_button_sound

        W, H = screen.get_size()
        input_w, input_h = 500, 70
        cx = W // 2

        # Inmatningsrutor
        self.font_input = pygame.font.Font("media/fonts/ArialRoundedMTBold.ttf", 32)
        self.ib_user = InputBox(cx - input_w//2, 260, input_w, input_h, self.font_input, is_password=False, placeholder="Användarnamn")
        self.ib_pass = InputBox(cx - input_w//2, 360, input_w, input_h, self.font_input, is_password=True, placeholder="Lösenord")
        self.ib_pass2 = InputBox(cx - input_w//2, 460, input_w, input_h, self.font_input, is_password=True, placeholder="Repetera Lösenord (för Sign Up)")

        # Knappar (återanvänder MainMenuButton-klassen via settings)
        from . import MainMenu  # för att undvika cirkulära imports
        self.btn_login = MainMenu.MainMenuButton(screen, "LOGGA IN", buttons_font_inactive, buttons_font_active, button_image, (cx, 580), mm_button_sound)
        self.btn_signup = MainMenu.MainMenuButton(screen, "SIGN UP", buttons_font_inactive, buttons_font_active, button_image, (cx, 670), mm_button_sound)

    def _verify(self, u, p):
        users = _load_users()
        return users.get(u) == p

    def _create(self, u, p, p2):
        if not u or not p:
            return False, "Fyll i alla fält."
        if p != p2:
            return False, "Lösenorden matchar inte."
        users = _load_users()
        if u in users:
            return False, "Användarnamnet är upptaget."
        users[u] = p
        _save_users(users)
        return True, "Konto skapat! Du kan nu logga in."

    def update(self, events, mouse_pos):
        # hantera inputrutor
        submitted = False
        for e in events:
            if self.ib_user.handle_event(e): submitted = True
            if self.ib_pass.handle_event(e): submitted = True
            if self.ib_pass2.handle_event(e): submitted = True

        # knappar
        self.btn_login.display()
        self.btn_signup.display()

        if self.btn_login.is_Clicked() or submitted:
            u, p = self.ib_user.value(), self.ib_pass.value()
            if self._verify(u, p):
                self.result = "login_ok"
                self.message = ""
                if self.button_sound: self.button_sound.play()
            else:
                self.message = "Fel användarnamn eller lösenord."

        elif self.btn_signup.is_Clicked():
            ok, msg = self._create(self.ib_user.value(), self.ib_pass.value(), self.ib_pass2.value())
            self.message = msg
            if ok and self.button_sound: self.button_sound.play()

    def draw(self):
        # Titel
        title = self.title_font.render("LOGGA IN", True, "Yellow")
        title_rect = title.get_rect(center=(self.screen.get_width()/2, 170))
        self.screen.blit(title, title_rect)

        # Etiketter
        lbl_font = pygame.font.Font("media/fonts/MightySouly.ttf", 28)
        def blit_label(text, y):
            surf = lbl_font.render(text, True, "White")
            rect = surf.get_rect(center=(self.screen.get_width()/2, y))
            self.screen.blit(surf, rect)

        blit_label("Användarnamn", 235)
        self.ib_user.draw(self.screen)

        blit_label("Lösenord", 335)
        self.ib_pass.draw(self.screen)

        blit_label("Repetera Lösenord (för Sign Up)", 435)
        self.ib_pass2.draw(self.screen)

        # Meddelande
        if self.message:
            msg_font = pygame.font.Font("media/fonts/ArialRoundedMTBold.ttf", 26)
            msg_surf = msg_font.render(self.message, True, "White")
            msg_rect = msg_surf.get_rect(center=(self.screen.get_width()/2, 540))
            self.screen.blit(msg_surf, msg_rect)
