import render

import tkinter as tk
from tkinter import *
import ttkbootstrap as ttk
from tkinter import filedialog, scrolledtext
import ctypes
import os
import re

# WindowsでGUIの解像度が低くなるため、これを設定して回避する
ctypes.windll.shcore.SetProcessDpiAwareness(1)


class XScrollableFrame(ttk.Frame):
    """
    スクロールできるようにCanvasを使用したFrame
    """
    def __init__(self, parent):
        super().__init__(parent)

        main_frame = ttk.Frame(parent)
        main_frame.grid(row=1, column=0, sticky=NSEW, padx=10, pady=10)
        main_frame.grid_columnconfigure([0, ], weight=1)
        main_frame.grid_rowconfigure([0, 1], weight=1)

        self.canvas = ttk.Canvas(main_frame)
        self.canvas["height"] = 150

        self.canvas.grid(row=0, column=0, sticky=EW)

        xscrollbar = Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        xscrollbar.grid(row=1, column=0, sticky=EW)

        yscrollbar = Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        yscrollbar.grid(row=0, column=1, sticky=NS)

        self.canvas.configure(xscrollcommand=xscrollbar.set)
        self.canvas.configure(yscrollcommand=yscrollbar.set)
        self.canvas.bind('<Configure>', self.update)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

    def update(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class Window:
    """
    GUIアプリケーションのメインウィンドウを表すクラス。
    このクラスはウィンドウ全体のレイアウトや、各種操作のバインドを担当します。
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root["bg"] = "blue"
        self.root.geometry("800x800")
        self.root.grid_columnconfigure([0, ], weight=1)
        self.root.grid_rowconfigure([0, 1, 2], weight=1)

        self.template_frame = Template(self.root, (0, 0))

        self.x_scrollable_frame = XScrollableFrame(self.root)
        self.user_entries_frame = UserEntries(self.x_scrollable_frame)

        self.text_frame = TextDisplayWindow(self.root, (2, 0))

        self.template_frame.set_render_command(self.render)

        self.root.bind("<<ComboboxSelected>>", self.drive_combobox_event)
        self.root.bind("<Configure>", self.update_x_scrollable_frame)

    def drive_combobox_event(self, event=None):
        """
        コンボボックスでテンプレートファイルが選択されたときの処理。

        選択されたテンプレートファイルに含まれる変数を取得し、
        入力欄を動的に作成、配置します。

        Parameters
        ----------
        event : tkinter.Event, optional
            コンボボックスが選択された際に発生するイベントオブジェクト。デフォルトはNone。

        Returns
        -------
        None
        """
        template_dir = self.template_frame.template_dir.get()
        combobox_value = event.widget.get()
        template_file_path = os.path.join(template_dir, combobox_value)

        variables = self.template_frame.get_variables_in_template(template_file_path)
        self.user_entries_frame.delete_entries()
        self.user_entries_frame.create_entries(variables)
        self.user_entries_frame.grid_entries()

    def render(self):
        """
        ユーザーの入力に基づきテンプレートをレンダリングし、結果をテキストエリアに表示します。

        Parameters
        ----------

        Returns
        -------
        None
        """
        contexts = self.user_entries_frame.get_entries_data()

        template_file_name = self.template_frame.select_template_file_combobox.get()
        tmp = []
        for context in contexts:
            tmp.append(render.get_render_text(template_file_name, context))

        self.text_frame.update("\n----\n".join(tmp))

    def update_x_scrollable_frame(self, event=None):
        """
        ウィンドウのサイズ変更に伴ってスクロールフレームの表示領域を更新します。

        Parameters
        ----------
        event : tkinter.Event, optional
            ウィンドウサイズ変更時に発生するイベントオブジェクト。デフォルトはNone。

        Returns
        -------
        None
        """
        self.x_scrollable_frame.update()


class Template:
    """
    テンプレート関連の処理を行うクラス
    """
    def __init__(self, parent: tk.Tk, grid: tuple):
        self.parent = parent

        frame = ttk.Frame(self.parent)
        frame["width"] = 100
        frame.grid(row=grid[0], column=grid[1], sticky=NSEW, padx=10, pady=10)
        frame.grid_columnconfigure([0, 1, 2], weight=1)
        frame.grid_rowconfigure([0, 1], weight=1)

        self.template_dir = tk.StringVar(value="テンプレートディレクトリを選択してください")

        template_dir_label = ttk.Label(frame, wraplength=300)
        template_dir_label["textvariable"] = self.template_dir
        template_dir_label.grid(row=0, column=1, sticky=EW)

        read_button = ttk.Button(frame)
        read_button.grid(row=0, column=0)
        read_button["text"] = "選択"
        read_button["command"] = self.get_template_directory

        self.select_template_file_combobox = ttk.Combobox(frame)
        self.select_template_file_combobox.grid(row=0, column=2, sticky=EW)

        self.render_button = ttk.Button(frame)
        self.render_button.grid(row=1, column=0, columnspan=3, pady=10, sticky=EW)
        self.render_button["text"] = "レンダリング"

    def set_render_command(self, command_func):
        self.render_button["command"] = command_func

    def get_template_directory(self):
        """
        ファイルシステムに保存されているテンプレートファイルを読み込む

        Returns
        -------
        None
        """
        template_dir = filedialog.askdirectory(title="テンプレート保管ディレクトリ")
        self.template_dir.set(template_dir)
        self.set_template_file_combobox(template_dir)

    def set_template_file_combobox(self, template_dir: str) -> None:
        """
        コンボボックスにテンプレートファイルを設定する関数

        Parameters
        ----------
        template_dir: str

        Returns
        -------
        None

        """
        if template_dir == "":
            self.select_template_file_combobox["values"] = []
        else:
            self.select_template_file_combobox["values"] = self.get_template_file(template_dir)

    @staticmethod
    def get_template_file(template_dir_path: str) -> tuple:
        """
        テンプレートディレクトリからテンプレートファイル一覧を取得する関数

        Parameters
        ----------
        template_dir_path: str

        Returns
        --------
        tuple
        """
        template_files = []
        for dir_entry in os.scandir(template_dir_path):
            if dir_entry.is_file():
                template_files.append(dir_entry.name)

        return tuple(template_files)

    @staticmethod
    def get_variables_in_template(template_file_path: str) -> tuple:
        """
        テンプレートファイルに記載されている変数の一覧を取得する

        Parameters
        ----------
        template_file_path: str
            テンプレートファイルパス

        Returns
        -------
        tuple
        """
        with open(template_file_path, "r", encoding="utf-8") as f:
            variables = re.findall(r"\{\{\s?([^{}\s]*)\s?}}", f.read())

        return tuple(variables)


class UserEntry:
    """
    ユーザーが入力するウィジェットを表すクラス
    """
    def __init__(self, name: str, parent: tk.Frame):
        self.name = name
        self.frame = ttk.Frame(parent)
        self.entry = ttk.Entry(self.frame)
        self.label = ttk.Label(self.frame, text=name)

    def get(self) -> str:
        return self.entry.get()

    def grid(self, row: int, column: int):
        self.frame.grid(row=row, column=column, sticky=NSEW, pady=10)
        self.label.grid(row=0, column=0, padx=10)
        self.entry.grid(row=1, column=0, padx=10)

    def destroy(self):
        self.frame.destroy()
        self.label.destroy()
        self.entry.destroy()


class UserEntries:
    """
    UserEntryクラスをグループ化しているクラス
    """
    def __init__(self, parent: XScrollableFrame):
        self.inner_frame = parent.inner_frame
        self.inner_frame["pady"] = 10
        self.entries: dict[int: UserEntry] = {}
        self.buttons: dict[int: [Button, Button]] = {}
        self.row = 0

    def create_entries(self, entry_names: tuple):
        """
        1つ以上のエントリーを作成する関数
        Parameters
        ----------
        entry_names: tuple
            エントリーの名前

        Returns
        -------
        None

        """
        self.entries[self.row] = []

        if entry_names == ():
            return None

        for name in entry_names:
            self.entries[self.row].append(UserEntry(name, self.inner_frame))

        button_index = self.row
        plus_b = ttk.Button(self.inner_frame, text="+", width=2, command=self.add_entry)
        minus_b = ttk.Button(self.inner_frame, text="-", width=2, command=lambda: self.delete_entry(button_index))
        self.buttons[self.row] = [plus_b, minus_b]

    def add_entry(self, event=None):
        """
        エントリーを追加するメソッド

        Parameters
        ----------
        event:
            Tkinterのイベント

        Returns
        -------
        None
        """
        self.row += 1
        entry_names = tuple([entry.name for entry in self.entries[0]])

        self.create_entries(entry_names)
        self.grid_entries()

    def grid_entries(self):
        for i, entry in enumerate(self.entries[self.row]):
            entry.grid(row=self.row, column=i)

        if len(self.buttons) == 0:
            return

        for i, b in enumerate(self.buttons[self.row]):
            b.grid(row=self.row, column=len(self.entries[self.row]) + i, padx=5)

    def delete_entry(self, row):
        """
        指定されたエントリーを削除するメソッド

        Parameters
        ----------
        row: int
            ボタンを配置した行数

        Returns
        -------
        None
        """
        if self.row == 0:
            return

        for e in self.entries[row]:
            e.destroy()

        del self.entries[row]

        for b in self.buttons[row]:
            b.destroy()

        del self.buttons[row]

        self.row -= 1

    def delete_entries(self):
        for row in self.entries.keys():
            for entry in self.entries[row]:
                entry.destroy()

        for row in self.buttons.keys():
            for b in self.buttons[row]:
                b.destroy()

        self.row = 0
        self.entries = {}
        self.buttons = {}

    def get_entries_data(self) -> list:
        tmp = []
        for row in self.entries.keys():
            entries_data = {}
            for entry in self.entries[row]:
                entries_data[entry.name] = entry.get()
            tmp.append(entries_data)

        return tmp


class TextDisplayWindow:
    """
    テンプレートから生成されるテキストを表示するクラス
    """
    def __init__(self, parent, grid: tuple):
        self.frame = ttk.Frame(parent)

        self.text = scrolledtext.ScrolledText(self.frame)
        self.text["height"] = 10

        self.grid(row=grid[0], column=grid[1])

    def grid(self, row, column):
        self.frame.grid(row=row, column=column, sticky=NSEW)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.text.grid(row=0, column=0, sticky=NSEW)
        self.text.grid_columnconfigure(0, weight=1)

    def update(self, text: str):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
