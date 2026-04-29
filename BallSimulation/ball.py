from abc import ABC, abstractmethod
import math

class Ball(ABC):
    def __init__(self, x, y, vx, vy, color, name):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.name = name
        self.radius = 15
        self.initial_state = (x, y, vx, vy)
        self.gravity = 900
        self.elasticity = 1.0   # Rebote perfectamente elástico para conservar energía
        self.mass = 1.0
        self.epsilon = 0.05     # Margen de colisión para el resolvedor
        
        # Datos para telemetría
        self.energy_history = [] # Lista de (tiempo, energia)
        self._saved_state = None

    def save_state(self):
        self._saved_state = (self.x, self.y, self.vx, self.vy)

    def restore_state(self):
        self.x, self.y, self.vx, self.vy = self._saved_state

    def get_energy(self, screen_height):
        # Ek = 1/2 * m * v^2
        v2 = self.vx**2 + self.vy**2
        ek = 0.5 * self.mass * v2
        
        # Ep = m * g * h (En Pygame h es screen_height - y)
        h = max(0, screen_height - self.y - self.radius)
        ep = self.mass * self.gravity * h
        return ek + ep

    def is_colliding(self, width, height):
        """Verifica si la pelota está penetrando algún límite (considerando dirección)."""
        if self.y + self.radius > height and self.vy > 0: return True
        if self.y - self.radius < 0 and self.vy < 0: return True
        if self.x + self.radius > width and self.vx > 0: return True
        if self.x - self.radius < 0 and self.vx < 0: return True
        return False

    def find_collision_dt(self, max_dt, width, height):
        """Busca el tiempo máximo seguro (ToI) usando búsqueda binaria."""
        if max_dt <= 1e-7: return 0.0
        
        self.save_state()
        
        # Si ya está colisionando, no puede avanzar nada
        if self.is_colliding(width, height):
            self.restore_state()
            return 0.0

        low = 0.0
        high = max_dt
        
        for _ in range(10):
            mid = (low + high) / 2
            self.restore_state()
            self.integrate_step(mid)
            
            if self.is_colliding(width, height):
                high = mid
            else:
                low = mid
        
        self.restore_state()
        return low

    def reset(self):
        self.x, self.y, self.vx, self.vy = self.initial_state
        self.energy_history = []

    @abstractmethod
    def integrate_step(self, dt):
        pass
