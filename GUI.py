# -*- coding: UTF-8 -*-
try:
    import tkinter as tk
except:
    import Tkinter as tk
import threading
import pigpio

class GUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.argument_dict={}
        self.speed_val = 0
        self.angle_val = 0
        
        self.flag = 0 # stop car
        self.timer_delay = 0.4  #舵机归中时间
        self.timer = threading.Timer(self.timer_delay, self.angle_0)
        self.timer.start()

        self.root = tk.Tk()
        self.state_str = tk.StringVar(self.root)
        self.state_str.set('auto mode')
        self.state = tk.Label(self.root, textvariable=self.state_str)
        self.stop = tk.Button(self.root, text='Stop')
        self.trans = tk.Button(self.root, text='Trans Mode', command=self.trans_mode)

        # self.entry = tk.Entry(self.root)
        # self.entry.bind('<Key>', self.deal_key)
        self.root.bind('<KeyPress>', self.deal_key)
        self.root.protocol('WM_DELETE_WINDOW',self.closeWindow)
        #self.root.bind('<KeyRelease>', self.release_key)
        
        self.angle_str = tk.StringVar(self.root)
        self.speed_str = tk.StringVar(self.root)
        self.speed_str.set('速度：0')
        self.angle_str.set('角度：0')
        self.speed = tk.Label(self.root, textvariable=self.speed_str)
        self.angle = tk.Label(self.root, textvariable=self.angle_str)

        self.angle.grid(row=0, column=1, padx=40, pady=40)
        self.speed.grid(row=0, column=0, padx=40, pady=40)
        self.stop.grid(row=1, column=1, padx=40, pady=40)
        self.trans.grid(row=1, column=0, padx=40, pady=40)
        self.state.grid(row=2, column=1)

        self.menubar = tk.Menu(self.root)
        self.menubar.add_command(label="Args", command=self.argument_table)
        self.root.config(menu=self.menubar)

        self.args_refresh_flag = 0
        

        self.root.protocol('WM_DELETE_WINDOW', self.closeWindow)
        self.root.mainloop()



    def closeWindow(self):
        print('close window')
        self.timer.cancel()
        self.root.destroy()
        self.pi = pigpio.pi()
        self.pi.bb_serial_read_close(18)

    def angle_0(self):
        if self.flag:
            self.speed_val=0
            self.flag=0
        self.angle_val = 0
        self.timer = threading.Timer(self.timer_delay, self.angle_0)
        self.timer.start()
        self.speed_str.set('速度：' + str(self.speed_val))
        self.angle_str.set('角度：' + str(self.angle_val))


    def trans_mode(self):
        if self.state_str.get() == 'auto mode':
            self.state_str.set('manual mode')
        else:
            self.state_str.set('auto mode')

        print(self.state_str.get())
        self.root.update()
    
    def release_key(self,event):
        #print(event)
        pass
        
    def deal_key(self, event):
        # self.entry.delete(0, 10)
        #print(event)
        event = event.char
        
        self.timer.cancel()
        self.timer = threading.Timer(self.timer_delay, self.angle_0)
        self.timer.start()

        if event == 'f':
            #if self.speed_val>0:
            self.speed_val = 0
            #else:
            #    self.speed_val = 0
            self.state_str.set('manual mode')
            #self.flag=1

        if self.state_str.get() == 'manual mode':
            if event == 'w':
                self.speed_val += 10
            if event == 's':
                self.speed_val -= 10
            if event == 'a':
                self.angle_val += 20
            if event == 'd':
                self.angle_val -= 20
            if self.speed_val < -100:
                self.speed_val = -100
            if self.speed_val > 100:
                self.speed_val = 100
            if self.angle_val > 90:
                self.angle_val = 90
            if self.angle_val < -90:
                self.angle_val = -90
            self.speed_str.set('速度：' + str(self.speed_val))
            self.angle_str.set('角度：' + str(self.angle_val))

        else:
            self.speed_val = 0
            self.angle_val = 0

    def argument_table(self):
        self.table = tk.Toplevel()
        file_object = open('argument.txt')
        text = file_object.read()

        self.argument_dict = dict(eval(text))
        #print(self.argument_dict)
        self.item = {}
        i = 0
        for key in self.argument_dict.keys():
            self.item[key] = tk.Label(self.table, text=key)
            self.item[key].grid(row=i, column=0)
            self.item[key + 'str'] = tk.StringVar()
            self.item[key + 'str'].set(str(self.argument_dict[key]))
            print(str(self.argument_dict[key]))
            self.item[key + 'val'] = tk.Entry(self.table, textvariable=self.item[key + 'str'])
            self.item[key + 'val'].grid(row=i, column=1)

            i = i + 1

        save = tk.Button(self.table, text='Save', command=self.save_args)
        save.grid(row=i + 1, column=1)
        file_object.close()
        self.table.mainloop()

    def save_args(self):
        if self.argument_dict=={}:
            with open('argument.txt', 'r') as file_object:
                text = file_object.read()
                self.argument_dict = dict(eval(text))
        else:
            for key in self.argument_dict.keys():
                self.argument_dict[key] = self.item[key + 'val'].get()
            with open('argument.txt', 'w') as file:
                file.write(str(self.argument_dict))
        self.args_refresh_flag = 1


if __name__ == '__main__':
    # t1 = threading.Thread(target=GUI)
    # t1.start()
    gui = GUI()
    gui.run()
    # gui.refresh_gui()
    # t1 = threading.Thread(target=gui.refresh_gui)
    # t1.start()
    print("test")
