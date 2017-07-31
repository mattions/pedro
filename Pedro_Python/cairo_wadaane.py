# cd /cygdrive/C/Users/del/Desktop/Pedro/pedro/Pedro_Python

import cairo
import gi
from math import pi, atan2, sin, cos, degrees, acos, asin, sqrt
from numpy import clip
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

SIZE = 100
Width = 12*SIZE
Height = 5*SIZE
length_Forearm = 2*SIZE
length_Hand = SIZE
length_EndPoint = 0.4*SIZE
r = 1
Y = 0
R = 1

global drawingarea
mXL = 0
mYL = 0
mXR = 0
mYR = 0
isForearm = True
base = 0
forearm = 0
hand = 0
originX = 0
originY = 0

OriginX = 0
OriginY = 5*SIZE

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
        
    if useIk:
        ctx.set_dash([SIZE / 4.0, SIZE / 4.0], 0)
        ctx.arc(OriginX,OriginY,length_Forearm+length_Hand+length_EndPoint,pi, 2*pi)
        ctx.stroke()
        c = length_Forearm-length_EndPoint-length_Hand
        ctx.arc(OriginX,OriginY,sqrt(c*c-Y*Y),pi, 2*pi)
        ctx.stroke()

    print('Base: ' + str(int(degrees(base)))+' Forearm: '+str(int(degrees(forearm)))+ ' Hand: '+ str(int(degrees(hand))))   #   print the angles in degrees, so we can send to servo.
    

# ---------------------------------
# draw_pedro_side
# ---------------------------------
def draw_pedro_side(ctx):

    global originX
    global originY
    global forearm
    global hand
    global mXL
    global mYL
    global mXR
    global mYR
    
    global OriginX, OriginY
    OriginX = 0
    OriginY = 5*SIZE	
    
        # Base
    ctx.save()
    ctx.rectangle(OriginX,OriginY,SIZE,-SIZE)
            
        # Forearm   ctx.save()                                      #   Save initial transformations: translations, rotations etc
    ctx.translate(OriginX+0.5*SIZE,OriginY-SIZE)                 #   Move origin to top and middle of base rectangle
    if not useIk and isForearm:                                 #   check if we are rotating the forearm.
        originX = 1.5*SIZE                          #   unTranslated coordinates of top middle of base rectangle
        originY = 4*SIZE                            #   so we can calculate the angle of click position

        forearm = atan2(mYL-originY, mXL-originX)   #   get angle from vector click position and origin
        forearm += (pi/2)                           #   the forearm initial position is 90 degrees
        
    ctx.rotate(forearm)                             #   rotate everything that comes next
    ctx.rectangle(-0.25*SIZE,0,0.5*SIZE,-2*SIZE)    #   Draw forearm rectangle.
    if not useIk: ctx.rectangle(0 , -4*SIZE, 0.05*SIZE,0.05*SIZE)   #   Draw a small rectangle showing us current Angle.
    
        # Hand
    ctx.save()                                      #   Save previous rotations, so we don't rotate the forearm again.
    ctx.translate(0,-2*SIZE)                        #   Move origin to top and middle of Forearm rectangle
    if not useIk and not isForearm:                             #   check if we are rotating the hand.
        originX = 1.5*SIZE + (2*SIZE)*cos(forearm - (pi/2)) #   unTranslated coordinates of top middle of base rectangle
        originY = 4*SIZE   + (2*SIZE)*sin(forearm - (pi/2)) 
        
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
	
    ctx.rectangle(OriginX+0.5*SIZE+r, OriginY-SIZE-Y, 0.05*SIZE,0.05*SIZE)
    ctx.stroke()                                    #   Draw all previous shapes.
    

# ---------------------------------
# draw_pedro_top
# ---------------------------------
def draw_pedro_top(ctx):

    global OriginX, OriginY
    OriginX = 8*SIZE
    OriginY = 5*SIZE
    
        # Base
    ctx.save()
    ctx.translate(OriginX,OriginY) #+0.5*SIZE
    ctx.rotate(-base+pi/2)
    
    ctx.rectangle(-0.5*SIZE,0.5*SIZE,SIZE,-SIZE)
	
    dx = mXL - OriginX
    dy = mYL - OriginY
    dist = min([sqrt(dx*dx + dy*dy), length_Forearm+length_Hand+length_EndPoint])

    c = length_Forearm-length_EndPoint-length_Hand
    dist = max(dist, sqrt(c*c-Y*Y))
    
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
        xyzToServoAngles(mXL-OriginX, mYL-OriginY, 0.1*SIZE)
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
    global base, forearm, hand,r, Y
    a = length_Forearm                  # Lenght of Forearm
    b = length_Hand + length_EndPoint       # Length of Hand
    r = sqrt(x*x + y*y)
    R = sqrt(r*r + z*z)
    Y = z
    if R > (a-b) and r < (a+b) and R < (a+b): # 
        base = -atan2(y,x)
        forearm = -acos((a*a + R*R - b*b)/(2*a*R)) - acos(r/R) +pi/2
        hand = -acos((a*a + b*b - R*R)/(2*a*b)) + pi
    else:
        print('Out of reach !!!')

        
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


