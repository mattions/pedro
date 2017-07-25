import sys, os
import glob
import serial
import cairo
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


pedro_xpm = [
"48 48 64 1",
"       c None",
".      c #DF7DCF3CC71B",
"X      c #965875D669A6",
"o      c #71C671C671C6",
"O      c #A699A289A699",
"+      c #965892489658",
"@      c #8E38410330C2",
"#      c #D75C7DF769A6",
"$      c #F7DECF3CC71B",
"%      c #96588A288E38",
"&      c #A69992489E79",
"*      c #8E3886178E38",
"=      c #104008200820",
"-      c #596510401040",
";      c #C71B30C230C2",
":      c #C71B9A699658",
">      c #618561856185",
",      c #20811C712081",
"<      c #104000000000",
"1      c #861720812081",
"2      c #DF7D4D344103",
"3      c #79E769A671C6",
"4      c #861782078617",
"5      c #41033CF34103",
"6      c #000000000000",
"7      c #49241C711040",
"8      c #492445144924",
"9      c #082008200820",
"0      c #69A618611861",
"q      c #B6DA71C65144",
"w      c #410330C238E3",
"e      c #CF3CBAEAB6DA",
"r      c #71C6451430C2",
"t      c #EFBEDB6CD75C",
"y      c #28A208200820",
"u      c #186110401040",
"i      c #596528A21861",
"p      c #71C661855965",
"a      c #A69996589658",
"s      c #30C228A230C2",
"d      c #BEFBA289AEBA",
"f      c #596545145144",
"g      c #30C230C230C2",
"h      c #8E3882078617",
"j      c #208118612081",
"k      c #38E30C300820",
"l      c #30C2208128A2",
"z      c #38E328A238E3",
"x      c #514438E34924",
"c      c #618555555965",
"v      c #30C2208130C2",
"b      c #38E328A230C2",
"n      c #28A228A228A2",
"m      c #41032CB228A2",
"M      c #104010401040",
"N      c #492438E34103",
"B      c #28A2208128A2",
"V      c #A699596538E3",
"C      c #30C21C711040",
"Z      c #30C218611040",
"A      c #965865955965",
"S      c #618534D32081",
"D      c #38E31C711040",
"F      c #082000000820",
"                                                ",
"          .XoO                                  ",
"         +@#$%o&                                ",
"         *=-;#::o+                              ",
"           >,<12#:34                            ",
"             45671#:X3                          ",
"               +89<02qwo                        ",
"e*                >,67;ro                       ",
"ty>                 459@>+&&                    ",
"$2u+                  ><ipas8*                  ",
"%$;=*                *3:.Xa.dfg>                ",
"Oh$;ya             *3d.a8j,Xe.d3g8+             ",
" Oh$;ka          *3d$a8lz,,xxc:.e3g54           ",
"  Oh$;kO       *pd$%svbzz,sxxxxfX..&wn>         ",
"   Oh$@mO    *3dthwlsslszjzxxxxxxx3:td8M4       ",
"    Oh$@g& *3d$XNlvvvlllm,mNwxxxxxxxfa.:,B*     ",
"     Oh$@,Od.czlllllzlmmqV@V#V@fxxxxxxxf:%j5&   ",
"      Oh$1hd5lllslllCCZrV#r#:#2AxxxxxxxxxcdwM*  ",
"       OXq6c.%8vvvllZZiqqApA:mq:Xxcpcxxxxxfdc9* ",
"        2r<6gde3bllZZrVi7S@SV77A::qApxxxxxxfdcM ",
"        :,q-6MN.dfmZZrrSS:#riirDSAX@Af5xxxxxfevo",
"         +A26jguXtAZZZC7iDiCCrVVii7Cmmmxxxxxx%3g",
"          *#16jszN..3DZZZZrCVSA2rZrV7Dmmwxxxx&en",
"           p2yFvzssXe:fCZZCiiD7iiZDiDSSZwwxx8e*>",
"           OA1<jzxwwc:$d%NDZZZZCCCZCCZZCmxxfd.B ",
"            3206Bwxxszx%et.eaAp77m77mmmf3&eeeg* ",
"             @26MvzxNzvlbwfpdettttttttttt.c,n&  ",
"             *;16=lsNwwNwgsvslbwwvccc3pcfu<o    ",
"              p;<69BvwwsszslllbBlllllllu<5+     ",
"              OS0y6FBlvvvzvzss,u=Blllj=54       ",
"               c1-699Blvlllllu7k96MMMg4         ",
"               *10y8n6FjvllllB<166668           ",
"                S-kg+>666<M<996-y6n<8*          ",
"                p71=4 m69996kD8Z-66698&&        ",
"                &i0ycm6n4 ogk17,0<6666g         ",
"                 N-k-<>     >=01-kuu666>        ",
"                 ,6ky&      &46-10ul,66,        ",
"                 Ou0<>       o66y<ulw<66&       ",
"                  *kk5       >66By7=xu664       ",
"                   <<M4      466lj<Mxu66o       ",
"                   *>>       +66uv,zN666*       ",
"                              566,xxj669        ",
"                              4666FF666>        ",
"                               >966666M         ",
"                                oM6668+         ",
"                                  *4            ",
"                                                ",
"                                                "
]


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
            if not self.displayNoPedro:
                self.displayNoPedro = True
                print ("*** No pedro connected! ***")
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
                    if ser_msg.decode('utf-8') == "Hi! Im Pedro":
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
        boxH.pack_start(servboxH, False, False, 0)
        boxH.set_size_request(width/2, height/3)
        boxV.pack_start(boxH, False, False, 0)

        wdth = width/4
        hght = height/4

        frame1 = Gtk.Frame()
        label1 = Gtk.Label("Servo 1")
        boxV1 = Gtk.VBox()
        boxH1 = Gtk.HBox()
        btn1Up.set_size_request(wdth/2, hght/2)
        btn1Down.set_size_request(wdth/2, hght/2)
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
        label2 = Gtk.Label("Servo 2")
        boxV2 = Gtk.VBox()
        boxH2 = Gtk.HBox()
        btn2Up.set_size_request(wdth/2, hght/2)
        btn2Down.set_size_request(wdth/2, hght/2)
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
        btn3Up.set_size_request(wdth/2, hght/2)
        btn3Down.set_size_request(wdth/2, hght/2)
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
        btn4Up.set_size_request(wdth/2, hght/2)
        btn4Down.set_size_request(wdth/2, hght/2)
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
        buttonStop = Gtk.Button("Stop")
        buttonStop.connect("clicked", self.on_stop_clicked)
        buttonRepeat = Gtk.CheckButton("Repeat one time")
        buttonRepeat.connect("toggled", self.on_repeat_clicked)
        buttonClear = Gtk.Button("Clear")
        buttonClear.connect("clicked", self.on_play_clicked)
        box5.pack_start(buttonRecord, False, False, 10)
        box5.pack_start(buttonPLay, False, False, 10)
        box5.pack_start(buttonStop, False, False, 0)
        box5.pack_start(buttonRepeat, False, False, 10)
        box5.pack_start(buttonClear, False, False, 10)

        servboxH.pack_start(box5, False, False, 60)


        ###########################################################
        align = Gtk.Alignment()
        pbar = Gtk.ProgressBar()
        align.add(pbar)
        
        boxV.pack_start(align, False, False, 0)

        ###########################################################

        boxLockH = Gtk.HBox()
        drawing_area = Gtk.EventBox()
        boxVdraw = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        #color_widget(drawing_area, 'coral')

        image = Gtk.Image()
        #self.pixbuf = GdkPixbuf.Pixbuf.new_from_xpm_data(pedro_xpm)
        #image.set_from_pixbuf(self.pixbuf)
        #image.set_from_file(self.ressource_path('pedro.png'))
        #drawing_area.set_size_request(780, 500)
        drawing_area.connect('button-press-event', self.on_area_button_press)
        drawing_area.connect('button-release-event', self.on_area_button_release)
        drawing_area.connect('motion-notify-event', self.on_area_motion)
        #drawing_area.connect('draw', self.checkerboard_draw_event)
        #self.checkerboard_draw_event(width/2, height/3, drawing_area.cairo_create())
        #drawing_area.add(image)

        lockLabel = Gtk.Label("Lock servo:")
        lock1 = Gtk.CheckButton("Servo 1")
        lock1.connect("toggled", self.on_lock_servo1)
        lock2 = Gtk.CheckButton("Servo 2")
        lock2.connect("toggled", self.on_lock_servo2)
        lock3 = Gtk.CheckButton("Servo 3")
        lock3.connect("toggled", self.on_lock_servo3)
        lock4 = Gtk.CheckButton("Servo 4")
        lock4.connect("toggled", self.on_lock_servo4)
        boxLockH.pack_start(lockLabel, False, False, 5)
        boxLockH.pack_start(lock1, False, False, 5)
        boxLockH.pack_start(lock2, False, False, 5)
        boxLockH.pack_start(lock3, False, False, 5)
        boxLockH.pack_start(lock4, False, False, 5)
        
        frameDraw = Gtk.Frame()
        frameDraw.add(drawing_area)

        boxH = Gtk.HBox()
        boxV1 = Gtk.VBox()
        boxV2 = Gtk.VBox()

        boxH1 = Gtk.HBox()
        boxH2 = Gtk.HBox()
        boxH.pack_start(boxH1, False, False, 10)
        boxH.pack_start(frameDraw, True, True, 0)
        boxH.pack_start(boxH2, False, False, 10)

        boxV1.pack_start(boxH, True, True, 0)

        #boxH.pack_start(lock, False, False, 10)
        boxVdraw.pack_start(boxLockH, False, False, 10)
        boxVdraw.pack_start(boxV1, True, True, 0)
        boxVdraw.pack_start(boxV2, False, False, 10)

        boxV.pack_start(boxVdraw, True, True, 0)

        ###################################################
        
        self.add(boxV)
        global initApp
        initApp = True

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



