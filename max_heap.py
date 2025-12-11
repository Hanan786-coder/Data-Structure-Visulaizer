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
pygame.display.set_caption("Priority Queue Visualizer (Max Cap 20)")

# 🔷 COLORS (EXACT MATCH)
ORANGE = (255, 108, 12)       # Highlight
GREY = (57, 62, 70)           # Background
TEAL = (0, 173, 181)          # Nodes and Buttons
TEAL_BRIGHT = (0, 200, 210)   # Button Hover
BLACK = (43, 40, 49)
LIGHT_GREY = (238, 238, 238)
WHITE = (255, 255, 255)
ERROR_COLOR = (255, 87, 87)
SUCCESS_COLOR = (0, 200, 81)

# MAX LIMIT
MAX_CAPACITY = 20

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
# Smaller font for nodes to fit 20 items
font_node_small = get_font(12) 

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
        color = TEAL_BRIGHT if self.is_hovered else TEAL
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        txt_surf = font_ui.render(self.text, True, LIGHT_GREY)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, x, y, w, h, text='', numeric_only=False, max_chars=8):
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
            self.color = TEAL_BRIGHT if self.active else TEAL
            
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
# DATA STRUCTURE LOGIC: MAX-HEAP
# -------------------------------------------------------------------------

class MaxHeap:
    def __init__(self, capacity=6):
        self.heap = []
        self.capacity = capacity

    def set_capacity(self, new_cap):
        self.capacity = new_cap
        # Truncate if current size > new capacity
        if len(self.heap) > new_cap:
            self.heap = self.heap[:new_cap]
            return True # Indicates truncation occurred
        return False

    def parent(self, i): return (i - 1) // 2
    def left(self, i): return 2 * i + 1
    def right(self, i): return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, value, priority):
        if len(self.heap) >= self.capacity:
            return False, f"Queue Overflow! Max capacity ({self.capacity}) reached."
        
        self.heap.append({'val': value, 'prio': priority})
        index = len(self.heap) - 1
        
        # Bubble Up (MAX HEAP LOGIC: Parent must be larger than Child)
        # If Parent < Child, we swap
        while index > 0 and self.heap[self.parent(index)]['prio'] < self.heap[index]['prio']:
            self.swap(index, self.parent(index))
            index = self.parent(index)
            
        return True, f"Inserted '{value}' (Prio {priority})."

    def extract_max(self):
        if not self.heap:
            return None, "Queue Underflow! Queue is empty."
        
        max_item = self.heap[0]
        last_item = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last_item
            self.max_heapify(0)
            
        return max_item, f"Extracted Max: '{max_item['val']}' (Prio {max_item['prio']})."

    def max_heapify(self, i):
        largest = i
        l = self.left(i)
        r = self.right(i)
        
        # MAX HEAP LOGIC: Check if Child > Current Largest
        if l < len(self.heap) and self.heap[l]['prio'] > self.heap[largest]['prio']:
            largest = l
        if r < len(self.heap) and self.heap[r]['prio'] > self.heap[largest]['prio']:
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
# MAIN VISUALIZER CLASS
# -------------------------------------------------------------------------

class Visualizer:
    def __init__(self):
        self.pq = MaxHeap(capacity=6)
        
        # --- UI LAYOUT ---
        # 1. Capacity Row (Top)
        self.input_cap = InputBox(50, 90, 80, 40, text="6", numeric_only=True, max_chars=2)
        btn_set = Button(140, 90, 100, 40, "Set Cap", "SET_CAP")
        
        # 2. Operations Row (Below Capacity)
        y_op = 160
        # Reduced max_chars to 4 so it fits inside small tree nodes
        self.input_val = InputBox(50, y_op, 140, 40, max_chars=4) 
        self.input_prio = InputBox(210, y_op, 80, 40, numeric_only=True, max_chars=3)
        
        self.buttons = [
            btn_set,
            Button(300, y_op, 100, 40, "Insert", "INS"),
            Button(420, y_op, 120, 40, "Extract Max", "EXT"), # Renamed Button
            Button(560, y_op, 100, 40, "Peek", "PEEK"),
            Button(680, y_op, 100, 40, "Clear", "CLR")
        ]
        
        # State Messages
        self.status_msg = "Welcome. Default Capacity: 6"
        self.msg_color = WHITE
        self.logic_msg = "Waiting for operation..."
        
        # Visuals
        self.peek_highlight = False
        self.peek_timer = 0
        
        # Generate Node Positions dynamically for 20 nodes
        self.node_positions = self.generate_tree_layout()

    def generate_tree_layout(self):
        """
        Calculates geometric positions for a binary tree up to 20 nodes (Levels 0-4).
        """
        positions = {}
        start_y = 280
        level_height = 80 # Vertical space between levels
        
        for i in range(MAX_CAPACITY):
            # 1. Determine Level (Depth)
            level = int(math.log2(i + 1))
            
            # 2. Determine index position within that level
            level_start_index = (1 << level) - 1
            pos_in_level = i - level_start_index
            
            # 3. Calculate max nodes in this level (for spacing)
            nodes_in_level = 1 << level
            
            # 4. Calculate X
            # Divide screen width into equal sections
            section_width = SCREEN_WIDTH / (nodes_in_level + 1)
            x = section_width * (pos_in_level + 1)
            
            # 5. Calculate Y
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
            self.input_prio.handle_event(event)
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
        
        # --- SET CAPACITY ---
        if code == "SET_CAP":
            txt = self.input_cap.text
            if not txt: return
            try:
                val = int(txt)
                if val > MAX_CAPACITY:
                    self.set_status(f"Error: Max Capacity is {MAX_CAPACITY}!", ERROR_COLOR, f"Constraint: Max {MAX_CAPACITY}")
                    self.input_cap.text = str(MAX_CAPACITY)
                elif val < 1:
                    self.set_status("Error: Min Capacity is 1!", ERROR_COLOR)
                else:
                    truncated = self.pq.set_capacity(val)
                    if truncated:
                        self.set_status(f"Capacity set to {val}. Truncated.", ERROR_COLOR, "Rear elements removed")
                    else:
                        self.set_status(f"Capacity set to {val}.", SUCCESS_COLOR, "New Max Capacity applied")
            except ValueError:
                self.set_status("Invalid Capacity Number", ERROR_COLOR)

        # --- INSERT ---
        elif code == "INS":
            val = self.input_val.text
            prio = self.input_prio.text
            if val and prio:
                success, msg = self.pq.insert(val, int(prio))
                if success:
                    self.set_status(msg, SUCCESS_COLOR, "Inserted at leaf -> Bubbled Up")
                    self.input_val.text = ""
                    self.input_prio.text = ""
                else:
                    self.set_status(msg, ERROR_COLOR, "Heap is Full")
            else:
                self.set_status("Enter Value and Priority!", ERROR_COLOR)

        # --- EXTRACT ---
        elif code == "EXT":
            item, msg = self.pq.extract_max()
            if item:
                self.set_status(msg, SUCCESS_COLOR, "Root removed -> Last Node to Root -> Bubble Down")
            else:
                self.set_status(msg, ERROR_COLOR)

        # --- PEEK ---
        elif code == "PEEK":
            item = self.pq.peek()
            if item:
                self.set_status(f"Front: {item['val']} ({item['prio']})", ORANGE, "Returning root node")
                self.peek_highlight = True
                self.peek_timer = pygame.time.get_ticks()
            else:
                self.set_status("Queue is Empty", ERROR_COLOR)

        # --- CLEAR ---
        elif code == "CLR":
            self.pq.clear()
            self.set_status("Queue Cleared", WHITE, "All items removed")

    def draw_tree_connection(self, i, parent_i):
        if i >= len(self.pq.heap): return
        start = self.node_positions[parent_i]
        end = self.node_positions[i]
        # Thinner line for dense tree
        pygame.draw.line(SCREEN, LIGHT_GREY, start, end, 2)

    def draw_node(self, i, data):
        pos = self.node_positions[i]
        
        # SMALLER SIZE for 20 nodes support
        w, h = 48, 30
        rect = pygame.Rect(0, 0, w, h)
        rect.center = pos
        
        # Color Logic
        color = TEAL
        if self.peek_highlight and i == 0:
            if pygame.time.get_ticks() - self.peek_timer < 1000:
                color = ORANGE
            else:
                self.peek_highlight = False

        pygame.draw.rect(SCREEN, color, rect, border_radius=6)
        pygame.draw.rect(SCREEN, LIGHT_GREY, rect, 1, border_radius=6)
        
        # Compact Text: "Val(P)"
        txt = f"{data['val']}({data['prio']})"
        txt_surf = font_node_small.render(txt, True, BLACK)
        txt_rect = txt_surf.get_rect(center=rect.center)
        SCREEN.blit(txt_surf, txt_rect)

    def draw(self):
        SCREEN.fill(GREY)
        
        # 1. Header
        title_surf = font_title.render("PRIORITY QUEUE (MAX-HEAP)", True, ORANGE)
        SCREEN.blit(title_surf, (50, 30))
        
        # 2. Controls Area
        # Row 1: Capacity
        lbl_cap = font_ui.render(f"Capacity (Max {MAX_CAPACITY}):", True, LIGHT_GREY)
        SCREEN.blit(lbl_cap, (50, 65))
        self.input_cap.draw(SCREEN)
        
        # Row 2: Inputs
        lbl_val = font_ui.render("Value:", True, LIGHT_GREY)
        lbl_prio = font_ui.render("Prio:", True, LIGHT_GREY)
        SCREEN.blit(lbl_val, (50, 135))
        SCREEN.blit(lbl_prio, (210, 135))
        
        self.input_val.draw(SCREEN)
        self.input_prio.draw(SCREEN)
        
        for btn in self.buttons:
            btn.draw(SCREEN)
            
        # 3. Status Messages 
        s_surf = font_ui.render(self.status_msg, True, self.msg_color)
        SCREEN.blit(s_surf, (550, 40))
        
        l_lbl = font_ui.render("Logic Flow:", True, LIGHT_GREY)
        SCREEN.blit(l_lbl, (550, 70))
        l_surf = font_msg.render(f"> {self.logic_msg}", True, TEAL_BRIGHT)
        SCREEN.blit(l_surf, (550, 95))

        # 4. Visualization Area
        pygame.draw.line(SCREEN, TEAL, (0, 240), (SCREEN_WIDTH, 240), 2)
        
        # Draw Lines first
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

# -------------------------------------------------------------------------
# EXECUTION
# -------------------------------------------------------------------------
if __name__ == "__main__":
    app = Visualizer()
    app.run()