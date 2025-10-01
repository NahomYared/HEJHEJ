# Modules/Login.py
import pygame
from .InputBox import InputBox
from . import AuthDB
from . import MainMenu  # för MainMenuButton-knapparna

class Login:
    def __init__(self, screen, buttons_font_inactive, buttons_font_active, button_image, title_font, mm_button_sound):
        self.screen = screen
        self.is_active = False
        self.result = None          # "login_ok" när man är inne
        self.message = ""           # status/felmeddelande
        self.mode = "login"         # "login" eller "signup"
        self.username = None
        self.user_id = None
        self.button_sound = mm_button_sound

        self.buttons_font_inactive = buttons_font_inactive
        self.buttons_font_active = buttons_font_active
        self.button_image = button_image
        self.title_font = title_font

        W, H = screen.get_size()
        input_w, input_h = 500, 70
        cx = W // 2

        self.font_input = pygame.font.Font("media/fonts/ArialRoundedMTBold.ttf", 32)
        self.font_label = pygame.font.Font("media/fonts/MightySouly.ttf", 28)
        self.font_msg = pygame.font.Font("media/fonts/ArialRoundedMTBold.ttf", 26)

        self.ib_user = InputBox(cx - input_w//2, 260, input_w, input_h, self.font_input, is_password=False, placeholder="Användarnamn")
        self.ib_pass = InputBox(cx - input_w//2, 360, input_w, input_h, self.font_input, is_password=True, placeholder="Lösenord")
        self.ib_pass2 = InputBox(cx - input_w//2, 460, input_w, input_h, self.font_input, is_password=True, placeholder="Repetera Lösenord")

        # Knappar (återanvänder spelets stil)
        self.btn_submit = MainMenu.MainMenuButton(screen, "LOGGA IN", buttons_font_inactive, buttons_font_active, button_image, (cx, 580), mm_button_sound)
        self.btn_toggle = MainMenu.MainMenuButton(screen, "SIGN UP", buttons_font_inactive, buttons_font_active, button_image, (cx, 670), mm_button_sound)

        # --- Edge-trigger state för knappklick (förhindrar att hålla-inne spammar) ---
        self._prev_submit_clicked = False
        self._prev_toggle_clicked = False

        # (valfritt) kort cooldown för extra säkerhet
        self._last_click_ms = 0
        self._click_cooldown = 0  # sätt till t.ex. 200 om du vill ha spärr i ms

    def _cooldown_ok(self):
        if self._click_cooldown <= 0:
            return True
        now = pygame.time.get_ticks()
        if now - self._last_click_ms >= self._click_cooldown:
            self._last_click_ms = now
            return True
        return False

    def _submit_login(self):
        u, p = self.ib_user.value(), self.ib_pass.value()
        ok, data = AuthDB.verify_user(u, p)
        if ok:
            self.result = "login_ok"
            self.username = u
            self.user_id = data["user_id"]
            self.message = ""
            if self.button_sound: 
                self.button_sound.play()
        else:
            self.message = str(data)

    def _submit_signup(self):
        u = self.ib_user.value()
        p = self.ib_pass.value()
        p2 = self.ib_pass2.value()
        if not u or not p or not p2:
            self.message = "Fyll i alla fält."
            return
        if p != p2:
            self.message = "Lösenorden matchar inte."
            return
        ok, data = AuthDB.create_user(u, p)
        if ok:
            self.message = "Konto skapat! Logga in nu."
            self.mode = "login"
            if self.button_sound: 
                self.button_sound.play()
        else:
            self.message = str(data)

    def update(self, events, mouse_pos):
        submitted_by_enter = False
        for e in events:
            if self.ib_user.handle_event(e): 
                submitted_by_enter = True
            if self.ib_pass.handle_event(e): 
                submitted_by_enter = True
            if self.mode == "signup":
                if self.ib_pass2.handle_event(e): 
                    submitted_by_enter = True

        # Rita knappar (de kan uppdatera intern hover/animations-state)
        self.btn_submit.display()
        self.btn_toggle.display()

        # --- Edge-trigger på knappar ---
        # Läser nuvarande "hålls-ner" status från knapparna
        cur_submit_clicked = bool(self.btn_submit.is_Clicked())
        cur_toggle_clicked = bool(self.btn_toggle.is_Clicked())

        # Trigga EN gång när status går False -> True
        submit_edge = (cur_submit_clicked and not self._prev_submit_clicked)
        toggle_edge = (cur_toggle_clicked and not self._prev_toggle_clicked)

        # Spara för nästa frame
        self._prev_submit_clicked = cur_submit_clicked
        self._prev_toggle_clicked = cur_toggle_clicked

        # Toggle mellan login/signup (endast på edge + ev. cooldown)
        if toggle_edge and self._cooldown_ok():
            if self.mode == "login":
                self.mode = "signup"
                self.btn_submit = MainMenu.MainMenuButton(
                    self.screen, "SKAPA KONTO",
                    self.buttons_font_inactive, self.buttons_font_active,
                    self.button_image, self.btn_submit.ButtonPos, self.button_sound
                )
                self.btn_toggle = MainMenu.MainMenuButton(
                    self.screen, "TILLBAKA TILL LOGIN",
                    self.buttons_font_inactive, self.buttons_font_active,
                    self.button_image, self.btn_toggle.ButtonPos, self.button_sound
                )
            else:
                self.mode = "login"
                self.btn_submit = MainMenu.MainMenuButton(
                    self.screen, "LOGGA IN",
                    self.buttons_font_inactive, self.buttons_font_active,
                    self.button_image, self.btn_submit.ButtonPos, self.button_sound
                )
                self.btn_toggle = MainMenu.MainMenuButton(
                    self.screen, "SIGN UP",
                    self.buttons_font_inactive, self.buttons_font_active,
                    self.button_image, self.btn_toggle.ButtonPos, self.button_sound
                )

        # Submit (edge på knappen eller via Enter i input)
        if (submit_edge and self._cooldown_ok()) or submitted_by_enter:
            if self.mode == "login":
                self._submit_login()
            else:
                self._submit_signup()

    def draw(self):
        # Titel
        title_text = "LOGGA IN" if self.mode == "login" else "SKAPA KONTO"
        title = self.title_font.render(title_text, True, "Yellow")
        title_rect = title.get_rect(center=(self.screen.get_width()/2, 170))
        self.screen.blit(title, title_rect)

        # Etiketter
        def blit_label(text, y):
            surf = self.font_label.render(text, True, "White")
            rect = surf.get_rect(center=(self.screen.get_width()/2, y))
            self.screen.blit(surf, rect)

        blit_label("Användarnamn", 235)
        self.ib_user.draw(self.screen)

        blit_label("Lösenord", 335)
        self.ib_pass.draw(self.screen)

        if self.mode == "signup":
            blit_label("Repetera Lösenord", 435)
            self.ib_pass2.draw(self.screen)

        # Meddelande
        if self.message:
            msg_surf = self.font_msg.render(self.message, True, "White")
            msg_rect = msg_surf.get_rect(center=(self.screen.get_width()/2, 540))
            self.screen.blit(msg_surf, msg_rect)
