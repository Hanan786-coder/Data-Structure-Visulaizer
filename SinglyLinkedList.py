import pygame
from button_template import Button
import Colors
import time


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
screen = pygame.display.set_mode((900, 700))
screen.fill(color=Colors.GREY)


# Font helper
def get_font(size):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont('Arial', size)


# Font loaders
titleFont = get_font(35)
paraFont = get_font(17)
subFont = get_font(13)
nodeFont = get_font(28)
logicFont = get_font(15)
statFont = get_font(19)
status_color = Colors.LIGHT_GREY

# Text rendering
title = titleFont.render("Singly Linked List", True, Colors.TEAL)
cap_value_txt = paraFont.render("Capacity (Max 6): ", True, Colors.LIGHT_GREY)
value_txt = paraFont.render("Value: ", True, Colors.LIGHT_GREY)
status_msg = "Ready"
logic_msg = "Waiting for a operation..."


def set_status(message, color, logic_message=""):
    global status_msg, status_color, logic_msg
    status_msg = message
    status_color = color
    logic_msg = logic_message


def update_status_ui():
    # Clear the area where status text is drawn to prevent overlap during animations
    pygame.draw.rect(screen, Colors.GREY, (430, 50, 450, 100))

    logic_lbl = statFont.render("Logic Flow: ", True, Colors.LIGHT_GREY)
    screen.blit(logic_lbl, (430, 90))

    logic_txt = logicFont.render(f"{logic_msg}", True, Colors.TEAL_BRIGHT)
    screen.blit(logic_txt, (430, 115))

    status_surf = nodeFont.render(status_msg, True, status_color)
    screen.blit(status_surf, (430, 50))


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


def draw_temp_on_head(node):
    temp_x = node.shape.x + node.shape.width // 2
    temp_y = node.shape.y - 20

    # Draw TEMP pointer
    pygame.draw.polygon(screen, Colors.ORANGE, [
        (temp_x, temp_y - 29),  # Tip of TEMP pointer (above HEAD)
        (temp_x - 10, temp_y - 45),  # Left point
        (temp_x + 10, temp_y - 45)  # Right point
    ])

    lbl_temp = subFont.render("TEMP", True, Colors.ORANGE)
    screen.blit(lbl_temp, (temp_x - lbl_temp.get_width() // 2, temp_y - 65))


# Text Input
cap_bar = InputBar(50, 145, 130, 40, Colors.BLACK)
cap_bar.text = "6"
node_bar = InputBar(50, 230, 130, 40, Colors.BLACK, 4)

# Buttons
set_max_button = Button(190, 145, 120, 40, "Set Max", None, 18)
add_node_button = Button(190, 230, 120, 40, "Add Node", None, 18)
delete_head_button = Button(50, 290, 130, 50, "Delete Head", None, 18)
delete_tail_button = Button(190, 290, 130, 50, "Delete Tail", None, 18)


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
            1: (350, 430),
            2: (300, 430),
            3: (250, 430),
            4: (200, 430),
            5: (110, 430),
            6: (40, 430),
        }
        self.currentPos = self.initialPos[self.size]
        self.nodes = []  # For drawing

    def drawList(self):
        for node in self.nodes:
            node.draw(screen, sll)

    def addNode(self, data):
        if self.length > self.size:
            set_status("Limit Reached!", Colors.RED, "> if self.length > self.size: return")
            return
        newNode = Node(data, self.currentPos)

        # Empty List
        if self.head is None:
            self.head = newNode
            self.tail = newNode
        else:
            self.tail.next = newNode
            self.tail = newNode
        self.length += 1
        self.currentPos = (self.currentPos[0] + 125, self.currentPos[1])
        self.nodes.append(newNode)

        set_status(f"Node Added: {data}", Colors.GREEN, f"> tail.next = newNode")

    def deleteHead(self, screen):
        if self.head is None:
            set_status("List Empty!", Colors.RED, "> if head is None: return")
            return
        else:
            set_status("Initializing...", Colors.ORANGE, "> temp = head")
            temp = self.head

            draw_temp_on_head(temp)

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

    def deleteTail(self):
        if self.tail is None:
            set_status("List Empty!", Colors.RED, "> if tail is None: return")
            return

        if self.head == self.tail:
            self.deleteHead(screen)
            return

        set_status("Initializing...", Colors.ORANGE, "> temp = head")
        temp = self.head

        draw_temp_on_head(temp)
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
        clear_rect = pygame.Rect(rect_x, rect_y, 900, 150)
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

    def destroyList(self):
        temp = self.head
        while self.head is not None:
            temp = temp.next
            del self.head  # Delete the Node
            self.head = temp
        del temp
        self.nodes.clear()
        self.length = 1
        self.currentPos = self.initialPos[self.size]
        set_status("List Cleared!", Colors.GREEN, "> New Max Capacity Set")


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
    screen.blit(cap_value_txt, (50, 115))
    screen.blit(value_txt, (50, 200))

    # Buttons
    set_max_button.draw(screen)
    delete_head_button.draw(screen)
    add_node_button.draw(screen)
    delete_tail_button.draw(screen)

    # Input Bars
    cap_bar.draw(screen)
    node_bar.draw(screen)

    # List
    sll.drawList()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if add_node_button.is_clicked(event):
            if node_bar.text != "":
                sll.addNode(node_bar.text)
                node_bar.text = ""
            else:
                set_status("Value Empty!", Colors.RED, "> if text == '': return")

        if set_max_button.is_clicked(event):
            if cap_value_txt != "" and 6 >= int(cap_bar.text) > 0:
                sll.size = int(cap_bar.text)
                sll.destroyList()
            elif cap_bar.text == "":
                set_status("Capacity can't be empty!", Colors.RED, "> cap_value != ''")
            elif int(cap_bar.text) > 6:
                set_status("Capacity should be < 6", Colors.RED, "> ")
            else:
                set_status("Invalid Capacity!", Colors.RED, "> ")

        if delete_head_button.is_clicked(event):
            sll.deleteHead(screen)
        if delete_tail_button.is_clicked(event):
            sll.deleteTail()

        cap_bar.handle_input(event)
        node_bar.handle_input(event)

    update_status_ui()

    pygame.display.update()
    clock.tick(60)