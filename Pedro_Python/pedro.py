#============================================================================================================
#                              PEDRO : Programming Educational Robot
#============================================================================================================
#!/usr/bin/env python
#title           :pedro.py
#description     :Interface for Pedro Petit Robot an open source 3D robotic arm, with serial USB control
#email           :pedropetitrobot@gmail.com
#date            :2016-2017
#version         :1.0
#usage           :python3 pedro.py
#python_version  :3.6.1  
#============================================================================================================

 # -*-coding:Latin-1 -*
import sys, os
import glob
import serial
import gi
import glib
import time
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

global recFile
recFile = None

global testBool
testBool = True

global recButton
recButton = False

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

#global servo_change
#servo_change = False

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

serv1Lbl = Gtk.Label("50", name="label")
serv2Lbl = Gtk.Label("50", name="label")
serv3Lbl = Gtk.Label("50", name="label")
serv4Lbl = Gtk.Label("50", name="label")

global updateSerial
updateSerial = True

global checkPedro
checkPedro = True

global initApp
initApp = False

THR_LOCK = threading.Lock()

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
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event( )


    def join(self, *args):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout=None)

    # ---------------------------------
    # start
    # ---------------------------------
    def start(self, *args):
        super(Send_Cmd, self).start()

    # ---------------------------------
    # stop
    # ---------------------------------
    def stop(self, *args):
        self.pause.stop()

    def __del__(self):
        print ("goodbye!")
    
    # ---------------------------------
    # run
    # ---------------------------------
    def run(self):
        #global ser
        #global servo_change
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
        global recFile
        global recButton
        global testBool
        if serv1_chg:
            if servocmd == 11 and int(serv1Lbl.get_label()) < 180:
                serv1Lbl.set_label(str(int(serv1Lbl.get_label()) + 1))
                self.send_cmd(1, int(serv1Lbl.get_label()))
            elif servocmd == 22 and int(serv1Lbl.get_label()) > 0:
                serv1Lbl.set_label(str(int(serv1Lbl.get_label()) - 1))
                self.send_cmd(1, int(serv1Lbl.get_label()))
            if recButton:
                recFile = open("record_pedro.log", 'a' )
                recFile.write("a" + str(serv1Lbl.get_label()) + " ")
                recFile.close()
        elif serv2_chg:
            if servocmd == 11 and int(serv2Lbl.get_label()) < 180:
                serv2Lbl.set_label(str(int(serv2Lbl.get_label()) + 1))
                self.send_cmd(2, int(serv2Lbl.get_label()))
            elif servocmd == 22 and int(serv2Lbl.get_label()) > 0:
                serv2Lbl.set_label(str(int(serv2Lbl.get_label()) - 1))
                self.send_cmd(2, int(serv2Lbl.get_label()))
            if recButton:
                recFile = open("record_pedro.log", 'a' )
                recFile.write("b" + str(serv2Lbl.get_label()) + " ")
                recFile.close()
        elif serv3_chg:
            if servocmd == 11 and int(serv3Lbl.get_label()) < 180:
                serv3Lbl.set_label(str(int(serv3Lbl.get_label()) + 1))
                self.send_cmd(3, int(serv3Lbl.get_label()))
            elif servocmd == 22 and int(serv3Lbl.get_label()) > 0:
                serv3Lbl.set_label(str(int(serv3Lbl.get_label()) - 1))
                self.send_cmd(3, int(serv3Lbl.get_label()))
            if recButton:
                recFile = open("record_pedro.log", 'a' )
                recFile.write("c" + str(serv3Lbl.get_label()) + " ")
                recFile.close()
        elif serv4_chg:
            if servocmd == 11 and int(serv4Lbl.get_label()) < 180:
                serv4Lbl.set_label(str(int(serv4Lbl.get_label()) + 1))
                self.send_cmd(4, int(serv4Lbl.get_label()))
            elif servocmd == 22 and int(serv4Lbl.get_label()) > 0:
                serv4Lbl.set_label(str(int(serv4Lbl.get_label()) - 1))
                self.send_cmd(4, int(serv4Lbl.get_label()))
            if recButton:
                recFile = open("record_pedro.log", 'a' )
                recFile.write("d" + str(serv4Lbl.get_label()) + " ")
                recFile.close()

#=======================================
# Pedro
#=======================================
class Pedro(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        ###########################################################
        ######## HeaderBar
        ###########################################################

        hb = Gtk.HeaderBar()
        hb.props.title = "Robot Pedro"
        self.set_titlebar(hb)
        color_widget(self, 'black')
        #self.set_size_request(screen.get_width()/1.5, screen.get_height()/1.1)
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

        pedro_combo.connect("changed", self.on_pedro_combo_changed)
        hb.pack_end(buttonClose)

        ###########################################################
        ######## Robot function
        ###########################################################


        lblTitle = Gtk.Label("Robot Pedro", name="label_title")
        barHTitle = Gtk.HSeparator(name = "label")
        ###################
        ###### Button servo
        ###################
        wdth = width/4
        hght = height/4
        boxHAllServo = Gtk.HBox()

        lblBase = Gtk.Label("Base", name="label")
        boxV1 = Gtk.VBox()
        boxH1 = Gtk.HBox()
        btn1Up.set_size_request(wdth/2.5, hght/2.5)
        btn1Down.set_size_request(wdth/2.5, hght/2.5)
        btn1Up.connect('button-press-event', self.on_btn1Up_press)
        btn1Up.connect('button-release-event', self.on_btn1Up_release)
        btn1Down.connect('button-press-event', self.on_btn1Down_press)
        btn1Down.connect('button-release-event', self.on_btn1Up_release)
        boxV1.pack_start(lblBase, False, False, 10)
        boxV1.pack_start(btn1Up, False, False, 10)
        boxV1.pack_start(serv1Lbl, False, False, 10)
        boxV1.pack_start(btn1Down, False, False, 10)
        boxH1.pack_start(boxV1, False, False, 10)
        boxVServoFrame1 = Gtk.VBox()
        boxVServoFrame1.pack_start(boxH1, False, False, 10)
        boxHAllServo.pack_start(boxVServoFrame1, True, True, 10)
        
        lblForearm = Gtk.Label("Forearm", name="label")
        boxV2 = Gtk.VBox()
        boxH2 = Gtk.HBox()
        btn2Up.set_size_request(wdth/2.5, hght/2.5)
        btn2Down.set_size_request(wdth/2.5, hght/2.5)
        btn2Up.connect('button-press-event', self.on_btn2Up_press)
        btn2Up.connect('button-release-event', self.on_btn2Up_release)
        btn2Down.connect('button-press-event', self.on_btn2Down_press)
        btn2Down.connect('button-release-event', self.on_btn2Up_release)
        boxV2.pack_start(lblForearm, False, False, 10)
        boxV2.pack_start(btn2Up, False, False, 10)
        boxV2.pack_start(serv2Lbl, False, False, 10)
        boxV2.pack_start(btn2Down, False, False, 10)
        boxH2.pack_start(boxV2, False, False, 10)
        boxVServoFrame2 = Gtk.VBox()
        boxVServoFrame2.pack_start(boxH2, False, False, 10)
        boxHAllServo.pack_start(boxVServoFrame2, True, True, 10)
        
        lblHand = Gtk.Label("Hand", name="label")
        boxV3 = Gtk.VBox()
        boxH3 = Gtk.HBox()
        btn3Up.set_size_request(wdth/2.5, hght/2.5)
        btn3Down.set_size_request(wdth/2.5, hght/2.5)
        btn3Up.connect('button-press-event', self.on_btn3Up_press)
        btn3Up.connect('button-release-event', self.on_btn3Up_release)
        btn3Down.connect('button-press-event', self.on_btn3Down_press)
        btn3Down.connect('button-release-event', self.on_btn3Up_release)
        boxV3.pack_start(lblHand, False, False, 10)
        boxV3.pack_start(btn3Up, False, False, 10)
        boxV3.pack_start(serv3Lbl, False, False, 10)
        boxV3.pack_start(btn3Down, False, False, 10)
        boxH3.pack_start(boxV3, False, False, 10)
        boxVServoFrame3 = Gtk.VBox()
        boxVServoFrame3.pack_start(boxH3, False, False, 10)
        boxHAllServo.pack_start(boxVServoFrame3, True, True, 10)
        
        lblGripper = Gtk.Label("Gripper", name="label")
        boxV4 = Gtk.VBox()
        boxH4 = Gtk.HBox()
        btn4Up.set_size_request(wdth/2.5, hght/2.5)
        btn4Down.set_size_request(wdth/2.5, hght/2.5)
        btn4Up.connect('button-press-event', self.on_btn4Up_press)
        btn4Up.connect('button-release-event', self.on_btn4Up_release)
        btn4Down.connect('button-press-event', self.on_btn4Down_press)
        btn4Down.connect('button-release-event', self.on_btn4Up_release)
        boxV4.pack_start(lblGripper, False, False, 10)
        boxV4.pack_start(btn4Up, False, False, 10)
        boxV4.pack_start(serv4Lbl, False, False, 10)
        boxV4.pack_start(btn4Down, False, False, 10)
        boxH4.pack_start(boxV4, False, False, 10)
        boxVServoFrame4 = Gtk.VBox()
        boxVServoFrame4.pack_start(boxH4, False, False, 10)
        boxHAllServo.pack_start(boxVServoFrame4, True, True, 10)

              
        ###################
        ###### Robot speed
        ###################        
        ad1 = Gtk.Adjustment(1, 1, 4, 5, 10, 0)
        self.speed_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.speed_scale.set_digits(0)
        self.speed_scale.set_hexpand(True)
        self.speed_scale.set_valign(Gtk.Align.START)
        self.speed_scale.connect("value-changed", self.update_speed)
        
        btnSpeed1 = Gtk.RadioButton(label="1")
        btnSpeed1.connect("toggled", self.btnSpeed, "button Speed 1")
        btnSpeed2 = Gtk.RadioButton.new_with_label_from_widget(btnSpeed1, "2")
        btnSpeed2.set_active(False)
        btnSpeed2.connect("toggled", self.btnSpeed, "button Speed 2")
        btnSpeed3 = Gtk.RadioButton.new_with_label_from_widget(btnSpeed1, "3")
        btnSpeed3.set_active(False)
        btnSpeed3.connect("toggled", self.btnSpeed, "button Speed 3")

        boxHAllSpeed = Gtk.HBox()
        boxHSpeed = Gtk.HBox()
        boxVSpeed = Gtk.VBox()
        boxHSpeed.pack_start(btnSpeed1, True, False, 0)
        boxHSpeed.pack_start(btnSpeed2, True, False, 10)
        boxHSpeed.pack_start(btnSpeed3, True, False, 10)

        frameSpeed = Gtk.Frame(name = "label")
        frameSpeed.set_label("Speed")
        frameSpeed.add(boxHSpeed)
        boxVSpeed.pack_start(frameSpeed, False, False, 10)
        boxHAllSpeed.pack_start(boxVSpeed, True, True, 10)

        ######################
        ###### Button function
        ######################
        buttonRecord = Gtk.Button(name="button", label="Record")
        buttonRecord.connect("clicked", self.on_rec_clicked)
        buttonPLay = Gtk.Button(name="button", label="Play")
        buttonPLay.connect("clicked", self.on_play_clicked)
        buttonPause = Gtk.Button(name="button", label="Pause")
        buttonPause.connect("clicked", self.on_pause_clicked)
        buttonStop = Gtk.Button(name="button", label="Stop")
        buttonStop.connect("clicked", self.on_stop_clicked)
        buttonRepeat = Gtk.CheckButton("Repeat one time", name = "label")
        buttonRepeat.connect("toggled", self.on_repeat_clicked)
        buttonClear = Gtk.Button(name="button", label="Clear")
        buttonClear.connect("clicked", self.on_clear_clicked)

        boxHAllButton = Gtk.HBox()
        boxVAllButton = Gtk.VBox() 
        boxVAllButton.pack_start(buttonRecord, False, False, 0)
        boxVAllButton.pack_start(buttonPLay, False, False, 20)
        boxVAllButton.pack_start(buttonPause, False, False, 20)
        boxVAllButton.pack_start(buttonStop, False, False, 0)
        boxVAllButton.pack_start(buttonRepeat, False, False, 20)
        boxVAllButton.pack_start(buttonClear, False, False, 0)
        boxHAllButton.pack_start(boxVAllButton, True, True, 10)

        boxVBar = Gtk.VBox()
    
        barH = Gtk.HSeparator(name = "label")
        boxVBar.pack_start(barH, False, False, 0)

        pedroLbl = Gtk.Label("© Robot Pedro - Programming Educational Robotic \n Open Source Project", name="label_petit")
        pedroLbl.set_justify(Gtk.Justification.CENTER)

        #################
        ###### Frame main
        #################
        frameMAIN = Gtk.Frame()
        boxVAll = Gtk.VBox()
        boxVAll.pack_start(lblTitle, False, False, 10)
        boxVAll.pack_start(barHTitle, False, False, 20)
        boxVAll.pack_start(boxHAllServo, False, False, 0)
        boxVAll.pack_start(boxHAllSpeed, False, False, 0)
        boxVAll.pack_start(boxHAllButton, True, True, 30)
        boxVAll.pack_start(boxVBar, False, False, 20)
        boxVAll.pack_start(pedroLbl, True, True, 10)

        """
        frameMAIN.add(boxVAll)
        boxHframeMAIN = Gtk.HBox()
        boxHframeMAIN.pack_start(frameMAIN, False, False, 10)
        boxVframeMAIN = Gtk.VBox()
        boxVframeMAIN.pack_start(boxHframeMAIN, False, False, 10)
        """
        ###########
        ###### Main
        ###########
        boxHMAIN = Gtk.HBox()
        boxHMAIN.pack_start(boxVAll, True, True, 10)
        #boxHMAIN.pack_start(boxVdraw, True, True, 10)

        ###################################################
        
        self.add(boxHMAIN)
        global initApp
        initApp = True

    # ---------------------------------
    # on_close_clicked
    # ---------------------------------
    def on_close_clicked(self, button):
        global close_app
        close_app = True
        #thread_send_cmd.join()
        self.destroy()
        Gtk.main_quit()

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
    # update_speed
    # ---------------------------------
    def update_speed(self, event):
        print("speed value: " + str(int(self.speed_scale.get_value())))

    # ---------------------------------
    # btnSpeed
    # ---------------------------------
    def btnSpeed(self, widget, data=None):
       print ("%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()]))

    # ---------------------------------
    # on_btn1Up_press
    # ---------------------------------    
    def on_btn1Up_press(self, widget, event):
        #global servo_change
        global serv1_chg
        global servocmd
        global recFile
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
        global recFile
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
    # on_rec_clicked
    # ---------------------------------
    def on_rec_clicked(self, button):
        global recButton
        recButton = True
        print("rec button was clicked")
        """
        try:
            ser.write(bytearray([99, 44]))
        except:
            print ("Record unavailable. No Pedro Connected")
        """
    # ---------------------------------
    # on_play_clicked
    # ---------------------------------
    def on_play_clicked(self, button):
        global recButton
        recButton = False
        print("play button was clicked")
        """
        try:
            ser.write(bytearray([99, 55]))
        except:
            print ("Play unavailable. No Pedro Connected")
        """

    # ---------------------------------
    # on_pause_clicked
    # ---------------------------------
    def on_pause_clicked(self, button):
        print("pause button was clicked")
        """
        try:
            ser.write(bytearray([99, 66]))
        except:
            print ("Pause unavailable. No Pedro Connected")
        """

    # ---------------------------------
    # on_stop_clicked
    # ---------------------------------
    def on_stop_clicked(self, button):
        global recButton
        recButton = False
        print("stop button was clicked")
        """
        try:
            ser.write(bytearray([99, 77]))
        except:
            print ("Play unavailable. No Pedro Connected")
        """

    # ---------------------------------
    # on_repeat_clicked
    # ---------------------------------
    def on_repeat_clicked(self, button):
        print("repeat button was toggled " + str(button.get_active()))


    # ---------------------------------
    # on_clear_clicked
    # ---------------------------------
    def on_clear_clicked(self, button):
        print("clear button was clicked")
        try:
            ser.write(bytearray([99, 88]))
        except:
            print ("Clear unavailable. No Pedro Connected")

    # ---------------------------------
    # mouse_pressed
    # ---------------------------------
    def mouse_pressed(self, widget, e):
        global isForearm

    # ---------------------------------
    # mouse_dragged
    # ---------------------------------
    def mouse_dragged(self, widget, e):
        global mXL, mYL
          
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
#label_title {
    color: #ffffff;
    font-size: 30;
}
#label {
    color: #ffffff;
}
#label_petit {
    color: #ffffff;
    font-size: 10;
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

thread_send_cmd = Send_Cmd()

window = Pedro()
window.connect("delete-event", Gtk.main_quit)
window.show_all()


Gtk.main()

