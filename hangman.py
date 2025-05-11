import pygame
import math
import random
import time
import easywords
import mediumwords
import hardwords

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game")

FPS = 60
clock = pygame.time.Clock()
run = True

# Sound effects
sound_on = True
correct_sound = pygame.mixer.Sound("audio/correct.mp3")
wrong_sound = pygame.mixer.Sound("audio/wrong.mp3")
win_sound = pygame.mixer.Sound("audio/win.mp3")
lose_sound = pygame.mixer.Sound("audio/lose.mp3")
select_sound = pygame.mixer.Sound("audio/select.mp3")

correct_sound.set_volume(0.7)
wrong_sound.set_volume(0.7)
win_sound.set_volume(0.7)
lose_sound.set_volume(0.7)
select_sound.set_volume(0.7)

# Game state variables
level = 0
score = 0
highest_score = 0
help_uses = 2
difficulty = None
background_color = (20, 33, 61)

# Fonts
LETTER_FONT = pygame.font.SysFont("comicsans", 25)
WORD_FONT = pygame.font.SysFont("comicsans", 40)
TITLE_FONT = pygame.font.SysFont("comicsans", 70)

# Image assets
images = [pygame.transform.smoothscale(pygame.image.load(f"images/hangman{i}.png"), (200, 285)) for i in range(7)]
win_trophy = pygame.transform.scale(pygame.image.load("images/wintrophy.png"), (200, 200))
lose_face = pygame.transform.scale(pygame.image.load("images/loseface1.png"), (200, 190))
help_icon = pygame.transform.scale(pygame.image.load("images/bulb.png"), (70, 70))
help_rect = help_icon.get_rect(topright=(WIDTH - 80, 35))
sound_on_img = pygame.transform.scale(pygame.image.load("images/sound_on.png").convert_alpha(), (50, 50))
sound_off_img = pygame.transform.scale(pygame.image.load("images/sound_off.png").convert_alpha(), (50, 50))
sound_btn_rect = pygame.Rect(WIDTH - 70, 50, 50, 50)

# Button layout
radius = 20
space = 15
x_start_buttons = round((WIDTH - (radius * 2 + space) * 13) / 2)
y_start_buttons = 600
A_ascii = 65

# Merge sort and win check
def merge(left, right):
    merged = []
    left_idx = right_idx = 0
    while left_idx < len(left) and right_idx < len(right):
        if left[left_idx] <= right[right_idx]:
            merged.append(left[left_idx])
            left_idx += 1
        else:
            merged.append(right[right_idx])
            right_idx += 1
    merged.extend(left[left_idx:])
    merged.extend(right[right_idx:])
    return merged

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def check_win_with_merge_sort(secret, guessed_letters):
    sorted_secret = merge_sort(list(set(secret)))
    sorted_guesses = merge_sort(list(guessed_letters))
    i = j = 0
    while i < len(sorted_secret):
        if j >= len(sorted_guesses): return False
        if sorted_secret[i] < sorted_guesses[j]: return False
        elif sorted_secret[i] == sorted_guesses[j]:
            i += 1
            j += 1
        else:
            j += 1
    return True

# Toggle sound
def toggle_sound():
    global sound_on
    sound_on = not sound_on

# Drawing functions
def draw(win_state=False):
    win.fill(background_color)
    win.blit(WORD_FONT.render("HangMan", 1, (255, 215, 0)), (WIDTH / 2 - 100, 40))
    win.blit(WORD_FONT.render(f"Level: {level}", 1, (100, 255, 200)), (50, 20))
    win.blit(WORD_FONT.render(f"Score: {score}", 1, (255, 215, 100)), (50, 60))
    guesses_text = WORD_FONT.render(f"Guesses Left: {6 - hangman}/6", 1, (255, 100, 100))
    win.blit(guesses_text, (50, 100))
    win.blit(help_icon, help_rect)
    win.blit(sound_on_img if sound_on else sound_off_img, sound_btn_rect)

    disp_word = "  ".join([ltr if ltr in guessed else "_" for ltr in words])
    text = WORD_FONT.render(disp_word, 1, (229, 229, 229))
    win.blit(text, (WIDTH / 2 - text.get_width() / 2, 300))

    for x, y, ltr, visible in letters:
        if visible:
            pygame.draw.circle(win, (252, 163, 17), (x, y), radius, 3)
            txt = LETTER_FONT.render(ltr, 1, (229, 229, 229))
            win.blit(txt, (x - txt.get_width() / 2, y - txt.get_height() / 2))

    win.blit(images[hangman], (50, 150))
    pygame.display.update()

def draw_button(text, color, y_offset, hover_color=None):
    mouse_pos = pygame.mouse.get_pos()
    button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + y_offset, 300, 70)
    current_color = hover_color if button.collidepoint(mouse_pos) and hover_color else color
    pygame.draw.rect(win, current_color, button, border_radius=10)
    text_surface = WORD_FONT.render(text, True, (255, 255, 255))
    win.blit(text_surface, (button.centerx - text_surface.get_width() // 2,
                            button.centery - text_surface.get_height() // 2))
    return button

def draw_difficulty_screen():
    win.fill(background_color)
    title = TITLE_FONT.render("Select Difficulty", 1, (255, 215, 0))
    win.blit(title, (WIDTH / 2 - title.get_width() / 2, 40))
    easy_btn = draw_button("Easy", (46, 139, 87), -50, (60, 179, 113))
    medium_btn = draw_button("Medium", (218, 165, 32), 40, (255, 193, 37))
    hard_btn = draw_button("Hard", (178, 34, 34), 130, (220, 20, 60))
    win.blit(sound_on_img if sound_on else sound_off_img, sound_btn_rect)
    pygame.display.update()
    return easy_btn, medium_btn, hard_btn

def draw_game_over_screen():
    win.fill(background_color)
    if win_state:
        win.blit(win_trophy, (WIDTH // 2 - win_trophy.get_width() // 2, HEIGHT // 2 - 250))
        win.blit(WORD_FONT.render("YOU WON!", 1, (50, 205, 50)), (WIDTH / 2 - 90, HEIGHT / 2 - 20))
        text = WORD_FONT.render(f"The word was: {words}", 1, (175, 238, 238))
        win.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 + 30))
        high_score_text = WORD_FONT.render(f"Score: {highest_score}", 1, (255, 215, 0))
        win.blit(high_score_text, (WIDTH / 2 - high_score_text.get_width() // 2, HEIGHT / 2 + 80))
    else:
        win.blit(lose_face, (WIDTH // 2 - lose_face.get_width() // 2, HEIGHT // 2 - 250))
        win.blit(WORD_FONT.render("GAME OVER!", 1, (220, 20, 60)), (WIDTH / 2 - 120, HEIGHT / 2 - 20))
        text = WORD_FONT.render(f"The word is: {words}", 1, (175, 238, 238))
        win.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 + 30))
        high_score_text = WORD_FONT.render(f"Highest Score: {highest_score}", 1, (255, 215, 0))
        win.blit(high_score_text, (WIDTH / 2 - high_score_text.get_width() // 2, HEIGHT / 2 + 80))



    global play_again_btn, quit_btn
    play_again_btn = draw_button("Play Again", (46, 139, 87), 180, (60, 179, 113))
    quit_btn = draw_button("Quit", (178, 34, 34), 270, (220, 20, 60))

    win.blit(sound_on_img if sound_on else sound_off_img, sound_btn_rect)
    pygame.display.update()

# Game initialization
def init_game():
    global words, guessed, hangman, letters, game_over, win_state, help_uses
    word_list = {"easy": easywords.easy, "medium": mediumwords.medium, "hard": hardwords.hard}
    words = random.choice(word_list[difficulty]).upper()
    guessed = []
    hangman = 0
    letters = [[x_start_buttons + space * 2 + ((radius * 2 + space) * (i % 13)),
                y_start_buttons + ((i // 13) * (space + radius * 2)),
                chr(A_ascii + i), True] for i in range(26)]
    game_over = False
    win_state = False
    help_uses = 2

# Difficulty selection screen
easy_btn, medium_btn, hard_btn = draw_difficulty_screen()
selecting = True
while selecting and run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            selecting = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if sound_btn_rect.collidepoint(mouse_pos):
                toggle_sound()
                easy_btn, medium_btn, hard_btn = draw_difficulty_screen()
            elif easy_btn.collidepoint(mouse_pos):
                difficulty = "easy"; selecting = False
                if sound_on: select_sound.play(); pygame.time.wait(300)
            elif medium_btn.collidepoint(mouse_pos):
                difficulty = "medium"; selecting = False
                if sound_on: select_sound.play(); pygame.time.wait(300)
            elif hard_btn.collidepoint(mouse_pos):
                difficulty = "hard"; selecting = False
                if sound_on: select_sound.play(); pygame.time.wait(300)

# Main game loop
if run:
    init_game()
    while run:
        clock.tick(FPS)
        draw(win_state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if sound_btn_rect.collidepoint(mouse_pos):
                    toggle_sound()
                elif help_rect.collidepoint(mouse_pos) and help_uses > 0 and not game_over:
                    hint = random.choice([ltr for ltr in set(words) if ltr not in guessed])
                    guessed.append(hint); help_uses -= 1
                    for i, ltr_info in enumerate(letters):
                        if ltr_info[2] == hint and ltr_info[3]:
                            letters[i][3] = False
                            if sound_on: correct_sound.play()
                elif not game_over:
                    for i, (x, y, ltr, visible) in enumerate(letters):
                        if visible and math.hypot(x - mouse_pos[0], y - mouse_pos[1]) <= radius:
                            letters[i][3] = False
                            guessed.append(ltr)
                            if ltr not in words:
                                hangman += 1
                                if sound_on: wrong_sound.play()
                            else:
                                if sound_on: correct_sound.play()

        if not game_over:
            if check_win_with_merge_sort(words, guessed):
                win_state = True; game_over = True; score += 10; level += 1
                if sound_on: win_sound.play()
                highest_score = max(highest_score, score)
            elif hangman == 6:
                win_state = False; game_over = True
                if sound_on: lose_sound.play()
                draw(); pygame.display.update(); time.sleep(2)
                highest_score = max(highest_score, score)

        if game_over:
            draw_game_over_screen()
            waiting = True
            while waiting and run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False; waiting = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if sound_btn_rect.collidepoint(mouse_pos):
                            toggle_sound(); draw_game_over_screen()
                        elif play_again_btn.collidepoint(mouse_pos):
                            if sound_on: select_sound.play(); pygame.time.wait(300)
                            if not win_state: level = score = highest_score = 0
                            init_game(); game_over = False; waiting = False
                        elif quit_btn.collidepoint(mouse_pos):
                            if sound_on: select_sound.play(); pygame.time.wait(300)
                            run = False; waiting = False

pygame.quit()
