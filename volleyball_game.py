import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100
BALL_RADIUS = 15
NET_WIDTH = 10
NET_HEIGHT = 300
GRAVITY = 0.5
JUMP_FORCE = -15
PLAYER_SPEED = 5
BALL_SPEED = 7
WINNING_SCORE = 21

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Volleyball Game")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont(None, 36)

class Player:
    def __init__(self, x, y, color, is_left_player):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = color
        self.vel_y = 0
        self.is_jumping = False
        self.is_left_player = is_left_player
        self.score = 0
    
    def move(self, direction):
        # Move left or right
        self.x += direction * PLAYER_SPEED
        
        # Boundary checks
        if self.is_left_player:
            # Left player can't go beyond the net or left screen edge
            if self.x < 0:
                self.x = 0
            elif self.x > SCREEN_WIDTH // 2 - NET_WIDTH // 2 - self.width:
                self.x = SCREEN_WIDTH // 2 - NET_WIDTH // 2 - self.width
        else:
            # Right player can't go beyond the net or right screen edge
            if self.x < SCREEN_WIDTH // 2 + NET_WIDTH // 2:
                self.x = SCREEN_WIDTH // 2 + NET_WIDTH // 2
            elif self.x > SCREEN_WIDTH - self.width:
                self.x = SCREEN_WIDTH - self.width
    
    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_FORCE
            self.is_jumping = True
    
    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Check if player is on the ground
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.is_jumping = False
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 4
        self.vel_x = random.choice([-1, 1]) * BALL_SPEED
        self.vel_y = 0
    
    def update(self, player1, player2):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Bounce off the ceiling
        if self.y - BALL_RADIUS < 0:
            self.y = BALL_RADIUS
            self.vel_y = abs(self.vel_y)
        
        # Check if ball hits the ground
        if self.y + BALL_RADIUS > SCREEN_HEIGHT:
            # Award point to the player on the opposite side
            if self.x < SCREEN_WIDTH // 2:
                player2.score += 1
            else:
                player1.score += 1
            self.reset()
            return
        
        # Bounce off the walls
        if self.x - BALL_RADIUS < 0:
            self.x = BALL_RADIUS
            self.vel_x = abs(self.vel_x)
        elif self.x + BALL_RADIUS > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - BALL_RADIUS
            self.vel_x = -abs(self.vel_x)
        
        # Bounce off the net
        net_left = SCREEN_WIDTH // 2 - NET_WIDTH // 2
        net_right = SCREEN_WIDTH // 2 + NET_WIDTH // 2
        net_top = SCREEN_HEIGHT - NET_HEIGHT
        
        if (self.x + BALL_RADIUS > net_left and self.x - BALL_RADIUS < net_right and 
            self.y + BALL_RADIUS > net_top):
            # Horizontal collision with net
            if self.x < net_left:
                self.x = net_left - BALL_RADIUS
                self.vel_x = -abs(self.vel_x)
            elif self.x > net_right:
                self.x = net_right + BALL_RADIUS
                self.vel_x = abs(self.vel_x)
            # Vertical collision with net
            elif self.y < net_top:
                self.y = net_top - BALL_RADIUS
                self.vel_y = -abs(self.vel_y)
        
        # Collision with players
        self.check_player_collision(player1)
        self.check_player_collision(player2)
    
    def check_player_collision(self, player):
        # Check if ball collides with player
        if (self.x + BALL_RADIUS > player.x and self.x - BALL_RADIUS < player.x + player.width and
            self.y + BALL_RADIUS > player.y and self.y - BALL_RADIUS < player.y + player.height):
            
            # Determine collision side
            dx = (self.x - (player.x + player.width / 2)) / (player.width / 2)
            dy = (self.y - (player.y + player.height / 2)) / (player.height / 2)
            
            # Determine bounce direction based on collision angle
            if abs(dx) > abs(dy):
                # Horizontal collision
                if dx > 0:
                    self.x = player.x + player.width + BALL_RADIUS
                    self.vel_x = abs(self.vel_x) + random.uniform(0, 2)
                else:
                    self.x = player.x - BALL_RADIUS
                    self.vel_x = -abs(self.vel_x) - random.uniform(0, 2)
            else:
                # Vertical collision
                if dy > 0:
                    self.y = player.y + player.height + BALL_RADIUS
                    self.vel_y = abs(self.vel_y)
                else:
                    self.y = player.y - BALL_RADIUS
                    self.vel_y = -abs(self.vel_y) - 5  # Extra upward force when hit from top
            
            # Add some randomness to make the game more interesting
            self.vel_x += random.uniform(-1, 1)
            self.vel_y += random.uniform(-1, 1)
            
            # Cap the velocity to prevent the ball from moving too fast
            max_speed = BALL_SPEED * 1.5
            if abs(self.vel_x) > max_speed:
                self.vel_x = max_speed if self.vel_x > 0 else -max_speed
            if abs(self.vel_y) > max_speed:
                self.vel_y = max_speed if self.vel_y > 0 else -max_speed
    
    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_RADIUS)
        # Add some detail to the ball
        pygame.draw.line(screen, BLACK, (self.x - BALL_RADIUS, self.y), (self.x + BALL_RADIUS, self.y), 1)
        pygame.draw.line(screen, BLACK, (self.x, self.y - BALL_RADIUS), (self.x, self.y + BALL_RADIUS), 1)

def draw_net():
    net_x = SCREEN_WIDTH // 2 - NET_WIDTH // 2
    net_y = SCREEN_HEIGHT - NET_HEIGHT
    pygame.draw.rect(screen, WHITE, (net_x, net_y, NET_WIDTH, NET_HEIGHT))
    
    # Draw net lines
    for y in range(net_y, SCREEN_HEIGHT, 20):
        pygame.draw.line(screen, BLACK, (net_x, y), (net_x + NET_WIDTH, y), 2)

def draw_court():
    # Draw sky
    screen.fill(SKY_BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
    
    # Draw court lines
    pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT - 20), (SCREEN_WIDTH, SCREEN_HEIGHT - 20), 2)
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

def draw_scores(player1, player2):
    # Draw scores
    score1_text = font.render(f"Player 1: {player1.score}", True, RED)
    score2_text = font.render(f"Player 2: {player2.score}", True, BLUE)
    screen.blit(score1_text, (50, 20))
    screen.blit(score2_text, (SCREEN_WIDTH - 200, 20))
    
    # Draw controls info
    controls1 = font.render("Controls: Z, X, C", True, BLACK)
    controls2 = font.render("Controls: ←, →, ↑", True, BLACK)
    screen.blit(controls1, (50, 50))
    screen.blit(controls2, (SCREEN_WIDTH - 250, 50))

def show_winner(player1, player2):
    screen.fill(BLACK)
    if player1.score >= WINNING_SCORE:
        winner_text = font.render("Player 1 Wins!", True, RED)
    else:
        winner_text = font.render("Player 2 Wins!", True, BLUE)
    
    restart_text = font.render("Press SPACE to play again", True, WHITE)
    
    screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    # Create players
    player1 = Player(100, SCREEN_HEIGHT - PLAYER_HEIGHT, RED, True)
    player2 = Player(SCREEN_WIDTH - 100 - PLAYER_WIDTH, SCREEN_HEIGHT - PLAYER_HEIGHT, BLUE, False)
    
    # Create ball
    ball = Ball()
    
    # Game loop
    running = True
    game_over = False
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        if not game_over:
            # Player 1 controls (Z, X, C)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_z]:  # Left
                player1.move(-1)
            if keys[pygame.K_x]:  # Right
                player1.move(1)
            if keys[pygame.K_c]:  # Jump
                player1.jump()
            
            # Player 2 controls (Arrow keys)
            if keys[pygame.K_LEFT]:
                player2.move(-1)
            if keys[pygame.K_RIGHT]:
                player2.move(1)
            if keys[pygame.K_UP]:
                player2.jump()
            
            # Update game objects
            player1.update()
            player2.update()
            ball.update(player1, player2)
            
            # Check for game over
            if player1.score >= WINNING_SCORE or player2.score >= WINNING_SCORE:
                game_over = True
                show_winner(player1, player2)
                # Reset game
                player1.score = 0
                player2.score = 0
                ball.reset()
                game_over = False
        
        # Draw everything
        draw_court()
        draw_net()
        player1.draw()
        player2.draw()
        ball.draw()
        draw_scores(player1, player2)
        
        # Update the display
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
