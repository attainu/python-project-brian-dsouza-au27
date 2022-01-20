# responsible for handling user input and displaying the current game state object
from re import T
from turtle import color
import pygame as p
import chessEngine

WIDTH = 712
HEIGHT = 712
DIMENSION = 8 # dimension of the board are 8*8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animation
IMAGES = {}

# initialize a global dictionary of images. This will be called exactly once in the main

def loadimages():
    pieces = ['wp','wK', 'wR', 'wN', 'wB', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("image/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

"""
the main driver of the code. this will handle user input and updating the graphics
"""

def main():   
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.Gamestate()
    validmoves = gs.getvalidmoves()
    movemade = False #flag varable for when a move is made
    animate = False #flag var
    loadimages()
    running = True
    sqSelected = () #keep track of last click of user
    playerclick = [] #keep track of player click
    gameover = False
    while running:
        for i in p.event.get():
            if i.type == p.QUIT:
                running = False
            elif i.type == p.MOUSEBUTTONDOWN:
                if not gameover:
                    location = p.mouse.get_pos() #x and y pos of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): #the user clicked the same square twice
                        sqSelected = () #unselect
                        playerclick = [] #clear player clicks
                    else:
                        sqSelected = (row , col)
                        playerclick.append(sqSelected)#append for both 1st and 2nd clicks
                
                    if len(playerclick) == 2: #after 2nd click
                        move = chessEngine.Move(playerclick[0],playerclick[1], gs.board)
                        print(move.getChessNotation())
                        for a in range(len(validmoves)):
                            if move == validmoves[a]:
                                gs.makemove(validmoves[a])
                                movemade = True
                                animate = True
                                sqSelected = () #reset user click
                                playerclick = []
                        if not movemade:
                            playerclick = [sqSelected]
            elif i.type == p.KEYDOWN:
                if i.key == p.K_z: #undo when "z" is pressed
                    gs.undomove()
                    movemade = True
                    animate = False
                if i.key == p.K_r: #reset the board when r is pressed
                    gs = chessEngine.Gamestate()
                    validmoves = gs.getvalidmoves()
                    sqSelected = ()
                    playerclick = []
                    movemade = False
                    animate = False

        if movemade:
            if animate:
               animationmove(gs.moveLog[-1], screen,gs.board, clock)
            validmoves = gs.getvalidmoves()
            movemade = False
            animate = False

        drawGameState(screen, gs, validmoves, sqSelected)
        if gs.checkmate:
            gameover = True
            if gs.whiteToMove:
                drawtext(screen, 'Black wins by checkmate')
            else:
                drawtext(screen , 'white wins ny checkmate')
        elif gs.stalemate:
            gameover = True
            drawtext(screen,'stalemate')
        clock.tick(MAX_FPS)
        p.display.flip()
        
"""
highlight square selected moves
"""

def hightlightSquares(screen,gs,validmoves , sqSelected):
    if sqSelected != ():
        i , j = sqSelected
        if gs.board[i][j][0] == ('w' if gs.whiteToMove else 'b'):
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s,(j*SQ_SIZE, i*SQ_SIZE))
            s.fill(p.Color('black'))
            for move in validmoves:
                if move.startrow == i and move.startcol == j:
                    screen.blit(s, (move.endcol*SQ_SIZE, move.endrow*SQ_SIZE))


"""
responsible for all the graphics within a board
"""
def drawGameState(screen, gs, validmoves, sqselected):

    drawboard(screen)#draw squares on the board
    hightlightSquares(screen,gs,validmoves,sqselected)
    drawpieces(screen, gs.board)

"""
draw the square on the board , the top left square is always light
"""
def drawboard(screen):
    global colors
    colors = [p.Color("white"), p.Color("green")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[((i+j) % 2)]
            p.draw.rect(screen, color, p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
draw the pieces on the board using the current game state.board
"""

def drawpieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animationmove(move, screen , board , clock):
    global colors
    dr = move.endrow-move.startrow
    dc = move.endcol - move.startcol
    frampersquare = 10
    frameCount = (abs(dr)+ abs(dc)) * frampersquare
    for frame in range(frameCount +1):
        r , c = (move.startrow + dr*frame/frameCount,move.startcol + dc*frame/frameCount)
        drawboard(screen)
        drawpieces(screen,board)
        colors = colors[(move.endrow + move.endcol)%2]
        endsquare = p.Rect(move.endcol*SQ_SIZE, move.endrow*SQ_SIZE, SQ_SIZE,SQ_SIZE)
        if move.piececaptured != '--':
            screen.blit(IMAGES[move.piececaptured], endsquare)
        screen.blit(IMAGES[move.piecemoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE , SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)
    
def drawtext(screen ,text):
    font = p.font.SysFont("Helvitca", 32 ,True , False)
    textobject = font.render(text, 0, p.Color('gray'))
    textlocation = p.Rect(0,0 , WIDTH, HEIGHT).move(WIDTH/2 - textobject.get_width()/2, HEIGHT/2 - textobject.get_height()/2)
    screen.blit(textobject, textlocation)
    textobject = font.render(text , 0, p.Color("black"))
    screen.blit(textobject  , textlocation.move(2,2))
if __name__ == "__main__":
    main()


