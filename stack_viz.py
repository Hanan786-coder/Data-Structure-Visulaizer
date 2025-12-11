import pygame
import sys
import Colors

# --- Configuration ---
SCREEN_WIDTH = 1000  # Updated to 1000
SCREEN_HEIGHT = 700

# Map Colors
BACKGROUND_COLOR = Colors.GREY
ELEMENT_COLOR = Colors.TEAL
HOVER_COLOR = Colors.TEAL_BRIGHT
HIGHLIGHT_COLOR = Colors.ORANGE
TEXT_COLOR = Colors.LIGHT_GREY
INPUT_BG_COLOR = Colors.BLACK
CONTAINER_COLOR = Colors.LIGHT_GREY
ERROR_COLOR = (255, 87, 87)
SUCCESS_COLOR = (0, 200, 81)

# Dimensions
ELEM_WIDTH = 200
ELEM_HEIGHT = 40
SPACING = 5
MAX_ALLOWED_CAPACITY = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stack Visualization (DSA Project)")
clock = pygame.time.Clock()


# --- Font Loading Helper ---
def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('Arial', size, bold=bold)


# FONT SIZES
font_title = get_font(28)
font_ui = get_font(17)
font_elem = get_font(19)
font_logic = get_font(13)


# --- UI Classes ---
class Button:
    def __init__(self, x, y, w, h, text, action_func=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action_func
        self.is_hovered = False

    def draw(self, surface):
        color = HOVER_COLOR if self.is_hovered else ELEMENT_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        txt_surf = font_ui.render(self.text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        if self.is_hovered and self.action:
            self.action()


class InputBox:
    def __init__(self, x, y, w, h, text='', is_numeric_only=False, max_chars=9):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = Colors.LIGHT_GREY
        self.color_active = Colors.TEAL
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font_ui.render(text, True, TEXT_COLOR)
        self.active = False
        self.is_numeric = is_numeric_only
        self.max_chars = max_chars

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < self.max_chars:
                    if self.is_numeric:
                        if event.unicode.isdigit():
                            self.text += event.unicode
                    else:
                        self.text += event.unicode
            self.txt_surface = font_ui.render(self.text, True, TEXT_COLOR)

    def draw(self, screen):
        pygame.draw.rect(screen, INPUT_BG_COLOR, self.rect, border_radius=5)
        # Centering text vertically in input box
        screen.blit(self.txt_surface, (self.rect.x + 8, self.rect.y + (self.rect.height // 2 - 8)))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)


# --- Logic State ---
stack = []
capacity = 10
status_message = "Stack Initialized"
status_color = TEXT_COLOR
logic_message = "Waiting for operation..."
peek_highlight_idx = -1
peek_timer_start = 0

# UI Elements
val_input = InputBox(50, 180, 140, 40, text="", max_chars=9)
cap_input = InputBox(50, 90, 80, 40, text="10", is_numeric_only=True, max_chars=2)


def set_status(msg, color, logic_msg=""):
    global status_message, status_color, logic_message
    status_message = msg
    status_color = color
    logic_message = logic_msg


def set_capacity():
    global capacity, stack
    try:
        if not cap_input.text: return
        new_cap = int(cap_input.text)

        if new_cap > MAX_ALLOWED_CAPACITY:
            set_status(f"Error: Max Limit is {MAX_ALLOWED_CAPACITY}!", ERROR_COLOR, "Constraint: Capacity <= 10")
            cap_input.text = str(MAX_ALLOWED_CAPACITY)
            cap_input.txt_surface = font_ui.render(cap_input.text, True, TEXT_COLOR)
            return

        if new_cap < 1:
            set_status("Capacity must be >= 1", ERROR_COLOR, "Error: Invalid Size")
            return

        if len(stack) > new_cap:
            stack = stack[:new_cap]
            set_status(f"Resized to {new_cap}. Truncated.", ERROR_COLOR, f"stack = stack[:{new_cap}]")
        else:
            set_status(f"Capacity updated to {new_cap}", SUCCESS_COLOR, "Capacity variable updated")

        capacity = new_cap
    except ValueError:
        set_status("Invalid Capacity", ERROR_COLOR)


def push_item():
    val = val_input.text.strip()
    if not val:
        set_status("Enter a value first!", ERROR_COLOR, "if val is None: return")
        return

    if len(stack) >= capacity:
        set_status("Stack Overflow!", ERROR_COLOR, "if len(stack) == capacity: Overflow")
        return

    stack.append(val)
    val_input.text = ""
    val_input.txt_surface = font_ui.render("", True, TEXT_COLOR)
    set_status(f"Pushed: {val}", SUCCESS_COLOR, f"stack.append({val}) | Top: {len(stack) - 1}")


def pop_item():
    if len(stack) == 0:
        set_status("Stack Underflow!", ERROR_COLOR, "if len(stack) == 0: Underflow")
        return

    popped = stack.pop()
    set_status(f"Popped: {popped}", SUCCESS_COLOR, f"val = stack.pop() | New Top: {len(stack) - 1}")


def top_item():
    global peek_highlight_idx, peek_timer_start
    if len(stack) == 0:
        set_status("Stack is Empty", ERROR_COLOR, "return None")
        return

    peek_highlight_idx = len(stack) - 1
    peek_timer_start = pygame.time.get_ticks()
    set_status(f"Top Element: {stack[-1]}", HIGHLIGHT_COLOR, f"return stack[{len(stack) - 1}]")


# Buttons
btn_set_cap = Button(140, 90, 100, 40, "Set Cap", set_capacity)
btn_push = Button(200, 180, 100, 40, "Push", push_item)
btn_pop = Button(50, 240, 120, 50, "Pop", pop_item)
btn_top = Button(180, 240, 120, 50, "Top", top_item)

buttons = [btn_set_cap, btn_push, btn_pop, btn_top]
input_boxes = [val_input, cap_input]

# --- Main Loop ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()

    if peek_highlight_idx != -1:
        if current_time - peek_timer_start > 1000:
            peek_highlight_idx = -1
            set_status("Ready", TEXT_COLOR, "Waiting...")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for box in input_boxes:
            box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                btn.check_click(event.pos)

    for btn in buttons:
        btn.check_hover(mouse_pos)

    screen.fill(BACKGROUND_COLOR)

    # 1. UI Dashboard
    title_surf = font_title.render("STACK (LIFO)", True, ELEMENT_COLOR)
    screen.blit(title_surf, (50, 30))

    status_surf = font_ui.render(status_message, True, status_color)
    screen.blit(status_surf, (350, 30))

    logic_label = font_ui.render("Logic Flow:", True, Colors.LIGHT_GREY)
    screen.blit(logic_label, (350, 60))
    logic_surf = font_logic.render(f"> {logic_message}", True, Colors.TEAL_BRIGHT)
    screen.blit(logic_surf, (350, 85))

    lbl_cap = font_ui.render(f"Capacity (Max {MAX_ALLOWED_CAPACITY}):", True, Colors.LIGHT_GREY)
    screen.blit(lbl_cap, (50, 65))
    lbl_val = font_ui.render("Value:", True, Colors.LIGHT_GREY)
    screen.blit(lbl_val, (50, 155))

    for box in input_boxes: box.draw(screen)
    for btn in buttons: btn.draw(screen)

    # 2. Visualization
    bucket_center_x = 650  # Shifted right slightly for wider screen
    bucket_bottom_y = 650

    wall_height = capacity * (ELEM_HEIGHT + SPACING) + 20

    pygame.draw.line(screen, CONTAINER_COLOR,
                     (bucket_center_x - ELEM_WIDTH // 2 - 5, bucket_bottom_y),
                     (bucket_center_x - ELEM_WIDTH // 2 - 5, bucket_bottom_y - wall_height), 4)
    pygame.draw.line(screen, CONTAINER_COLOR,
                     (bucket_center_x + ELEM_WIDTH // 2 + 5, bucket_bottom_y),
                     (bucket_center_x + ELEM_WIDTH // 2 + 5, bucket_bottom_y - wall_height), 4)
    pygame.draw.line(screen, CONTAINER_COLOR,
                     (bucket_center_x - ELEM_WIDTH // 2 - 5, bucket_bottom_y),
                     (bucket_center_x + ELEM_WIDTH // 2 + 5, bucket_bottom_y), 4)

    # Elements
    for i, item in enumerate(stack):
        y_pos = bucket_bottom_y - (i + 1) * (ELEM_HEIGHT + SPACING) + SPACING
        x_pos = bucket_center_x - ELEM_WIDTH // 2
        rect = pygame.Rect(x_pos, y_pos, ELEM_WIDTH, ELEM_HEIGHT)

        bg_col = HIGHLIGHT_COLOR if i == peek_highlight_idx else ELEMENT_COLOR
        pygame.draw.rect(screen, bg_col, rect, border_radius=6)

        txt_surf = font_elem.render(str(item), True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)

        idx_surf = font_ui.render(f"[{i}]", True, Colors.LIGHT_GREY)
        screen.blit(idx_surf, (x_pos - 35, y_pos + 8))

    # Top Pointer
    if stack:
        top_y = bucket_bottom_y - (len(stack)) * (ELEM_HEIGHT + SPACING) + SPACING + ELEM_HEIGHT // 2
        top_x = bucket_center_x + ELEM_WIDTH // 2 + 10

        pygame.draw.line(screen, TEXT_COLOR, (top_x, top_y), (top_x + 30, top_y), 2)
        top_lbl = font_ui.render("TOP", True, TEXT_COLOR)
        screen.blit(top_lbl, (top_x + 35, top_y - 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()