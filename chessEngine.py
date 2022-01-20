from tkinter.messagebox import RETRY


class Gamestate():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunction = {'p': self.getPawnMoves, 'R':self.getRookMoves , 'N': self.getKnightMoves,
                            'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whitekingLoc = (7, 4)
        self.blackkingLoc = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()
    
    def makemove(self, move):
        self.board[move.startrow][move.startcol] = "--"
        self.board[move.endrow][move.endcol]= move.piecemoved
        self.moveLog.append(move) #log the move so we can undo later
        self.whiteToMove = not self.whiteToMove #swap player
        #update king location
        if move.piecemoved == 'wK':
            self.whitekingLoc = (move.endrow, move.endcol)
        elif move.piecemoved == 'bK':
            self.blackkingLoc = (move.endrow, move.endcol)
        #pawn promotion
        if move.ispawnpromotion:
            self.board[move.endrow][move.endcol] = move.piecemoved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.startrow][move.endcol] = '--'
        
        if move.piecemoved[1] == 'p' and abs(move.startrow - move.endrow) == 2:
            self.enpassantPossible = ((move.startrow + move.endrow)//2, move.startcol)
        else:
            self.enpassantPossible = ()

    #undo the last move
    
    def undomove(self):
        if len(self.moveLog)!=0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startrow][move.startcol] = move.piecemoved
            self.board[move.endrow][move.endcol] = move.piececaptured
            self.whiteToMove = not self.whiteToMove #switch turns back 
             #update king location
            if move.piecemoved == 'wK':
                self.whitekingLoc = (move.startrow, move.startcol)
            elif move.piecemoved == 'bK':
                self.blackkingLoc = (move.startrow, move.startcol)
            
            if move.isEnpassantMove:
                self.board[move.startrow][move.startcol] = '--'
                self.board[move.startrow][move.endcol] = move.piececaptured
                self.enpassantPossible = (move.endrow, move.endcol)

            if move.piecemoved[1] == 'p' and abs (move.startrow - move.endrow) ==2:
                self.enpassantPossible = ()


    #all the moves considering checks
    

    def getvalidmoves(self):
        tempEnpassantpossible = self.enpassantPossible
        #generate all possible moves
        moves = self.getAllPossibleMoves()
        #for each move, make a move
        for a in range(len(moves)-1, -1 ,-1):  #when removing from list go backword throught list
            self.makemove(moves[a])
            self.whiteToMove = not self.whiteToMove
            if self.incheck():
                moves.remove(moves[a])  #if they do attack you king , not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undomove()
        if len(moves) == 0: #either checkmate or stalemate
            if self.incheck():
                self.checkmate = True
            else:
                self.stalemate = True
        self.enpassantPossible = tempEnpassantpossible
        return moves


    def incheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whitekingLoc[0], self.whitekingLoc[1])
        else:
            return self.squareUnderAttack(self.blackkingLoc[0], self.blackkingLoc[1])
    

    def squareUnderAttack(self, i, j):
        self.whiteToMove = not self.whiteToMove #switch to opponents turn
        #generate all opponents move
        oppmoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppmoves:
            if move.endrow == i and move.endcol == j: #squar in under attack
                return True
        return False


    def getAllPossibleMoves(self):
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                turn = self.board[i][j][0]
                if(turn == 'w' and self.whiteToMove) or(turn == 'b' and not self.whiteToMove):
                    piece = self.board[i][j][1]
                    self.moveFunction[piece](i,j, moves) #call the appropiate move function based on piece type
        return moves

    def getPawnMoves(self,i,j, moves):
        if self.whiteToMove: # white pawn move
            if self.board[i-1][j] == "--": #1 square pawn advance
                moves.append(Move((i,j),(i-1, j), self.board))
                if i == 6 and self.board[i-2][j] == "--": #2ns square pawn advance
                    moves.append(Move((i,j), (i-2,j), self.board))
            if j-1 >=0:
                if self.board[i-1][j-1][0] == 'b': #enemy piece capture
                    moves.append(Move((i, j), (i-1 , j-1), self.board))
                elif (i-1, j+1) == self.enpassantPossible:
                    moves.append(Move((i, j), (i-1 , j+1), self.board, isEnpassantMove= True))

            if j+1<= 7: #captures to the right
                if self.board[i-1][j+1][0] == 'b':#enemy piece capture
                    moves.append(Move((i,j), (i-1 , j+1),self.board))
                elif (i-1, j-1) == self.enpassantPossible:
                    moves.append(Move((i, j), (i-1 , j-1), self.board, isEnpassantMove= True))

        else:#black pawn moves
            if self.board[i+1][j] == "--": #1 square move
                moves.append(Move((i,j),(i+1, j), self.board))
                if i == 1 and self.board[i+2][j] == "--": #2ns square pawn move
                    moves.append(Move((i,j), (i+2,j), self.board))
                
            #capture        
            if j-1 >=0:    #capture to left
                if self.board[i+1][j-1][0] == 'w': #enemy piece capture
                    moves.append(Move((i, j), (i+1 , j-1), self.board))
                elif (i+1, j-1) == self.enpassantPossible:
                    moves.append(Move((i, j), (i+1 , j-1), self.board, isEnpassantMove= True))
            if j+1<= 7: #captures to the right
                if self.board[i+1][j+1][0] == 'w':#enemy piece capture
                    moves.append(Move((i,j), (i+1 , j+1),self.board))
                elif (i+1, j+1) == self.enpassantPossible:
                    moves.append(Move((i, j), (i+1 , j+1), self.board, isEnpassantMove= True))

    def getRookMoves(self,i,j, moves):
        directions = ((-1,0), (0,-1),(1,0),(0,1))
        enemycolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for a in range(1, 8):
                endrow = i + d[0] * a
                endcol = j +d[1]* a
                if 0<= endrow <8 and 0 <= endcol <8: #on board
                    endpiece = self.board[endrow][endcol]
                    if endpiece == "--":    #empty space valid
                        moves.append(Move((i,j), (endrow, endcol), self.board))
                    elif endpiece[0] == enemycolor:     #enemy piece valid
                        moves.append(Move((i,j), (endrow, endcol), self.board))
                        break
                    else:   #friendly piece valid
                        break
                else:   #off board
                    break

    def getKnightMoves(self,i,j, moves):
        knightmoves = ((-2,-1), (-2,1), (-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allycolor = "w" if self.whiteToMove else "b"
        for m in knightmoves:
            endrow = i + m[0]
            endcol = j +m[1]
            if 0<= endrow <8 and 0 <= endcol <8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0]!= allycolor: #not an ally piece
                    moves.append(Move((i,j), (endrow, endcol), self.board))

    def getBishopMoves(self,i,j, moves):
        directions = ((-1,-1), (-1,1),(1,-1),(1,1))
        enemycolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for a in range(1, 8):
                endrow = i + d[0] * a
                endcol = j +d[1]* a
                if 0<= endrow <8 and 0 <= endcol <8: #on board
                    endpiece = self.board[endrow][endcol]
                    if endpiece == "--":    #empty space valid
                        moves.append(Move((i,j), (endrow, endcol), self.board))
                    elif endpiece[0] == enemycolor:     #enemy piece valid
                        moves.append(Move((i,j), (endrow, endcol), self.board))
                        break
                    else:   #friendly piece valid
                        break
                else:   #off board
                    break


    def getKingMoves(self,i,j, moves):
        kingmoves = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1),( 1,-1), (1,0), (1,1))
        allycolor = "w" if self.whiteToMove else "b"
        for a in range(8):
            endrow = i + kingmoves[a][0]
            endcol = j + kingmoves[a][1]
            if 0 <=endrow < 8 and 0<=endcol <8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != allycolor:     #enemy piece valid
                        moves.append(Move((i,j), (endrow, endcol), self.board))

    def getQueenMoves(self,i,j, moves):
        self.getRookMoves(i,j,moves)
        self.getBishopMoves(i,j, moves)


class Move():
    ranktorows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowstorank = {v:k for k ,v in ranktorows.items()}
    filestocols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colstofiles = {v: k for k, v in filestocols.items()}

    def __init__(self, startsq, endsq, board, isEnpassantMove = False):
        self.startrow = startsq[0]
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.piecemoved = board[self.startrow][self.startcol]
        self.piececaptured = board[self.endrow][self.endcol]
        #pawn promotion
        self.ispawnpromotion = (self.piecemoved =='wp' and self.endrow == 0) or (self.piecemoved == 'bp' and self.endrow == 7)
        
        self.isEnpassantMove =  isEnpassantMove
        if self.isEnpassantMove:
            self.piececaptured = 'wp' if self.piecemoved == 'bp' else 'bp'
            
        self.moveID = self.startrow*1000 + self.startcol *100 + self.endrow *10 + self.endcol
        
    #overriding the equals method

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getrankfile(self.startrow, self.startcol)+ self.getrankfile(self.endrow, self.endcol)

    
    def getrankfile(self, i,j):
        return self.colstofiles[j]+ self.rowstorank[i]
