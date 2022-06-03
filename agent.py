import torch
import numpy
import matplotlib.pyplot as plt
from collections import deque
from game import *
from model import Model, QTrainer

class Memory():
    def __init__(self, maxMemory=100):
        self.memory = []
        self.maxMemory = maxMemory

    def append(self, state, action, reward, nextState, gameOver):
        self.memory.append(state, action, reward, nextState, gameOver)

        if len(self.memory) > self.maxMemory:
            self.memory.pop(0)

class Agent():
    def __init__(self, learningRate, gamma, batchSize=100):
        self.learningRate = learningRate
        self.gamma = gamma
        self.nGames = 0
        self.randomness = 0
        self.batchSize = batchSize
        self.memory = deque(maxlen=100000)
        self.model = Model(8, 256, 4)
        self.trainer = QTrainer(self.model, self.learningRate, self.gamma)
        self.game = SnakeGame()

    def getState(self):

        snakeX = self.game.snake[0].x
        snakeY = self.game.snake[0].y
        foodX = self.game.food.x
        foodY = self.game.food.y

        dangerLeft = 0
        dangerRight = 0
        dangerUp = 0
        dangerDown = 0

        leftSnake = Block(self.game.snake[0].x - BLOCKSIZE, self.game.snake[0].y)
        rightSnake = Block(self.game.snake[0].x + BLOCKSIZE, self.game.snake[0].y)
        upSnake = Block(self.game.snake[0].x, self.game.snake[0].y - BLOCKSIZE)
        downSnake = Block(self.game.snake[0].x, self.game.snake[0].y + BLOCKSIZE)
        for part in self.game.snake[1:]:
            if self.game.isOutOfBounds(leftSnake) or self.game.isCollision(leftSnake, part):
                dangerLeft = 1
            if self.game.isOutOfBounds(rightSnake) or self.game.isCollision(rightSnake, part):
                dangerRight = 1
            if self.game.isOutOfBounds(upSnake) or self.game.isCollision(upSnake, part):
                dangerUp = 1
            if self.game.isOutOfBounds(downSnake) or self.game.isCollision(downSnake, part):
                dangerDown = 1

        return [snakeX, snakeY, foodX, foodY, dangerLeft, dangerRight, dangerUp, dangerDown]

    def getAction(self, state):
        self.randomness = 90 - self.nGames

        action = [0, 0, 0, 0]
        if random.randint(0, 200) < self.randomness:
            move = random.randint(0, 3)
        else:
            prediction = self.model(torch.tensor(state, dtype=torch.float))
            move = torch.argmax(prediction).item()

        action[move] = 1
        return action

    def storeInMemory(self, state, action, reward, nextState, gameOver):
        self.memory.append((state, action, reward, nextState, gameOver))

    def trainShort(self, state, action, reward, nextState, gameOver):
        self.trainer.trainStep(state, action, reward, nextState, gameOver)

    def trainLong(self):
        if len(self.memory) < self.batchSize:
            miniBatch = self.memory
        else:
            miniBatch = random.sample(self.memory, self.batchSize)

        for (state, action, reward, nextState, gameOver) in miniBatch:
            self.trainer.trainStep(state, action, reward, nextState, gameOver)

    def plot(self, scores, meanScores):

        plt.ion()

        plt.clf()
        plt.title("Training")

        plt.plot(scores, color="b")
        plt.plot(meanScores, color="r")
        plt.ylim(ymin=0)

    def humanTest(self):
        self.game.reset()

        while self.game.gameOver == False:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.game.gameStep([1, 0, 0, 0])
                    elif event.key == pygame.K_RIGHT:
                        self.game.gameStep([0, 1, 0, 0])
                    elif event.key == pygame.K_UP:
                        self.game.gameStep([0, 0, 1, 0])
                    elif event.key == pygame.K_DOWN:
                        self.game.gameStep([0, 0, 0, 1])
        while self.game.gameOver:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def train(self):

        self.record = 0
        scores = []
        totalScore = 0
        meanScores = []

        rewards = []

        while True:
            oldState = self.getState()

            action = self.getAction(oldState)

            reward, gameOver, score = self.game.gameStep(action)

            newState = self.getState()

            #self.trainShort(oldState, action, reward, newState, gameOver)
            self.storeInMemory(oldState, action, reward, newState, gameOver)

            self.trainLong()

            rewards.append(reward)

            if self.game.gameOver == True:
                self.trainLong()
                self.nGames += 1
                print("Game: {0}, RewardSum: {1}".format(self.nGames, sum(rewards)))
                rewards = []
                totalScore += score

                scores.append(score)
                meanScores.append((totalScore / self.nGames))
                self.plot(scores, meanScores)

                self.game.reset()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
agent = Agent(0.001, 0.9, batchSize=500)
#agent.humanTest()
agent.train()
