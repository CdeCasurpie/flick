import pygame
import sys
from renderer import BallRenderer

class Game:
    def __init__(self, screen, balls):
        self.screen = screen
        self.balls = balls
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        self.debug_mode = False
        self.time_scale = 1.0
        self.running = True
        self.width, self.height = screen.get_size()
        self.sim_time = 0.0

    def resolve_collisions(self):
        """Resuelve colisiones y detiene pelotas sin energía para evitar congelamiento."""
        for ball in self.balls:
            # Suelo
            if ball.y + ball.radius >= self.height - ball.epsilon and ball.vy > 0:
                # Si la velocidad es muy baja, la detenemos totalmente (Snap to floor)
                if abs(ball.vy) < 45: 
                    ball.vy = 0
                    ball.y = self.height - ball.radius
                else:
                    ball.vy = -ball.vy * ball.elasticity
            
            # Techo
            elif ball.y - ball.radius <= ball.epsilon and ball.vy < 0:
                ball.vy = -ball.vy * ball.elasticity
            
            # Paredes
            if ball.x + ball.radius >= self.width - ball.epsilon and ball.vx > 0:
                ball.vx = -ball.vx * ball.elasticity
            elif ball.x - ball.radius <= ball.epsilon and ball.vx < 0:
                ball.vx = -ball.vx * ball.elasticity

    def draw_energy_graph(self):
        # Configuración del área de dibujo
        margin_x = 20
        graph_rect = pygame.Rect(self.width - 320, 40, 300, 180)
        pygame.draw.rect(self.screen, (15, 15, 15), graph_rect) # Fondo más profundo
        pygame.draw.rect(self.screen, (100, 100, 100), graph_rect, 1) # Borde

        # Recopilar todos los puntos visibles para calcular escalas
        all_energies = []
        for ball in self.balls:
            history = ball.energy_history[-200:]
            all_energies.extend([e for t, e in history])
        
        if not all_energies: return

        # Calcular límites dinámicos
        max_e = max(all_energies)
        min_e = min(all_energies)
        e_range = max_e - min_e
        
        # Evitar división por cero y escala demasiado pequeña
        if e_range < 10: e_range = max_e * 0.1 if max_e > 0 else 100
        
        # Añadir un margen del 10% arriba y abajo
        padding = e_range * 0.1
        display_max = max_e + padding
        display_min = min_e - padding
        display_range = display_max - display_min

        # Dibujar Cuadrícula y Referencia Inicial
        ref_e = self.balls[0].energy_history[0][1]
        ref_y = graph_rect.bottom - ((ref_e - display_min) / display_range) * graph_rect.height
        if graph_rect.top < ref_y < graph_rect.bottom:
            pygame.draw.line(self.screen, (50, 50, 50), (graph_rect.x, ref_y), (graph_rect.right, ref_y), 1)

        # Etiquetas de valores en el eje Y
        max_label = self.font.render(f"{int(display_max)}J", True, (150, 150, 150))
        min_label = self.font.render(f"{int(display_min)}J", True, (150, 150, 150))
        self.screen.blit(max_label, (graph_rect.x - 45, graph_rect.top))
        self.screen.blit(min_label, (graph_rect.x - 45, graph_rect.bottom - 15))

        for ball in self.balls:
            history = ball.energy_history[-200:]
            if len(history) < 2: continue
            
            min_t = history[0][0]
            max_t = history[-1][0]
            dt = max_t - min_t if max_t > min_t else 1

            points = []
            for t, e in history:
                # Eje X: El tiempo actual llega hasta el 90% del recuadro
                x_ratio = (t - min_t) / dt
                x = graph_rect.x + (x_ratio * 0.9) * graph_rect.width
                
                # Eje Y: Mapeo dinámico
                y_ratio = (e - display_min) / display_range
                y = graph_rect.bottom - y_ratio * graph_rect.height
                
                # Clipping de seguridad
                y = max(graph_rect.top, min(graph_rect.bottom, y))
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(self.screen, ball.color, False, points, 2)

        title = self.font.render("Análisis de Conservación Energética", True, (255, 255, 255))
        self.screen.blit(title, (graph_rect.x, graph_rect.y - 25))

    def run(self):
        while self.running:
            dt_total = (1.0 / 60.0) * self.time_scale
            remaining_dt = dt_total
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F3: self.debug_mode = not self.debug_mode
                    if event.key == pygame.K_r: 
                        for b in self.balls: b.reset()
                        self.sim_time = 0
                    if event.key == pygame.K_UP: self.time_scale += 0.2
                    if event.key == pygame.K_DOWN: self.time_scale = max(0.1, self.time_scale - 0.2)
                    if event.key == pygame.K_ESCAPE: self.running = False

            # Simulación
            max_events = 100
            while remaining_dt > 1e-6 and max_events > 0:
                min_dt = remaining_dt
                collision_ball = None

                for ball in self.balls:
                    toi = ball.find_collision_dt(remaining_dt, self.width, self.height)
                    if toi < min_dt:
                        min_dt = toi
                        collision_ball = ball

                # Avanzar tiempo
                for ball in self.balls:
                    ball.integrate_step(min_dt)
                
                self.sim_time += min_dt
                remaining_dt -= min_dt
                max_events -= 1

                # Resolver si hubo colisión
                if collision_ball or min_dt < 1e-6:
                    self.resolve_collisions()

            # Registrar energía
            for ball in self.balls:
                ball.energy_history.append((self.sim_time, ball.get_energy(self.height)))
                if len(ball.energy_history) > 500: ball.energy_history.pop(0)

            # Render
            self.screen.fill((20, 20, 20))
            for ball in self.balls:
                BallRenderer.render(self.screen, ball, self.debug_mode, self.font)

            if self.debug_mode:
                self.draw_energy_graph()
                info = self.font.render(f"Sim Time: {self.sim_time:.2f}s | Events/frame: {10-max_events}", True, (0, 255, 0))
                self.screen.blit(info, (10, self.height - 20))

            pygame.display.flip()
            self.clock.tick(60)
