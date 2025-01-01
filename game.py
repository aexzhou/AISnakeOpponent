from config import *
import random
import queue
import asyncio
from gameEntities import Snake, Prey
from gameGUI import Gui

class Game:
    '''
        Implementation of the main Snake game logic.
    '''
    def __init__(self, gameQueue : queue.Queue, inputQueue : queue.Queue):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.inputQueue = inputQueue
        self.score = 0
        
        self.playerSnake = Snake(
            playable=False,
            spawnDirection="Left",
            spawnCoordinates=[(20*RESOLUTION, 3*RESOLUTION), 
                                 (19*RESOLUTION, 3*RESOLUTION), 
                                 (18*RESOLUTION, 3*RESOLUTION), 
                                 (17*RESOLUTION, 3*RESOLUTION), 
                                 (16*RESOLUTION, 3*RESOLUTION)],
            fillColour=SNAKE_FILL,
            borderColour=SNAKE_BORDER_COLOUR,
            allowedZone=(0,0,WINDOW_WIDTH,WINDOW_HEIGHT),
        )
        self.gameNotOver = True
        self.preyCoordinates = None
        self.createNewPrey()
        # send snake init info over to the gui
        self.queue.put({"move" : self.playerSnake.coordinates}) 
        self.queue.put({"playerDirection" : self.playerSnake.direction})

    async def superloop(self):
        """
            Async main loop of the game, communicates to and fro
            from the GUI using queues.
        """
        SPEED = 0.15  # snake update interval
        while self.gameNotOver:
            self.getPlayerInput()

            if self.playerSnake.move(self.preyCoordinates, [(None)]):
                self.score += 1
                self.queue.put({"score": self.score})
                self.createNewPrey()

            if not self.playerSnake.alive:
                self.endGame()

            self.queue.put({"move": self.playerSnake.coordinates})
            await asyncio.sleep(SPEED)


    def endGame(self) -> None:
        self.gameNotOver = False
        self.queue.put({"game_over"})

    def getPlayerInput(self) -> None:
        try:
            while True:
                task = self.inputQueue.get_nowait()
                if "input" in task:
                    self.playerSnake.direction = task["input"]
                    # print("got player input")
                    self.inputQueue.task_done()
                    return 
        except queue.Empty:
            pass

    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 1*RESOLUTION   # This sets how close the prey can spawn to the border
        while True: # Keep trying to generate coordinates until valid.
            x = random.randrange(THRESHOLD, WINDOW_WIDTH - THRESHOLD, RESOLUTION)
            y = random.randrange(THRESHOLD, WINDOW_HEIGHT - THRESHOLD, RESOLUTION)
            if (x, y) not in self.playerSnake.coordinates:
                break
        self.preyCoordinates = (x, y)
        self.queue.put({"prey" : self.preyCoordinates})


if __name__ == "__main__":
    gameQueue = queue.Queue()
    inputQueue = queue.Queue()
    game = Game(gameQueue, inputQueue)
    gui = Gui(gameQueue, inputQueue)

    async def main():
        try:
            await asyncio.gather(
                game.superloop(),
                gui.getPlayerInput(),
                gui.gui_loop(),
            )
        except KeyboardInterrupt:
            print("Game exited by user.")
        except Exception as e:
            print(f"{e}")

    asyncio.run(main())

