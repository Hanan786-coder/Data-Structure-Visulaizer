import pygame
import sys
import math
import Colors

# -------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# -------------------------------------------------------------------------

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# 🔷 COLORS
ORANGE = (255, 108, 12)       # Title & Highlight
GREY_BG = Colors.GREY         # Dark Background
TEAL = (0, 173, 181)          # Buttons & Nodes
TEAL_HOVER = (0, 200, 210)    # Button Hover
BLACK = (43, 40, 49)          # Input Box BG
WHITE = (255, 255, 255)       # Text
LIGHT_GREY = (238, 238, 238)  # Labels
ERROR_COLOR = (255, 87, 87)
SUCCESS_COLOR = (0, 200, 81)

# MAX CAPACITY (Tree levels limit)
MAX_CAPACITY = 31

# -------------------------------------------------------------------------
# FONTS
# -------------------------------------------------------------------------
def get_font(size):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont("Arial", size, bold=True)

font_title = get_font(35)
font_ui = get_font(18)
font_msg = get_font(16)
font_node = get_font(14)

# -------------------------------------------------------------------------
# UI CLASSES
# -------------------------------------------------------------------------

class Button:
    def __init__(self, x, y, w, h, text, action_code, color=TEAL):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.base_color = color
        self.hover_color = TEAL_HOVER if color == TEAL else ORANGE
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        txt_surf = font_ui.render(self.text, True, LIGHT_GREY)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, x, y, w, h, text='', numeric_only=False, max_chars=12):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = TEAL
        self.text = text
        self.active = False
        self.numeric_only = numeric_only 
        self.max_chars = max_chars

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = WHITE if self.active else TEAL
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = TEAL
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.numeric_only:
                        if event.unicode.isdigit():
                             if len(self.text) < self.max_chars:
                                self.text += event.unicode
                    else:
                        if len(self.text) < self.max_chars:
                            self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=6)
        txt_surface = font_ui.render(self.text, True, WHITE)
        surface.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

# -------------------------------------------------------------------------
# DATA STRUCTURE: MIN HEAP
# -------------------------------------------------------------------------

class MinHeap:
    def __init__(self, capacity=15):
        self.heap = []
        self.capacity = capacity

    def set_capacity(self, new_cap):
        self.capacity = new_cap
        if len(self.heap) > new_cap:
            self.heap = self.heap[:new_cap]
            return True 
        return False

    def parent(self, i): return (i - 1) // 2
    def left(self, i): return 2 * i + 1
    def right(self, i): return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, val_str):
        if len(self.heap) >= self.capacity:
            return False, f"Heap Full! Max capacity ({self.capacity}) reached."
        
        try:
            val = int(val_str)
        except ValueError:
            return False, "Please enter a valid integer."

        self.heap.append(val)
        index = len(self.heap) - 1
        
        # MIN HEAP LOGIC: Bubble Up if Child < Parent
        while index > 0 and self.heap[index] < self.heap[self.parent(index)]:
            self.swap(index, self.parent(index))
            index = self.parent(index)
            
        return True, f"Inserted '{val}'."

    def extract_min(self):
        if not self.heap:
            return None, "Heap is Empty!"
        
        min_item = self.heap[0]
        last_item = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last_item
            self.min_heapify(0)
            
        return min_item, f"Extracted Min: '{min_item}'."

    def min_heapify(self, i):
        smallest = i
        l = self.left(i)
        r = self.right(i)
        
        # Find smallest among Root, Left, Right
        if l < len(self.heap) and self.heap[l] < self.heap[smallest]:
            smallest = l
            
        if r < len(self.heap) and self.heap[r] < self.heap[smallest]:
            smallest = r
            
        if smallest != i:
            self.swap(i, smallest)
            self.min_heapify(smallest)

    def peek(self):
        if not self.heap:
            return None
        return self.heap[0]

    def clear(self):
        self.heap = []

# -------------------------------------------------------------------------
# MAIN VISUALIZER RUN FUNCTION
# -------------------------------------------------------------------------

def run(SCREEN):
    clock = pygame.time.Clock()
    pq = MinHeap(capacity=15)
    
    # State Dictionary
    state = {
        "status_msg": "Min Heap Ready.",
        "msg_color": WHITE,
        "logic_msg": "Waiting for operation...",
        "peek_highlight": False,
        "peek_timer": 0
    }
    
    # --- UI LAYOUT ---
    
    # 1. Capacity Controls
    input_cap = InputBox(50, 90, 80, 40, text="15", numeric_only=True, max_chars=2)
    btn_set = Button(140, 90, 100, 40, "Set Cap", "SET_CAP")
    
    # 2. Main Inputs
    y_op = 160
    input_val = InputBox(50, y_op, 200, 40, max_chars=10, numeric_only=True)
    
    # Buttons
    buttons = [
        btn_set,
        Button(270, y_op, 100, 40, "Insert", "INS"),
        Button(390, y_op, 120, 40, "Extract Min", "EXT"), 
        Button(530, y_op, 100, 40, "Peek", "PEEK"),
        Button(650, y_op, 100, 40, "Clear", "CLR"),
        Button(900, 15, 80, 40, "← Back", "BACK", color=ORANGE)
    ]
    
    input_boxes = [input_cap, input_val]

    def set_status(msg, color, logic=""):
        state["status_msg"] = msg
        state["msg_color"] = color
        state["logic_msg"] = logic

    def generate_tree_layout():
        """ Calculate node coordinates for a perfect binary tree """
        positions = {}
        start_y = 280
        level_height = 80 
        
        for i in range(MAX_CAPACITY):
            level = int(math.log2(i + 1))
            level_start_index = (1 << level) - 1
            pos_in_level = i - level_start_index
            nodes_in_level = 1 << level
            
            section_width = SCREEN_WIDTH / (nodes_in_level + 1)
            x = section_width * (pos_in_level + 1)
            y = start_y + (level * level_height)
            
            positions[i] = (x, y)
        return positions
    
    node_positions = generate_tree_layout()

    # --- ACTION HANDLER ---
    def execute_action(code):
        state["peek_highlight"] = False 
        
        if code == "BACK":
            return "back"

        if code == "SET_CAP":
            txt = input_cap.text
            if not txt: return
            try:
                val = int(txt)
                if val > MAX_CAPACITY:
                    set_status(f"Error: Max Limit is {MAX_CAPACITY}", ERROR_COLOR)
                    input_cap.text = str(MAX_CAPACITY)
                elif val < 1:
                    set_status("Error: Min Capacity 1", ERROR_COLOR)
                else:
                    truncated = pq.set_capacity(val)
                    msg = f"Capacity set to {val}." + (" (Truncated)" if truncated else "")
                    set_status(msg, SUCCESS_COLOR, "Heap Resized")
            except ValueError:
                set_status("Invalid Capacity", ERROR_COLOR)

        elif code == "INS":
            val = input_val.text
            if val:
                success, msg = pq.insert(val)
                if success:
                    set_status(msg, SUCCESS_COLOR, f"Insert {val} -> Bubble Up (if < Parent)")
                    input_val.text = ""
                else:
                    set_status(msg, ERROR_COLOR)
            else:
                set_status("Enter a Value!", ERROR_COLOR)

        elif code == "EXT":
            item, msg = pq.extract_min()
            if item is not None:
                set_status(msg, SUCCESS_COLOR, "Swap Root/Last -> Remove -> Heapify Down")
            else:
                set_status(msg, ERROR_COLOR)

        elif code == "PEEK":
            item = pq.peek()
            if item is not None:
                set_status(f"Min Value: {item}", ORANGE, "Root Node (Index 0)")
                state["peek_highlight"] = True
                state["peek_timer"] = pygame.time.get_ticks()
            else:
                set_status("Heap is Empty", ERROR_COLOR)

        elif code == "CLR":
            pq.clear()
            set_status("Heap Cleared", WHITE, "Reset")
        
        return None

    # --- DRAWING FUNCTIONS ---
    def draw_tree_connection(i, parent_i):
        if i >= len(pq.heap): return
        start = node_positions[parent_i]
        end = node_positions[i]
        pygame.draw.line(SCREEN, LIGHT_GREY, start, end, 2)

    def draw_node(i, val):
        pos = node_positions[i]
        w, h = 45, 45
        rect = pygame.Rect(0, 0, w, h)
        rect.center = pos
        
        # Color Logic for Peek
        color = TEAL
        if state["peek_highlight"] and i == 0:
            if pygame.time.get_ticks() - state["peek_timer"] < 1000:
                color = ORANGE
            else:
                state["peek_highlight"] = False

        pygame.draw.rect(SCREEN, color, rect, border_radius=6)
        pygame.draw.rect(SCREEN, LIGHT_GREY, rect, 1, border_radius=6)
        
        txt = str(val)
        txt_surf = font_node.render(txt, True, BLACK)
        txt_rect = txt_surf.get_rect(center=rect.center)
        SCREEN.blit(txt_surf, txt_rect)

    def draw():
        SCREEN.fill(GREY_BG)
        
        # Header
        title_surf = font_title.render("MIN HEAP", True, ORANGE)
        SCREEN.blit(title_surf, (50, 30))
        
        # Controls
        lbl_cap = font_ui.render(f"Capacity (Max {MAX_CAPACITY}):", True, LIGHT_GREY)
        SCREEN.blit(lbl_cap, (50, 65))
        input_cap.draw(SCREEN)
        
        lbl_val = font_ui.render("Value (Int):", True, LIGHT_GREY)
        SCREEN.blit(lbl_val, (50, 135))
        input_val.draw(SCREEN)
        
        for btn in buttons:
            btn.draw(SCREEN)
            
        # Status Messages
        s_surf = font_ui.render(state["status_msg"], True, state["msg_color"])
        SCREEN.blit(s_surf, (550, 40))
        
        l_lbl = font_ui.render("Logic Flow:", True, LIGHT_GREY)
        SCREEN.blit(l_lbl, (550, 70))
        l_surf = font_msg.render(f"> {state['logic_msg']}", True, TEAL_HOVER)
        SCREEN.blit(l_surf, (550, 95))

        # Divider
        pygame.draw.line(SCREEN, TEAL, (0, 240), (SCREEN_WIDTH, 240), 2)
        
        # Draw Connectors
        for i in range(1, len(pq.heap)):
            draw_tree_connection(i, pq.parent(i))
            
        # Draw Nodes
        for i in range(len(pq.heap)):
            draw_node(i, pq.heap[i])

        pygame.display.flip()

    # --- MAIN LOOP ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            for box in input_boxes:
                box.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        result = execute_action(btn.action_code)
                        if result == "back":
                            return "back"

        for btn in buttons:
            btn.check_hover(mouse_pos)

        draw()
        clock.tick(60)

    return "back"