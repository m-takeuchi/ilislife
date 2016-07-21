from __future__ import division  # 少数点以下表示のためのモジュール

### For logging to current dir/log_dir
import os
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
Config.set('kivy', 'log_dir', os.path.dirname(os.path.abspath(__file__))+'/logs/')
print(Config.get('kivy', 'log_dir'))

from functools import partial
# from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock
from kivy.app import App

# Importing my modules
import e3640a_prologix as BPHV
import hioki
from kivy.properties import StringProperty
import datetime as dtm
import random

# Device settings
#tty = '/dev/tty.usbserial-PXWV0AMC'
VeAddr = 5
IcAddr = 1
IgAddr = 2

from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    # linux
    tty = '/dev/ttyUSB0'
elif _platform == "darwin":
    # OS X
    tty = '/dev/tty.usbserial-PXWV0AMC'
elif _platform == "win32":
    # Windows...
    # tty =
    pass

# Rc = 100e+3 # (ohm), Resistor for Faraday cup current
# Rg = 100e+3 # (ohm), Resistor for Extractor current
dV = 50 # (V)
dt_meas = 1 #(s) measurement interval
dt_op = 1 # (s) time per step for Ve change


# list of [Voltage (V), holding time(s)]
DT = 300 # (s) time per step for time-dependence measurement
SEQ = [ [3000, DT],\
        [3250, DT],\
        [3500, DT],\
        [3750, DT],\
        [4000, DT],\
        [4250, DT],\
        [4500, DT],\
        [4750, DT],\
        [5000, 3600]]

# Prepare file
# filename = 'tmp.dat'
directory = 'data/'
filename = directory+"{0:%y%m%d-%H%M%S}.dat".format(dtm.datetime.now())
with open(filename, mode = 'w', encoding = 'utf-8') as fh:
    fh.write('#date\ttime(s)\tVe(kV)\tIg(V)\tIc(V)\n')


# class MyRoot(TabbedPanel):
class MyRoot(BoxLayout):
    is_countup = BooleanProperty(False)
    is_sequence = BooleanProperty(False)
    is_connected = BooleanProperty(False)
    is_changevolt = BooleanProperty(False)
    is_holdvolt = BooleanProperty(False)
    time_now = NumericProperty(0)
    volt_now = NumericProperty(0.0)
    volt_target = NumericProperty(0.0)
    seq = ListProperty(SEQ)
    seq_now = NumericProperty(0)
    left_time = NumericProperty()
    Ve_status = StringProperty('Ve')
    Ic_status = StringProperty('Ic')
    Ig_status = StringProperty('Ig')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_command(self, command):
        global Ve_obj, Ic_obj, Ig_obj

        if command == 'connect/disconnect':
            if self.is_connected:
                self.disconnect_device()#Ve_obj, Ic_obj, Ig_obj)
            else:
                self.time_now = 0
                Ve_obj, Ic_obj, Ig_obj = self.connect_device()

        elif command == 'start/stop':
            if self.is_countup:
                self.stop_timer()
                # self.Stop_IncVolt()
                self.abort_sequence()
            else:
                # if self.is_connected:
                if Ve_obj:
                    msg = Ve_obj.Clear()
                ### for simple test ###
                # self.Start_IncVolt(1000, dt)
                self.start_timer()
                self.start_sequence(self.seq)
                #######################
                # else:
                    # print('Connect first')


        elif command == 'reset':
            self.abort_sequence()
#            self.stop_timer()
#            self.time_now = 0
#            if self.is_connected:
#                msg = Ve_obj.Clear()
#                Ve_obj.ShutDown()
#                Ig_obj.Cls()
#                Ic_obj.Cls()
#            self.Ve_status = str(self.volt_now)
        ### 以下追加条件


    def on_countup(self, dt):
        """Callback function for fetching measured values
        """
        try:
            Ig_value = Ig_obj.Measure()
            Ic_value = Ic_obj.Measure()
            self.Ic_status = str(Ic_value)
            self.Ig_status = str(Ig_value)
        except ValueError:
            Ig_value = '='
            Ic_value = '='
            self.Ic_status = Ic_obj.ClearBuffer()
            self.Ig_status = Ig_obj.ClearBuffer()
        Ve_value = self.volt_now
        ### データをファイルに追記
        StoreValue.append_to_file(filename, [self.time_now, Ve_value, Ig_value, Ic_value])
        self.time_now += 1

    def start_timer(self):
        self.is_countup = True
        Clock.schedule_interval(self.on_countup, dt_meas)
        pass

    def stop_timer(self):
        self.is_countup = False
        Clock.unschedule(self.on_countup)
        pass

    def connect_device(self):#, tty, VeAddr, IcAddr, IgAddr):
        """各GPIB機器を設定する
        """
        Ve_obj = BPHV.E3640A(tty, VeAddr)
        Ic_obj = hioki.dmm3239gpib(tty, IcAddr)
        Ig_obj = hioki.dmm3239gpib(tty, IgAddr)
        # self.Ve_status = Ve.Query('*IDN?')
        self.Ve_status = Ve_obj.Query('*IDN?')
        self.Ic_status = Ic_obj.Query('*IDN?')
        self.Ig_status = Ig_obj.Query('*IDN?')
        msg = Ve_obj.Clear()
        Ic_obj.Mode()
        Ic_obj.SampleRate(rate='medium')
        Ig_obj.Mode()
        Ig_obj.SampleRate(rate='medium')
        self.is_connected = True
        return Ve_obj, Ic_obj, Ig_obj

    def disconnect_device(self):#, Ve_obj, Ic_obj, Ig_obj):
        """設定したGPIB機器を初期状態に戻し, ポートを開放する
        """
        Ve_obj.VoltZero()
        Ve_obj.ShutDown()
        Ve_obj.Clear()
        Ic_obj.Rst()
        Ig_obj.Rst()
        self.Ve_status = 'Disconnected'
        self.Ic_status = 'Disconnected'
        self.Ig_status = 'Disconnected'
        # Ve_obj.ClosePort()
        self.is_connected = False

    # def increment_Volt(self, dt):
    def increment_Volt(self, volt_target, *largs):
        """Callback for increasing voltage
        """
        # print('I am in increment_Volt')
        self.volt_now = Ve_obj.AskVolt()*1000
        volt_raw_now = self.volt_now/1000
        deltaV_raw = dV/1000
        next_raw = '{0:.2f}'.format(volt_raw_now + deltaV_raw)
        Ve_obj.Instruct('volt ' + str(next_raw))
        Ve_obj.OutOn()
        # self.volt_now = '{0:.2f}'.format(Ve_obj.AskVolt())*1000
        self.volt_now = Ve_obj.AskVolt()*1000
        self.Ve_status = str(self.volt_now)
        if self.volt_now >= volt_target:
            self.is_changevolt = False
            return False

    # def decrement_Volt(self, dt):
    def decrement_Volt(self, volt_target, *largs):
        """Callback for decreasing voltage
        """
        # step_raw = Ve_obj.VoltStep(dV)
        self.volt_now = Ve_obj.AskVolt()*1000
        # print(type(self.volt_now))
        volt_raw_now = self.volt_now/1000
        deltaV_raw = dV/1000
        next_raw = '{0:.2f}'.format(volt_raw_now - deltaV_raw)
        Ve_obj.Instruct('volt ' + str(next_raw))
        Ve_obj.OutOn()
        # self.volt_now = '{0:.2f}'.format(Ve_obj.AskVolt())*1000
        self.volt_now = Ve_obj.AskVolt()*1000
        self.Ve_status = str(self.volt_now)
        if self.volt_now <= volt_target:
            self.is_changevolt = False
            return False

    def change_Volt(self, volt_target, *largs):
        """Callback for change voltage
        """
        self.volt_now = Ve_obj.AskVolt()*1000
        if self.volt_now == volt_target:
            return False
        elif self.volt_now < volt_target:
            self.increment_Volt(volt_target, *largs)
        elif self.volt_now > volt_target:
            self.decrement_Volt(volt_target, *largs)
        else:
            print('End change_Volt')
            return False


    def hold_Volt(self, left_time, *largs):
        """Hold voltage output by left_time == 0
        """
        self.volt_now = Ve_obj.AskVolt()*1000
        # print(type(self.volt_now))
        volt_raw_now = self.volt_now/1000
        # Ve_obj.Instruct('volt ' + str(volt_raw_now))
        # Ve_obj.OutOn()
        self.Ve_status = str(self.volt_now)
        if self.left_time <= 0:
            self.seq_now += 1 #シーケンスを1進める
            self.is_holdvolt = False
            return False
        self.left_time -= 1

    def start_sequence(self, seqlist):
        """Start voltage sequence
        """
        if not self.is_sequence:
            self.is_sequence = True
            # trigger = Clock.create_trigger(self.on_countdown, dt_meas)
            # trigger()
            Clock.schedule_interval(self.on_countdown, dt_meas/5)
            print('created on_countdown trigger')

    def on_countdown(self, dt):
        """Callback for voltage sequence
        """
        if self.seq_now < len(self.seq) -1:
            # print('I am in on_countdonw'+str(self.seq_now))
            # print(Clock.get_events())
            ### 現在電圧が現在シーケンス設定電圧より低い場合に電圧増加を実行
            self.volt_target = self.seq[self.seq_now][0]
            if self.volt_now < self.volt_target:
                ### 電圧変更中でない場合
                if not self.is_changevolt:
                    # イベントループに投入
                    self.is_changevolt = True
                    Clock.schedule_interval(partial(self.change_Volt, self.volt_target), dt_op)
                    print('Now on change voltage')


            ### 現在電圧が現在シーケンス設定電圧と等しく, 電圧変更中でなく, hold_Volt中でない場合
            else:
                if not self.is_changevolt and not self.is_holdvolt:
                    self.is_holdvolt = True
                    self.left_time = self.seq[self.seq_now][1] #left_timeにシーケンスリスト
                    # イベントループに投入
                    Clock.schedule_interval(partial(self.hold_Volt, self.left_time), dt_op)
                    print('Now on hold voltage')
        # except IndexError:
        elif self.seq_now == len[self.seq] -1:
            print('All sequences are finished. Measurement is now stopped.')
            self.abort_sequence()

    def get_seq(self):
        """Read sequence status
        """
        try:
            out = str(self.seq[self.seq_now])
        except IndexError:
            out = 'Sequence is over!'
        return out

    def lapse_time(self, t):
        """Retrun lapse time (hh:mm:ss format)
        """
        rh = (t-t%3600)/3600
        rm = (t-((t-rh*3600)%60))/60
        rs = t -rm*60
        return "{0:2.0f} [sub][i]H[/i][/sub] {1:2.0f} [sub][i]M[/i][/sub] {2:2.0f} [sub][i]S[/i][/sub]".format(rh,rm,rs)

    def total_time(self):
        l = len(self.seq)
        total=0
        for i in range(l):
            if i == 0:
                total += (self.seq[i][0]/dV)*dt_op
            else:
                total += ((self.seq[i][0]-self.seq[i-1][0])/dV)*dt_op
            total += self.seq[i][1]
        return total

    def remaining_time(self,t):
        total = self.total_time()
        rt = total - t
        return self.lapse_time(rt)

    def abort_sequence(self):
        """Force to abort measurement immediately
        """
        # events = Clock.get_events()
        # for ev in events:
        #    # Clock.unschedule(ev)
        #    ev.cancel()
        try:
            Clock.unschedule(self.on_countup)
        except:
            print('abort_sequence error 1')
            pass
        try:
            Clock.unschedule(self.on_countdown)
        except:
            print('abort_sequence error 2')
            pass
        try:
            Clock.unschedule(self.change_Volt)
        except:
            print('abort_sequence error 3')
            pass
        try:
            Clock.unschedule(self.hold_Volt)
        except:
            print('abort_sequence error 4')
            pass
        self.is_countdown = False
        self.is_countup = False
        self.is_changevolt = False
        self.is_sequence = False
        self.is_changevolt = False
        self.is_holdvolt = False
        if self.is_connected:
            msg = Ve_obj.Clear()
            Ve_obj.VoltZero()
            Ve_obj.OutOff()
            self.seq_now = 0
            self.time_now = 0
            self.volt_now = Ve_obj.AskVolt()*1000
            # Ve_obj.ShutDown()
            # Ig_obj.Cls()
            # Ic_obj.Cls()
        pass

    def Start_IncVolt(self, volt_target, dt):
        Clock.schedule_interval(partial(self.increment_Volt, volt_target), dt)
        self.is_changevolt = True
        pass

    def Stop_IncVolt(self):
        Clock.unschedule(self.increment_Volt)
        self.is_countup = False
        pass

class StoreValue(BoxLayout):
    """Store measured values to file
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def append_to_file(cls, filename, data1d):
        ## ファイルにデータ書き込み
        datastr = ''
        with open(filename, mode = 'a', encoding = 'utf-8') as fh:
            for data in data1d:
                datastr += '\t'+str(data)
            fh.write(str(cls.get_ctime()) + datastr + '\n')
    @classmethod
    def get_ctime(self):
        t = dtm.datetime.now()
        point = (t.microsecond - t.microsecond%10000)/10000
        app_time = "{0:%y%m%d-%H:%M:%S}.{1:.0f}".format(t, point)
        return app_time


# class MyGraph(BoxLayout):
#     sensorEnabled = BooleanProperty(False)
#     plot = ListProperty([])
#     graph_y_upl = NumericProperty(2)
#     graph_y_lwl = NumericProperty(-1)
#     graph_x_range = NumericProperty(100)
#     graph_x_hist = NumericProperty(0)
#     graph_x_step = NumericProperty(10)
#     data_buffer = ListProperty([[],[],[]])
#     BUFFSIZE = 10000
#     to_val = ListProperty([])
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#     #     Clock.schedule_once(self.prepare_graph,0)
#     # def prepare_graph(self, dt):
#     #     graph = Graph(\
#     #         label_options={'color': (1, 1, 1, 0.9), 'bold': True},\
#     #         background_color=(0.1, 0.1, 0.1, 1),\
#     #         tick_color=(1, 0, 1, 1),\
#     #         border_color=(1, 0, 1, 1),\
#     #         xlabel='Time (s)',\
#     #         # self.xlabel=str(self.ids),\
#     #         ylabel='Values',\
#     #         y_grid_label=True,\
#     #         x_grid_label=True,\
#     #         padding=5,\
#     #         x_ticks_major=10,\
#     #         x_grid=True,\
#     #         y_grid=True,\
#     #         xmin = self.graph_x_range  - self.graph_x_hist,\
#     #         xmax = 0 - self.graph_x_hist,\
#     #         ymin = self.graph_y_lwl,\
#     #         ymax = self.graph_y_upl)
#         #
#         # # 描画サイズ変数の定義
#         # size_root_x =1; size_root_y =1
#         # size_graph_x = 0.9; size_graph_y =0.9
#         # size_rlbl_x = size_root_x - size_graph_x
#         # size_rlbl_y = (size_root_y - size_graph_y)/3.
#         # size_rbtn_x = size_root_x - size_graph_x
#         # size_rbtn_y = 2*size_rlbl_y
#         #
#         # # 描画位置変数の定義
#         # pos_rlbl1 = 0.99
#         # pd = 0.1
#         # pos_rbtn1 = size_root_y-size_rbtn_y
#         # pos_rbtn2 = pos_rbtn1 - size_rbtn_y
#         # pos_rlbl2 = pos_rbtn2 - size_rbtn_y - pd
#         # pos_rbtn3 = pos_rlbl2 - size_rbtn_y
#         # pos_rbtn4 = pos_rbtn3 - size_rbtn_y
#         # pos_rbtn5 = pos_rbtn4 - size_rbtn_y - pd
#         # # Graphウィジェットの相対位置, 相対サイズ
#         # graph.pos_hint = {'top': 1}
#         # graph.size_hint = (size_graph_x,size_graph_y)
#
#         # ### Indicator of Uppper level
#         # lbl_upl = Label(text=str(self.graph_y_upl), size_hint=(size_rlbl_x,size_rlbl_y), pos_hint={'top':pos_rlbl1, 'right':1} )
#         # # lbl_upl.bind()
#         # ### buttons for y upper level
#         # bt1up = Button(text='+ UPL', size_hint=(size_rbtn_x,size_rbtn_y), pos_hint={'top':pos_rbtn1,'right':1})
#         # bt1up.bind(on_press=self.up_y_upl)
#         # bt1down = Button(text='- UPL', size_hint=(size_rbtn_x,size_rbtn_y), pos_hint={'top':pos_rbtn2,'right':1})
#         # bt1down.bind(on_press=self.down_y_upl)
#         #
#         # ### Indicator of Lower level
#         # lbl_lwl = Label(text=str(self.graph_y_lwl), size_hint=(size_rlbl_x,size_rlbl_y), pos_hint={'top':pos_rlbl2, 'right':1})
#         # ### buttons for y lower level
#         # bt2up = Button(text='+ UPL', size_hint=(size_rbtn_x,size_rbtn_y), pos_hint={'top':pos_rbtn3,'right':1})
#         # bt2up.bind(on_press=self.up_y_lwl)
#         # bt2down = Button(text='- UPL', size_hint=(size_rbtn_x,size_rbtn_y), pos_hint={'top':pos_rbtn4,'right':1})
#         # bt2down.bind(on_press=self.down_y_lwl)
#         #
#         # bttg = Button(text='do_toggle', size_hint=(size_rbtn_x,size_rbtn_y), pos_hint={'top':pos_rbtn5, 'right':1})
#         # bttg.bind(on_press=self.do_toggle)
#         #
#         # s = Slider(y=0, pos_hint={'x': .5}, size_hint=(.7, None), height=50)
#         # # s.bind(value=self._set_bezier_dash_offset)
#         # self.add_widget(graph)
#         # self.add_widget(lbl_upl)
#         # self.add_widget(bt1up)
#         # self.add_widget(bt1down)
#         # self.add_widget(lbl_lwl)
#         # self.add_widget(bt2up)
#         # self.add_widget(bt2down)
#         # self.add_widget(bttg)
#
#         # self.graph = self.graph_plot
#
#         # self.plot.append(MeshLinePlot(color=[1, 0, 0, 1]))  # X - Red
#         # self.plot.append(MeshLinePlot(color=[0, 1, 0, 1]))  # Y - Green
#         # self.plot.append(MeshLinePlot(color=[0, 0.5, 1, 1]))  # Z - Blue
#         # self.reset_plots()
#         # for plot in self.plot:
#         #     self.graph.add_plot(plot) # Add MeshLinePlot object of garden.graph into Graph()
#         #     # graph.add_plot(plot) # Add MeshLinePlot object of garden.graph into Graph()
#
#
#     # def up_y_upl(self, instance):
#     def up_y_upl(self):
#         self.graph_y_upl += 1
#     # def down_y_upl(self, instance):
#     def down_y_upl(self):
#         if (self.graph_y_upl -1 > self.graph_y_lwl):
#             self.graph_y_upl -= 1
#     # def up_y_lwl(self, instance):
#     def up_y_lwl(self):
#         if (self.graph_y_upl -1 > self.graph_y_lwl):
#             self.graph_y_lwl += 1
#     # def down_y_lwl(self, instance):
#     def down_y_lwl(self):
#         self.graph_y_lwl -= 1
#
#     def reset_plots(self):
#         for plot in self.plot:
#             # plot.points = [(0, 0),(1,0.5)]
#             plot.points = [(0, 0)]
#
#     def do_toggle(self):
#     # def do_toggle(self, instance):
#         try:
#             if not self.sensorEnabled:
#                 Clock.schedule_interval(self.get_mydata, 10 / 10.)
#                 self.sensorEnabled = True
#             else:
#                 Clock.unschedule(self.get_mydata)
#                 self.sensorEnabled = False
#         except NotImplementedError:
#                 popup = ErrorPopup()
#                 popup.open()
#
#     def get_mydata(self, dt):
#         self.to_val = val = self._make_random_data()
#         # self.to_val = val
#         # gr.make_random_data()
#         if len(self.data_buffer[0]) > self.BUFFSIZE:
#             del(self.data_buffer[0][0]) # バッファがサイズを越えたら古いvalから削除
#             del(self.data_buffer[1][0]) # バッファがサイズを越えたら古いvalから削除
#             del(self.data_buffer[2][0]) # バッファがサイズを越えたら古いvalから削除
#         if(not val == (None, None, None)):
#             self.data_buffer[0].append(val[0]) # バッファにデータを追加
#             self.data_buffer[1].append(val[1]) # バッファにデータを追加
#             self.data_buffer[2].append(val[2]) # バッファにデータを追加
#             ### 時間t を設定
#             buff_len = len(self.data_buffer[0])
#             t = list(range(buff_len))[::-1]
#
#             # for i, p in enumerate(self.plot):
#                 # self.plot[i].points = self.T_list(t, self.data_buffer[i][-buff_len:]) #リストの転置
#             self.plot[0].points = self.T_list(t, self.data_buffer[0][-buff_len:])
#             self.plot[1].points = self.T_list(t, self.data_buffer[1][-buff_len:])
#             self.plot[2].points = self.T_list(t, self.data_buffer[2][-buff_len:])
#             print(self.graph_y_upl,self.graph_y_lwl)
#
#     def T_list(self, x, y):
#          #リストの転置
#         return list(map(list, zip(*[x, y] )))
#     def format_val(self, val):
#         return '{0:.3f}'.format(val)
#     def _make_random_data(self):
#         ## valに値を代入する. 例では乱数を入れている.
#         self.val = [random.random()+0.2, random.random(), random.random()-0.2]
#         return self.val


class IlislifeApp(App):
    def build(self):
        return MyRoot()
    pass

if __name__ == '__main__':
    IlislifeApp().run()
