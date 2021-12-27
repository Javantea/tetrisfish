﻿"""
Class representing the bounds on a video or image
They can also draw themselves onto surfaces

It contains a raw rectangle, and a subrectangle.

For example, a raw rectangle would be the entire next box, and a sub rectangle would
be the minimal rectangle for the preview piece.

Or another example, raw rectangle is the field, but sub rectangle crops out bottom few
and right few pixels since they are black.
"""

import numpy as np
import pygame
from colors import (
PURE_BLUE, BRIGHT_BLUE, BRIGHT_RED, BRIGHT_GREEN, COLOR_CYCLE
)  #todo: remove this dependency.


from TetrisUtility import clamp, distance #todo: remove this dependency
from enum import Enum

from calibrate.autolayout import PREVIEW_LAYOUTS

class CalibrationStatus(Enum):
    TOP_LEFT = 1
    BOTTOM_RIGHT = 2
    ALREADY_SET = 0

class Bounds:
    # Pseudo random pixel offsets for sampling each block
    PIXEL_SAMPLE_OFFSETS = [[0,0],
                            [1,0],
                            [-1,0],
                            [0,1],
                            [0,-1]]

    def __init__(self, isNextBox, config=None):
        # alternate constructor; json dictionary
        if isinstance(isNextBox, dict):
            self._from_json(isNextBox, config)
            return

        self.firstClick = True
        self.config = config # todo: remove this dependency.
        self.isNB = isNextBox
        # bounding rect
        self.x1 = 0
        self.y1 = 0
        self.x2 = self.config.VIDEO_WIDTH
        self.y2 = self.config.VIDEO_HEIGHT

        # offset rect
        self.X_LEFT = 0
        self.Y_TOP = 0
        self.X_RIGHT = 0
        self.Y_BOTTOM = 0
        self.calibration_status = CalibrationStatus.TOP_LEFT
        self.r = 4 if isNextBox else 8
        self.dragRadius = 10
        self.dragRadiusBig = 13
        self.dragMode = CalibrationStatus.ALREADY_SET

        self.notSet = True

        # cached list of calibration dots
        self.xrlist = None
        self.yrlist = None

        # whether to draw the corner circles big or not
        self.draw_big_top_left = False
        self.draw_big_bot_right = False

        if self.isNB:
            self.color = PURE_BLUE
            self.horizontal = 8
            self.vertical = 4
        else:
            self.color = BRIGHT_RED
            self.horizontal = self.config.NUM_HORIZONTAL_CELLS
            self.vertical = self.config.NUM_VERTICAL_CELLS

        self.sub_rect_name = None
        self.isMaxoutClub = False
        self._defineDimensions()
            

    def setRect(self, rect):
        """
        Sets the rectangles position in videospace pixels
        """
        #percentage of pixel to original video
        self.x1 = rect[0]
        self.x2 = rect[2]
        self.y1 = rect[1]
        self.y2 = rect[3]
               
        self.updateConversions()
        self.set()
        
    
    def setSubRect(self, rect):
        """
        sets the subrect proportions
        """
        self.X_LEFT, self.Y_TOP, self.X_RIGHT, self.Y_BOTTOM = rect
        
        # initialize lookup tables for bounds
        self.updateConversions()
    
    def cycle_sub_rect(self):
        """
        cycles to the next available subrect for previews
        """
        if self.isNB:
            names = list(PREVIEW_LAYOUTS.keys())
            idx = names.index(self.sub_rect_name)
            idx = (idx + 1) % len(names)
            self.sub_rect_name = names[idx]
        self._defineDimensions()

    def _defineDimensions(self):
        """
        Reads sub_rect from autolayouts
        """
        if self.isNB:
            if self.sub_rect_name is None:
                self.sub_rect_name = list(PREVIEW_LAYOUTS.keys())[0]
            layout = PREVIEW_LAYOUTS[self.sub_rect_name]
            self.setSubRect(layout.inner_box)

        else: # field
            self.setSubRect((0.01,0.0,0.99,0.993)) #todo, read from autolayout
            self.sub_rect_name = "field"

    

    def mouseNearDot(self, mx, my):
        mx, my = self.convert_to_video_px(mx,my)
        
        return ((distance(mx,my,self.x1,self.y1) <= self.dragRadius*3) or 
                (distance(mx,my,self.x2,self.y2) <= self.dragRadius*3) or 
               self.calibration_status != CalibrationStatus.ALREADY_SET or
               self.dragMode != CalibrationStatus.ALREADY_SET)

    def mouseOutOfBounds(self, mx, my):
        return not (0 <= mx <= self.config.X_MAX and 0 <= my <= self.config.Y_MAX) 

    # return True to delete
    def updateMouse(self, mx, my, pressDown, pressUp):

        self.doNotDisplay = self.notSet and self.mouseOutOfBounds(mx, my)

        if self.doNotDisplay:
            if pressUp and not self.firstClick:
                return True
            elif not pressUp:
                self.firstClick = False
                return False

        self.firstClick = False
        mx, my = self.convert_to_video_px(mx,my)
        
        
        # should the corner circles be drawn bigger?
        # yes if we are hovering or we are up to that stage of calibration.
        self.draw_big_top_left = self.dragMode == CalibrationStatus.TOP_LEFT
        self.draw_big_bot_right = self.dragMode == CalibrationStatus.BOTTOM_RIGHT
        if distance(mx,my,self.x1,self.y1) <= self.dragRadius*3:
            self.draw_big_top_left = True
            if pressDown:
                self.dragMode = CalibrationStatus.TOP_LEFT
        elif distance(mx,my,self.x2,self.y2) <= self.dragRadius*3:
            self.draw_big_bot_right = True
            if pressDown:
                self.dragMode = CalibrationStatus.BOTTOM_RIGHT

        if pressUp:
            self.dragMode = CalibrationStatus.ALREADY_SET

        minimumLength = 20
        
        
        if (self.calibration_status == CalibrationStatus.TOP_LEFT or
            self.dragMode == CalibrationStatus.TOP_LEFT):
            self.x1 = min(mx, self.x2 - minimumLength)
            self.y1 = min(my, self.y2 - minimumLength)
            self.updateConversions()
        elif (self.calibration_status == CalibrationStatus.BOTTOM_RIGHT or 
             self.dragMode == CalibrationStatus.BOTTOM_RIGHT):
            self.x2 = max(mx, self.x1 + minimumLength)
            self.y2 = max(my, self.y1 + minimumLength)
            self.updateConversions()

        return False
        

    def click(self, mx, my):
        if self.mouseOutOfBounds(mx ,my):
            return
        
        if self.calibration_status == CalibrationStatus.TOP_LEFT:
            self.calibration_status = CalibrationStatus.BOTTOM_RIGHT
            
        elif self.calibration_status == CalibrationStatus.BOTTOM_RIGHT:
            self.set()

    # Finalize callibration
    def set(self):
        self.calibration_status = CalibrationStatus.ALREADY_SET
        self.notSet = False


    def _getPosition(self):
        
        dx = self.X_RIGHT*(self.x2-self.x1) / self.horizontal
        margin = (self.y2-self.y1)*self.Y_TOP
        dy = self.Y_BOTTOM*(self.y2-self.y1-margin) / self.vertical

        # dx, dy, radius
        return dx, dy, (dx+dy)/2/8
    
 
        
    # After change x1/y1/x2/y2, update conversions to scale
    # Generate lookup tables of locations of elements
    def updateConversions(self):
        w = self.x2 - self.x1
        h = self.y2 - self.y1

        # Generate a list of every x scaled location of the center of all 10 minos in a row
        self.xlist = []
        cell_half_width = w * (self.X_RIGHT - self.X_LEFT) / self.horizontal / 2.0
        cell_half_height = h * (self.Y_BOTTOM - self.Y_TOP) / self.vertical / 2.0
        

        x1 = (self.x1 + w*self.X_LEFT)   * self.config.SCALAR + self.config.VIDEO_X
        y1 = (self.y1 + h*self.Y_TOP)    * self.config.SCALAR + self.config.VIDEO_Y
        x2 = (self.x1 + w*self.X_RIGHT)  * self.config.SCALAR + self.config.VIDEO_X
        y2 = (self.y1 + h*self.Y_BOTTOM) * self.config.SCALAR + self.config.VIDEO_Y

        x = self.x1 + w*self.X_LEFT + cell_half_width
        for i in range(self.horizontal):
            self.xlist.append( int(clamp(x, 0, self.config.VIDEO_WIDTH) ) )
            x += 2*cell_half_width

         # Generate a list of every y scaled location of the center of all 10 minos in a row
        self.ylist = []
        y = self.y1 + h*self.Y_TOP + cell_half_height
        for i in range(self.vertical):
            self.ylist.append( int(clamp(y, 0, self.config.VIDEO_HEIGHT) ) )
            y += 2*cell_half_height

        # xrlist and xylist are an 5-element array of different variants of xlist and ylist.
        # Specifically, they store xlist and ylist offset by radius by different directions.
        # It is precomputed this way for efficiency during each frame.
        # They will be used to quickly get numpy pixels and see if average of each of those 5 points
        #   constitute a filled or empty cell
        self.xrlist = [ self.xlist ]
        self.yrlist = [ self.ylist ]
        for a,b in self.PIXEL_SAMPLE_OFFSETS: # (a,b) represent some (x,y) offset from the center
            # abbreviated: current x/y list. List comprehension to generate copies of lists with given offset
            self.cxl = [(x+a) for x in self.xlist]
            self.cyl = [(y+b) for y in self.ylist]

            self.xrlist.append(self.cxl)
            self.yrlist.append(self.cyl)


    # Faster replacement for getMinosAndDisplay(). Works directly from nparray.
    # Generates a 2d nparray of minos from nparray of pixels without explicit iteration over each pixel.
    # Called every frame so must be optimized well.
    def getMinos(self, nparray):

        minosList = [] # Represents the 2d arrays of colors at each mino of slightly different offsets from each tetronimo
        for i in range(0,5):
            # colorsList is a [10x20x3] array (vertical x horizontal x rgb] for regular, [4x8x3] for nextbox
            colorsList = nparray[ self.yrlist[0] ][ :  , self.xrlist[0] ]

            # minosVariant is a 10x20 array (4x8 for nextbox), each element representing the average of the rgb values on that pixel for the mino
            minosVariant = np.mean(colorsList, axis = 2)
            minosList.append(minosVariant)

        # np.mean averages all 5 2d arrays. averagedMinosInts is a 10x20 array (4x8 for nextbox), each element the brightness (0-255) of the entire mino
        averagedMinosInts = np.mean(minosList, axis = 0)

        # We use a step function for each element: f(x) = 1 if x >= COLOR_CALLIBRATION else 0
        finalMinos = np.heaviside(averagedMinosInts - self.config.COLOR_CALLIBRATION, 1) # 1 means borderline case (x = COLOR_CALLIBRATION) still 1

        return finalMinos
    
    def convert_to_video_px(self, mx, my):
        mx -= self.config.VIDEO_X
        my -= self.config.VIDEO_Y
        mx /= self.config.SCALAR
        my /= self.config.SCALAR
        return mx, my

    def in_bounds(self, mx, my):
        mx,my = self.convert_to_video_px(mx,my)
        return self.x1 <= mx <= self.x2 and self.y1 <= my <= self.y2

    # Draw the markings for detected minos.
    def displayBounds(self, surface, nparray = None, minos = None):
        
        if self.doNotDisplay:
            return None

        if type(minos) != np.ndarray:
            minos = self.getMinos(nparray)
        
        # draw bounds rect
        x1 = self.x1 * self.config.SCALAR + self.config.VIDEO_X
        y1 = self.y1 * self.config.SCALAR + self.config.VIDEO_Y
        x2 = self.x2 * self.config.SCALAR + self.config.VIDEO_X
        y2 = self.y2 * self.config.SCALAR + self.config.VIDEO_Y
        pygame.draw.rect(surface, self.color, [x1, y1, x2-x1, y2-y1], width = 3)
        
        # Draw draggable bounds dots
        pygame.draw.circle(surface, self.color, [x1,y1], self.dragRadiusBig if self.draw_big_top_left else self.dragRadius)
        pygame.draw.circle(surface, self.color, [x2,y2], self.dragRadiusBig if self.draw_big_bot_right else self.dragRadius)

        # draw sub-bounds rect
        w = self.x2 - self.x1
        h = self.y2 - self.y1
        x1 = (self.x1 + w*self.X_LEFT)   * self.config.SCALAR + self.config.VIDEO_X
        y1 = (self.y1 + h*self.Y_TOP)    * self.config.SCALAR + self.config.VIDEO_Y
        x2 = (self.x1 + w*self.X_RIGHT)  * self.config.SCALAR + self.config.VIDEO_X
        y2 = (self.y1 + h*self.Y_BOTTOM) * self.config.SCALAR + self.config.VIDEO_Y
        pygame.draw.rect(surface, BRIGHT_BLUE, [x1, y1, x2-x1, y2-y1], width = 3)
        #  Draw cell callibration markers. Start on the center of the first cell

        #r = max(1,int(self.r * self.config.SCALAR))
        r = self.r
        for i in range(self.vertical):
            for j in range(self.horizontal):
                exists = (minos[i][j] == 1)
                
                x = int(self.xlist[j] * self.config.SCALAR + self.config.VIDEO_X)
                y = int(self.ylist[i] * self.config.SCALAR + self.config.VIDEO_Y)
                pygame.draw.circle(surface, BRIGHT_GREEN if exists else BRIGHT_RED, [x,y], (r+2) if exists else r, width = (0 if exists else 3))

        return minos

    def to_json(self):
        return {"firstClick": self.firstClick,
                "isNextBox": self.isNB,
                "bounding_rect": [self.x1,self.y1,self.x2,self.y2],
                "sub_rect": [self.X_LEFT, self.Y_TOP, self.X_RIGHT, self.Y_BOTTOM],
                "callibration" : self.calibration_status,
                "sub_rect_name": self.sub_rect_name}


    def _from_json(self, data, c):
        self.__init__(data["isNextBox"], c)
        self.setRect(data["bounding_rect"])
        self.setSubRect(data["sub_rect"])
        self.calibration_status = data["callibration"]
        self.sub_rect_name = data["sub_rect_name"]
        

class BoundsPicker:
    """
    Class that displays and allows users to pick multiple bounds
    """ 
    def __init__(self, bounds_list, config):
        self.bounds_list = bounds_list
        for index, item in enumerate(bounds_list):
            item[0].color = COLOR_CYCLE[index%len(COLOR_CYCLE)]
        self.config = c
    
    def updateMouse(self, mx, my, pressDown, pressUp):
        return

    def displayBounds(self, surface):
        for item in self.bounds_list:
            item[0].displayBounds(surface)

    def click(self, mx, my):
        for index, bound in bounds_list:
            if bound[0].in_bounds(mx,my):
                print("selected:", index)
                break

    def handle_keyboard(self):
        pass