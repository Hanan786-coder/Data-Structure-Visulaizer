import pygame
import sys
import Colors

# -----------------------------------------------------------------------------
# 1) CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------

# Window Dimensions
WIDTH, HEIGHT = 1000, 700

# Color Constants
ORANGE = (255, 108, 12)  # Highlight / Important
GREY = Colors.GREY  # Background
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
ROTATION_MS = 1200  # Time allowed for rotation animation


# -----------------------------------------------------------------------------
# 2) DATA STRUCTURES & FONTS
# -----------------------------------------------------------------------------

class Node:
    def __init__(self, value, x=0, y=0):
        self.value = value
        self.left = None
        self.right = None
        # Physics Coordinates
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.height = 1

    def update_physics(self):
        # Smoothly interpolate towards target
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1


def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except:
        return pygame.font.SysFont('Arial', size, bold=bold)


# Global fonts (loaded once)
font_ui = get_font(20)
font_elem = get_font(18, bold=True)
font_title = get_font(28, bold=True)
font_logic = get_font(16)


# -----------------------------------------------------------------------------
# 3) UI CLASSES
# -----------------------------------------------------------------------------

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
            self.color = WHITE if self.active else TEAL
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


# -----------------------------------------------------------------------------
# 4) MAIN RUN FUNCTION
# -----------------------------------------------------------------------------

def run(screen):
    clock = pygame.time.Clock()

    # --- Local Logic State (Reset on every run) ---
    state = {
        "root": None,
        "current_generator": None,
        "last_step_time": 0,
        "status_message": "Ready",
        "status_color": LIGHT_GREY,
        "logic_message": "",
        "traversal_path": [],
        "highlight_node": None,
        "final_highlight_node": None,
        "inorder_list": []
    }

    # UI Elements
    input_box = InputBox(50, 150, 140, 40)

    buttons = [
        Button(50, 210, 140, 40, "Insert", "INSERT"),
        Button(50, 260, 140, 40, "Delete", "DELETE"),
        Button(50, 310, 140, 40, "Search", "SEARCH"),
        Button(50, 360, 140, 40, "Traverse", "TRAVERSE"),
        Button(50, 410, 140, 40, "Balance", "BALANCE"),
        Button(50, 480, 140, 40, "Clear Tree", "CLEAR"),
        Button(900, 20, 80, 40, "Back", "BACK")
    ]

    # --- Helper Functions ---

    def set_status(msg, color, logic=""):
        state["status_message"] = msg
        state["status_color"] = color
        state["logic_message"] = "> " + logic if logic else ""

    def update_targets(node, x_min, x_max, depth, y_base, level_gap):
        if not node: return
        mid_x = (x_min + x_max) // 2
        # Set Target position (Physics will glide node there)
        node.target_x = mid_x
        node.target_y = y_base + (depth * level_gap)
        update_targets(node.left, x_min, mid_x, depth + 1, y_base, level_gap)
        update_targets(node.right, mid_x, x_max, depth + 1, y_base, level_gap)

    def refresh_layout():
        update_targets(state["root"], 250, WIDTH, 0, START_Y, LEVEL_GAP)

    def update_physics(node):
        if not node: return
        node.update_physics()
        update_physics(node.left)
        update_physics(node.right)

    # AVL Helpers
    def get_height(node):
        if not node: return 0
        return 1 + max(get_height(node.left), get_height(node.right))

    def get_balance(node):
        if not node: return 0
        return get_height(node.left) - get_height(node.right)

    # --- Generator Algorithms ---

    def gen_insert(val):
        state["traversal_path"] = []

        if state["root"] is None:
            # Spawn root at top center
            state["root"] = Node(val, 600, START_Y)
            refresh_layout()
            state["final_highlight_node"] = state["root"]
            set_status(f"Inserted: {val}", SUCCESS_COLOR, "root is None; root = newNode")
            yield INSERT_HIGHLIGHT_MS
            state["final_highlight_node"] = None
            return

        curr = state["root"]
        while True:
            state["highlight_node"] = curr
            state["traversal_path"].append(curr)

            if val == curr.value:
                set_status(f"Duplicate: {val}", ERROR_COLOR, "Value exists. Ignore.")
                yield 1000
                state["highlight_node"] = None
                state["traversal_path"] = []
                return
            elif val < curr.value:
                set_status(f"Visiting: {curr.value}", TEAL_BRIGHT, f"{val} < {curr.value}: Go Left")
                yield TRAVERSE_STEP_MS
                if curr.left is None:
                    # Spawn at parent location
                    curr.left = Node(val, curr.x, curr.y)
                    refresh_layout()  # Triggers physics movement to new spot
                    state["final_highlight_node"] = curr.left
                    set_status(f"Inserted: {val}", SUCCESS_COLOR, "curr.left = newNode")
                    state["highlight_node"] = None
                    yield INSERT_HIGHLIGHT_MS
                    state["final_highlight_node"] = None
                    break
                else:
                    curr = curr.left
            else:
                set_status(f"Visiting: {curr.value}", TEAL_BRIGHT, f"{val} > {curr.value}: Go Right")
                yield TRAVERSE_STEP_MS
                if curr.right is None:
                    # Spawn at parent location
                    curr.right = Node(val, curr.x, curr.y)
                    refresh_layout()
                    state["final_highlight_node"] = curr.right
                    set_status(f"Inserted: {val}", SUCCESS_COLOR, "curr.right = newNode")
                    state["highlight_node"] = None
                    yield INSERT_HIGHLIGHT_MS
                    state["final_highlight_node"] = None
                    break
                else:
                    curr = curr.right
        state["traversal_path"] = []

    def gen_search(val):
        state["traversal_path"] = []
        curr = state["root"]
        found = False

        while curr:
            state["highlight_node"] = curr
            state["traversal_path"].append(curr)
            path_str = " -> ".join([str(n.value) for n in state["traversal_path"]])

            if val == curr.value:
                set_status(f"Found: {val}", SUCCESS_COLOR, "val == node.value: return node")
                state["logic_message"] = f"> Path: {path_str}"
                yield TRAVERSE_STEP_MS
                state["highlight_node"] = None
                state["final_highlight_node"] = curr
                yield FOUND_HIGHLIGHT_MS
                state["final_highlight_node"] = None
                found = True
                break
            elif val < curr.value:
                set_status(f"Searching: {val}", TEAL_BRIGHT, f"{val} < {curr.value}: Go Left")
                state["logic_message"] = f"> Path: {path_str}"
                yield TRAVERSE_STEP_MS
                curr = curr.left
            else:
                set_status(f"Searching: {val}", TEAL_BRIGHT, f"{val} > {curr.value}: Go Right")
                state["logic_message"] = f"> Path: {path_str}"
                yield TRAVERSE_STEP_MS
                curr = curr.right

        if not found:
            set_status(f"Not Found: {val}", ERROR_COLOR, "Reached None (Leaf)")
            yield 1000
        state["traversal_path"] = []

    def gen_inorder(node, visit_list):
        if node:
            yield from gen_inorder(node.left, visit_list)
            state["highlight_node"] = node
            state["traversal_path"].append(node)
            visit_list.append(node.value)
            list_str = ", ".join(map(str, visit_list))
            set_status("Traversing...", TEAL_BRIGHT, f"Inorder: [{list_str}]")
            yield TRAVERSE_STEP_MS
            yield from gen_inorder(node.right, visit_list)

    def gen_traverse_wrapper():
        state["traversal_path"] = []
        state["inorder_list"] = []
        if state["root"] is None:
            set_status("Tree is Empty", ORANGE, "root is None")
            yield 1000
            return
        yield from gen_inorder(state["root"], state["inorder_list"])
        state["highlight_node"] = None
        final_str = ", ".join(map(str, state["inorder_list"]))
        set_status(f"Inorder: {final_str}", SUCCESS_COLOR, "Traversal Complete")
        yield POST_TRAVERSE_MS
        state["traversal_path"] = []

    def gen_delete(val, parent=None, current=None, is_left_child=False):
        if current is None:
            if state["root"] is None:
                set_status("Empty Tree", ERROR_COLOR, "Cannot delete from empty tree")
                yield 1000
                return
            current = state["root"]
            parent = None
            state["traversal_path"] = []

        found_target = False
        while current:
            state["highlight_node"] = current
            state["traversal_path"].append(current)

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
            state["traversal_path"] = []
            return

        state["highlight_node"] = current
        state["final_highlight_node"] = current

        # Case 1: Leaf
        if current.left is None and current.right is None:
            set_status("Deleting Leaf", ORANGE, "Leaf node removed")
            yield INSERT_HIGHLIGHT_MS
            if parent is None:
                state["root"] = None
            elif is_left_child:
                parent.left = None
            else:
                parent.right = None
            refresh_layout()
            set_status(f"Deleted: {val}", SUCCESS_COLOR, "Node removed")
            state["final_highlight_node"] = None
            state["highlight_node"] = None
            yield 1000

        # Case 2: One Child (Left)
        elif current.right is None:
            set_status("Deleting Node (1 Child)", ORANGE, "Replace node with left child")
            yield INSERT_HIGHLIGHT_MS
            if parent is None:
                state["root"] = current.left
            elif is_left_child:
                parent.left = current.left
            else:
                parent.right = current.left
            refresh_layout()
            set_status(f"Deleted: {val}", SUCCESS_COLOR, "Structure updated")
            state["final_highlight_node"] = None
            state["highlight_node"] = None
            yield 1000

        # Case 2: One Child (Right)
        elif current.left is None:
            set_status("Deleting Node (1 Child)", ORANGE, "Replace node with right child")
            yield INSERT_HIGHLIGHT_MS
            if parent is None:
                state["root"] = current.right
            elif is_left_child:
                parent.left = current.right
            else:
                parent.right = current.right
            refresh_layout()
            set_status(f"Deleted: {val}", SUCCESS_COLOR, "Structure updated")
            state["final_highlight_node"] = None
            state["highlight_node"] = None
            yield 1000

        # Case 3: Two Children
        else:
            set_status("Deleting Node (2 Children)", ORANGE, "Finding Inorder Successor")
            yield INSERT_HIGHLIGHT_MS
            succ_parent = current
            successor = current.right
            state["traversal_path"].append(successor)
            state["highlight_node"] = successor
            set_status("Visiting Right Child", TEAL_BRIGHT, "Start searching min in right subtree")
            yield TRAVERSE_STEP_MS

            while successor.left:
                succ_parent = successor
                successor = successor.left
                state["traversal_path"].append(successor)
                state["highlight_node"] = successor
                set_status("Go Left", TEAL_BRIGHT, "Seeking minimum...")
                yield TRAVERSE_STEP_MS

            set_status(f"Successor Found: {successor.value}", ORANGE, f"Copy {successor.value} to Node {current.value}")
            state["final_highlight_node"] = successor
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
            state["final_highlight_node"] = None
            state["highlight_node"] = None
            yield 1000
        state["traversal_path"] = []

    # --- AVL ROTATION LOGIC ---

    def rotate_right(y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        return x

    def rotate_left(x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        return y

    def gen_balance_recursive(node):
        if not node:
            return None

        # Post-order traversal: Balance children first
        node.left = yield from gen_balance_recursive(node.left)
        node.right = yield from gen_balance_recursive(node.right)

        # Highlight current node being checked
        state["highlight_node"] = node
        refresh_layout()
        # No yield here allows faster checking of balanced nodes,
        # preventing "press twice" feel for simple traversals.

        bf = get_balance(node)

        # Only pause and animate if there is an issue
        if bf > 1 or bf < -1:
            state["final_highlight_node"] = node
            set_status(f"Imbalance at {node.value}: {bf}", ORANGE, "Rotating...")
            yield 800

            # Left Heavy
            if bf > 1:
                if get_balance(node.left) >= 0:
                    set_status(f"LL Case at {node.value}", TEAL_BRIGHT, "Right Rotate")
                    new_root = rotate_right(node)
                    refresh_layout()  # Physics glide
                    yield ROTATION_MS
                    return new_root
                else:
                    set_status(f"LR Case at {node.value}", TEAL_BRIGHT, "Left Rotate Child...")
                    node.left = rotate_left(node.left)
                    refresh_layout()
                    yield ROTATION_MS

                    set_status(f"LR Case at {node.value}", TEAL_BRIGHT, "Right Rotate Root")
                    new_root = rotate_right(node)
                    refresh_layout()
                    yield ROTATION_MS
                    return new_root

            # Right Heavy
            if bf < -1:
                if get_balance(node.right) <= 0:
                    set_status(f"RR Case at {node.value}", TEAL_BRIGHT, "Left Rotate")
                    new_root = rotate_left(node)
                    refresh_layout()
                    yield ROTATION_MS
                    return new_root
                else:
                    set_status(f"RL Case at {node.value}", TEAL_BRIGHT, "Right Rotate Child...")
                    node.right = rotate_right(node.right)
                    refresh_layout()
                    yield ROTATION_MS

                    set_status(f"RL Case at {node.value}", TEAL_BRIGHT, "Left Rotate Root")
                    new_root = rotate_left(node)
                    refresh_layout()
                    yield ROTATION_MS
                    return new_root

        # No rotation needed for this node
        state["final_highlight_node"] = None
        return node

    def gen_balance():
        if state["root"] is None:
            set_status("Tree is Empty", ERROR_COLOR, "Nothing to balance")
            yield 1000
            return

        set_status("Balancing Tree...", TEAL_BRIGHT, "Bottom-up Check")
        state["root"] = yield from gen_balance_recursive(state["root"])

        refresh_layout()
        state["highlight_node"] = None
        state["final_highlight_node"] = None
        set_status("Balancing Complete", SUCCESS_COLOR, "AVL Property Satisfied")
        yield 1000

    # --- Drawing Functions ---
    def draw_edges(surface, node):
        if node is None: return
        if node.left:
            # Draw actual current positions
            pygame.draw.line(surface, WHITE, (node.x, node.y), (node.left.x, node.left.y), 2)
            draw_edges(surface, node.left)
        if node.right:
            pygame.draw.line(surface, WHITE, (node.x, node.y), (node.right.x, node.right.y), 2)
            draw_edges(surface, node.right)

    def draw_nodes(surface, node):
        if node is None: return

        fill_color = TEAL
        border_color = WHITE

        if node == state["highlight_node"]:
            border_color = TEAL_BRIGHT
            fill_color = TEAL_BRIGHT
        elif node == state["final_highlight_node"]:
            border_color = ORANGE
            fill_color = ORANGE
        elif node in state["traversal_path"]:
            border_color = TEAL_BRIGHT
            fill_color = TEAL_DARK

        # Draw at current physics coordinates
        pygame.draw.circle(surface, fill_color, (int(node.x), int(node.y)), NODE_RADIUS)
        pygame.draw.circle(surface, border_color, (int(node.x), int(node.y)), NODE_RADIUS, NODE_BORDER_WIDTH)

        text_color = WHITE if fill_color in [TEAL, TEAL_BRIGHT, TEAL_DARK, ORANGE] else BLACK
        val_surf = font_elem.render(str(node.value), True, text_color)
        val_rect = val_surf.get_rect(center=(int(node.x), int(node.y)))
        surface.blit(val_surf, val_rect)

        draw_nodes(surface, node.left)
        draw_nodes(surface, node.right)

    def draw_ui(surface):
        title_surf = font_title.render("BST Visualizer", True, TEAL)
        surface.blit(title_surf, (50, 30))

        status_surf = font_ui.render(state["status_message"], True, state["status_color"])
        status_rect = status_surf.get_rect(midtop=(WIDTH // 2 + 100, 30))
        surface.blit(status_surf, status_rect)

        logic_label = font_elem.render("Logic Flow:", True, LIGHT_GREY)
        surface.blit(logic_label, (350, 60))
        logic_surf = font_logic.render(state["logic_message"], True, TEAL_BRIGHT)
        surface.blit(logic_surf, (350, 85))

        input_box.draw(surface)
        for btn in buttons:
            btn.draw(surface)

        if state["root"] is None:
            ph_surf = font_ui.render("Tree is empty.", True, LIGHT_GREY)
            ph_rect = ph_surf.get_rect(center=(WIDTH // 2 + 100, HEIGHT // 2))
            surface.blit(ph_surf, ph_rect)

    def draw_tree(surface):
        draw_edges(surface, state["root"])
        draw_nodes(surface, state["root"])

    # -------------------------------------------------------------------------
    # 5) RUN LOOP
    # -------------------------------------------------------------------------

    running = True
    while running:
        dt = clock.tick(60)
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        # Update Physics every frame for smooth sliding
        update_physics(state["root"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            input_box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not state["current_generator"]:
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            if btn.action_code == "BACK":
                                return "back"

                            if btn.action_code == "CLEAR":
                                state["root"] = None
                                state["traversal_path"] = []
                                state["highlight_node"] = None
                                state["final_highlight_node"] = None
                                set_status("Tree Cleared", SUCCESS_COLOR, "root = None")
                                continue

                            val = None
                            if btn.action_code in ["INSERT", "DELETE", "SEARCH"]:
                                try:
                                    val = int(input_box.text)
                                except ValueError:
                                    set_status("Error: Invalid Input", ERROR_COLOR, "Enter an integer")
                                    continue

                            if btn.action_code == "INSERT":
                                state["current_generator"] = gen_insert(val)
                                input_box.text = ""
                                input_box.txt_surface = font_ui.render("", True, LIGHT_GREY)
                            elif btn.action_code == "DELETE":
                                state["current_generator"] = gen_delete(val)
                                input_box.text = ""
                                input_box.txt_surface = font_ui.render("", True, LIGHT_GREY)
                            elif btn.action_code == "SEARCH":
                                state["current_generator"] = gen_search(val)
                            elif btn.action_code == "TRAVERSE":
                                state["current_generator"] = gen_traverse_wrapper()
                            elif btn.action_code == "BALANCE":
                                state["current_generator"] = gen_balance()

                            state["last_step_time"] = current_time - 2000

        for btn in buttons:
            btn.check_hover(mouse_pos)

        if state["current_generator"]:
            if current_time - state["last_step_time"] >= 0:
                try:
                    wait_ms = next(state["current_generator"])
                    state["last_step_time"] = current_time + wait_ms
                except StopIteration:
                    state["current_generator"] = None
                    state["last_step_time"] = 0
                    state["highlight_node"] = None
        else:
            if current_time >= state["last_step_time"]:
                state["last_step_time"] = 0

        screen.fill(GREY)
        draw_ui(screen)
        draw_tree(screen)
        pygame.display.flip()

    return "back"