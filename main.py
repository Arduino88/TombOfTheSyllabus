import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import json

WIDTH = 640
HEIGHT = 640
PADDING = 1
TILE_WIDTH = 9
FPS = 48
GRID_X = 64
GRID_Y = 64
CLI = False
titlePrefix = "TOTS: "

LVL_dir = "levelFiles"
movementQueueMax = 1
debugMode = False

pygame.init()

def loadLevels(dir):
    levels = {}
    for file in os.scandir(dir):
        if file.is_file:
            name = file.name.split(".")[0]
            levels[name] = {}
            with open(f"{dir}/{file.name}", 'r') as f:
                levelData = json.loads(f.read())
                levels[name]["playerSpawn"] = tuple(levelData["playerSpawn"])
                levels[name]["levelMap"] = levelData["levelMap"]
    return levels

LVLs = loadLevels(LVL_dir)

def dprint(x):
    if debugMode: print(x)

def clear():
    os.system("clear")

def setTitle(text, prefix=True):
    pygame.display.set_caption(f"{titlePrefix if prefix else ''}{text}")

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xVel = 0
        self.yVel = 0
        self.moving = False
        self.movementQueue = []
        self.lastMovement = (0,0)
        self.alive = True
        self.won = False
        self.starsCollected = 0

    def addToMovementQueue(self, velDirection):
        if len(self.movementQueue) < movementQueueMax:
            if self.getLastMovement() != velDirection:
                self.lastMovement = velDirection
                self.movementQueue.append(velDirection)

    def getNextMovement(self, perish=False):
        if len(self.movementQueue) == 0:
            return None
        nextMovement = self.movementQueue[0]
        if perish:
            self.movementQueue = self.movementQueue[1:]
        return nextMovement
    
    def getLastMovement(self):
        if len(self.movementQueue) == 0: return self.lastMovement
        return self.movementQueue[len(self.movementQueue)-1]
    
    def consolidateMovementQueue(self):
        nextMovement = self.getNextMovement(perish=True)
        if nextMovement:
            nextMovementX, nextMovementY = nextMovement
            self.xVel += nextMovementX
            self.yVel += nextMovementY
            self.moving = True
    
    def move(self, direction):
        self.addToMovementQueue(direction)

    def up(self):
        self.move(UP)

    def down(self):
        self.move(DOWN)

    def left(self):
        self.move(LEFT)

    def right(self):
        self.move(RIGHT)

    def tick(self, grid):
        dprint(self.movementQueue)
        if not self.moving:
            self.consolidateMovementQueue()
        if self.moving:
            desX = self.x + self.xVel
            desY = self.y + self.yVel
            # self.xVel = 0
            # self.yVel = 0
            legal = False
            if desX<GRID_X and desY<GRID_Y: 
                des = grid[desY][desX]
                if des in [0,4,5] and desX >= 0 and desY >= 0:
                    legal = True
                
                match des:
                    case 4:
                        self.starsCollected += 1
                        grid[desY][desX] = 0
                    case 3:
                        self.alive = False
                    case 5:
                        self.won = True

            if legal:
                self.moving = True
                self.x = desX
                self.y = desY
            else:
                self.moving = False
                self.xVel = 0
                self.yVel = 0
        # self.x += self.xVel
        # if self.x not in range(columns): self.x -= self.xVel
        # self.xVel = 0
        # self.y += self.yVel
        # if self.y not in range(rows): self.y -= self.yVel
        # self.yVel = 0

# class Button():
#     def __init__(self, x, y, width, height, text, bg_colour, text_colour):
#         self.bg_colour = bg_colour
#         self.rect = pygame.Rect(x, y, width, height)

#     def draw(self):
#         pygame.draw.rect(SCREEN, self.bg_colour)

def draw(grid, player, lastFrame=""):
    view = ""
    view += "- - - - - - - - - - -\n"
    
    for rowN, row in enumerate(grid):
        view += "| "
        for tileN, tile in enumerate(row):
            if (tileN, rowN) == (player.x, player.y):
                if player.alive:
                    view += "@"
                    pygame.draw.rect(SCREEN, YELLOW, pygame.Rect(tileN*(TILE_WIDTH+PADDING), rowN*(TILE_WIDTH+PADDING), TILE_WIDTH, TILE_WIDTH))
                else:
                    view += " "
            else: 
                match tile:
                    case 0:
                        view += " "
                    case 2:
                        view += "#"
                        pygame.draw.rect(SCREEN, WHITE, pygame.Rect(tileN*(TILE_WIDTH+PADDING), rowN*(TILE_WIDTH+PADDING), TILE_WIDTH, TILE_WIDTH))
                    case 3:
                        view += "X"
                        pygame.draw.rect(SCREEN, RED, pygame.Rect(tileN*(TILE_WIDTH+PADDING), rowN*(TILE_WIDTH+PADDING), TILE_WIDTH, TILE_WIDTH))
                    case 4:
                        view += "+"
                        pygame.draw.rect(SCREEN, PURPLE, pygame.Rect(tileN*(TILE_WIDTH+PADDING), rowN*(TILE_WIDTH+PADDING), TILE_WIDTH, TILE_WIDTH))
                    case 5:
                        view += "$"
                        pygame.draw.rect(SCREEN, GREEN, pygame.Rect(tileN*(TILE_WIDTH+PADDING), rowN*(TILE_WIDTH+PADDING), TILE_WIDTH, TILE_WIDTH))
                    case _:
                        print(f'Tile {tile} not recognized')
            view += " "
        view += "|"
        view += "\n"
    view += "- - - - - - - - - - -\n"
    if not lastFrame == view and CLI:
        clear()
        print(view)
    return view

## Constants

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (93, 63, 211)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), vsync=1)
CLOCK = pygame.time.Clock()

def init(LVL="1"):
    global grid, p1, controls
    grid = []

    grid = LVLs[LVL]["levelMap"]
    pX, pY = LVLs[LVL]["playerSpawn"]

    # match LVL:
    #     case "0":
    #         grid = [[0, 0, 0, 2, 3, 2, 0, 0, 0], 
    #                 [0, 0, 0, 2, 0, 2, 0, 0, 0], 
    #                 [0, 0, 0, 2, 0, 2, 0, 0, 0], 
    #                 [0, 2, 2, 2, 0, 2, 2, 2, 0], 
    #                 [0, 2, 0, 0, 0, 0, 0, 2, 0], 
    #                 [0, 2, 0, 0, 0, 2, 0, 2, 0], 
    #                 [0, 2, 0, 0, 0, 2, 0, 2, 0], 
    #                 [0, 2, 0, 0, 0, 2, 0, 2, 0], 
    #                 [0, 2, 2, 2, 2, 2, 0, 2, 0]]
    #     case _:
    #         with open(f"levelFiles/{LVL}.json", "r") as f:
    #             levelData = json.loads(f.read())
    #             grid = levelData["levelMap"]
    #             pX, pY = tuple(levelData["playerSpawn"])

    p1 = Player(pX, pY)

    controls = {
        pygame.K_UP: p1.up,
        pygame.K_DOWN: p1.down,
        pygame.K_LEFT: p1.left,
        pygame.K_RIGHT: p1.right,

        pygame.K_w: p1.up,
        pygame.K_s: p1.down,
        pygame.K_a: p1.left,
        pygame.K_d: p1.right
    }

def levelSelect():
    setTitle("Level Select", True)
    while True:
        LEVEL_SELECT_MOUSE_POS = pygame.mouse.get_pos()
        CLOCK.tick(FPS)
        levelList = LVLs.keys()
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONDOWN:
                    pass
                case pygame.QUIT:
                    pygame.quit()
                    exit()
        SCREEN.fill(BLACK)

        for level in levelList:
            pygame.draw.rect(SCREEN, YELLOW, pygame.Rect(int(level)*(30+50), (120), 60, 40))
        pygame.display.flip()
        if CLI:
            levelSelection = input(f"select level ({', '.join(levelList)}): ")
    return levelSelection

def play():
    run = True
    lastFrame=""
    while run and p1.alive and not p1.won:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key in controls.keys():
                controls.get(event.key)()

        p1.tick(grid)
        SCREEN.fill(BLACK)
        
        if CLI: lastFrame = draw(grid, p1, lastFrame)
        else:
            draw(grid, p1)
        pygame.display.flip()
    # if p1.won:

if __name__ == "__main__":
    levelSelect()
    init("3")
    play()
