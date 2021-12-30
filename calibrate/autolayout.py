﻿"""
Helper classes for autocalibration
"""
class Layout:
    def __init__(self, name, fillpoint, preview):
        self.name = name
        self.fillpoint = fillpoint # fill point in relative screen coords (x,y)
        self.preview = preview # preview type

class PreviewLayout:    
    TIGHT=1
    STANDARD=2 # flood fill the box, then choose subset based on nes_px_size    
    HARDCODE=3 # don't expand, just hardcode it.
    
    def __init__(self, name, nes_px_offset, nes_px_size, inner_box, preview_type, preview_size):
        self.name = name
        self.nes_px_offset = nes_px_offset #e.g. (90, 90)
        self.nes_px_size = nes_px_size #e.g (42, 32)
        self.inner_box = inner_box # e.g. (0.1, 0.1, 0.9, 0.9)
        self.preview_type = preview_type
        self.preview_size = preview_size #e.g. 1.0

    def recalc_sub_rect(self, new_sub_rect):
        """Given a new subrect in nes_pixels, calculates inner_box"""
        print (new_sub_rect, self.nes_px_size)
        result = (new_sub_rect.left / float(self.nes_px_size[0]),
                  new_sub_rect.top / float(self.nes_px_size[1]),
                  new_sub_rect.right / float(self.nes_px_size[0]),
                  new_sub_rect.bottom / float(self.nes_px_size[1]))
        self.inner_box = result

    @property
    def inner_box_size(self):
        return [self.inner_box[2] - self.inner_box[0],
                self.inner_box[3] - self.inner_box[1]]
    
    @property
    def fillpoint(self):
        # return inner box top left corner
        x = self.nes_px_size[0] * self.inner_box[0]
        y = self.nes_px_size[1] * self.inner_box[1]
        return (x,y)
        
    @property
    def inner_box_nespx(self):
        left = self.nes_px_size[0] * self.inner_box[0]
        top = self.nes_px_size[1] * self.inner_box[1]
        right = self.nes_px_size[0] * self.inner_box[2]
        bot = self.nes_px_size[1] * self.inner_box[3]
        return (left,top,right,bot)
    
    @property
    def should_suboptimize(self):
        """
        we should only do template matching if we have heaps of 
        black space around. Otherwise we will fail horrendously
        """
        perc = self.inner_box_size[0] * self.inner_box_size[1]
        print(f"optimize_perc = {perc}")
        return perc < 0.9

    @property
    def inner_box_corners_nespx(self):
        box = self.inner_box_nespx
        return [(box[0],box[1]), #tl
                (box[0],box[3]), #bl
                (box[2],box[1]), #tr
                (box[2],box[3])] #br
        
    def __str__(self):
        return (f"PreviewLayout: {self.nes_px_offset}, {self.preview_type}")
    
    def __eq__(self, other):
        if not isinstance(other, PreviewLayout):
            return False
        return (self.nes_px_offset == other.nes_px_offset and
               self.preview_type == other.preview_type and
               self.nes_px_size == other.nes_px_size and
               self.inner_box == other.inner_box)

    def clone(self):
        return PreviewLayout(self.name,
                               self.nes_px_offset,
                               self.nes_px_size,
                               self.inner_box,
                               self.preview_type,
                               self.preview_size)


#A bug/quirk; the key and name must match 1:1 for preview layouts
PREVIEW_LAYOUTS = { # stencil, stock capture etc.
                    "STANDARD": PreviewLayout("STANDARD", (96,56),(32,41), (0.04,0.41,0.96,0.78), PreviewLayout.STANDARD, 1.0),
                    # ctwc 2p                    
                    "MOC": PreviewLayout("MOC", (5.4*8,-3.1*8), (37,19), (0.08,0.16,0.90,0.89),PreviewLayout.TIGHT, 1.0),
                    # ctwc 4p
                    "MOC4pLeft": PreviewLayout("MOC4pLeft", (-5*8,4.5*8), (34,18), (0.05,0.07,0.97,0.95), PreviewLayout.TIGHT, 1.0),
                    "MOC4pRight": PreviewLayout("MOC4pRight", (10.8*8,4.5*8), (34,18), (0.05,0.07,0.97,0.95),PreviewLayout.TIGHT, 1.0),
                    # "CTM": #2p
                    # "CTM": #4p
                  }


LAYOUTS = {"STANDARD": Layout("Standard", (0.5,0.5), PREVIEW_LAYOUTS["STANDARD"]),
           "RIGHT_SIDE": Layout("Standard", (0.75,0.5), PREVIEW_LAYOUTS["STANDARD"]),
           "STENCIL": Layout("Stencil™", (0.3,0.5), PREVIEW_LAYOUTS["STANDARD"]),
           "MOC_LEFT": Layout("MaxoutClub", (0.422,0.302), PREVIEW_LAYOUTS["MOC"]), #ctwc 2p
           "MOC_RIGHT": Layout("MaxoutClub", (0.578,0.302), PREVIEW_LAYOUTS["MOC"]), #ctwc 2p
           "MOC_TOPLEFT": Layout("MaxoutClub", (0.444,0.204), PREVIEW_LAYOUTS["MOC4pLeft"]), #ctwc 4p
           "MOC_TOPRIGHT": Layout("MaxoutClub", (0.556,0.204), PREVIEW_LAYOUTS["MOC4pRight"]), #ctwc 4p
           "MOC_BOTLEFT": Layout("MaxoutClub", (0.444,0.669), PREVIEW_LAYOUTS["MOC4pLeft"]), #ctwc 4p
           "MOC_BOTRIGHT": Layout("MaxoutClub", (0.556,0.669), PREVIEW_LAYOUTS["MOC4pRight"]) #ctwc 4p
          }

class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
    
    @property
    def width(self):
        return self.right - self.left
    
    @property
    def height(self):
        return self.bottom - self.top

    @property
    def area(self):
        return self.width * self.height

    @property
    def centre(self):
        return (self.left + 0.5* self.width,
               self.top + 0.5 * self.height)

    def to_array(self):
        return (self.left, self.top, self.right, self.bottom)
    
    def __str__(self):
        return str(self.to_array())
   
    def __eq__(self, other):
        if isinstance(other, Rect):
            return (self.left == other.left and
                   self.top == other.top and
                   self.right == other.right and
                   self.bottom == other.bottom)
        return False
    
    def contains(self, xy):
        return (self.left <= xy[0] <= self.right and 
               self.top <= xy[1] <= self.bottom)

    def within(self, yx):
        """
        returns if rectangle is within an image with given y/x size.
        """
        return (0 <= self.left <= self.right <= yx[1] and 
                0 <= self.top <= self.bottom <= yx[0])
           
    def multiply(self, constant):
        self.left = self.left * constant
        self.top = self.top * constant
        self.right = self.right * constant
        self.bottom = self.bottom* constant
    
    def round_to_int(self):
        self.left = round(self.left)
        self.top = round(self.top)
        self.right = round(self.right)
        self.bottom= round(self.bottom)

    def sq_distance(self, point):
        """
        square distance from center of rect to point.
        Because math.sqrt is expensive yo
        """
        you = self.centre #you self.centred b****
        xdist = (you[0] - point[0]) 
        ydist = (you[1] - point[1])
        result = xdist*xdist + ydist*ydist
        return result