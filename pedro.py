import sys, os
import glob
import serial
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from threading import Thread


screen = Gdk.Screen.get_default()
#print (screen.get_width(), screen.get_height())

global pedro_combo
pedro_combo = Gtk.ComboBoxText()

global pedro_list
pedro_list = {}

global close_app
close_app = False

global ser

global adjserv1
global adjserv2
global adjserv3
global adjserv4

global servocmd
servocmd = 0

adjserv1 = Gtk.Adjustment( value=10, lower=0, upper=180, step_incr=1, page_incr=10, page_size=0)
adjserv2 = Gtk.Adjustment( value=10, lower=0, upper=180, step_incr=1, page_incr=10, page_size=0)
adjserv3 = Gtk.Adjustment( value=10, lower=0, upper=180, step_incr=1, page_incr=10, page_size=0)
adjserv4 = Gtk.Adjustment( value=10, lower=0, upper=180, step_incr=1, page_incr=10, page_size=0)

servo1 = Gtk.VScale(adjustment=adjserv1)
servo2 = Gtk.VScale(adjustment=adjserv2)
servo3 = Gtk.VScale(adjustment=adjserv3)
servo4 = Gtk.VScale(adjustment=adjserv4)

global serv1_chg
serv1_chg = False
global serv2_chg
serv2_chg = False
global serv3_chg
serv3_chg = False
global serv4_chg
serv4_chg = False

global servo_change
servo_change = False

GObject.threads_init()

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
class Update_Serial(Thread):
    
    # ---------------------------------
    # __init__
    # ---------------------------------
    def __init__(self):
        Thread.__init__(self)
    
    # ---------------------------------
    # run
    # ---------------------------------
    def run(self):
        while not close_app:
            None #print ("hello")



#=======================================
# Get_Value_Servo
#=======================================
class Get_Value_Servo(Thread):
    
    # ---------------------------------
    # __init__
    # ---------------------------------
    def __init__(self):
        Thread.__init__(self)
    
    # ---------------------------------
    # run
    # ---------------------------------
    def run(self):
        #global ser
        global servo_change
        global serv1_chg, serv2_chg, serv3_chg, serv4_chg
        print ("len(pedro_list) = " + str(len(pedro_list)))
        while not close_app and len(pedro_list) > 0:
            while servo_change and ser.isOpen():
                print (ser.isOpen())
                print (servocmd)
                if serv1_chg:
                    serv1 = [1, servocmd]
                    data = bytearray(serv1)
                    ser.write(data)
                    serv1_chg = False
                elif serv2_chg:
                    serv2 = [2, servocmd]
                    data = bytearray(serv2)
                    ser.write(data)
                    serv2_chg = False
                elif serv3_chg:
                    serv3 = [3, servocmd]
                    data = bytearray(serv3)
                    ser.write(data)
                    serv3_chg = False
                elif serv4_chg:
                    serv4 = [4, servocmd]
                    data = bytearray(serv4)
                    ser.write(data)
                    serv4_chg = False
                servo_change = False


#=======================================
# Serial_Port
#=======================================
class Serial_Port:
    # ---------------------------------
    # serial_ports
    # ---------------------------------
    def serial_ports(self):
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
                ser = serial.Serial(port)
                ser.close()
                print (port)
                print (str(len(pedro_list)))
                pedro_list["Robot Pedro " + str(len(pedro_list)+1)] = port
                pedro_combo.append_text("Robot Pedro " + str(len(pedro_list)))
                #del pedro_list["No Robot Pedro"] #le faire une seule fois
                #self.window.show_all()
            except (OSError, serial.SerialException):
                pass
        pedro_combo.set_active(0)

    # ---------------------------------
    # pedro_response
    # ---------------------------------
    def pedro_response(self):
        while True:
            if ser.inWainting() > 0:
                data = ser.readline()
                print ("Pedro response " + str(data))


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
        self.color_widget(self, 'white')
        self.set_size_request(screen.get_width()/2, screen.get_height()/2)
        #self.set_resizable(False)
        self.mouseClick = False
        width, height = self.get_size()
        buttonPLay = Gtk.Button("Play")
        buttonPLay.connect("clicked", self.on_play_clicked)
        buttonRecord = Gtk.Button("Record")
        buttonRecord.connect("clicked", self.on_rec_clicked)
        buttonStop = Gtk.Button("Stop")
        buttonStop.connect("clicked", self.on_stop_clicked)
        sepa = Gtk.VSeparator()
        buttonClose = Gtk.Button("Close")
        buttonClose.connect("clicked", self.on_close_clicked)
        connected = Gtk.Label("Connected : ")

        hb.pack_start(buttonPLay)
        hb.pack_start(buttonRecord)
        hb.pack_start(buttonStop)
        hb.pack_start(sepa)
        hb.pack_start(connected)
        hb.pack_start(pedro_combo)
        
        serial_port = Serial_Port()
        serial_port.serial_ports()
        pedro_combo.connect("changed", self.on_pedro_combo_changed)
        hb.pack_end(buttonClose)

        ###########################################################
        
        vpaned = Gtk.VPaned()

        boxV = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        boxVdraw = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        boxH = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vpaned.add1(boxV)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_size_request(width/2, height/3)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(boxH)
        boxV.pack_start(scrolled, True, True, 0)
        servboxH = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        global adjserv1
        global adjserv2
        global adjserv3
        global adjserv4

        adjserv1.connect("value_changed", self.on_changed_servo1)
        # adjserv1.emit("value_changed")
        servboxH.pack_start(servo1, True, True, 0)
        global old_value1
        old_value1 = int(servo1.get_value())

        adjserv2.connect("value_changed", self.on_changed_servo2)
        # adjserv2.emit("value_changed")
        servboxH.pack_start(servo2, True, True, 0)
        global old_value2
        old_value2 = int(servo2.get_value())
        
        adjserv3.connect("value_changed", self.on_changed_servo3)
        # adjserv3.emit("value_changed")
        servboxH.pack_start(servo3, True, True, 0)
        global old_value3
        old_value3 = int(servo3.get_value())
        
        adjserv4.connect("value_changed", self.on_changed_servo4)
        #  adjserv4.emit("value_changed")
        servboxH.pack_start(servo4, True, True, 0)
        global old_value4
        old_value4 = int(servo4.get_value())
        
        boxH.pack_start(servboxH, True, True, 0)

        ###########################################################

        drawing_area = Gtk.EventBox()
        self.color_widget(drawing_area, 'coral')

        image = Gtk.Image()
        #self.pixbuf = GdkPixbuf.Pixbuf.new_from_xpm_data(pedro_xpm)
        #image.set_from_pixbuf(self.pixbuf)
        #image.set_from_file(self.ressource_path('pedro.png'))
        #drawing_area.set_size_request(780, 500)
        drawing_area.connect('button-press-event', self.on_area_button_press)
        drawing_area.connect('button-release-event', self.on_area_button_release)
        drawing_area.connect('motion-notify-event', self.on_area_motion)
        #drawing_area.add(image)
        button_area = Gtk.Button()
        boxVdraw.pack_start(drawing_area, True, True, 0)
        boxVdraw.pack_start(button_area, False, False, 0)
        boxH.pack_start(boxVdraw, True, True, 0)


        ###################################################

        self.notebook = Gtk.Notebook()
        self.color_widget(self.notebook, 'black')
        boxServo1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        boxServo2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        boxServo3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        boxServo4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vpaned.add2(self.notebook)

        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(boxServo1)
        self.notebook.append_page(self.page1, Gtk.Label('Servo 1'))

        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.page2.add(boxServo2)
        self.notebook.append_page(self.page2, Gtk.Label('Servo 2'))

        self.page3 = Gtk.Box()
        self.page3.set_border_width(10)
        self.page3.add(boxServo3)
        self.notebook.append_page(self.page3, Gtk.Label('Servo 3'))

        self.page4 = Gtk.Box()
        self.page4.set_border_width(10)
        self.page4.add(boxServo4)
        self.notebook.append_page(self.page4, Gtk.Label('Servo 4'))

        scrolled1 = Gtk.ScrolledWindow()
        scrolled1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        scrolled2 = Gtk.ScrolledWindow()
        scrolled2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        scrolled3 = Gtk.ScrolledWindow()
        scrolled3.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        scrolled4 = Gtk.ScrolledWindow()
        scrolled4.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        Initial_Minimum_Length = 30
        Initial_Maximum_Length = 15
        Initial_Cspacing       = 2
        Initial_Rspacing       = 2

        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_halign (Gtk.Align.CENTER);
        flowbox.set_max_children_per_line(30)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        #flowbox.set_column_spacing (Initial_Cspacing);
        #flowbox.set_row_spacing (Initial_Rspacing);
        flowbox.set_min_children_per_line (Initial_Minimum_Length);
        #flowbox.set_max_children_per_line (Initial_Maximum_Length);

        flowbox2 = Gtk.FlowBox()
        flowbox2.set_valign(Gtk.Align.START)
        flowbox2.set_halign (Gtk.Align.CENTER);
        flowbox2.set_max_children_per_line(30)
        flowbox2.set_selection_mode(Gtk.SelectionMode.NONE)
        #flowbox2.set_column_spacing (Initial_Cspacing);
        #flowbox2.set_row_spacing (Initial_Rspacing);
        flowbox2.set_min_children_per_line (Initial_Minimum_Length);
        #flowbox2.set_max_children_per_line (Initial_Maximum_Length);

        flowbox3 = Gtk.FlowBox()
        flowbox3.set_valign(Gtk.Align.START)
        flowbox3.set_halign (Gtk.Align.CENTER);
        flowbox3.set_max_children_per_line(30)
        flowbox3.set_selection_mode(Gtk.SelectionMode.NONE)
        #flowbox3.set_column_spacing (Initial_Cspacing);
        #flowbox3.set_row_spacing (Initial_Rspacing);
        flowbox3.set_min_children_per_line (Initial_Minimum_Length);
        #flowbox3.set_max_children_per_line (Initial_Maximum_Length);

        flowbox4 = Gtk.FlowBox()
        flowbox4.set_valign(Gtk.Align.START)
        flowbox4.set_halign (Gtk.Align.CENTER);
        flowbox4.set_max_children_per_line(30)
        flowbox4.set_selection_mode(Gtk.SelectionMode.NONE)
        #flowbox4.set_column_spacing (Initial_Cspacing);
        #flowbox4.set_row_spacing (Initial_Rspacing);
        flowbox4.set_min_children_per_line (Initial_Minimum_Length);
        #flowbox4.set_max_children_per_line (Initial_Maximum_Length);

        self.create_flowbox(flowbox)
        self.create_flowbox(flowbox2)
        self.create_flowbox(flowbox3)
        self.create_flowbox(flowbox4)

        scrolled1.add(flowbox)
        scrolled2.add(flowbox2)
        scrolled3.add(flowbox3)
        scrolled4.add(flowbox4)
        boxServo1.pack_start(scrolled1, True, True, 0)
        boxServo2.pack_start(scrolled2, True, True, 0)
        boxServo3.pack_start(scrolled3, True, True, 0)
        boxServo4.pack_start(scrolled4, True, True, 0)

        self.add(vpaned)

    # ---------------------------------
    # on_play_clicked
    # ---------------------------------
    def on_play_clicked(self, button):
        print("play button was clicked")

    # ---------------------------------
    # on_rec_clicked
    # ---------------------------------
    def on_rec_clicked(self, button):
        print("rec button was clicked")

    # ---------------------------------
    # on_stop_clicked
    # ---------------------------------
    def on_stop_clicked(self, button):
        print("stop button was clicked")

    # ---------------------------------
    # on_close_clicked
    # ---------------------------------
    def on_close_clicked(self, button):
        global close_app
        close_app = True
        print("Closing application")
        Gtk.main_quit()

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
    # on_pedro_combo_changed
    # ---------------------------------
    def on_pedro_combo_changed(self, combo):
        pedro_select = combo.get_active_iter()
        global ser
        if pedro_select != None:
            model = combo.get_model()
            select = model[pedro_select][0]
            # ser.close()
            ser = serial.Serial(str(pedro_list[select]))
            print (ser.isOpen())
            print ("Selected: Pedro: " + str(pedro_list[select]))
   
    # ---------------------------------
    # color_widget
    # ---------------------------------
    def color_widget(self, widget, color):
        color = Gdk.color_parse(color)
        rgba = Gdk.RGBA.from_color(color)
        widget.override_background_color(0, rgba)

    # ---------------------------------
    # on_area_button_press
    # ---------------------------------
    def on_area_button_press(self, widget, event):
        if event.button == 1:
            print ("left click")
        elif event.button == 2:
            print ("middle click")
        elif event.button == 3:
            print ("right click")
        print ('YES')
        self.mouseClick = True

    # ---------------------------------
    # on_area_button_release
    # ---------------------------------
    def on_area_button_release(self, widget, event):
        print ('NO')
        self.mouseClick = False

    # ---------------------------------
    # on_area_motion
    # ---------------------------------
    def on_area_motion(self, widget, event):
        if self.mouseClick:
            print (event.x, ' ', event.y)

    # ---------------------------------
    # on_changed_servo1
    # ---------------------------------    
    def on_changed_servo1(self, widget):
        global servo_change
        global serv1_chg
        global old_value1
        global servocmd
        if old_value1 >= int(servo1.get_value()) :
           servocmd = 11
        else:
           servocmd = 22
        servo_change = True
        serv1_chg = True
        old_value1 = int(servo1.get_value())


    # ---------------------------------
    # on_changed_servo2
    # --------------------------------- 
    def on_changed_servo2(self, widget):
        global servo_change
        global serv2_chg
        global old_value2
        global servocmd
        if old_value2 >= int(servo2.get_value()) :
            servocmd = 11
        else:
            servocmd = 22
        servo_change = True
        serv2_chg = True
        old_value2 = int(servo2.get_value())

    # ---------------------------------
    # on_changed_servo3
    # --------------------------------- 
    def on_changed_servo3(self, widget):
        global servo_change
        global serv3_chg
        global old_value3
        global servocmd
        if old_value3 >= int(servo3.get_value()) :
            servocmd = 11
        else:
            servocmd = 22
        servo_change = True
        serv3_chg = True
        old_value3 = int(servo3.get_value())

    # ---------------------------------
    # on_changed_servo4
    # --------------------------------- 
    def on_changed_servo4(self, widget):
        global servo_change
        global serv4_chg
        global old_value4
        global servocmd
        if old_value4 >= int(servo4.get_value()) :
            servocmd = 11
        else:
            servocmd = 22
        servo_change = True
        serv4_chg = True
        old_value4 = int(servo4.get_value())

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

        for color in colors:
            LabelMem = Gtk.Label ("    0    ")
            FrameMem = Gtk.Frame()
            self.color_widget(FrameMem, 'coral')
            button = self.color_swatch_new(color)
            FrameMem.add (LabelMem)
            flowbox.add(FrameMem)

window = Pedro()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
update_ser = Update_Serial()
update_ser.start()
get_serv = Get_Value_Servo()
get_serv.start()
Gtk.main()
update_ser.join()
get_serv.join()
