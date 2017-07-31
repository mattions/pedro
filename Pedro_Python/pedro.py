#============================================================================================================
#                              PEDRO : Programming Educational Robot
#============================================================================================================
#!/usr/bin/env python
#title           :pedro.py
#description     :Interface for Pedro Petit Robot an open source 3D robotic arm, with serial USB control
#authors         :Almoutazar Saandi, Mohamed Salim Wadaane
#date            :2016-2017
#version         :1.0
#usage           :python3 pedro.py
#python_version  :3.6.1  
#============================================================================================================

import sys, os
import glob
import serial
import gi
import glib
import time
import cairo
from math import pi, atan2, sin, cos, degrees, acos, asin, sqrt
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import threading
#from threading import Thread
GObject.threads_init()

screen = Gdk.Screen.get_default()
#print (screen.get_width(), screen.get_height())

global pedro_combo
pedro_combo = Gtk.ComboBoxText()

global pedro_list
pedro_list = {}

global close_app
close_app = False

global mouseClick
mouseClick = ""

notebook = Gtk.Notebook()

global ser
ser = None

global lockServo1, lockServo2, lockServo3, lockServo4
lockServo1 = False
lockServo2 = False
lockServo3 = False
lockServo4 = False

global servocmd
servocmd = 0

btn1Up = Gtk.Button("Up")
btn1Down = Gtk.Button("Down")
btn2Up = Gtk.Button("Up")
btn2Down = Gtk.Button("Down")
btn3Up = Gtk.Button("Up")
btn3Down = Gtk.Button("Down")
btn4Up = Gtk.Button("Up")
btn4Down = Gtk.Button("Down")

global serv1_chg, serv2_chg, serv3_chg, serv4_chg
serv1_chg = False
serv2_chg = False
serv3_chg = False
serv4_chg = False

global servo_change
servo_change = False

global old_mouse1, old_mouse2, old_mouse3, old_mouse4
old_mouse1 = None
old_mouse2 = None
old_mouse3 = None
old_mouse4 = None

global indexFlowbox
indexFlowbox = 0

global flowbox, flowbox2, flowbox3, flowbox4
flowbox1 = Gtk.FlowBox()
flowbox2 = Gtk.FlowBox()
flowbox3 = Gtk.FlowBox()
flowbox4 = Gtk.FlowBox()

serv1Lbl = Gtk.Label("50")
serv2Lbl = Gtk.Label("50")
serv3Lbl = Gtk.Label("50")
serv4Lbl = Gtk.Label("50")

global updateSerial
updateSerial = True

global checkPedro
checkPedro = True

global initApp
initApp = False

THR_LOCK = threading.Lock()

#=======================================
# For cairo
#=======================================
SIZE = 30
Width = 3*SIZE
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
useIk = True
#=======================================


#=======================================
# Update_Serial
#=======================================
class Update_Serial():
    
    # ---------------------------------
    # __init__
    # ---------------------------------
    def __init__(self):
        self.displayNoPedro = False

    # ---------------------------------
    # serial_ports
    # ---------------------------------
    def serial_ports(self):
        global updateSerial
        print (str(updateSerial))
        if updateSerial:
            #if not self.displayNoPedro:
            #    self.displayNoPedro = True
            #    print ("*** No pedro connected! ***")
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                # this excludes your current terminal "/dev/tty"
                ports = glob.glob('/dev/tty[A-Za-z]*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            else:
                raise EnvironmentError('Unsupported platform')
            global pedro_list
            global ser
            pedro_list.clear()
            #pedro_combo.append_text("No Robot Pedro ")
            for port in ports:
                try:
                    ser = serial.Serial(port,\
                                        baudrate=9600,\
                                        timeout=1)
                    ser.write(bytearray([9, 1, 1, 0, 3, 1]))
                    ser_msg = ser.readline()
                    ser.close()
                    if True:
                    #if ser_msg.decode('utf-8') == "Hi! Im Pedro":
                        print(ser_msg.decode('utf-8'))
                        pedro_list["Robot Pedro " + str(len(pedro_list)+1)] = port
                        pedro_combo.append_text("Robot Pedro " + str(len(pedro_list)))
                        print (port)
                        print (str(len(pedro_list)))
                    #del pedro_list["No Robot Pedro"] #le faire une seule fois
                    #self.window.show_all()
                except (OSError, serial.SerialException):
                    pass
            pedro_combo.set_active(0)
            updateSerial = False


#=======================================
# Send_Cmd
#=======================================
class Send_Cmd(threading.Thread):
    pause = threading.Event()
    
    # ---------------------------------
    # start
    # ---------------------------------
    def start(self, *args):
        super(Send_Cmd, self).start()
    
    # ---------------------------------
    # run
    # ---------------------------------
    def run(self):
        #global ser
        global servo_change
        global serv1_chg, serv2_chg, serv3_chg, serv4_chg
        # if there is stuff in the queue...
        while not close_app:
            self.pause.wait()
            GObject.idle_add(self.update_servo)
            time.sleep(0.02)

    # ---------------------------------
    # send_cmd
    # ---------------------------------
    def send_cmd(self, numServ):
        try:
            ser.write(bytearray([numServ, servocmd]))
        except:
            print ("No Pedro Connected")

    # ---------------------------------
    # send_cmd
    # ---------------------------------
    def update_servo(self):
        if serv1_chg:
            if servocmd == 11 and int(serv1Lbl.get_label()) < 180:
                serv1Lbl.set_label(str(int(serv1Lbl.get_label()) + 1))
                self.send_cmd(1)
            elif servocmd == 22 and int(serv1Lbl.get_label()) > 0:
                serv1Lbl.set_label(str(int(serv1Lbl.get_label()) - 1))
                self.send_cmd(1)    
        elif serv2_chg:
            if servocmd == 11 and int(serv2Lbl.get_label()) < 180:
                serv2Lbl.set_label(str(int(serv2Lbl.get_label()) + 1))
                self.send_cmd(2)
            elif servocmd == 22 and int(serv2Lbl.get_label()) > 0:
                serv2Lbl.set_label(str(int(serv2Lbl.get_label()) - 1))
                self.send_cmd(2)
        elif serv3_chg:
            if servocmd == 11 and int(serv3Lbl.get_label()) < 180:
                serv3Lbl.set_label(str(int(serv3Lbl.get_label()) + 1))
                self.send_cmd(3)
            elif servocmd == 22 and int(serv3Lbl.get_label()) > 0:
                serv3Lbl.set_label(str(int(serv3Lbl.get_label()) - 1))
                self.send_cmd(3)
        elif serv4_chg:
            if servocmd == 11 and int(serv4Lbl.get_label()) < 180:
                serv4Lbl.set_label(str(int(serv4Lbl.get_label()) + 1))
                self.send_cmd(4)
            elif servocmd == 22 and int(serv4Lbl.get_label()) > 0:
                serv4Lbl.set_label(str(int(serv4Lbl.get_label()) - 1))
                self.send_cmd(4)

#=======================================
# Pedro
#=======================================
class Pedro(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Pedro")
        
        hb = Gtk.HeaderBar()
        #hb.set_show_close_button(True)
        hb.props.title = "Pedro"
        self.set_titlebar(hb)
        color_widget(self, 'White')
        self.set_size_request(screen.get_width()/1.5, screen.get_height()/1.1)
        self.set_resizable(False)
        self.mouseClick = False
        width, height = self.get_size()
        sepa = Gtk.VSeparator()
        buttonClose = Gtk.Button("Close")
        buttonClose.connect("clicked", self.on_close_clicked)
        connected = Gtk.Label("Connected : ")
        btnUpdate = Gtk.Button("Serial")
        btnUpdate.connect("clicked", self.on_serial_updated)

        hb.pack_start(connected)
        hb.pack_start(pedro_combo)
        hb.pack_start(btnUpdate)

        #serial_port = Serial_Port()
        #serial_port.serial_ports()

        pedro_combo.connect("changed", self.on_pedro_combo_changed)
        hb.pack_end(buttonClose)

        vpaned = Gtk.VPaned()
        hpaned = Gtk.HPaned()
        #vpaned.add1(hpaned) 

        ###########################################################
               
        boxV = Gtk.VBox()
        boxH = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        servboxH = Gtk.HBox()
        servboxV1 = Gtk.VBox()
        servboxV2 = Gtk.VBox()
        servboxV3 = Gtk.VBox()
        servboxV4 = Gtk.VBox()
        box5 = Gtk.VBox()
        scrolled1 = Gtk.ScrolledWindow()
        scrolled1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box7 = Gtk.HBox()
        boxH.pack_start(box7, False, False, 10)
        boxH.pack_start(servboxH, False, False, 0)
        boxH.set_size_request(width/2, height/3)
        boxV.pack_start(boxH, False, False, 0)

        wdth = width/4
        hght = height/4

        frame1 = Gtk.Frame()
        label1 = Gtk.Label("Servo 1")
        boxV1 = Gtk.VBox()
        boxH1 = Gtk.HBox()
        btn1Up.set_size_request(wdth/2.5, hght/2.5)
        btn1Down.set_size_request(wdth/2.5, hght/2.5)
        btn1Up.connect('button-press-event', self.on_btn1Up_press)
        btn1Up.connect('button-release-event', self.on_btn1Up_release)
        btn1Down.connect('button-press-event', self.on_btn1Down_press)
        btn1Down.connect('button-release-event', self.on_btn1Up_release)
        boxV1.pack_start(label1, False, False, 10)
        boxV1.pack_start(btn1Up, False, False, 10)
        boxV1.pack_start(serv1Lbl, False, False, 10)
        boxV1.pack_start(btn1Down, False, False, 10)
        boxH1.pack_start(boxV1, False, False, 10)
        frame1.add(boxH1)
        servboxV1.pack_start(frame1, False, False, 10)
        servboxH.pack_start(servboxV1, False, False, 0)
        
        frame2 = Gtk.Frame()
        label2 = Gtk.Label("Servo 2")
        boxV2 = Gtk.VBox()
        boxH2 = Gtk.HBox()
        btn2Up.set_size_request(wdth/2.5, hght/2.5)
        btn2Down.set_size_request(wdth/2.5, hght/2.5)
        btn2Up.connect('button-press-event', self.on_btn2Up_press)
        btn2Up.connect('button-release-event', self.on_btn2Up_release)
        btn2Down.connect('button-press-event', self.on_btn2Down_press)
        btn2Down.connect('button-release-event', self.on_btn2Up_release)
        boxV2.pack_start(label2, False, False, 10)
        boxV2.pack_start(btn2Up, False, False, 10)
        boxV2.pack_start(serv2Lbl, False, False, 10)
        boxV2.pack_start(btn2Down, False, False, 10)
        boxH2.pack_start(boxV2, False, False, 10)
        frame2.add(boxH2)
        servboxV2.pack_start(frame2, False, False, 10)
        servboxH.pack_start(servboxV2, False, False, 10)
        
        frame3 = Gtk.Frame()
        label3 = Gtk.Label("Servo 3")
        boxV3 = Gtk.VBox()
        boxH3 = Gtk.HBox()
        btn3Up.set_size_request(wdth/2.5, hght/2.5)
        btn3Down.set_size_request(wdth/2.5, hght/2.5)
        btn3Up.connect('button-press-event', self.on_btn3Up_press)
        btn3Up.connect('button-release-event', self.on_btn3Up_release)
        btn3Down.connect('button-press-event', self.on_btn3Down_press)
        btn3Down.connect('button-release-event', self.on_btn3Up_release)
        boxV3.pack_start(label3, False, False, 10)
        boxV3.pack_start(btn3Up, False, False, 10)
        boxV3.pack_start(serv3Lbl, False, False, 10)
        boxV3.pack_start(btn3Down, False, False, 10)
        boxH3.pack_start(boxV3, False, False, 10)
        frame3.add(boxH3)
        servboxV3.pack_start(frame3, False, False, 10)
        servboxH.pack_start(servboxV3, False, False, 10)
        
        frame4 = Gtk.Frame()
        label4 = Gtk.Label("Servo 4")
        boxV4 = Gtk.VBox()
        boxH4 = Gtk.HBox()
        btn4Up.set_size_request(wdth/2.5, hght/2.5)
        btn4Down.set_size_request(wdth/2.5, hght/2.5)
        btn4Up.connect('button-press-event', self.on_btn4Up_press)
        btn4Up.connect('button-release-event', self.on_btn4Up_release)
        btn4Down.connect('button-press-event', self.on_btn4Down_press)
        btn4Down.connect('button-release-event', self.on_btn4Up_release)
        boxV4.pack_start(label4, False, False, 10)
        boxV4.pack_start(btn4Up, False, False, 10)
        boxV4.pack_start(serv4Lbl, False, False, 10)
        boxV4.pack_start(btn4Down, False, False, 10)
        boxH4.pack_start(boxV4, False, False, 10)
        frame4.add(boxH4)
        servboxV4.pack_start(frame4, False, False, 10)
        servboxH.pack_start(servboxV4, False, False, 10)

        buttonRecord = Gtk.Button("Record")
        buttonRecord.connect("clicked", self.on_rec_clicked)
        buttonPLay = Gtk.Button("Play")
        buttonPLay.connect("clicked", self.on_play_clicked)
        buttonPause = Gtk.Button("Pause")
        buttonPause.connect("clicked", self.on_play_clicked)
        buttonStop = Gtk.Button("Stop")
        buttonStop.connect("clicked", self.on_stop_clicked)
        buttonRepeat = Gtk.CheckButton("Repeat one time")
        buttonRepeat.connect("toggled", self.on_repeat_clicked)
        buttonClear = Gtk.Button("Clear")
        buttonClear.connect("clicked", self.on_play_clicked)

        boxHSpeed = Gtk.HBox()
        speedLabel = Gtk.Label("Speed: ")
        ad1 = Gtk.Adjustment(1, 1, 4, 5, 10, 0)
        self.speed_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.speed_scale.set_digits(0)
        self.speed_scale.set_hexpand(True)
        self.speed_scale.set_valign(Gtk.Align.START)
        self.speed_scale.connect("value-changed", self.update_speed)
        boxHSpeed.pack_start(speedLabel, False, False, 0)
        boxHSpeed.pack_start(self.speed_scale, True, True, 0)

        box5.pack_start(buttonRecord, False, False, 10)
        box5.pack_start(buttonPLay, False, False, 10)
        box5.pack_start(buttonPause, False, False, 10)
        box5.pack_start(buttonStop, False, False, 0)
        box5.pack_start(buttonRepeat, False, False, 10)
        box5.pack_start(buttonClear, False, False, 10)
        box5.pack_start(boxHSpeed, False, False, 10)
        boxH.pack_start(box5, True, True, 0)

        box6 = Gtk.HBox()
        boxH.pack_start(box6, False, False, 10)

        ###########################################################
        align = Gtk.Alignment()
        pbar = Gtk.ProgressBar()
        align.add(pbar)

        boxHBar = Gtk.HBox()

        boxH1Bar = Gtk.HBox()
        boxH2Bar = Gtk.HBox()
        boxHBar.pack_start(boxH1Bar, False, False, 10)
        boxHBar.pack_start(align, True, True, 0)
        boxHBar.pack_start(boxH2Bar, False, False, 10)
        
        memoryLabel = Gtk.Label("Memory used: 0%")
        boxV.pack_start(memoryLabel, False, False, 10)
        boxV.pack_start(boxHBar, False, False, 10)

        ###########################################################

        boxLockH = Gtk.HBox()
        drawing_area = Gtk.EventBox()
        boxVdraw = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        drawing_area.connect('button-press-event', self.on_area_button_press)
        drawing_area.connect('button-release-event', self.on_area_button_release)
        drawing_area.connect('motion-notify-event', self.on_area_motion)

        drawLabel = Gtk.Label("Click on right/left button mouse for move Pedro...")
        drawing_area.add(drawLabel)

        global drawingarea
        drawingarea = Gtk.DrawingArea()
        drawingarea.connect('draw', self.draw)
        
        drawing_event_box = Gtk.EventBox()      #   Needed to grab mouse click events.
        drawing_event_box.add(drawingarea)
        drawing_event_box.connect('button-press-event', self.mouse_pressed)
        drawing_event_box.connect('motion-notify-event', self.mouse_dragged)


        frameDraw = Gtk.Frame()
        frameDraw.add(drawing_event_box)

        boxH = Gtk.HBox()
        boxV1 = Gtk.VBox()
        boxV2 = Gtk.VBox()

        boxH1 = Gtk.HBox()
        boxH2 = Gtk.HBox()
        boxH.pack_start(boxH1, False, False, 10)
        boxH.pack_start(frameDraw, True, True, 0)
        boxH.pack_start(boxH2, False, False, 10)

        boxV1.pack_start(boxH, True, True, 10)

        boxVdraw.pack_start(boxV1, True, True, 0)
        boxVdraw.pack_start(boxV2, False, False, 0)

        boxV.pack_start(boxVdraw, True, True, 10)

        ###################################################
        
        self.add(boxV)
        global initApp
        initApp = True


#=======================================
# For cairo
#=======================================
    # ---------------------------------
    # draw
    # ---------------------------------
    def draw(self, da, ctx):
        ctx.set_source_rgb(0, 0, 0)         #   Set our color to black
        ctx.set_line_width(SIZE / 20)           #   Set line width
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)    #   Set our line end shape
        
        self.draw_pedro(ctx)

    # ---------------------------------
    # draw_pedro
    # ---------------------------------
    def draw_pedro(self, ctx):

        global originX
        global originY
        global forearm
        global hand
        global mXL
        global mYL
        global mXR
        global mYR
        
            # Base
        #ctx.save()
        #ctx.rotate(base)           #   rotate everything that comes next
        ctx.rectangle(SIZE,5*SIZE,SIZE,-SIZE)
                
            # Forearm   ctx.save()                                      #   Save initial transformations: translations, rotations etc
        ctx.translate(1.5*SIZE, 4*SIZE)                 #   Move origin to top and middle of base rectangle
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
        
        ctx.rectangle(mXL, mYL,0.05*SIZE,0.05*SIZE)
        ctx.rectangle(1.5*SIZE+r, 
                      4*SIZE-Y,
                      0.05*SIZE,0.05*SIZE)
        ctx.stroke()                                    #   Draw all previous shapes.
        
        if useIk:
            ctx.set_dash([SIZE / 4.0, SIZE / 4.0], 0)
            ctx.arc(0,0,length_Forearm+length_Hand+length_EndPoint,0, pi/2)
            ctx.stroke()
            c = length_Forearm-length_EndPoint-length_Hand
            ctx.arc(0,0,sqrt(c*c-Y*Y),0, pi/2)
            ctx.stroke()
        
        print('Base: ' + str(int(degrees(base)))+' Forearm: '+str(int(degrees(forearm)))+ ' Hand: '+ str(int(degrees(hand))))   #   print the angles in degrees, so we can send to servo.
        
    # ---------------------------------
    # mouse_pressed
    # ---------------------------------
    def mouse_pressed(self, widget, e):
        global isForearm
        isForearm = (e.button == 1)     # Rotate forearm if the left mouse button is clicked.
    
    # ---------------------------------
    # mouse_dragged
    # ---------------------------------
    def mouse_dragged(self, widget, e):
        global mXL, mYL
        global mXR, mYR
        
        if useIk: 
            mXL=e.x
            mYL=e.y
            self.xyzToServoAngles(mXL, mYL, 0.1*SIZE)
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
    def xyzToServoAngles(self, x, y, z):
        global base, forearm, hand,r, Y
        a = length_Forearm                  # Lenght of Forearm
        b = length_Hand + length_EndPoint       # Length of Hand
        r = sqrt(x*x + y*y)
        R = sqrt(r*r + z*z)
        Y = z
        if R > (a-b) and r < (a+b) and R < (a+b): # 
            base = atan2(y,x)
            forearm = -acos((a*a + R*R - b*b)/(2*a*R)) - acos(r/R) +pi/2
            hand = -acos((a*a + b*b - R*R)/(2*a*b)) + pi
        else:
            print('Out of reach !!!')

#=======================================



    # ---------------------------------
    # checkerboard_draw_event
    # ---------------------------------
    def checkerboard_draw_event(self, da, cairo_ctx):

        # At the start of a draw handler, a clip region has been set on
        # the Cairo context, and the contents have been cleared to the
        # widget's background color. The docs for
        # gdk_window_begin_paint_region() give more details on how this
        # works.
        check_size = 10
        spacing = 2
        print ("HELLO!!!")
        xcount = 0
        i = spacing
        width = da.get_allocated_width()
        height = da.get_allocated_height()

        while i < width:
            j = spacing
            ycount = xcount % 2  # start with even/odd depending on row
            while j < height:
                if ycount % 2:
                    cairo_ctx.set_source_rgb(0.45777, 0, 0.45777)
                else:
                    cairo_ctx.set_source_rgb(1, 1, 1)
                # If we're outside the clip this will do nothing.
                cairo_ctx.rectangle(i, j,
                                    check_size,
                                    check_size)
                cairo_ctx.fill()

                j += check_size + spacing
                ycount += 1

            i += check_size + spacing
            xcount += 1

        return True

    # ---------------------------------
    # update_speed
    # ---------------------------------
    def update_speed(self, event):
        print("speed value: " + str(int(self.speed_scale.get_value())))


    # ---------------------------------
    # on_repeat_clicked
    # ---------------------------------
    def on_repeat_clicked(self, button):
        print("repeat button was toggled " + str(button.get_active()))

    # ---------------------------------
    # on_lock_servo1
    # ---------------------------------
    def on_lock_servo1(self, button):
        global lockServo1
        print("lock servo 1 was toggled " + str(button.get_active()))
        if button.get_active():
            lockServo1 = True
        else:
            lockServo1 = False

    # ---------------------------------
    # on_lock_servo2
    # ---------------------------------
    def on_lock_servo2(self, button):
        global lockServo2
        print("lock servo 2 was toggled " + str(button.get_active()))
        if button.get_active():
            lockServo2 = True
        else:
            lockServo2 = False

    # ---------------------------------
    # on_lock_servo3
    # ---------------------------------
    def on_lock_servo3(self, button):
        global lockServo3
        print("lock servo 3 was toggled " + str(button.get_active()))
        if button.get_active():
            lockServo3 = True
        else:
            lockServo3 = False

    # ---------------------------------
    # on_lock_servo4
    # ---------------------------------
    def on_lock_servo4(self, button):
        global lockServo4
        print("lock servo 4 was toggled " + str(button.get_active()))
        if button.get_active():
            lockServo4 = True
        else:
            lockServo4 = False

    # ---------------------------------
    # on_play_clicked
    # ---------------------------------
    def on_play_clicked(self, button):
        print("play button was clicked")
        #rec = [0, 0, 99]
        #data = bytearray(rec)
        #ser.write(data)

    # ---------------------------------
    # on_rec_clicked
    # ---------------------------------
    def on_rec_clicked(self, button):
        print("rec button was clicked")
        rec = [0, 0, 88]
        data = bytearray(rec)
        ser.write(data)

    # ---------------------------------
    # on_stop_clicked
    # ---------------------------------
    def on_stop_clicked(self, button):
        print("stop button was clicked")
        rec = [0, 0, 77]
        data = bytearray(rec)
        ser.write(data)

    # ---------------------------------
    # on_close_clicked
    # ---------------------------------
    def on_close_clicked(self, button):
        global close_app
        close_app = True
        print("Closing application")
        Gtk.main_quit()
        window.destroy()
        print("Closing application****")

    # ---------------------------------
    # ressource_path
    # ---------------------------------
    def ressource_path(self,relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path) 

    # ---------------------------------
    # on_serial_updated
    # ---------------------------------
    def on_serial_updated(self, btn):
        global updateSerial, ser
        pedro_combo.get_model().clear()
        ser.close()
        updateSerial = True
        update_ser.serial_ports()
    
    # ---------------------------------
    # on_pedro_combo_changed
    # ---------------------------------
    def on_pedro_combo_changed(self, combo):
        pedro_select = combo.get_active_iter()
        global ser, checkPedro
        if pedro_select != None: #a voir plus necessaire si fenetre bloquante "no pedro"
            model = combo.get_model()
            select = model[pedro_select][0]
            # ser.close()
            ser = serial.Serial(str(pedro_list[select]),\
                                baudrate=9600,\
                                timeout=1)
            ser.write(bytearray([9, 1, 1, 0, 3, 1]))
            print ("Selected: Pedro: " + str(pedro_list[select]))

    # ---------------------------------
    # on_area_button_press
    # ---------------------------------
    def on_area_button_press(self, widget, event):
        global mouseClick
        if event.button == 1:
            print ("left click")
            mouseClick = "left"
        elif event.button == 2:
            print ("middle click")
        elif event.button == 3:
            print ("right click")
            mouseClick = "right"
        self.mouseClick = True

    # ---------------------------------
    # on_area_button_release
    # ---------------------------------
    def on_area_button_release(self, widget, event):
        global old_mouse1, old_mouse2, old_mouse3, old_mouse4
        global servo_change
        global serv1_chg, serv2_chg, serv3_chg, serv4_chg
        print ('NO')
        if mouseClick == "left":
           old_mouse1 = int(event.x)
           old_mouse2 = int(event.y)
           serv1_chg = False
           serv2_chg = False
        elif mouseClick == "right":
           old_mouse3 = int(event.x)
           old_mouse4 = int(event.y)
        self.mouseClick = False
        servo_change = False
        serv1_chg = False

    # ---------------------------------
    # on_area_motion
    # ---------------------------------
    def on_area_motion(self, widget, event):
        global old_mouse1, old_mouse2, old_mouse3, old_mouse4
        global lockServo1, lockServo2, lockServo3, lockServo4
        global servo_change
        global serv1_chg, serv2_chg, serv3_chg, serv4_chg
        global servocmd
        if self.mouseClick:
            servo_change = True
            if mouseClick == "left":
                if old_mouse1 == None:
                    old_mouse1 = int(event.x)
                if old_mouse2 == None:
                    old_mouse2 = int(event.y)
                if not lockServo1:
                    serv1_chg = True
                    if old_mouse1 > int(event.x) :
                        servocmd = 22
                        serv1Lbl.set_label(str(int(serv1Lbl.get_label()) - 1))
                    elif old_mouse1 < int(event.x):
                        servocmd = 11
                        serv1Lbl.set_label(str(int(serv1Lbl.get_label()) + 1))
                    old_mouse1 = int(event.x)
                if not lockServo2:
                    serv2_chg = True
                    if old_mouse2 > int(event.y) :
                        servocmd = 22
                        serv2Lbl.set_label(str(int(serv2Lbl.get_label()) - 1))
                    elif old_mouse2 < int(event.y):
                        servocmd = 11
                        serv2Lbl.set_label(str(int(serv2Lbl.get_label()) + 1))
                    old_mouse2 = int(event.y)
            elif mouseClick == "right":
                if old_mouse3 == None:
                    old_mouse3 = int(event.x)
                if old_mouse4 == None:
                    old_mouse4 = int(event.y)
                if not lockServo3:
                    if old_mouse3 > int(event.x) :
                        serv3Lbl.set_label(str(int(serv3Lbl.get_label()) - 1))
                    elif old_mouse3 < int(event.x):
                        serv3Lbl.set_label(str(int(serv3Lbl.get_label()) + 1))
                    old_mouse3 = int(event.x)
                if not lockServo4:
                    if old_mouse4 > int(event.y) :
                        serv4Lbl.set_label(str(int(serv4Lbl.get_label()) - 1))
                    elif old_mouse4 < int(event.y):
                        serv4Lbl.set_label(str(int(serv4Lbl.get_label()) + 1))
                    old_mouse4 = int(event.y)
          
    # ---------------------------------
    # on_btn1Up_press
    # ---------------------------------    
    def on_btn1Up_press(self, widget, event):
        #global servo_change
        global serv1_chg
        global servocmd
        notebook.set_current_page(0)
        servocmd = 11
        #servo_change = True
        serv1_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn1Up_release
    # ---------------------------------  
    def on_btn1Up_release(self, widget, event):
        #global servo_change
        global serv1_chg
        #servo_change = False
        serv1_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

    # ---------------------------------
    # on_btn1Down_press
    # ---------------------------------    
    def on_btn1Down_press(self, widget, event):
        #global servo_change
        global serv1_chg
        global servocmd
        notebook.set_current_page(0)
        servocmd = 22
        #servo_change = True
        serv1_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn1Down_release
    # ---------------------------------  
    def on_btn1Down_release(self, widget, event):
        #global servo_change
        global serv1_chg
        #servo_change = False
        serv1_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

#########

    # ---------------------------------
    # on_btn2Up_press
    # ---------------------------------    
    def on_btn2Up_press(self, widget, event):
        global servo_change
        global serv2_chg
        global servocmd
        notebook.set_current_page(1)
        servocmd = 11
        servo_change = True
        serv2_chg = True

    # ---------------------------------
    # on_btn2Up_release
    # ---------------------------------  
    def on_btn2Up_release(self, widget, event):
        global servo_change
        global serv2_chg
        servo_change = False
        serv2_chg = False

    # ---------------------------------
    # on_btn2Down_press
    # ---------------------------------    
    def on_btn2Down_press(self, widget, event):
        global servo_change
        global serv2_chg
        global servocmd
        notebook.set_current_page(1)
        servocmd = 22
        servo_change = True
        serv2_chg = True

    # ---------------------------------
    # on_btn2Down_release
    # ---------------------------------  
    def on_btn2Down_release(self, widget, event):
        global servo_change
        global serv2_chg
        servo_change = False
        serv2_chg = False

#########

    # ---------------------------------
    # on_btn3Up_press
    # ---------------------------------    
    def on_btn3Up_press(self, widget, event):
        global servo_change
        global serv3_chg
        global servocmd
        notebook.set_current_page(2)
        servocmd = 11
        servo_change = True
        serv3_chg = True

    # ---------------------------------
    # on_btn3Up_release
    # ---------------------------------  
    def on_btn3Up_release(self, widget, event):
        global servo_change
        global serv3_chg
        servo_change = False
        serv3_chg = False

    # ---------------------------------
    # on_btn3Down_press
    # ---------------------------------    
    def on_btn3Down_press(self, widget, event):
        global servo_change
        global serv3_chg
        global servocmd
        notebook.set_current_page(2)
        servocmd = 22
        servo_change = True
        serv3_chg = True

    # ---------------------------------
    # on_btn3Down_release
    # ---------------------------------  
    def on_btn3Down_release(self, widget, event):
        global servo_change
        global serv3_chg
        servo_change = False
        serv3_chg = False

########

    # ---------------------------------
    # on_btn4Up_press
    # ---------------------------------    
    def on_btn4Up_press(self, widget, event):
        global servo_change
        global serv4_chg
        global servocmd
        notebook.set_current_page(3)
        servocmd = 11
        servo_change = True
        serv4_chg = True

    # ---------------------------------
    # on_btn4Up_release
    # ---------------------------------  
    def on_btn4Up_release(self, widget, event):
        global servo_change
        global serv4_chg
        servo_change = False
        serv4_chg = False

    # ---------------------------------
    # on_btn4Down_press
    # ---------------------------------    
    def on_btn4Down_press(self, widget, event):
        global servo_change
        global serv4_chg
        global servocmd
        notebook.set_current_page(3)
        servocmd = 22
        servo_change = True
        serv4_chg = True

    # ---------------------------------
    # on_btn4Down_release
    # ---------------------------------  
    def on_btn4Down_release(self, widget, event):
        global servo_change
        global serv4_chg
        servo_change = False
        serv4_chg = False

    # ---------------------------------
    # color_swatch_new
    # --------------------------------- 
    def color_swatch_new(self, str_color):
        color = Gdk.color_parse(str_color)

        rgba = Gdk.RGBA.from_color(color)
        button = Gtk.Button()

        area = Gtk.DrawingArea()
        area.set_size_request(24, 24)
        area.override_background_color(0, rgba)

        button.add(area)

        return button

    # ---------------------------------
    # create_flowbox
    # --------------------------------- 
    def create_flowbox(self, flowbox):
        colors = [
        'AliceBlue',
        'AntiqueWhite',
        'AntiqueWhite1',
        'AntiqueWhite2',
        'AntiqueWhite3',
        'AntiqueWhite4',
        'aqua',
        'aquamarine',
        'aquamarine1',
        'aquamarine2',
        'aquamarine3',
        'aquamarine4',
        'azure',
        'azure1',
        'azure2',
        'azure3',
        'azure4',
        'beige',
        'bisque',
        'bisque1',
        'bisque2',
        'bisque3',
        'bisque4',
        'black',
        'BlanchedAlmond',
        'blue',
        'blue1',
        'blue2',
        'blue3',
        'blue4',
        'BlueViolet',
        'brown',
        'brown1',
        'brown2',
        'brown3',
        'brown4',
        'burlywood',
        'burlywood1',
        'burlywood2',
        'burlywood3',
        'burlywood4',
        'CadetBlue',
        'CadetBlue1',
        'CadetBlue2',
        'CadetBlue3',
        'CadetBlue4',
        'chartreuse',
        'chartreuse1',
        'chartreuse2',
        'chartreuse3',
        'chartreuse4',
        'chocolate',
        'chocolate1',
        'chocolate2',
        'chocolate3',
        'chocolate4',
        'coral',
        'coral1',
        'coral2',
        'coral3',
        'coral4'
        ]

        for i in range(0,255):
            LabelMem = Gtk.Label ("   255   ")
            FrameMem = Gtk.Frame() 
            color_widget(FrameMem, 'coral')
            FrameMem.add (LabelMem)
            flowbox.add(FrameMem)
            

def recv_thr():
    global ser
    while ser is not None:
        try:
            if not ser.readable() or not ser.inWaiting() > 0:
                continue
            THR_LOCK.acquire()
            ser_msg = ser.readline()
            if ser_msg.decode('utf-8') == "Hi! Im Pedro":
                print(ser_msg.decode('utf-8'))
            THR_LOCK.release()
        except:
            pass
# print("Pedro deconnected")
# ---------------------------------
# color_widget
# ---------------------------------
def color_widget(widget, color):
    color = Gdk.color_parse(color)
    rgba = Gdk.RGBA.from_color(color)
    widget.override_background_color(0, rgba)



update_ser = Update_Serial()
update_ser.serial_ports()

recv=threading.Thread(target=recv_thr)
recv.start()

thread_send_cmd = Send_Cmd()
window = Pedro()
window.connect("delete-event", Gtk.main_quit)
window.show_all()

#update_block = Update_Block_Memory()
#update_block.start()

Gtk.main()

#update_block.join()
