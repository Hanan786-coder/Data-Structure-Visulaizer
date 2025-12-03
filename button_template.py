import pygame
import Colors

class Button:
    def __init__(self, x, y, w, h, text, action_code, txt_size):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.is_hovered = False
        self.FONT = pygame.font.Font("ScienceGothic-Regular.ttf", txt_size)

    def draw(self, surface):
        self.check_hover(pygame.mouse.get_pos())
        color = Colors.TEAL_BRIGHT if self.is_hovered else Colors.TEAL
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Text
        txt_surf = self.FONT.render(self.text, True, Colors.LIGHT_GREY)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        return self.rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN

