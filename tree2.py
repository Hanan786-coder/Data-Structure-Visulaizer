import pygame
import sys

# -----------------------------------------------------------------------------
# 1) CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------

# Window Dimensions
WIDTH, HEIGHT = 1000, 600

# Color Constants
ORANGE = (255, 108, 12)  # Highlight / Important
GREY = (57, 62, 70)  # Background
TEAL = (0, 173, 181)  # Default node fill / Primary UI
TEAL_BRIGHT = (0, 200, 210)  # Hover / Path color
TEAL_DARK = (0, 140, 145)  # Visited path fill color
BLACK = (43, 40, 49)  # Input background
LIGHT_GREY = (238, 238, 238)  # UI Text / Light elements
WHITE = (255, 255, 255)  # Edges / Accent
ERROR_COLOR = (255, 87, 87)  # Error messages
SUCCESS_COLOR = (0, 200, 81)  # Success messages

# Node Geometry
NODE_RADIUS = 30
NODE_BORDER_WIDTH = 2
LEVEL_GAP = 70  # Vertical distance between levels
START_Y = 150  # Base Y for the Root Node

# Timing Constants (ms)
TRAVERSE_STEP_MS = 500
POST_TRAVERSE_MS = 1000
INSERT_HIGHLIGHT_MS = 1000
FOUND_HIGHLIGHT_MS = 1000
ROTATION_MS = 1500  # Time to pause and show "Rotating..."


# -----------------------------------------------------------------------------
# 2) DATA STRUCTURES
# -----------------------------------------------------------------------------

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.x = 0
        self.y = 0
        self.height = 1  # Used for AVL calculations


# Global Tree State
root = None

# Global Animation/UI State
current_generator = None  # The active operation generator
last_step_time = 0  # Timestamp of last animation step
status_message = "Ready"
status_color = LIGHT_GREY
logic_message = ""
traversal_path = []  # List of nodes visited in current op
highlight_node = None  # Node currently being processed/highlighted
final_highlight_node = None  # Node to show in ORANGE at end of op
inorder_list = []  # For storing inorder results

# -----------------------------------------------------------------------------
# 3) PYGAME SETUP & UI CLASSES
# -----------------------------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BST Visualizer with AVL Rotations")


# Fonts
def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont('Arial', size, bold=bold)


font_ui = get_font(20)
font_elem = get_font(18, bold=True)
font_title = get_font(28, bold=True)
font_logic = get_font(16)


class Button:
    def __init__(self, x, y, w, h, text, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.is_hovered = False

    def draw(self, surface):
        color = TEAL_BRIGHT if self.is_hovered else TEAL
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Text
        txt_surf = font_ui.render(self.text, True, LIGHT_GREY)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = TEAL
        self.text = text
        self.txt_surface = font_ui.render(text, True, LIGHT_GREY)
        self.active = False

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
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isnumeric():
                        self.text += event.unicode
                self.txt_surface = font_ui.render(self.text, True, LIGHT_GREY)

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=8)
        surface.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))


# UI Elements Initialization
input_box = InputBox(50, 150, 140, 40)
buttons = [
    Button(50, 210, 140, 40, "Insert", "INSERT"),
    Button(50, 260, 140, 40, "Delete", "DELETE"),
    Button(50, 310, 140, 40, "Search", "SEARCH"),
    Button(50, 360, 140, 40, "Traverse", "TRAVERSE"),
    Button(50, 410, 140, 40, "Balance", "BALANCE"),
    Button(50, 480, 140, 40, "Clear Tree", "CLEAR")
]


# -----------------------------------------------------------------------------
# 4) HELPER FUNCTIONS (Layout, Logic, Math)
# -----------------------------------------------------------------------------

def set_status(msg, color, logic=""):
    global status_message, status_color, logic_message
    status_message = msg
    status_color = color
    logic_message = "> " + logic if logic else ""


def update_positions(node, x_min, x_max, depth, y_base, level_gap):
    if not node:
        return
    mid_x = (x_min + x_max) // 2
    node.x = mid_x
    node.y = y_base + (depth * level_gap)
    update_positions(node.left, x_min, mid_x, depth + 1, y_base, level_gap)
    update_positions(node.right, mid_x, x_max, depth + 1, y_base, level_gap)


def refresh_layout():
    update_positions(root, 300, WIDTH, 0, START_Y, LEVEL_GAP)


# AVL Helpers
def get_height(node):
    if not node: return 0
    return 1 + max(get_height(node.left), get_height(node.right))


def get_balance(node):
    if not node: return 0
    return get_height(node.left) - get_height(node.right)


# -----------------------------------------------------------------------------
# 5) GENERATOR ALGORITHMS (Animation Logic)
# -----------------------------------------------------------------------------

def gen_insert(val):
    global root, highlight_node, final_highlight_node, traversal_path
    traversal_path = []

    if root is None:
        root = Node(val)
        refresh_layout()
        final_highlight_node = root
        set_status(f"Inserted: {val}", SUCCESS_COLOR, "root is None; root = newNode")
        yield INSERT_HIGHLIGHT_MS
        final_highlight_node = None
        return

    curr = root
    while True:
        highlight_node = curr
        traversal_path.append(curr)

        if val == curr.value:
            set_status(f"Duplicate: {val}", ERROR_COLOR, "Value exists. Ignore.")
            yield 1000
            highlight_node = None
            traversal_path = []
            return
        elif val < curr.value:
            set_status(f"Visiting: {curr.value}", TEAL_BRIGHT, f"{val} < {curr.value}: Go Left")
            yield TRAVERSE_STEP_MS
            if curr.left is None:
                curr.left = Node(val)
                refresh_layout()
                final_highlight_node = curr.left
                set_status(f"Inserted: {val}", SUCCESS_COLOR, "curr.left = newNode")
                highlight_node = None
                yield INSERT_HIGHLIGHT_MS
                final_highlight_node = None
                break
            else:
                curr = curr.left
        else:
            set_status(f"Visiting: {curr.value}", TEAL_BRIGHT, f"{val} > {curr.value}: Go Right")
            yield TRAVERSE_STEP_MS
            if curr.right is None:
                curr.right = Node(val)
                refresh_layout()
                final_highlight_node = curr.right
                set_status(f"Inserted: {val}", SUCCESS_COLOR, "curr.right = newNode")
                highlight_node = None
                yield INSERT_HIGHLIGHT_MS
                final_highlight_node = None
                break
            else:
                curr = curr.right

    traversal_path = []


def gen_search(val):
    global highlight_node, final_highlight_node, traversal_path, logic_message
    traversal_path = []
    curr = root
    found = False

    while curr:
        highlight_node = curr
        traversal_path.append(curr)
        path_str = " -> ".join([str(n.value) for n in traversal_path])

        if val == curr.value:
            set_status(f"Found: {val}", SUCCESS_COLOR, "val == node.value: return node")
            logic_message = f"> Path: {path_str}"
            yield TRAVERSE_STEP_MS
            highlight_node = None
            final_highlight_node = curr
            yield FOUND_HIGHLIGHT_MS
            final_highlight_node = None
            found = True
            break
        elif val < curr.value:
            set_status(f"Searching: {val}", TEAL_BRIGHT, f"{val} < {curr.value}: Go Left")
            logic_message = f"> Path: {path_str}"
            yield TRAVERSE_STEP_MS
            curr = curr.left
        else:
            set_status(f"Searching: {val}", TEAL_BRIGHT, f"{val} > {curr.value}: Go Right")
            logic_message = f"> Path: {path_str}"
            yield TRAVERSE_STEP_MS
            curr = curr.right

    if not found:
        set_status(f"Not Found: {val}", ERROR_COLOR, "Reached None (Leaf)")
        yield 1000
    traversal_path = []


def gen_inorder(node, visit_list):
    global highlight_node, traversal_path
    if node:
        yield from gen_inorder(node.left, visit_list)
        highlight_node = node
        traversal_path.append(node)
        visit_list.append(node.value)
        list_str = ", ".join(map(str, visit_list))
        set_status("Traversing...", TEAL_BRIGHT, f"Inorder: [{list_str}]")
        yield TRAVERSE_STEP_MS
        yield from gen_inorder(node.right, visit_list)


def gen_traverse_wrapper():
    global highlight_node, traversal_path, inorder_list
    traversal_path = []
    inorder_list = []
    if root is None:
        set_status("Tree is Empty", ORANGE, "root is None")
        yield 1000
        return
    yield from gen_inorder(root, inorder_list)
    highlight_node = None
    final_str = ", ".join(map(str, inorder_list))
    set_status(f"Inorder: {final_str}", SUCCESS_COLOR, "Traversal Complete")
    yield POST_TRAVERSE_MS
    traversal_path = []


def gen_delete(val, parent=None, current=None, is_left_child=False):
    global root, highlight_node, final_highlight_node, traversal_path

    if current is None:
        if root is None:
            set_status("Empty Tree", ERROR_COLOR, "Cannot delete from empty tree")
            yield 1000
            return
        current = root
        parent = None
        traversal_path = []

    found_target = False
    while current:
        highlight_node = current
        traversal_path.append(current)

        if val == current.value:
            set_status(f"Found: {val}", TEAL_BRIGHT, "Target node identified")
            yield TRAVERSE_STEP_MS
            found_target = True
            break
        elif val < current.value:
            set_status(f"Finding: {val}", TEAL_BRIGHT, f"{val} < {current.value}: Go Left")
            yield TRAVERSE_STEP_MS
            parent = current
            current = current.left
            is_left_child = True
        else:
            set_status(f"Finding: {val}", TEAL_BRIGHT, f"{val} > {current.value}: Go Right")
            yield TRAVERSE_STEP_MS
            parent = current
            current = current.right
            is_left_child = False

    if not found_target:
        set_status("Value not found", ERROR_COLOR, "Traversal reached None")
        yield 1000
        traversal_path = []
        return

    highlight_node = current
    final_highlight_node = current

    # Case 1: Leaf
    if current.left is None and current.right is None:
        set_status("Deleting Leaf", ORANGE, "Leaf node removed")
        yield INSERT_HIGHLIGHT_MS
        if parent is None:
            root = None
        elif is_left_child:
            parent.left = None
        else:
            parent.right = None
        refresh_layout()
        set_status(f"Deleted: {val}", SUCCESS_COLOR, "Node removed")
        final_highlight_node = None
        highlight_node = None
        yield 1000

    # Case 2: One Child (Left)
    elif current.right is None:
        set_status("Deleting Node (1 Child)", ORANGE, "Replace node with left child")
        yield INSERT_HIGHLIGHT_MS
        if parent is None:
            root = current.left
        elif is_left_child:
            parent.left = current.left
        else:
            parent.right = current.left
        refresh_layout()
        set_status(f"Deleted: {val}", SUCCESS_COLOR, "Structure updated")
        final_highlight_node = None
        highlight_node = None
        yield 1000

    # Case 2: One Child (Right)
    elif current.left is None:
        set_status("Deleting Node (1 Child)", ORANGE, "Replace node with right child")
        yield INSERT_HIGHLIGHT_MS
        if parent is None:
            root = current.right
        elif is_left_child:
            parent.left = current.right
        else:
            parent.right = current.right
        refresh_layout()
        set_status(f"Deleted: {val}", SUCCESS_COLOR, "Structure updated")
        final_highlight_node = None
        highlight_node = None
        yield 1000

    # Case 3: Two Children
    else:
        set_status("Deleting Node (2 Children)", ORANGE, "Finding Inorder Successor")
        yield INSERT_HIGHLIGHT_MS
        succ_parent = current
        successor = current.right
        traversal_path.append(successor)
        highlight_node = successor
        set_status("Visiting Right Child", TEAL_BRIGHT, "Start searching min in right subtree")
        yield TRAVERSE_STEP_MS

        while successor.left:
            succ_parent = successor
            successor = successor.left
            traversal_path.append(successor)
            highlight_node = successor
            set_status("Go Left", TEAL_BRIGHT, "Seeking minimum...")
            yield TRAVERSE_STEP_MS

        set_status(f"Successor Found: {successor.value}", ORANGE, f"Copy {successor.value} to Node {current.value}")
        final_highlight_node = successor
        yield 1200

        current.value = successor.value
        set_status("Removing Successor", TEAL_BRIGHT, "delete(successor)")
        yield 500

        if succ_parent == current:
            succ_parent.right = successor.right
        else:
            succ_parent.left = successor.right

        refresh_layout()
        set_status(f"Deleted Original: {val}", SUCCESS_COLOR, "Copied val, removed successor")
        final_highlight_node = None
        highlight_node = None
        yield 1000
    traversal_path = []


# --- AVL ROTATION LOGIC ---

def rotate_right(y):
    """
         y           x
        / \         / \
       x   T3  ->  T1  y
      / \             / \
     T1  T2          T2  T3
    """
    x = y.left
    T2 = x.right
    # Rotation
    x.right = y
    y.left = T2
    return x


def rotate_left(x):
    """
       x             y
      / \           / \
     T1  y    ->   x   T3
        / \       / \
       T2  T3    T1  T2
    """
    y = x.right
    T2 = y.left
    # Rotation
    y.left = x
    x.right = T2
    return y


def gen_balance_recursive(node):
    global highlight_node, final_highlight_node

    if not node:
        return None

    # Post-order traversal: Balance children first
    node.left = yield from gen_balance_recursive(node.left)
    node.right = yield from gen_balance_recursive(node.right)

    # Update layout to show return from recursion
    refresh_layout()
    highlight_node = node

    # Calculate Balance
    bf = get_balance(node)

    if bf > 1 or bf < -1:
        set_status(f"Imbalance at {node.value}: {bf}", ORANGE, "Checking rotation cases...")
        final_highlight_node = node
        yield 1000

    # Left Heavy
    if bf > 1:
        # Check Left Child
        if get_balance(node.left) >= 0:
            # Left-Left Case -> Right Rotation
            set_status(f"LL Case at {node.value}", TEAL_BRIGHT, "Performing Right Rotation")
            yield ROTATION_MS

            new_root = rotate_right(node)
            refresh_layout()
            final_highlight_node = new_root
            yield ROTATION_MS
            return new_root

        else:
            # Left-Right Case -> Left Rotate Child, Right Rotate Root
            set_status(f"LR Case at {node.value}", TEAL_BRIGHT, "1. Left Rotate Child")
            final_highlight_node = node.left
            yield ROTATION_MS

            node.left = rotate_left(node.left)
            refresh_layout()
            yield ROTATION_MS

            set_status(f"LR Case at {node.value}", TEAL_BRIGHT, "2. Right Rotate Root")
            final_highlight_node = node
            yield ROTATION_MS

            new_root = rotate_right(node)
            refresh_layout()
            final_highlight_node = new_root
            yield ROTATION_MS
            return new_root

    # Right Heavy
    if bf < -1:
        # Check Right Child
        if get_balance(node.right) <= 0:
            # Right-Right Case -> Left Rotation
            set_status(f"RR Case at {node.value}", TEAL_BRIGHT, "Performing Left Rotation")
            yield ROTATION_MS

            new_root = rotate_left(node)
            refresh_layout()
            final_highlight_node = new_root
            yield ROTATION_MS
            return new_root

        else:
            # Right-Left Case -> Right Rotate Child, Left Rotate Root
            set_status(f"RL Case at {node.value}", TEAL_BRIGHT, "1. Right Rotate Child")
            final_highlight_node = node.right
            yield ROTATION_MS

            node.right = rotate_right(node.right)
            refresh_layout()
            yield ROTATION_MS

            set_status(f"RL Case at {node.value}", TEAL_BRIGHT, "2. Left Rotate Root")
            final_highlight_node = node
            yield ROTATION_MS

            new_root = rotate_left(node)
            refresh_layout()
            final_highlight_node = new_root
            yield ROTATION_MS
            return new_root

    final_highlight_node = None
    return node


def gen_balance():
    global root, highlight_node, final_highlight_node

    if root is None:
        set_status("Tree is Empty", ERROR_COLOR, "Nothing to balance")
        yield 1000
        return

    set_status("Starting AVL Balance", TEAL_BRIGHT, "Bottom-up Post-Order Traversal")
    yield 1000

    # Start Recursive Generator
    # We assign result to root to catch if the rotation happens at the very top
    root = yield from gen_balance_recursive(root)

    highlight_node = None
    final_highlight_node = None
    set_status("Balancing Complete", SUCCESS_COLOR, "Tree satisfies AVL property")
    yield 1000


# -----------------------------------------------------------------------------
# 6) DRAWING FUNCTIONS
# -----------------------------------------------------------------------------

def draw_tree(surface):
    draw_edges(surface, root)
    draw_nodes(surface, root)


def draw_edges(surface, node):
    if node is None: return
    if node.left:
        color, width = WHITE, 2
        # Path Highlighting Logic
        if node in traversal_path and node.left in traversal_path:
            try:
                idx = traversal_path.index(node)
                if idx + 1 < len(traversal_path) and traversal_path[idx + 1] == node.left:
                    color, width = TEAL_BRIGHT, 4
            except:
                pass
        pygame.draw.line(surface, color, (node.x, node.y), (node.left.x, node.left.y), width)
        draw_edges(surface, node.left)

    if node.right:
        color, width = WHITE, 2
        if node in traversal_path and node.right in traversal_path:
            try:
                idx = traversal_path.index(node)
                if idx + 1 < len(traversal_path) and traversal_path[idx + 1] == node.right:
                    color, width = TEAL_BRIGHT, 4
            except:
                pass
        pygame.draw.line(surface, color, (node.x, node.y), (node.right.x, node.right.y), width)
        draw_edges(surface, node.right)


def draw_nodes(surface, node):
    if node is None: return

    fill_color = TEAL
    border_color = WHITE

    # 1. Currently processing
    if node == highlight_node:
        border_color = TEAL_BRIGHT
        fill_color = TEAL_BRIGHT

    # 2. Final Result / Important
    elif node == final_highlight_node:
        border_color = ORANGE
        fill_color = ORANGE

    # 3. Path History
    elif node in traversal_path:
        border_color = TEAL_BRIGHT
        fill_color = TEAL_DARK

    pygame.draw.circle(surface, fill_color, (node.x, node.y), NODE_RADIUS)
    pygame.draw.circle(surface, border_color, (node.x, node.y), NODE_RADIUS, NODE_BORDER_WIDTH)

    text_color = WHITE if fill_color in [TEAL, TEAL_BRIGHT, TEAL_DARK, ORANGE] else BLACK
    val_surf = font_elem.render(str(node.value), True, text_color)
    val_rect = val_surf.get_rect(center=(node.x, node.y))
    surface.blit(val_surf, val_rect)

    draw_nodes(surface, node.left)
    draw_nodes(surface, node.right)


def draw_ui(surface):
    title_surf = font_title.render("BST Visualizer", True, TEAL)
    surface.blit(title_surf, (50, 30))

    status_surf = font_ui.render(status_message, True, status_color)
    status_rect = status_surf.get_rect(midtop=(WIDTH // 2 + 100, 30))
    surface.blit(status_surf, status_rect)

    logic_label = font_elem.render("Logic Flow:", True, LIGHT_GREY)
    surface.blit(logic_label, (350, 60))
    logic_surf = font_logic.render(logic_message, True, TEAL_BRIGHT)
    surface.blit(logic_surf, (350, 85))

    input_box.draw(surface)
    for btn in buttons:
        btn.draw(surface)

    if root is None:
        ph_surf = font_ui.render("Tree is empty.", True, LIGHT_GREY)
        ph_rect = ph_surf.get_rect(center=(WIDTH // 2 + 100, HEIGHT // 2))
        surface.blit(ph_surf, ph_rect)


# -----------------------------------------------------------------------------
# 7) MAIN LOOP
# -----------------------------------------------------------------------------

def main():
    global root, current_generator, last_step_time, highlight_node, traversal_path, final_highlight_node

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60)
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            input_box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not current_generator:
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            val = None
                            if btn.action_code in ["INSERT", "DELETE", "SEARCH"]:
                                try:
                                    val = int(input_box.text)
                                except ValueError:
                                    set_status("Error: Invalid Input", ERROR_COLOR, "Enter an integer")
                                    continue

                            if btn.action_code == "INSERT":
                                current_generator = gen_insert(val)
                            elif btn.action_code == "DELETE":
                                current_generator = gen_delete(val)
                            elif btn.action_code == "SEARCH":
                                current_generator = gen_search(val)
                            elif btn.action_code == "TRAVERSE":
                                current_generator = gen_traverse_wrapper()
                            elif btn.action_code == "BALANCE":
                                current_generator = gen_balance()
                            elif btn.action_code == "CLEAR":
                                root = None
                                traversal_path = []
                                highlight_node = None
                                final_highlight_node = None
                                set_status("Tree Cleared", SUCCESS_COLOR, "root = None")

                            last_step_time = current_time - 2000

        for btn in buttons:
            btn.check_hover(mouse_pos)

        if current_generator:
            if current_time - last_step_time >= 0:
                try:
                    wait_ms = next(current_generator)
                    last_step_time = current_time + wait_ms
                except StopIteration:
                    current_generator = None
                    last_step_time = 0
                    highlight_node = None
        else:
            if current_time >= last_step_time:
                last_step_time = 0

        screen.fill(GREY)
        draw_ui(screen)
        draw_tree(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()