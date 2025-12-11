import pygame
import sys
import random
import Colors  # Your custom colors file

# --- Configuration ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700 
SIDEBAR_WIDTH = 300

# Colors
BG_COLOR = Colors.GREY
SIDEBAR_COLOR = (30, 30, 35)

# Node Colors
NODE_DEFAULT = Colors.TEAL
NODE_SPLIT = (70, 130, 180)    # Steel Blue (Just split)
NODE_COMPARE = (255, 215, 0)   # Gold
NODE_MERGING = (155, 89, 182)  # Purple (Moving up)
NODE_SORTED = (46, 204, 113)   # Green

TEXT_COLOR = Colors.LIGHT_GREY
BUTTON_COLOR = Colors.TEAL
BUTTON_HOVER = Colors.TEAL_BRIGHT
INPUT_BG = (50, 50, 55)
ERROR_COLOR = (255, 87, 87)

# Dimensions
NODE_W = 50
NODE_H = 40
GAP = 20
START_Y = 100  
LEVEL_HEIGHT = 100  # Vertical distance between recursion levels

# --- Fonts ---
def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('Arial', size, bold=bold)


font_header = get_font(28, bold=True)
font_ui = get_font(16)
font_val = get_font(18, bold=True)
font_small = get_font(14)
font_logic = get_font(20)


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
                return self.func() # Return result
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

class MergeSortTreeVisualizer:
    def __init__(self):
        self.initial_array = []
        self.history = []
        self.step_index = 0
        self.playing = False
        self.last_update = 0
        self.finished = False
        self.status_msg = "Welcome"
        self.status_color = TEXT_COLOR
        self.sort_mode = "asc"

        # State tracking for generation
        self.active_chunks = []
        self.comps_count = 0
        self.merges_count = 0

    def set_msg(self, msg, color=TEXT_COLOR):
        self.status_msg = msg
        self.status_color = color

    def generate_random(self, size):
        if not (2 <= size <= 8):
            self.set_msg("Size must be 2-8!", ERROR_COLOR)
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
            if 2 <= len(new_arr) <= 8:
                self.initial_array = new_arr
                self.set_msg("Manual Input Loaded", Colors.TEAL)
                self.precompute_history()
            else:
                self.set_msg("Error: Input count must be 2-8", ERROR_COLOR)
        except ValueError:
            self.set_msg("Error: Numbers only", ERROR_COLOR)

    def toggle_sort_mode(self):
        self.sort_mode = "desc" if self.sort_mode == "asc" else "asc"
        if self.initial_array:
            self.precompute_history()

    def save_state(self, desc):
        # Deep copy the chunks to save history
        snapshot_chunks = []
        for chunk in self.active_chunks:
            snapshot_chunks.append({
                'values': chunk['values'][:],
                'colors': chunk['colors'][:],
                'depth': chunk['depth'],
                'abs_index': chunk['abs_index']
            })

        self.history.append({
            'chunks': snapshot_chunks,
            'stats': (self.comps_count, self.merges_count),
            'desc': desc
        })

    def precompute_history(self):
        self.history = []
        self.comps_count = 0
        self.merges_count = 0

        # Initial State: One chunk at depth 0
        self.active_chunks = [{
            'values': self.initial_array[:],
            'colors': [NODE_DEFAULT] * len(self.initial_array),
            'depth': 0,
            'abs_index': 0 
        }]

        mode_label = "Descending" if self.sort_mode == "desc" else "Ascending"
        self.save_state(f"Start (Sort: {mode_label})")

        # Recursion
        self.split_merge_recursive(self.initial_array, 0, 0)

        # Final Sorted
        if self.active_chunks:
            self.active_chunks[0]['colors'] = [NODE_SORTED] * len(self.active_chunks[0]['values'])
        self.save_state("Sorting Complete")

        self.reset()

    def remove_chunk(self, depth, abs_index):
        # Helper to remove a specific chunk from active list
        for i, c in enumerate(self.active_chunks):
            if c['depth'] == depth and c['abs_index'] == abs_index:
                self.active_chunks.pop(i)
                return

    def split_merge_recursive(self, arr, depth, abs_idx):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left_part = arr[:mid]
        right_part = arr[mid:]

        # --- SPLIT ANIMATION ---

        # 1. Identify Parent Chunk to remove
        self.remove_chunk(depth, abs_idx)

        # 2. Add two Children Chunks at depth + 1
        # Left Child
        self.active_chunks.append({
            'values': left_part[:],
            'colors': [NODE_SPLIT] * len(left_part),
            'depth': depth + 1,
            'abs_index': abs_idx
        })
        # Right Child
        self.active_chunks.append({
            'values': right_part[:],
            'colors': [NODE_SPLIT] * len(right_part),
            'depth': depth + 1,
            'abs_index': abs_idx + mid
        })

        self.save_state(f"Split [{arr[0]}...{arr[-1]}] into two levels")

        # Color reset after split highlight
        for c in self.active_chunks:
            if c['depth'] == depth + 1 and c['abs_index'] in [abs_idx, abs_idx + mid]:
                c['colors'] = [NODE_DEFAULT] * len(c['values'])

        # Recurse
        sorted_left = self.split_merge_recursive(left_part, depth + 1, abs_idx)
        sorted_right = self.split_merge_recursive(right_part, depth + 1, abs_idx + mid)

        # --- MERGE LOGIC ---
        merged = []
        i = j = 0

        while i < len(sorted_left) and j < len(sorted_right):
            self.comps_count += 1

            # Highlight Comparison in the children chunks
            left_chunk = next(c for c in self.active_chunks if c['depth'] == depth + 1 and c['abs_index'] == abs_idx)
            right_chunk = next(
                c for c in self.active_chunks if c['depth'] == depth + 1 and c['abs_index'] == abs_idx + mid)

            left_chunk['colors'][i] = NODE_COMPARE
            right_chunk['colors'][j] = NODE_COMPARE
            self.save_state(f"Comparing {sorted_left[i]} vs {sorted_right[j]}")

            is_desc = self.sort_mode == "desc"
            condition = sorted_left[i] > sorted_right[j] if is_desc else sorted_left[i] < sorted_right[j]
            
            if condition:
                merged.append(sorted_left[i])
                left_chunk['colors'][i] = NODE_MERGING
                i += 1
            else:
                merged.append(sorted_right[j])
                right_chunk['colors'][j] = NODE_MERGING
                j += 1

            move_direction = "larger" if is_desc else "smaller"
            self.save_state(f"Moving {move_direction} element up")

            # Reset colors
            if i < len(left_chunk['colors']): left_chunk['colors'][i] = NODE_DEFAULT
            if j < len(right_chunk['colors']): right_chunk['colors'][j] = NODE_DEFAULT

        # Remaining
        while i < len(sorted_left):
            merged.append(sorted_left[i])
            i += 1
        while j < len(sorted_right):
            merged.append(sorted_right[j])
            j += 1

        # --- MERGE ANIMATION (Move Up) ---
        self.merges_count += 1

        # Remove the two children
        self.remove_chunk(depth + 1, abs_idx)
        self.remove_chunk(depth + 1, abs_idx + mid)

        # Add parent back (Sorted)
        self.active_chunks.append({
            'values': merged[:],
            'colors': [NODE_SORTED] * len(merged),
            'depth': depth,
            'abs_index': abs_idx
        })
        self.save_state(f"Merged & Sorted range depth {depth}")

        # Fade back to teal
        self.active_chunks[-1]['colors'] = [NODE_DEFAULT] * len(merged)

        return merged

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
        chunks = state['chunks']

        # Determine Global Centering based on initial Array Size
        total_slots = len(self.initial_array)
        full_width = total_slots * (NODE_W + GAP) - GAP
        viz_start_x = SIDEBAR_WIDTH + (SCREEN_WIDTH - SIDEBAR_WIDTH - full_width) // 2

        # --- Logic Flow Text ---
        label_x = SIDEBAR_WIDTH + 40
        label_y = 30
        surface.blit(font_ui.render("Logic Flow:", True, (150, 150, 150)), (label_x, label_y))
        desc_surf = font_logic.render(f"> {state['desc']}", True, Colors.TEAL_BRIGHT)
        surface.blit(desc_surf, (label_x, label_y + 25))

        # --- Draw Chunks ---
        for chunk in chunks:
            depth = chunk['depth']
            abs_idx = chunk['abs_index']
            vals = chunk['values']
            colors = chunk['colors']

            # Calculate Y based on Depth
            y_pos = START_Y + (depth * LEVEL_HEIGHT)

            # Calculate X based on Absolute Index
            x_start = viz_start_x + abs_idx * (NODE_W + GAP)

            for i, val in enumerate(vals):
                cx = x_start + i * (NODE_W + GAP)
                rect = pygame.Rect(cx, y_pos, NODE_W, NODE_H)

                pygame.draw.rect(surface, colors[i], rect, border_radius=6)
                pygame.draw.rect(surface, (20, 20, 20), rect, 2, border_radius=6)

                txt = font_val.render(str(val), True, (255, 255, 255))
                surface.blit(txt, txt.get_rect(center=rect.center))

                # Draw lines connecting to parent (Visual Tree lines)
                if depth > 0:
                    parent_y = y_pos - LEVEL_HEIGHT + NODE_H
                    # Just a simple line up
                    pygame.draw.line(surface, (60, 60, 60), (rect.centerx, y_pos), (rect.centerx, parent_y), 1)


# --- Main Run Function ---
def run(screen):
    clock = pygame.time.Clock()
    viz = MergeSortTreeVisualizer()

    # --- Actions ---
    def btn_rand_action():
        try:
            s = int(size_input.text)
            viz.generate_random(s)
        except ValueError:
            viz.set_msg("Size must be number", ERROR_COLOR)

    def btn_load_action(): viz.load_manual(input_box.text)
    def btn_sort_mode_action(): viz.toggle_sort_mode()
    def btn_prev_action(): viz.prev_step(); viz.playing = False
    def btn_play_action(): viz.toggle_play()
    def btn_next_action(): viz.next_step(); viz.playing = False
    def btn_reset_action(): viz.reset()
    def go_back(): return "back"

    # Layout
    size_input = InputBox(20, 75, 50, 35, text="6", numeric_only=True, max_chars=1)
    btn_rand = Button(80, 75, 200, 35, "Randomize (Size 2-8)", btn_rand_action)
    input_box = InputBox(20, 128, 190, 35, text="")
    btn_load = Button(220, 128, 60, 35, "Load", btn_load_action)
    btn_sort_mode = Button(20, 185, 260, 35, "Sort: Ascending ↑", btn_sort_mode_action)
    
    btn_prev = Button(20, 240, 80, 40, "Prev", btn_prev_action)
    btn_play = Button(110, 240, 80, 40, "Play/||", btn_play_action)
    btn_next = Button(200, 240, 80, 40, "Next", btn_next_action)
    btn_reset = Button(20, 290, 260, 35, "Reset", btn_reset_action, color=Colors.ORANGE)
    
    btn_back = Button(900, 15, 80, 40, "← Back", go_back, color=Colors.ORANGE)
    
    speed_slider = Slider(20, 360, 260, 50, 1000, 500)

    # Group UI Elements for Loop
    ui_elements = [size_input, btn_rand, input_box, btn_load, btn_sort_mode, 
                   btn_prev, btn_play, btn_next, btn_reset, btn_back, speed_slider]

    viz.generate_random(6)

    # --- Main Loop ---
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

        # Sidebar
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)
        pygame.draw.line(screen, Colors.TEAL, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)

        screen.blit(font_header.render("Merge Sort", True, Colors.TEAL), (20, 20))
        screen.blit(font_small.render("1. Array Size (2-8):", True, TEXT_COLOR), (20, 55))
        screen.blit(font_small.render("2. Manual Input :", True, TEXT_COLOR), (20, 108))
        screen.blit(font_small.render("3. Sort Order:", True, TEXT_COLOR), (20, 165))
        screen.blit(font_small.render("4. Controls:", True, TEXT_COLOR), (20, 220))

        btn_sort_mode.text = "Mode: Desc" if viz.sort_mode == "desc" else "Mode: Asc"

        for el in ui_elements: el.draw(screen)

        status_surf = font_ui.render(viz.status_msg, True, viz.status_color)
        screen.blit(status_surf, (20, 400))

        pygame.draw.line(screen, (50, 50, 50), (20, 430), (280, 430), 1)
        screen.blit(font_val.render("Statistics", True, TEXT_COLOR), (20, 440))

        c_comps, c_merges = 0, 0
        if viz.history:
            c_comps, c_merges = viz.history[viz.step_index]['stats']

        stats_info = [
            f"Comparisons: {c_comps}",
            f"Merges: {c_merges}",
            f"Step: {viz.step_index + 1} / {len(viz.history)}",
            "Complexity: O(n log n)",
            "Structure: Recursive Tree"
        ]
        for i, txt in enumerate(stats_info):
            col = Colors.ORANGE if i < 3 else TEXT_COLOR
            screen.blit(font_ui.render(txt, True, col), (20, 470 + i * 25))

        viz.draw_viz(screen)

        # Legend
        leg_y = SCREEN_HEIGHT - 40
        leg_x = SIDEBAR_WIDTH + 50

        def draw_legend(x, color, text):
            r = pygame.Rect(x, leg_y, 20, 20)
            pygame.draw.rect(screen, color, r, border_radius=4)
            t = font_small.render(text, True, TEXT_COLOR)
            screen.blit(t, (x + 30, leg_y + 2))
            return x + 110

        lx = draw_legend(leg_x, NODE_SPLIT, "Split")
        lx = draw_legend(lx, NODE_COMPARE, "Compare")
        lx = draw_legend(lx, NODE_SORTED, "Sorted")
        lx = draw_legend(lx, NODE_MERGING, "Merging")

        pygame.display.flip()
        clock.tick(60)

    return "back"