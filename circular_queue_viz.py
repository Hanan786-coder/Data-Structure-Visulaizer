import pygame
import sys
import math
import Colors

# --- Configuration ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Map Colors
BACKGROUND_COLOR = Colors.GREY
FILLED_COLOR = Colors.TEAL
EMPTY_COLOR = (80, 80, 80)
HOVER_COLOR = Colors.TEAL_BRIGHT
HIGHLIGHT_COLOR = Colors.ORANGE
TEXT_COLOR = Colors.LIGHT_GREY
INPUT_BG_COLOR = Colors.BLACK
CONTAINER_COLOR = Colors.LIGHT_GREY
ERROR_COLOR = (255, 87, 87)
SUCCESS_COLOR = (0, 200, 81)

# Logic Constraints
MAX_ALLOWED_CAPACITY = 12 

# Dimensions
OUTER_RADIUS = 200
INNER_RADIUS = 115
CENTER = (650, 380)

# --- Font Loading ---
def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('Arial', size, bold=bold)

# Global fonts
font_title = get_font(25)
font_ui = get_font(17)
font_elem = get_font(19)
font_index = get_font(14, bold=True)
font_logic = get_font(13)
font_label = get_font(14, bold=True)


# --- Logic Structure: Array Based Circular Queue ---
class CircularQueueArray:
    def __init__(self, size):
        self.size = size
        self.queue = [None] * size
        self.front = -1
        self.rear = -1
        self.count = 0

    def enqueue(self, value):
        if self.count == self.size:
            return False  # Full

        if self.front == -1:  # First element
            self.front = 0
            self.rear = 0
        else:
            self.rear = (self.rear + 1) % self.size

        self.queue[self.rear] = value
        self.count += 1
        return True

    def dequeue(self):
        if self.count == 0:
            return None

        val = self.queue[self.front]
        self.queue[self.front] = None

        if self.front == self.rear:  # Last element removed
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.size

        self.count -= 1
        return val

    def peek(self):
        if self.count == 0: return None
        return self.queue[self.front]


# --- UI Classes ---
class Button:
    def __init__(self, x, y, w, h, text, action_func=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action_func
        self.is_hovered = False

    def draw(self, surface):
        color = HOVER_COLOR if self.is_hovered else FILLED_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        txt = font_ui.render(self.text, True, TEXT_COLOR)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        """Returns the result of the action if clicked, else None"""
        if self.is_hovered and self.action:
            return self.action()
        return None


class InputBox:
    def __init__(self, x, y, w, h, text='', max_chars=9, is_numeric_only=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = FILLED_COLOR
        self.color_inactive = Colors.LIGHT_GREY
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font_ui.render(text, True, TEXT_COLOR)
        self.active = False
        self.max_chars = max_chars
        self.is_numeric = is_numeric_only

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


# --- Helper: Draw Donut Segment (High Res) ---
def draw_donut_segment(surface, center, inner_r, outer_r, start_angle, end_angle, color, border=False):
    points = []
    step = 1

    # Outer Arc (Clockwise)
    for angle in range(int(start_angle), int(end_angle) + step, step):
        if angle > end_angle: angle = end_angle
        rad = math.radians(angle)
        x = center[0] + outer_r * math.cos(rad)
        y = center[1] + outer_r * math.sin(rad)
        points.append((x, y))

    # Inner Arc (Counter-Clockwise)
    for angle in range(int(end_angle), int(start_angle) - step, -step):
        if angle < start_angle: angle = start_angle
        rad = math.radians(angle)
        x = center[0] + inner_r * math.cos(rad)
        y = center[1] + inner_r * math.sin(rad)
        points.append((x, y))

    rad_start = math.radians(start_angle)
    points.append((center[0] + inner_r * math.cos(rad_start), center[1] + inner_r * math.sin(rad_start)))

    if border:
        pygame.draw.aalines(surface, color, True, points)
    else:
        pygame.draw.polygon(surface, color, points)
        pygame.draw.aalines(surface, color, True, points)


def draw_pointer_label(surface, text, angle_deg, center, radius, color):
    rad = math.radians(angle_deg)

    # Position for the text
    text_dist = radius + 35
    x = center[0] + text_dist * math.cos(rad)
    y = center[1] + text_dist * math.sin(rad)

    lbl = font_label.render(text, True, color)
    lbl_rect = lbl.get_rect(center=(x, y))
    surface.blit(lbl, lbl_rect)

    start_pos = (center[0] + (radius + 5) * math.cos(rad), center[1] + (radius + 5) * math.sin(rad))
    end_pos = (center[0] + (radius + 20) * math.cos(rad), center[1] + (radius + 20) * math.sin(rad))
    pygame.draw.line(surface, color, start_pos, end_pos, 2)


# --- Main Run Function ---
def run(screen):
    clock = pygame.time.Clock()

    # --- Local Logic State ---
    state = {
        "cq": CircularQueueArray(8),
        "capacity": 8,
        "status_msg": "Array Circular Queue Initialized",
        "status_col": TEXT_COLOR,
        "logic_msg": "Waiting...",
        "peek_mode": False,
        "peek_timer": 0
    }

    # UI Elements
    val_input = InputBox(50, 180, 140, 40)
    cap_input = InputBox(50, 90, 80, 40, text="8", is_numeric_only=True, max_chars=2)

    # --- Inner Helper Functions ---
    def set_status(msg, col, logic=""):
        state["status_msg"] = msg
        state["status_col"] = col
        state["logic_msg"] = logic

    def set_capacity():
        try:
            if not cap_input.text: return
            new_cap = int(cap_input.text)

            if new_cap > MAX_ALLOWED_CAPACITY:
                set_status(f"Max Capacity is {MAX_ALLOWED_CAPACITY}", ERROR_COLOR)
                cap_input.text = str(MAX_ALLOWED_CAPACITY)
                cap_input.txt_surface = font_ui.render(cap_input.text, True, TEXT_COLOR)
                return

            if new_cap < 1:
                set_status("Capacity must be >= 1", ERROR_COLOR)
                return

            # Reset Queue with new capacity
            state["capacity"] = new_cap
            state["cq"] = CircularQueueArray(new_cap)
            set_status(f"Capacity set to {new_cap}. Queue Reset.", SUCCESS_COLOR)

        except ValueError:
            set_status("Invalid Capacity", ERROR_COLOR)

    def do_enqueue():
        val = val_input.text.strip()
        if not val:
            set_status("Enter a value!", ERROR_COLOR, "if val is None: return")
            return

        success = state["cq"].enqueue(val)
        if not success:
            set_status("Queue Overflow! (Full)", ERROR_COLOR, "if count == size: Overflow")
            return

        val_input.text = ""
        val_input.txt_surface = font_ui.render("", True, TEXT_COLOR)
        set_status(f"Enqueued: {val}", SUCCESS_COLOR, f"rear = (rear + 1) % {state['capacity']}")

    def do_dequeue():
        val = state["cq"].dequeue()
        if val is None:
            set_status("Queue Underflow! (Empty)", ERROR_COLOR, "if count == 0: Underflow")
        else:
            set_status(f"Dequeued: {val}", SUCCESS_COLOR, f"front = (front + 1) % {state['capacity']}")

    def do_peek():
        val = state["cq"].peek()
        if val is None:
            set_status("Queue is Empty", ERROR_COLOR, "return None")
        else:
            state["peek_mode"] = True
            state["peek_timer"] = pygame.time.get_ticks()
            set_status(f"Front Item: {val}", HIGHLIGHT_COLOR, f"return queue[{state['cq'].front}]")

    def go_back():
        return "back"

    # Buttons
    btn_set_cap = Button(140, 90, 100, 40, "Set Cap", set_capacity)
    btn_enq = Button(200, 180, 100, 40, "Enqueue", do_enqueue)
    btn_deq = Button(50, 240, 120, 50, "Dequeue", do_dequeue)
    btn_peek = Button(180, 240, 120, 50, "Peek", do_peek)
    btn_back = Button(900, 15, 80, 40, "← Back", go_back)

    buttons = [btn_set_cap, btn_enq, btn_deq, btn_peek, btn_back]
    input_boxes = [val_input, cap_input]

    # --- Main Loop ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()

        # Handle Peek Highlight Timer
        if state["peek_mode"]:
            if current_time - state["peek_timer"] > 1000:
                state["peek_mode"] = False
                set_status("Ready", TEXT_COLOR, "Waiting...")

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            for box in input_boxes:
                box.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    result = btn.check_click(event.pos)
                    # Handle return signal
                    if result == "back":
                        return "back"

        for btn in buttons:
            btn.check_hover(mouse_pos)

        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)

        # 1. Dashboard
        screen.blit(font_title.render("CIRCULAR QUEUE (Array)", True, FILLED_COLOR), (50, 30))
        screen.blit(font_ui.render(state["status_msg"], True, state["status_col"]), (450, 30))
        screen.blit(font_ui.render("Logic Flow:", True, TEXT_COLOR), (450, 60))
        screen.blit(font_logic.render(f"> {state['logic_msg']}", True, HOVER_COLOR), (450, 85))

        # Labels
        screen.blit(font_ui.render(f"Capacity (Max {MAX_ALLOWED_CAPACITY}):", True, TEXT_COLOR), (50, 65))
        screen.blit(font_ui.render(f"Count: {state['cq'].count} / {state['capacity']}", True, TEXT_COLOR), (50, 135))
        screen.blit(font_ui.render("Value:", True, TEXT_COLOR), (50, 155))

        for box in input_boxes: box.draw(screen)
        for btn in buttons: btn.draw(screen)

        # 2. Visualization (The Donut)
        angle_step = 360 / state["capacity"]
        cq_obj = state["cq"]

        for i in range(state["capacity"]):
            start_deg = -90 + (i * angle_step) + 2
            end_deg = -90 + ((i + 1) * angle_step) - 2

            is_filled = cq_obj.queue[i] is not None

            bg_col = EMPTY_COLOR
            should_fill = is_filled

            if state["peek_mode"] and i == cq_obj.front:
                bg_col = HIGHLIGHT_COLOR
                should_fill = True
            elif is_filled:
                bg_col = FILLED_COLOR

            if should_fill:
                draw_donut_segment(screen, CENTER, INNER_RADIUS, OUTER_RADIUS, start_deg, end_deg, bg_col)
            else:
                draw_donut_segment(screen, CENTER, INNER_RADIUS, OUTER_RADIUS, start_deg, end_deg, Colors.LIGHT_GREY, border=True)

            # Draw Index
            mid_angle = (start_deg + end_deg) / 2
            mid_rad = math.radians(mid_angle)
            idx_x = CENTER[0] + (OUTER_RADIUS + 15) * math.cos(mid_rad)
            idx_y = CENTER[1] + (OUTER_RADIUS + 15) * math.sin(mid_rad)
            idx_surf = font_index.render(str(i), True, Colors.LIGHT_GREY)
            screen.blit(idx_surf, idx_surf.get_rect(center=(idx_x, idx_y)))

            # Draw Value
            if is_filled:
                val_dist = (INNER_RADIUS + OUTER_RADIUS) / 2
                val_x = CENTER[0] + val_dist * math.cos(mid_rad)
                val_y = CENTER[1] + val_dist * math.sin(mid_rad)
                val_surf = font_elem.render(str(cq_obj.queue[i]), True, TEXT_COLOR)
                screen.blit(val_surf, val_surf.get_rect(center=(val_x, val_y)))

        # 3. Draw Pointers
        if cq_obj.count > 0:
            f_angle = -90 + (cq_obj.front * angle_step) + (angle_step / 2)
            r_angle = -90 + (cq_obj.rear * angle_step) + (angle_step / 2)

            if cq_obj.front == cq_obj.rear:
                # Stack vertically
                draw_pointer_label(screen, "FRONT", f_angle, CENTER, OUTER_RADIUS + 20, TEXT_COLOR)
                draw_pointer_label(screen, "REAR", r_angle, CENTER, OUTER_RADIUS + 60, TEXT_COLOR)
            else:
                draw_pointer_label(screen, "FRONT", f_angle, CENTER, OUTER_RADIUS + 25, TEXT_COLOR)
                draw_pointer_label(screen, "REAR", r_angle, CENTER, OUTER_RADIUS + 25, TEXT_COLOR)

        pygame.display.flip()
        clock.tick(60)

    return "back"