import csv
import datetime
import os
import tkinter as tk

IMGS = "img"
CSV = "csv"
COLOR1 = "#f4ede6"
COLOR2 = "#e9dbcc"
COLOR3 = "#dec8b1"
COLOR4 = "#c8a580"


################################################################
#------------------------# Home class #------------------------#
################################################################
class Home(tk.Frame):
    def __init__(self, master=None):
        self.master = master
        self.color1 = COLOR1
        self.color2 = COLOR2
        self.color3 = COLOR3
        self.color4 = COLOR4
        self.mode = tk.IntVar()
        self.rd = []
        self.rv = []
        self.rf = []
        self.rn = 10
        self.index = 0
        self.widgets = []
        super().__init__(master, bg=self.color1)
        self.read_csv()

        # ----------------------# sidebar #----------------------#
        self.sidebar = tk.Frame(self, width=350, bg=self.color2)
        logoimg = IMGS + "/logo.png"
        self.logo = tk.PhotoImage(file=logoimg)
        self.logo_label = tk.Label(self.sidebar, bg=self.color2, image=self.logo)
        self.btnframe = tk.Frame(self.sidebar, bg=self.color2)
        self.button1 = tk.Button(self.btnframe, command=self.master.open_dir, bg=self.color3, activebackground=self.color3, width=20, height=2, relief=tk.FLAT, text="フォルダを開く", font=("BIZ UDゴシック", 11))
        self.button2 = tk.Button(self.btnframe, command=self.master.open_video, bg=self.color3, activebackground=self.color3, width=20, height=2, relief=tk.FLAT, text="動画を開く", font=("BIZ UDゴシック", 11))
        self.button3 = tk.Button(self.btnframe, command=self.master.open_file, bg=self.color3, activebackground=self.color3, width=20, height=2, relief=tk.FLAT, text="画像を開く", font=("BIZ UDゴシック", 11))
        self.modeframe = tk.Frame(self.sidebar, bg=self.color2)
        self.mode.set(1)
        self.scale = tk.Scale(self.modeframe, orient=tk.HORIZONTAL, bg=self.color4, activebackground=self.color4, troughcolor=self.color3, borderwidth=0, from_=1, to=2, highlightthickness=0, showvalue=0, sliderrelief=tk.FLAT, variable=self.mode)
        self.logo_label.grid(row=0, column=0, sticky=tk.N)
        self.btnframe.grid(row=1, column=0, sticky=tk.N, pady=20)
        self.button1.grid(row=0, column=0, sticky=tk.N, pady=8)
        self.button2.grid(row=1, column=0, sticky=tk.N, pady=8)
        self.button3.grid(row=2, column=0, sticky=tk.N, pady=8)
        self.modeframe.grid(row=2, column=0, sticky=tk.N)
        self.scale.grid(row=0, column=0, sticky=tk.N, pady=5)
        self.sidebar.grid(row=0, column=0, sticky=tk.NS+tk.W)

        # ----------------------# homemain #----------------------#
        self.homemain = tk.Frame(self, bg=self.color1)
        self.homemain.grid(row=0, column=1, sticky=tk.NSEW, pady=10)
        buttonimg = IMGS + "/button.png"
        self.btn = tk.PhotoImage(file=buttonimg)
        #recentdirframe
        self.rdframe = tk.Frame(self.homemain, bg=self.color1)
        self.rdbutton = tk.Button(self.rdframe, command=lambda:self.set_index(0), bg=self.color1, activebackground=self.color1, relief=tk.FLAT, image=self.btn)
        self.rdlabel = tk.Label(self.rdframe, bg=self.color1, text="最近開いたフォルダ", font=("BIZ UDゴシック", 12))
        self.rdbutton.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rdlabel.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.rdlist = tk.Frame(self.rdframe, bg=self.color1)
        self.rds = []
        for i in range(self.rn):
            fullpath, date = self.get_data(self.rd, i+1)
            self.rds.append(Resent(self.rdlist, mode=1, fullpath=fullpath, date=date))
            self.rds[i].grid(row=i+1, column=0, sticky=tk.EW, pady=4)
        self.rdlist.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.EW)
        self.rdlist.columnconfigure(0, weight=1)
        self.rdframe.grid(row=0, column=0, sticky=tk.N+tk.EW, padx=25, pady=5)
        self.rdframe.columnconfigure(1, weight=1)
        #recentvideoframe
        self.rvframe = tk.Frame(self.homemain, bg=self.color1)
        self.rvbutton = tk.Button(self.rvframe, command=lambda:self.set_index(1), bg=self.color1, activebackground=self.color1, relief=tk.FLAT, image=self.btn)
        self.rvlabel = tk.Label(self.rvframe, bg=self.color1, text="最近開いた動画", font=("BIZ UDゴシック", 12))
        self.rvbutton.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rvlabel.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.rvlist = tk.Frame(self.rvframe, bg=self.color1)
        self.rvs = []
        for i in range(self.rn):
            fullpath, date = self.get_data(self.rv, i+1)
            self.rvs.append(Resent(self.rvlist, mode=2, fullpath=fullpath, date=date))
            self.rvs[i].grid(row=i+1, column=0, sticky=tk.EW, pady=4)
        self.rvlist.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.EW)
        self.rvlist.columnconfigure(0, weight=1)
        self.rvframe.grid(row=1, column=0, sticky=tk.N+tk.EW, padx=25, pady=5)
        self.rvframe.columnconfigure(1, weight=1)
        #recentfileframe
        self.rfframe = tk.Frame(self.homemain, bg=self.color1)
        self.rfbutton = tk.Button(self.rfframe, command=lambda:self.set_index(2), bg=self.color1, activebackground=self.color1, relief=tk.FLAT, image=self.btn)
        self.rflabel = tk.Label(self.rfframe, bg=self.color1, text="最近開いた画像", font=("BIZ UDゴシック", 12))
        self.rfbutton.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rflabel.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.rflist = tk.Frame(self.rfframe, bg=self.color1)
        self.rfs = []
        for i in range(self.rn):
            fullpath, date = self.get_data(self.rf, i+1)
            self.rfs.append(Resent(self.rflist, fullpath=fullpath, date=date))
            self.rfs[i].grid(row=i+1, column=0, sticky=tk.EW, pady=4)
        self.rflist.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.EW)
        self.rflist.columnconfigure(0, weight=1)
        self.rfframe.grid(row=2, column=0, sticky=tk.N+tk.EW, padx=25, pady=5)
        self.rfframe.columnconfigure(1, weight=1)
        #設定
        self.homemain.columnconfigure(0, weight=1)

        self.widgets.append(self.rdlist)
        self.widgets.append(self.rvlist)
        self.widgets.append(self.rflist)
        self.reset_index(2)
        self.reset_index(1)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


    # ----------------------# index操作 #----------------------#
    def set_index(self, index):
        self.reset_index()
        self.widgets[index].grid()
        self.index = index

    def reset_index(self, index=None):
        index = self.index if index==None else index
        self.widgets[index].grid_remove()


    # ----------------------# csv操作 #----------------------#

    # 読み込み
    def read_csv(self):
        with open(CSV+"/rf.csv", "r", newline="") as f:
            self.rf = [row for row in csv.reader(f)]
        with open(CSV+"/rd.csv", "r", newline="") as f:
            self.rd = [row for row in csv.reader(f)]
        with open(CSV+"/rv.csv", "r", newline="") as f:
            self.rv = [row for row in csv.reader(f)]

    # データ取得
    def get_data(self, csv, i):
        fullpath = None
        date = None
        if csv[i][0] != "":
            fullpath = csv[i][0]
            date = csv[i][1]
        return fullpath, date

    # データ書き換え
    def rewrite_data(self, csv, fullpath, rforrd):
        match = 1
        for i in range(1, self.rn):
            if fullpath == csv[i][0]:
                break
            match += 1
        csv.pop(match)
        dt = datetime.datetime.today()
        new_data = [fullpath, str(dt.month)+"/"+str(dt.day)+" "+str(dt.hour)+":"+str(dt.minute).zfill(2)]
        csv.insert(1, new_data)
        for i in range(self.rn):
            fullpath, date = self.get_data(csv, i+1)
            rforrd[i].set_strs(fullpath, date)
    
    # データ初期化
    def init_data(self):
        for i in range(self.rn):
            self.rf[i+1] = ['', '']
            self.rd[i+1] = ['', '']
            self.rv[i+1] = ['', '']
            fullpathf, datef = self.get_data(self.rf, i+1)
            fullpathd, dated = self.get_data(self.rd, i+1)
            fullpathv, datev = self.get_data(self.rv, i+1)
            self.rfs[i].set_strs(fullpathf, datef)
            self.rds[i].set_strs(fullpathd, dated)
            self.rvs[i].set_strs(fullpathv, datev)

    # 書き込み
    def write_csv(self):
        with open(CSV+"/rf.csv", "w", newline="") as f:
            csv.writer(f).writerows(self.rf)
        with open(CSV+"/rd.csv", "w", newline="") as f:
            csv.writer(f).writerows(self.rd)
        with open(CSV+"/rv.csv", "w", newline="") as f:
            csv.writer(f).writerows(self.rv)


######################### Resent class #########################
class Resent(tk.Frame):
    def __init__(self, master=None, mode=0, fullpath=None, date=None):
        self.master = master
        self.mode = mode
        self.color2 = COLOR2
        self.color3 = COLOR3
        self.font = ("", 10)
        self.height = 2
        super().__init__(master, bg=self.color2, relief=tk.FLAT)
        self.column0str = tk.StringVar()
        self.column1str = tk.StringVar()
        self.column2str = tk.StringVar()
        self.column0 = tk.Label(self, width=15, textvariable=self.column0str, bg=self.color2, font=self.font, anchor=tk.W, height=self.height)
        self.column1 = tk.Label(self, textvariable=self.column1str, bg=self.color2, font=self.font, anchor=tk.W, height=self.height)
        self.column2 = tk.Label(self, width=11, textvariable=self.column2str, bg=self.color2, font=self.font, anchor=tk.W, height=self.height)
        self.button = tk.Button(self, command=self.open, bg=self.color3, activebackground=self.color3, relief=tk.FLAT, width=10, text="開く", font=self.font)
        self.column0.grid(row=0, column=0, sticky=tk.W, padx=4)
        self.column1.grid(row=0, column=1, sticky=tk.W, padx=4)
        self.column2.grid(row=0, column=2, sticky=tk.W, padx=4)
        self.button.grid(row=0, column=3, sticky=tk.NS)
        self.columnconfigure(1, weight=1)
        self.set_strs(fullpath, date)
    # 更新
    def set_strs(self, fullpath, date):
        self.fullpath = fullpath
        if self.fullpath != None:
            column1str, column0str = os.path.split(fullpath)
            self.column0str.set(column0str)
            self.column1str.set(column1str)
            self.column2str.set(date)
            self.button.config(state=tk.NORMAL)
        else:
            self.column0str.set("-----")
            self.column1str.set("---------------")
            self.column2str.set("-----")
            self.button.config(state=tk.DISABLED)
    # button
    def open(self):
        if self.mode == 0:
            self.open_rf()
        elif self.mode == 1:
            self.open_rd()
        elif self.mode == 2:
            self.open_rv()
    # button（画像）
    def open_rf(self):
        if os.path.exists(self.fullpath):
            self.master.master.master.master.master.read_show_file(self.fullpath)
            self.master.master.master.master.rewrite_data(self.master.master.master.master.rf, self.fullpath, self.master.master.master.master.rfs)
    # button（フォルダ）
    def open_rd(self):
        if os.path.exists(self.fullpath):
            self.master.master.master.master.master.read_show_dir(self.fullpath)
            self.master.master.master.master.rewrite_data(self.master.master.master.master.rd, self.fullpath, self.master.master.master.master.rds)
    # button（動画）
    def open_rv(self):
        if os.path.exists(self.fullpath):
            self.master.master.master.master.master.read_show_video(self.fullpath)
            self.master.master.master.master.rewrite_data(self.master.master.master.master.rv, self.fullpath, self.master.master.master.master.rvs)
