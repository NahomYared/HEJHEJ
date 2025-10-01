import time 
import random
import pygame
from settings import *
from Modules import AuthDB  # <-- ADDED: progress & user lookup från pickle

# ADDED: edge-state för country-nav (behöver leva över frames)
_prev_country_prev_clicked = False
_prev_country_next_clicked = False
_prev_country_back_clicked = False

# ADDED: ladda och cacha låsikon
LOCK_IMAGE_PATH = "media/images/buttons/lock.png"
_lock_img = None
def _lock_icon_surface():
    global _lock_img
    if _lock_img is None:
        try:
            _lock_img = pygame.image.load(LOCK_IMAGE_PATH).convert_alpha()
        except Exception:
            _lock_img = None
    return _lock_img

# PYGAME LOOP
start_ticks = pygame.time.get_ticks()
while True:
    PygameEvents = pygame.event.get()
    keys = pygame.key.get_pressed()
    # Mouse Position
    MousePosition = pygame.mouse.get_pos()

    # QUIT
    for event in PygameEvents:
        if event.type == pygame.QUIT:
            Quit()

    # Time
    MillisecondsPassed = pygame.time.get_ticks() - start_ticks

    # Intro Screen
    if MillisecondsPassed / 1000 < IntroTime - 0.5:
        PygameLogo_rect = PygameLogo.convert_alpha().get_rect()
        PygameLogo_rect.center = PygameLogoPosition
        screen.blit(PygameLogo.convert_alpha(), PygameLogo_rect)

        IntroMazeText_rect = IntroMazeText.get_rect()
        IntroMazeText_rect.midtop = (PygameLogo_rect.midbottom[0] - 20,
                                     PygameLogo_rect.midbottom[1])  # Adjusting the Position of the position of the text
        screen.blit(IntroMazeText, IntroMazeText_rect)

        IntroLoadingBarBackground_rect = IntroLoadingBarBackground.get_rect()
        IntroLoadingBarBackground_rect.midtop = (IntroMazeText_rect.midbottom[0], (IntroMazeText_rect.midbottom[1] + 50))
        screen.blit(IntroLoadingBarBackground, IntroLoadingBarBackground_rect)

        xLength = 480 * MillisecondsPassed / ((IntroTime - 0.5) * 1000)
        IntroLoadingBar = LoadScaledImage("media/images/IntroLoadingBar/IntroLoadingBar.png", scaling_dim=(int(xLength), 40))  # CHANGED
        IntroLoadingBar_rect = IntroLoadingBar.get_rect()
        IntroLoadingBar_rect.midleft = (IntroLoadingBarBackground_rect.midleft[0] + 10, IntroLoadingBarBackground_rect.midleft[1])
        screen.blit(IntroLoadingBar, IntroLoadingBar_rect)
    elif int((MillisecondsPassed / 1000) * 4) / 4 == IntroTime - 0.25:
        screen.fill("Black")
    elif int((MillisecondsPassed / 1000) * 4) / 4 == IntroTime + 0.25:
        LoginScreen.is_active = True
        main_menu.is_active = False
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(IntroMusicAddress)
            pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
            pygame.mixer.music.play(-1)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(IntroMusicAddress)
            pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
            pygame.mixer.music.play(-1)
    
    # Login Screen
    if LoginScreen.is_active:
        # Visuell matchning: samma bakgrund som menyn
        main_menu.BackgroundDisplay(MainMenuBackground[0])

        # Rita & hantera
        LoginScreen.draw()
        LoginScreen.update(PygameEvents, MousePosition)

        # Klar → vidare till huvudmenyn
        if LoginScreen.result == "login_ok":
            LoginScreen.is_active = False
            # Sätt spelarnamnet så det följer med i spelet
            Game.PlayerName = LoginScreen.username
            main_menu.is_active = True


    # Main Menu
    if main_menu.is_active and not LoginScreen.is_active:
        # Setting the frame rate
        main_menu.BackgroundFrameIndex = (MillisecondsPassed % (
                MainMenuBackgroundFrameTime * len(MainMenuBackground))) // MainMenuBackgroundFrameTime
        # Main Menu Background
        main_menu.BackgroundDisplay(MainMenuBackground[main_menu.BackgroundFrameIndex])
        # Header of the MainMenu
        MainMenuHeaderLogo_rect = MainMenuHeaderLogo.get_rect()
        MainMenuHeaderLogo_rect.center = MainMenuHeaderLogoPosition
        screen.blit(MainMenuHeaderLogo, MainMenuHeaderLogo_rect)
        MainMenuMazeText_rect = MainMenuMazeText.get_rect()
        MainMenuMazeText_rect.midtop = (MainMenuHeaderLogo_rect.midbottom[0] - 10, MainMenuHeaderLogo_rect.midbottom[1] + 20)
        screen.blit(MainMenuMazeText, MainMenuMazeText_rect)
        # Main Menu Buttons
        main_menu.Buttons()
        if MM_Quit.is_Clicked():
            Quit()
        elif MM_Play.is_Clicked():
            main_menu.is_active = False
            time.sleep(ButtonDelay)
            # Game.is_active = True                # <<< REMOVED (we go to country chooser first)
            CountrySelectionActive = True          # <<< ADDED
        elif MM_Scores.is_Clicked():
            main_menu.is_active = False
            time.sleep(ButtonDelay)
            Scores.is_active = True
        elif MM_Preferences.is_Clicked():
            main_menu.is_active = False
            time.sleep(ButtonDelay)
            GamePreferences.is_active = True
            if GameOver_Back.is_Clicked():
                Game.MazeGame = None
                Scores.GameDone = False
                Game.is_active = False
                Game.GameOverScreen = False
                Game.LevelScreen = True
                main_menu.is_active = True
                Game.db_recorded = False  # <-- återställ
                time.sleep(BackButtonDelay)
                pygame.mixer.music.stop()
                pygame.mixer.music.load(IntroMusicAddress)
                pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
                pygame.mixer.music.play(-1)


    # ---------------- COUNTRY SELECTION (FIXED MINIMAL) ----------------
    if 'CountrySelectionActive' in globals() and CountrySelectionActive:
        # Background (same animated style)
        main_menu.BackgroundFrameIndex = (MillisecondsPassed % (
            MainMenuBackgroundFrameTime * len(MainMenuBackground))) // MainMenuBackgroundFrameTime
        main_menu.BackgroundDisplay(MainMenuBackground[main_menu.BackgroundFrameIndex])

        # Title
        ChooseCountryRect = ChooseCountryText.get_rect(center=ChooseCountryPos)
        screen.blit(ChooseCountryText, ChooseCountryRect)

        total = len(CountryButtons)

        # ADDED: clamp av CountryPage innan vi räknar slice
        per = COUNTRIES_PER_PAGE  # ADDED
        max_page = 0 if total == 0 else ((total - 1) // per)  # ADDED
        if CountryPage < 0: CountryPage = 0  # ADDED
        if CountryPage > max_page: CountryPage = max_page  # ADDED

        # Page slice
        start = CountryPage * COUNTRIES_PER_PAGE
        end = min(start + COUNTRIES_PER_PAGE, total)
        page_buttons = CountryButtons[start:end]

        # Draw buttons ------------- (progress-lås + LÅSIKON) -------------
        for i_btn, btn in enumerate(page_buttons):
            btn.display()
            country_id = Countries.COUNTRIES[start + i_btn]["country"]

            # hämta user_id från spelarnamn utan att röra login.py
            uid = None
            if hasattr(Game, "PlayerName") and Game.PlayerName:
                try:
                    uid = AuthDB.user_id_by_username(str(Game.PlayerName))
                except Exception:
                    uid = None

            # UNLOCK RULES: 1) bana 1 alltid öppen
            #               2) denna bana redan klar
            #               3) föregående bana klar → lås upp denna
            unlocked = False
            idx = start + i_btn
            if idx == 0:
                unlocked = True
            else:
                if uid is not None and AuthDB.has_access(uid, country_id):
                    unlocked = True
                else:
                    prev_id = Countries.COUNTRIES[idx - 1]["country"]
                    if uid is not None and AuthDB.has_access(uid, prev_id):
                        unlocked = True

            if not unlocked:
                # Rita en låsikon centrerad på knappen (ca 80% av min(rect.w, rect.h))
                rect = getattr(btn, "ButtonRect", None) or getattr(btn, "rect", None)
                icon = _lock_icon_surface()
                if rect and icon:
                    size = int(min(rect.width, rect.height) * 0.8)
                    if size > 0:
                        icon_scaled = pygame.transform.smoothscale(icon, (size, size))
                        screen.blit(icon_scaled, (rect.centerx - size // 2, rect.centery - size // 2))
        # -----------------------------------------------------------------

        # Navigation
        if total > COUNTRIES_PER_PAGE:
            if CountryPage > 0:
                CountryPrev.display()
            if end < total:
                CountryNext.display()
        else:
            CountryBack.display()

        # ADDED: Edge-trigger för navknappar
        cur_prev = (CountryPage > 0 and CountryPrev.is_Clicked()) if total > COUNTRIES_PER_PAGE else False  # ADDED
        cur_next = (end < total and CountryNext.is_Clicked()) if total > COUNTRIES_PER_PAGE else False       # ADDED
        cur_back = CountryBack.is_Clicked() if not (total > COUNTRIES_PER_PAGE) else False                   # ADDED

        prev_edge = cur_prev and not _prev_country_prev_clicked   # ADDED
        next_edge = cur_next and not _prev_country_next_clicked   # ADDED
        back_edge = cur_back and not _prev_country_back_clicked   # ADDED

        _prev_country_prev_clicked = cur_prev   # ADDED
        _prev_country_next_clicked = cur_next   # ADDED
        _prev_country_back_clicked = cur_back   # ADDED

        # Click handling (ignorera klick på låsta)
        for i_btn, btn in enumerate(page_buttons):
            if btn.is_Clicked():
                country_id = Countries.COUNTRIES[start + i_btn]["country"]

                uid = None
                if hasattr(Game, "PlayerName") and Game.PlayerName:
                    try:
                        uid = AuthDB.user_id_by_username(str(Game.PlayerName))
                    except Exception:
                        uid = None

                # UNLOCK RULES (samma som vid ritning)
                unlocked = False
                idx = start + i_btn
                if idx == 0:
                    unlocked = True
                else:
                    if uid is not None and AuthDB.has_access(uid, country_id):
                        unlocked = True
                    else:
                        prev_id = Countries.COUNTRIES[idx - 1]["country"]
                        if uid is not None and AuthDB.has_access(uid, prev_id):
                            unlocked = True

                if not unlocked:
                    continue  # låst → gör inget

                time.sleep(ButtonDelay)
                SelectedCountry = country_id
                SelectedCities = Countries.COUNTRIES[start + i_btn]["cities"]
                CountrySelectionActive = False
                Game.is_active = True
                Game.LevelScreen = True
                # FIX: ny runda startar → progress får sparas igen
                Game.progress_recorded = False  # <-- FIX: nollställ per runda
                break

        if total > COUNTRIES_PER_PAGE:
            if prev_edge:                              # CHANGED (edge + clamp)
                CountryPage = max(0, CountryPage - 1) # CHANGED
                time.sleep(ButtonDelay)
            if next_edge:                              # CHANGED (edge + clamp)
                CountryPage = min(max_page, CountryPage + 1)  # CHANGED
                time.sleep(ButtonDelay)
            if back_edge:                              # CHANGED (använd CountryBack i denna vy)
                CountrySelectionActive = False
                main_menu.is_active = True
                time.sleep(BackButtonDelay)
        else:
            if back_edge:  # CHANGED
                CountrySelectionActive = False
                main_menu.is_active = True
                time.sleep(BackButtonDelay)
    # -----------------------------------------------------------

    # The Game!
    if Game.is_active:
        if Game.LevelScreen:
            # Background Static
            main_menu.BackgroundDisplay(MainMenuBackground[0])
            # Buttons
            GLB_Easy.display()
            GLB_Medium.display()
            GLB_Difficult.display()

            GLB_Level_Back.display()

            # Button Functionality Implementation
            if GLB_Easy.is_Clicked() or GLB_Medium.is_Clicked() or GLB_Difficult.is_Clicked():
                Game.LevelScreen = False
                if GLB_Easy.is_Clicked():
                    Game.Level = 1
                elif GLB_Medium.is_Clicked():
                    Game.Level = 2
                elif GLB_Difficult.is_Clicked():
                    Game.Level = 3

                # --- ADDED: choose a random target city from the selected country
                try:
                    if isinstance(SelectedCities, list) and SelectedCities:
                        Game.TargetCity = random.choice(SelectedCities)
                    else:
                        Game.TargetCity = None
                except NameError:
                    Game.TargetCity = None
                # ---------------------------------------------------------------

                Game.GameScreen = True
                Game.SetMazeLevel()
                time.sleep(ButtonDelay)
                pygame.mixer.music.stop()
                pygame.mixer.music.load(GameplayMusicAddress)
                pygame.mixer.music.set_volume(0.2 * int(GamePreferences.MusicState))
                pygame.mixer.music.play(-1)
            elif GLB_Level_Back.is_Clicked():
                Game.is_active = False
                main_menu.is_active = True
                time.sleep(BackButtonDelay)
        elif Game.GameScreen:
            screen.fill("Black")

            Game.GamePlay(keys, MillisecondsPassed)

            # Right Background for Displaying Buttons
            screen.blit(GameRightBackground, (screen.get_height() + Game.XShift, 0))

            # StopWatch
            StopWatchButton = MainMenu.MainMenuButton(screen, f"Time Elapsed = {int(Game.StopwatchValue / 1000)}s",
                                                      GameStopwatchFont, GameStopwatchFont, TimeButtonImage,
                                                      StopWatchButtonPos)
            StopWatchButton.display()

            # --- ADDED: “GO TO CITY” label under the stopwatch
            target_label = ("GO TO " + Game.TargetCity.upper()) if getattr(Game, "TargetCity", None) else "FIND THE EXIT"
            TargetButton = MainMenu.MainMenuButton(
                screen, target_label,
                GameStopwatchFont, GameStopwatchFont, TimeButtonImage,
                (StopWatchButtonPos[0], StopWatchButtonPos[1] + 100)
            )
            TargetButton.display()
            # -----------------------------------------------------

            # Change Background Button
            Game_ChangeBackground.display()
            # Back Button
            Game_Back.display()

            # Sound Button
            if GamePreferences.MusicState and not Game_Sound.ButtonRect.collidepoint(MousePosition[0],
                                                                                     MousePosition[1]):
                Game_Sound.display()
            else:
                # Muted Symbol
                screen.blit(SoundControlButtonImageOff.convert_alpha(),
                            SoundControlButtonImageOff.convert_alpha().get_rect(center=GameSoundButtonPos))

            if Game_Sound.is_Clicked():
                GamePreferences.MusicState = not GamePreferences.MusicState
                pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
                time.sleep(SoundButtonDelay)
            elif Game_ChangeBackground.is_Clicked():
                Game.ChangeBackground()
                time.sleep(SoundButtonDelay)

            # Back Button Functionality
            if Game_Back.is_Clicked():
                Game.MazeGame = None
                Game.GameScreen = False
                Game.LevelScreen = True
                time.sleep(ButtonDelay)
                pygame.mixer.music.stop()
                pygame.mixer.music.load(IntroMusicAddress)
                pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
                pygame.mixer.music.play(-1)

            if Game.GameOverScreen:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(GameOverMusicAddress)
                pygame.mixer.music.set_volume(0.2 * int(GamePreferences.MusicState))
                pygame.mixer.music.play()
        elif Game.GameOverScreen:
            # Background Static
            main_menu.BackgroundDisplay(MainMenuBackground[0])
            Game.GameOverScreenDisplay()
            GameOver_Back.display()

            # StopWatch
            TimeTakenButton = MainMenu.MainMenuButton(screen, f"TIME TAKEN = {int(Game.StopwatchValue / 1000)} SEC",
                                                      ButtonsFontInactive, ButtonsFontInactive, TimeButtonImage,
                                                      TimeTakenButtonPos)
            TimeTakenButton.display()

            # High Score
            Scores.UpdateScore(Game.StopwatchValue / 1000, Game.Level)
            if hasattr(LoginScreen, "user_id") and LoginScreen.user_id is not None:
                if not hasattr(Game, "db_recorded") or not Game.db_recorded:
                    try:
                        AuthDB.record_score(LoginScreen.user_id, Game.Level, int(Game.StopwatchValue / 1000))
                    except Exception:
                        pass
                    Game.db_recorded = True


                    
                # Skriv score till DB en (1) gång
            if hasattr(LoginScreen, "user_id") and LoginScreen.user_id is not None:
                if not hasattr(Game, "db_recorded") or not Game.db_recorded:
                    try:
                        AuthDB.record_score(LoginScreen.user_id, Game.Level, int(Game.StopwatchValue / 1000))
                    except Exception:
                        pass
                    Game.db_recorded = True

            # High Score String
            HighScoreString = ("NEW HIGH SCORE : " + str(int(Game.StopwatchValue / 1000)) + " SEC") if Scores.isUpdated else ("HIGH SCORE: " + Scores.HighScore(Game.Level) + " SEC")

            HighScoreButton = MainMenu.MainMenuButton(screen, HighScoreString, ButtonsFontInactive, ButtonsFontInactive,
                                                      MMButtonsImage, HighScoreButtonPos)
            HighScoreButton.display()

            # --- SPARA PROGRESS: exakt en gång per runda ---
            try:
                if not hasattr(Game, "progress_recorded"):
                    Game.progress_recorded = False  # defensivt default

                uid = None
                if hasattr(LoginScreen, "user_id") and LoginScreen.user_id is not None:
                    uid = LoginScreen.user_id
                elif hasattr(Game, "PlayerName") and Game.PlayerName:
                    uid = AuthDB.user_id_by_username(str(Game.PlayerName))

                if (uid is not None) and (not Game.progress_recorded) and ('SelectedCountry' in globals()) and SelectedCountry:
                    AuthDB.add_country_progress(uid, SelectedCountry)
                    Game.progress_recorded = True  # <-- FIX: blockera fler sparningar samma runda
            except Exception:
                pass
            # ------------------------------------------------

            # Back to Main Menu
            if GameOver_Back.is_Clicked():
                Game.MazeGame = None
                Scores.GameDone = False
                Game.is_active = False
                Game.GameOverScreen = False
                Game.LevelScreen = True
                main_menu.is_active = True
                time.sleep(BackButtonDelay)
                pygame.mixer.music.stop()
                pygame.mixer.music.load(IntroMusicAddress)
                pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
                pygame.mixer.music.play(-1)

    # Preferences
    if GamePreferences.is_active:
        # Background Static
        main_menu.BackgroundDisplay(MainMenuBackground[0])

        GP_MusicText.display()
        GP_Back.display()
        if GamePreferences.MusicState and not GP_Sound.ButtonRect.collidepoint(MousePosition[0], MousePosition[1]):
            GP_Sound.display()
        else:
            # Muted Symbol
            screen.blit(SoundControlButtonImageOff.convert_alpha(), SoundControlButtonImageOff.convert_alpha().get_rect(
                center=((WINDOW_DIM[0] / 2 + 300), (WINDOW_DIM[1] / 2 - 100))))

        if GP_Sound.is_Clicked():
            GamePreferences.MusicState = not GamePreferences.MusicState
            pygame.mixer.music.set_volume(0.25 * int(GamePreferences.MusicState))
            time.sleep(SoundButtonDelay)
        elif GP_Back.is_Clicked():
            GamePreferences.is_active = False
            main_menu.is_active = True
            time.sleep(BackButtonDelay)

    # Scores
    if Scores.is_active:
        # Background Static
        main_menu.BackgroundDisplay(MainMenuBackground[0])

        Scores.DisplayHighScores()

        Scores_Back.display()

        if Scores_Back.is_Clicked():
            Scores.is_active = False
            time.sleep(BackButtonDelay)
            main_menu.is_active = True

    pygame.display.update()
