# cd /cygdrive/C/Users/del/Desktop/Pedro/pedro/Pedro_Python

import cairo
import gi
from math import pi, atan2, sin, cos, degrees, radians, acos, asin, sqrt, fabs
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

SIZE = 100
TXT_SIZE = SIZE/5
length_Hand = SIZE
length_EndPoint = 0.4*SIZE
length_Forearm = 2*SIZE
Z = 1*SIZE
d = length_Forearm+length_Hand+length_EndPoint
c = length_Forearm-length_EndPoint-length_Hand
r = 1
R = 1


OriginSideX = d - 0.5*SIZE+SIZE
OriginSideY = d
OriginTopX = d+SIZE
OriginTopY = 2*d

originForearmX = OriginSideX+1.5*SIZE
originForearmY = OriginSideY-SIZE

Width = 2*OriginTopX
Height = 2*OriginSideY


global drawingarea
mXL = 0
mYL = 0
mXR = 0
mYR = 0
isForearm = True
base = pi/2
forearm = -pi/2
hand = pi*3/4

outOfReach = False
useIk = True

# ---------------------------------
# draw
# ---------------------------------
def draw(da, ctx):
    ctx.set_source_rgb(0, 0, 0)         #   Set our color to black
    ctx.set_line_width(SIZE / 20)           #   Set line width
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)    #   Set our line end shape
    
    draw_pedro_side(ctx)
    draw_pedro_top(ctx)
    draw_text(ctx)
        
    if useIk:
        ctx.set_dash([SIZE / 4.0, SIZE / 4.0], 0)
        ctx.new_path()
        if (d*d-Z*Z)>=0: ctx.arc(OriginTopX,OriginTopY,sqrt(d*d-Z*Z),pi, 2*pi)
        ctx.stroke()
    
        if (c*c-Z*Z)>=0: ctx.arc(OriginTopX,OriginTopY,sqrt(c*c-Z*Z),pi, 2*pi)
        ctx.stroke()

    
def draw_text(ctx):
     
    ctx.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(TXT_SIZE)
    ctx.move_to(0.01*SIZE, TXT_SIZE)
    ctx.show_text('Base: ' +        str(-int(degrees(base))+90))
    ctx.move_to(0.01*SIZE, 2*TXT_SIZE)
    ctx.show_text('Forearm: '+      str(int(degrees(forearm)+90)))
    ctx.move_to(0.01*SIZE, 3*TXT_SIZE)
    ctx.show_text('Hand: '+         str(int(-degrees(hand)+135)))
    if outOfReach:
        ctx.move_to(0.01*SIZE, 4*TXT_SIZE)
        ctx.show_text('OUT OF REACH !')

# ---------------------------------
# draw_pedro_side
# ---------------------------------
def draw_pedro_side(ctx):

    global forearm
    global hand 
    
        # Base
    ctx.save()
    ctx.rectangle(OriginSideX,OriginSideY,SIZE,-SIZE)
            
        # Forearm   ctx.save()                                      #   Save initial transformations: translations, rotations etc
    ctx.translate(OriginSideX+0.5*SIZE,OriginSideY-SIZE)                 #   Move origin to top and middle of base rectangle
    if not useIk and isForearm:                                 #   check if we are rotating the forearm.
        forearm = atan2(mYL-originForearmY, mXL-originForearmX)   #   get angle from vector click position and origin
        forearm += (pi/2)                           #   the forearm initial position is 90 degrees
        
    ctx.rotate(forearm)                             #   rotate everything that comes next
    ctx.rectangle(-0.25*SIZE,0,0.5*SIZE,-2*SIZE)    #   Draw forearm rectangle.
    if not useIk: ctx.rectangle(0 , -4*SIZE, 0.05*SIZE,0.05*SIZE)   #   Draw a small rectangle showing us current Angle.
    
        # Hand
    ctx.save()                                      #   Save previous rotations, so we don't rotate the forearm again.
    ctx.translate(0,-2*SIZE)                        #   Move origin to top and middle of Forearm rectangle
    if not useIk and not isForearm:                             #   check if we are rotating the hand.
        originX = originForearmX + (length_Forearm)*cos(forearm - (pi/2)) #   unTranslated coordinates of top middle of base rectangle
        originY = originForearmY + (length_Forearm)*sin(forearm - (pi/2)) 
        
        hand = atan2(mYR-originY,
                     mXR-originX)
        hand += (pi/2)
        hand -= forearm                             #   We remove the forearm rotation so tha hand rotate independantly.
    
    ctx.rotate(hand)
    ctx.rectangle(-0.25*SIZE, 0,0.5*SIZE,-SIZE)
    if not useIk: ctx.rectangle(0 ,-2*SIZE, 0.05*SIZE,0.05*SIZE)
    ctx.stroke()                                    #   Draw all previous shapes.
        
        # End Point
    ctx.save()                                      #   We draw the end point triangles manually
    ctx.translate(0,-SIZE)
    ctx.new_path()
    
    ctx.move_to(    -0.2*SIZE, 0)
    ctx.rel_line_to(0.15*SIZE, -0.4*SIZE)
    ctx.rel_line_to(0        ,  0.4*SIZE)
    ctx.close_path()    
    
    ctx.move_to(      0.2*SIZE, 0)
    ctx.rel_line_to(-0.15*SIZE, -0.4*SIZE)
    ctx.rel_line_to(0         ,  0.4*SIZE)
    ctx.close_path()
    ctx.stroke()
    
    ctx.restore()                                   #   Restore all previous transformations, for each save() a restore()
    ctx.restore()
    ctx.restore()
    
    ctx.rectangle(OriginSideX+0.5*SIZE+r, OriginSideY-SIZE-Z, 0.05*SIZE,0.05*SIZE)
    ctx.stroke()                                    #   Draw all previous shapes.
    

# ---------------------------------
# draw_pedro_top
# ---------------------------------
def draw_pedro_top(ctx):
    
        # Base
    ctx.save()
    ctx.translate(OriginTopX,OriginTopY)
    ctx.rotate(base)
    
    ctx.rectangle(-0.5*SIZE,0.5*SIZE,SIZE,-SIZE)
    
    dx = mXL - OriginTopX
    dy = mYL - OriginTopY
    
    if (d*d-Z*Z)>=0: dist = min([sqrt(dx*dx + dy*dy), sqrt(d*d-Z*Z)])
    if (c*c-Z*Z)>=0: 
        dist = max([dist, sqrt(c*c-Z*Z)])
        
    ctx.rectangle(-0.25*SIZE,-0.5*SIZE,0.5*SIZE,-dist+0.5*SIZE)    
        
    ctx.restore()
    ctx.rectangle(mXL, mYL,0.05*SIZE,0.05*SIZE)
    ctx.stroke()                                    #   Draw all previous shapes.

    
# ---------------------------------
# mouse_pressed
# ---------------------------------
def mouse_pressed(self, e):
    global isForearm
    isForearm = (e.button == 1)     # Rotate forearm if the left mouse button is clicked.

# ---------------------------------
# mouse_dragged
# ---------------------------------
def mouse_dragged(self, e):
    global mXL, mYL
    global mXR, mYR
    
    if useIk: 
        mXL=e.x
        mYL=e.y
        xyzToServoAngles(mXL-OriginTopX, mYL-OriginTopY, Z)
    else:
        if isForearm:               #   Grab click positions.
            mXL = e.x
            mYL = e.y
        else :
            mXR = e.x
            mYR = e.y
        
    drawingarea.queue_draw()    #   Redraw eerything if mouse is dragged.


# Inverse Kinematics:
# From Cartesian to Servo Angles
# ---------------------------------
# xyzToServoAngles
# ---------------------------------
def xyzToServoAngles(x, y, z):
    global base, forearm, hand,r, Z
    a = length_Forearm                  # Lenght of Forearm
    b = length_Hand + length_EndPoint       # Length of Hand
    r = sqrt(x*x + y*y)
    R = sqrt(r*r + z*z)
    Z = z
    global outOfReach
    outOfReach = False
    if Z>=0 and Z<= d and R > (a-b) and r < (a+b) and R < (a+b): # 
        base = atan2(y,x)+pi/2
        forearm = -acos((a*a + R*R - b*b)/(2*a*R)) - acos(r/R) +pi/2
        hand = -acos((a*a + b*b - R*R)/(2*a*b)) + pi
    
        if base >pi/2 and base <pi:
            base = pi/2
            outOfReach = True
        elif base <= -pi/2 or base >pi:
            base = -pi/2
            outOfReach = True

        if forearm >pi/2 and forearm <pi:
            forearm = pi/2
            outOfReach = True
        elif forearm <= -pi/2 or forearm >pi:
            forearm = -pi/2
            outOfReach = True

        if hand >pi*3/4:
            hand = pi*3/4
            outOfReach = True
        elif hand <= 0:
            hand = 0
            outOfReach = True
    else:
        outOfReach = True
        
def main():
    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    win.set_default_size(Width, Height)
    
    global drawingarea
    drawingarea = Gtk.DrawingArea()
    drawingarea.connect('draw', draw)
    
    drawing_event_box = Gtk.EventBox()      #   Needed to grab mouse click events.
    drawing_event_box.add(drawingarea)
    drawing_event_box.connect('button-press-event', mouse_pressed)
    drawing_event_box.connect('motion-notify-event', mouse_dragged)

    win.add(drawing_event_box)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()


