import pygame

class BallRenderer:
    @staticmethod
    def render(screen, ball, debug_mode, font):
        # Dibujar la pelota
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)
        
        if debug_mode:
            # Dibujar vector de velocidad
            end_pos = (ball.x + ball.vx * 0.1, ball.y + ball.vy * 0.1)
            pygame.draw.line(screen, (0, 255, 0), (ball.x, ball.y), end_pos, 2)
            
            # Info texto
            debug_text = f"{ball.name}: ({int(ball.vx)}, {int(ball.vy)})"
            text_surface = font.render(debug_text, True, (200, 200, 200))
            screen.blit(text_surface, (ball.x + 20, ball.y - 20))
