import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import home
import viewer

NAME = "LiViewer"
VERSION = "0.11"
ICON = "icon.ico"
IMAGE_EXTENSIONS = [("JPEG", ".jpg"), ("PNG", ".png"), ("TIFF", ".tif")]
VIDEO_EXTENSIONS = [("MP4",".mp4")]
MAG = 1.1


################################################################
#------------------------# Main class #------------------------#
################################################################
class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(NAME)
        self.iconbitmap(default=ICON)
        self.geometry("1050x600")
        self.minsize(width=350, height=320)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.bind("<Control-o>", self.ctrl_o)
        self.bind("<Control-v>", self.ctrl_v)
        self.bind("<Control-i>", self.ctrl_i)
        self.bind("<Control-d>", self.ctrl_d)
        self.bind("m", self.key_m)

        self.bind(";", self.key_plus)
        self.bind("+", self.key_plus)
        self.bind("-", self.key_minus)
        self.bind("<Control-Key-1>", self.ctrl_one)
        self.bind("<Control-Key-0>", self.ctrl_zero)
        self.bind("<Control-MouseWheel>", self.ctrl_wheel)
        self.bind("f", self.key_f)
        self.bind("<Escape>", self.key_esc)

        self.bind("<Right>", self.key_right)
        self.bind("<Left>", self.key_left)
        self.bind("<Up>", self.key_up)
        self.bind("<Down>", self.key_down)
        self.bind("<Shift-MouseWheel>", self.shift_wheel)
        self.bind("<MouseWheel>", self.wheel)
        self.bind("<Control-Right>", self.ctrl_right)
        self.bind("<Control-Left>", self.ctrl_left)
        self.bind("<Control-Down>", self.ctrl_down)
        self.bind("<Control-Up>", self.ctrl_up)
        self.bind("q", lambda e: self.key_one_zero(e, 0))
        self.bind("1", lambda e: self.key_one_zero(e, 0.1))
        self.bind("2", lambda e: self.key_one_zero(e, 0.2))
        self.bind("3", lambda e: self.key_one_zero(e, 0.3))
        self.bind("4", lambda e: self.key_one_zero(e, 0.4))
        self.bind("5", lambda e: self.key_one_zero(e, 0.5))
        self.bind("6", lambda e: self.key_one_zero(e, 0.6))
        self.bind("7", lambda e: self.key_one_zero(e, 0.7))
        self.bind("8", lambda e: self.key_one_zero(e, 0.8))
        self.bind("9", lambda e: self.key_one_zero(e, 0.9))
        self.bind("0", lambda e: self.key_one_zero(e, 1))

        self.bind("<space>", self.space)
        self.bind("<Control-space>", self.ctrl_space)
        self.bind("<Control-k>", self.ctrl_k)
        self.bind("[", self.lbracket)
        self.bind("]", self.rbracket)
        self.bind("<Control-[>", self.ctrl_lbracket)
        self.bind("<Control-]>", self.ctrl_rbracket)
        self.bind("<Shift-{>", self.shift_lbracket)
        self.bind("<Shift-}>", self.shift_rbracket)

        self.bind("<Control-q>", self.ctrl_q)

        ## index : Home = 0, LiViewer = 1, TiViewer = 2 ##
        self.index = 0
        self.widgets = []

        self.nowplay = False
        self.fps = 10
        self.rngx = 0
        self.rngy = 0

        self.fullscreen = False

        # ----------------------# メニュー #----------------------#
        self.menu = tk.Menu(self)
		# Menu>ファイル
        self.menu_file = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="ファイル", menu=self.menu_file)
        self.menu_file.add_command(label="フォルダを開く", command=self.open_dir, accelerator="Ctrl+O")
        self.menu_file.add_command(label="動画を開く", command=self.open_video, accelerator="Ctrl+V")
        self.menu_file.add_command(label="画像を開く", command=self.open_file, accelerator="Ctrl+I")
        self.menu_file.add_separator()
        self.menu_file.add_command(label="全て閉じる", command=self.close_all, accelerator="Ctrl+D")
        self.menu_file.add_separator()
        self.menu_file.add_command(label="モード切替", command=self.mode_change, accelerator="M")
        # Menu>編集
        self.menu_edit = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="編集", menu=self.menu_edit)
        self.menu_edit.add_command(label="履歴削除", command=self.delete_history, accelerator="Ctrl+D")
        # Menu>再生
        self.menu_play = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="再生", menu=self.menu_play)
        self.menu_play.add_command(label="再生/停止", command=self.start_stop, accelerator="Space")
        self.menu_play.add_command(label="逆再生", command=self.rev_start, accelerator="Ctrl+Space")
        self.menu_play.add_separator()
        self.menu_play.add_command(label="再生設定", command=self.open_setting, accelerator="Ctrl+K")
		# Menu>表示
        self.menu_display = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="表示", menu=self.menu_display)
        self.menu_display.add_command(label="拡大", command=self.zoomin, accelerator="+")
        self.menu_display.add_command(label="縮小", command=self.zoomout, accelerator="-")
        self.menu_display.add_command(label="元の大きさ", command=self.original_size, accelerator="Ctrl+1")
        self.menu_display.add_command(label="画面に合わせる", command=self.fit_canvas, accelerator="Ctrl+0")
        self.menu_display.add_separator()
        self.menu_display.add_command(label="全画面表示", command=self.show_fullscreen, accelerator="F")
        # Menu>ヘルプ
        self.menu_help = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="ヘルプ", menu=self.menu_help)
        self.menu_help.add_command(label="バージョン情報", command=self.version_info)
		# 設置
        self.config(menu=self.menu)

        # ----------------------# Widget #----------------------#
        self.home = home.Home(self)
        self.home.grid(row=0, column=0, sticky=tk.NSEW)
        self.liviewer = viewer.LiViewer(self)
        self.liviewer.grid(row=0, column=0, sticky=tk.NSEW)
        self.tiviewer = viewer.TiViewer(self)
        self.tiviewer.grid(row=0, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.widgets.append(self.home)
        self.widgets.append(self.liviewer)
        self.widgets.append(self.tiviewer)
        self.reset_index(2)
        self.reset_index(1)
        self.menu_activate(self.index)


    # ----------------------# index操作 #----------------------#
    def set_index(self, index):
        self.reset_index()
        self.widgets[index].grid()
        self.menu_activate(index)
        self.index = index

    def reset_index(self, index=None):
        index = self.index if index==None else index
        self.widgets[index].grid_remove()

    def menu_activate(self, index):
        if index == 0:
            self.menu_file.entryconfigure("全て閉じる", state=tk.DISABLED)
            self.menu_file.entryconfigure("モード切替", state=tk.NORMAL)
            self.menu_edit.entryconfigure("履歴削除", state=tk.NORMAL)
            self.menu_play.entryconfigure("再生/停止", state=tk.DISABLED)
            self.menu_play.entryconfigure("逆再生", state=tk.DISABLED)
            self.menu_display.entryconfigure("拡大", state=tk.DISABLED)
            self.menu_display.entryconfigure("縮小", state=tk.DISABLED)
            self.menu_display.entryconfigure("元の大きさ", state=tk.DISABLED)
            self.menu_display.entryconfigure("画面に合わせる", state=tk.DISABLED)
        else:
            self.menu_file.entryconfigure("全て閉じる", state=tk.NORMAL)
            self.menu_file.entryconfigure("モード切替", state=tk.DISABLED)
            self.menu_edit.entryconfigure("履歴削除", state=tk.DISABLED)
            self.menu_play.entryconfigure("再生/停止", state=tk.NORMAL)
            self.menu_play.entryconfigure("逆再生", state=tk.NORMAL)
            self.menu_display.entryconfigure("拡大", state=tk.NORMAL)
            self.menu_display.entryconfigure("縮小", state=tk.NORMAL)
            self.menu_display.entryconfigure("元の大きさ", state=tk.NORMAL)
            self.menu_display.entryconfigure("画面に合わせる", state=tk.NORMAL)


    # ----------------------# Menu / Home 動作 #----------------------#

    # Menu>ファイル>フォルダを開く / Home>フォルダを開く
    def open_dir(self):
        dirname = filedialog.askdirectory()
        if dirname != "":
            self.home.rewrite_data(self.home.rd, dirname, self.home.rds)
            self.read_show_dir(dirname)

    # Menu>ファイル>動画を開く / Home>動画を開く
    def open_video(self):
        fullpath = filedialog.askopenfilename(filetypes=VIDEO_EXTENSIONS)
        if fullpath != "":
            self.home.rewrite_data(self.home.rv, fullpath, self.home.rvs)
            self.read_show_video(fullpath)

    # Menu>ファイル>画像を開く / Home>画像を開く
    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=IMAGE_EXTENSIONS)
        if filename != "":
            self.home.rewrite_data(self.home.rf, filename, self.home.rfs)
            self.read_show_file(filename)

    # Menu>ファイル>全て閉じる
    def close_all(self):
        if self.nowplay:
            self.nowplay = False
            self.after_cancel(self.id)
        if self.index == 1:
            self.liviewer.cleanup()
        elif self.index == 2:
            self.tiviewer.cleanup()
        self.set_index(0)
    
    # Menu>ファイル>モード切替
    def mode_change(self):
        self.home.mode.set(2) if self.home.mode.get() == 1 else self.home.mode.set(1)

    # Menu>編集>履歴削除
    def delete_history(self):
        message = "履歴を削除しますか？"
        if messagebox.askokcancel(NAME, message):
            self.home.init_data()

    # Menu>再生>再生/停止
    def start_stop(self):
        if self.nowplay:
            self.nowplay = False
            self.after_cancel(self.id)
        else:
            self.nowplay = True
            self.playback()

    # Menu>再生>逆再生
    def rev_start(self):
        if self.nowplay:
            self.after_cancel(self.id)
        else:
            self.nowplay = True
        self.rev_playback()

    # Menu>編集>再生設定
    def open_setting(self):
        self.setting = Setting(self)

    # Menu>表示>拡大
    def zoomin(self):
        if self.index == 1:
            self.liviewer.resize(MAG)
        elif self.index == 2:
            self.tiviewer.resize(MAG)

    # Menu>表示>縮小
    def zoomout(self):
        if self.index == 1:
            self.liviewer.resize(1/MAG)
        elif self.index == 2:
            self.tiviewer.resize(1/MAG)

    # Menu>表示>元の大きさ
    def original_size(self):
        if self.index == 1:
            self.liviewer.resize()
        elif self.index == 2:
            self.tiviewer.resize()

    # Menu>表示>画面に合わせる
    def fit_canvas(self):
        if self.index == 1:
            self.liviewer.resize_cs()
        elif self.index == 2:
            self.tiviewer.resize_cs()
    
    # Menu>表示>全画面表示
    def show_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
            self.config(menu=self.menu)
            self.liviewer.lframe.grid()
            self.tiviewer.lframe.grid()
            self.attributes("-fullscreen", False)
        else:
            self.fullscreen = True
            self.config(menu=False)
            self.liviewer.lframe.grid_remove()
            self.tiviewer.lframe.grid_remove()
            self.attributes("-fullscreen", True)

    # Menu>ヘルプ>バージョン情報
    def version_info(self):
        message = "バージョン: " + VERSION
        messagebox.showinfo(NAME, message)


    # ----------------------# イベント動作 #----------------------#
    
    # ctrl + O（フォルダを開く）
    def ctrl_o(self, event):
        self.open_dir()
    
    # ctrl + V（動画を開く）
    def ctrl_v(self, event):
        self.open_video()

    # ctrl + I（画像を開く）
    def ctrl_i(self, event):
        self.open_file()

    # ctrl + D（履歴削除 / 全て閉じる）
    def ctrl_d(self, event):
        if self.index == 0:
            self.delete_history()
        elif self.index == 1 or self.index == 2:
            self.close_all()
    
    # M（モード切替）
    def key_m(self, event):
        if self.index == 0:
            self.mode_change()

    # ctrl + K（再生設定）
    def ctrl_k(self, event):
        self.open_setting()

    # ; or +（拡大）
    def key_plus(self, event):
        if self.index == 1 or self.index == 2:
            self.zoomin()

    # -（縮小）
    def key_minus(self, event):
        if self.index == 1 or self.index == 2:
            self.zoomout()

    # ctrl + 1（元の大きさ）
    def ctrl_one(self, event):
        if self.index == 1 or self.index == 2:
            self.original_size()

    # ctrl + 0（画面に合わせる）
    def ctrl_zero(self, event):
        if self.index == 1 or self.index == 2:
            self.fit_canvas()

    # ctrl + ホイール（拡大縮小）
    def ctrl_wheel(self, event):
        if self.index == 1:
            self.liviewer.resize(MAG) if 0 < event.delta else self.liviewer.resize(1/MAG)
        elif self.index == 2:
            self.tiviewer.resize(MAG) if 0 < event.delta else self.tiviewer.resize(1/MAG)
    
    # F（全画面表示）
    def key_f(self, event):
        self.show_fullscreen()

    # esc（全画面表示終了）
    def key_esc(self, event):
        if self.fullscreen:
            self.fullscreen = False
            self.config(menu=self.menu)
            self.liviewer.lframe.grid()
            self.tiviewer.lframe.grid()
            self.attributes("-fullscreen", False)

    # Right（右移動）
    def key_right(self, event):
        if self.index == 1:
            self.liviewer.move_right()
        elif self.index == 2:
            self.tiviewer.move_right()

    # Left（左移動）
    def key_left(self, event):
        if self.index == 1:
            self.liviewer.move_left()
        elif self.index == 2:
            self.tiviewer.move_left()

    # Up（上移動）
    def key_up(self, event):
        if self.index == 1:
            self.liviewer.move_up()
        elif self.index == 2:
            self.tiviewer.move_up()

    # Down（下移動）
    def key_down(self, event):
        if self.index == 1:
            self.liviewer.move_down()
        elif self.index == 2:
            self.tiviewer.move_down()

    # shift + ホイール（横移動）
    def shift_wheel(self, event):
        if self.index == 1:
            self.liviewer.move_left() if 0 < event.delta else self.liviewer.move_right()
        elif self.index == 2:
            self.tiviewer.move_left() if 0 < event.delta else self.tiviewer.move_right()

    # ホイール（縦移動）
    def wheel(self, event):
        if self.index == 1:
            self.liviewer.move_up() if 0 < event.delta else self.liviewer.move_down()
        elif self.index == 2:
            self.tiviewer.move_up() if 0 < event.delta else self.tiviewer.move_down()

    # ctrl + Right（次の画像）
    def ctrl_right(self, event):
        if self.index == 1:
            self.liviewer.move_next()

    # ctrl + Left（前の画像）
    def ctrl_left(self, event):
        if self.index == 1:
            self.liviewer.move_prev()

    # ctrl + Down（次の画像）
    def ctrl_down(self, event):
        if self.index == 2:
            self.tiviewer.move_next()

    # ctrl + Up（前の画像）
    def ctrl_up(self, event):
        if self.index == 2:
            self.tiviewer.move_prev()

    # 1-9（指定位置）
    def key_one_zero(self, event, to):
        if self.index == 1:
            self.liviewer.move_to(to)
        elif self.index == 2:
            self.tiviewer.move_to(to)

    # space（再生/停止）
    def space(self, event):
        if self.index == 1 or self.index == 2:
            self.start_stop()

    # ctrl + space（逆再生）
    def ctrl_space(self, event):
        if self.index == 1 or self.index == 2:
            self.rev_start()

    # [（速さ-1）
    def lbracket(self, event):
        self.fps = self.fps-1 if 1 < self.fps else 1

    # ]（速さ+1）
    def rbracket(self, event):
        self.fps = self.fps+1 if self.fps < 50 else 50

    # ctrl + [（揺れ幅：横-1）
    def ctrl_lbracket(self, event):
        self.rngx = self.rngx-1 if 0 < self.rngx else 0

    # ctrl + ]（揺れ幅：横+1）
    def ctrl_rbracket(self, event):
        self.rngx = self.rngx+1 if self.rngx < 20 else 20

    # shift + [（揺れ幅：縦-1）
    def shift_lbracket(self, event):
        self.rngy = self.rngy-1 if 0 < self.rngy else 0

    # shift + ]（揺れ幅：縦+1）
    def shift_rbracket(self, event):
        self.rngy = self.rngy+1 if self.rngy < 20 else 20
    
    # ctrl + Q（終了）
    def ctrl_q(self, event):
        self.on_closing()


    # ----------------------# 基礎メソッド #----------------------#

    # フォルダ
    def read_show_dir(self, dirname):
        self.home.set_index(0)
        cv2imgs = []
        files = os.listdir(dirname)
        for f in files:
            flag = False
            for e in IMAGE_EXTENSIONS:
                if os.path.splitext(f)[1] == e[1]:
                    flag = True
                    break
            if flag:
                filename = dirname + "/" + f
                cv2img = cv2.imread(filename)
                cv2imgs.append(cv2img)
        label = "フォルダ名：" + dirname
        if self.home.mode.get() == 1:
            if self.index == 0:
                self.set_index(1)
            self.liviewer.show_images(cv2imgs, label)
        elif self.home.mode.get() == 2:
            if self.index == 0:
                self.set_index(2)
            self.tiviewer.show_images(cv2imgs, label)

    # 動画
    def read_show_video(self, fullpath):
        self.home.set_index(1)
        cv2imgs = self.convert_video(fullpath)
        label = "ファイル名：" + fullpath
        if self.home.mode.get() == 1:
            if self.index == 0:
                self.set_index(1)
            self.liviewer.show_images(cv2imgs, label)
        elif self.home.mode.get() == 2:
            if self.index == 0:
                self.set_index(2)
            self.tiviewer.show_images(cv2imgs, label)
    
    # 画像
    def read_show_file(self, filename):
        self.home.set_index(2)
        cv2img = cv2.imread(filename)
        label = "ファイル名：" + filename
        if self.home.mode.get() == 1:
            if self.index == 0:
                self.set_index(1)
            self.liviewer.show_image(cv2img, label)
        elif self.home.mode.get() == 2:
            if self.index == 0:
                self.set_index(2)
            self.tiviewer.show_image(cv2img, label)

    # 動画変換
    def convert_video(self, fullpath):
        cv2imgs = []
        video = cv2.VideoCapture(fullpath)
        r = round(video.get(cv2.CAP_PROP_FPS)/10)
        num = 0
        cnt = 0
        while True:
            ret, frame = video.read()
            if ret and cnt%r==0:
                cv2imgs.append(frame)
                num += 1
                cnt += 1
            elif ret:
                cnt += 1
            else:
                break
        video.release()
        return cv2imgs

    # 再生
    def playback(self):
        if self.index == 1:
            if self.liviewer.scrollx.get()[1]==1.0:
                self.nowplay = False
                self.after_cancel(self.id)
            else:
                try:
                    self.liviewer.move_next(rngx=self.rngx, rngy=self.rngy)
                except:
                    pass
                finally:
                    self.id = self.after(round(1000/self.fps), self.playback)
        elif self.index == 2:
            if self.tiviewer.scrolly.get()[1]==1.0:
                self.nowplay = False
                self.after_cancel(self.id)
            else:
                try:
                    self.tiviewer.move_next(rngx=self.rngx, rngy=self.rngy)
                except:
                    pass
                finally:
                    self.id = self.after(round(1000/self.fps), self.playback)

    # 逆再生
    def rev_playback(self):
        if self.index == 1:
            if self.liviewer.scrollx.get()[0] == 0.0:
                self.nowplay = False
                self.after_cancel(self.id)
            else:
                try:
                    self.liviewer.move_prev(rngx=self.rngx, rngy=self.rngy)
                except:
                    pass
                finally:
                    self.id = self.after(round(1000/self.fps), self.rev_playback)
        elif self.index == 2:
            if self.tiviewer.scrolly.get()[0] == 0.0:
                self.nowplay = False
                self.after_cancel(self.id)
            else:
                try:
                    self.tiviewer.move_prev(rngx=self.rngx, rngy=self.rngy)
                except:
                    pass
                finally:
                    self.id = self.after(round(1000/self.fps), self.rev_playback)

    # 終了処理
    def on_closing(self):
        self.home.write_csv()
        self.destroy()


######################### Setting class ########################
class Setting(tk.Toplevel):
    def __init__(self, master=None):
        self.master = master
        super().__init__(master=master)
        self.title("再生設定")
        self.geometry("330x230")
        self.resizable(0,0)
        self.grab_set()
        self.bind("<Return>", lambda e: self.push_ok())
        self.frame = tk.Frame(self)
        self.var1 = tk.IntVar()
        self.var2 = tk.IntVar()
        self.var3 = tk.IntVar()
        self.var1.set(self.master.fps)
        self.var2.set(self.master.rngx)
        self.var3.set(self.master.rngy)
        self.label1 = tk.Label(self.frame,text="速さ (fps)")
        self.scale1 = tk.Scale(self.frame, from_=1, to=50, orient=tk.HORIZONTAL, variable=self.var1)
        self.label2 = tk.Label(self.frame,text="揺れ幅：横 (%)")
        self.scale2 = tk.Scale(self.frame, from_=0, to=20, orient=tk.HORIZONTAL, variable=self.var2)
        self.label3 = tk.Label(self.frame,text="揺れ幅：縦 (%)")
        self.scale3 = tk.Scale(self.frame, from_=0, to=20, orient=tk.HORIZONTAL, variable=self.var3)
        self.button = tk.Button(self.frame, text="OK", width=10, command=self.push_ok, bg="gray85", relief=tk.FLAT)
        self.label1.grid(row=0, column=0, sticky=tk.S, ipady=5)
        self.scale1.grid(row=0, column=1, sticky=tk.EW, pady=5)
        self.label2.grid(row=1, column=0, sticky=tk.S, ipady=5)
        self.scale2.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.label3.grid(row=2, column=0, sticky=tk.S, ipady=5)
        self.scale3.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.button.grid(row=3, column=0, columnspan=2, pady=20)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        self.frame.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
    # button（OK）
    def push_ok(self):
        self.master.fps = self.var1.get()
        self.master.rngx = self.var2.get()
        self.master.rngy = self.var3.get()
        self.destroy()


if __name__ == "__main__":
    main = Main()
    main.mainloop()
