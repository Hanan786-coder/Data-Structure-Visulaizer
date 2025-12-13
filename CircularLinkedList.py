import pygame
from button_template import Button
import Colors


status_msg = "Ready"
logic_msg = "Waiting for operation..."
status_color = Colors.LIGHT_GREY


# fonts
def get_font(size):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont('Arial', size)

titleFont = get_font(40)
paraFont = get_font(17)
subFont = get_font(13)
nodeFont = get_font(28)
logicFont = get_font(15)
statFont = get_font(19)


status_msg = "Ready"
logic_msg = "Waiting for operation..."
status_color = Colors.LIGHT_GREY

# Text rendering
title = titleFont.render("Circular Linked List", True, Colors.TEAL)
cap_value_txt = paraFont.render("Capacity (Max 6): ", True, Colors.LIGHT_GREY)
value_txt_1 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
value_txt_2 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
pos_txt_1 = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)
del_pos_txt = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)

status_msg = "Ready"
logic_msg = "Waiting for operation..."

def set_status(message, color, logic_message=""):
    global status_msg, status_color, logic_msg 
    status_msg = message
    status_color = color
    logic_msg = logic_message

def update_status_ui(screen):
    pygame.draw.rect(screen, Colors.GREY, (480, 50, 450, 100))

    logic_lbl = statFont.render("Logic Flow: ", True, Colors.LIGHT_GREY)
    screen.blit(logic_lbl, (500, 90))
    logic_txt = logicFont.render(f"{logic_msg}", True, Colors.TEAL_BRIGHT)
    screen.blit(logic_txt, (500, 115))

    status_surf = nodeFont.render(status_msg, True, status_color)
    screen.blit(status_surf, (500, 50))

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
            elif event.unicode.isprintable():
                if len(self.text) < self.max_chars:
                    self.text += event.unicode

        self.text_rendered = self.input_font.render(self.text, True, Colors.LIGHT_GREY)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.shape, border_radius=5)
        pygame.draw.rect(screen, self.color, self.shape, 2, border_radius=5)
        screen.blit(self.text_rendered, (self.shape.x + 2, self.shape.y + 5))

# Helper pointer drawing
def draw_pointer(node, text, color, screen):
    node_x = node.shape.x + node.shape.width // 2

    # Up-pointing triangle (same style as QUEUE FRONT)
    if text != "LAST" and text != "CURR" and text != "PREV":
        node_y = node.shape.y + node.shape.height + 8
        pygame.draw.polygon(screen, color, [
            (node_x, node_y),
            (node_x - 10, node_y + 15),
            (node_x + 10, node_y + 15)
        ])
    else:
        node_y = node.shape.y - 10
        pygame.draw.polygon(screen, color, [
            (node_x, node_y),
            (node_x - 10, node_y - 15),
            (node_x + 10, node_y - 15)
        ])

    # Label
    lbl_head = subFont.render(f"{text}", True, color)
    if text != "LAST" and text != "CURR" and text != "PREV":
        screen.blit(lbl_head, (node_x - lbl_head.get_width() // 2, node_y + 20))
    else:
        screen.blit(lbl_head, (node_x - lbl_head.get_width() // 2, node_y - 37))


def erase_pointer(screen, node, pointer_type="LAST"):
    # Calculate center of the node
    node_x = node.shape.x + node.shape.width // 2

    if pointer_type != "LAST" and pointer_type != "CURR" and pointer_type != "PREV":
        start_y = node.shape.y + node.shape.height + 2

        clear_rect = pygame.Rect(0, 0, 80, 50)
        clear_rect.centerx = node_x
        clear_rect.y = start_y

        pygame.draw.rect(screen, Colors.GREY, clear_rect)

    else:

        # Determine how high we need to erase
        if pointer_type == "TEMP_ABOVE":
            rect_height = 40
            clear_rect = pygame.Rect(0, 0, 80, rect_height)
            clear_rect.centerx = node_x
            clear_rect.bottom = node.shape.y - 48
            pygame.draw.rect(screen, Colors.GREY, clear_rect)
        else:
            rect_height = 50
            clear_rect = pygame.Rect(0, 0, 80, rect_height)
            clear_rect.centerx = node_x
            clear_rect.bottom = node.shape.y - 2

        pygame.draw.rect(screen, Colors.GREY, clear_rect)


def draw_pointer_on_last(node, text, color, screen):
    temp_x = node.shape.x + node.shape.width // 2
    temp_y = node.shape.y - 20

    # Draw TEMP pointer
    pygame.draw.polygon(screen, color, [
        (temp_x, temp_y - 29),  # Tip of TEMP pointer (above HEAD)
        (temp_x - 10, temp_y - 45),  # Left point
        (temp_x + 10, temp_y - 45)  # Right point
    ])

    lbl_temp = subFont.render(f"{text}", True, color)
    screen.blit(lbl_temp, (temp_x - lbl_temp.get_width() // 2, temp_y - 65))

class SCLLNode:
    def __init__(self, data, pos, next=None):
        self.data = data
        self.next = next
        self.shape = pygame.Rect(pos[0], pos[1], 90, 70)
        self.text = nodeFont.render(f"{data}", True, Colors.LIGHT_GREY)

    def draw(self, screen, scll, highlight_color=Colors.TEAL, fill=False):
        # Draw Node Box
        if fill:
            pygame.draw.rect(screen, highlight_color, self.shape, border_radius=2)
        else:
            pygame.draw.rect(screen, Colors.TEAL, self.shape, border_radius=2)
            if highlight_color != Colors.TEAL:
                pygame.draw.rect(screen, highlight_color, self.shape, 2, border_radius=2)

        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (self.shape.x, self.shape.y))
        text_rect = self.text.get_rect(center=self.shape.center)
        screen.blit(self.text, text_rect)

        if scll.last is not None and self == scll.last:
            draw_pointer(self, "LAST", Colors.LIGHT_GREY, screen)

        # next
        start_x = self.shape.x + self.shape.width
        start_y = self.shape.y + 35  # Center Y
        
        if self.next is not None:
            # Check if this is the LAST node pointing back to first node (Wrap Around)
            if scll.last is not None and self == scll.last and self.next == scll.last.next and scll.length > 1:
                # Draw Wrap-Around Line (UNDERNEATH)
                head_node = scll.last.next
                path_points = [
                    (start_x, start_y),
                    (start_x + 20, start_y),  # Out Right
                    (start_x + 20, start_y + 60),  # Down
                    (head_node.shape.x - 20, start_y + 60),  # All the way Left
                    (head_node.shape.x - 20, start_y),  # Up
                    (head_node.shape.x, start_y)  # In to Head
                ]
                pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
                # Arrow at first node
                end_x, end_y = path_points[-1]
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
            
            # Special case: Single node pointing to itself
            elif scll.length == 1 and self.next == self:
                path_points = [
                    (start_x, start_y),
                    (start_x + 20, start_y),
                    (start_x + 20, start_y + 70),
                    (self.shape.x - 20, start_y + 70),
                    (self.shape.x - 20, start_y),
                    (self.shape.x, start_y)
                ]
                pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
                end_x, end_y = path_points[-1]
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])

            else:
                # Normal Adjacent Connection
                end_x = self.next.shape.x
                end_y = self.next.shape.y + 35
                pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                # Arrow-head (triangle)
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])

class SCLL:
    def __init__(self, size):
        self.last = None  # The ONLY main pointer
        self.size = size
        self.length = 0
        self.nodes = []  # For rendering purposes, to keep order in UI
        
        # Approximate start X
        self.start_x_coord = 120
        self.currentPos = (self.start_x_coord, 480)

    def drawList(self, screen):
        for node in self.nodes:
            node.draw(screen, self)

    def _recalculate_positions(self):
        start_x = self.start_x_coord
        y_pos = 480
        for node in self.nodes:
            node.shape.x = start_x
            node.shape.y = y_pos
            start_x += 125
        self.currentPos = (start_x, y_pos)

    def _redraw(self, screen):
        pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
        self.drawList(screen)
        update_status_ui(screen)
        pygame.display.update()

    def insertAtEnd(self, data, screen):
        if self.length >= self.size:
            set_status("Limit Reached!", Colors.RED, "> Capacity Full")
            return

        newNode = SCLLNode(data, self.currentPos)
        self.nodes.append(newNode)
        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])
        
        set_status(f"Node Created: {data}", Colors.GREEN, "> newNode = Node(data)")
        self._redraw(screen)
        pygame.time.delay(1000)

        if self.last is None:
            self.last = newNode
            self.last.next = self.last
            set_status("List Initialized", Colors.GREEN, "> last = newNode; last.next = last")
        else:
            old_last = self.last
            first_node = self.last.next  # first node (last.next)
            
            # Erase the circular pointer (wrap-around from old_last to first_node)
            set_status("Erasing Circular Pointer...", Colors.ORANGE, "> Removing wrap")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            # Draw all nodes without the circular connection
            for node in self.nodes:
                # Draw node box
                pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
                screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
                text_rect = node.text.get_rect(center=node.shape.center)
                screen.blit(node.text, text_rect)
                
                # Draw LAST pointer if applicable
                if node == old_last:
                    draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
                
                # Draw normal connections (not the wrap-around)
                # Skip drawing if it's the circular connection from last to first
                if node.next is not None:
                    if not (node == old_last and node.next == first_node and self.length > 1):
                        # Also skip if it's a self-loop (single node case)
                        if not (node == old_last and node.next == old_last):
                            start_x = node.shape.x + node.shape.width
                            start_y = node.shape.y + 35
                            end_x = node.next.shape.x
                            end_y = node.next.shape.y + 35
                            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                            arrow_size = 7
                            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                                (end_x, end_y),
                                (end_x - arrow_size, end_y - arrow_size),
                                (end_x - arrow_size, end_y + arrow_size)
                            ])
            
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)

            # Draw simple pointer from old_last to newNode
            set_status("Linking Last...", Colors.ORANGE, "> last.next = newNode")
            self.last.next = newNode
            start_x = old_last.shape.x + old_last.shape.width
            start_y = old_last.shape.y + 35
            end_x = newNode.shape.x
            end_y = newNode.shape.y + 35
            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
            arrow_size = 7
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_x, end_y),
                (end_x - arrow_size, end_y - arrow_size),
                (end_x - arrow_size, end_y + arrow_size)
            ])
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)

            # Connect newNode to first_node (circular connection)
            newNode.next = first_node
            set_status("Linking Circular...", Colors.ORANGE, "> newNode.next = last.next")
            # Draw the wrap-around from newNode to first_node
            start_x = newNode.shape.x + newNode.shape.width
            start_y = newNode.shape.y + 35
            first_node_pos = first_node
            path_points = [
                (start_x, start_y),
                (start_x + 20, start_y),  # Out Right
                (start_x + 20, start_y + 60),  # Down
                (first_node_pos.shape.x - 20, start_y + 60),  # All the way Left
                (first_node_pos.shape.x - 20, start_y),  # Up
                (first_node_pos.shape.x, start_y)  # In to first node
            ]
            pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
            # Arrow at first node
            end_x, end_y = path_points[-1]
            arrow_size = 7
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_x, end_y),
                (end_x - arrow_size, end_y - arrow_size),
                (end_x - arrow_size, end_y + arrow_size)
            ])
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)

            # Update Last pointer
            self.last = newNode
            set_status("Tail Updated", Colors.GREEN, "> last = newNode")
            # Erase old LAST pointer and draw new one
            erase_pointer(screen, old_last, "LAST")
            draw_pointer(newNode, "LAST", Colors.LIGHT_GREY, screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(500)

        self.length += 1
        self._redraw(screen)
        pygame.time.delay(500)

    def insertAtBeginning(self, data, screen):
        if self.length >= self.size:
            set_status("Limit Reached!", Colors.RED, "> Capacity Full")
            return

        if self.length > 0:
            set_status("Shifting Nodes...", Colors.ORANGE, "> UI Shift")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 280))
            for node in self.nodes:
                node.shape.x += 125
            self.drawList(screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)

        start_x = self.start_x_coord
        start_y = 480
        newNode = SCLLNode(data, (start_x, start_y))
        
        set_status("Creating Node...", Colors.ORANGE, "> newNode = Node(data)")
        self.nodes.insert(0, newNode)
        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])
        self._redraw(screen)
        pygame.time.delay(1000)

        if self.last is None:
            self.last = newNode
            self.last.next = self.last
            set_status("List Initialized", Colors.GREEN, "> last = newNode; last.next = last")
        else:
            old_last = self.last
            first_node = self.last.next  # first node (last.next)
            
            # Erase the circular pointer
            set_status("Erasing Circular Pointer...", Colors.ORANGE, "> Removing wrap")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            # Draw all nodes without the circular connection
            for node in self.nodes:
                # Draw node box
                pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
                screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
                text_rect = node.text.get_rect(center=node.shape.center)
                screen.blit(node.text, text_rect)
                
                # Draw LAST pointer if applicable
                if node == old_last:
                    draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
                
                # Draw normal connections (not the wrap-around)
                if node.next is not None:
                    if not (node == old_last and node.next == first_node and self.length > 1):
                        if not (node == old_last and node.next == old_last):
                            start_x = node.shape.x + node.shape.width
                            start_y = node.shape.y + 35
                            end_x = node.next.shape.x
                            end_y = node.next.shape.y + 35
                            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                            arrow_size = 7
                            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                                (end_x, end_y),
                                (end_x - arrow_size, end_y - arrow_size),
                                (end_x - arrow_size, end_y + arrow_size)
                            ])
            
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)
            
            # Connect newNode to first_node
            newNode.next = first_node
            set_status("Linking Forward...", Colors.ORANGE, "> newNode.next = last.next")
            start_x = newNode.shape.x + newNode.shape.width
            start_y = newNode.shape.y + 35
            end_x = first_node.shape.x
            end_y = first_node.shape.y + 35
            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
            arrow_size = 7
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_x, end_y),
                (end_x - arrow_size, end_y - arrow_size),
                (end_x - arrow_size, end_y + arrow_size)
            ])
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)
            
            # Update last.next to point to newNode (circular connection)
            self.last.next = newNode
            set_status("Linking Circular...", Colors.ORANGE, "> last.next = newNode")
            # Draw the wrap-around from last to newNode
            start_x = old_last.shape.x + old_last.shape.width
            start_y = old_last.shape.y + 35
            path_points = [
                (start_x, start_y),
                (start_x + 20, start_y),  # Out Right
                (start_x + 20, start_y + 60),  # Down
                (newNode.shape.x - 20, start_y + 60),  # All the way Left
                (newNode.shape.x - 20, start_y),  # Up
                (newNode.shape.x, start_y)  # In to newNode
            ]
            pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
            # Arrow at newNode
            end_x, end_y = path_points[-1]
            arrow_size = 7
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_x, end_y),
                (end_x - arrow_size, end_y - arrow_size),
                (end_x - arrow_size, end_y + arrow_size)
            ])
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(200)
        set_status("Added!!", Colors.ORANGE, "> Success")
        self.length += 1
        self._redraw(screen)
        pygame.time.delay(500)

    def insertAtPosition(self, data, pos, screen):
        if pos < 1 or pos > self.length + 1:
            set_status("Invalid Position", Colors.RED)
            return
        if pos == 1: 
            self.insertAtBeginning(data, screen)
            return
        if pos == self.length + 1: 
            self.insertAtEnd(data, screen)
            return
        if self.length >= self.size: 
            set_status("Limit Reached", Colors.RED)
            return

        set_status("Traversing...", Colors.ORANGE, "> p = last.next; count=1")
        # Visual traversal starting from first node (last.next)
        temp = self.last.next 
        draw_pointer(temp, "CURR", Colors.ORANGE, screen)
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(800)

        # Iterate to pos-1
        for i in range(pos - 2):
            erase_pointer(screen, temp, "CURR")
            temp = temp.next
            draw_pointer(temp, "CURR", Colors.ORANGE, screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(800)

        set_status("Creating Node...", Colors.ORANGE, "> newNode = Node(data)")
        
        # Position newNode below temp to avoid overlap
        newNode = SCLLNode(data, (temp.shape.x + 60, temp.shape.y + 150))
        
        # Draw floating node
        pygame.draw.rect(screen, Colors.TEAL, newNode.shape, border_radius=2)
        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (newNode.shape.x, newNode.shape.y))
        screen.blit(newNode.text, newNode.text.get_rect(center=newNode.shape.center))
        
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Check if temp is the last node (circular connection case)
        is_circular_connection = (temp == self.last and temp.next == self.last.next and self.length > 1)
        target_node = temp.next
        
        # Erase the connection from temp to temp.next (might be circular)
        if is_circular_connection:
            set_status("Erasing Circular Pointer...", Colors.ORANGE, "> Removing wrap")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            # Redraw all nodes without the circular connection
            for node in self.nodes:
                pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
                screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
                text_rect = node.text.get_rect(center=node.shape.center)
                screen.blit(node.text, text_rect)
                
                if node == self.last:
                    draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
                
                # Draw normal connections (not the circular one we're erasing)
                if node.next is not None:
                    if not (node == self.last and node.next == self.last.next and self.length > 1):
                        if not (node == self.last and node.next == self.last):
                            start_x = node.shape.x + node.shape.width
                            start_y = node.shape.y + 35
                            end_x = node.next.shape.x
                            end_y = node.next.shape.y + 35
                            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                            arrow_size = 7
                            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                                (end_x, end_y),
                                (end_x - arrow_size, end_y - arrow_size),
                                (end_x - arrow_size, end_y + arrow_size)
                            ])
        else:
            # Just erase the simple arrow from temp to temp.next
            erase_x = temp.shape.x + temp.shape.width
            erase_y = temp.shape.y + (temp.shape.height // 2) - 10
            pygame.draw.rect(screen, Colors.GREY, (erase_x, erase_y, 35, 20))
        
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Draw pointer from temp to newNode: right -> down -> left -> down -> right
        set_status("Linking Previous...", Colors.ORANGE, "> temp.next = newNode")
        temp.next = newNode
        
        # Path: right -> down -> left -> down -> right
        start_x = temp.shape.x + temp.shape.width
        start_y = temp.shape.y + 35
        
        corner1 = (start_x + 20, start_y)  # Right
        corner2 = (corner1[0], start_y + 40)  # Down
        corner3 = (newNode.shape.x - 20, corner2[1])  # Left
        corner4 = (corner3[0], newNode.shape.y + newNode.shape.height // 2)  # Down
        end_x = newNode.shape.x  # Right into newNode
        end_y = corner4[1]
        
        pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), corner1, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner1, corner2, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner2, corner3, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner3, corner4, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner4, (end_x, end_y), 2)
        
        arrow_size = 7
        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
            (end_x, end_y),
            (end_x - arrow_size, end_y - arrow_size),
            (end_x - arrow_size, end_y + arrow_size)
        ])
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Connect newNode to target_node: right -> down -> left -> down -> right
        set_status("Linking Next...", Colors.ORANGE, "> newNode.next = temp.next")
        newNode.next = target_node
        
        if target_node:
            if is_circular_connection:
                # Draw circular connection from newNode to first node
                start_x = newNode.shape.x + newNode.shape.width
                start_y = newNode.shape.y + 35
                first_node = target_node
                path_points = [
                    (start_x, start_y),
                    (start_x + 20, start_y),  # Out Right
                    (start_x + 20, start_y + 60),  # Down
                    (first_node.shape.x - 20, start_y + 60),  # All the way Left
                    (first_node.shape.x - 20, start_y),  # Up
                    (first_node.shape.x, start_y)  # In to first node
                ]
                pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
                end_x, end_y = path_points[-1]
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
            else:
                # Draw connection from newNode to target_node: right -> up -> left -> up -> right
                start_x = newNode.shape.x + newNode.shape.width
                start_y = newNode.shape.y + 35
                
                corner1 = (start_x + 20, start_y)  # Right
                corner2 = (corner1[0], start_y - 40)  # Up
                corner3 = (target_node.shape.x - 20, corner2[1])  # Left
                corner4 = (corner3[0], target_node.shape.y + target_node.shape.height // 2)  # Up
                end_x = target_node.shape.x  # Right into target_node
                end_y = corner4[1]
                
                pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), corner1, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner1, corner2, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner2, corner3, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner3, corner4, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner4, (end_x, end_y), 2)
                
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
        
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        set_status("Realigning List...", Colors.ORANGE, "> Formatting UI")
        self.nodes.insert(pos - 1, newNode)
        self.length += 1
        
        erase_pointer(screen, temp, "CURR")
        self._recalculate_positions()
        self._redraw(screen)
        set_status("Insertion Complete!", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def deleteFromBeginning(self, screen):
        if self.last is None: 
            set_status("List Empty!", Colors.RED, "> return")
            return
        
        first_node = self.last.next
        set_status("Identifying First Node...", Colors.ORANGE, "> first = last.next")
        
        pygame.draw.rect(screen, Colors.RED, first_node.shape, 2)
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        if self.last == self.last.next:  # Only 1 Node
            # Erase circular connection
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            self.last = None
            set_status("Deleting Single Node...", Colors.ORANGE, "> last = None")
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)
        else:
            # Erase old circular connection from last to first
            set_status("Erasing Circular Pointer...", Colors.ORANGE, "> Removing wrap")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            # Redraw nodes without circular connection
            for node in self.nodes:
                pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
                screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
                text_rect = node.text.get_rect(center=node.shape.center)
                screen.blit(node.text, text_rect)
                if node == self.last:
                    draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
                # Draw connections except circular and first_node connections
                if node.next is not None and node != first_node:
                    if not (node == self.last and node.next == self.last.next):
                        start_x = node.shape.x + node.shape.width
                        start_y = node.shape.y + 35
                        end_x = node.next.shape.x
                        end_y = node.next.shape.y + 35
                        pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                        arrow_size = 7
                        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                            (end_x, end_y), (end_x - arrow_size, end_y - arrow_size),
                            (end_x - arrow_size, end_y + arrow_size)
                        ])
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)
            
            # Update last.next and draw new circular connection
            next_node = first_node.next
            self.last.next = next_node
            set_status("Updating Tail Link...", Colors.ORANGE, "> last.next = first.next")
            
            # Draw new circular connection from last to next_node
            if next_node:
                start_x = self.last.shape.x + self.last.shape.width
                start_y = self.last.shape.y + 35
                path_points = [
                    (start_x, start_y), (start_x + 20, start_y),
                    (start_x + 20, start_y + 60), (next_node.shape.x - 20, start_y + 60),
                    (next_node.shape.x - 20, start_y), (next_node.shape.x, start_y)
                ]
                pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
                end_x, end_y = path_points[-1]
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y), (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)

        set_status("Deleting First Node...", Colors.ORANGE, "> del first")
        update_status_ui(screen)
        pygame.time.delay(500)
        self.length -= 1
        self.nodes.pop(0)
        
        self._recalculate_positions()
        self._redraw(screen)
        set_status("First Node Deleted!", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def deleteFromEnd(self, screen):
        if self.last is None: 
            set_status("List Empty!", Colors.RED, "> return")
            return
        
        if self.length == 1:
            pygame.draw.rect(screen, Colors.RED, self.last.shape, 2)
            set_status("Deleting Single Node...", Colors.ORANGE, "> last = None")
            pygame.display.update()
            pygame.time.delay(800)
            self.last = None
            self.length -= 1
            self.nodes.pop()
            self._redraw(screen)
            set_status("Tail Deleted!", Colors.GREEN, "> Success")
            pygame.time.delay(500)
            return
        
        set_status("Traversing...", Colors.ORANGE, "> while curr.next != last")
        
        curr = self.last.next  # First node
        draw_pointer(curr, "CURR", Colors.ORANGE, screen)
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        while curr.next != self.last:
            erase_pointer(screen, curr, "CURR")
            curr = curr.next
            draw_pointer(curr, "CURR", Colors.ORANGE, screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)
        
        pygame.draw.rect(screen, Colors.RED, self.last.shape, 2)
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)
        
        set_status("Erasing Circular Pointer...", Colors.ORANGE, "> Removing wrap")
        # Erase old circular connection from last to first
        pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
        # Redraw nodes without circular connection
        for node in self.nodes:
            pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
            screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
            text_rect = node.text.get_rect(center=node.shape.center)
            screen.blit(node.text, text_rect)
            if node == self.last:
                draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
            # Draw connections except circular
            if node.next is not None and node != self.last:
                start_x = node.shape.x + node.shape.width
                start_y = node.shape.y + 35
                end_x = node.next.shape.x
                end_y = node.next.shape.y + 35
                pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y), (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
        erase_pointer(screen, curr, "CURR")
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)
        
        set_status("Updating Pointers...", Colors.ORANGE, "> curr.next = last.next")
        
        # Store old last before updating
        old_last = self.last
        
        # Erase LAST pointer from old last node
        erase_pointer(screen, old_last, "LAST")
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(500)
        
        # Update pointers
        curr.next = self.last.next
        self.last = curr  # Move tail pointer

        erase_x = curr.shape.x + curr.shape.width
        erase_y = curr.shape.y + (curr.shape.height // 2) - 10
        pygame.draw.rect(screen, Colors.GREY, (erase_x, erase_y, 35, 20))
        # Draw new circular connection from curr (new last) to first
        first_node = curr.next
        start_x = curr.shape.x + curr.shape.width
        start_y = curr.shape.y + 35
        path_points = [
            (start_x, start_y), (start_x + 20, start_y),
            (start_x + 20, start_y + 60), (first_node.shape.x - 20, start_y + 60),
            (first_node.shape.x - 20, start_y + 15), (first_node.shape.x, start_y + 15)
        ]
        pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
        end_x, end_y = path_points[-1]
        arrow_size = 7
        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
            (end_x, end_y), (end_x - arrow_size, end_y - arrow_size),
            (end_x - arrow_size, end_y + arrow_size)
        ])
        
        # Draw LAST pointer on new last node (curr)
        draw_pointer(curr, "LAST", Colors.LIGHT_GREY, screen)
        set_status("Moving Tail...", Colors.ORANGE, "> last = curr")
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)
        
        set_status("Deleting Last Node...", Colors.ORANGE, "> del last")
        update_status_ui(screen)
        pygame.time.delay(500)
        self.nodes.pop()
        self.length -= 1
        
        self._recalculate_positions()
        self._redraw(screen)
        set_status("Tail Deleted!", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def deleteByPosition(self, pos, screen):
        if self.last is None:
            set_status("List Empty!", Colors.RED, "> return")
            return
        
        if pos < 1 or pos > self.length:
            set_status("Invalid Position", Colors.RED, "> Position out of bounds")
            return
        
        if pos == 1:
            self.deleteFromBeginning(screen)
            return
        
        if pos == self.length:
            self.deleteFromEnd(screen)
            return

        set_status("Traversing...", Colors.ORANGE, "> while curr != pos")
        # Visual traversal starting from first node (last.next)
        curr = self.last.next
        prev = self.last
        draw_pointer(curr, "CURR", Colors.ORANGE, screen)
        # Draw PREV pointer on last node using draw_pointer_on_last
        draw_pointer_on_last(prev, "PREV", Colors.TEAL_BRIGHT, screen)
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Iterate to position
        for i in range(pos - 1):
            erase_pointer(screen, curr, "CURR")
            if prev == self.last:
                y = self.last.shape.y - 80
                x = self.last.shape.x + self.last.shape.width // 2 - 20
                pygame.draw.rect(screen, Colors.GREY, (x, y, 75, 35))
            else:
                erase_pointer(screen, prev, "PREV")
            prev = curr
            curr = curr.next
            draw_pointer(curr, "CURR", Colors.ORANGE, screen)
            # Draw PREV pointer - use draw_pointer_on_last if prev is last node
            if prev == self.last:
                draw_pointer_on_last(prev, "PREV", Colors.TEAL_BRIGHT, screen)
            else:
                draw_pointer(prev, "PREV", Colors.TEAL_BRIGHT, screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(1000)

        # Find previous node with visualization
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Highlight node to delete
        pygame.draw.rect(screen, Colors.RED, curr.shape, 2)
        set_status("Node Found!", Colors.GREEN, "> Node at position found")
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Check if this is a circular connection case
        is_circular_connection = (prev == self.last and prev.next == self.last.next and self.length > 1)
        
        # Erase the connection from prev to curr (might be circular)
        if is_circular_connection:
            set_status("Erasing Circular Pointer...", Colors.ORANGE, "> Removing wrap")
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            # Redraw all nodes without the circular connection
            for node in self.nodes:
                pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
                screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
                text_rect = node.text.get_rect(center=node.shape.center)
                screen.blit(node.text, text_rect)
                
                if node == self.last:
                    draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
                
                # Draw normal connections (not the circular one we're erasing)
                if node.next is not None:
                    if not (node == self.last and node.next == self.last.next and self.length > 1):
                        if not (node == self.last and node.next == self.last):
                            if node != prev or node.next != curr:
                                start_x = node.shape.x + node.shape.width
                                start_y = node.shape.y + 35
                                end_x = node.next.shape.x
                                end_y = node.next.shape.y + 35
                                pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                                arrow_size = 7
                                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                                    (end_x, end_y),
                                    (end_x - arrow_size, end_y - arrow_size),
                                    (end_x - arrow_size, end_y + arrow_size)
                                ])
        else:
            # Erase the simple arrow from prev to curr
            erase_x = prev.shape.x + prev.shape.width
            erase_y = prev.shape.y + (prev.shape.height // 2) - 10
            pygame.draw.rect(screen, Colors.GREY, (erase_x, erase_y, 35, 20))
        
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Update pointer: prev.next = curr.next (bypass curr)
        set_status("Bypassing Node...", Colors.ORANGE, "> prev.next = curr.next")
        prev.next = curr.next
        
        # Draw bridge connection from prev to curr.next: right -> down -> left -> down -> right
        if curr.next:
            if is_circular_connection:
                # Draw circular connection from prev to first node
                start_x = prev.shape.x + prev.shape.width
                start_y = prev.shape.y + 35
                first_node = curr.next
                path_points = [
                    (start_x, start_y),
                    (start_x + 20, start_y),  # Out Right
                    (start_x + 20, start_y + 60),  # Down
                    (first_node.shape.x - 20, start_y + 60),  # All the way Left
                    (first_node.shape.x - 20, start_y + 15),  # Up
                    (first_node.shape.x, start_y + 15)  # In to first node
                ]
                pygame.draw.lines(screen, Colors.LIGHT_GREY, False, path_points, 2)
                end_x, end_y = path_points[-1]
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
            else:
                # Draw bridge connection: right -> down -> left -> down -> right
                start_x = prev.shape.x + prev.shape.width
                start_y = prev.shape.y + 35
                
                corner1 = (start_x + 20, start_y)  # Right
                corner2 = (corner1[0], start_y + 40)  # Down
                corner3 = (curr.next.shape.x - 20, corner2[1])  # Left
                corner4 = (corner3[0], curr.next.shape.y + curr.next.shape.height // 2 + 15)  # Down
                end_x = curr.next.shape.x  # Right into target
                end_y = corner4[1]
                
                pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), corner1, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner1, corner2, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner2, corner3, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner3, corner4, 2)
                pygame.draw.line(screen, Colors.LIGHT_GREY, corner4, (end_x, end_y), 2)
                
                arrow_size = 7
                pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                    (end_x, end_y),
                    (end_x - arrow_size, end_y - arrow_size),
                    (end_x - arrow_size, end_y + arrow_size)
                ])
        
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(1000)

        # Remove node from list
        set_status("Removing Node...", Colors.ORANGE, "> del curr")
        update_status_ui(screen)
        index = self.nodes.index(curr)
        self.nodes.pop(index)
        self.length -= 1

        self._recalculate_positions()
        self._redraw(screen)
        set_status("Deletion Complete", Colors.GREEN, "> Success")
        pygame.time.delay(500)

    def search(self, value, screen):
        if self.last is None: 
            set_status("List Empty!", Colors.RED, "> return")
            return
        
        set_status(f"Searching {value}...", Colors.ORANGE, "> p = last.next; do...while")
        
        curr = self.last.next  # First node
        idx = 1
        found = False
        
        draw_pointer(curr, "CURR", Colors.ORANGE, screen)
        update_status_ui(screen)
        pygame.display.update()
        pygame.time.delay(800)
        
        while True:
            if str(curr.data) == str(value):
                found = True
                curr.draw(screen, self, highlight_color=Colors.ORANGE, fill=True)
                set_status(f"Found {value} at Pos {idx}", Colors.GREEN, f"> return {idx}")
                update_status_ui(screen)
                pygame.display.update()
                pygame.time.delay(1000)
                break
            
            # Check exit 
            if curr == self.last:
                break
            
            erase_pointer(screen, curr, "CURR")
            curr = curr.next
            idx += 1
            if curr == self.last:
                draw_pointer_on_last(self.last, "CURR", Colors.ORANGE, screen)
            else:
                draw_pointer(curr, "CURR", Colors.ORANGE, screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(800)
            
        if not found:
            set_status("Value Not Found", Colors.RED, "> return -1")
            
        self._redraw(screen)

    def destroyList(self, screen):
        if self.last is None:
            set_status("List is already Empty!", Colors.RED, "> if last is None: return")
            return

        set_status("Clearing List...", Colors.ORANGE, "> while last is not None:")
        
        while self.last is not None:
            curr = self.last.next  # First node
            
            # Show pointer on current node
            draw_pointer(curr, "CURR", Colors.ORANGE, screen)
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(500)
            
            # Erase circular connection if exists
            if self.length > 1:
                pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
                # Redraw remaining nodes
                for node in self.nodes:
                    if node != curr:
                        pygame.draw.rect(screen, Colors.TEAL, node.shape, border_radius=2)
                        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (node.shape.x, node.shape.y))
                        text_rect = node.text.get_rect(center=node.shape.center)
                        screen.blit(node.text, text_rect)
                        if node == self.last:
                            draw_pointer(node, "LAST", Colors.LIGHT_GREY, screen)
                        # Draw connections
                        if node.next is not None and node.next != curr:
                            start_x = node.shape.x + node.shape.width
                            start_y = node.shape.y + 35
                            end_x = node.next.shape.x
                            end_y = node.next.shape.y + 35
                            pygame.draw.line(screen, Colors.LIGHT_GREY, (start_x, start_y), (end_x, end_y), 2)
                            arrow_size = 7
                            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                                (end_x, end_y), (end_x - arrow_size, end_y - arrow_size),
                                (end_x - arrow_size, end_y + arrow_size)
                            ])
            
            erase_pointer(screen, curr, "CURR")
            
            # Update pointers
            if self.length == 1:
                self.last = None
            else:
                self.last.next = curr.next
                if curr == self.last:
                    self.last = None
            
            # Remove node
            if len(self.nodes) > 0:
                self.nodes.pop(0)
            self.length -= 1
            
            # Redraw list
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 330))
            if self.last:
                self.drawList(screen)
                if self.last.next == self.last:
                    draw_pointer_on_last(self.last, "CURR", Colors.ORANGE, screen)
                else:
                    draw_pointer(self.last.next, "CURR", Colors.ORANGE, screen)
                
            
            update_status_ui(screen)
            pygame.display.update()
            pygame.time.delay(500)

        self.nodes = []
        self.length = 0
        self.currentPos = (self.start_x_coord, 480)
        
        set_status("List Cleared!", Colors.GREEN, "> Success")
        self._redraw(screen)
        pygame.time.delay(500)


def run(screen):
    # Font loaders
    titleFont = get_font(40)
    paraFont = get_font(17)
    subFont = get_font(13)
    nodeFont = get_font(28)
    logicFont = get_font(15)
    statFont = get_font(19)


    status_msg = "Ready"
    logic_msg = "Waiting for operation..."
    status_color = Colors.LIGHT_GREY

    # Text rendering
    title = titleFont.render("Circular Linked List", True, Colors.TEAL)
    cap_value_txt = paraFont.render("Capacity (Max 6): ", True, Colors.LIGHT_GREY)
    value_txt_1 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
    value_txt_2 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
    pos_txt_1 = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)
    del_pos_txt = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)

    status_msg = "Ready"
    logic_msg = "Waiting for operation..."

    scll = SCLL(6)

    cap_bar = InputBar(100, 145, 130, 40, Colors.BLACK)
    cap_bar.text = "6"
    node_bar = InputBar(100, 230, 130, 40, Colors.BLACK, 4)
    pos_insert_bar = InputBar(100, 315, 130, 40, Colors.BLACK, 2)
    del_val_bar = InputBar(380, 315, 130, 40, Colors.BLACK, 4)
    search_val_bar = InputBar(660, 315, 120, 40, Colors.BLACK, 4)

    set_max_button = Button(240, 145, 120, 40, "Set Max", None, 18)
    insert_tail_button = Button(240, 230, 120, 40, "Insert End", None, 18)
    insert_head_button = Button(370, 230, 120, 40, "Insert Beg", None, 18)
    insert_at_pos_button = Button(240, 315, 120, 40, "Insert Pos", None, 18)
    delete_head_button = Button(500, 170, 130, 50, "Delete Beg", None, 18)
    delete_tail_button = Button(640, 170, 130, 50, "Delete End", None, 18)
    destroy_button = Button(780, 170, 130, 50, "Destroy List", None, 18)
    delete_pos_button = Button(520, 315, 120, 40, "Delete Pos", None, 18)
    search_button = Button(790, 315, 120, 40, "Search", None, 18)
    back_button = Button(930, 15, 70, 35, "← Back", None, 18)

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(Colors.GREY)

        screen.blit(title, (40, 40))
        screen.blit(cap_value_txt, (100, 115))
        screen.blit(value_txt_1, (100, 200))
        screen.blit(del_pos_txt, (380, 285))
        screen.blit(value_txt_2, (660, 285))
        screen.blit(pos_txt_1, (100, 285))

        set_max_button.draw(screen)
        insert_tail_button.draw(screen)
        insert_head_button.draw(screen)
        insert_at_pos_button.draw(screen)
        delete_head_button.draw(screen)
        delete_tail_button.draw(screen)
        destroy_button.draw(screen)
        delete_pos_button.draw(screen)
        search_button.draw(screen)
        back_button.draw(screen)

        cap_bar.draw(screen)
        node_bar.draw(screen)
        pos_insert_bar.draw(screen)
        del_val_bar.draw(screen)
        search_val_bar.draw(screen)

        scll.drawList(screen)
        update_status_ui(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            cap_bar.handle_input(event)
            node_bar.handle_input(event)
            pos_insert_bar.handle_input(event)
            del_val_bar.handle_input(event)
            search_val_bar.handle_input(event)

            if set_max_button.is_clicked(event):
                if cap_bar.text.isdigit() and 0 < int(cap_bar.text) <= 6:
                    scll = SCLL(int(cap_bar.text))
                    set_status(f"Max Set to {cap_bar.text}", Colors.GREEN)
                else:
                    set_status("Invalid Max (1-6)", Colors.RED)

            if insert_tail_button.is_clicked(event):
                if node_bar.text:
                    scll.insertAtEnd(node_bar.text, screen)
                    node_bar.text = ""
                    set_status("Inserted at end", Colors.GREEN)
                else:
                    set_status("Input Value", Colors.RED)

            if insert_head_button.is_clicked(event):
                if node_bar.text:
                    scll.insertAtBeginning(node_bar.text, screen)
                    node_bar.text = ""
                    set_status("Inserted at beginning", Colors.GREEN)
                else:
                    set_status("Input Value", Colors.RED)

            if insert_at_pos_button.is_clicked(event):
                if node_bar.text and pos_insert_bar.text.isdigit():
                    scll.insertAtPosition(node_bar.text, int(pos_insert_bar.text), screen)
                    pos_insert_bar.text = ""
                    set_status("Inserted at position", Colors.GREEN)
                else:
                    set_status("Check Inputs", Colors.RED)

            if delete_head_button.is_clicked(event):
                scll.deleteFromBeginning(screen)
                set_status("Deleted from beginning", Colors.GREEN)

            if delete_tail_button.is_clicked(event):
                scll.deleteFromEnd(screen)
                set_status("Deleted from end", Colors.GREEN)

            if destroy_button.is_clicked(event):
                scll.destroyList(screen)
                set_status("List destroyed", Colors.GREEN)

            if delete_pos_button.is_clicked(event):
                if del_val_bar.text and del_val_bar.text.isdigit():
                    scll.deleteByPosition(int(del_val_bar.text), screen)
                    del_val_bar.text = ""
                    set_status("Deleted from position", Colors.GREEN)
                else:
                   set_status("Input Valid Position", Colors.RED)

            if search_button.is_clicked(event):
                if search_val_bar.text:
                    scll.search(search_val_bar.text, screen)
                    set_status("Search completed", Colors.GREEN)
                else:
                    set_status("Input Value", Colors.RED)

            if back_button.is_clicked(event):
                return "back"

        update_status_ui(screen)
        pygame.display.update()
        clock.tick(60)

    return "back"

