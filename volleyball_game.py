import pygame
import sys
import random
import math
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_BOTTOM_RADIUS = 30
PLAYER_TOP_RADIUS = 20
PLAYER_HEIGHT = PLAYER_BOTTOM_RADIUS + PLAYER_TOP_RADIUS  # Total height
BALL_RADIUS = 25
NET_WIDTH = 10
NET_HEIGHT = 300
GRAVITY = 0.5
JUMP_FORCE = -15
PLAYER_SPEED = 6.25  # 1.25x faster
BALL_SPEED = 5.25  # 0.75x slower
WINNING_SCORE = 21
GOAL_TIMEOUT = 1000  # 1 second in milliseconds

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
        self.bottom_radius = PLAYER_BOTTOM_RADIUS
        self.top_radius = PLAYER_TOP_RADIUS
        self.height = PLAYER_HEIGHT
        self.width = PLAYER_BOTTOM_RADIUS * 2  # Width is diameter of bottom circle
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
            if self.x - self.bottom_radius < 0:
                self.x = self.bottom_radius
            elif self.x + self.bottom_radius > SCREEN_WIDTH // 2 - NET_WIDTH // 2:
                self.x = SCREEN_WIDTH // 2 - NET_WIDTH // 2 - self.bottom_radius
        else:
            # Right player can't go beyond the net or right screen edge
            if self.x - self.bottom_radius < SCREEN_WIDTH // 2 + NET_WIDTH // 2:
                self.x = SCREEN_WIDTH // 2 + NET_WIDTH // 2 + self.bottom_radius
            elif self.x + self.bottom_radius > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - self.bottom_radius
    
    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_FORCE
            self.is_jumping = True
    
    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Check if player is on the ground
        if self.y + self.bottom_radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.bottom_radius
            self.vel_y = 0
            self.is_jumping = False
    
    def draw(self):
        # Draw bottom circle (larger)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.bottom_radius)
        
        # Draw top circle (smaller) - positioned on top of the bottom circle
        top_y = self.y - self.bottom_radius - self.top_radius + 5  # +5 for slight overlap
        pygame.draw.circle(screen, self.color, (int(self.x), int(top_y)), self.top_radius)
        
        # Draw eyes (small white circles with black pupils)
        eye_y = top_y - 5
        # Left eye
        pygame.draw.circle(screen, WHITE, (int(self.x - 7), int(eye_y)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.x - 7), int(eye_y)), 2)
        # Right eye
        pygame.draw.circle(screen, WHITE, (int(self.x + 7), int(eye_y)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.x + 7), int(eye_y)), 2)

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
                
            # Show goal message
            show_goal_message(player1, player2)
            
            # Wait for timeout
            pygame.time.delay(GOAL_TIMEOUT)
            
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
        # Check if ball collides with player's bottom circle
        bottom_circle_dist = ((self.x - player.x)**2 + (self.y - player.y)**2)**0.5
        if bottom_circle_dist < BALL_RADIUS + player.bottom_radius:
            
            # Determine collision angle
            dx = self.x - player.x
            dy = self.y - player.y
            angle = math.atan2(dy, dx)
            
            # Set new position outside of collision
            self.x = player.x + math.cos(angle) * (BALL_RADIUS + player.bottom_radius)
            self.y = player.y + math.sin(angle) * (BALL_RADIUS + player.bottom_radius)
            
            # Determine bounce direction based on collision angle
            # Horizontal component
            if abs(math.cos(angle)) > 0.5:  # If hit from sides
                if math.cos(angle) > 0:  # Hit from left
                    self.vel_x = abs(self.vel_x) + random.uniform(0, 2)
                else:  # Hit from right
                    self.vel_x = -abs(self.vel_x) - random.uniform(0, 2)
            
            # Vertical component
            if math.sin(angle) < -0.5:  # Hit from below
                self.vel_y = -abs(self.vel_y) - 5  # Extra upward force when hit from top
            elif math.sin(angle) > 0.5:  # Hit from above
                self.vel_y = abs(self.vel_y)
            
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

def show_goal_message(player1, player2):
    # Determine who scored
    if player1.score > player2.score:
        message = "Player 1 Scores!"
        color = RED
    else:
        message = "Player 2 Scores!"
        color = BLUE
    
    # Draw message
    goal_text = font.render(message, True, color)
    screen.blit(goal_text, (SCREEN_WIDTH // 2 - goal_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    pygame.display.update()

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
    player1 = Player(100, SCREEN_HEIGHT - PLAYER_BOTTOM_RADIUS, RED, True)
    player2 = Player(SCREEN_WIDTH - 100, SCREEN_HEIGHT - PLAYER_BOTTOM_RADIUS, BLUE, False)
    
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
