import pygame
import sys
import random
import Colors

# --- Configuration ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SIDEBAR_WIDTH = 300

# Colors
BG_COLOR = Colors.GREY
SIDEBAR_COLOR = (30, 30, 35)
NODE_COLOR = Colors.TEAL
COMPARE_COLOR = (255, 215, 0)  # Gold
SWAP_COLOR = (155, 89, 182)  # Purple
SORTED_COLOR = (46, 204, 113)  # Green
TEXT_COLOR = Colors.LIGHT_GREY
BUTTON_COLOR = Colors.TEAL
BUTTON_HOVER = Colors.TEAL_BRIGHT
INPUT_BG = (50, 50, 55)
ERROR_COLOR = (255, 87, 87)

# Dimensions
NODE_W = 60
NODE_H = 45
GAP = 30
START_Y = 300


# --- Fonts ---
def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('Arial', size, bold=bold)


font_header = get_font(28, bold=True)
font_ui = get_font(16)
font_val = get_font(20, bold=True)
font_small = get_font(14)
font_logic = get_font(22)


# --- UI Components ---

class Button:
    def __init__(self, x, y, w, h, text, func, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func = func
        self.base_color = color
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False

    def draw(self, surface):
        col = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, col, self.rect, border_radius=5)
        txt = font_ui.render(self.text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.func:
                return self.func() # Return the result of the function
        return None


class InputBox:
    def __init__(self, x, y, w, h, text='', numeric_only=False, max_chars=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False
        self.color_inactive = (100, 100, 100)
        self.color_active = Colors.TEAL
        self.numeric_only = numeric_only
        self.max_chars = max_chars

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                valid = False
                if self.numeric_only:
                    if event.unicode.isdigit(): valid = True
                else:
                    if event.unicode.isdigit() or event.unicode in ', ': valid = True

                if valid and len(self.text) < self.max_chars:
                    self.text += event.unicode

    def draw(self, surface):
        col = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=5)
        pygame.draw.rect(surface, col, self.rect, 2, border_radius=5)
        txt = font_ui.render(self.text, True, TEXT_COLOR)
        surface.blit(txt, (self.rect.x + 5, self.rect.y + (self.rect.height // 2 - 8)))


class Slider:
    def __init__(self, x, y, w, min_val, max_val, initial):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial
        self.dragging = False
        self.handle_rect = pygame.Rect(x, y - 5, 10, 30)
        self.update_handle()

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + (self.rect.width * ratio)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.rect.x
                rel_x = max(0, min(rel_x, self.rect.width))
                ratio = rel_x / self.rect.width
                self.val = self.min_val + (self.max_val - self.min_val) * ratio
                self.update_handle()

    def draw(self, surface):
        pygame.draw.line(surface, (100, 100, 100), (self.rect.left, self.rect.centery),
                         (self.rect.right, self.rect.centery), 4)
        pygame.draw.rect(surface, Colors.TEAL, self.handle_rect, border_radius=5)
        lbl = font_small.render(f"Speed: {int(self.val)}ms", True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.x, self.rect.y - 20))


# --- Logic & State Management ---

class BubbleSortVisualizer:
    def __init__(self):
        self.array = []
        self.history = []
        self.step_index = 0
        self.playing = False
        self.last_update = 0
        self.finished = False
        self.status_msg = "Welcome"
        self.status_color = TEXT_COLOR
        self.sort_mode = "ASC"  # "ASC" or "DESC"

    def set_msg(self, msg, color=TEXT_COLOR):
        self.status_msg = msg
        self.status_color = color

    def generate_random(self, size):
        if not (2 <= size <= 8):
            self.set_msg("Size must be 2-8!", ERROR_COLOR)
            return

        self.array = [random.randint(10, 99) for _ in range(size)]
        self.set_msg(f"Generated {size} items", Colors.TEAL)
        self.precompute_history()

    def load_manual(self, text):
        try:
            parts = text.split(',')
            new_arr = []
            for p in parts:
                if p.strip():
                    val = int(p.strip())
                    new_arr.append(val)

            if 2 <= len(new_arr) <= 8:
                self.array = new_arr
                self.set_msg("Manual Input Loaded", Colors.TEAL)
                self.precompute_history()
                return True
            else:
                self.set_msg("Error: Input count must be 2-8", ERROR_COLOR)
        except ValueError:
            self.set_msg("Error: Numbers only", ERROR_COLOR)
        return False

    def toggle_sort_mode(self):
        self.sort_mode = "DESC" if self.sort_mode == "ASC" else "ASC"
        if self.array:
            self.precompute_history()

    def precompute_history(self):
        self.history = []
        arr = self.array[:]
        n = len(arr)
        is_asc = self.sort_mode == "ASC"
        op_str = ">" if is_asc else "<"
        mode_label = "Ascending" if is_asc else "Descending"

        # Initial State
        self.history.append({
            'arr': arr[:],
            'colors': [NODE_COLOR] * n,
            'stats': (0, 0),
            'desc': f"Start ({mode_label})"
        })

        comps = 0
        swaps = 0

        for i in range(n):
            for j in range(0, n - i - 1):
                # 1. Compare State
                colors = [NODE_COLOR] * n
                # Mark sorted part
                for k in range(n - i, n): colors[k] = SORTED_COLOR

                colors[j] = COMPARE_COLOR
                colors[j + 1] = COMPARE_COLOR

                comps += 1
                self.history.append({
                    'arr': arr[:],
                    'colors': colors[:],
                    'stats': (comps, swaps),
                    'desc': f"Comparing {arr[j]} {op_str} {arr[j + 1]}?"
                })

                # Logic Check
                should_swap = arr[j] > arr[j + 1] if is_asc else arr[j] < arr[j + 1]

                if should_swap:
                    # 2. Swap Needed State
                    colors[j] = SWAP_COLOR
                    colors[j + 1] = SWAP_COLOR
                    self.history.append({
                        'arr': arr[:],
                        'colors': colors[:],
                        'stats': (comps, swaps),
                        'desc': "Condition Met: Swapping..."
                    })

                    # Perform Swap
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swaps += 1

                    # 3. Post-Swap State
                    self.history.append({
                        'arr': arr[:],
                        'colors': colors[:],
                        'stats': (comps, swaps),
                        'desc': "Swapped"
                    })

            # Element Sorted
            colors = [NODE_COLOR] * n
            for k in range(n - i - 1, n): colors[k] = SORTED_COLOR
            self.history.append({
                'arr': arr[:],
                'colors': colors[:],
                'stats': (comps, swaps),
                'desc': f"Element {arr[n - i - 1]} Sorted"
            })

        # Final Sorted State
        self.history.append({
            'arr': arr[:],
            'colors': [SORTED_COLOR] * n,
            'stats': (comps, swaps),
            'desc': "Algorithm Complete"
        })

        self.reset()

    def reset(self):
        self.step_index = 0
        self.playing = False
        self.finished = False

    def next_step(self):
        if self.step_index < len(self.history) - 1:
            self.step_index += 1
        else:
            self.finished = True
            self.playing = False

    def prev_step(self):
        if self.step_index > 0:
            self.step_index -= 1
            self.finished = False

    def toggle_play(self):
        if self.finished:
            self.reset()
            self.playing = True
        else:
            self.playing = not self.playing

    def update(self, delay):
        if self.playing:
            now = pygame.time.get_ticks()
            if now - self.last_update > delay:
                self.next_step()
                self.last_update = now

    def draw_viz(self, surface):
        if not self.history:
            return

        state = self.history[self.step_index]
        arr = state['arr']
        colors = state['colors']

        # Calculate centering
        total_w = len(arr) * (NODE_W + GAP) - GAP
        start_x = SIDEBAR_WIDTH + (SCREEN_WIDTH - SIDEBAR_WIDTH - total_w) // 2

        # --- Logic Flow Display ---
        label_x = SIDEBAR_WIDTH + 40
        label_y = 40

        # Heading
        lbl_logic = font_ui.render("Logic Flow:", True, (150, 150, 150))
        surface.blit(lbl_logic, (label_x, label_y))

        # Content
        desc_txt = f"> {state['desc']}"
        desc_surf = font_logic.render(desc_txt, True, Colors.TEAL_BRIGHT)
        surface.blit(desc_surf, (label_x, label_y + 25))

        # --- Draw Nodes & Arrows (Linked List Style) ---
        for i, val in enumerate(arr):
            x = start_x + i * (NODE_W + GAP)
            y = START_Y

            rect = pygame.Rect(x, y, NODE_W, NODE_H)
            pygame.draw.rect(surface, colors[i], rect, border_radius=8)

            txt = font_val.render(str(val), True, (255, 255, 255))
            surface.blit(txt, txt.get_rect(center=rect.center))

            idx = font_small.render(str(i), True, (100, 100, 100))
            surface.blit(idx, (rect.centerx - 5, rect.bottom + 5))

            # Draw Arrow
            if i < len(arr) - 1:
                arrow_start = (rect.right, rect.centery)
                arrow_end = (rect.right + GAP, rect.centery)
                pygame.draw.line(surface, TEXT_COLOR, arrow_start, arrow_end, 2)
                pygame.draw.polygon(surface, TEXT_COLOR, [
                    (arrow_end[0], arrow_end[1]),
                    (arrow_end[0] - 5, arrow_end[1] - 5),
                    (arrow_end[0] - 5, arrow_end[1] + 5)
                ])


# --- Main Run Function ---
def run(screen):
    clock = pygame.time.Clock()
    
    # Initialize Visualizer Logic
    viz = BubbleSortVisualizer()

    # --- UI Callbacks (Defined inside run to capture `viz` and inputs) ---
    def btn_rand_action():
        try:
            s = int(size_input.text)
            viz.generate_random(s)
        except ValueError:
            viz.set_msg("Size must be a number", ERROR_COLOR)

    def btn_load_action():
        if viz.load_manual(input_box.text):
            input_box.text = ""

    def btn_prev_action(): viz.prev_step(); viz.playing = False
    def btn_play_action(): viz.toggle_play()
    def btn_next_action(): viz.next_step(); viz.playing = False
    def btn_reset_action(): viz.reset()
    def btn_mode_action(): viz.toggle_sort_mode()
    def go_back(): return "back"

    # --- UI Layout Initialization ---
    
    # 1. Size
    size_input = InputBox(20, 75, 50, 35, text="5", numeric_only=True, max_chars=1)
    btn_rand = Button(80, 75, 200, 35, "Randomize (Size 2-8)", btn_rand_action)

    # 2. Manual
    input_box = InputBox(20, 145, 190, 35, text="")
    btn_load = Button(220, 145, 60, 35, "Load", btn_load_action)

    # 3. Sort Mode Button
    btn_mode = Button(20, 185, 260, 35, "Mode: ASC", btn_mode_action, color=Colors.ORANGE)

    # 4. Playback
    btn_prev = Button(20, 240, 80, 40, "Prev", btn_prev_action)
    btn_play = Button(110, 240, 80, 40, "Play/||", btn_play_action)
    btn_next = Button(200, 240, 80, 40, "Next", btn_next_action)
    btn_reset = Button(20, 290, 260, 35, "Reset", btn_reset_action, color=Colors.ORANGE)
    
    # 5. Back Button
    btn_back = Button(900, 15, 80, 40, "← Back", go_back, color=Colors.ORANGE)

    speed_slider = Slider(20, 360, 260, 50, 1000, 500)

    # Group UI Elements
    ui_elements = [size_input, btn_rand, input_box, btn_load, btn_mode, 
                   btn_prev, btn_play, btn_next, btn_reset, speed_slider, btn_back]

    # Initialize with default data
    viz.generate_random(5)

    running = True
    while running:
        viz.update(speed_slider.val)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            size_input.handle_event(event)
            input_box.handle_event(event)
            speed_slider.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in ui_elements:
                    if isinstance(btn, Button):
                        result = btn.handle_event(event)
                        if result == "back":
                            return "back"

            if event.type == pygame.MOUSEMOTION:
                for btn in ui_elements:
                    if isinstance(btn, Button):
                        btn.handle_event(event)
                    elif isinstance(btn, Slider):
                        btn.handle_event(event)

        screen.fill(BG_COLOR)

        # Sidebar Background
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)
        pygame.draw.line(screen, Colors.TEAL, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)

        # Labels
        title = font_header.render("Bubble Sort", True, Colors.TEAL)
        screen.blit(title, (20, 20))

        screen.blit(font_small.render("1. Set Array Size (2-8):", True, TEXT_COLOR), (20, 55))
        screen.blit(font_small.render("2. Manual Input :", True, TEXT_COLOR), (20, 125))
        screen.blit(font_small.render("3. Controls:", True, TEXT_COLOR), (20, 220))

        # Update button text dynamically
        btn_mode.text = "Mode: ASC" if viz.sort_mode == "ASC" else "Mode: DESC"

        # Draw UI
        for el in ui_elements:
            el.draw(screen)

        # Status Message
        status_surf = font_ui.render(viz.status_msg, True, viz.status_color)
        screen.blit(status_surf, (20, 400))

        # Statistics
        pygame.draw.line(screen, (50, 50, 50), (20, 430), (280, 430), 1)
        screen.blit(font_val.render("Statistics", True, TEXT_COLOR), (20, 440))

        curr_comps = 0
        curr_swaps = 0
        if viz.history:
            curr_comps, curr_swaps = viz.history[viz.step_index]['stats']

        stats_info = [
            f"Comparisons: {curr_comps}",
            f"Swaps: {curr_swaps}",
            f"Step: {viz.step_index + 1} / {len(viz.history)}",
            "Time: O(n²)",
            "Space: O(1)"
        ]

        for i, txt in enumerate(stats_info):
            col = Colors.ORANGE if i < 3 else TEXT_COLOR
            surf = font_ui.render(txt, True, col)
            screen.blit(surf, (20, 470 + i * 25))

        # Draw Visualization (Nodes)
        viz.draw_viz(screen)

        # Legend
        leg_y = 650
        leg_x = SIDEBAR_WIDTH + 50

        def draw_legend(x, color, text):
            r = pygame.Rect(x, leg_y, 20, 20)
            pygame.draw.rect(screen, color, r, border_radius=4)
            t = font_small.render(text, True, TEXT_COLOR)
            screen.blit(t, (x + 30, leg_y + 2))
            return x + 120

        lx = draw_legend(leg_x, NODE_COLOR, "Idle")
        lx = draw_legend(lx, COMPARE_COLOR, "Compare")
        lx = draw_legend(lx, SWAP_COLOR, "Swap")
        lx = draw_legend(lx, SORTED_COLOR, "Sorted")

        pygame.display.flip()
        clock.tick(60)

    return "back"