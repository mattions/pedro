# cd /cygdrive/C/Users/del/Desktop/Pedro/pedro/Pedro_Python

import cairo
import gi
from math import pi, atan2, sin, cos, degrees, radians, acos, asin, sqrt, fabs
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

global drawingarea

SIZE = 75
TXT_SIZE = SIZE/5
length_Hand = SIZE
length_EndPoint = 0.4*SIZE
length_Forearm = 2*SIZE

Z = 1*SIZE
d = length_Forearm + length_Hand + length_EndPoint
c = length_Forearm - length_Hand - length_EndPoint
r = 1

mXL = 0
mYL = 0
mXR = 0
mYR = 0

OriginSideX = d + SIZE
OriginSideY = d + SIZE
OriginTopX = d + SIZE
OriginTopY = d + SIZE + OriginSideY

Width = 2*OriginTopX
Height = OriginTopY + SIZE

originForearmX = OriginSideX 
originForearmY = OriginSideY - 0.5*SIZE
originHandX = originForearmX - length_Forearm
originHandY = originForearmY


base = pi/2
forearm = 0
hand = 0

isForearm = True
outOfReach = False

# ---------------------------------
# draw
# ---------------------------------
def draw(da, ctx):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(SIZE/20)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)  
    
    draw_extra(ctx)
    draw_pedro_side(ctx)
    draw_pedro_top(ctx)
    draw_text(ctx)
        
    
# ---------------------------------
# draw_extra
# ---------------------------------
def draw_extra(ctx):
    ctx.move_to(0, Height/2)
    ctx.rel_line_to(Width, 0)
    ctx.stroke()
    
    ctx.new_path()
    ctx.set_dash([SIZE/4.0, SIZE/4.0], 0)
    if (d*d - Z*Z)>=0: ctx.arc(OriginTopX, OriginTopY, sqrt(d*d-Z*Z),pi, 2*pi)
    if (c*c - Z*Z)>=0: ctx.arc(OriginTopX, OriginTopY, sqrt(c*c-Z*Z),pi, 2*pi)
    ctx.close_path()
    ctx.stroke()

    ctx.set_dash([], 0)
    ctx.rectangle(
            OriginSideX + r,
            OriginSideY - 0.5*SIZE - Z,
            0.05*SIZE, 0.05*SIZE)
    ctx.stroke()
    

# ---------------------------------
# draw_text
# ---------------------------------
def draw_text(ctx):
    ctx.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, 
            cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(TXT_SIZE)
    ctx.move_to(0.01*SIZE, TXT_SIZE)
    ctx.show_text('Base: ' + str(-int(degrees(base)) + 90))
    ctx.move_to(0.01*SIZE, 2*TXT_SIZE)
    ctx.show_text('Forearm: '+ str(int(degrees(forearm))))
    ctx.move_to(0.01*SIZE, 3*TXT_SIZE)
    ctx.show_text('Hand: '+ str(int(degrees(-hand))))
    if outOfReach:        
        ctx.set_source_rgb(1, 0, 0) 
        ctx.move_to(-3*TXT_SIZE + Width/2, 0.5*SIZE + Height/2)
        ctx.show_text('OUT OF REACH !!!')

# ---------------------------------
# draw_pedro_side
# ---------------------------------
def draw_pedro_side(ctx):

        # Base
    ctx.rectangle(OriginSideX - 0.5*SIZE, OriginSideY + 0.5*SIZE, SIZE, -SIZE)
    ctx.rectangle(OriginSideX, OriginSideY, 0.05*SIZE, 0.05*SIZE)
    ctx.stroke()
    
        # Forearm
    ctx.save()
    ctx.translate(originForearmX, originForearmY)
    ctx.rectangle(0, 0, 0.05*SIZE, 0.05*SIZE)
    ctx.rotate(forearm)                             
    ctx.rectangle(0, -0.25*SIZE, -2*SIZE, 0.5*SIZE)
    ctx.stroke()
    ctx.restore()
    
    
        # Hand
    ctx.save()    
    ctx.translate(originHandX, originHandY)    
    ctx.rectangle(0, 0, 0.05*SIZE, 0.05*SIZE)
    ctx.rotate(forearm)
    ctx.stroke()
    
    ctx.rotate(hand)
    ctx.new_path()
    ctx.move_to(-0.25*SIZE*cos(-pi/4), 0.25*SIZE*sin(-pi/4))
    ctx.rel_line_to(0.5*SIZE*cos(-pi/4), -0.5*SIZE*sin(-pi/4))
    ctx.rel_line_to(SIZE*cos(-pi/4), SIZE*sin(-pi/4))
    ctx.rel_line_to(-0.5*SIZE*cos(-pi/4), 0.5*SIZE*sin(-pi/4))
    ctx.close_path()    
    ctx.stroke()    
        
        # # End Point
    ctx.rotate(-pi/4)
    ctx.translate(SIZE, 0)
    ctx.new_path()
    ctx.move_to(0, -0.2*SIZE)
    ctx.rel_line_to(0.4*SIZE, 0.15*SIZE)
    ctx.rel_line_to(-0.4*SIZE, 0)
    ctx.close_path()    
    ctx.move_to(0, 0.2*SIZE)
    ctx.rel_line_to(0.4*SIZE, -0.15*SIZE)
    ctx.rel_line_to(-0.4*SIZE, 0)
    ctx.close_path()    
    ctx.stroke()    
    ctx.restore() 
    

# ---------------------------------
# draw_pedro_top
# ---------------------------------
def draw_pedro_top(ctx):
    # Base
    ctx.save()
    ctx.translate(OriginTopX, OriginTopY)
    ctx.rotate(base)
    
    ctx.rectangle(-0.5*SIZE, 0.5*SIZE, SIZE, -SIZE)
    
    dx = mXL - OriginTopX
    dy = mYL - OriginTopY
    
    if (d*d - Z*Z)>=0: 
        dist = min([sqrt(dx*dx + dy*dy), sqrt(d*d-Z*Z)])
    if (c*c - Z*Z)>=0: 
        dist = max([dist, sqrt(c*c-Z*Z)])
        
    ctx.rectangle(-0.25*SIZE, -0.5*SIZE, 0.5*SIZE, -dist + 0.5*SIZE)    

    ctx.restore()
    ctx.stroke()

    
# ---------------------------------
# mouse_pressed
# ---------------------------------
def mouse_pressed(self, e):
    global isForearm
    isForearm = (e.button == 1)

# ---------------------------------
# mouse_dragged
# ---------------------------------
def mouse_dragged(self, e):
    global mXL, mYL
    global mXR, mYR
    global originHandX, originHandY
    
    if e.y > Height/2: 
        mXL = e.x
        mYL = e.y
        xyzToServoAngles(0, mXL - OriginTopX, mYL - OriginTopY, Z)
    else:
        if isForearm:
            mXL = e.x
            mYL = e.y
            xyzToServoAngles(1, mXL - originForearmX, mYL - originForearmY, Z)
            
        else :
            mXR = e.x
            mYR = e.y
            xyzToServoAngles(2, mXR - originHandX, mYR - originHandY, Z)
        
    originHandX = originForearmX + (length_Forearm)*cos(forearm - pi)
    originHandY = originForearmY + (length_Forearm)*sin(forearm - pi) 
    drawingarea.queue_draw()


# Inverse Kinematics:
# From Cartesian to Servo Angles
# ---------------------------------
# xyzToServoAngles
# ---------------------------------
def xyzToServoAngles(choice,x, y, z):
    global base, forearm, hand,r, Z
    global outOfReach
    outOfReach = False
    
    if choice == 0:
        a = length_Forearm
        b = length_Hand + length_EndPoint     
        r = sqrt(x*x + y*y)
        R = sqrt(r*r + z*z)
        Z = z
    
        if Z >= 0 and Z <= d and R > (a-b) and r < (a+b) and R < (a+b):
            base     = atan2(y,x) + pi/2
            forearm  = -acos((a*a + R*R - b*b)/(2*a*R)) - acos(r/R) + pi
            hand     = -acos((a*a + b*b - R*R)/(2*a*b)) + pi/4
        else:
            outOfReach = True
    
    elif choice == 1:
        forearm = atan2(y, x) + pi
    
    elif choice == 2:
        hand = atan2(y, x) + pi/4 - forearm        
    
    # Set limits
    if base > pi/2 and base < pi:
        base = pi/2
        outOfReach = True
    elif base <= -pi/2 or base >pi:
        base = -pi/2
        outOfReach = True

    if forearm >= pi and forearm < pi*3/2:
        forearm = pi
        outOfReach = True
    elif forearm <= 0 or forearm > pi*3/2:
        forearm = 0
        outOfReach = True

    if forearm > pi/4:
        if hand < -pi or hand > pi/2:
            hand = -pi
            outOfReach = True
        elif hand > 0 and hand < pi/2:
            hand = 0
            outOfReach = True
    else:
        hand -= pi/4
        if hand > -pi/4 and hand < pi/2:
            hand = -pi/4
            outOfReach = True
        elif hand > 0 and hand > pi/2:
            hand = -pi - forearm
            outOfReach = True
        hand += pi/4
        
        
def main():
    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    win.set_default_size(Width, Height)
    
    global drawingarea
    drawingarea = Gtk.DrawingArea()
    drawingarea.connect('draw', draw)
    
    drawing_event_box = Gtk.EventBox()
    drawing_event_box.add(drawingarea)
    drawing_event_box.connect('button-press-event', mouse_pressed)
    drawing_event_box.connect('motion-notify-event', mouse_dragged)

    win.add(drawing_event_box)
    win.show_all()
    Gtk.main()
    
if __name__ == '__main__':
    main()


