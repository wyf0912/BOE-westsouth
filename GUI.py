# -*- coding: UTF-8 -*-
import tkinter as tk
import threading


class GUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.speed_val = 0
        self.angle_val = 0

        self.root = tk.Tk()
        self.state_str = tk.StringVar(self.root)
        self.state_str.set('auto mode')
        self.state = tk.Label(self.root, textvariable=self.state_str)
        self.stop = tk.Button(self.root, text='Stop')
        self.trans = tk.Button(self.root, text='Trans Mode', command=self.trans_mode)

        self.entry = tk.Entry(self.root)
        self.entry.bind('<Key>', self.deal_key)

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
        self.entry.grid(row=2, column=0)
        self.root.mainloop()

    def trans_mode(self):
        if self.state_str.get() == 'auto mode':
            self.state_str.set('manual mode')
        else:
            self.state_str.set('auto mode')

        print(self.state_str.get())
        self.root.update()

    def deal_key(self, event):
        self.entry.delete(0, 10)
        event = event.char
        if event == 'f':
            self.speed_val = 0
            self.state_str.set('manual mode')
        if self.state_str.get() == 'manual mode':
            if event == 'w':
                self.speed_val += 10
            if event == 's':
                self.speed_val -= 10
            if event == 'a':
                self.angle_val -= 10
            if event == 'd':
                self.angle_val += 10
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

    def refresh_gui(self):
        pass


if __name__ == '__main__':
    # t1 = threading.Thread(target=GUI)
    # t1.start()
    gui = GUI()
    gui.start()
    #gui.refresh_gui()
    #t1 = threading.Thread(target=gui.refresh_gui)
   # t1.start()
    print("test")
