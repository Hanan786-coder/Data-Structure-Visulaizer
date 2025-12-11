import pygame
import sys
import random
import Colors  # Your custom colors file

# --- Configuration ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SIDEBAR_WIDTH = 300

# Colors
BG_COLOR = Colors.GREY
SIDEBAR_COLOR = (30, 30, 35)

# Node Colors
NODE_DEFAULT = Colors.TEAL          # Unsorted
NODE_SORTED = (46, 204, 113)        # Green (Sorted portion)
NODE_KEY = (255, 215, 0)            # Gold (The element currently being placed)
NODE_COMPARE = (155, 89, 182)       # Purple (Element being compared against)
NODE_SHIFT = (231, 76, 60)          # Red (Shift animation hint)

TEXT_COLOR = Colors.LIGHT_GREY
BUTTON_COLOR = Colors.TEAL
BUTTON_HOVER = Colors.TEAL_BRIGHT
INPUT_BG = (50, 50, 55)
ERROR_COLOR = (255, 87, 87)

# Dimensions
NODE_W = 60
NODE_H = 50
GAP = 15
START_Y = 300  # Vertically centered

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Insertion Sort Visualization")
clock = pygame.time.Clock()


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
font_logic = get_font(18)


# --- UI Components (Identical to Merge Sort) ---
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
                self.func()


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
                    if event.unicode.isdigit() or event.unicode == ',': valid = True
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

class InsertionSortVisualizer:
    def __init__(self):
        self.initial_array = []
        self.history = []
        self.step_index = 0
        self.playing = False
        self.last_update = 0
        self.finished = False
        self.status_msg = "Welcome"
        self.status_color = TEXT_COLOR
        self.comps_count = 0
        self.swaps_count = 0 # Shifts in insertion sort

    def set_msg(self, msg, color=TEXT_COLOR):
        self.status_msg = msg
        self.status_color = color

    def generate_random(self, size):
        if not (2 <= size <= 12): # Allowed slightly larger size for Insertion
            self.set_msg("Size must be 2-12!", ERROR_COLOR)
            return
        self.initial_array = [random.randint(10, 99) for _ in range(size)]
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
            if 2 <= len(new_arr) <= 12:
                self.initial_array = new_arr
                self.set_msg("Manual Input Loaded", Colors.TEAL)
                self.precompute_history()
            else:
                self.set_msg("Error: Input count 2-12", ERROR_COLOR)
        except ValueError:
            self.set_msg("Error: Numbers only", ERROR_COLOR)

    def save_state(self, current_arr, colors, desc, active_key_idx=None, compare_idx=None):
        # We save who is the "Key" (being moved) to draw it lifted up
        self.history.append({
            'values': current_arr[:],
            'colors': colors[:],
            'stats': (self.comps_count, self.swaps_count),
            'desc': desc,
            'key_idx': active_key_idx,    # Index of the floating key
            'compare_idx': compare_idx    # Index being compared against
        })

    def precompute_history(self):
        self.history = []
        self.comps_count = 0
        self.swaps_count = 0
        arr = self.initial_array[:]
        n = len(arr)

        # Initial State
        colors = [NODE_DEFAULT] * n
        colors[0] = NODE_SORTED # First element is trivially sorted
        self.save_state(arr, colors, "Start: First element is sorted")

        for i in range(1, n):
            key = arr[i]
            j = i - 1
            
            # Highlight the key being picked up
            colors = [NODE_SORTED if x < i else NODE_DEFAULT for x in range(n)]
            colors[i] = NODE_KEY
            self.save_state(arr, colors, f"Pick up Key: {key}", active_key_idx=i)

            while j >= 0:
                self.comps_count += 1
                
                # Highlight comparison
                colors[j] = NODE_COMPARE
                self.save_state(arr, colors, f"Compare Key ({key}) vs {arr[j]}", active_key_idx=j+1, compare_idx=j)

                if key < arr[j]:
                    # Shift
                    self.swaps_count += 1
                    arr[j + 1] = arr[j]
                    colors[j] = NODE_SHIFT # Briefly show shift color
                    colors[j+1] = NODE_KEY # The hole moves
                    
                    self.save_state(arr, colors, f"{key} < {arr[j]}. Shift {arr[j]} right.", active_key_idx=j, compare_idx=j+1)
                    
                    # Reset color after shift
                    colors[j+1] = NODE_SORTED
                    j -= 1
                else:
                    # Found position
                    colors[j] = NODE_SORTED
                    self.save_state(arr, colors, f"{key} >= {arr[j]}. Position found.", active_key_idx=j+1)
                    break
            
            arr[j + 1] = key
            
            # Place Key
            colors = [NODE_SORTED if x <= i else NODE_DEFAULT for x in range(n)]
            self.save_state(arr, colors, f"Insert {key} at index {j+1}", active_key_idx=None)

        # Final State
        colors = [NODE_SORTED] * n
        self.save_state(arr, colors, "Sorting Complete")
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
        vals = state['values']
        cols = state['colors']
        key_idx = state['key_idx']
        
        # Centering
        total_w = len(vals) * (NODE_W + GAP) - GAP
        start_x = SIDEBAR_WIDTH + (SCREEN_WIDTH - SIDEBAR_WIDTH - total_w) // 2
        
        # --- Logic Flow Text ---
        label_x = SIDEBAR_WIDTH + 40
        label_y = 30
        surface.blit(font_ui.render("Logic Flow:", True, (150, 150, 150)), (label_x, label_y))
        desc_surf = font_logic.render(f"> {state['desc']}", True, Colors.TEAL_BRIGHT)
        surface.blit(desc_surf, (label_x, label_y + 25))

        # --- Draw Nodes ---
        for i, val in enumerate(vals):
            # Calculate positions
            x = start_x + i * (NODE_W + GAP)
            y = START_Y
            
            # If this is the active key, lift it up visually
            if key_idx is not None and i == key_idx:
                y -= 80 # Lift height
                
            rect = pygame.Rect(x, y, NODE_W, NODE_H)
            
            # Shadow for lifted node
            if key_idx is not None and i == key_idx:
                shadow_rect = pygame.Rect(x + 5, START_Y + 45, NODE_W - 10, 10)
                pygame.draw.ellipse(surface, (20, 20, 25), shadow_rect)
            
            pygame.draw.rect(surface, cols[i], rect, border_radius=8)
            pygame.draw.rect(surface, (200, 200, 200) if cols[i] == NODE_KEY else (30,30,30), rect, 2, border_radius=8)
            
            txt = font_val.render(str(val), True, (255, 255, 255) if cols[i] != NODE_KEY else (0,0,0))
            surface.blit(txt, txt.get_rect(center=rect.center))
            
            # Draw Index below
            idx_txt = font_small.render(str(i), True, (100,100,100))
            surface.blit(idx_txt, idx_txt.get_rect(center=(rect.centerx, START_Y + NODE_H + 15)))


# --- App Instance ---
viz = InsertionSortVisualizer()


# --- Controls Actions ---
def btn_rand_action():
    try:
        s = int(size_input.text)
        viz.generate_random(s)
    except ValueError:
        viz.set_msg("Size must be number", ERROR_COLOR)


def btn_load_action(): viz.load_manual(input_box.text)
def btn_prev_action(): viz.prev_step(); viz.playing = False
def btn_play_action(): viz.toggle_play()
def btn_next_action(): viz.next_step(); viz.playing = False
def btn_reset_action(): viz.reset()


# Layout (Identical Positions to Merge Sort)
size_input = InputBox(20, 75, 50, 35, text="8", numeric_only=True, max_chars=2)
btn_rand = Button(80, 75, 200, 35, "Randomize (Size 2-12)", btn_rand_action)
input_box = InputBox(20, 145, 190, 35, text="")
btn_load = Button(220, 145, 60, 35, "Load", btn_load_action)
btn_prev = Button(20, 240, 80, 40, "Prev", btn_prev_action)
btn_play = Button(110, 240, 80, 40, "Play/||", btn_play_action)
btn_next = Button(200, 240, 80, 40, "Next", btn_next_action)
btn_reset = Button(20, 290, 260, 35, "Reset", btn_reset_action, color=Colors.ORANGE)
speed_slider = Slider(20, 360, 260, 50, 1000, 300)

ui_elements = [size_input, btn_rand, input_box, btn_load, btn_prev, btn_play, btn_next, btn_reset, speed_slider]

viz.generate_random(8)

# --- Main Loop ---
running = True
while running:
    viz.update(speed_slider.val)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        size_input.handle_event(event)
        input_box.handle_event(event)
        speed_slider.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in [btn_rand, btn_load, btn_prev, btn_play, btn_next, btn_reset]:
                btn.handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            for btn in [btn_rand, btn_load, btn_prev, btn_play, btn_next, btn_reset]:
                btn.handle_event(event)

    screen.fill(BG_COLOR)

    # Sidebar
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)
    pygame.draw.line(screen, Colors.TEAL, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)

    screen.blit(font_header.render("Insertion Sort", True, Colors.TEAL), (20, 20))
    screen.blit(font_small.render("1. Array Size (2-12):", True, TEXT_COLOR), (20, 55))
    screen.blit(font_small.render("2. Manual Input :", True, TEXT_COLOR), (20, 125))
    screen.blit(font_small.render("3. Controls:", True, TEXT_COLOR), (20, 220))

    for el in ui_elements: el.draw(screen)

    status_surf = font_ui.render(viz.status_msg, True, viz.status_color)
    screen.blit(status_surf, (20, 400))

    pygame.draw.line(screen, (50, 50, 50), (20, 430), (280, 430), 1)
    screen.blit(font_val.render("Statistics", True, TEXT_COLOR), (20, 440))

    c_comps, c_swaps = 0, 0
    if viz.history:
        c_comps, c_swaps = viz.history[viz.step_index]['stats']

    stats_info = [
        f"Comparisons: {c_comps}",
        f"Shifts/Swaps: {c_swaps}",
        f"Step: {viz.step_index + 1} / {len(viz.history)}",
        "Complexity: O(n^2)",
        "Type: In-Place Stable"
    ]
    for i, txt in enumerate(stats_info):
        col = Colors.ORANGE if i < 3 else TEXT_COLOR
        screen.blit(font_ui.render(txt, True, col), (20, 470 + i * 25))

    viz.draw_viz(screen)

    # Legend
    leg_y = 600 - 40 # Bottom right
    leg_x = SIDEBAR_WIDTH + 50

    def draw_legend(x, color, text):
        r = pygame.Rect(x, leg_y, 20, 20)
        pygame.draw.rect(screen, color, r, border_radius=4)
        t = font_small.render(text, True, TEXT_COLOR)
        screen.blit(t, (x + 30, leg_y + 2))
        return x + 120

    lx = draw_legend(leg_x, NODE_SORTED, "Sorted")
    lx = draw_legend(lx, NODE_KEY, "Key (Insert)")
    lx = draw_legend(lx, NODE_COMPARE, "Compare")
    lx = draw_legend(lx, NODE_SHIFT, "Shift")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
