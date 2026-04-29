from ball import Ball

class RK4Ball(Ball):
    def integrate_step(self, dt):
        if dt <= 0: return

        def get_derivatives(v_val):
            return v_val, self.gravity

        # RK4 para Y
        k1_v, k1_a = get_derivatives(self.vy)
        k2_v, k2_a = get_derivatives(self.vy + k1_a*dt/2)
        k3_v, k3_a = get_derivatives(self.vy + k2_a*dt/2)
        k4_v, k4_a = get_derivatives(self.vy + k3_a*dt)

        self.y += (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        self.vy += (dt / 6.0) * (k1_a + 2*k2_a + 2*k3_a + k4_a)
        
        # X es lineal
        self.x += self.vx * dt
