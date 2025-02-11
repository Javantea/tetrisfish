import random
import numpy as np

NTSC = 0
PAL = 1

# 8x4 masks for all seven tetronimos to be used in next box


# For main playing field. 4x4x4 (rotation x row x col)
I_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,0,1,0],
        [0,0,1,0],
        [0,0,1,0]
    ]
])

L_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [0,1,1,1],
        [0,1,0,0],
        [0,0,0,0]
    ],
    [
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,1],
        [0,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,0]
    ]
], dtype = np.uint8)

Z_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [0,1,1,0],
        [0,0,1,1],
        [0,0,0,0]
    ],
    [
        [0,0,0,1],
        [0,0,1,1],
        [0,0,1,0],
        [0,0,0,0]
    ]
], dtype = np.uint8)

S_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [0,0,1,1],
        [0,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [0,0,0,0]
    ]
], dtype = np.uint8)

J_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [0,1,1,1],
        [0,0,0,1],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,0,1,0],
        [0,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,1,0,0],
        [0,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,1],
        [0,0,1,0],
        [0,0,1,0],
        [0,0,0,0]
    ]
], dtype = np.uint8)

T_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [0,1,1,1],
        [0,0,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    [
        [0,0,1,0],
        [0,0,1,1],
        [0,0,1,0],
        [0,0,0,0]
    ]
], dtype = np.uint8)

O_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [0,1,1,0],
        [0,1,1,0],
        [0,0,0,0]
    ]
], dtype = np.uint8)


# for nextbox usage
I_PIECEMASK = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
], dtype = np.uint8)

L_PIECEMASK  = np.array([
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
], dtype = np.uint8)

Z_PIECEMASK  = np.array([
    [0, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
], dtype = np.uint8)

S_PIECEMASK  = np.array([
    [0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 0, 0, 0],
], dtype = np.uint8)

J_PIECEMASK  = np.array([
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 0],
], dtype = np.uint8)

T_PIECEMASK  = np.array([
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
], dtype = np.uint8)

O_PIECEMASK  = np.array([
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
], dtype = np.uint8)

TETRONIMO_MASKS = [I_PIECEMASK, L_PIECEMASK, Z_PIECEMASK, S_PIECEMASK, J_PIECEMASK, T_PIECEMASK, O_PIECEMASK]
TETRONIMO_SHAPES = [I_PIECESHAPE, L_PIECESHAPE, Z_PIECESHAPE, S_PIECESHAPE, J_PIECESHAPE, T_PIECESHAPE, O_PIECESHAPE]

I_PIECE  = 0
L_PIECE = 1
Z_PIECE = 2
S_PIECE = 3
J_PIECE = 4
T_PIECE = 5
O_PIECE = 6
NO_PIECE = 7

TETRONIMOS = [I_PIECE, L_PIECE, Z_PIECE, S_PIECE, J_PIECE, T_PIECE, O_PIECE]
TETRONIMO_NAMES = {-1 : "UNDEFINED", None : "None", I_PIECE : "LONGBAR", L_PIECE : "L-PIECE", Z_PIECE : "Z-PIECE", S_PIECE : "S-PIECE", J_PIECE : "J-PIECE", T_PIECE : "T-PIECE", O_PIECE : "O-PIECE"}
TETRONIMO_LETTER = {I_PIECE : "I", L_PIECE : "L", Z_PIECE : "Z", S_PIECE : "S", J_PIECE : "J", T_PIECE : "T", O_PIECE : "O"}
LETTER_TO_PIECE = inv_map = {v: k for k, v in TETRONIMO_LETTER.items()}

# Names of all images used
BOARD = "board"
CURRENT = "current"
NEXT = "next"
LEFTARROW = "leftarrow"
RIGHTARROW = "rightarrow"

LEFTARROW_FAST= "leftarrowfast"
RIGHTARROW_FAST= "rightarrowfast"
LEFTARROW_FAST2= "leftarrowfast2"
RIGHTARROW_FAST2= "rightarrowfast2"

LEFTARROW_MAX = "prevframe"
RIGHTARROW_MAX = "nextframe"
LEFTARROW2_MAX = "prevframe2"
RIGHTARROW2_MAX = "nextframe2"

PANEL = "panel"
STRIPES = "stripes"
LOGO = "tfish"
LOGO2 = "tfish2"

# Mino colors
EMPTY = 0
WHITE_MINO = 1
WHITE_MINO_2 = 4
FIRST_MINO = 3
SECOND_MINO = 2
MINO_COLORS = [WHITE_MINO, WHITE_MINO_2, FIRST_MINO, SECOND_MINO]

START_LEVELS = [9, 12, 15, 18, 19, 29]

# Multiply by 6/5 by PAL. Format is [NTSC, PAL]
timelineNum = [None] * 2
timelineNum[NTSC] = [10, 11, 12, 13, 14, 15, 20, 24, 30]
timelineNum[PAL] = [10, 11, 12.5, 13, 14, 15, 17, 20, 25]

timeline = []
TIMELINE_MAX_HZ = "X."
timeline.append( ["X.....", "X...."] ) # 10, 12hz
timeline.append( ["X.....X....X....", "X....X..."] ) # 11, 13.2hz
timeline.append( ["X....", "X..."] ) # 12,15hz
timeline.append( ["X....X...", "X...X...X...X...X.."] ) # 13, 15.6hz
timeline.append( ["X....X...X...X...", "X...X...X...X...X..X..X.."] ) # 14, 16.8hz
timeline.append( ["X...", "X...X..X.."] ) # 15, 18hz
timeline.append( ["X..", "X.."] ) # 20, 20 (17)
timeline.append( ["X..X.", "X..X."] ) # 24, 24 (20)
timeline.append( [TIMELINE_MAX_HZ,TIMELINE_MAX_HZ] ) # 30 hz NTSC, 25 hz PAL

def getTransitionFromLevel(level):
    if level <= 9:
        return (level+1) * 10
    elif level <= 15:
        return 100
    elif level <= 19:
        return (level - 5) * 10
    elif level == 29:
        return 200
    assert(False)


def colorMinos(minos, piece, white2 = False):

    num = colorOfPiece(piece)

    if num == WHITE_MINO and white2:
        num = WHITE_MINO_2

    return minos.copy() * num
    #return [[i*num for i in row] for row in minos]

def colorOfPiece(piece):

    if piece == L_PIECE or piece == Z_PIECE:
        return SECOND_MINO
    
    elif piece == J_PIECE or piece == S_PIECE:
        return FIRST_MINO
    elif piece == NO_PIECE:
        return EMPTY
    else:
        return WHITE_MINO

# Convert 2d array of pieces to their colors
def colorOfPieces(arr2d):
    return [[colorOfPiece(p) for p in row] for row in arr2d]

def randomPiece():
    return random.choice(TETRONIMOS)

