# button.py
import pygame

class Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.text = font.render(self.text_input, True, self.base_color)
        self.rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, (self.x_pos - self.image.get_width() // 2, self.y_pos - self.image.get_height() // 2))
        screen.blit(self.text, self.rect)

    def changeColor(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

    def checkForInput(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)