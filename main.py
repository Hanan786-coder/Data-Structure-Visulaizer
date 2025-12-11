import pygame
import sys
import os
import Colors
import random
import importlib.util

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SIDEBAR_WIDTH = 300

BG_COLOR = Colors.GREY
SIDEBAR_COLOR = (30, 30, 35)
TEXT_COLOR = Colors.LIGHT_GREY
BUTTON_COLOR = Colors.TEAL
BUTTON_HOVER = Colors.TEAL_BRIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Data Structure & Algorithm Visualizer")
clock = pygame.time.Clock()


def get_font(size, bold=False):
    try:
        return pygame.font.Font("ScienceGothic-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('Arial', size, bold=bold)


font_header = get_font(40, bold=True)
font_title = get_font(32, bold=True)
font_button = get_font(18, bold=True)
font_small = get_font(14)


class Button:
    def __init__(self, x, y, w, h, text, func, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func = func
        self.base_color = color
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False

    def draw(self, surface):
        col = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        txt = font_button.render(self.text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.func:
                self.func()


DATA_STRUCTURES = [
    ("Singly Linked List", "SinglyLinkedList.py"),
    ("Doubly Linked List", "DoublyLinkedList.py"),
    ("Circular Linked List", "CircularLinkedList.py"),
    ("Stack", "stack_viz.py"),
    ("Queue", "queue_viz.py"),
    ("Circular Queue", "circular_queue_viz.py"),
    ("Binary Tree", "tree2.py"),
]

ALGORITHMS = [
    ("Bubble Sort", "bubble_sort_viz.py", "BubbleSortVisualizer"),
    ("Selection Sort", "SelectionSort.py", "SelectionSortVisualizer"),
    ("Merge Sort", "mergesort.py", "MergeSortTreeVisualizer"),
]


class MainApp:
    def __init__(self):
        self.state = "home"
        self.buttons = []
        self.current_category = None
        self.current_viz = None
        self.viz_class_name = None

    def show_home(self):
        self.state = "home"
        self.current_viz = None
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 80, "Data Structures", self.show_data_structures, Colors.TEAL),
            Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 80, "Algorithms", self.show_algorithms, Colors.ORANGE),
        ]

    def show_data_structures(self):
        self.state = "list"
        self.current_category = "Data Structures"
        self.create_file_buttons(DATA_STRUCTURES)

    def show_algorithms(self):
        self.state = "list"
        self.current_category = "Algorithms"
        self.create_file_buttons(ALGORITHMS)

    def create_file_buttons(self, files):
        self.buttons = []
        y_pos = 180
        for name, filepath in files:
            btn = Button(50, y_pos, SCREEN_WIDTH - 100, 60, name, 
                        lambda f=filepath, n=name: self.load_visualization(f, n), Colors.TEAL)
            self.buttons.append(btn)
            y_pos += 90

        back_btn = Button(SCREEN_WIDTH - 200, 20, 180, 40, "← Back", self.show_home, Colors.ORANGE)
        self.buttons.append(back_btn)

    def load_visualization(self, filepath, name):
        try:
            full_path = os.path.join(os.path.dirname(__file__), filepath)
            
            spec = importlib.util.spec_from_file_location("viz_module", full_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if filepath == "SelectionSort.py":
                self.current_viz = module.SelectionSortVisualizer()
                self.viz_class_name = "SelectionSort"
                self.current_viz.generate_random(5)
            elif filepath == "mergesort.py":
                self.current_viz = module.MergeSortTreeVisualizer()
                self.viz_class_name = "MergeSort"
                self.current_viz.generate_random(6)
            else:
                print(f"Visualization {filepath} not yet integrated")
                return
                
            self.state = "viz"
            self.setup_viz_buttons()
        except Exception as e:
            print(f"Error loading visualization: {e}")
            import traceback
            traceback.print_exc()

    def setup_viz_buttons(self):
        self.buttons = [
            Button(20, 240, 80, 40, "Prev", self.viz_prev, Colors.TEAL),
            Button(110, 240, 80, 40, "Play/||", self.viz_play, Colors.TEAL),
            Button(200, 240, 80, 40, "Next", self.viz_next, Colors.TEAL),
            Button(20, 290, 260, 35, "Reset", self.viz_reset, color=Colors.ORANGE),
            Button(SCREEN_WIDTH - 200, 20, 180, 40, "← Menu", self.show_home, Colors.ORANGE),
        ]
        
        if self.viz_class_name == "SelectionSort":
            self.buttons.insert(3, Button(20, 185, 260, 35, "Min ↓", self.viz_toggle_mode, Colors.ORANGE))
        elif self.viz_class_name == "MergeSort":
            self.buttons.insert(3, Button(20, 170, 260, 35, "Sort: Ascending ↑", self.viz_toggle_mode, Colors.ORANGE))

    def viz_prev(self):
        if self.current_viz:
            self.current_viz.prev_step()
            self.current_viz.playing = False

    def viz_next(self):
        if self.current_viz:
            self.current_viz.next_step()
            self.current_viz.playing = False

    def viz_play(self):
        if self.current_viz:
            self.current_viz.toggle_play()

    def viz_reset(self):
        if self.current_viz:
            self.current_viz.reset()

    def viz_toggle_mode(self):
        if self.current_viz and hasattr(self.current_viz, 'toggle_sort_mode'):
            self.current_viz.toggle_sort_mode()

    def draw_home(self):
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, SIDEBAR_COLOR, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        title = font_header.render("Data Structures & Algorithms", True, Colors.TEAL_BRIGHT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        subtitle = font_small.render("Choose a category to explore visualizations", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(subtitle, subtitle_rect)

        for btn in self.buttons:
            btn.draw(screen)

    def draw_list(self):
        screen.fill(BG_COLOR)

        category_title = font_title.render(self.current_category, True, Colors.TEAL)
        screen.blit(category_title, (50, 40))

        line_y = 120
        pygame.draw.line(screen, Colors.TEAL, (50, line_y), (SCREEN_WIDTH - 50, line_y), 2)

        for btn in self.buttons:
            btn.draw(screen)

    def draw_viz(self):
        if self.current_viz:
            screen.fill(BG_COLOR)
            
            sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
            pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)
            pygame.draw.line(screen, Colors.TEAL, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)
            
            self.current_viz.draw_viz(screen)
            
            for btn in self.buttons:
                btn.draw(screen)

    def draw(self):
        if self.state == "home":
            self.draw_home()
        elif self.state == "list":
            self.draw_list()
        elif self.state == "viz":
            self.draw_viz()

        pygame.display.flip()

    def update(self):
        if self.state == "viz" and self.current_viz:
            if self.viz_class_name == "SelectionSort":
                self.buttons[3].text = "Max ↑" if self.current_viz.sort_mode == "max" else "Min ↓"
            elif self.viz_class_name == "MergeSort":
                self.buttons[3].text = "Sort: Descending ↓" if self.current_viz.sort_mode == "desc" else "Sort: Ascending ↑"
            
            speed_val = 300
            self.current_viz.update(speed_val)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            for btn in self.buttons:
                btn.handle_event(event)
        return True


app = MainApp()
app.show_home()

running = True
while running:
    running = app.handle_events()
    app.update()
    app.draw()
    clock.tick(60)

pygame.quit()
sys.exit()
