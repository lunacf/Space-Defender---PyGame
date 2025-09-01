"""
SPACE DEFENDER - Juego de naves espaciales
Desarrollado por Carlos Facundo Luna como primer proyecto en Python.
Versión 1.0 - Septiembre 2025
"""

import pygame
import random
import sys
import math

# ================= CONFIGURACIÓN =================
class Config:
    # Ventana
    WIDTH, HEIGHT = 800, 600
    FPS = 60
    TITLE = "Space Defender v1.0"
    
    # Colores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    GREEN = (50, 255, 50)
    BLUE = (50, 100, 255)
    PURPLE = (200, 50, 255)
    YELLOW = (255, 255, 0)
    
    # Velocidades
    PLAYER_SPEED = 7
    BULLET_SPEED = 8
    ENEMY_SPEED = 3
    POWERUP_SPEED = 2
    
    # Gameplay
    INITIAL_SPAWN_RATE = 60  # frames entre enemigos
    DIFFICULTY_INCREASE = 0.95  # reducción de spawn rate por nivel
    MAX_ENEMIES = 10

# ================= ENTIDADES =================
class Bullet:
    def __init__(self, x, y, bullet_type="normal"):
        self.x = x
        self.y = y
        self.type = bullet_type
        
        if bullet_type == "normal":
            self.width = 5
            self.height = 15
            self.speed = Config.BULLET_SPEED
            self.color = Config.GREEN
            self.damage = 1
        else:  # powerup
            self.width = 8
            self.height = 20
            self.speed = Config.BULLET_SPEED + 2
            self.color = Config.PURPLE
            self.damage = 2
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Efecto visual
        if self.type == "powerup":
            pygame.draw.rect(screen, Config.WHITE, 
                           (self.x, self.y, self.width, 5))
    
    def is_off_screen(self):
        return self.y < 0

class Enemy:
    def __init__(self, level=1):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, Config.WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.speed = Config.ENEMY_SPEED + (level * 0.2)
        self.health = level
        self.max_health = level
        self.color = Config.RED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Tipos de enemigos según nivel
        if level >= 3:
            self.color = Config.YELLOW
            self.width = 50
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Barra de vida para enemigos fuertes
        if self.max_health > 1:
            health_width = (self.health / self.max_health) * self.width
            pygame.draw.rect(screen, Config.GREEN, 
                           (self.x, self.y - 5, health_width, 3))
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def is_off_screen(self):
        return self.y > Config.HEIGHT

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = Config.WIDTH // 2 - self.width // 2
        self.y = Config.HEIGHT - 80
        self.speed = Config.PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.bullets = []
        self.cooldown = 0
        self.lives = 3
        self.score = 0
        self.powerup_timer = 0
        self.has_powerup = False
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < Config.WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x
    
    def shoot(self):
        if self.cooldown == 0:
            bullet_type = "powerup" if self.has_powerup else "normal"
            bullet = Bullet(self.x + self.width // 2 - 2, self.y, bullet_type)
            self.bullets.append(bullet)
            self.cooldown = 15 if self.has_powerup else 20
    
    def update(self):
        # Cooldown de disparo
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Duración del powerup
        if self.has_powerup:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.has_powerup = False
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        # Dibujar jugador
        color = Config.PURPLE if self.has_powerup else Config.BLUE
        pygame.draw.rect(screen, color, self.rect)
        
        # Dibujar balas
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # Dibujar vidas
        for i in range(self.lives):
            pygame.draw.rect(screen, Config.GREEN, 
                           (10 + i * 20, Config.HEIGHT - 30, 15, 15))

class PowerUp:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(0, Config.WIDTH - self.width)
        self.y = -30
        self.speed = Config.POWERUP_SPEED
        self.type = random.choice(["life", "weapon"])
        self.color = Config.GREEN if self.type == "life" else Config.PURPLE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Icono según tipo
        if self.type == "life":
            pygame.draw.rect(screen, Config.RED, 
                           (self.x + 10, self.y + 10, 10, 10))
        else:
            pygame.draw.rect(screen, Config.WHITE, 
                           (self.x + 5, self.y + 5, 20, 5))
    
    def is_off_screen(self):
        return self.y > Config.HEIGHT

# ================= JUEGO PRINCIPAL =================
class SpaceDefender:
    def __init__(self):
        # Inicialización
        pygame.init()
        pygame.mixer.init()
        
        # Ventana
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)
        
        # Estados del juego
        self.reset_game()
        
        # Efectos de partículas
        self.particles = []
    
    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.powerups = []
        self.game_over = False
        self.paused = False
        self.level = 1
        self.enemies_destroyed = 0
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.spawn_rate = Config.INITIAL_SPAWN_RATE
        
        # Efectos visuales
        self.screen_shake = 0
        self.flash_effect = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                    self.player.shoot()
                
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        # Movimiento continuo
        if not self.game_over and not self.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move("left")
            if keys[pygame.K_RIGHT]:
                self.player.move("right")
        
        return True

    def update(self):
        if self.paused or self.game_over:
            return
        
        # Actualizar jugador
        self.player.update()
        
        # Generar enemigos
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.spawn_rate and len(self.enemies) < Config.MAX_ENEMIES:
            self.enemies.append(Enemy(self.level))
            self.enemy_spawn_timer = 0
        
        # Generar powerups (5% de chance cada 2 segundos)
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= 120 and random.random() < 0.05:
            self.powerups.append(PowerUp())
            self.powerup_spawn_timer = 0
        
        # Actualizar enemigos
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
        
        # Actualizar powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)
        
        # Verificar colisiones
        self.check_collisions()
        
        # Efectos de pantalla
        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.flash_effect > 0:
            self.flash_effect -= 1
        
        # Aumentar dificultad
        if self.enemies_destroyed >= self.level * 10:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.spawn_rate = max(20, int(self.spawn_rate * Config.DIFFICULTY_INCREASE))
        self.screen_shake = 10
        self.flash_effect = 5

    def check_collisions(self):
        # Colisiones bala-enemigo
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if enemy.take_damage(bullet.damage):
                        self.enemies.remove(enemy)
                        self.player.score += 10 * self.level
                        self.enemies_destroyed += 1
                        self.create_explosion(enemy.x, enemy.y)
                    self.player.bullets.remove(bullet)
                    break
        
        # Colisiones jugador-enemigo
        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                self.player.lives -= 1
                self.screen_shake = 15
                self.enemies.remove(enemy)
                self.create_explosion(enemy.x, enemy.y)
                
                if self.player.lives <= 0:
                    self.game_over = True
        
        # Colisiones jugador-powerup
        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                if powerup.type == "life":
                    self.player.lives = min(5, self.player.lives + 1)
                else:  # weapon
                    self.player.has_powerup = True
                    self.player.powerup_timer = 300  # 5 segundos
                self.powerups.remove(powerup)

    def create_explosion(self, x, y):
        # Crear partículas de explosión
        for _ in range(10):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'size': random.randint(2, 6),
                'color': random.choice([Config.RED, Config.YELLOW, Config.WHITE]),
                'speed': random.uniform(1, 3),
                'angle': random.uniform(0, 2 * math.pi),
                'life': random.randint(20, 40)
            }
            self.particles.append(particle)

    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self):
        # Fondo con efecto de shake
        shake_offset = (random.randint(-self.screen_shake, self.screen_shake), 
                       random.randint(-self.screen_shake, self.screen_shake))
        
        self.screen.fill(Config.BLACK)
        
        # Efecto de flash
        if self.flash_effect > 0:
            self.screen.fill(Config.WHITE, special_flags=pygame.BLEND_ADD)
        
        # Dibujar entidades
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        self.player.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        pygame.display.flip()

    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, Config.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, Config.YELLOW)
        self.screen.blit(level_text, (10, 40))
        
        # Powerup timer
        if self.player.has_powerup:
            timer_text = self.small_font.render(
                f"POWERUP: {self.player.powerup_timer//60}s", True, Config.PURPLE)
            self.screen.blit(timer_text, (Config.WIDTH - 150, 10))
        
        # Game over
        if self.game_over:
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.title_font.render("GAME OVER", True, Config.RED)
            score_text = self.font.render(f"Final Score: {self.player.score}", True, Config.WHITE)
            restart_text = self.font.render("Press R to Restart", True, Config.GREEN)
            
            self.screen.blit(game_over_text, (Config.WIDTH//2 - game_over_text.get_width()//2, 200))
            self.screen.blit(score_text, (Config.WIDTH//2 - score_text.get_width()//2, 270))
            self.screen.blit(restart_text, (Config.WIDTH//2 - restart_text.get_width()//2, 320))
        
        # Paused
        if self.paused:
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            paused_text = self.title_font.render("PAUSED", True, Config.WHITE)
            continue_text = self.font.render("Press P to Continue", True, Config.WHITE)
            
            self.screen.blit(paused_text, (Config.WIDTH//2 - paused_text.get_width()//2, 250))
            self.screen.blit(continue_text, (Config.WIDTH//2 - continue_text.get_width()//2, 310))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.update_particles()
            self.draw()
            self.clock.tick(Config.FPS)
        
        pygame.quit()
        sys.exit()

# ================= EJECUCIÓN =================
if __name__ == "__main__":
    print("🚀 Iniciando Space Defender...")
    print("🎮 Controles:")
    print("   ← → : Movimiento")
    print("   ESPACIO : Disparar")
    print("   P : Pausa")
    print("   R : Reiniciar (game over)")
    print("   ESC : Salir")
    
    game = SpaceDefender()
    game.run()