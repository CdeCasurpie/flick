from ball import Ball

class ExplicitEulerBall(Ball):
    def integrate_step(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt

class ImplicitEulerBall(Ball):
    def integrate_step(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
