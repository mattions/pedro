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
Z0 = Z
d = length_Forearm + length_Hand + length_EndPoint
c = length_Forearm - length_Hand - length_EndPoint
r = length_Forearm
r0 = r

mXL = 0
mYL = 0
mXR = 0
mYR = 0
mXik = 0
mYik = 0

OriginSideX = d 
OriginSideY = d + SIZE
OriginTopX = 2*d + SIZE + OriginSideX
OriginTopY = d + SIZE

Width = 4*d + 3*SIZE
Height = OriginTopY + SIZE

originForearmX = OriginSideX 
originForearmY = OriginSideY - 0.5*SIZE
originHandX = originForearmX - length_Forearm
originHandY = originForearmY


base = 0
forearm = 0
hand = 0

isForearm = True
outOfReach = False
lockHandAndForearm = False

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
    ctx.move_to(-SIZE +Width/2, 0)
    ctx.rel_line_to(0, Height)
    ctx.rectangle(Width - 0.5*SIZE, 0.5*SIZE, - 0.5*SIZE, d )
    ctx.stroke()
    
    ctx.new_path()
    ctx.set_dash([SIZE/4.0, SIZE/4.0], 0)
    if (d*d - Z*Z)>=0: ctx.arc(OriginTopX, OriginTopY, sqrt(d*d-Z*Z), pi, 2*pi)
    if (c*c - Z*Z)>=0: ctx.arc(OriginTopX, OriginTopY, sqrt(c*c-Z*Z), pi, 2*pi)
    ctx.close_path()
    ctx.stroke()

    ctx.set_dash([], 0)
    if not outOfReach:
        global r0, Z0
        r0 = r
        Z0 = Z
    if not lockHandAndForearm:
        ctx.rectangle(
            OriginSideX + r0,
            OriginSideY - 0.5*SIZE - Z0,
            0.05*SIZE, 0.05*SIZE)
        ctx.stroke()
        
        ctx.new_path()
        ctx.move_to(Width - SIZE, OriginSideY - 0.5*SIZE - Z0)
        ctx.rel_line_to(0.5*SIZE, 0)

        ctx.stroke()
    

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
        
    ctx.rectangle(0, -0.25*SIZE, - r0, 0.5*SIZE)    

    ctx.restore()
    ctx.stroke()

# ---------------------------------
# draw_text
# ---------------------------------
def draw_text(ctx):
    ctx.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, 
            cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(TXT_SIZE)
    ctx.move_to(0.01*SIZE, TXT_SIZE)
    ctx.show_text('Base: ' + str(int(degrees(base))))
    ctx.move_to(0.01*SIZE, 2*TXT_SIZE)
    ctx.show_text('Forearm: '+ str(int(degrees(forearm))))
    ctx.move_to(0.01*SIZE, 3*TXT_SIZE)
    ctx.show_text('Hand: '+ str(int(degrees(-hand))))
    if outOfReach:        
        ctx.set_source_rgb(1, 0, 0) 
        ctx.move_to(0.01*SIZE, 4*TXT_SIZE)
        #ctx.move_to(-3*TXT_SIZE + Width/2, 0.5*SIZE + Height/2)
        ctx.show_text('OUT OF REACH !!!')
    
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
    global mXik, mYik
    global originHandX, originHandY
    global outOfReach
    
    if e.x > Width/2 and e.x < Width - 1.5*SIZE: 
        mXik = e.x
        mYik = e.y
        xyzToServoAngles(0, mXik - OriginTopX, mYik - OriginTopY, Z)
    else:
        if e.x > Width - 1.5*SIZE :
            if e.x < Width - 0.5*SIZE and e.x > Width - SIZE and e.y > 0.5*SIZE and e.y < d + 0.5*SIZE:
                xyzToServoAngles(0, mXik - OriginTopX, mYik - OriginTopY, d + 0.5*SIZE - e.y)
            else:
                outOfReach = True
        elif isForearm:
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

def check_toggled(e):
    global lockHandAndForearm
    lockHandAndForearm ^=1

# Inverse Kinematics:
# From Cartesian to Servo Angles
# ---------------------------------
# xyzToServoAngles
# ---------------------------------
def xyzToServoAngles(choice,x, y, z):
    global base, forearm, hand, r, Z
    global outOfReach
    outOfReach = False
    base0 = base
    forearm0 = forearm
    hand0 = hand
    
    if choice == 0:
        a = length_Forearm
        b = length_Hand + length_EndPoint     
        r = sqrt(x*x + y*y)
        
        if r > d:
            r = d
        
        R = sqrt(r*r + z*z)
        
        if z <= 0:
            Z = 0
        elif z >= d + 0.5*SIZE:
            z = d + 0.5*SIZE
        else:
            Z = z
    
        if Z >= 0 and Z <= d and R > (a-b) and R < (a+b):
            base0     = atan2(y,x) + pi
            if not lockHandAndForearm:
                forearm0  = -acos((a*a + R*R - b*b)/(2*a*R)) - acos(r/R) + pi
                hand0     = -acos((a*a + b*b - R*R)/(2*a*b)) + pi/4
        else:
            outOfReach = True
    
    elif choice == 1:
        forearm0 = atan2(y, x) + pi              
    
    elif choice == 2:
        hand0 = atan2(y, x) + pi/4 - forearm0    
    
    # Set limits
    if base0 > pi and base0 < pi*3/2:
        base0 = pi
        outOfReach = True
    elif base0 > pi and base0 > pi*3/2:
        base0 = 0
        outOfReach = True

    if forearm0 >= pi and forearm0 < pi*3/2:
        forearm0 = pi
        outOfReach = True
    elif forearm0 <= 0 or forearm0 >= pi*3/2:
        forearm0 = 0
        outOfReach = True

    if forearm0 > pi/4:
        if hand0 < -pi or hand0 > pi/2:
            hand0 = -pi
            outOfReach = True
        elif hand0 > 0 and hand0 < pi/2:
            hand0 = 0
            outOfReach = True
    else:
        hand0 -= pi/4
        if hand0 > -pi/4 and hand0 < pi/2:
            hand0 = -pi/4
            outOfReach = True
        elif hand0 > 0 and hand0 > pi/2:
            hand0 = -pi - forearm0
            outOfReach = True
        hand0 += pi/4

    if not outOfReach:
        base = base0
        forearm = forearm0
        hand = hand0

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

    check_useIk = Gtk.CheckButton("Lock Forearm & Hand")
    check_useIk.connect("toggled", check_toggled)
    
    box = Gtk.VBox()
    box.pack_start(check_useIk, False, True, 0)
    box.pack_start(drawing_event_box, True, True, 0)
    win.add(box)
    win.show_all()
    Gtk.main()
    
if __name__ == '__main__':
    main()


