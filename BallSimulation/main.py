import sys
import tty
import termios
import os
from euler_balls import ExplicitEulerBall, ImplicitEulerBall
from runge_kutta import RK4Ball
from game import Game
import pygame

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
BG_GRAY = "\033[47;30m"

def get_key():
    """Captura una tecla sin necesidad de presionar Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b': # Escape sequence for arrows
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def draw_menu(current_idx, selected_options, options):
    os.system('clear')

    print("Usa las flechas [↑/↓] para navegar y [Enter] para seleccionar.\n")

    for i in range(len(options)):
        prefix = " > " if i == current_idx else "   "
        
        # Color si está seleccionado
        color = GREEN if selected_options[i] else RESET
        mark = "[X]" if selected_options[i] else "[ ]"
        
        # Resaltar si es la opción actual
        style = BG_GRAY if i == current_idx else ""
        
        print(f"{prefix}{style}{mark} {options[i]}{RESET}")

    
    
    # Botones Aceptar / Cancelar
    acc_prefix = " > " if current_idx == 3 else "   "
    can_prefix = " > " if current_idx == 4 else "   "
    
    acc_style = BG_GRAY if current_idx == 3 else ""
    can_style = BG_GRAY if current_idx == 4 else ""
    
    print(f"{acc_prefix}{acc_style}[ ACEPTAR ]{RESET}")
    print(f"{can_prefix}{can_style}{RED}[ CANCELAR ]{RESET}")

def main():
    options = ["Explicit Euler (Rojo)", "Implicit Euler (Azul)", "Runge-Kutta 4 (Amarillo)"]
    selected = [False, False, False]
    current_idx = 0

    while True:
        draw_menu(current_idx, selected, options)
        key = get_key()

        if key == '\x1b[A': # Up
            current_idx = (current_idx - 1) % 5
        elif key == '\x1b[B': # Down
            current_idx = (current_idx + 1) % 5
        elif key == '\r': # Enter
            if current_idx < 3:
                selected[current_idx] = not selected[current_idx]
            elif current_idx == 3: # Aceptar
                if any(selected):
                    start_pygame_simulation(selected)
                else:
                    input("\n¡Selecciona al menos una opción! (Presiona Enter para continuar)")
            elif current_idx == 4: # Cancelar
                print("\nSaliendo...")
                sys.exit()

def start_pygame_simulation(selected):
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Simulación de Física")
    
    balls = []
    start_x, start_y = 200, 400
    start_vx, start_vy = 300, -600
    
    if selected[0]:
        balls.append(ExplicitEulerBall(start_x, start_y, start_vx, start_vy, (255, 50, 50), "Explicit"))
    if selected[1]:
        balls.append(ImplicitEulerBall(start_x, start_y, start_vx, start_vy, (50, 50, 255), "Implicit"))
    if selected[2]:
        balls.append(RK4Ball(start_x, start_y, start_vx, start_vy, (200, 200, 0), "RK4"))
    
    game = Game(screen, balls)
    game.run()
    
    # Al salir de game.run(), volvemos a la consola
    pygame.quit()

if __name__ == "__main__":
    main()
