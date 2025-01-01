import pygame
import queue
import asyncio
from time import sleep
from config import *

class Gui:
    """
        This class handles all GUI-related processing. 
        It's rendering is controlled by the GameEngine class,
        which contains the main game rendering loop.
    """
    def __init__(self, gameQueue : queue.Queue, inputQueue : queue.Queue):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial player score.
        """
        pygame.init()

        self.queue = gameQueue
        self.inputQueue = inputQueue

        # some GUI Constants
        self.scoreTextXLocation = 60
        self.scoreTextYLocation = 15
        textColour = (255, 255, 255)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.textColour = textColour
        self.backgroundColor = BACKGROUND_COLOUR 

        self.preyCoordinates = None
        # get init info from snake
        self.getGameInitInfo()
        
        self.score = 0

        self.screen.fill(self.backgroundColor)

        pygame.display.update() # Update the screen to show the latest staged object results

    """
        The following render* functions are called by the GameEngine class
        inside of the queueHandler method. The queueHandler method also acts as
        the main event loop for rendering the GUI elements.
    """
    def renderSnake(self) -> None:
        """
            Once called by the queueHandler/GUI render loop, this function renders the Snake.
        """
        if self.snakeCoordinates:
            # Draw each segment of the snake as a rectangle
            for coord in self.snakeCoordinates:
                # Stage this object to pygame
                rect = pygame.Rect(coord[0], coord[1], SNAKE_ICON_WIDTH, SNAKE_ICON_WIDTH)
                innerRect = pygame.Rect(coord[0] + SPRITE_BORDER, 
                                        coord[1] + SPRITE_BORDER, 
                                        SNAKE_ICON_WIDTH - 2*SPRITE_BORDER,
                                        SNAKE_ICON_WIDTH - 2*SPRITE_BORDER)
                pygame.draw.rect(self.screen, SNAKE_BORDER_COLOUR, rect)
                pygame.draw.rect(self.screen, SNAKE_FILL, innerRect)

    def renderPrey(self) -> None:
        """
            Once called by the queueHandler/GUI render loop, this function renders the Prey.
        """
        # Render prey and get snake coordinates from the event queue
        if self.preyCoordinates:
            x, y = self.preyCoordinates
            prey_rect = pygame.Rect(x, y, PREY_ICON_WIDTH, PREY_ICON_WIDTH)
            pygame.draw.rect(self.screen, PREY_COLOUR, prey_rect)

    def renderScore(self) -> None:
        """
            Renders the current score on the screen when called.
        """
        # Using blit to overlap this score suurface to the designated background location
        score_surface = self.font.render(f"Your Score: {self.score}", True, self.textColour)
        self.screen.blit(score_surface, (self.scoreTextXLocation, self.scoreTextYLocation))

    def drawScreenGrid(self) -> None:
        for i in range (0, WINDOW_WIDTH, RESOLUTION):
                    pygame.draw.line(self.screen, "blue", [i, 0],[i, WINDOW_HEIGHT],1)
        for j in range (0, WINDOW_HEIGHT, RESOLUTION):
                pygame.draw.line(self.screen, "blue", [0, j],[WINDOW_WIDTH, j],1)

    def gameOver(self) -> None:
        """
            Clears the screen and renders the Game Over message 
        """
        game_over_surface = self.font.render("Game Over!", True, self.textColour)
        # Centers this message on screen
        self.screen.blit(game_over_surface, ((WINDOW_WIDTH - game_over_surface.get_width()) // 2,
                                                (WINDOW_HEIGHT - game_over_surface.get_height()) // 2))
        pygame.display.update() 
        sleep(0.5)
        pygame.quit()

    async def getPlayerInput(self):
        """ 
            Asynchronous detection of player input, only used on the player Snake
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.playerSnakeDirection != "Down":
                        self.playerSnakeDirection = "Up"
                        # print(self.playerSnakeDirection)
                    elif event.key == pygame.K_DOWN and self.playerSnakeDirection != "Up":
                        self.playerSnakeDirection = "Down"
                        # print(self.playerSnakeDirection)
                    elif event.key == pygame.K_LEFT and self.playerSnakeDirection != "Right":
                        self.playerSnakeDirection = "Left"
                        # print(self.playerSnakeDirection)
                    elif event.key == pygame.K_RIGHT and self.playerSnakeDirection != "Left":
                        self.playerSnakeDirection = "Right"
                        # print(self.playerSnakeDirection)
                    self.inputQueue.put({"input": self.playerSnakeDirection}) 
            await asyncio.sleep(0.01)  # delay interval

    def getGameInitInfo(self) -> None:
        gotPlayerDirection : bool = False
        gotSnakeCoordinates : bool = False
        gotPreyCoordinates : bool = False
        
        while True:
            try:
                task = self.queue.get_nowait()
                if "playerDirection" in task:
                    self.playerSnakeDirection = task["playerDirection"]
                    gotPlayerDirection = True
                elif "move" in task:
                    self.snakeCoordinates = task["move"]
                    gotSnakeCoordinates = True
                elif "prey" in task:
                    self.preyCoordinates = task["prey"]
                    gotPreyCoordinates = True

                if gotPlayerDirection and gotSnakeCoordinates \
                    and gotPreyCoordinates:
                    self.queue.task_done()
                    return
            except queue.Empty:
                pass
    
    async def gui_loop(self):
        while True:
            self.screen.fill(self.backgroundColor)
            self.drawScreenGrid()

            try:
                while True:
                    task = self.queue.get_nowait()
                    if "game_over" in task:
                        self.gameOver()
                    elif "move" in task:
                        self.snakeCoordinates = task["move"]
                    elif "prey" in task:
                        self.preyCoordinates = task["prey"]
                    elif "score" in task:
                        self.score = task["score"]
                    self.queue.task_done()
            except queue.Empty:
                pass
            finally:
                self.renderPrey()
                self.renderSnake()
                self.renderScore()
                pygame.display.update()
            await asyncio.sleep(0.016)  # 60 fps







        


             