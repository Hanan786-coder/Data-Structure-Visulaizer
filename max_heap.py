import pygame
import sys
import math

# -------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# -------------------------------------------------------------------------

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Max Heap Visualizer")

# 🔷 COLORS (Matching your screenshot)
ORANGE = (255, 108, 12)       # Title & Highlight
GREY_BG = (57, 62, 70)        # Dark Background
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
    def __init__(self, x, y, w, h, text, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.is_hovered = False

    def draw(self, surface):
        color = TEAL_HOVER if self.is_hovered else TEAL
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
            self.color = TEAL_HOVER if self.active else TEAL
            
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
        # Draw background 
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=6)
        
        # Draw Text
        txt_surface = font_ui.render(self.text, True, WHITE)
        surface.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

# -------------------------------------------------------------------------
# DATA STRUCTURE: MAX HEAP (No Priority Dictionary)
# -------------------------------------------------------------------------

class MaxHeap:
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
        
        # 1. Convert to Integer for proper sorting (e.g., 10 > 2)
        # If input is not a number, keep as string
        try:
            val = int(val_str)
        except ValueError:
            val = val_str 

        self.heap.append(val)
        index = len(self.heap) - 1
        
        # 2. Bubble Up (Max Heap: Child > Parent means swap)
        while index > 0 and self.heap[index] > self.heap[self.parent(index)]:
            self.swap(index, self.parent(index))
            index = self.parent(index)
            
        return True, f"Inserted '{val}'."

    def extract_max(self):
        if not self.heap:
            return None, "Heap is Empty!"
        
        max_item = self.heap[0]
        last_item = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last_item
            self.max_heapify(0)
            
        return max_item, f"Extracted Max: '{max_item}'."

    def max_heapify(self, i):
        largest = i
        l = self.left(i)
        r = self.right(i)
        
        # Check Left
        if l < len(self.heap) and self.heap[l] > self.heap[largest]:
            largest = l
        # Check Right
        if r < len(self.heap) and self.heap[r] > self.heap[largest]:
            largest = r
            
        if largest != i:
            self.swap(i, largest)
            self.max_heapify(largest)

    def peek(self):
        if not self.heap:
            return None
        return self.heap[0]

    def clear(self):
        self.heap = []

# -------------------------------------------------------------------------
# MAIN VISUALIZER
# -------------------------------------------------------------------------

class Visualizer:
    def __init__(self):
        self.pq = MaxHeap(capacity=15)
        
        # --- UI LAYOUT ---
        
        # 1. Capacity Controls (Top Left)
        self.input_cap = InputBox(50, 90, 80, 40, text="15", numeric_only=True, max_chars=2)
        btn_set = Button(140, 90, 100, 40, "Set Cap", "SET_CAP")
        
        # 2. Main Inputs (Row 2) - "Prio" Removed, "Value" Expanded
        y_op = 160
        self.input_val = InputBox(50, y_op, 200, 40, max_chars=10)
        
        # Buttons shifted to account for removed Prio box
        self.buttons = [
            btn_set,
            Button(270, y_op, 100, 40, "Insert", "INS"),
            Button(390, y_op, 120, 40, "Extract Max", "EXT"), # Changed text from Min to Max
            Button(530, y_op, 100, 40, "Peek", "PEEK"),
            Button(650, y_op, 100, 40, "Clear", "CLR")
        ]
        
        # State
        self.status_msg = "Max Heap Ready."
        self.msg_color = WHITE
        self.logic_msg = "Waiting for operation..."
        
        # Visuals
        self.peek_highlight = False
        self.peek_timer = 0
        self.node_positions = self.generate_tree_layout()

    def generate_tree_layout(self):
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

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            self.input_val.handle_event(event)
            self.input_cap.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.buttons:
                    if btn.is_clicked(mouse_pos):
                        self.execute_action(btn.action_code)

        for btn in self.buttons:
            btn.check_hover(mouse_pos)

    def set_status(self, msg, color, logic=""):
        self.status_msg = msg
        self.msg_color = color
        self.logic_msg = logic

    def execute_action(self, code):
        self.peek_highlight = False 
        
        # --- SET CAP ---
        if code == "SET_CAP":
            txt = self.input_cap.text
            if not txt: return
            try:
                val = int(txt)
                if val > MAX_CAPACITY:
                    self.set_status(f"Error: Max Limit is {MAX_CAPACITY}", ERROR_COLOR)
                    self.input_cap.text = str(MAX_CAPACITY)
                elif val < 1:
                    self.set_status("Error: Min Capacity 1", ERROR_COLOR)
                else:
                    truncated = self.pq.set_capacity(val)
                    msg = f"Capacity set to {val}." + (" (Truncated)" if truncated else "")
                    self.set_status(msg, SUCCESS_COLOR, "Heap Resized")
            except ValueError:
                self.set_status("Invalid Capacity", ERROR_COLOR)

        # --- INSERT ---
        elif code == "INS":
            val = self.input_val.text
            if val:
                # Direct insertion of value
                success, msg = self.pq.insert(val)
                if success:
                    self.set_status(msg, SUCCESS_COLOR, f"Insert {val} -> Bubble Up")
                    self.input_val.text = ""
                else:
                    self.set_status(msg, ERROR_COLOR, "Heap Full")
            else:
                self.set_status("Enter a Value!", ERROR_COLOR)

        # --- EXTRACT MAX ---
        elif code == "EXT":
            item, msg = self.pq.extract_max()
            if item is not None:
                self.set_status(msg, SUCCESS_COLOR, "Swap Root/Last -> Remove Last -> Heapify")
            else:
                self.set_status(msg, ERROR_COLOR)

        # --- PEEK ---
        elif code == "PEEK":
            item = self.pq.peek()
            if item is not None:
                self.set_status(f"Max Value: {item}", ORANGE, "Root Node")
                self.peek_highlight = True
                self.peek_timer = pygame.time.get_ticks()
            else:
                self.set_status("Heap is Empty", ERROR_COLOR)

        # --- CLEAR ---
        elif code == "CLR":
            self.pq.clear()
            self.set_status("Heap Cleared", WHITE, "Reset")

    def draw_tree_connection(self, i, parent_i):
        if i >= len(self.pq.heap): return
        start = self.node_positions[parent_i]
        end = self.node_positions[i]
        pygame.draw.line(SCREEN, LIGHT_GREY, start, end, 2)

    def draw_node(self, i, val):
        pos = self.node_positions[i]
        
        w, h = 45, 45
        rect = pygame.Rect(0, 0, w, h)
        rect.center = pos
        
        # Color Logic for Peek
        color = TEAL
        if self.peek_highlight and i == 0:
            if pygame.time.get_ticks() - self.peek_timer < 1000:
                color = ORANGE
            else:
                self.peek_highlight = False

        pygame.draw.rect(SCREEN, color, rect, border_radius=6)
        pygame.draw.rect(SCREEN, LIGHT_GREY, rect, 1, border_radius=6)
        
        # Draw Value Only (No Priority)
        txt = str(val)
        txt_surf = font_node.render(txt, True, BLACK)
        txt_rect = txt_surf.get_rect(center=rect.center)
        SCREEN.blit(txt_surf, txt_rect)

    def draw(self):
        SCREEN.fill(GREY_BG)
        
        # 1. Header
        title_surf = font_title.render("MAX HEAP", True, ORANGE)
        SCREEN.blit(title_surf, (50, 30))
        
        # 2. Controls Area
        # Row 1: Capacity
        lbl_cap = font_ui.render(f"Capacity (Max {MAX_CAPACITY}):", True, LIGHT_GREY)
        SCREEN.blit(lbl_cap, (50, 65))
        self.input_cap.draw(SCREEN)
        
        # Row 2: Value Input Only (Priority removed)
        lbl_val = font_ui.render("Value:", True, LIGHT_GREY)
        SCREEN.blit(lbl_val, (50, 135))
        self.input_val.draw(SCREEN)
        
        # Buttons
        for btn in self.buttons:
            btn.draw(SCREEN)
            
        # 3. Status Messages (Right Side)
        s_surf = font_ui.render(self.status_msg, True, self.msg_color)
        SCREEN.blit(s_surf, (550, 40))
        
        l_lbl = font_ui.render("Logic Flow:", True, LIGHT_GREY)
        SCREEN.blit(l_lbl, (550, 70))
        l_surf = font_msg.render(f"> {self.logic_msg}", True, TEAL_HOVER)
        SCREEN.blit(l_surf, (550, 95))

        # 4. Visualization Area Divider
        pygame.draw.line(SCREEN, TEAL, (0, 240), (SCREEN_WIDTH, 240), 2)
        
        # Draw Connectors first
        for i in range(1, len(self.pq.heap)):
            self.draw_tree_connection(i, self.pq.parent(i))
            
        # Draw Nodes
        for i in range(len(self.pq.heap)):
            self.draw_node(i, self.pq.heap[i])

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_input()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    app = Visualizer()
    app.run()