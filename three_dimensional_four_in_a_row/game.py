"""立体四目並べの可視化モジュール"""
from __future__ import annotations
import tkinter as tk
import tkinter.ttk as ttk

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .base import BallType, Board

matplotlib.use('Agg')


class BoardFrame(tk.Frame):
    """matplotlibを使用してボードの状態を可視化するフレームクラス
    """

    def __init__(self, master: Application, cnf={}, **kw) -> None:
        super().__init__(master, cnf, **kw)
        self._size = master.board_size
        fig = plt.figure(figsize=(1, 1))
        self._ax = fig.add_subplot(1, 1, 1, projection='3d')
        self._ax.view_init(elev=50, azim=330)
        self._canvas = FigureCanvasTkAgg(fig, master=self)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        self._canvas.get_tk_widget().bind('<Button-2>', lambda event: None)
        self._canvas.get_tk_widget().bind('<Button-3>', lambda event: None)

    def reset(self) -> None:
        """表示角度をリセットするメソッド
        """
        self._ax.view_init(elev=50, azim=330)

    def plot(self, show_reach_date: bool) -> None:
        """表示を更新するメソッド

        Args:
            show_reach_date (bool): リーチ情報を表示するかの真理値
        """
        cmap = plt.get_cmap('jet')
        self._ax.clear()
        self._ax.set_xlim([-0.5, self._size - 0.5])
        self._ax.set_ylim([-0.5, self._size - 0.5])
        self._ax.set_zlim([-0.5, self._size - 0.5])
        self._ax.set_xticks([i for i in range(self._size)])
        self._ax.set_yticks([i for i in range(self._size)])
        self._ax.set_zticks([])
        self._ax.set_xticklabels([f'{chr(ord("A") + i)}' for i in range(self._size)])
        self._ax.set_yticklabels([f'{i + 1}' for i in range(self._size)])
        for x, y, z in np.array([[x, y, z] for x in range(self._size) for y in range(self._size) for z in range(self._size)]):
            if self.master.board_data[x, y, z].value != -1:
                self._ax.scatter3D(x, y, z, s=np.min(self._ax.figure.get_size_inches()) ** 2 * 90, color=rgb2hex(cmap(self.master.color_code_per_player * (self.master.board_data[x, y, z].value + 1))), edgecolor='000')
            elif show_reach_date:
                for r in self.master.reach_data[x, y, z]:
                    if r.value != -1:
                        self._ax.scatter3D(x, y, z, s=np.min(self._ax.figure.get_size_inches()) ** 2 * 90, color=rgb2hex(cmap(self.master.color_code_per_player * (r.value + 1))), alpha=0.5, edgecolor='000')
        self._canvas.draw()


class Button(tk.Button):
    """X座標とY座標保持したボタンクラス
    """

    def __init__(self, master: ButtonFrame, x=0, y=0, cnf={}, **kw) -> None:
        super().__init__(master, cnf, **kw)
        self._x, self._y = x, y

    @property
    def position(self) -> tuple[int, int]:
        """ボタンが保持しているX座標とY座標を取得するプロパティ

        Returns:
            tuple[int, int]: X座標とY座標
        """
        return self._x, self._y


class ButtonFrame(tk.Frame):
    """操作用のボタンを配置したフレームクラス
    """

    def __init__(self, master: Application, cnf={}, **kw) -> None:
        super().__init__(master, cnf, **kw)
        self.master = master
        for x in range(master.board_size):
            self.rowconfigure(x, weight=2)
            self.columnconfigure(x, weight=1)
            for y in range(master.board_size):
                button = Button(self, x, y, text=f'{chr(ord("A") + x)}{y + 1}')
                button.grid(row=x, column=y, sticky=(tk.N, tk.S, tk.W, tk.E))
                button.bind('<Button-1>', self._click_event)

    def _click_event(self, event: tk.Event) -> None:
        x, y = event.widget.position
        self.master.put_event(x, y)


class TopFrame(tk.Frame):
    """現在のプレーヤーを表示するラベルとリーチ情報を表示するかのチェックボックスを配置したフレームクラス
    """

    def __init__(self, master: Application, cnf={}, **kw) -> None:
        super().__init__(master, cnf, **kw)
        self._label = tk.Label(self, relief=tk.SOLID, bd=1)
        button = tk.Button(self, text='リセット')
        self._boolean_var = tk.BooleanVar()
        self._boolean_var.set(master.show_reach_date)
        checkbutton = tk.Checkbutton(self, variable=self._boolean_var, text='リーチ位置を表示', relief=tk.SOLID, bd=1, command=self._check_event)
        label = tk.Label(self, text='ランダム', relief=tk.SOLID, bd=1)
        self._combobox = ttk.Combobox(self, state='readonly', values=['無し', 'プレーヤー1', 'プレーヤー2'])
        self._combobox.set('無し')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self._label.grid(row=0, column=0, columnspan=4, sticky=(tk.N, tk.S, tk.W, tk.E))
        button.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        checkbutton.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        label.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        self._combobox.grid(row=1, column=3, sticky=(tk.N, tk.S, tk.W, tk.E))
        button.bind('<Button-1>', lambda event: self.master.reset_event())
        self._combobox.bind('<<ComboboxSelected>>', lambda event: self.master.random_event())

    def change(self, player: BallType) -> None:
        """プレーヤーを表示するラベルを変更するメソッド

        Args:
            player (BallType): 変更するプレーヤー
        """
        cmap = plt.get_cmap('jet')
        if player == BallType.PLAYER1:
            self._label['text'] = 'プレーヤー1'
        elif player == BallType.PLAYER2:
            self._label['text'] = 'プレーヤー2'
        else:
            self._label['text'] = player.name
        self._label['bg'] = rgb2hex(cmap(self.master.color_code_per_player * (player.value + 1)))

    def _check_event(self) -> None:
        self.master.check_event(self._boolean_var.get())
    
    @property
    def random_player(self) -> BallType:
        a = self._combobox.get()
        if self._combobox.get() == 'プレーヤー1':
            return BallType.PLAYER1
        elif self._combobox.get() == 'プレーヤー2':
            return BallType.PLAYER2
        else:
            return BallType.INVALID


class Application(tk.Tk, Board):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        Board.__init__(self)
        self.geometry('300x300')
        self.title('立体四目並べ')
        self._width, self._height = 0, 0
        self._isend, self._show_reach_date = False, True
        self._top_frame = TopFrame(self)
        self._board_frame = BoardFrame(self)
        self._button_frame = ButtonFrame(self, relief=tk.SOLID, bd=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self._top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        self._board_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        self._button_frame.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.bind('<Configure>', self._callback)
        self.plot()

    @property
    def show_reach_date(self) -> bool:
        """リーチ情報を表示するかの真理値を取得するプロパティ

        Returns:
            bool: リーチ情報を表示するかの真理値
        """
        return self._show_reach_date

    def _callback(self, event: tk.Event) -> None:
        if event.widget == self and (event.width != self._width or event.height != self._height):
            self._width, self._height = event.width, event.height
            self.after(5, self._board_frame.plot, self.show_reach_date)

    def put_event(self, x: int, y: int) -> None:
        """ボードにボールを置くメソッド

        Args:
            x (int): X座標
            y (int): Y座標
        """
        if self.winner == BallType.INVALID:
            if self._top_frame.random_player == BallType.PLAYER1:
                if self.player == BallType.PLAYER2:
                    if self.board_put(x, y):
                        self.plot()
                    if self.winner == BallType.INVALID:
                        self.random_put()
                        self.plot()
            elif self._top_frame.random_player == BallType.PLAYER2:
                if self.player == BallType.PLAYER1:
                    if self.board_put(x, y):
                        self.plot()
                    if self.winner == BallType.INVALID:
                        self.random_put()
                        self.plot()
            else:
                if self.board_put(x, y):
                    self.plot()
        if self.winner != BallType.INVALID and not self._isend:
            self.after(5, self._end, self.winner)

    def reset_event(self) -> None:
        """リセットメソッド
        """
        self._isend, self._show_reach_date = False, True
        self.board_reset()
        self._board_frame.reset()
        self.plot()
    
    def random_event(self):
        """コンボボックスでランダムプレーヤーが変更すれた際に設置するメソッド
        """
        if self.player == self._top_frame.random_player:
            self.random_put()
            self.plot()

    def _end(self, winner: BallType) -> None:
        self._isend = True
        self.write_log()
        if tk.messagebox.askyesno('勝者', f'{winner.name}が勝利しました。\nリセットしますか？'):
            self.reset_event()

    def check_event(self, check: bool) -> None:
        """リーチ情報を表示するかのチェックボックスの真理値を受け取りボードの表示を変更するメソッド

        Args:
            check (_type_): リーチ情報を表示するかの真理値
        """
        self._show_reach_date = check
        self._board_frame.plot(self.show_reach_date)

    def plot(self) -> None:
        """表示を更新するメソッド
        """
        if self.winner == BallType.INVALID:
            self._top_frame.change(self.player)
        self._board_frame.plot(self.show_reach_date)
