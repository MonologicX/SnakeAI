import pygame
import random
import math
import sys

WINWIDTH, WINHEIGHT = (600, 600)
FPS = 120

#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKRED = (139, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 139)

BLOCKSIZE = 30

class Block:
    def __init__(self, x, y, border=True, borderColor=WHITE):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        self.border = border
        if self.border:
            self.borderColor = borderColor
            self.borderTop = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE / 10)
            self.borderLeft = pygame.Rect(self.x, self.y, BLOCKSIZE / 10, BLOCKSIZE)
            self.borderBottom = pygame.Rect(self.x, self.y + (BLOCKSIZE - BLOCKSIZE / 10), BLOCKSIZE, BLOCKSIZE / 10)
            self.borderRight = pygame.Rect(self.x + (BLOCKSIZE - BLOCKSIZE / 10), self.y, BLOCKSIZE / 10, BLOCKSIZE)

    def updateRect(self):
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        if self.border:
            self.borderTop = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE / 10)
            self.borderLeft = pygame.Rect(self.x, self.y, BLOCKSIZE / 10, BLOCKSIZE)
            self.borderBottom = pygame.Rect(self.x, self.y + (BLOCKSIZE - BLOCKSIZE / 10), BLOCKSIZE, BLOCKSIZE / 10)
            self.borderRight = pygame.Rect(self.x + (BLOCKSIZE - BLOCKSIZE / 10), self.y, BLOCKSIZE / 10, BLOCKSIZE)

    def drawBorder(self, WIN, color=None):
        if self.border:
            if color != None:
                self.borderColor = color
            pygame.draw.rect(WIN, self.borderColor, self.borderTop)
            pygame.draw.rect(WIN, self.borderColor, self.borderLeft)
            pygame.draw.rect(WIN, self.borderColor, self.borderBottom)
            pygame.draw.rect(WIN, self.borderColor, self.borderRight)

class SnakeGame:
    def __init__(self, startLength=3):
        pygame.init()

        pygame.display.set_caption("SnakeAI")
        self.FONT = pygame.font.SysFont('Sans', 15)
        self.WIN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
        self.clock = pygame.time.Clock()

        self.startLength = startLength
        self.snake = [Block(WINWIDTH / 2, WINHEIGHT / 2)]
        for i in range(1, self.startLength):
            self.snake.append(Block((self.snake[-1].x - BLOCKSIZE), self.snake[-1].y))

        self.food = Block(math.floor(random.randrange(0, (WINWIDTH - BLOCKSIZE), BLOCKSIZE)), math.floor(random.randrange(0, (WINHEIGHT - BLOCKSIZE), BLOCKSIZE)))
        self.gameOver = False
        self.score = 0
        self.frames = 0
        self.lastFoodDist = (((self.snake[0].x - self.food.x)**2) + ((self.snake[0].y - self.food.y)**2))**(1/2)

    def gameStep(self, action):

        #Move
        self.move(action)


        reward = 0
        foodDist = (((self.snake[0].x - self.food.x)**2) + ((self.snake[0].y - self.food.y)**2))**(1/2)
        if self.lastFoodDist > float(foodDist):
            reward += 1

        self.lastFoodDist = float(foodDist)
        #Check for Game Over
        if self.isOutOfBounds(self.snake[0]):
            reward = -100
            self.gameOver = True
            return reward, self.gameOver, self.score
        for part in self.snake[1:]:
            if self.isCollision(self.snake[0], part):
                reward = -100
                self.gameOver = True
                return reward, self.gameOver, self.score

        #Check for Food
        for part in self.snake:
            if self.isCollision(part, self.food):
                self.score += 1
                reward = 1000
                self.food = Block(math.floor(random.randrange(0, (WINWIDTH - BLOCKSIZE), BLOCKSIZE)), math.floor(random.randrange(0, (WINHEIGHT - BLOCKSIZE), BLOCKSIZE)))
                self.snake.append(Block(self.snake[-1].x - BLOCKSIZE, self.snake[-1].y))

        self.draw()
        self.clock.tick(FPS)
        self.frames += 1

        return reward, self.gameOver, self.score

    def move(self, action):

        #Action Code [LEFT, RIGHT, UP, DOWN]
        for part in self.snake[::-1]:
            if self.snake.index(part) != 0:
                part.x = self.snake[self.snake.index(part) - 1].x
                part.y = self.snake[self.snake.index(part) - 1].y

        if action[0] == 1:
            self.snake[0].x -= BLOCKSIZE
        elif action[1] == 1:
            self.snake[0].x += BLOCKSIZE
        elif action[2] == 1:
            self.snake[0].y -= BLOCKSIZE
        elif action[3] == 1:
            self.snake[0].y += BLOCKSIZE

    def draw(self):

        self.WIN.fill(BLACK)

        for part in self.snake:
            part.updateRect()
            pygame.draw.rect(self.WIN, BLUE, part.rect)
            part.drawBorder(self.WIN, color=DARKBLUE)

        self.food.updateRect()
        pygame.draw.rect(self.WIN, RED, self.food.rect)
        self.food.drawBorder(self.WIN, color=DARKRED)

        scoreMessage = self.FONT.render("Score: {0}".format(self.score), True, WHITE)
        self.WIN.blit(scoreMessage, scoreMessage.get_rect(center=(WINWIDTH / 2, WINHEIGHT / 10)))

        pygame.display.update()

    def reset(self):
        self.snake = [Block(WINWIDTH / 2, WINHEIGHT / 2)]
        for i in range(1, self.startLength):
            self.snake.append(Block((self.snake[-1].x - BLOCKSIZE), self.snake[-1].y))

        self.food = Block(math.floor(random.randrange(0, (WINWIDTH - BLOCKSIZE), BLOCKSIZE)), math.floor(random.randrange(0, (WINHEIGHT - BLOCKSIZE), BLOCKSIZE)))
        self.gameOver = False
        self.score = 0
        self.lastFoodDist = (((self.snake[0].x - self.food.x)**2) + ((self.snake[0].y - self.food.y)**2))**(1/2)

    def isOutOfBounds(self, snakeHead):

        if (snakeHead.x > (WINWIDTH - BLOCKSIZE)) or (snakeHead.x < 0):
            return True
        if (snakeHead.y > (WINHEIGHT - BLOCKSIZE)) or (snakeHead.y < 0):
            return True

        return False

    def isCollision(self, blockA, blockB):

        if blockB.rect.collidepoint((blockA.x, blockA.y)):
            return True
        else:
            return False

    def humanTest(self):
        self.reset()

        while self.gameOver == False:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.gameStep([1, 0, 0, 0])
                    elif event.key == pygame.K_RIGHT:
                        self.gameStep([0, 1, 0, 0])
                    elif event.key == pygame.K_UP:
                        self.gameStep([0, 0, 1, 0])
                    elif event.key == pygame.K_DOWN:
                        self.gameStep([0, 0, 0, 1])

            self.draw()
        while self.gameOver == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.draw()
