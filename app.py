import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import shutil
from datetime import datetime
import uuid

# 导入主程序文件
from main import ArchiveManagementSystem

# 程序入口点
if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用程序实例
    app = ArchiveManagementSystem(root)
    
    # 运行主循环
    root.mainloop()