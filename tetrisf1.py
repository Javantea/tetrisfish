import ast
import binascii
import base64
import numpy as np
import PieceMasks as PM

# From SaveAnalysis.
# Take encoded string, return nparray.
def decodeArray(string):

    b = base64.decodebytes(string)
    int8 = np.frombuffer(b, dtype=np.uint8)
    decoded = np.unpackbits(int8).reshape(20,10).astype(np.uint8)
    #print(decoded.dtype)
    return decoded

def compare(piece_rot, data):
    if piece_rot.size != data.size:
        print('diff size', piece_rot.size, data.size)
        return False
    #print(piece_rot)
    #print(data)
    for i in range(len(piece_rot)):
        for j in range(len(piece_rot[i])):
            if piece_rot[i][j] != data[i][j]: return False
    return True

def findPiece(place, piece_rot):
    piece_width = len(piece_rot)
    #print('lp', len(place[0]))
    #print(piece_width)
    for i in range(len(place[0])-piece_width):
        if compare(piece_rot, place[:,i:i+piece_width]):
            return True

def getPiece(place):
    place_fixed = np.lib.pad(place, ((0,1),(0,0)), 'constant', constant_values=(0))
    #print('lpf', len(place_fixed))
    #print(place_fixed)
    for i, piece in enumerate(PM.TETRONIMO_SHAPES): # [PM.S_PIECESHAPE]):#
        for piece_rot in piece:
            r = findPiece(place_fixed, piece_rot)
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
translate_names = {'LONGBAR':'I', 'L-PIECE':'L', 'J-PIECE':'J', 'S-PIECE':'S', 'Z-PIECE':'Z', 'T-PIECE':'T', 'O-PIECE':'O'}

# Don't need to parse every piece
paranoia = False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tetrisfish")
    parser.add_argument('filename')
    args = parser.parse_args()
    file = open(args.filename, 'r')
    positionDatabase = ast.literal_eval(file.read())
    i = 0
    pieces = []
    droughts = {'L-PIECE':[], 'J-PIECE':[], 'S-PIECE':[], 'Z-PIECE':[], 'T-PIECE':[], 'LONGBAR':[], 'O-PIECE':[]}
    for position in positionDatabase['positions']:
        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAYAg==
        if paranoia or len(pieces) == 0:
            pp = decodeArray(position['placement'])
            # Just the rows with the pieces please.
            row_with_pieces = []
            for j, row in enumerate(pp):
                if 1 in row:
                    row_with_pieces.append(j)
            use_rows = (row_with_pieces[0], row_with_pieces[-1] + 1)
            print(pp[use_rows[0]:use_rows[1]])
            curr_piece = getPiece(pp[use_rows[0]:use_rows[1]])
            print('curr', curr_piece)
            pieces.append(TETRONIMO_NAMES[curr_piece])
            #print('next', TETRONIMO_NAMES[position['next']])
            i += 1
            if i > 1: break
        if not paranoia:
            # We can use next box instead of computation to determine piece sequence.
            pieces.append(TETRONIMO_NAMES[position['next']])

    print(''.join([translate_names[piece] for piece in pieces]))
    dur_since = {'L-PIECE':0, 'J-PIECE':0, 'S-PIECE':0, 'Z-PIECE':0, 'T-PIECE':0, 'LONGBAR':0, 'O-PIECE':0}
    for piece in pieces:
        for x in dur_since:
            if piece != x:
                dur_since[x] += 1
            else:
                droughts[piece].append(dur_since[piece])
                dur_since[piece] = 0
    for piece in droughts:
        print(piece, droughts[piece])

if __name__ == '__main__':
    main()
