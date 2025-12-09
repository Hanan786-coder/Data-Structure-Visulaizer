import pygame
from button_template import Button
import Colors

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Doubly Linked List Visualization")
screen.fill(color=Colors.GREY)

# --- FONTS ---
def get_font(size):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont('Arial', size)

titleFont = get_font(35)
paraFont = get_font(17)
subFont = get_font(13)
nodeFont = get_font(28)
logicFont = get_font(15)
statFont = get_font(19)

# --- GLOBAL VARIABLES ---
status_msg = "Ready"
logic_msg = "Waiting for operation..."
status_color = Colors.LIGHT_GREY

def set_status(message, color, logic_message=""):
    global status_msg, status_color, logic_msg
    status_msg = message
    status_color = color
    logic_msg = logic_message

def update_status_ui():
    pygame.draw.rect(screen, Colors.GREY, (430, 50, 450, 100))
    
    logic_lbl = statFont.render("Logic Flow: ", True, Colors.LIGHT_GREY)
    screen.blit(logic_lbl, (450, 90))
    logic_txt = logicFont.render(f"{logic_msg}", True, Colors.TEAL_BRIGHT)
    screen.blit(logic_txt, (450, 115))
    
    status_surf = nodeFont.render(status_msg, True, status_color)
    screen.blit(status_surf, (450, 50))

# --- INPUT BAR CLASS ---
class InputBar:
    def __init__(self, x, y, width, height, bg_color, max_chars=1):
        self.shape = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.inactive_color = Colors.LIGHT_GREY
        self.active_color = Colors.TEAL
        self.color = self.inactive_color
        self.active = False
        self.text = ""
        self.max_chars = max_chars
        self.input_font = get_font(19)
        self.text_rendered = self.input_font.render(self.text, True, Colors.LIGHT_GREY)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.shape.collidepoint(event.pos)
            self.color = self.active_color if self.active else self.inactive_color

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(self.text) > 0:
                self.text = self.text[:len(self.text) - 1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                if len(self.text) < self.max_chars:
                    self.text += str(event.unicode)

        self.text_rendered = self.input_font.render(self.text, True, Colors.LIGHT_GREY)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.shape, border_radius=5)
        pygame.draw.rect(screen, self.color, self.shape, 2, border_radius=5)
        screen.blit(self.text_rendered, (self.shape.x + 5, self.shape.y + 10))

# --- HELPER FUNCTIONS ---
def draw_pointer(node, text, color):
    node_x = node.shape.x + node.shape.width // 2
    if text == "TAIL":
        node_y = node.shape.y + node.shape.height + 8
        pygame.draw.polygon(screen, color, [(node_x, node_y), (node_x-10, node_y+15), (node_x+10, node_y+15)])
        lbl = subFont.render(f"{text}", True, color)
        screen.blit(lbl, (node_x - lbl.get_width() // 2, node_y + 20))
    elif text == "HEAD" or text == "TEMP":
        node_y = node.shape.y - 10
        pygame.draw.polygon(screen, color, [(node_x, node_y), (node_x-10, node_y-15), (node_x+10, node_y-15)])
        lbl = subFont.render(f"{text}", True, color)
        screen.blit(lbl, (node_x - lbl.get_width() // 2, node_y - 37))

def erase_pointer(screen, node, pointer_type="HEAD"):
    node_x = node.shape.x + node.shape.width // 2
    if pointer_type == "TAIL":
        start_y = node.shape.y + node.shape.height + 2
        pygame.draw.rect(screen, Colors.GREY, (node_x - 40, start_y, 80, 50))
    else:
        pygame.draw.rect(screen, Colors.GREY, (node_x - 40, node.shape.y - 50, 80, 50))

# --- NODE CLASS ---
class DLLNode:
    def __init__(self, data, pos, next=None, prev=None):
        self.data = data
        self.next = next
        self.prev = prev
        self.shape = pygame.Rect(pos[0], pos[1], 90, 70)
        self.text = nodeFont.render(f"{data}", True, Colors.LIGHT_GREY)

    def draw(self, screen, dll, highlight_color=Colors.TEAL, fill=False, drawNULL= True):
        # Draw node box
        if fill:
             pygame.draw.rect(screen, highlight_color, self.shape, border_radius=2)
        else:
            pygame.draw.rect(screen, Colors.TEAL, self.shape, border_radius=2)
            if highlight_color != Colors.TEAL: # Border highlight
                 pygame.draw.rect(screen, highlight_color, self.shape, 2, border_radius=2)

        # Labels
        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (self.shape.x, self.shape.y))
        text_rect = self.text.get_rect(center=self.shape.center)
        screen.blit(self.text, text_rect)

        if self == dll.head:
            draw_pointer(self, "HEAD", Colors.LIGHT_GREY)
        if self == dll.tail:
            draw_pointer(self, "TAIL", Colors.LIGHT_GREY)

        # --- NEXT POINTER (Top Half -> Right) ---
        start_x = self.shape.x + self.shape.width
        start_y = self.shape.y + 20
        
        if self.next is not None:
            end_x = self.next.shape.x
            end_y = self.next.shape.y + 20
            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [(end_x, end_y), (end_x-7, end_y-5), (end_x-7, end_y+5)])
        elif self == dll.tail:
            # NULL Next (always show for tail, or if drawNULL=True)
            null_x = start_x + 30
            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (null_x, start_y), 2)
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [(null_x, start_y), (null_x-7, start_y-5), (null_x-7, start_y+5)])
            null_txt = paraFont.render("NULL", True, Colors.LIGHT_GREY)
            screen.blit(null_txt, (null_x + 5, start_y - 10))

        # --- PREV POINTER (Bottom Half -> Left) ---
        start_x_prev = self.shape.x
        start_y_prev = self.shape.y + 50
        
        if self.prev is not None:
            end_x_prev = self.prev.shape.x + self.prev.shape.width
            end_y_prev = self.prev.shape.y + 50
            pygame.draw.line(screen, Colors.ORANGE, (start_x_prev, start_y_prev), (end_x_prev, end_y_prev), 2)
            pygame.draw.polygon(screen, Colors.ORANGE, [(end_x_prev, end_y_prev), (end_x_prev+7, end_y_prev-5), (end_x_prev+7, end_y_prev+5)])
        elif self == dll.head:
            # NULL Prev (always show for head, or if drawNULL=True)
            null_x_prev = start_x_prev - 30
            pygame.draw.line(screen, Colors.ORANGE, (start_x_prev, start_y_prev), (null_x_prev, start_y_prev), 2)
            pygame.draw.polygon(screen, Colors.ORANGE, [(null_x_prev, start_y_prev), (null_x_prev+7, start_y_prev-5), (null_x_prev+7, start_y_prev+5)])
            if drawNULL and self == dll.head:
                null_txt = paraFont.render("NULL", True, Colors.ORANGE)
                text_x = max(5, null_x_prev - 55)
                screen.blit(null_txt, (text_x, start_y_prev - 10))


# --- DOUBLY LINKED LIST CLASS ---
class DLL:
    def __init__(self, size):
        self.head = None
        self.tail = None
        self.size = size
        self.length = 0
        self.nodes = [] 
        
        node_width = 90
        gap_between_nodes = 35
        null_space = 30
        left_margin = 30
        
        total_width_needed = (size * node_width) + ((size - 1) * gap_between_nodes) + null_space + left_margin
        self.start_x_coord = max(30, (900 - total_width_needed) // 2 + left_margin)
        self.currentPos = (self.start_x_coord, 480)

    def drawList(self, drawNULL=True):
        for node in self.nodes:
            node.draw(screen, self, drawNULL=drawNULL)

    def _recalculate_positions(self):
        start_x = self.start_x_coord
        y_pos = 480
        for node in self.nodes:
            node.shape.x = start_x
            node.shape.y = y_pos
            start_x += 125
        self.currentPos = (start_x, y_pos)

    def _redraw(self, drawNULL=True):
        pygame.draw.rect(screen, Colors.GREY, (0, 370, 900, 330))
        self.drawList(drawNULL=drawNULL)
        update_status_ui()
        pygame.display.update()

    def insertAtTail(self, data):
        if self.length >= self.size:
            set_status("Limit Reached!", Colors.RED, "> Capacity Full")
            return

        newNode = DLLNode(data, self.currentPos)
        self.nodes.append(newNode)
        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])
        
        set_status(f"Node Added: {data}", Colors.GREEN, "> newNode = Node(data)")
        self._redraw()
        pygame.time.delay(1000)

        if self.head is None:
            self.head = newNode
            self.tail = newNode
            set_status("Head & Tail Updated", Colors.GREEN, "> head = tail = newNode")
        else:
            # 1. Update Logical Next
            self.tail.next = newNode
            set_status("Linking Next...", Colors.ORANGE, "> tail.next = newNode")
            self._redraw()
            pygame.time.delay(1000)
            
            # 2. Update Logical Prev
            newNode.prev = self.tail
            set_status("Linking Prev...", Colors.ORANGE, "> newNode.prev = tail")
            self._redraw()
            pygame.time.delay(1000)
            
            self.tail = newNode
            set_status("Tail Updated!", Colors.GREEN, "> tail = newNode")

        self.length += 1
        self._redraw()
        pygame.time.delay(500)

    def insertAtHead(self, data):
        if self.length >= self.size:
            set_status("Limit Reached!", Colors.RED, "> Capacity Full")
            return

        # Shift
        if self.length > 0:
            set_status("Shifting Nodes...", Colors.ORANGE, "> Shifting Right")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 900, 280))
            for node in self.nodes:
                node.shape.x += 125
            self.drawList(drawNULL=False)
            update_status_ui()
            # Erase the NULL text
            erase_rect = pygame.Rect(self.head.shape.x - 90, self.head.shape.y + 40, 60, 40)
            pygame.draw.rect(screen, Colors.GREY, erase_rect)
            pygame.display.update()
            pygame.time.delay(1000)

        start_x = self.start_x_coord
        start_y = 480
        newNode = DLLNode(data, (start_x, start_y))
        
        set_status("Creating Node...", Colors.ORANGE, "> newNode = Node(data)")
        self.nodes.insert(0, newNode)
        self.length += 1
        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])
        self._redraw(drawNULL=False)
        pygame.time.delay(1000)

        if self.head is None:
            self.head = newNode
            self.tail = newNode
        else:
            newNode.next = self.head
            set_status("Linking Forward...", Colors.ORANGE, "> newNode.next = head")
            self._redraw(drawNULL=False)
            pygame.time.delay(1000)
            
            self.head.prev = newNode
            set_status("Linking Backward...", Colors.ORANGE, "> head.prev = newNode")
            self._redraw(drawNULL=False)
            pygame.time.delay(1000)
            
            self.head = newNode

        set_status("Head Updated!", Colors.GREEN, "> head = newNode")
        self._redraw()
        pygame.time.delay(500)

    def insertAtPos(self, data, pos):
        if pos < 1 or pos > self.length + 1:
            set_status("Invalid Position", Colors.RED); return
        if pos == 1: self.insertAtHead(data); return
        if pos == self.length + 1: self.insertAtTail(data); return
        if self.length >= self.size: set_status("Limit Reached", Colors.RED); return

        set_status("Traversing...", Colors.ORANGE, "> while i < pos - 1")
        temp = self.head
        draw_pointer(temp, "TEMP", Colors.ORANGE)
        pygame.display.update()
        pygame.time.delay(1000)

        for i in range(pos - 2):
            erase_pointer(screen, temp, "TEMP")
            temp = temp.next
            draw_pointer(temp, "TEMP", Colors.ORANGE)
            update_status_ui()
            pygame.display.update()
            pygame.time.delay(1000)

        # Create Visual Node (Lowered)
        set_status("Creating Node...", Colors.ORANGE, "> newNode = Node(data)")
        
        newNode = DLLNode(data, (temp.shape.x + 60, temp.shape.y + 150))
        
        # Manually Draw Box only (No .draw() so no auto-NULLs yet)
        pygame.draw.rect(screen, Colors.TEAL, newNode.shape, border_radius=2)
        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (newNode.shape.x, newNode.shape.y))
        screen.blit(newNode.text, newNode.text.get_rect(center=newNode.shape.center))
        
        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        # --- 1. NewNode.next = Temp.next ---
        set_status("Linking Next...", Colors.ORANGE, "> newNode.next = temp.next")
        
        # Line: NewNode Right -> Up -> Right -> NextNode Left
        start_pos = (newNode.shape.x + newNode.shape.width, newNode.shape.y + 20)
        corner1 = (temp.next.shape.x - 10, start_pos[1]) # Right
        corner2 = (corner1[0], temp.next.shape.y + 20) # Up
        end_pos = (temp.next.shape.x, temp.next.shape.y + 20) # Right
        
        pygame.draw.line(screen, Colors.LIGHT_GREY, start_pos, corner1, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner1, corner2, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner2, end_pos, 2)
        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [(end_pos[0], end_pos[1]), (end_pos[0]-5, end_pos[1]-5), (end_pos[0]-5, end_pos[1]+5)])
        
        pygame.display.update()
        pygame.time.delay(1000)
        
        # Logically update
        newNode.next = temp.next

        # --- 2. Temp.next.prev = NewNode ---
        set_status("Linking Back...", Colors.ORANGE, "> temp.next.prev = newNode")
        
        # Erase NextNode's PREV area (pointing to temp initially)
        # We must redraw the grey background there to 'erase' the old line
        erase_rect = pygame.Rect(temp.next.shape.x - 50, temp.next.shape.y + 40, 50, 40)
        pygame.draw.rect(screen, Colors.GREY, erase_rect)

        # Line: NextNode Bottom-Left -> Left -> Down -> Left -> NewNode Bottom-Right
        start_pos = (temp.next.shape.x, temp.next.shape.y + 50)
        corner1 = (newNode.shape.x + newNode.shape.width + 10, start_pos[1]) # Left
        corner2 = (corner1[0], newNode.shape.y + 50) # Down
        end_pos = (newNode.shape.x + newNode.shape.width, newNode.shape.y + 50) # Left
        
        pygame.draw.line(screen, Colors.ORANGE, start_pos, corner1, 2)
        pygame.draw.line(screen, Colors.ORANGE, corner1, corner2, 2)
        pygame.draw.line(screen, Colors.ORANGE, corner2, end_pos, 2)
        pygame.draw.polygon(screen, Colors.ORANGE, [(end_pos[0], end_pos[1]), (end_pos[0]+5, end_pos[1]-5), (end_pos[0]+5, end_pos[1]+5)])
        
        pygame.display.update()
        pygame.time.delay(1000)
        
        # Logically update
        temp.next.prev = newNode

        # --- 3. Temp.next = NewNode ---
        set_status("Linking Temp Next...", Colors.ORANGE, "> temp.next = newNode")
        
        # Erase Temp's NEXT area
        erase_rect = pygame.Rect(temp.shape.x + temp.shape.width, temp.shape.y, 40, 40)
        pygame.draw.rect(screen, Colors.GREY, erase_rect)
        
        # Line: Temp Top-Right -> Right -> Down -> Right -> NewNode Top-Left
        start_pos = (temp.shape.x + temp.shape.width, temp.shape.y + 20)
        corner1 = (newNode.shape.x - 10, start_pos[1]) # Right
        corner2 = (corner1[0], newNode.shape.y + 20) # Down
        end_pos = (newNode.shape.x, newNode.shape.y + 20) # Right
        
        pygame.draw.line(screen, Colors.LIGHT_GREY, start_pos, corner1, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner1, corner2, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner2, end_pos, 2)
        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [(end_pos[0], end_pos[1]), (end_pos[0]-5, end_pos[1]-5), (end_pos[0]-5, end_pos[1]+5)])
        
        pygame.display.update()
        pygame.time.delay(1000)
        
        # Logically update
        temp.next = newNode

        # --- 4. NewNode.prev = Temp ---
        set_status("Linking Node Prev...", Colors.ORANGE, "> newNode.prev = temp")
        
        # Line: NewNode Bottom-Left -> Left -> Up -> Left -> Temp Bottom-Right
        start_pos = (newNode.shape.x, newNode.shape.y + 50)
        corner1 = (temp.shape.x + temp.shape.width + 10, start_pos[1]) # Left
        corner2 = (corner1[0], temp.shape.y + 50) # Up
        end_pos = (temp.shape.x + temp.shape.width, temp.shape.y + 50) # Left
        
        pygame.draw.line(screen, Colors.ORANGE, start_pos, corner1, 2)
        pygame.draw.line(screen, Colors.ORANGE, corner1, corner2, 2)
        pygame.draw.line(screen, Colors.ORANGE, corner2, end_pos, 2)
        pygame.draw.polygon(screen, Colors.ORANGE, [(end_pos[0], end_pos[1]), (end_pos[0]+5, end_pos[1]-5), (end_pos[0]+5, end_pos[1]+5)])
        
        pygame.display.update()
        pygame.time.delay(1000)
        
        # Logically update
        newNode.prev = temp

        # Realign List
        set_status("Realigning List...", Colors.ORANGE, "> Formatting UI")
        self.nodes.insert(pos - 1, newNode)
        self.length += 1
        
        self._recalculate_positions()
        self._redraw()
        erase_pointer(screen, temp, "TEMP")
        set_status("Insertion Complete!", Colors.GREEN, "> Success")
        pygame.time.delay(500)


    def deleteHead(self):
        if self.head is None: set_status("List Empty!", Colors.RED, "> return"); return
        
        set_status("Deleting Head...", Colors.ORANGE, "> head = head.next")
        
        # Simple Red Border Highlight
        pygame.draw.rect(screen, Colors.RED, self.head.shape, 2)
        pygame.display.update()
        pygame.time.delay(1000)

        if self.head.next:
            self.head = self.head.next
            self.head.prev = None
        else:
            self.head = None
            self.tail = None
            
        self.length -= 1
        self.nodes.pop(0)
        
        self._recalculate_positions()
        self._redraw()
        set_status("Head Deleted!", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def deleteTail(self):
        if self.tail is None: set_status("List Empty!", Colors.RED, "> return"); return
        if self.head == self.tail: self.deleteHead(); return
        
        set_status("Deleting Tail...", Colors.ORANGE, "> tail = tail.prev")
        
        # Simple Red Border Highlight
        pygame.draw.rect(screen, Colors.RED, self.tail.shape, 2)
        pygame.display.update()
        pygame.time.delay(1000)
        
        self.tail = self.tail.prev
        self.tail.next = None
        self.nodes.pop()
        self.length -= 1
        
        self._recalculate_positions()
        self._redraw()
        set_status("Tail Deleted!", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def deleteFromPos(self, pos):
        if pos < 1 or pos > self.length: set_status("Invalid Position", Colors.RED, "> Out of bounds"); return
        if pos == 1: self.deleteHead(); return
        if pos == self.length: self.deleteTail(); return
        
        set_status("Traversing...", Colors.ORANGE, "> finding pos")
        temp = self.head
        draw_pointer(temp, "TEMP", Colors.ORANGE)
        pygame.display.update()
        pygame.time.delay(1000)
        
        for i in range(pos - 1):
            erase_pointer(screen, temp, "TEMP")
            temp = temp.next
            draw_pointer(temp, "TEMP", Colors.ORANGE)
            update_status_ui()
            pygame.display.update()
            pygame.time.delay(1000)
            
        prevNode = temp.prev
        nextNode = temp.next
        
        set_status("Bypassing...", Colors.ORANGE, "> prev.next = next; next.prev = prev")
        
        # 1. Bridge NEXT (Over the top)
        # From PrevNode Top-Right -> Up -> Right (Past Curr) -> Down -> NextNode Top-Left
        start = (prevNode.shape.x + prevNode.shape.width, prevNode.shape.y + 20)
        corner1 = (start[0], prevNode.shape.y - 40) # Up high
        corner2 = (nextNode.shape.x, corner1[1]) # Across
        end = (nextNode.shape.x, nextNode.shape.y + 20) # Down
        
        pygame.draw.line(screen, Colors.LIGHT_GREY, start, corner1, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner1, corner2, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner2, end, 2)
        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [(end[0], end[1]), (end[0]-5, end[1]-5), (end[0]-5, end[1]+5)])
        
        # 2. Bridge PREV (Under the bottom)
        # From NextNode Bottom-Left -> Down -> Left (Past Curr) -> Up -> PrevNode Bottom-Right
        start_b = (nextNode.shape.x, nextNode.shape.y + 50)
        corner1_b = (start_b[0], nextNode.shape.y + 110) # Down low
        corner2_b = (prevNode.shape.x + prevNode.shape.width, corner1_b[1]) # Across
        end_b = (prevNode.shape.x + prevNode.shape.width, prevNode.shape.y + 50) # Up
        
        pygame.draw.line(screen, Colors.ORANGE, start_b, corner1_b, 2)
        pygame.draw.line(screen, Colors.ORANGE, corner1_b, corner2_b, 2)
        pygame.draw.line(screen, Colors.ORANGE, corner2_b, end_b, 2)
        pygame.draw.polygon(screen, Colors.ORANGE, [(end_b[0], end_b[1]), (end_b[0]+5, end_b[1]+5), (end_b[0]+5, end_b[1]-5)])
        
        pygame.display.update()
        pygame.time.delay(1500)
        
        # Update Logic
        prevNode.next = nextNode
        nextNode.prev = prevNode
        self.nodes.pop(pos-1)
        self.length -= 1
        
        self._recalculate_positions()
        
        self._redraw()
        set_status("Deleted!", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def search(self, data):
        if not self.head: set_status("List Empty!", Colors.RED, "> return"); return
        
        set_status(f"Searching {data}...", Colors.ORANGE, "> while temp != None")
        temp = self.head
        idx = 1
        found = False
        
        draw_pointer(temp, "TEMP", Colors.ORANGE)
        pygame.display.update()
        pygame.time.delay(1000)
        
        while temp:
            if str(temp.data) == str(data):
                found = True
                # Orange Background Fill using the modified draw method
                temp.draw(screen, self, highlight_color=Colors.ORANGE, fill=True)
                
                set_status(f"Found at Pos {idx}", Colors.GREEN, f"> return {idx}")
                pygame.display.update()
                pygame.time.delay(1000)
                break
            
            erase_pointer(screen, temp, "TEMP")
            temp = temp.next
            idx += 1
            
            if temp:
                draw_pointer(temp, "TEMP", Colors.ORANGE)
                update_status_ui()
                pygame.display.update()
                pygame.time.delay(1000)
            
        if not found:
            set_status("Value Not Found", Colors.RED, "> return -1")
            
        self._redraw()

    def destroy(self):
        set_status("Clearing...", Colors.ORANGE, "> while head != None")
        while self.head:
            self.head = self.head.next
            if self.nodes: self.nodes.pop(0)
            self._redraw()
            pygame.time.delay(300)
        self.tail = None
        self.length = 0
        self.currentPos = (self.start_x_coord, 480)
        set_status("List Cleared", Colors.GREEN, "> Success")


# --- UI SETUP ---
dll = DLL(6)

cap_bar = InputBar(50, 145, 130, 40, Colors.BLACK)
cap_bar.text = "6"
node_bar = InputBar(50, 230, 130, 40, Colors.BLACK, 4)
pos_insert_bar = InputBar(50, 315, 130, 40, Colors.BLACK, 2)
pos_delete_bar = InputBar(330, 315, 130, 40, Colors.BLACK, 2)
search_val_bar = InputBar(610, 315, 120, 40, Colors.BLACK, 2)

set_max_button = Button(190, 145, 120, 40, "Set Max", None, 18)
insert_tail_button = Button(190, 230, 120, 40, "Ins Tail", None, 18)
insert_head_button = Button(320, 230, 120, 40, "Ins Head", None, 18)
insert_at_pos_button = Button(190, 315, 120, 40, "Insert", None, 18)
delete_head_button = Button(450, 170, 130, 50, "Del Head", None, 18)
delete_tail_button = Button(590, 170, 130, 50, "Del Tail", None, 18)
destroy_button = Button(730, 170, 130, 50, "Destroy", None, 18)
delete_at_pos_button = Button(470, 315, 120, 40, "Delete", None, 18)
search_button = Button(740, 315, 120, 40, "Search", None, 18)

title = titleFont.render("Doubly Linked List", True, Colors.TEAL)
cap_value_txt = paraFont.render("Capacity (Max 6): ", True, Colors.LIGHT_GREY)
value_txt_1 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
value_txt_2 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
pos_txt_1 = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)
pos_txt_2 = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)

# --- MAIN LOOP ---
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(Colors.GREY)
    
    screen.blit(title, (50, 40))
    screen.blit(cap_value_txt, (50, 115))
    screen.blit(value_txt_1, (50, 200))
    screen.blit(value_txt_2, (610, 285))
    screen.blit(pos_txt_1, (50, 285))
    screen.blit(pos_txt_2, (330, 285))
    
    set_max_button.draw(screen)
    insert_tail_button.draw(screen)
    insert_head_button.draw(screen)
    insert_at_pos_button.draw(screen)
    delete_head_button.draw(screen)
    delete_tail_button.draw(screen)
    destroy_button.draw(screen)
    delete_at_pos_button.draw(screen)
    search_button.draw(screen)
    
    cap_bar.draw(screen)
    node_bar.draw(screen)
    pos_insert_bar.draw(screen)
    pos_delete_bar.draw(screen)
    search_val_bar.draw(screen)
    
    dll.drawList()
    update_status_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        cap_bar.handle_input(event)
        node_bar.handle_input(event)
        pos_insert_bar.handle_input(event)
        pos_delete_bar.handle_input(event)
        search_val_bar.handle_input(event)
        
        if set_max_button.is_clicked(event):
            if cap_bar.text.isdigit() and 0 < int(cap_bar.text) <= 6:
                dll = DLL(int(cap_bar.text))
                set_status(f"Max Set to {cap_bar.text}", Colors.GREEN)
            else:
                set_status("Invalid Max (1-6)", Colors.RED)

        if insert_tail_button.is_clicked(event):
            if node_bar.text: dll.insertAtTail(node_bar.text); node_bar.text = ""
            else: set_status("Input Value", Colors.RED)

        if insert_head_button.is_clicked(event):
            if node_bar.text: dll.insertAtHead(node_bar.text); node_bar.text = ""
            else: set_status("Input Value", Colors.RED)

        if insert_at_pos_button.is_clicked(event):
            if node_bar.text and pos_insert_bar.text.isdigit():
                dll.insertAtPos(node_bar.text, int(pos_insert_bar.text))
            else: set_status("Check Inputs", Colors.RED)

        if delete_head_button.is_clicked(event): dll.deleteHead()
        if delete_tail_button.is_clicked(event): dll.deleteTail()
        if destroy_button.is_clicked(event): dll.destroy()
        
        if delete_at_pos_button.is_clicked(event):
            if pos_delete_bar.text.isdigit():
                dll.deleteFromPos(int(pos_delete_bar.text))
            else: set_status("Invalid Pos", Colors.RED)

        if search_button.is_clicked(event):
            if search_val_bar.text: dll.search(search_val_bar.text)
            else: set_status("Input Value", Colors.RED)

    pygame.display.update()
    clock.tick(60)

pygame.quit()