import cv2
import numpy as np
from PIL import ImageTk, Image
import random
import tkinter as tk

OVERLAP = 500


################################################################
#----------------------# LiViewer class #----------------------#
################################################################
class LiViewer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.startdrawx = 0
        self.canvasw = 0
        self.canvash = 0
        self.mag = 1
        self.cv2imgs = [0]
        self.convertimgs = []
        self.ends = [0]
        self.label1str = tk.StringVar()
        self.label2str = tk.StringVar()
        self.posx = 0
        self.posy = 0

        self.create_widgets()
        self.resize()

    # ----------------------# widget #----------------------#
    def create_widgets(self):
        # 作成
        self.lframe = tk.Frame(self)
        self.label1 = tk.Label(self.lframe, textvariable=self.label1str)
        self.label2 = tk.Label(self.lframe, textvariable=self.label2str, bg="gray97")
        self.frame = tk.Frame(self)
        self.canvas = tk.Canvas(self.frame, bg="black", highlightthickness=0)
        self.canvas.bind("<Configure>", self.change_winsize)
        self.canvas.bind("<ButtonPress-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.scrolly = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scrollx = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.canvas.config(yscrollcommand=self.scrolly.set)
        self.canvas.config(xscrollcommand=self.scrollx.set)
        self.scrolly.config(command=self.canvas.yview)
        self.scrollx.config(command=self.canvas.xview)
        self.scrolly.bind("<B1-Motion>", self.scrollbar_motion)
        self.scrollx.bind("<B1-Motion>", self.scrollbar_motion)
        # 配置
        self.lframe.grid(row=0, column=0, sticky=tk.N+tk.EW)
        self.label1.grid(row=0, column=0, sticky=tk.W)
        self.label2.grid(row=0, column=1, sticky=tk.E, padx=4)
        self.frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        # 設定
        self.lframe.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)


    # ----------------------# イベント動作 #----------------------#

    # ウィンドウサイズ変更
    def change_winsize(self, event):
        if self.cv2imgs != [0]:
            self.create_view()

    # スクロールバードラッグ（移動）
    def scrollbar_motion(self, event):
        self.move()

    # クリック
    def click(self, event):
        if self.cv2imgs != [0]:
            self.canvas.scan_mark(event.x, event.y)

    # ドラッグ（移動）
    def drag(self, event):
        if self.cv2imgs != [0]:
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.move()


    # ----------------------# 移動 #----------------------#
    def move(self):
        if 300 < abs(self.posx-self.canvas.canvasx(0)) or 300 < abs(self.posy-self.canvas.canvasy(0)) or self.scrollx.get()[0]==0.0 or self.scrollx.get()[1]==1.0 or self.scrolly.get()[0]==0.0 or self.scrolly.get()[1]==1.0:
            self.create_view()

    # 右移動
    def move_right(self):
        self.canvas.xview_scroll(1, 'units')
        self.move()

    # 左移動
    def move_left(self):
        self.canvas.xview_scroll(-1, 'units')
        self.move()
    
    # 上移動
    def move_up(self):
        self.canvas.yview_scroll(-1, 'units')
        self.move()

    # 下移動
    def move_down(self):
        self.canvas.yview_scroll(1, 'units')
        self.move()
    
    # 次の画像
    def move_next(self, rngx=0, rngy=0):
        cnt = self.get_cp()
        if cnt < len(self.ends)-1:
            self.canvas.scan_mark(0,0)
            rndmx = 0 if rngx==0 else (random.randrange(0, rngx*20+1)-rngx*10)/1000
            rndmy = 0 if rngy==0 else (random.randrange(0, rngy*20+1)-rngy*10)/1000
            dragtox = -round(((self.ends[cnt+1]-self.ends[cnt])*self.mag)*(1+rndmx))
            dragtoy = -round(self.canvash*rndmy)
            self.canvas.scan_dragto(dragtox, dragtoy, gain=1)
            self.create_view()

    # 前の画像
    def move_prev(self, rngx=0, rngy=0):
        cnt = self.get_cp()
        if 0 < cnt:
            self.canvas.scan_mark(0,0)
            rndmx = 0 if rngx==0 else (random.randrange(0, rngx*20+1)-rngx*10)/1000
            rndmy = 0 if rngy==0 else (random.randrange(0, rngy*20+1)-rngy*10)/1000
            dragtox = round(((self.ends[cnt]-self.ends[cnt-1])*self.mag)*(1+rndmx))
            dragtoy = -round(self.canvash*rndmy)
            self.canvas.scan_dragto(dragtox, dragtoy, gain=1)
            self.create_view()

    # 現在地取得
    def get_cp(self):
        cnt = 0
        current_pos = self.canvas.canvasx(0)
        for i in range(len(self.ends)):
            if current_pos < self.ends[i]*self.mag:
                break
            cnt += 1
        return cnt

    # 指定位置
    def move_to(self, to):
        self.canvas.xview_moveto(to)
        self.move()


    # ----------------------# 基礎メソッド #----------------------#

    # リサイズ
    def resize(self, magx=None, mag=1):
        self.mag = mag if magx==None else self.mag*magx
        label2str = str(round(self.mag*100, 2)) + "%"
        self.label2str.set(label2str)
        if self.cv2imgs != [0]:
            offsetx = self.scrollx.get()[0]
            offsety = self.scrolly.get()[0]
            self.canvas.config(scrollregion=(-50, -50, self.canvasw*self.mag+50, self.canvash*self.mag+50))
            self.canvas.xview_moveto(offsetx) if offsetx!=0.0 else 0
            self.canvas.yview_moveto(offsety) if offsety!=0.0 else 0
            self.create_view()

    # キャンバスに合わせてリサイズ
    def resize_cs(self):
        mag = (self.canvas.winfo_height()-4) / self.canvash
        self.resize(mag=mag)
        self.canvas.yview_moveto(0)
        self.canvas.scan_mark(0, 0)
        self.canvas.scan_dragto(0, -50, gain=1)

    # 画像表示
    def show_image(self, cv2img, label=None):
        if label != None:
            self.label1str.set(label)
        self.load_image(cv2img)
        self.size_i()
        self.scroll_and_view()

    # 複数画像表示
    def show_images(self, cv2imgs, label=None):
        if label != None:
            self.label1str.set(label)
        for cv2img in cv2imgs:
            self.load_image(cv2img)
        self.size_i()
        self.scroll_and_view()

	# 画像入力
    def load_image(self, cv2img):
        self.cv2imgs.append(cv2img)
        h, w = cv2img.shape[:2]
        self.canvasw += w
        self.ends.append(self.canvasw)
        if self.canvash < h:
            self.canvash = h

    # 高さ合わせ
    def size_i(self):
        for i in range(1, len(self.ends)):
            s = self.canvash - self.cv2imgs[i].shape[0]
            if 2 <= s:
                if s%2 == 1:
                    s -= 1
                mgn = np.zeros((int(s/2), self.cv2imgs[i].shape[1], 3), np.uint8)
                src = [mgn, self.cv2imgs[i], mgn]
                self.cv2imgs[i] = cv2.vconcat(src)

    # 初期化
    def cleanup(self):
        self.startdrawx = 0
        self.canvash = 0
        self.canvasw = 0
        self.cv2imgs = [0]
        self.convertimgs = []
        self.ends = [0]
        label1str = ""
        self.label1str.set(label1str)
        self.resize()
        self.canvas.config(scrollregion=(0, 0, self.canvasw+25, self.canvash+25))

    # スクロールバー・キャンバス表示
    def scroll_and_view(self):
        if self.cv2imgs != [0]:
            self.canvas.config(scrollregion=(-50, -50, self.canvasw*self.mag+50, self.canvash*self.mag+50))
            self.create_view()

    # キャンバス表示
    def create_view(self):
        self.convertimgs = []
        self.startdrawx = self.canvas.canvasx(0)-OVERLAP
        left_limit = self.canvas.canvasx(0)-OVERLAP
        right_limit = self.canvas.canvasx(self.canvas.winfo_width())+OVERLAP
        for i in range(1, len(self.ends)):
            end0 = self.ends[i-1]*self.mag
            end1 = self.ends[i]*self.mag
            if end1 < left_limit:
                continue
            elif left_limit <= end1 < right_limit:
                if end0 < left_limit:
                    self.convert_draw(i, round(left_limit/self.mag-self.ends[i-1]), self.ends[i]-self.ends[i-1])
                else:
                    self.convert_draw(i, 0, self.ends[i]-self.ends[i-1])
            else:
                if end0 < left_limit:
                    self.convert_draw(i, round(left_limit/self.mag-self.ends[i-1]), round(right_limit/self.mag-self.ends[i-1]))
                elif left_limit <= end0 < right_limit:
                    self.convert_draw(i, 0, round(right_limit/self.mag-self.ends[i-1]))
                else:
                    break
        self.posx = self.canvas.canvasx(0)
        self.posy = self.canvas.canvasy(0)

    # キャンバス表示（後半）
    def convert_draw(self, i, sx, ex):
        top_limit = self.canvas.canvasy(0)-OVERLAP
        bottom_limit = self.canvas.canvasy(self.canvas.winfo_height())+OVERLAP
        sy = 0 if top_limit < 0 else round(top_limit/self.mag)
        ey = round(bottom_limit/self.mag) if bottom_limit < self.cv2imgs[i].shape[0]*self.mag else self.cv2imgs[i].shape[0]
        cutimg = cv2.resize(self.cv2imgs[i][sy:ey, sx:ex], dsize=None, fx=self.mag, fy=self.mag)
        convertimg = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(cutimg, cv2.COLOR_BGR2RGB)))
        self.convertimgs.append(convertimg)
        self.startdrawx = 2 if self.startdrawx<=2 else self.startdrawx
        startdrawy = 2 if top_limit<=2 else top_limit
        self.canvas.create_image(round(self.startdrawx), round(startdrawy), image=convertimg, anchor=tk.NW)
        self.startdrawx += cutimg.shape[1]


################################################################
#----------------------# TiViewer class #----------------------#
################################################################
class TiViewer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.startdrawy = 0
        self.canvasw = 0
        self.canvash = 0
        self.mag = 1
        self.cv2imgs = [0]
        self.convertimgs = []
        self.ends = [0]
        self.label1str = tk.StringVar()
        self.label2str = tk.StringVar()
        self.posx = 0
        self.posy = 0

        self.create_widgets()
        self.resize()

    # ----------------------# widget #----------------------#
    def create_widgets(self):
        # 作成
        self.lframe = tk.Frame(self)
        self.label1 = tk.Label(self.lframe, textvariable=self.label1str)
        self.label2 = tk.Label(self.lframe, textvariable=self.label2str, bg="gray97")
        self.frame = tk.Frame(self)
        self.canvas = tk.Canvas(self.frame, bg="black", highlightthickness=0)
        self.canvas.bind("<Configure>", self.change_winsize)
        self.canvas.bind("<ButtonPress-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.scrolly = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scrollx = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.canvas.config(yscrollcommand=self.scrolly.set)
        self.canvas.config(xscrollcommand=self.scrollx.set)
        self.scrolly.config(command=self.canvas.yview)
        self.scrollx.config(command=self.canvas.xview)
        self.scrolly.bind("<B1-Motion>", self.scrollbar_motion)
        self.scrollx.bind("<B1-Motion>", self.scrollbar_motion)
        # 配置
        self.lframe.grid(row=0, column=0, sticky=tk.N+tk.EW)
        self.label1.grid(row=0, column=0, sticky=tk.W)
        self.label2.grid(row=0, column=1, sticky=tk.E, padx=4)
        self.frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        # 設定
        self.lframe.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)


    # ----------------------# イベント動作 #----------------------#

    # ウィンドウサイズ変更
    def change_winsize(self, event):
        if self.cv2imgs != [0]:
            self.create_view()

    # スクロールバードラッグ（移動）
    def scrollbar_motion(self, event):
        self.move()

    # クリック
    def click(self, event):
        if self.cv2imgs != [0]:
            self.canvas.scan_mark(event.x, event.y)

    # ドラッグ（移動）
    def drag(self, event):
        if self.cv2imgs != [0]:
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.move()


    # ----------------------# 移動 #----------------------#
    def move(self):
        if 300 < abs(self.posx-self.canvas.canvasx(0)) or 300 < abs(self.posy-self.canvas.canvasy(0)) or self.scrollx.get()[0]==0.0 or self.scrollx.get()[1]==1.0 or self.scrolly.get()[0]==0.0 or self.scrolly.get()[1]==1.0:
            self.create_view()

    # 右移動
    def move_right(self):
        self.canvas.xview_scroll(1, 'units')
        self.move()

    # 左移動
    def move_left(self):
        self.canvas.xview_scroll(-1, 'units')
        self.move()
    
    # 上移動
    def move_up(self):
        self.canvas.yview_scroll(-1, 'units')
        self.move()

    # 下移動
    def move_down(self):
        self.canvas.yview_scroll(1, 'units')
        self.move()
    
    # 次の画像
    def move_next(self, rngx=0, rngy=0):
        cnt = self.get_cp()
        if cnt < len(self.ends)-1:
            self.canvas.scan_mark(0,0)
            rndmx = 0 if rngx==0 else (random.randrange(0, rngx*20+1)-rngx*10)/1000
            rndmy = 0 if rngy==0 else (random.randrange(0, rngy*20+1)-rngy*10)/1000
            dragtox = -round(self.canvasw*rndmx)
            dragtoy = -round(((self.ends[cnt+1]-self.ends[cnt])*self.mag)*(1+rndmy))
            self.canvas.scan_dragto(dragtox, dragtoy, gain=1)
            self.create_view()

    # 前の画像
    def move_prev(self, rngx=0, rngy=0):
        cnt = self.get_cp()
        if 0 < cnt:
            self.canvas.scan_mark(0,0)
            rndmx = 0 if rngx==0 else (random.randrange(0, rngx*20+1)-rngx*10)/1000
            rndmy = 0 if rngy==0 else (random.randrange(0, rngy*20+1)-rngy*10)/1000
            dragtox = -round(self.canvasw*rndmx)
            dragtoy = round(((self.ends[cnt]-self.ends[cnt-1])*self.mag)*(1+rndmy))
            self.canvas.scan_dragto(dragtox, dragtoy, gain=1)
            self.create_view()

    # 現在地取得
    def get_cp(self):
        cnt = 0
        current_pos = self.canvas.canvasy(0)
        for i in range(len(self.ends)):
            if current_pos < self.ends[i]*self.mag:
                break
            cnt += 1
        return cnt

    # 指定位置
    def move_to(self, to):
        self.canvas.yview_moveto(to)
        self.move()


    # ----------------------# 基礎メソッド #----------------------#

    # リサイズ
    def resize(self, magx=None, mag=1):
        self.mag = mag if magx==None else self.mag*magx
        label2str = str(round(self.mag*100, 2)) + "%"
        self.label2str.set(label2str)
        if self.cv2imgs != [0]:
            offsetx = self.scrollx.get()[0]
            offsety = self.scrolly.get()[0]
            self.canvas.config(scrollregion=(-50, -50, self.canvasw*self.mag+50, self.canvash*self.mag+50))
            self.canvas.xview_moveto(offsetx) if offsetx!=0.0 else 0
            self.canvas.yview_moveto(offsety) if offsety!=0.0 else 0
            self.create_view()

    # キャンバスに合わせてリサイズ
    def resize_cs(self):
        mag = (self.canvas.winfo_width() - 4) / self.canvasw
        self.resize(mag=mag)
        self.canvas.xview_moveto(0)
        self.canvas.scan_mark(0, 0)
        self.canvas.scan_dragto(-50, 0, gain=1)

    # 画像表示
    def show_image(self, cv2img, label=None):
        if label != None:
            self.label1str.set(label)
        self.load_image(cv2img)
        self.size_i()
        self.scroll_and_view()

    # 複数画像表示
    def show_images(self, cv2imgs, label=None):
        if label != None:
            self.label1str.set(label)
        for cv2img in cv2imgs:
            self.load_image(cv2img)
        self.size_i()
        self.scroll_and_view()

	# 画像入力
    def load_image(self, cv2img):
        self.cv2imgs.append(cv2img)
        h, w = cv2img.shape[:2]
        self.canvash += h
        self.ends.append(self.canvash)
        if self.canvasw < w:
            self.canvasw = w

    # 高さ合わせ
    def size_i(self):
        for i in range(1, len(self.ends)):
            s = self.canvasw - self.cv2imgs[i].shape[1]
            if 2 <= s:
                if s%2 == 1:
                    s -= 1
                mgn = np.zeros((self.cv2imgs[i].shape[0], int(s/2), 3), np.uint8)
                src = [mgn, self.cv2imgs[i], mgn]
                self.cv2imgs[i] = cv2.hconcat(src)

    # 初期化
    def cleanup(self):
        self.startdrawy = 0
        self.canvash = 0
        self.canvasw = 0
        self.cv2imgs = [0]
        self.convertimgs = []
        self.ends = [0]
        label1str = ""
        self.label1str.set(label1str)
        self.resize()
        self.canvas.config(scrollregion=(0, 0, self.canvasw+25, self.canvash+25))

    # スクロールバー・キャンバス表示
    def scroll_and_view(self):
        if self.cv2imgs != [0]:
            self.canvas.config(scrollregion=(-50, -50, self.canvasw*self.mag+50, self.canvash*self.mag+50))
            self.create_view()

    # キャンバス表示
    def create_view(self):
        self.convertimgs = []
        self.startdrawy = self.canvas.canvasy(0)-OVERLAP
        top_limit = self.canvas.canvasy(0)-OVERLAP
        bottom_limit = self.canvas.canvasy(self.canvas.winfo_height())+OVERLAP
        for i in range(1, len(self.ends)):
            end0 = self.ends[i-1]*self.mag
            end1 = self.ends[i]*self.mag
            if end1 < top_limit:
                continue
            elif top_limit <= end1 < bottom_limit:
                if end0 < top_limit:
                    self.convert_draw(i, round(top_limit/self.mag-self.ends[i-1]), self.ends[i]-self.ends[i-1])
                else:
                    self.convert_draw(i, 0, self.ends[i]-self.ends[i-1])
            else:
                if end0 < top_limit:
                    self.convert_draw(i, round(top_limit/self.mag-self.ends[i-1]), round(bottom_limit/self.mag-self.ends[i-1]))
                elif top_limit <= end0 < bottom_limit:
                    self.convert_draw(i, 0, round(bottom_limit/self.mag-self.ends[i-1]))
                else:
                    break
        self.posx = self.canvas.canvasx(0)
        self.posy = self.canvas.canvasy(0)

    # キャンバス表示（後半）
    def convert_draw(self, i, sy, ey):
        left_limit = self.canvas.canvasx(0)-OVERLAP
        right_limit = self.canvas.canvasx(self.canvas.winfo_width())+OVERLAP
        sx = 0 if left_limit < 0 else round(left_limit/self.mag)
        ex = round(right_limit/self.mag) if right_limit < self.cv2imgs[i].shape[1]*self.mag else self.cv2imgs[i].shape[1]
        cutimg = cv2.resize(self.cv2imgs[i][sy:ey, sx:ex], dsize=None, fx=self.mag, fy=self.mag)
        convertimg = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(cutimg, cv2.COLOR_BGR2RGB)))
        self.convertimgs.append(convertimg)
        startdrawx = 2 if left_limit<=2 else left_limit
        self.startdrawy = 2 if self.startdrawy<=2 else self.startdrawy
        self.canvas.create_image(round(startdrawx), round(self.startdrawy), image=convertimg, anchor=tk.NW)
        self.startdrawy += cutimg.shape[0]
