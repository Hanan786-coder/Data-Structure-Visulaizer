import pygame
import sys

# -----------------------------------------------------------------------------
# 1) CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------

# Window Dimensions
WIDTH, HEIGHT = 1000, 600

# Color Constants (Explicitly Requested)
ORANGE = (255, 108, 12)  # Highlight / Important
GREY = (57, 62, 70)  # Background
TEAL = (0, 173, 181)  # Default node fill / Primary UI
TEAL_BRIGHT = (0, 200, 210)  # Hover / Path color
BLACK = (43, 40, 49)  # Input background
LIGHT_GREY = (238, 238, 238)  # UI Text / Light elements
WHITE = (255, 255, 255)  # Edges / Accent
ERROR_COLOR = (255, 87, 87)  # Error messages
SUCCESS_COLOR = (0, 200, 81)  # Success messages

# Node Geometry
NODE_RADIUS = 30
NODE_BORDER_WIDTH = 2
LEVEL_GAP = 70  # Vertical distance between levels
START_Y = 150  # Base Y for the Root Node (Adjusted to fit tree nicely)

# Timing Constants (ms)
TRAVERSE_STEP_MS = 800
POST_TRAVERSE_MS = 1000
INSERT_HIGHLIGHT_MS = 1200
FOUND_HIGHLIGHT_MS = 1200


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


# Global Tree State
root = None

# Global Animation/UI State
current_generator = None  # The active operation generator
last_step_time = 0  # Timestamp of last animation step
status_message = "Ready"
status_color = LIGHT_GREY
logic_message = ""
traversal_path = []  # List of nodes visited in current op
highlight_node = WHITE  # Node currently being processed/highlighted
final_highlight_node = None  # Node to show in ORANGE at end of op
highlight_start_time = 0  # Timer for static highlights
inorder_list = []  # For storing inorder results

# -----------------------------------------------------------------------------
# 3) PYGAME SETUP & UI CLASSES
# -----------------------------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Data Structure Visualizer")


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
                    pass  # Handled by buttons usually
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Numeric only constraint
                    if event.unicode.isnumeric():
                        self.text += event.unicode
                self.txt_surface = font_ui.render(self.text, True, LIGHT_GREY)

    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=8)
        # Border
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=8)
        # Text
        surface.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))


# UI Elements Initialization
input_box = InputBox(50, 150, 140, 40)
buttons = [
    Button(50, 210, 140, 40, "Insert", "INSERT"),
    Button(50, 260, 140, 40, "Delete", "DELETE"),
    Button(50, 310, 140, 40, "Search", "SEARCH"),
    Button(50, 360, 140, 40, "Traverse", "TRAVERSE"),
    Button(50, 410, 140, 40, "Clear Tree", "CLEAR")
]


# -----------------------------------------------------------------------------
# 4) HELPER FUNCTIONS (Layout & Logic)
# -----------------------------------------------------------------------------

def set_status(msg, color, logic=""):
    global status_message, status_color, logic_message
    status_message = msg
    status_color = color
    logic_message = "> " + logic if logic else ""


def update_positions(node, x_min, x_max, depth, y_base, level_gap):
    """
    Deterministic recursive positional layout.
    x_min/x_max: current horizontal span.
    """
    if not node:
        return

    # Center this node in current span
    mid_x = (x_min + x_max) // 2
    node.x = mid_x
    node.y = y_base + (depth * level_gap)

    # Recurse
    update_positions(node.left, x_min, mid_x, depth + 1, y_base, level_gap)
    update_positions(node.right, mid_x, x_max, depth + 1, y_base, level_gap)


def get_node_at_pos(pos):
    """Check if mouse click is on a node (optional interaction)."""
    # Just a helper, mainly for debug or future expansion
    pass


def refresh_layout():
    # Tree area spans roughly from x=300 to x=WIDTH
    update_positions(root, 300, WIDTH, 0, START_Y, LEVEL_GAP)


def find_min_node(node):
    current = node
    while current.left is not None:
        current = current.left
    return current


# -----------------------------------------------------------------------------
# 5) GENERATOR ALGORITHMS (Animation Logic)
# -----------------------------------------------------------------------------
# These functions yield control back to main loop to allow animation steps.

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

        else:  # val > curr.value
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

    # Cleanup
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
    """Recursive helper generator for inorder traversal"""
    global highlight_node, traversal_path

    if node:
        # Go Left
        yield from gen_inorder(node.left, visit_list)

        # Visit Node
        highlight_node = node
        traversal_path.append(node)  # Add to visual path for connection
        visit_list.append(node.value)

        # Update logic display list
        list_str = ", ".join(map(str, visit_list))
        set_status("Traversing...", TEAL_BRIGHT, f"Inorder: [{list_str}]")

        yield TRAVERSE_STEP_MS

        # Go Right
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
    """
    Complex generator for deletion.
    It handles Search -> Logic -> Structure Change.
    To support recursion with animation, we pass parent/current context.
    If called initially, parent/current are derived from root.
    """
    global root, highlight_node, final_highlight_node, traversal_path

    # 1. Initialization (Start at root if not recursive call)
    if current is None:
        if root is None:
            set_status("Empty Tree", ERROR_COLOR, "Cannot delete from empty tree")
            yield 1000
            return
        current = root
        parent = None
        traversal_path = []  # Reset path on fresh start

    # 2. Search Phase (only if we haven't 'found' it yet conceptually)
    # However, since this is recursive-like, we handle the 'step' here.

    found_target = False

    # We loop to find the node (Search animation)
    # Note: If this is a recursive call for successor deletion, current is already the target.
    # But for the initial call, we need to walk down.

    # To simplify the generator structure for 2-child case, we implement an iterative search first
    # then handle the deletion logic.

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

    # 3. Deletion Logic (Case handling)

    highlight_node = current  # Keep it highlighted
    final_highlight_node = current  # Orange highlight for target

    # Case 1: Leaf Node
    if current.left is None and current.right is None:
        set_status("Deleting Leaf", ORANGE, "Leaf node removed")
        yield INSERT_HIGHLIGHT_MS  # Pause to show selection

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
        set_status("Deleting Node (2 Children)", ORANGE, "Finding inorder successor (Min of Right Subtree)")
        yield INSERT_HIGHLIGHT_MS

        # Animate finding successor
        succ_parent = current
        successor = current.right
        # Visual path to successor needs to be shown.
        # We append to traversal_path visually

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

        # Successor found
        set_status(f"Successor Found: {successor.value}", ORANGE, f"Copy {successor.value} to Node {current.value}")
        final_highlight_node = successor  # Highlight successor in Orange
        yield 1200

        # Perform Value Copy
        current.value = successor.value
        # Temporarily clear highlight to show the 'copy' effect visually if we wanted,
        # but the text explains it.

        # Now we must delete the successor
        # The successor is guaranteed to have 0 or 1 child (right child)
        set_status("Removing Successor", TEAL_BRIGHT, "delete(successor)")
        yield 500

        # Structural removal of successor
        if succ_parent == current:
            succ_parent.right = successor.right
        else:
            succ_parent.left = successor.right

        refresh_layout()
        set_status(f"Deleted Original: {val}", SUCCESS_COLOR, "two children: node.val = succ.val; delete(succ)")
        final_highlight_node = None
        highlight_node = None
        yield 1000

    traversal_path = []


# -----------------------------------------------------------------------------
# 6) MAIN DRAWING FUNCTIONS
# -----------------------------------------------------------------------------

def draw_tree(surface):
    # Draw Edges first
    draw_edges(surface, root)
    # Draw Nodes
    draw_nodes(surface, root)


def draw_edges(surface, node):
    if node is None:
        return

    if node.left:
        # Check if this edge is part of traversal path
        color = WHITE
        width = 4
        # If both nodes in traversal path and connected in sequence, highlight edge
        if node in traversal_path and node.left in traversal_path:
            # Basic check: is node.left the next one in list?
            try:
                idx = traversal_path.index(node)
                if idx + 1 < len(traversal_path) and traversal_path[idx + 1] == node.left:
                    color = TEAL_BRIGHT
                    width = 4
            except:
                pass

        start = (node.x, node.y)
        end = (node.left.x, node.left.y)
        pygame.draw.line(surface, color, start, end, width)
        draw_edges(surface, node.left)

    if node.right:
        color = WHITE
        width = 2
        if node in traversal_path and node.right in traversal_path:
            try:
                idx = traversal_path.index(node)
                if idx + 1 < len(traversal_path) and traversal_path[idx + 1] == node.right:
                    color = TEAL_BRIGHT
                    width = 4
            except:
                pass

        start = (node.x, node.y)
        end = (node.right.x, node.right.y)
        pygame.draw.line(surface, color, start, end, width)
        draw_edges(surface, node.right)


def draw_nodes(surface, node):
    if node is None:
        return

    # Default Colors
    fill_color = TEAL
    border_color = WHITE

    # 1. Current Active Node (The one moving right now)
    if node == highlight_node:
        border_color = TEAL_BRIGHT
        fill_color = TEAL_BRIGHT  # Bright active color

    # 2. Final Result Node (Found target / New insert)
    elif node == final_highlight_node:
        border_color = ORANGE
        fill_color = ORANGE

    # 3. Path History (Nodes we have passed through)
    elif node in traversal_path:
        border_color = TEAL_BRIGHT
        # CHANGE THIS LINE below to fill the node:
        fill_color = (0, 140, 145)  # A slightly darker Teal to show "history"
        # OR use 'fill_color = TEAL_BRIGHT' to make them look exactly like the active node

    # Draw Circle
    pygame.draw.circle(surface, fill_color, (node.x, node.y), NODE_RADIUS)
    pygame.draw.circle(surface, border_color, (node.x, node.y), NODE_RADIUS, NODE_BORDER_WIDTH)

    # Draw Value
    # Ensure text remains readable against the new fill colors
    text_color = WHITE if fill_color in [TEAL, TEAL_BRIGHT, (0, 140, 145), ORANGE] else BLACK

    val_surf = font_elem.render(str(node.value), True, text_color)
    val_rect = val_surf.get_rect(center=(node.x, node.y))
    surface.blit(val_surf, val_rect)

    draw_nodes(surface, node.left)
    draw_nodes(surface, node.right)

def draw_ui(surface):
    # Left Panel Background (Implicit by clearing screen with GREY, but can darken left side)
    # pygame.draw.rect(surface, (50, 55, 65), (0, 0, 250, HEIGHT))

    # Title
    title_surf = font_title.render("BST Visualizer", True, TEAL)
    surface.blit(title_surf, (50, 30))

    # Status Area
    status_surf = font_ui.render(status_message, True, status_color)
    # Center status horizontally roughly
    status_rect = status_surf.get_rect(midtop=(WIDTH // 2 + 100, 30))
    surface.blit(status_surf, status_rect)

    # Logic Flow Area
    logic_label = font_elem.render("Logic Flow:", True, LIGHT_GREY)
    surface.blit(logic_label, (350, 60))

    logic_surf = font_logic.render(logic_message, True, TEAL_BRIGHT)
    surface.blit(logic_surf, (350, 85))

    # Controls
    input_box.draw(surface)
    for btn in buttons:
        btn.draw(surface)

    # Tree Area Placeholder if empty
    if root is None:
        ph_surf = font_ui.render("Tree is empty. Insert a value.", True, LIGHT_GREY)
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
        dt = clock.tick(60)  # 60 FPS
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            input_box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Button Clicks
                if not current_generator:  # Disable buttons while animating
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            # Parse Input
                            val = None
                            if btn.action_code in ["INSERT", "DELETE", "SEARCH"]:
                                try:
                                    val = int(input_box.text)
                                except ValueError:
                                    set_status("Error: Invalid Input", ERROR_COLOR, "Enter an integer")
                                    continue

                            # Dispatch Action
                            if btn.action_code == "INSERT":
                                current_generator = gen_insert(val)
                            elif btn.action_code == "DELETE":
                                current_generator = gen_delete(val)
                            elif btn.action_code == "SEARCH":
                                current_generator = gen_search(val)
                            elif btn.action_code == "TRAVERSE":
                                current_generator = gen_traverse_wrapper()
                            elif btn.action_code == "CLEAR":
                                root = None
                                traversal_path = []
                                highlight_node = None
                                final_highlight_node = None
                                set_status("Tree Cleared", SUCCESS_COLOR, "root = None")

                            # Reset timer for immediate start
                            last_step_time = current_time - 2000

                            # --- Update State (Hover) ---
        for btn in buttons:
            btn.check_hover(mouse_pos)

        # --- Animation Step ---
        if current_generator:
            # Check if it's time for the next step
            # The generator yields the duration to wait *before* the next step
            # We treat the yielded value as the delay required for the current state to be visible

            # Note: We need a mechanism to know the delay requested by the *previous* yield.
            # We'll store `wait_time` from the yield.

            # Initial Call
            if last_step_time == 0:
                # This logic is slightly tricky with generators.
                # Strategy: execute next step immediately if sufficient time passed since last step.
                pass

            if current_time - last_step_time >= 0:  # 0 is placeholder, real wait is controlled below
                try:
                    # Execute next step
                    wait_ms = next(current_generator)
                    # Update the time marker to now + wait_ms
                    # So the loop won't enter here again until wait_ms passes
                    last_step_time = current_time + wait_ms
                    # We subtract current_time in the check, so condition is:
                    # (current_time > last_step_time) where last_step_time = now + delay
                    # Let's adjust logic:
                    # last_step_time will represent "Time when we can run next step"
                except StopIteration:
                    current_generator = None
                    last_step_time = 0
                    highlight_node = None
                    # Keep status message

        else:
            # Idle logic checks
            # If wait time is pending (e.g. from last yield of generator), wait it out
            if current_time < last_step_time:
                pass
            else:
                last_step_time = 0

        # Override logic for timer:
        # If current_generator is active, we only call next() if current_time >= last_step_time

        # --- Drawing ---
        screen.fill(GREY)

        draw_ui(screen)

        # Calculate positions again just in case (though usually done in logic)
        # Doing it every frame is cheap for small trees and ensures smooth updates if we added dragging later
        # update_positions(root, 300, WIDTH, 0, START_Y, LEVEL_GAP)

        draw_tree(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()