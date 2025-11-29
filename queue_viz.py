import pygame
import sys
import Colors

# --- Configuration ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

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
ELEM_WIDTH = 100
ELEM_HEIGHT = 70
SPACING = 5
START_X = 300
MAX_ALLOWED_CAPACITY = 6

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Queue Visualization (DSA Project)")
clock = pygame.time.Clock()


# --- Font Loading ---
def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('Arial', size, bold=bold)


# --- REDUCED FONT SIZES (~30% smaller) ---
font_title = get_font(28)  # Was 32
font_ui = get_font(17)  # Was 20
font_elem = get_font(19)  # Was 24
font_index = get_font(11)  # Was 14
font_logic = get_font(13)  # Was 18


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
        # Center vertically
        screen.blit(self.txt_surface, (self.rect.x + 8, self.rect.y + (self.rect.height // 2 - 8)))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)


# --- Logic State ---
queue = []
capacity = 6
status_message = "Queue Initialized"
status_color = TEXT_COLOR
logic_message = "Waiting for operation..."
peek_highlight_idx = -1
peek_timer_start = 0

# UI
val_input = InputBox(50, 180, 140, 40, text="", max_chars=9)
cap_input = InputBox(50, 100, 80, 40, text="6", is_numeric_only=True, max_chars=2)


def set_status(msg, color, logic_msg=""):
    global status_message, status_color, logic_message
    status_message = msg
    status_color = color
    logic_message = logic_msg


def set_capacity():
    global capacity, queue
    try:
        if not cap_input.text: return
        new_cap = int(cap_input.text)

        if new_cap > MAX_ALLOWED_CAPACITY:
            set_status(f"Error: Max Limit is {MAX_ALLOWED_CAPACITY}!", ERROR_COLOR, "Constraint: Capacity <= 6")
            cap_input.text = str(MAX_ALLOWED_CAPACITY)
            cap_input.txt_surface = font_ui.render(cap_input.text, True, TEXT_COLOR)
            return

        if new_cap < 1:
            set_status("Capacity must be >= 1", ERROR_COLOR, "Error: Invalid Size")
            return

        if len(queue) > new_cap:
            queue = queue[:new_cap]
            set_status(f"Resized to {new_cap}. Truncated.", ERROR_COLOR, "Rear items removed")
        else:
            set_status(f"Capacity updated to {new_cap}", SUCCESS_COLOR, "capacity = " + str(new_cap))
        capacity = new_cap
    except ValueError:
        set_status("Invalid Capacity", ERROR_COLOR)


def enqueue_item():
    val = val_input.text.strip()
    if not val:
        set_status("Enter a value first!", ERROR_COLOR, "if val is None: return")
        return

    if len(queue) >= capacity:
        set_status("Queue Overflow!", ERROR_COLOR, "if size == capacity: Overflow")
        return

    queue.append(val)
    val_input.text = ""
    val_input.txt_surface = font_ui.render("", True, TEXT_COLOR)
    set_status(f"Enqueued: {val}", SUCCESS_COLOR, f"queue[rear] = {val} | rear++")


def dequeue_item():
    if len(queue) == 0:
        set_status("Queue Underflow!", ERROR_COLOR, "if size == 0: Underflow")
        return

    removed = queue.pop(0)
    set_status(f"Dequeued: {removed}", SUCCESS_COLOR, f"val = queue[0] | Shift Left | rear--")


def peek_item():
    global peek_highlight_idx, peek_timer_start
    if len(queue) == 0:
        set_status("Queue is Empty", ERROR_COLOR, "return None")
        return

    peek_highlight_idx = 0
    peek_timer_start = pygame.time.get_ticks()
    set_status(f"Front Item: {queue[0]}", HIGHLIGHT_COLOR, "return queue[front]")


# Buttons
btn_set_cap = Button(140, 100, 100, 40, "Set Cap", set_capacity)
btn_enq = Button(200, 180, 100, 40, "Enqueue", enqueue_item)
btn_deq = Button(50, 240, 120, 50, "Dequeue", dequeue_item)
btn_peek = Button(180, 240, 120, 50, "Peek", peek_item)

buttons = [btn_set_cap, btn_enq, btn_deq, btn_peek]
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
    title_surf = font_title.render("QUEUE (FIFO)", True, ELEMENT_COLOR)
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
    container_width = capacity * (ELEM_WIDTH + SPACING) + SPACING
    container_y = 400

    # Guidelines
    pygame.draw.line(screen, CONTAINER_COLOR,
                     (START_X, container_y - 10),
                     (START_X + container_width, container_y - 10), 4)
    pygame.draw.line(screen, CONTAINER_COLOR,
                     (START_X, container_y + ELEM_HEIGHT + 10),
                     (START_X + container_width, container_y + ELEM_HEIGHT + 10), 4)

    # Elements
    for i, item in enumerate(queue):
        x_pos = START_X + i * (ELEM_WIDTH + SPACING) + SPACING
        rect = pygame.Rect(x_pos, container_y, ELEM_WIDTH, ELEM_HEIGHT)

        bg_col = HIGHLIGHT_COLOR if i == peek_highlight_idx else ELEMENT_COLOR
        pygame.draw.rect(screen, bg_col, rect, border_radius=6)

        txt_surf = font_elem.render(str(item), True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)

        # Index
        idx_surf = font_index.render(f"{i}", True, Colors.LIGHT_GREY)
        screen.blit(idx_surf, (x_pos + 6, container_y + 4))

    # Pointers
    if queue:
        # FRONT
        front_x = START_X + SPACING + ELEM_WIDTH // 2
        front_y = container_y - 20
        pygame.draw.polygon(screen, TEXT_COLOR,
                            [(front_x, front_y), (front_x - 10, front_y - 15), (front_x + 10, front_y - 15)])
        lbl_front = font_index.render("FRONT", True, TEXT_COLOR)
        screen.blit(lbl_front, (front_x - 20, front_y - 35))

        # REAR
        rear_idx = len(queue) - 1
        rear_x = START_X + rear_idx * (ELEM_WIDTH + SPACING) + SPACING + ELEM_WIDTH // 2
        rear_y = container_y + ELEM_HEIGHT + 20
        pygame.draw.polygon(screen, TEXT_COLOR,
                            [(rear_x, rear_y), (rear_x - 10, rear_y + 15), (rear_x + 10, rear_y + 15)])
        lbl_rear = font_index.render("REAR", True, TEXT_COLOR)
        screen.blit(lbl_rear, (rear_x - 15, rear_y + 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()