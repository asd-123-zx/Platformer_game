import os
import pygame
import sys
import pygame_menu as pm
from button import Button
import my_game
from my_game import *

pygame.init()

# Set up the screen
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Match the game's window size
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu")

# Load and scale the background image
try:
    BG = pygame.image.load("Assets/Backgrounds/Background.png")
    BG = pygame.transform.scale(BG, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scale the background to fit the window size
except pygame.error as e:
    print(f"Unable to load background image: {e}")
    sys.exit()


def get_font(size):  # Returns a font in the desired size
    return pygame.font.SysFont("Arial", size)


def play():
    # Call the main game function
    main(SCREEN)  # Pass the screen to the game
    return  # Return to the main menu after the game ends


def options():
    # Create the settings menu using pygame_menu
    settings = pm.Menu(title="Settings", width=700, height=600, theme=pm.themes.THEME_DARK)

    # Customize the theme for settings
    settings._theme.background_color = (255, 204, 153)  # Light orange for the background
    settings._theme.widget_font_size = 25
    settings._theme.widget_font_color = (0, 0, 0)
    settings._theme.title_background_color = (255, 204, 153)  # Light orange title bar
    settings._theme.title_font_color = (0, 0, 0)

    # Menu options
    resolution = [("1920x1080", "1920x1080"), ("1920x1200", "1920x1200"),
                  ("1280x720", "1280x720"), ("2560x1440", "2560x1440"), ("3840x2160", "3840x2160")]
    difficulty = [("Easy", "Easy"), ("Medium", "Medium"), ("Expert", "Expert")]

    settings.add.dropselect_multiple(title="Window Resolution", items=resolution,
                                      dropselect_multiple_id="Resolution",
                                      open_middle=True, max_selected=1,
                                      selection_box_height=6)
    settings.add.toggle_switch(title="Music", default=True, toggleswitch_id="music")
    settings.add.toggle_switch(title="Sounds", default=False, toggleswitch_id="sound")
    settings.add.selector(title="Difficulty", items=difficulty, selector_id="difficulty", default=0)

    # Add the return button
    settings.add.button(title="Return To Main Menu", action=lambda: main_menu())

    while True:
        # Set the background image
        SCREEN.blit(BG, (0, 0))

        # Draw a light orange background rectangle for the settings menu
        pygame.draw.rect(SCREEN, (255, 204, 153), pygame.Rect(290, 60, 700, 600), border_radius=20)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update and draw the settings menu
        settings.update(events)
        settings.draw(SCREEN)

        pygame.display.update()


def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))  # Set the background image for the main menu

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # Adjust the position of the "MAIN MENU" text
        MENU_TEXT = get_font(70).render("MAIN MENU", True, "#b68f40")  # Smaller font size
        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))  # Center horizontally

        # Adjust the positions of the buttons
        PLAY_BUTTON = Button(image=pygame.image.load("Assets/Backgrounds/Play Rect.png"), 
                             pos=(SCREEN_WIDTH // 2, 250),  # Center horizontally
                             text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("Assets/Backgrounds/Options Rect.png"), 
                                pos=(SCREEN_WIDTH // 2, 350),  # Center horizontally
                                text_input="OPTIONS", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("Assets/Backgrounds/Quit Rect.png"), 
                             pos=(SCREEN_WIDTH // 2, 450),  # Center horizontally
                             text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()  # Start the game
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


if __name__ == "__main__":
    main_menu()