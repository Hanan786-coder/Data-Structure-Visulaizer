import pygame
from button_template import Button
import Colors


class Node:
    def __init__(self, data, pos, next=None):
        # Logical terms
        self.data = data
        self.next = next

        # UI terms
        self.shape = pygame.Rect(pos[0], pos[1], 90, 70)
        self.text = nodeFont.render(f"{data}", True, Colors.LIGHT_GREY)

    def draw(self, screen, sll):
        # Draw node box
        pygame.draw.rect(screen, Colors.TEAL, self.shape, border_radius=2)

        # Labels
        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (self.shape.x, self.shape.y))
        text_rect = self.text.get_rect(center=self.shape.center)
        screen.blit(self.text, text_rect)

        if self == sll.head:
            draw_pointer(self, "HEAD", Colors.LIGHT_GREY)
        if self == sll.tail:
            draw_pointer(self, "TAIL", Colors.LIGHT_GREY)

        # Arrows
        if self.next is not None:
            start_x = self.shape.x + self.shape.width
            start_y = self.shape.y + self.shape.height // 2

            end_x = self.next.shape.x
            end_y = self.next.shape.y + self.next.shape.height // 2

            # Draw line between nodes
            pygame.draw.line(screen, Colors.LIGHT_GREY,
                             (start_x, start_y), (end_x, end_y), 2)

            # Arrow-head (triangle)
            arrow_size = 7
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_x, end_y),
                (end_x - arrow_size, end_y - arrow_size),
                (end_x - arrow_size, end_y + arrow_size)
            ])
        else:
            # Draw NULL arrow
            start_x = self.shape.x + self.shape.width
            start_y = self.shape.y + self.shape.height // 2

            null_x = start_x + 60
            null_y = start_y

            # Line to NULL
            pygame.draw.line(screen, Colors.LIGHT_GREY,
                             (start_x, start_y), (null_x, null_y), 2)

            # Arrow-head pointing to NULL
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (null_x, null_y),
                (null_x - 7, null_y - 7),
                (null_x - 7, null_y + 7)
            ])

            # Draw the NULL text
            null_text = paraFont.render("NULL", True, Colors.LIGHT_GREY)
            screen.blit(null_text, (null_x + 5, null_y - 10))


# Initializing
pygame.init()

# Screen
screen = pygame.display.set_mode((1000, 700))
screen.fill(color=Colors.GREY)


# Font helper
def get_font(size):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont('Arial', size)


# Font loaders
titleFont = get_font(40)
paraFont = get_font(17)
subFont = get_font(13)
nodeFont = get_font(28)
logicFont = get_font(15)
statFont = get_font(19)
status_color = Colors.LIGHT_GREY

# Text rendering
title = titleFont.render("Singly Linked List", True, Colors.TEAL)
cap_value_txt = paraFont.render("Capacity (Max 6): ", True, Colors.LIGHT_GREY)
value_txt_1 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
value_txt_2 = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
pos_txt_1 = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)
pos_txt_2 = paraFont.render("Pos: ", True, Colors.LIGHT_GREY)

status_msg = "Ready"
logic_msg = "Waiting for a operation..."


def set_status(message, color, logic_message=""):
    global status_msg, status_color, logic_msg
    status_msg = message
    status_color = color
    logic_msg = logic_message


def update_status_ui():
    # Clear the area where status text is drawn to prevent overlap during animations
    pygame.draw.rect(screen, Colors.GREY, (480, 50, 450, 100))

    logic_lbl = statFont.render("Logic Flow: ", True, Colors.LIGHT_GREY)
    screen.blit(logic_lbl, (500, 90))

    logic_txt = logicFont.render(f"{logic_msg}", True, Colors.TEAL_BRIGHT)
    screen.blit(logic_txt, (500, 115))

    status_surf = nodeFont.render(status_msg, True, status_color)
    screen.blit(status_surf, (500, 50))


# Input Bar Class
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
            else:  # any other key
                if len(self.text) < self.max_chars:
                    self.text += str(event.unicode)

        self.text_rendered = self.input_font.render(self.text, True, Colors.LIGHT_GREY)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.shape, border_radius=5)
        pygame.draw.rect(screen, self.color, self.shape, 2, border_radius=5)
        screen.blit(self.text_rendered, (self.shape.x + 2, self.shape.y + 5))


# Helper pointer drawing
def draw_pointer(node, text, color):
    node_x = node.shape.x + node.shape.width // 2

    # Up-pointing triangle (same style as QUEUE FRONT)
    if text == "TAIL":
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
    if text == "TAIL":
        screen.blit(lbl_head, (node_x - lbl_head.get_width() // 2, node_y + 20))
    else:
        screen.blit(lbl_head, (node_x - lbl_head.get_width() // 2, node_y - 37))


def erase_pointer(screen, node, pointer_type="HEAD"):
    # Calculate center of the node
    node_x = node.shape.x + node.shape.width // 2

    if pointer_type == "TAIL":
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


def draw_pointer_on_head(node, text, color):
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


# Text Input
cap_bar = InputBar(100, 145, 130, 40, Colors.BLACK)
cap_bar.text = "6"
node_bar = InputBar(100, 230, 130, 40, Colors.BLACK, 4)
pos_insert_bar = InputBar(100, 315, 130, 40, Colors.BLACK, 2)
pos_delete_bar = InputBar(380, 315, 130, 40, Colors.BLACK, 2)
search_val_bar = InputBar(660, 315, 120, 40, Colors.BLACK, 2)


# Buttons
set_max_button = Button(240, 145, 120, 40, "Set Max", None, 18)
insert_tail_button = Button(240, 230, 120, 40, "Insert Tail", None, 18)
insert_head_button = Button(370, 230, 120, 40, "Insert Head", None, 18)
insert_at_pos_button = Button(240, 315, 120, 40, "Insert", None, 18)
delete_head_button = Button(500, 170, 130, 50, "Delete Head", None, 18)
delete_tail_button = Button(640, 170, 130, 50, "Delete Tail", None, 18)
destroy_button = Button(780, 170, 130, 50, "Destroy List", None, 18)
delete_at_pos_button = Button(520, 315, 120, 40, "Delete", None, 18)
search_button = Button(790, 315, 120, 40, "Search", None, 18)


# Linked Lists class
class SLL:
    def __init__(self, size, head=None):
        # Logical terms
        self.head = head
        self.size = size
        self.length = 1
        self.tail = None

        # UI terms
        self.initialPos = {
            1: (400, 480),
            2: (350, 480),
            3: (300, 480),
            4: (250, 480),
            5: (160, 480),
            6: (90, 480),
        }
        self.currentPos = self.initialPos[self.size]
        self.nodes = []  # For drawing

    def drawList(self):
        for node in self.nodes:
            node.draw(screen, sll)

    def insertAtTail(self, data, screen):
        if self.length > self.size:
            set_status("Limit Reached!", Colors.RED, "> if self.length > self.size: return")
            return
        newNode = Node(data, self.currentPos)
        self.length += 1
        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])
        self.nodes.append(newNode)

        set_status(f"Node Added: {data}", Colors.GREEN, f"> tail.next = newNode")

        # Clear previous list
        rect_x = self.initialPos[self.size][0]
        rect_y = self.initialPos[self.size][1]
        clear_rect = pygame.Rect(rect_x, rect_y, 1000, 150)
        pygame.draw.rect(screen, Colors.GREY, clear_rect)

        # New List
        self.drawList()

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        # Empty List
        if self.head is None:
            self.head = newNode
            self.tail = newNode
        else:
            self.tail.next = newNode
            self.tail = newNode

        set_status("Tail Updated!", Colors.GREEN, "> tail = newNode")

    def insertAtHead(self, data, screen):
        if self.length > self.size:
            set_status("Limit Reached!", Colors.RED, "> Capacity Full")
            return

        if self.length > 0:
            set_status("Shifting Nodes...", Colors.ORANGE, "> Shifting existing nodes right")

            # Clear the list area
            pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 280))

            # Shift coordinates
            for node in self.nodes:
                node.shape.x += 125

            # Redraw shifted nodes
            self.drawList()
            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

        # 2. Create the new node at the start position
        start_x = self.initialPos[self.size][0]
        start_y = self.initialPos[self.size][1]
        newNode = Node(data, (start_x, start_y))

        set_status("Linking...", Colors.ORANGE, "> newNode.next = head")
        newNode.next = self.head

        self.nodes.insert(0, newNode)
        self.length += 1

        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])

        pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 280))
        self.drawList()

        set_status("New Node Inserted!", Colors.GREEN, "> newNode.next = head")

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        self.head = newNode

        if self.tail is None:
            self.tail = newNode

        set_status("Head Updated!", Colors.GREEN, "> head = newNode")
        pygame.draw.rect(screen, Colors.GREY, (0, 370, 1000, 280))
        self.drawList()

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)


    def deleteHead(self, screen):
        if self.head is None:
            set_status("List Empty!", Colors.RED, "> if head is None: return")
            return
        else:
            set_status("Initializing...", Colors.ORANGE, "> temp = head")
            temp = self.head

            draw_pointer_on_head(temp, "TEMP", Colors.ORANGE)

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

            erase_pointer(screen, temp, "HEAD")
            erase_pointer(screen, temp, "TEMP_ABOVE")

            set_status("Updating Head...", Colors.ORANGE, "> head = head.next")
            draw_pointer(self.head, "TEMP", Colors.ORANGE)

            if self.head.next:
                self.head = self.head.next
            else:
                self.head = None
                self.tail = None

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

            # Draw new HEAD pointer if exists
            if self.head:
                draw_pointer(self.head, "HEAD", Colors.LIGHT_GREY)

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

            set_status("Deleting Node...", Colors.ORANGE, "> delete temp")
            self.length -= 1
            self.nodes.pop(0)

            for node in self.nodes:
                node.shape.x -= 125

            # Update current position for next node
            if len(self.nodes) > 0:
                last_node = self.nodes[-1]
                self.currentPos = (last_node.shape.x + 125, self.currentPos[1])
            else:
                # Reset to initial position if list is empty
                self.currentPos = self.initialPos[self.size]

            set_status("Head Deleted!", Colors.GREEN, "> Success")
            update_status_ui()
            pygame.time.delay(500)

    def deleteTail(self, screen):
        if self.tail is None:
            set_status("List Empty!", Colors.RED, "> if tail is None: return")
            return

        if self.head == self.tail:
            self.deleteHead(screen)
            return

        set_status("Initializing...", Colors.ORANGE, "> temp = head")
        temp = self.head

        draw_pointer_on_head(temp, "TEMP", Colors.ORANGE)
        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)

        # Traverse to the second to last node
        set_status("Traversing...", Colors.ORANGE, "> while temp.next != tail:")
        while temp.next != self.tail:
            if temp == self.head:
                erase_pointer(screen, temp, "TEMP_ABOVE")
            else:
                erase_pointer(screen, temp, "TEMP")

            temp = temp.next

            # Draw new pointer
            if self.length > 3:
                draw_pointer(temp, "TEMP", Colors.ORANGE)

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

        # Logical Deletion
        set_status("Removing Tail...", Colors.ORANGE, "> tail = temp; tail.next = None")
        del self.tail
        self.nodes.pop()
        self.length -= 1

        self.tail = temp
        self.tail.next = None

        # Clear previous list
        rect_x = self.initialPos[self.size][0]
        rect_y = self.initialPos[self.size][1]
        clear_rect = pygame.Rect(rect_x, rect_y, 1000, 150)
        pygame.draw.rect(screen, Colors.GREY, clear_rect)

        # New List
        self.drawList()

        erase_pointer(screen, self.tail, "TAIL")
        if self.length > 3:
            draw_pointer(self.tail, "TEMP", Colors.ORANGE)

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        self.currentPos = (self.tail.shape.x + 125, self.tail.shape.y)

        set_status("Tail Deleted!", Colors.GREEN, "> Success")
        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)

    def insertAtPos(self, data, pos, screen):
        # 1. Validation
        if pos <= 1:
            self.insertAtHead(data, screen)
            return
        if pos > self.length + 1:
            set_status("Invalid Position!", Colors.RED, "> pos > length + 1")
            return
        if self.length >= self.size + 1:
            set_status("Limit Reached!", Colors.RED, "> Capacity Full")
            return

        if pos == self.length:
            self.insertAtTail(data, screen)
            return

        set_status("Traversing...", Colors.ORANGE, "> while i < pos - 1:")

        # 2. Traversal
        temp = self.head
        draw_pointer_on_head(temp, "TEMP", Colors.ORANGE)
        pygame.display.update()
        pygame.time.delay(500)

        for i in range(pos - 2):
            if temp == self.head:
                erase_pointer(screen, temp, "TEMP_ABOVE")
            else:
                erase_pointer(screen, temp, "TEMP")

            temp = temp.next

            draw_pointer(temp, "TEMP", Colors.ORANGE)
            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

        # 3. Create Visual Node (Lowered)
        set_status("Creating Node...", Colors.ORANGE, "> newNode = Node(data)")

        newNode = Node(data, (temp.shape.x + 60, temp.shape.y + 150))

        pygame.draw.rect(screen, Colors.TEAL, newNode.shape, border_radius=2)
        screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (newNode.shape.x, newNode.shape.y))
        text_rect = newNode.text.get_rect(center=newNode.shape.center)
        screen.blit(newNode.text, text_rect)

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)

        set_status("Linking Next...", Colors.ORANGE, "> newNode.next = temp.next")
        newNode.next = temp.next

        if temp.next:
            start_pos = (newNode.shape.x + newNode.shape.width // 2, newNode.shape.y)
            corner_pos = (start_pos[0], temp.next.shape.y + temp.next.shape.height // 1.2)
            end_pos = (temp.next.shape.x, corner_pos[1])

            pygame.draw.line(screen, Colors.LIGHT_GREY, start_pos, corner_pos, 2)
            pygame.draw.line(screen, Colors.LIGHT_GREY, corner_pos, end_pos, 2)

            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_pos[0], end_pos[1]),
                (end_pos[0] - 10, end_pos[1] - 5),
                (end_pos[0] - 10, end_pos[1] + 5)
            ])

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)

        set_status("Linking Previous...", Colors.ORANGE, "> temp.next = newNode")
        temp.next = newNode

        # Erase the old arrow
        erase_x = temp.shape.x + temp.shape.width
        erase_y = temp.shape.y + (temp.shape.height // 2) - 10
        pygame.draw.rect(screen, Colors.GREY, (erase_x, erase_y, 35, 20))

        # Draw Arrow: Down then Right
        start_pos = (temp.shape.x + temp.shape.width // 2, temp.shape.y + temp.shape.height)
        corner_pos = (start_pos[0], newNode.shape.y + newNode.shape.height // 2)
        end_pos = (newNode.shape.x, corner_pos[1])

        pygame.draw.line(screen, Colors.LIGHT_GREY, start_pos, corner_pos, 2)
        pygame.draw.line(screen, Colors.LIGHT_GREY, corner_pos, end_pos, 2)

        pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
            (end_pos[0], end_pos[1]),
            (end_pos[0] - 10, end_pos[1] - 5),
            (end_pos[0] - 10, end_pos[1] + 5)
        ])

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        set_status("Realigning List...", Colors.ORANGE, "> Formatting UI")

        self.length += 1
        self.nodes.insert(pos - 1, newNode)

        start_x = self.initialPos[self.size][0]
        y_pos = self.initialPos[self.size][1]

        for node in self.nodes:
            node.shape.x = start_x
            node.shape.y = y_pos

            node.text_rect = node.text.get_rect(center=node.shape.center)

            start_x += 125

        self.currentPos = (start_x, y_pos)

        # Update Tail logic
        if newNode.next is None:
            self.tail = newNode

        # Redraw List
        pygame.draw.rect(screen, Colors.GREY, (0, 350, 1000, 350))
        self.drawList()

        if temp == self.head:
            draw_pointer_on_head(temp, "TEMP", Colors.ORANGE)
        else:
            draw_pointer(temp, "TEMP", Colors.ORANGE)

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)

        # Clean up temp pointer
        if temp == self.head:
            erase_pointer(screen, temp, "TEMP_ABOVE")
        else:
            erase_pointer(screen, temp, "TEMP")

        set_status("Insertion Complete!", Colors.GREEN, "> Success")
        update_status_ui()
        pygame.display.update()

    def deleteFromPos(self, pos, screen):
        # Validation & Edge Cases
        if pos < 1 or pos > self.length:
            set_status("Invalid Position!", Colors.RED, "> pos out of bounds")
            return
        if pos == 1:
            self.deleteHead(screen)
            return
        if pos == self.length - 1:
            self.deleteTail(screen)
            return

        set_status("Traversing...", Colors.ORANGE, "> finding pos - 1")

        # 2. Traversal
        temp = self.head
        prev = None

        # Draw initial status
        draw_pointer_on_head(temp,"TEMP",Colors.ORANGE)

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(500)

        for i in range(pos - 1):
            # Erase previous pointers
            if temp == self.head:
                erase_pointer(screen, temp, "TEMP_ABOVE")
            else:
                erase_pointer(screen, temp, "TEMP")
            if prev:
                if prev == self.head:
                    erase_pointer(screen, prev, "TEMP_ABOVE")
                else:
                    erase_pointer(screen, prev, "PREV")

            # Move pointers
            prev = temp
            temp = temp.next

            draw_pointer(temp, "TEMP", Colors.ORANGE)
            if prev == self.head:
                draw_pointer_on_head(prev, "PREV", Colors.TEAL_BRIGHT)
            else:
                draw_pointer(prev, "PREV", Colors.TEAL_BRIGHT)

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(500)

        set_status("Re-linking...", Colors.ORANGE, "> prev.next = temp.next")

        prev.next = temp.next

        # Update
        # Erase the old arrow
        if prev is not None and temp.next is not None:
            erase_x = prev.shape.x + prev.shape.width
            erase_y = prev.shape.y + (prev.shape.height // 2) - 10
            pygame.draw.rect(screen, Colors.GREY, (erase_x, erase_y, 35, 20))

            start_pos = (prev.shape.x + prev.shape.width // 2 + 25, prev.shape.y)
            corner_pos_1 = (start_pos[0], prev.shape.y - (prev.shape.height // 2) - 20)
            corner_pos_2 = (temp.next.shape.x + 10, temp.next.shape.y - temp.next.shape.height // 2 - 20)
            end_pos = (temp.next.shape.x + 10, temp.next.shape.y)

            # Draw Vertical Line (Up)
            pygame.draw.line(screen, Colors.LIGHT_GREY, start_pos, corner_pos_1, 2)
            # Draw Horizontal Line (Corner 1 to 2)
            pygame.draw.line(screen, Colors.LIGHT_GREY, corner_pos_1, corner_pos_2, 2)
            # Draw Horizontal Line (Right)
            pygame.draw.line(screen, Colors.LIGHT_GREY, corner_pos_2, end_pos, 2)

            # Arrowhead pointing Right
            pygame.draw.polygon(screen, Colors.LIGHT_GREY, [
                (end_pos[0] + 1, end_pos[1]),  # Tip of TEMP pointer (above HEAD)
                (end_pos[0] - 7, end_pos[1] - 7),  # Left point
                (end_pos[0] + 7, end_pos[1] - 7)  # Right point
            ])

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(1000)


        set_status("Deleting Node...", Colors.ORANGE, ">temp.next = None; del temp")

        temp.next = None

        erase_x = temp.shape.x + temp.shape.width
        erase_y = temp.shape.y + (temp.shape.height // 2) - 10
        pygame.draw.rect(screen, Colors.GREY, (erase_x, erase_y, 35, 20))

        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        del temp
        self.nodes.pop(pos - 1)
        self.length -= 1

        set_status("Realigning List...", Colors.ORANGE, "> Formatting UI")

        for i in range(pos - 1, len(self.nodes)):
            self.nodes[i].shape.x -= 125
            # Update text rect position
            self.nodes[i].text_rect = self.nodes[i].text.get_rect(center=self.nodes[i].shape.center)

        # Update the 'currentPos' for next insertions
        self.currentPos = (self.currentPos[0] - 125, self.currentPos[1])

        set_status("Deletion Complete!", Colors.GREEN, "> Success")
        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

    def search(self, data, screen):
        if self.head is None:
            set_status("List is Empty!", Colors.RED, "> if head is None: return")
            return

        set_status(f"Searching for {data}...", Colors.ORANGE, "> while temp is not None; if data == temp.data")

        # Traversal
        temp = self.head
        index = 1
        found = False

        # Draw initial pointer
        draw_pointer_on_head(temp, "TEMP", Colors.ORANGE)
        update_status_ui()
        pygame.display.update()
        pygame.time.delay(1000)

        while temp is not None:
            # Compare Data (Convert both to string to be safe)
            if str(temp.data) == str(data):
                found = True

                pygame.draw.rect(screen, Colors.ORANGE, temp.shape, border_radius=2)
                screen.blit(subFont.render("data: ", True, Colors.LIGHT_GREY), (temp.shape.x, temp.shape.y))
                text_rect = (temp.text.get_rect(center=temp.shape.center))
                screen.blit(temp.text, text_rect)

                set_status(f"Found at Pos: {index}", Colors.GREEN, f"> return {index}")

                update_status_ui()
                pygame.display.update()
                pygame.time.delay(1000)
                break

            else:
                # Erase current pointer before moving
                if temp == self.head:
                    erase_pointer(screen, temp, "TEMP_ABOVE")
                else:
                    erase_pointer(screen, temp, "TEMP")

                # Move to next
                temp = temp.next
                index += 1

                # If next node exists, draw pointer there
                if temp is not None:
                    draw_pointer(temp, "TEMP", Colors.ORANGE)
                    update_status_ui()
                    pygame.display.update()
                    pygame.time.delay(1000)

        # Cleanup
        if temp is not None:
            if temp == self.head:
                erase_pointer(screen, temp, "TEMP_ABOVE")
            else:
                erase_pointer(screen, temp, "TEMP")

        if not found:
            set_status("Value Not Found", Colors.RED, "> return -1")
            update_status_ui()
        else:
            set_status("Search Complete", Colors.GREEN, "> Success")
            update_status_ui()

        pygame.display.update()
        pygame.time.delay(1000)


    def destroyList(self, screen):
        if self.head is None:
            set_status("List is already Empty!", Colors.RED, "> if head is None: return")
            return

        set_status("Clearing List...", Colors.ORANGE, "> while head is not None:")

        while self.head is not None:
            temp = self.head

            draw_pointer_on_head(temp, "TEMP", Colors.ORANGE)
            update_status_ui()
            pygame.display.update()
            pygame.time.delay(300)

            erase_pointer(screen, temp, "HEAD")
            erase_pointer(screen, temp, "TEMP_ABOVE")

            self.head = self.head.next

            if len(self.nodes) > 0:
                self.nodes.pop(0)
            self.length -= 1

            pygame.draw.rect(screen, Colors.GREY, (0, 360, 1000, 320))
            self.drawList()

            if self.head:
                draw_pointer(self.head, "HEAD", Colors.LIGHT_GREY)

            update_status_ui()
            pygame.display.update()
            pygame.time.delay(300)

        self.tail = None
        self.nodes = []
        self.length = 1
        self.currentPos = self.initialPos[self.size]

        set_status("List Cleared!", Colors.GREEN, "> New Max Capacity Set")
        update_status_ui()
        pygame.display.update()

# Main Loop
running = True
clock = pygame.time.Clock()
sll = SLL(6)
while running:
    # 1. CLEAR THE SCREEN FIRST
    screen.fill(Colors.GREY)

    # UI
    # Texts
    screen.blit(title, (50, 40))
    screen.blit(cap_value_txt, (100, 115))
    screen.blit(value_txt_1, (100, 200))
    screen.blit(value_txt_2, (660, 285))
    screen.blit(pos_txt_1, (100, 285))
    screen.blit(pos_txt_2, (380, 285))

    # Buttons
    set_max_button.draw(screen)
    delete_head_button.draw(screen)
    insert_tail_button.draw(screen)
    delete_tail_button.draw(screen)
    insert_head_button.draw(screen)
    insert_at_pos_button.draw(screen)
    destroy_button.draw(screen)
    delete_at_pos_button.draw(screen)
    search_button.draw(screen)

    # Input Bars
    cap_bar.draw(screen)
    node_bar.draw(screen)
    pos_insert_bar.draw(screen)
    pos_delete_bar.draw(screen)
    search_val_bar.draw(screen)

    # List
    sll.drawList()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if insert_tail_button.is_clicked(event):
            if node_bar.text != "":
                sll.insertAtTail(node_bar.text, screen)
                node_bar.text = ""
            else:
                set_status("Value Empty!", Colors.RED, "> if text == '': return")

        # New Insert Head Logic
        if insert_head_button.is_clicked(event):
            if node_bar.text != "":
                sll.insertAtHead(node_bar.text, screen)
                node_bar.text = ""
            else:
                set_status("Value Empty!", Colors.RED, "> Enter Value to Insert")

        if set_max_button.is_clicked(event):
            if cap_value_txt != "" and 6 >= int(cap_bar.text) > 0:
                sll.size = int(cap_bar.text)
                sll.nodes.clear()
                sll.currentPos = sll.initialPos[sll.size]
                sll.length = 1
                set_status("Capacity Updated!", Colors.GREEN, f"> size = {cap_bar.text}")
            elif cap_bar.text == "":
                set_status("Capacity can't be empty!", Colors.RED, "> cap_value != ''")
            elif int(cap_bar.text) > 6:
                set_status("Capacity should be < 6", Colors.RED, "> ")
            else:
                set_status("Invalid Capacity!", Colors.RED, "> ")

        if delete_head_button.is_clicked(event):
            sll.deleteHead(screen)
        if delete_tail_button.is_clicked(event):
            sll.deleteTail(screen)
        if destroy_button.is_clicked(event):
            sll.destroyList(screen)
        if insert_at_pos_button.is_clicked(event):
            if pos_insert_bar.text == "":
                set_status("Position can't be empty!", Colors.RED, "> ")
            elif node_bar.text == "":
                set_status("Value can't be empty!", Colors.RED, "> ")
            elif not pos_insert_bar.text.isdigit():
                set_status("Invalid Position!", Colors.RED, "> ")
            else:
                sll.insertAtPos(node_bar.text, int(pos_insert_bar.text), screen)
        if delete_at_pos_button.is_clicked(event):
            if pos_delete_bar.text == "":
                set_status("Position can't be empty!", Colors.RED, "> ")
            elif not pos_delete_bar.text.isdigit():
                set_status("Pos must be a number!", Colors.RED, "> ")
            elif sll.length == 1:
                set_status("List is Empty!", Colors.RED, "> ")
            elif int(pos_delete_bar.text) > sll.length - 1:
                set_status("Invalid Position!", Colors.RED, "> ")
            else:
                sll.deleteFromPos(int(pos_delete_bar.text), screen)
        if search_button.is_clicked(event):
            if search_val_bar.text == "":
                set_status("Value can't be empty!", Colors.RED, "> ")
            else:
                sll.search(search_val_bar.text, screen)

        cap_bar.handle_input(event)
        node_bar.handle_input(event)
        pos_insert_bar.handle_input(event)
        pos_delete_bar.handle_input(event)
        search_val_bar.handle_input(event)

    update_status_ui()

    pygame.display.update()
    clock.tick(60)