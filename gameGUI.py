class Gui:
    """
        This class handles all GUI-related processing. 
        It's rendering is controlled by the GameEngine class,
        which contains the main game rendering loop.
    """
    def __init__(self):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial player score.
        """
        # These are some GUI Constants
        self.scoreTextXLocation = 60
        self.scoreTextYLocation = 15
        textColour = (255, 255, 255)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.textColour = textColour
        self.backgroundColor = BACKGROUND_COLOUR 
        # The snakeCoordinates are delivered from the instantiated Game class.
        self.snakeCoordinates = game.playerSnake.coordinates 
        self.preyCoordinates = None
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

    def gameOver(self) -> None:
        """
            Clears the screen and renders the Game Over message 
        """
        game_over_surface = self.font.render("Game Over!", True, self.textColour)
        # Centers this message on screen
        self.screen.blit(game_over_surface, ((WINDOW_WIDTH - game_over_surface.get_width()) // 2,
                                                (WINDOW_HEIGHT - game_over_surface.get_height()) // 2))
        pygame.display.update()