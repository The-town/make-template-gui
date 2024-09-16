import render

import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog, scrolledtext
import ctypes
import os
import re

# WindowsでGUIの解像度が低くなるため、これを設定して回避する
ctypes.windll.shcore.SetProcessDpiAwareness(1)


class XScrollableFrame(tk.Frame):
    """
    スクロールできるようにCanvasを使用したFrame
    """
    def __init__(self, parent):
        super().__init__(parent)

        main_frame = tk.Frame(parent, padx=10, pady=10)
        main_frame.grid(row=1, column=0, sticky=NSEW)
        main_frame.grid_columnconfigure([0, ], weight=1)
        main_frame.grid_rowconfigure([0, 1], weight=1)

        self.canvas = tk.Canvas(main_frame)
        self.canvas["height"] = 150

        self.canvas.grid(row=0, column=0, sticky=EW)

        scrollbar = Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scrollbar.grid(row=1, column=0, sticky=EW)

        self.canvas.configure(xscrollcommand=scrollbar.set)
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
        context = self.user_entries_frame.get_entries_data()
        template_file_name = self.template_frame.select_template_file_combobox.get()

        self.text_frame.update(render.get_render_text(template_file_name, context))

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

        frame = tk.Frame(self.parent, padx=10, pady=10)
        frame["width"] = 100
        frame.grid(row=grid[0], column=grid[1], sticky=NSEW)
        frame.grid_columnconfigure([0, 1, 2], weight=1)
        frame.grid_rowconfigure([0, 1], weight=1)

        self.template_dir = tk.StringVar(value="テンプレートディレクトリを選択してください")

        template_dir_label = tk.Label(frame, wraplength=300)
        template_dir_label["textvariable"] = self.template_dir
        template_dir_label["padx"] = 10
        template_dir_label["pady"] = 10
        template_dir_label.grid(row=0, column=1, sticky=EW)

        read_button = tk.Button(frame)
        read_button.grid(row=0, column=0)
        read_button["text"] = "選択"
        read_button["height"] = 2
        read_button["command"] = self.get_template_directory

        self.select_template_file_combobox = Combobox(frame)
        self.select_template_file_combobox.grid(row=0, column=2, sticky=EW)

        self.render_button = tk.Button(frame)
        self.render_button.grid(row=1, column=0, columnspan=3, pady=10, sticky=EW)
        self.render_button["text"] = "レンダリング"
        self.render_button["height"] = 2

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
        self.frame = tk.Frame(parent, padx=10, pady=10)
        self.entry = tk.Entry(self.frame, highlightcolor="blue", highlightthickness=1)
        self.label = tk.Label(self.frame, text=name)

    def get(self) -> str:
        return self.entry.get()

    def grid(self, row: int, column: int):
        self.frame.grid(row=row, column=column, sticky=NSEW)
        self.label.grid(row=0, column=0)
        self.entry.grid(row=1, column=0)

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
        self.entries: list[UserEntry] = []

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
        for name in entry_names:
            self.entries.append(UserEntry(name, self.inner_frame))

    def grid_entries(self):
        for i, entry in enumerate(self.entries):
            entry.grid(row=0, column=i)

    def delete_entries(self):
        for entry in self.entries:
            entry.destroy()

        self.entries = []

    def get_entries_data(self) -> dict:
        entries_data = {}
        for entry in self.entries:
            entries_data[entry.name] = entry.get()

        return entries_data


class TextDisplayWindow:
    """
    テンプレートから生成されるテキストを表示するクラス
    """
    def __init__(self, parent, grid: tuple):
        self.frame = tk.Frame(parent, padx=10, pady=10)

        self.text = scrolledtext.ScrolledText(self.frame)

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
