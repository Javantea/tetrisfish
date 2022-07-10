#!/usr/bin/env python3
"""
Piece Sequence and Drought Information
by Javantea
July 9, 2022

"""
import ast
import binascii
import base64
import numpy as np
import PieceMasks as PM

# TODO: optimization, remove piece masks and padding.

I_PIECESHAPE = np.array([
    [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    [
        [0,1,0,0],
        [0,1,0,0],
        [0,1,0,0],
        [0,1,0,0]
    ],
    [
        [0,0,1,0],
        [0,0,1,0],
        [0,0,1,0],
        [0,0,1,0]
    ]
])

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
        [0,1,0,0],
        [0,1,1,0],
        [0,1,0,0],
        [0,0,0,0]
    ]
], dtype = np.uint8)
TETRONIMO_SHAPES = [I_PIECESHAPE, PM.L_PIECESHAPE, PM.Z_PIECESHAPE, PM.S_PIECESHAPE, PM.J_PIECESHAPE, T_PIECESHAPE, PM.O_PIECESHAPE]

# From SaveAnalysis.
# Take encoded string, return nparray.
def decodeArray(string):
    """
    Convert AAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAYAg== to a 20x10 board.
    """

    b = base64.decodebytes(string)
    int8 = np.frombuffer(b, dtype=np.uint8)
    decoded = np.unpackbits(int8).reshape(20,10).astype(np.uint8)
    #print(decoded.dtype)
    return decoded

def compare(piece_rot, data, verbose=False):
    """
    compare two arrays with similar size
    TODO: Test with a lot of pieces.
    """
    if piece_rot.shape != data.shape:
        #print('diff size', piece_rot.shape, data.shape)
        return False
    if verbose: print('compare')
    if verbose: print(piece_rot)
    if verbose: print(data)
    for i in range(len(piece_rot)):
        for j in range(len(piece_rot[i])):
            if piece_rot[i][j] != data[i][j]: return False
    return True

def findPiece(place, piece_rot, verbose=False):
    """
    Compare 4 rows of placement data with a piece rotated.
    """
    #print('piece')
    #print(piece_rot)
    #if verbose: print('place', place.shape)
    #if verbose: print(place)
    piece_width = piece_rot.shape[1]
    #print('lp', len(place[0]))
    #print(piece_width)
    #if verbose: print('fpd', place.shape[0]-piece_width)
    for i in range(place.shape[1] + 1 - piece_width):
        if compare(piece_rot, place[:,i:i+piece_width], verbose):
            return True

def trim(data):
    """
    Remove rows that are all 0.
    """
    row_with_pieces = []
    for j, row in enumerate(data):
        if 1 in row:
            row_with_pieces.append(j)
    use_rows = (row_with_pieces[0], row_with_pieces[-1] + 1)
    return data[use_rows[0]:use_rows[1]]

def getPiece(place, verbose=False):
    """
    Find out which piece is in this 3 or 4 tall frame.
    """
    place_fixed = place
    #if place_fixed.shape[0] < 4:
       #if place_fixed.shape[0] == 2:
           #place_fixed = np.lib.pad(place, ((1, 1),(1, 0)), 'constant', constant_values=(0))
       #else:
           #place_fixed = np.lib.pad(place, ((0, 4 - place_fixed.shape[0]),(1, 0)), 'constant', constant_values=(0))
    #else:
    place_fixed = np.lib.pad(place, ((0, 0),(2, 1)), 'constant', constant_values=(0))
    #if place_fixed.shape[0] != 4:
    #    print("FIXME: getPiece is not working")
    #    return None
    if verbose: print('lpf', len(place_fixed))
    if verbose: print(place_fixed)
    for i, piece in enumerate(TETRONIMO_SHAPES): # [PM.S_PIECESHAPE]):#
        for piece_rot in piece:
            # FIXME: store trimmed values.
            r = findPiece(place_fixed, trim(piece_rot), verbose)
            if r: return i
    return None

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
translate_names = {'LONGBAR':'I', 'L-PIECE':'L', 'J-PIECE':'J', 'S-PIECE':'S', 'Z-PIECE':'Z', 'T-PIECE':'T', 'O-PIECE':'O', "None":"_"}

# Don't need to parse every piece
decodePieces = False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tetrisfish")
    parser.add_argument('filename')
    parser.add_argument('level', type=int, nargs='?', default=0)
    args = parser.parse_args()
    file = open(args.filename, 'r')
    positionDatabase = ast.literal_eval(file.read())
    i = 0
    clears = []
    pieces = []
    prevLines = 0
    pointsTetrises = 0
    pointsOther = 0

    droughts = {'L-PIECE':[], 'J-PIECE':[], 'S-PIECE':[], 'Z-PIECE':[], 'T-PIECE':[], 'LONGBAR':[], 'O-PIECE':[]}
    for position in positionDatabase['positions']:
        if decodePieces:
            pp = decodeArray(position['placement'])
            # Just the rows with the pieces please.
            curr_piece = getPiece(trim(pp))
            if curr_piece is None:
                curr_piece = getPiece(trim(pp), True)
                print(trim(pp))
            #print('piece found', curr_piece, curr_piece in TETRONIMO_NAMES and TETRONIMO_NAMES[curr_piece])
            if curr_piece in TETRONIMO_NAMES:
                pieces.append(TETRONIMO_NAMES[curr_piece])
            #print('next', TETRONIMO_NAMES[position['next']])
            i += 1
            #if i > 1: break
        else:
            # We can use next box instead of computation to determine piece sequence.
            pieces.append(TETRONIMO_NAMES[position['current']])
        if position['lines'] > prevLines:
            cleared = position['lines'] - prevLines
            if cleared == 4:
                points = 1200 * (position['level'] + 1)
                #print("Tetris for {0} points".format(points))
                pointsTetrises += points
            elif cleared == 3:
                pointsOther += 300 * (position['level'] + 1)
            elif cleared == 2:
                pointsOther += 100 * (position['level'] + 1)
            elif cleared == 1:
                pointsOther += 40 * (position['level'] + 1)
            clears.append(cleared)
            prevLines = position['lines']

    print(''.join([translate_names[piece] for piece in pieces]))
    dur_since = {'L-PIECE':0, 'J-PIECE':0, 'S-PIECE':0, 'Z-PIECE':0, 'T-PIECE':0, 'LONGBAR':0, 'O-PIECE':0}
    for piece in pieces:
        for x in dur_since:
            if piece != x:
                dur_since[x] += 1
            else:
                droughts[piece].append(dur_since[piece])
                dur_since[piece] = 0
    print("Drought durations: max [sequence]")
    for piece in droughts:
        print(piece, max(droughts[piece]), droughts[piece])
    print("Clears:")
    print(clears)
    tetrises = len([x for x in clears if x == 4])
    triples = len([x for x in clears if x == 3])
    doubles = len([x for x in clears if x == 2])
    singles = len([x for x in clears if x == 1])
    others  = len([x for x in clears if x not in (1, 2, 3, 4)])
    print("TRT: {0}%".format(round(100 * pointsTetrises / (pointsTetrises + pointsOther))), pointsTetrises, '/', pointsTetrises + pointsOther)
    print("{0} tetrises, {1} triples, {2} doubles, {3} singles{4}".format(tetrises, triples, doubles, singles, others and ', {0} ???'.format(others) or ''))
if __name__ == '__main__':
    main()
