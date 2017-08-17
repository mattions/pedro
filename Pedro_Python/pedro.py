#============================================================================================================
#                              PEDRO : Programming Educational Robot
#============================================================================================================
#!/usr/bin/env python
#title           :pedro.py
#description     :Interface for Pedro Petit Robot an open source 3D robotic arm, with serial USB control
#authors         :Almoutazar Saandi, Mohamed Salim Wadaane
#emails          :almoutazar.saandi@gmail.com
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

global ser
ser = None

global lockServo1, lockServo2, lockServo3, lockServo4
lockServo1 = False
lockServo2 = False
lockServo3 = False
lockServo4 = False

global servocmd
servocmd = 0

btn1Up = Gtk.Button(name="servo", label="Up")
btn1Down = Gtk.Button(name="servo", label="Down")
btn2Up = Gtk.Button(name="servo", label="Up")
btn2Down = Gtk.Button(name="servo", label="Down")
btn3Up = Gtk.Button(name="servo", label="Up")
btn3Down = Gtk.Button(name="servo", label="Down")
btn4Up = Gtk.Button(name="servo", label="Up")
btn4Down = Gtk.Button(name="servo", label="Down")

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
global drawingarea

SIZE = 50
TXT_SIZE = SIZE/4
length_Forearm = 2*SIZE
length_Hand = 0.93*length_Forearm
length_EndPoint = 0.28*length_Forearm
length_Base = 0.5*length_Forearm

Z = 0
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
OriginTopX = 2*d + OriginSideX + SIZE
OriginTopY = d + SIZE

Width = 4*d + 4*SIZE
Height = OriginTopY + SIZE

originForearmX = OriginSideX
originForearmY = OriginSideY - 0.5*length_Base
originHandX = originForearmX - length_Forearm
originHandY = originForearmY


base = 0
forearm = 0
hand = 0

isForearm = True
outOfReach = False
lockHandAndForearm = False
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
                print ("lkjhljkhjlkhlk")
                ports = glob.glob('/dev/cu.*')
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
                        #print (str(len(pedro_list)))
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
    def send_cmd(self, numServ, angleServ):
        try:
            ser.write(bytearray([numServ, angleServ]))
        except:
            print ("No Pedro Connected")

    # ---------------------------------
    # send_cmd
    # ---------------------------------
    def update_servo(self):
        if serv1_chg:
            if servocmd == 11 and int(serv1Lbl.get_label()) < 180:
                serv1Lbl.set_label(str(int(serv1Lbl.get_label()) + 1))
                self.send_cmd(1, int(serv1Lbl.get_label()))
                #self.send_cmd(1)
            elif servocmd == 22 and int(serv1Lbl.get_label()) > 0:
                serv1Lbl.set_label(str(int(serv1Lbl.get_label()) - 1))
                self.send_cmd(1, int(serv1Lbl.get_label()))
                #self.send_cmd(1)
        elif serv2_chg:
            if servocmd == 11 and int(serv2Lbl.get_label()) < 180:
                serv2Lbl.set_label(str(int(serv2Lbl.get_label()) + 1))
                self.send_cmd(2, int(serv2Lbl.get_label()))
                #self.send_cmd(2)
            elif servocmd == 22 and int(serv2Lbl.get_label()) > 0:
                serv2Lbl.set_label(str(int(serv2Lbl.get_label()) - 1))
                self.send_cmd(2, int(serv2Lbl.get_label()))
                #self.send_cmd(2)
        elif serv3_chg:
            if servocmd == 11 and int(serv3Lbl.get_label()) < 180:
                serv3Lbl.set_label(str(int(serv3Lbl.get_label()) + 1))
                self.send_cmd(3, int(serv3Lbl.get_label()))
                #self.send_cmd(3)
            elif servocmd == 22 and int(serv3Lbl.get_label()) > 0:
                serv3Lbl.set_label(str(int(serv3Lbl.get_label()) - 1))
                self.send_cmd(3, int(serv3Lbl.get_label()))
                #self.send_cmd(3)
        elif serv4_chg:
            if servocmd == 11 and int(serv4Lbl.get_label()) < 180:
                serv4Lbl.set_label(str(int(serv4Lbl.get_label()) + 1))
                self.send_cmd(4, int(serv4Lbl.get_label()))
                #self.send_cmd(4)
            elif servocmd == 22 and int(serv4Lbl.get_label()) > 0:
                serv4Lbl.set_label(str(int(serv4Lbl.get_label()) - 1))
                self.send_cmd(4, int(serv4Lbl.get_label()))
                #self.send_cmd(4)

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
        #self.set_size_request(screen.get_width()/1.5, screen.get_height()/1.1)
        #self.set_resizable(False)
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
        servboxV = Gtk.VBox()

        servboxV1 = Gtk.VBox()
        servboxV2 = Gtk.VBox()
        servboxV3 = Gtk.VBox()
        servboxV4 = Gtk.VBox()
        
        boxHSpeed = Gtk.HBox()
        boxVSpeed = Gtk.VBox()

        speedLabel = Gtk.Label("Speed: ")
        ad1 = Gtk.Adjustment(1, 1, 4, 5, 10, 0)
        self.speed_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.speed_scale.set_digits(0)
        self.speed_scale.set_hexpand(True)
        self.speed_scale.set_valign(Gtk.Align.START)
        self.speed_scale.connect("value-changed", self.update_speed)
        boxHSpeed.pack_start(speedLabel, False, False, 0)
        boxHSpeed.pack_start(self.speed_scale, True, True, 0)
        boxVSpeed.pack_start(boxHSpeed, True, True, 0)

        servboxV.pack_start(servboxH, False, False, 0)
        servboxV.pack_start(boxVSpeed, False, False, 10)

        box5 = Gtk.VBox()
        scrolled1 = Gtk.ScrolledWindow()
        scrolled1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box7 = Gtk.HBox()
        boxH.pack_start(box7, False, False, 10)
        boxH.pack_start(servboxV, True, True, 0)
        boxH.set_size_request(width/2, height/3)
        boxV.pack_start(boxH, False, False, 0)

        wdth = width/4
        hght = height/4

        frame1 = Gtk.Frame()
        label1 = Gtk.Label("Base")
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
        servboxH.pack_start(servboxV1, False, False, 10)
        
        frame2 = Gtk.Frame()
        label2 = Gtk.Label("Forearm")
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
        label3 = Gtk.Label("Hand")
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
        label4 = Gtk.Label("Gripper")
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

        buttonRecord = Gtk.Button(name="button", label="Record")
        buttonRecord.connect("clicked", self.on_rec_clicked)
        buttonPLay = Gtk.Button(name="button", label="Play")
        buttonPLay.connect("clicked", self.on_play_clicked)
        buttonPause = Gtk.Button(name="button", label="Pause")
        buttonPause.connect("clicked", self.on_play_clicked)
        buttonStop = Gtk.Button(name="button", label="Stop")
        buttonStop.connect("clicked", self.on_stop_clicked)
        buttonRepeat = Gtk.CheckButton("Repeat one time")
        buttonRepeat.connect("toggled", self.on_repeat_clicked)
        buttonClear = Gtk.Button(name="button", label="Clear")
        buttonClear.connect("clicked", self.on_play_clicked)

        box5.pack_start(buttonRecord, False, False, 10)
        box5.pack_start(buttonPLay, False, False, 10)
        box5.pack_start(buttonPause, False, False, 10)
        box5.pack_start(buttonStop, False, False, 0)
        box5.pack_start(buttonRepeat, False, False, 10)
        box5.pack_start(buttonClear, False, False, 10)
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

        boxVdraw = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        global drawingarea
        drawingarea = Gtk.DrawingArea()
        drawingarea.connect('draw', self.draw)
    
        drawing_event_box = Gtk.EventBox()
        drawing_event_box.add(drawingarea)
        drawing_event_box.connect('button-press-event', self.mouse_pressed)
        drawing_event_box.connect('motion-notify-event', self.mouse_dragged)
    
        check_useIk = Gtk.CheckButton("Lock Forearm & Hand")
        check_useIk.connect("toggled", self.check_toggled)
    
        boxVDraw = Gtk.VBox()
        boxVDraw.pack_start(check_useIk, False, True, 0)
        boxVDraw.pack_start(drawing_event_box, True, True, 0)

        frameDraw = Gtk.Frame()
        frameDraw.add(boxVDraw)

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
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(SIZE/20)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    
        self.draw_extra(ctx)
        self.draw_pedro_side(ctx)
        self.draw_pedro_top(ctx)
        self.draw_text(ctx)

    # ---------------------------------
    # draw_extra
    # ---------------------------------
    def draw_extra(self,ctx):
        # Vertical separator
        ctx.move_to(-1.5*SIZE + Width/2, 0) #
        ctx.rel_line_to(0, Height)
        ctx.stroke()
    
        # Z control rectangle
        ctx.rectangle(Width - 0.5*SIZE, 0.5*SIZE, - 0.5*SIZE, d )
        ctx.fill()
        # ctx.stroke()
    
        # Top View limits
        #    ctx.new_path()
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

        # Draw target and vertical slider
        if not lockHandAndForearm:
            ctx.rectangle(
                OriginSideX + r0,
                OriginSideY - 0.5*SIZE - Z0,   #
                0.05*SIZE, 0.05*SIZE)
            ctx.stroke()
                      
            ctx.new_path()
            ctx.move_to(Width - SIZE, OriginSideY - 0.5*SIZE - Z0)
            ctx.rel_line_to(0.5*SIZE, 0)
                      
            ctx.set_source_rgb(1, 0, 0)
            ctx.stroke()


    # ---------------------------------
    # draw_pedro_side
    # ---------------------------------
    def draw_pedro_side(self,ctx):
    
        ctx.save()
    
        self.side_base(ctx)
        self.side_forearm(ctx)
        self.side_hand(ctx)
        self.side_endpoint(ctx)
    
        ctx.restore()

    # ---------------------------------
    # side_base
    # ---------------------------------
    def side_base(self,ctx):
        ctx.set_source_rgb(0, 0, 0)
    
        ctx.rectangle(
            OriginSideX - 0.5*(length_Base + 0.5*SIZE),
            OriginSideY + 0.5*length_Base,
            length_Base + 0.5*SIZE, - length_Base)
        ctx.fill()
        # ctx.stroke()
                  
        #ctx.rectangle(OriginSideX, OriginSideY, 0.05*SIZE, 0.05*SIZE)
        ctx.set_source_rgb(1, 0, 0)
        ctx.arc(OriginSideX, OriginSideY - 0.5*length_Base, 0.5*(length_Base + 0.5*SIZE), pi, 0)
                  
        ctx.fill()
        # ctx.stroke()
        ctx.set_source_rgb(0, 0, 0)

    # ---------------------------------
    # side_forearm
    # ---------------------------------
    def side_forearm(self,ctx):
        ctx.translate(originForearmX, originForearmY)
        #ctx.rectangle(0, 0, 0.05*SIZE, 0.05*SIZE)
    
        ctx.rotate(forearm)
        ctx.arc(0 , 0, 0.4*(length_Base + 0.5*SIZE), 0, 2*pi)
        ctx.fill()
            # ctx.stroke()
    
        ctx.rectangle(0, -0.125*length_Forearm, -length_Forearm, 0.25*length_Forearm)
        ctx.fill()
        # ctx.stroke()
    
        ctx.set_source_rgb(1, 0, 0)
        ctx.arc(0 , 0, 0.05*length_Forearm, 0, 2*pi)
        ctx.fill()
        # ctx.stroke()
    
        ctx.restore()
        ctx.set_source_rgb(0, 0, 0)

    # ---------------------------------
    # side_hand
    # ---------------------------------
    def side_hand(self,ctx):
        ctx.save()
        ctx.translate(originHandX, originHandY)
        #ctx.rectangle(0, 0, 0.05*SIZE, 0.05*SIZE)
        #ctx.stroke()
    
        ctx.rotate(forearm)
    
        ctx.rotate(hand)
        ctx.arc(0 , 0, 0.4*(length_Base + 0.5*SIZE), 0, 2*pi)
        ctx.fill()
        # ctx.stroke()
    
        ctx.save()
        ctx.rotate(-pi/4)
        ctx.rectangle(
            0,
            -0.0625*length_Hand,
            0.6*length_Hand,
            0.125*length_Hand)
        
        ctx.rectangle(
            0.6*length_Hand,
            -0.125*length_Hand,
            0.4*length_Hand,
            0.25*length_Hand)
                  
        ctx.fill()
        # ctx.stroke()
                  
        ctx.set_source_rgb(1, 0, 0)
        ctx.arc(0 , 0, 0.05*length_Forearm, 0, 2*pi)
        ctx.fill()
        # ctx.stroke()


    # ---------------------------------
    # side_endpoint
    # ---------------------------------
    def side_endpoint(self,ctx):
        #ctx.rotate(-pi/4)
        ctx.translate(length_Hand, 0)
        ctx.set_source_rgb(1, 0, 0)
    
        ctx.new_path()
        ctx.move_to(0, -0.5*0.25*length_Hand)
        ctx.rel_line_to(length_EndPoint, 0.4*0.25*length_Hand)
        ctx.rel_line_to(-length_EndPoint, 0)
        ctx.close_path()
    
        ctx.move_to(0, 0.5*0.25*length_Hand)
        ctx.rel_line_to(length_EndPoint, -0.4*0.25*length_Hand)
        ctx.rel_line_to(-length_EndPoint, 0)
        ctx.close_path()
    
        ctx.fill()
        # ctx.stroke()
        ctx.restore()
        ctx.set_source_rgb(0, 0, 0)

    # ---------------------------------
    # draw_pedro_top
    # ---------------------------------
    def draw_pedro_top(self, ctx):
        # Base
        ctx.save()
        ctx.translate(OriginTopX, OriginTopY)
        ctx.rotate(base)
    
        ctx.rectangle(-0.5*SIZE, 0.5*SIZE, SIZE, -SIZE)
    
        ctx.rectangle(0, -0.25*SIZE, - r0, 0.5*SIZE)
    
        ctx.restore()
        ctx.fill()
        # ctx.stroke()

    # ---------------------------------
    # draw_text
    # ---------------------------------
    def draw_text(self, ctx):
        ctx.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(TXT_SIZE)
        ctx.move_to(0.01*SIZE, 1.5*TXT_SIZE)
        ctx.show_text('Base: ' + str(int(degrees(base))))
        ctx.move_to(0.01*SIZE, 3.5*TXT_SIZE)
        ctx.show_text('Forearm: '+ str(int(degrees(forearm))))
        ctx.move_to(0.01*SIZE, 5.5*TXT_SIZE)
        ctx.show_text('Hand: '+ str(int(degrees(-hand))))
        if outOfReach:
            ctx.set_source_rgb(1, 0, 0)
            ctx.move_to(0.01*SIZE, 4*TXT_SIZE)
            #ctx.move_to(-3*TXT_SIZE + Width/2, 0.5*SIZE + Height/2)
            ctx.show_text('OUT OF REACH !!!')

    # ---------------------------------
    # mouse_pressed
    # ---------------------------------
    def mouse_pressed(self, widget, e):
        global isForearm
        isForearm = (e.button == 1)

    # ---------------------------------
    # mouse_dragged
    # ---------------------------------
    def mouse_dragged(self, widget, e):
        global mXL, mYL
        global mXR, mYR
        global mXik, mYik
        global originHandX, originHandY
        global outOfReach
    
        if e.x > -1.5*SIZE + Width/2 and e.x < Width - 1.5*SIZE:
            mXik = e.x
            mYik = e.y
            self.xyzToServoAngles(0, mXik - OriginTopX, mYik - OriginTopY, Z)
        else:
            if e.x > Width - 1.5*SIZE :
                if e.x < Width - 0.5*SIZE and e.x > Width - SIZE and e.y > 0.5*SIZE and e.y < d + 0.5*SIZE:
                    self.xyzToServoAngles(0, mXik - OriginTopX, mYik - OriginTopY, d + 0.5*SIZE - e.y)
                else:
                    outOfReach = True
            elif isForearm:
                mXL = e.x
                mYL = e.y
                self.xyzToServoAngles(1, mXL - originForearmX, mYL - originForearmY, Z)
        
            else :
                mXR = e.x
                mYR = e.y
                self.xyzToServoAngles(2, mXR - originHandX, mYR - originHandY, Z)

        originHandX = originForearmX + (length_Forearm)*cos(forearm - pi)
        originHandY = originForearmY + (length_Forearm)*sin(forearm - pi)
        drawingarea.queue_draw()

    # ---------------------------------
    # check_toggled
    # ---------------------------------
    def check_toggled(self, e):
        global lockHandAndForearm
        lockHandAndForearm ^=1

    # Inverse Kinematics:
    # From Cartesian to Servo Angles
    # ---------------------------------
    # xyzToServoAngles
    # ---------------------------------
    def xyzToServoAngles(self, choice,x, y, z):
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
        
            if r >= d:
                r = d
        
            if z <= 0:
                Z = 0
            elif z >= d + 0.5*SIZE:
                Z = d + 0.5*SIZE
            else:
                Z = z
        
            R = sqrt(r*r + Z*Z)
        
            if R > (b-a) and R <= (a+b):
                base0 = atan2(y,x) + pi
                self.send_angles(1, int(degrees(base0)))

                #if not lockHandAndForearm:
                    #forearm0 = -acos((a*a + R*R - b*b)/(2*a*R)) - acos(r/R) + pi
                    #hand0 = -acos((a*a + b*b - R*R)/(2*a*b)) + pi/4
            else:
                outOfReach = True
    
        elif choice == 1:
            forearm0 = atan2(y, x) + pi
            self.send_angles(2, int(degrees(forearm0)))


        elif choice == 2:
            hand0 = atan2(y, x) + pi/4 - forearm0
            self.send_angles(4, -int(degrees(hand0)))

    
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




    # ---------------------------------
    # send_cmd
    # ---------------------------------
    def send_angles(self, numServ, angleServ):
        try:
            print("angleServ1: " + str(int(degrees(base))) + " angleServ2: " + str(int(degrees(forearm))) + " angleServ3: " + str(-int(degrees(hand))))
            ser.write(bytearray([numServ, angleServ]))
        except:
            print ("No Pedro Connected")

#=======================================

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
        #global servo_change
        global serv2_chg
        global servocmd
        servocmd = 11
        #servo_change = True
        serv2_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn2Up_release
    # ---------------------------------  
    def on_btn2Up_release(self, widget, event):
        #global servo_change
        global serv2_chg
        #servo_change = False
        serv2_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

    # ---------------------------------
    # on_btn2Down_press
    # ---------------------------------    
    def on_btn2Down_press(self, widget, event):
        #global servo_change
        global serv2_chg
        global servocmd
        servocmd = 22
        #servo_change = True
        serv2_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn2Down_release
    # ---------------------------------  
    def on_btn2Down_release(self, widget, event):
        #global servo_change
        global serv2_chg
        #servo_change = False
        serv2_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

#########

    # ---------------------------------
    # on_btn3Up_press
    # ---------------------------------    
    def on_btn3Up_press(self, widget, event):
        #global servo_change
        global serv3_chg
        global servocmd
        servocmd = 11
        #servo_change = True
        serv3_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn3Up_release
    # ---------------------------------  
    def on_btn3Up_release(self, widget, event):
        #global servo_change
        global serv3_chg
        #servo_change = False
        serv3_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

    # ---------------------------------
    # on_btn3Down_press
    # ---------------------------------    
    def on_btn3Down_press(self, widget, event):
        #global servo_change
        global serv3_chg
        global servocmd
        servocmd = 22
        #servo_change = True
        serv3_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn3Down_release
    # ---------------------------------  
    def on_btn3Down_release(self, widget, event):
        #global servo_change
        global serv3_chg
        #servo_change = False
        serv3_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

########

    # ---------------------------------
    # on_btn4Up_press
    # ---------------------------------    
    def on_btn4Up_press(self, widget, event):
        #global servo_change
        global serv4_chg
        global servocmd
        servocmd = 11
        #servo_change = True
        serv4_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn4Up_release
    # ---------------------------------  
    def on_btn4Up_release(self, widget, event):
        #global servo_change
        global serv4_chg
        #servo_change = False
        serv4_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

    # ---------------------------------
    # on_btn4Down_press
    # ---------------------------------    
    def on_btn4Down_press(self, widget, event):
        #global servo_change
        global serv4_chg
        global servocmd
        servocmd = 22
        #servo_change = True
        serv4_chg = True
        if not thread_send_cmd.is_alive():
            thread_send_cmd.start()
            thread_send_cmd.pause.set()
        else:
            thread_send_cmd.pause.set()

    # ---------------------------------
    # on_btn4Down_release
    # ---------------------------------  
    def on_btn4Down_release(self, widget, event):
        #global servo_change
        global serv4_chg
        #servo_change = False
        serv4_chg = False
        if thread_send_cmd.pause.is_set():
            thread_send_cmd.pause.clear()

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


# ---------------------------------
# gtk_style
# ---------------------------------
def gtk_style():
        css = b"""

#button {
    color: #ffffff;
    background: #e80606;
}
#servo {
    color: #ffffff;
    background: #d80606;
}

        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

gtk_style()

update_ser = Update_Serial()
update_ser.serial_ports()

recv=threading.Thread(target=recv_thr)
recv.start()

thread_send_cmd = Send_Cmd()
window = Pedro()
window.connect("delete-event", Gtk.main_quit)
window.show_all()


Gtk.main()
