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

# 尝试导入tkcalendar，如果不存在则提供一个简单的替代方案
try:
    from tkcalendar import Calendar
    ttk.Calendar = Calendar
except ImportError:
    # 如果没有tkcalendar库，创建一个简单的日期选择替代方案
    class SimpleCalendar(ttk.Frame):
        def __init__(self, master=None, selectmode='day', date_pattern='yyyy-mm-dd', **kw):
            super().__init__(master, **kw)
            self.selectmode = selectmode
            self.date_pattern = date_pattern
            self._selected_date = datetime.now().strftime("%Y-%m-%d")
            
            # 创建年月日选择框
            frame = ttk.Frame(self)
            frame.pack(padx=10, pady=10)
            
            # 年份选择
            ttk.Label(frame, text="年:").grid(row=0, column=0, padx=5, pady=5)
            current_year = datetime.now().year
            years = list(range(current_year-100, current_year+1))
            self.year_var = tk.StringVar(value=str(current_year))
            self.year_cb = ttk.Combobox(frame, textvariable=self.year_var, values=years, width=6)
            self.year_cb.grid(row=0, column=1, padx=5, pady=5)
            
            # 月份选择
            ttk.Label(frame, text="月:").grid(row=1, column=0, padx=5, pady=5)
            months = list(range(1, 13))
            self.month_var = tk.StringVar(value=str(datetime.now().month))
            self.month_cb = ttk.Combobox(frame, textvariable=self.month_var, values=months, width=6)
            self.month_cb.grid(row=1, column=1, padx=5, pady=5)
            
            # 日期选择
            ttk.Label(frame, text="日:").grid(row=2, column=0, padx=5, pady=5)
            days = list(range(1, 32))
            self.day_var = tk.StringVar(value=str(datetime.now().day))
            self.day_cb = ttk.Combobox(frame, textvariable=self.day_var, values=days, width=6)
            self.day_cb.grid(row=2, column=1, padx=5, pady=5)
        
        def get_date(self):
            """获取选择的日期"""
            year = self.year_var.get()
            month = self.month_var.get().zfill(2)
            day = self.day_var.get().zfill(2)
            return f"{year}-{month}-{day}"
        
        def selection_set(self, date_str):
            """设置日期"""
            try:
                date_parts = date_str.split('-')
                if len(date_parts) >= 3:
                    self.year_var.set(date_parts[0])
                    self.month_var.set(str(int(date_parts[1])))
                    self.day_var.set(str(int(date_parts[2])))
            except:
                pass
    
    # 使用简单日历替代
    ttk.Calendar = SimpleCalendar

# 创建应用程序主类
class ArchiveManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("教师档案管理系统")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # 创建数据库和文件夹
        self.setup_database()
        self.setup_folders()
        
        # 创建主界面
        self.create_main_interface()
    
    def setup_database(self):
        # 连接到SQLite数据库
        self.conn = sqlite3.connect('teacher_archive.db')
        self.cursor = self.conn.cursor()
        
        # 创建教师基本信息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_info (
            teacher_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            gender TEXT,
            birth_date TEXT,
            ethnicity TEXT,
            hometown TEXT,
            id_number TEXT UNIQUE,
            photo_path TEXT,
            party_join_date TEXT,
            work_start_date TEXT,
            health_status TEXT,
            teaching_subject TEXT,
            current_position TEXT,
            create_time TEXT,
            update_time TEXT
        )
        ''')
        
        # 创建职称信息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS title_history (
            record_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            title TEXT,
            obtain_date TEXT,
            post TEXT,
            appointment_date TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建教育背景表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            record_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            edu_type TEXT,
            degree TEXT,
            institution TEXT,
            obtain_date TEXT,
            scan_file_path TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建工作简历表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_experience (
            record_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            start_date TEXT,
            end_date TEXT,
            organization TEXT,
            position TEXT,
            description TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建教学工作情况表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS teaching_records (
            record_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            academic_year TEXT,
            semester TEXT,
            subject TEXT,
            classes TEXT,
            student_count INTEGER,
            weekly_hours INTEGER,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建教育工作情况表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS education_work (
            record_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            academic_year TEXT,
            semester TEXT,
            work_type TEXT,
            description TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建综合表彰表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS awards (
            award_id TEXT PRIMARY KEY,
            award_name TEXT,
            award_level TEXT,
            award_unit TEXT,
            award_date TEXT,
            award_type TEXT,
            create_time TEXT,
            update_time TEXT
        )
        ''')
        
        # 创建获奖人员关联表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS award_recipients (
            relation_id TEXT PRIMARY KEY,
            award_id TEXT,
            teacher_id TEXT,
            rank INTEGER,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (award_id) REFERENCES awards (award_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建公开课管理表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_lessons (
            lesson_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            lesson_name TEXT,
            lesson_scope TEXT,
            lesson_date TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建论文管理表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            paper_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            paper_title TEXT,
            journal_name TEXT,
            paper_level TEXT,
            publish_date TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建课题管理表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_projects (
            project_id TEXT PRIMARY KEY,
            project_name TEXT,
            project_level TEXT,
            completion_date TEXT,
            create_time TEXT,
            update_time TEXT
        )
        ''')
        
        # 创建课题成员表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_members (
            relation_id TEXT PRIMARY KEY,
            project_id TEXT,
            teacher_id TEXT,
            is_leader BOOLEAN,
            member_rank INTEGER,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (project_id) REFERENCES research_projects (project_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建学生竞赛辅导表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_competitions (
            competition_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            competition_name TEXT,
            winner_count INTEGER,
            award_level TEXT,
            competition_date TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建青蓝工程表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentoring (
            mentoring_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            apprentice_id TEXT,
            start_date TEXT,
            end_date TEXT,
            achievements TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id),
            FOREIGN KEY (apprentice_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建专业引领表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS professional_leadership (
            leadership_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            leadership_type TEXT,
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        # 创建考试成绩表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_results (
            result_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            exam_name TEXT,
            exam_date TEXT,
            rank INTEGER,
            class_average REAL,
            create_time TEXT,
            update_time TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info (teacher_id)
        )
        ''')
        
        self.conn.commit()
    
    def setup_folders(self):
        # 创建存储照片和扫描件的文件夹
        os.makedirs('photos', exist_ok=True)
        os.makedirs('scans', exist_ok=True)
    
    def create_main_interface(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧菜单栏
        self.menu_frame = ttk.Frame(self.main_frame, width=200)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 创建右侧内容区域
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 添加菜单按钮
        ttk.Label(self.menu_frame, text="功能菜单", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 基本信息管理菜单
        self.basic_info_btn = ttk.Button(self.menu_frame, text="基本信息管理", width=20, command=self.show_basic_info_management)
        self.basic_info_btn.pack(pady=5)
        
        # 业务情况管理菜单
        self.business_info_btn = ttk.Button(self.menu_frame, text="业务情况管理", width=20, command=self.show_business_management)
        self.business_info_btn.pack(pady=5)
        
        # 数据导入导出菜单
        self.data_io_btn = ttk.Button(self.menu_frame, text="数据导入导出", width=20, command=self.show_data_io)
        self.data_io_btn.pack(pady=5)
        
        # 综合查询功能菜单
        self.query_btn = ttk.Button(self.menu_frame, text="综合查询功能", width=20, command=self.show_query)
        self.query_btn.pack(pady=5)
        
        # 统计分析菜单
        self.stats_btn = ttk.Button(self.menu_frame, text="统计分析", width=20, command=self.show_statistics)
        self.stats_btn.pack(pady=5)
        
        # 默认显示基本信息管理页面
        self.show_basic_info_management()
    
    def clear_content_frame(self):
        # 清除内容区域的所有小部件
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    #====================== 基本信息管理 ======================
    def show_basic_info_management(self):
        self.clear_content_frame()
        
        # 创建基本信息管理页面
        ttk.Label(self.content_frame, text="基本信息管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建子功能按钮框架
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        # 添加子功能按钮
        ttk.Button(btn_frame, text="档案录入", command=self.show_archive_entry).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="档案修改", command=self.show_archive_edit).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="照片/扫描件管理", command=self.show_document_management).grid(row=0, column=2, padx=10, pady=5)
        
        # 显示教师列表
        self.show_teacher_list()
    
    def show_teacher_list(self):
        # 创建教师列表框架
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建搜索框架
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="搜索教师:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", command=lambda: self.search_teacher(search_entry.get())).pack(side=tk.LEFT, padx=5)
        
        # 创建教师列表
        columns = ("教师ID", "姓名", "性别", "出生年月", "民族", "籍贯", "身份证号", "任教学科")
        self.teacher_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.teacher_tree.heading(col, text=col)
            self.teacher_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.teacher_tree.yview)
        self.teacher_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teacher_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.teacher_tree.bind("<Double-1>", self.on_teacher_selected)
        
        # 加载教师数据
        self.load_teacher_data()
    
    def load_teacher_data(self):
        # 清除现有数据
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)
        
        # 从数据库加载教师数据
        self.cursor.execute("SELECT teacher_id, name, gender, birth_date, ethnicity, hometown, id_number, teaching_subject FROM teacher_info")
        teachers = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for teacher in teachers:
            self.teacher_tree.insert("", tk.END, values=teacher)
    
    def search_teacher(self, keyword):
        # 清除现有数据
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)
        
        # 搜索教师
        self.cursor.execute("""
        SELECT teacher_id, name, gender, birth_date, ethnicity, hometown, id_number, teaching_subject 
        FROM teacher_info 
        WHERE name LIKE ? OR id_number LIKE ?
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        teachers = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for teacher in teachers:
            self.teacher_tree.insert("", tk.END, values=teacher)
    
    def on_teacher_selected(self, event):
        # 获取选中的教师ID
        selected_item = self.teacher_tree.selection()[0]
        teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        
        # 显示教师详细信息
        self.show_teacher_details(teacher_id)
    
    def show_teacher_details(self, teacher_id):
        # 创建新窗口显示教师详细信息
        details_window = tk.Toplevel(self.root)
        details_window.title("教师详细信息")
        details_window.geometry("800x600")
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(details_window)
        
        # 创建基本信息选项卡
        basic_tab = ttk.Frame(tab_control)
        tab_control.add(basic_tab, text="基本信息")
        
        # 创建职称信息选项卡
        title_tab = ttk.Frame(tab_control)
        tab_control.add(title_tab, text="职称信息")
        
        # 创建教育背景选项卡
        education_tab = ttk.Frame(tab_control)
        tab_control.add(education_tab, text="教育背景")
        
        # 创建工作简历选项卡
        work_tab = ttk.Frame(tab_control)
        tab_control.add(work_tab, text="工作简历")
        
        tab_control.pack(expand=1, fill="both")
        
        # 加载基本信息
        self.load_basic_info(basic_tab, teacher_id)
        
        # 加载职称信息
        self.load_title_info(title_tab, teacher_id)
        
        # 加载教育背景
        self.load_education_info(education_tab, teacher_id)
        
        # 加载工作简历
        self.load_work_experience(work_tab, teacher_id)
    
    def load_basic_info(self, tab, teacher_id):
        # 从数据库加载教师基本信息
        self.cursor.execute("SELECT * FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        teacher = self.cursor.fetchone()
        
        if teacher:
            # 创建信息显示框架
            info_frame = ttk.Frame(tab)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 显示照片
            photo_frame = ttk.Frame(info_frame)
            photo_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
            
            if teacher[7] and os.path.exists(teacher[7]):  # photo_path
                try:
                    img = Image.open(teacher[7])
                    img = img.resize((150, 200), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    photo_label = ttk.Label(photo_frame, image=photo)
                    photo_label.image = photo  # 保持引用
                    photo_label.pack()
                except Exception as e:
                    ttk.Label(photo_frame, text="无法加载照片").pack()
            else:
                ttk.Label(photo_frame, text="无照片", width=20, height=10).pack()
            
            # 显示基本信息
            info_grid = ttk.Frame(info_frame)
            info_grid.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
            
            # 定义字段和标签
            fields = [
                ("姓名:", teacher[1]),  # name
                ("性别:", teacher[2]),  # gender
                ("出生年月:", teacher[3]),  # birth_date
                ("民族:", teacher[4]),  # ethnicity
                ("籍贯:", teacher[5]),  # hometown
                ("身份证号:", teacher[6]),  # id_number
                ("入党时间:", teacher[8]),  # party_join_date
                ("参加工作时间:", teacher[9]),  # work_start_date
                ("健康状况:", teacher[10]),  # health_status
                ("任教学科:", teacher[11]),  # teaching_subject
                ("现任职务:", teacher[12])  # current_position
            ]
            
            # 显示字段
            for i, (label, value) in enumerate(fields):
                ttk.Label(info_grid, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", padx=5, pady=3)
                ttk.Label(info_grid, text=value if value else "").grid(row=i, column=1, sticky="w", padx=5, pady=3)
    
    def load_title_info(self, tab, teacher_id):
        # 从数据库加载教师职称信息
        self.cursor.execute("SELECT * FROM title_history WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
        titles = self.cursor.fetchall()
        
        # 创建职称信息列表
        columns = ("职称", "取得时间", "岗位", "聘任时间")
        title_tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            title_tree.heading(col, text=col)
            title_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=title_tree.yview)
        title_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        title_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for title in titles:
            title_tree.insert("", tk.END, values=(title[2], title[3], title[4], title[5]))
    
    def load_education_info(self, tab, teacher_id):
        # 从数据库加载教师教育背景
        self.cursor.execute("SELECT * FROM education WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
        educations = self.cursor.fetchall()
        
        # 创建教育背景列表
        columns = ("类型", "学位", "院校", "取得时间", "扫描件")
        edu_tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            edu_tree.heading(col, text=col)
            edu_tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=edu_tree.yview)
        edu_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        edu_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for edu in educations:
            has_scan = "有" if edu[6] and os.path.exists(edu[6]) else "无"  # scan_file_path
            edu_tree.insert("", tk.END, values=(edu[2], edu[3], edu[4], edu[5], has_scan))
        
        # 绑定双击事件查看扫描件
        edu_tree.bind("<Double-1>", lambda event, tree=edu_tree, data=educations: self.view_scan_file(event, tree, data))
    
    def view_scan_file(self, event, tree, data):
        # 获取选中的项
        selected_item = tree.selection()[0]
        item_index = tree.index(selected_item)
        
        # 获取扫描件路径
        scan_path = data[item_index][6]  # scan_file_path
        
        if scan_path and os.path.exists(scan_path):
            # 创建新窗口显示扫描件
            scan_window = tk.Toplevel(self.root)
            scan_window.title("扫描件查看")
            scan_window.geometry("800x600")
            
            try:
                img = Image.open(scan_path)
                img = img.resize((700, 500), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                photo_label = ttk.Label(scan_window, image=photo)
                photo_label.image = photo  # 保持引用
                photo_label.pack(padx=10, pady=10)
            except Exception as e:
                ttk.Label(scan_window, text=f"无法加载扫描件: {e}").pack(padx=10, pady=10)
        else:
            messagebox.showinfo("提示", "没有可用的扫描件")
    
    def load_work_experience(self, tab, teacher_id):
        # 从数据库加载工作简历
        self.cursor.execute("SELECT * FROM work_experience WHERE teacher_id = ? ORDER BY start_date DESC", (teacher_id,))
        experiences = self.cursor.fetchall()
        
        # 创建工作简历列表
        columns = ("开始时间", "结束时间", "单位", "职务", "描述")
        work_tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            work_tree.heading(col, text=col)
            work_tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=work_tree.yview)
        work_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        work_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for exp in experiences:
            work_tree.insert("", tk.END, values=(exp[2], exp[3], exp[4], exp[5], exp[6]))
    
    def show_archive_entry(self):
        # 创建档案录入窗口
        entry_window = tk.Toplevel(self.root)
        entry_window.title("档案录入")
        entry_window.geometry("800x600")
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(entry_window)
        
        # 创建基本信息选项卡
        basic_tab = ttk.Frame(tab_control)
        tab_control.add(basic_tab, text="基本信息")
        
        # 创建职称信息选项卡
        title_tab = ttk.Frame(tab_control)
        tab_control.add(title_tab, text="职称信息")
        
        # 创建教育背景选项卡
        education_tab = ttk.Frame(tab_control)
        tab_control.add(education_tab, text="教育背景")
        
        # 创建工作简历选项卡
        work_tab = ttk.Frame(tab_control)
        tab_control.add(work_tab, text="工作简历")
        
        tab_control.pack(expand=1, fill="both")
        
        # 创建基本信息表单
        self.create_basic_info_form(basic_tab)
        
        # 创建职称信息表单
        self.create_title_info_form(title_tab)
        
        # 创建教育背景表单
        self.create_education_form(education_tab)
        
        # 创建工作简历表单
        self.create_work_experience_form(work_tab)
    
    def create_basic_info_form(self, parent):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建照片上传区域
        photo_frame = ttk.LabelFrame(form_frame, text="照片")
        photo_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=10, sticky="nw")
        
        self.photo_path = None
        self.photo_label = ttk.Label(photo_frame, text="无照片", width=20, height=10)
        self.photo_label.pack(padx=10, pady=10)
        
        # 添加照片上传按钮
        ttk.Button(photo_frame, text="上传照片", command=self.upload_photo).pack(padx=10, pady=5)
        
        # 创建基本信息表单
        form_grid = ttk.Frame(form_frame)
        form_grid.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        # 创建表单字段
        fields = [
            ("姓名:", "name"),
            ("性别:", "gender", ["男", "女"]),
            ("出生年月:", "birth_date"),
            ("民族:", "ethnicity", ["汉族", "蒙古族", "回族", "藏族", "维吾尔族", "苗族", "彝族", "壮族", "布依族", "朝鲜族", "满族", "侗族", "瑶族", "白族", "土家族", "哈尼族", "哈萨克族", "傣族", "黎族", "傈僳族", "佤族", "畲族", "高山族", "拉祜族", "水族", "东乡族", "纳西族", "景颇族", "柯尔克孜族", "土族", "达斡尔族", "仫佬族", "羌族", "布朗族", "撒拉族", "毛南族", "仡佬族", "锡伯族", "阿昌族", "普米族", "塔吉克族", "怒族", "乌孜别克族", "俄罗斯族", "鄂温克族", "德昂族", "保安族", "裕固族", "京族", "塔塔尔族", "独龙族", "鄂伦春族", "赫哲族", "门巴族", "珞巴族", "基诺族", "其他"]),
            ("籍贯:", "hometown"),
            ("身份证号:", "id_number"),
            ("入党时间:", "party_join_date"),
            ("参加工作时间:", "work_start_date"),
            ("健康状况:", "health_status", ["健康", "良好", "一般", "较差"]),
            ("任教学科:", "teaching_subject"),
            ("现任职务:", "current_position")
        ]
        
        # 创建表单输入框
        self.basic_entries = {}
        for i, field_info in enumerate(fields):
            ttk.Label(form_grid, text=field_info[0]).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            
            if len(field_info) > 2 and isinstance(field_info[2], list):  # 如果有下拉选项
                entry = ttk.Combobox(form_grid, width=28, values=field_info[2])
            else:
                entry = ttk.Entry(form_grid, width=30)
                
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.basic_entries[field_info[1]] = entry
        
        # 添加日期选择辅助按钮
        date_fields = ["birth_date", "party_join_date", "work_start_date"]
        for field in date_fields:
            if field in self.basic_entries:
                i = next(i for i, f in enumerate(fields) if f[1] == field)
                ttk.Button(form_grid, text="选择日期", width=8, 
                          command=lambda f=field: self.select_date(self.basic_entries[f])).grid(row=i, column=2, padx=5, pady=3)
        
        # 添加保存按钮
        ttk.Button(form_frame, text="保存基本信息", command=self.save_basic_info).grid(row=len(fields), column=1, padx=10, pady=20)
    
    def upload_photo(self):
        # 打开文件对话框选择照片
        file_path = filedialog.askopenfilename(title="选择照片", filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.gif")])
        
        if file_path:
            try:
                # 创建照片目录
                os.makedirs('photos', exist_ok=True)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"photo_{uuid.uuid4().hex}{file_ext}"
                new_path = os.path.join('photos', new_filename)
                
                # 复制照片到应用程序目录
                shutil.copy2(file_path, new_path)
                
                # 更新照片显示
                img = Image.open(new_path)
                img = img.resize((150, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_label.configure(image=photo, text="")
                self.photo_label.image = photo  # 保持引用
                
                # 保存照片路径
                self.photo_path = new_path
                
                messagebox.showinfo("成功", "照片上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"照片上传失败: {e}")
                
    def select_date(self, entry_widget):
        """打开日期选择对话框"""
        # 创建日期选择窗口
        date_window = tk.Toplevel(self.root)
        date_window.title("选择日期")
        date_window.geometry("300x250")
        date_window.resizable(False, False)
        
        # 创建日历控件
        cal = ttk.Calendar(date_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        
        # 确认按钮回调函数
        def confirm_date():
            selected_date = cal.get_date()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_date)
            date_window.destroy()
        
        # 添加确认按钮
        ttk.Button(date_window, text="确认", command=confirm_date).pack(pady=10)
        
        # 如果entry中已有日期，则设置为当前选中日期
        current_date = entry_widget.get()
        if current_date:
            try:
                cal.selection_set(current_date)
            except:
                pass
    
    def save_basic_info(self):
        # 获取表单数据
        name = self.basic_entries["name"].get()
        gender = self.basic_entries["gender"].get()
        birth_date = self.basic_entries["birth_date"].get()
        ethnicity = self.basic_entries["ethnicity"].get()
        hometown = self.basic_entries["hometown"].get()
        id_number = self.basic_entries["id_number"].get()
        party_join_date = self.basic_entries["party_join_date"].get()
        work_start_date = self.basic_entries["work_start_date"].get()
        health_status = self.basic_entries["health_status"].get()
        teaching_subject = self.basic_entries["teaching_subject"].get()
        current_position = self.basic_entries["current_position"].get()
        
        # 验证必填字段
        if not name:
            messagebox.showerror("错误", "姓名不能为空")
            return
        
        # 生成教师ID
        teacher_id = uuid.uuid4().hex
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 插入数据到数据库
            self.cursor.execute("""
            INSERT INTO teacher_info (
                teacher_id, name, gender, birth_date, ethnicity, hometown, id_number,
                photo_path, party_join_date, work_start_date, health_status,
                teaching_subject, current_position, create_time, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                teacher_id, name, gender, birth_date, ethnicity, hometown, id_number,
                self.photo_path, party_join_date, work_start_date, health_status,
                teaching_subject, current_position, current_time, current_time
            ))
            
            self.conn.commit()
            messagebox.showinfo("成功", "基本信息保存成功")
            
            # 刷新教师列表
            self.load_teacher_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "身份证号已存在")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
            
    def create_title_info_form(self, parent):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建表单字段
        fields = [
            ("职称:", "title"),
            ("取得时间:", "obtain_date"),
            ("岗位:", "post"),
            ("聘任时间:", "appointment_date")
        ]
        
        # 创建表单输入框
        self.title_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.title_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="保存职称信息", command=self.save_title_info).grid(row=len(fields), column=1, padx=10, pady=20)
    
    def save_title_info(self):
        # 获取表单数据
        title = self.title_entries["title"].get()
        obtain_date = self.title_entries["obtain_date"].get()
        post = self.title_entries["post"].get()
        appointment_date = self.title_entries["appointment_date"].get()
        
        # 验证必填字段
        if not title or not obtain_date:
            messagebox.showerror("错误", "职称和取得时间不能为空")
            return
        
        # 获取当前选中的教师ID
        try:
            selected_item = self.teacher_tree.selection()[0]
            teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 生成记录ID
        record_id = uuid.uuid4().hex
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 插入数据到数据库
            self.cursor.execute("""
            INSERT INTO title_history (
                record_id, teacher_id, title, obtain_date, post, appointment_date, create_time, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id, teacher_id, title, obtain_date, post, appointment_date, current_time, current_time
            ))
            
            self.conn.commit()
            messagebox.showinfo("成功", "职称信息保存成功")
            
            # 清空表单
            for entry in self.title_entries.values():
                entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def create_education_form(self, parent):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建扫描件上传区域
        scan_frame = ttk.LabelFrame(form_frame, text="扫描件")
        scan_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="nw")
        
        self.scan_path = None
        self.scan_label = ttk.Label(scan_frame, text="无扫描件", width=20, height=10)
        self.scan_label.pack(padx=10, pady=10)
        
        # 添加扫描件上传按钮
        ttk.Button(scan_frame, text="上传扫描件", command=self.upload_scan).pack(padx=10, pady=5)
        
        # 创建表单字段
        fields = [
            ("类型:", "edu_type"),
            ("学位:", "degree"),
            ("院校:", "institution"),
            ("取得时间:", "obtain_date")
        ]
        
        # 创建表单输入框
        self.education_entries = {}
        form_grid = ttk.Frame(form_frame)
        form_grid.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_grid, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form_grid, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.education_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="保存教育背景", command=self.save_education_info).grid(row=5, column=1, padx=10, pady=20)
    
    def upload_scan(self):
        # 打开文件对话框选择扫描件
        file_path = filedialog.askopenfilename(title="选择扫描件", filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.pdf")])
        
        if file_path:
            try:
                # 创建扫描件目录
                os.makedirs('scans', exist_ok=True)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"scan_{uuid.uuid4().hex}{file_ext}"
                new_path = os.path.join('scans', new_filename)
                
                # 复制扫描件到应用程序目录
                shutil.copy2(file_path, new_path)
                
                # 更新扫描件显示
                if file_ext.lower() in [".jpg", ".jpeg", ".png"]:
                    try:
                        img = Image.open(new_path)
                        img = img.resize((150, 200), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.scan_label.configure(image=photo)
                        self.scan_label.image = photo  # 保持引用
                    except Exception:
                        self.scan_label.configure(text="扫描件已上传")
                        self.scan_label.image = None
                else:
                    self.scan_label.configure(text="扫描件已上传")
                    self.scan_label.image = None
                
                # 保存扫描件路径
                self.scan_path = new_path
                
                messagebox.showinfo("成功", "扫描件上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"扫描件上传失败: {e}")
    
    def save_education_info(self):
        # 获取表单数据
        edu_type = self.education_entries["edu_type"].get()
        degree = self.education_entries["degree"].get()
        institution = self.education_entries["institution"].get()
        obtain_date = self.education_entries["obtain_date"].get()
        
        # 验证必填字段
        if not edu_type or not institution or not obtain_date:
            messagebox.showerror("错误", "类型、院校和取得时间不能为空")
            return
        
        # 获取当前选中的教师ID
        try:
            selected_item = self.teacher_tree.selection()[0]
            teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 生成记录ID
        record_id = uuid.uuid4().hex
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 插入数据到数据库
            self.cursor.execute("""
            INSERT INTO education (
                record_id, teacher_id, edu_type, degree, institution, obtain_date, scan_file_path, create_time, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id, teacher_id, edu_type, degree, institution, obtain_date, self.scan_path, current_time, current_time
            ))
            
            self.conn.commit()
            messagebox.showinfo("成功", "教育背景保存成功")
            
            # 清空表单
            for entry in self.education_entries.values():
                entry.delete(0, tk.END)
            
            # 重置扫描件
            self.scan_path = None
            self.scan_label.configure(text="无扫描件")
            self.scan_label.image = None
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def create_work_experience_form(self, parent):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建表单字段
        fields = [
            ("开始时间:", "start_date"),
            ("结束时间:", "end_date"),
            ("单位:", "organization"),
            ("职务:", "position"),
            ("描述:", "description")
        ]
        
        # 创建表单输入框
        self.work_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            
            if field == "description":
                entry = tk.Text(form_frame, width=30, height=4)
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            
            self.work_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="保存工作经历", command=self.save_work_experience).grid(row=len(fields), column=1, padx=10, pady=20)
    
    def save_work_experience(self):
        # 获取表单数据
        start_date = self.work_entries["start_date"].get()
        end_date = self.work_entries["end_date"].get()
        organization = self.work_entries["organization"].get()
        position = self.work_entries["position"].get()
        description = self.work_entries["description"].get("1.0", tk.END).strip()
        
        # 验证必填字段
        if not start_date or not organization:
            messagebox.showerror("错误", "开始时间和单位不能为空")
            return
        
        # 获取当前选中的教师ID
        try:
            selected_item = self.teacher_tree.selection()[0]
            teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 生成记录ID
        record_id = uuid.uuid4().hex
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 插入数据到数据库
            self.cursor.execute("""
            INSERT INTO work_experience (
                record_id, teacher_id, start_date, end_date, organization, position, description, create_time, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id, teacher_id, start_date, end_date, organization, position, description, current_time, current_time
            ))
            
            self.conn.commit()
            messagebox.showinfo("成功", "工作经历保存成功")
            
            # 清空表单
            for field, entry in self.work_entries.items():
                if field == "description":
                    entry.delete("1.0", tk.END)
                else:
                    entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
            
    def show_document_management(self):
        # 创建照片/扫描件管理窗口
        doc_window = tk.Toplevel(self.root)
        doc_window.title("照片/扫描件管理")
        doc_window.geometry("800x600")
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(doc_window)
        
        # 创建照片管理选项卡
        photo_tab = ttk.Frame(tab_control)
        tab_control.add(photo_tab, text="照片管理")
        
        # 创建扫描件管理选项卡
        scan_tab = ttk.Frame(tab_control)
        tab_control.add(scan_tab, text="扫描件管理")
        
        tab_control.pack(expand=1, fill="both")
        
        # 加载照片管理界面
        self.load_photo_management(photo_tab)
        
        # 加载扫描件管理界面
        self.load_scan_management(scan_tab)
    
    def load_photo_management(self, parent):
        # 创建主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建教师选择区域
        select_frame = ttk.LabelFrame(main_frame, text="选择教师")
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 创建教师下拉列表
        ttk.Label(select_frame, text="教师:").grid(row=0, column=0, padx=5, pady=5)
        
        # 获取所有教师
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info ORDER BY name")
        teachers = self.cursor.fetchall()
        
        # 创建教师选择变量
        self.selected_teacher_photo = tk.StringVar()
        teacher_combo = ttk.Combobox(select_frame, textvariable=self.selected_teacher_photo, width=30)
        teacher_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # 设置下拉列表值
        teacher_combo['values'] = [f"{teacher[1]} (ID: {teacher[0]})" for teacher in teachers]
        
        # 绑定选择事件
        teacher_combo.bind("<<ComboboxSelected>>", self.on_photo_teacher_selected)
        
        # 创建照片显示区域
        photo_frame = ttk.LabelFrame(main_frame, text="照片")
        photo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建照片标签
        self.photo_display = ttk.Label(photo_frame, text="请选择教师", width=30, height=15)
        self.photo_display.pack(padx=20, pady=20)
        
        # 创建按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 添加上传新照片按钮
        ttk.Button(button_frame, text="上传新照片", command=self.upload_new_photo).pack(side=tk.LEFT, padx=5)
        
        # 添加删除照片按钮
        ttk.Button(button_frame, text="删除照片", command=self.delete_photo).pack(side=tk.LEFT, padx=5)
    
    def on_photo_teacher_selected(self, event):
        # 获取选中的教师ID
        selected = self.selected_teacher_photo.get()
        if selected:
            teacher_id = selected.split("ID: ")[1].rstrip(')')
            
            # 查询教师照片
            self.cursor.execute("SELECT photo_path FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
            result = self.cursor.fetchone()
            
            if result and result[0] and os.path.exists(result[0]):
                try:
                    # 显示照片
                    img = Image.open(result[0])
                    img = img.resize((200, 250), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.photo_display.configure(image=photo)
                    self.photo_display.image = photo  # 保持引用
                except Exception as e:
                    self.photo_display.configure(text=f"无法加载照片: {e}")
                    self.photo_display.image = None
            else:
                self.photo_display.configure(text="无照片")
                self.photo_display.image = None
    
    def upload_new_photo(self):
        # 检查是否选择了教师
        selected = self.selected_teacher_photo.get()
        if not selected:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 获取教师ID
        teacher_id = selected.split("ID: ")[1].rstrip(')')
        
        # 打开文件对话框选择照片
        file_path = filedialog.askopenfilename(title="选择照片", filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.gif")])
        
        if file_path:
            try:
                # 创建照片目录
                os.makedirs('photos', exist_ok=True)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"photo_{uuid.uuid4().hex}{file_ext}"
                new_path = os.path.join('photos', new_filename)
                
                # 复制照片到应用程序目录
                shutil.copy2(file_path, new_path)
                
                # 更新数据库中的照片路径
                self.cursor.execute("UPDATE teacher_info SET photo_path = ?, update_time = ? WHERE teacher_id = ?",
                                   (new_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), teacher_id))
                self.conn.commit()
                
                # 更新照片显示
                img = Image.open(new_path)
                img = img.resize((200, 250), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_display.configure(image=photo)
                self.photo_display.image = photo  # 保持引用
                
                messagebox.showinfo("成功", "照片上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"照片上传失败: {e}")
    
    def delete_photo(self):
        # 检查是否选择了教师
        selected = self.selected_teacher_photo.get()
        if not selected:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 获取教师ID
        teacher_id = selected.split("ID: ")[1].rstrip(')')
        
        # 查询教师照片
        self.cursor.execute("SELECT photo_path FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        result = self.cursor.fetchone()
        
        if result and result[0] and os.path.exists(result[0]):
            # 确认删除
            if messagebox.askyesno("确认", "确定要删除该照片吗？"):
                try:
                    # 删除文件
                    os.remove(result[0])
                    
                    # 更新数据库
                    self.cursor.execute("UPDATE teacher_info SET photo_path = NULL, update_time = ? WHERE teacher_id = ?",
                                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), teacher_id))
                    self.conn.commit()
                    
                    # 更新显示
                    self.photo_display.configure(text="照片已删除")
                    self.photo_display.image = None
                    
                    messagebox.showinfo("成功", "照片已删除")
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {e}")
        else:
            messagebox.showinfo("提示", "没有可删除的照片")
    
    def load_scan_management(self, parent):
        # 创建主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建教师选择区域
        select_frame = ttk.LabelFrame(main_frame, text="选择教师")
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 创建教师下拉列表
        ttk.Label(select_frame, text="教师:").grid(row=0, column=0, padx=5, pady=5)
        
        # 获取所有教师
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info ORDER BY name")
        teachers = self.cursor.fetchall()
        
        # 创建教师选择变量
        self.selected_teacher_scan = tk.StringVar()
        teacher_combo = ttk.Combobox(select_frame, textvariable=self.selected_teacher_scan, width=30)
        teacher_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # 设置下拉列表值
        teacher_combo['values'] = [f"{teacher[1]} (ID: {teacher[0]})" for teacher in teachers]
        
        # 绑定选择事件
        teacher_combo.bind("<<ComboboxSelected>>", self.on_scan_teacher_selected)
        
        # 创建扫描件列表区域
        scan_frame = ttk.LabelFrame(main_frame, text="扫描件列表")
        scan_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建扫描件列表
        columns = ("记录ID", "类型", "学位", "院校", "取得时间", "扫描件")
        self.scan_tree = ttk.Treeview(scan_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.scan_tree.heading(col, text=col)
            self.scan_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(scan_frame, orient=tk.VERTICAL, command=self.scan_tree.yview)
        self.scan_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scan_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件查看扫描件
        self.scan_tree.bind("<Double-1>", self.view_selected_scan)
        
        # 创建按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 添加上传新扫描件按钮
        ttk.Button(button_frame, text="上传新扫描件", command=self.upload_new_scan).pack(side=tk.LEFT, padx=5)
        
        # 添加删除扫描件按钮
        ttk.Button(button_frame, text="删除扫描件", command=self.delete_scan).pack(side=tk.LEFT, padx=5)
    
    def on_scan_teacher_selected(self, event):
        # 获取选中的教师ID
        selected = self.selected_teacher_scan.get()
        if selected:
            teacher_id = selected.split("ID: ")[1].rstrip(')')
            
            # 清除现有数据
            for item in self.scan_tree.get_children():
                self.scan_tree.delete(item)
            
            # 查询教师的教育背景记录
            self.cursor.execute("""
            SELECT record_id, edu_type, degree, institution, obtain_date, scan_file_path 
            FROM education 
            WHERE teacher_id = ? 
            ORDER BY obtain_date DESC
            """, (teacher_id,))
            
            educations = self.cursor.fetchall()
            
            # 添加数据到树形视图
            for edu in educations:
                has_scan = "有" if edu[5] and os.path.exists(edu[5]) else "无"  # scan_file_path
                self.scan_tree.insert("", tk.END, values=(edu[0], edu[1], edu[2], edu[3], edu[4], has_scan))
    
    def view_selected_scan(self, event):
        # 获取选中的项
        selected_item = self.scan_tree.selection()
        if not selected_item:
            return
        
        # 获取记录ID
        record_id = self.scan_tree.item(selected_item[0], "values")[0]
        
        # 查询扫描件路径
        self.cursor.execute("SELECT scan_file_path FROM education WHERE record_id = ?", (record_id,))
        result = self.cursor.fetchone()
        
        if result and result[0] and os.path.exists(result[0]):
            # 创建新窗口显示扫描件
            scan_window = tk.Toplevel(self.root)
            scan_window.title("扫描件查看")
            scan_window.geometry("800x600")
            
            try:
                # 如果是图片文件
                file_ext = os.path.splitext(result[0])[1].lower()
                if file_ext in [".jpg", ".jpeg", ".png", ".gif"]:
                    img = Image.open(result[0])
                    img = img.resize((700, 500), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    photo_label = ttk.Label(scan_window, image=photo)
                    photo_label.image = photo  # 保持引用
                    photo_label.pack(padx=10, pady=10)
                else:
                    # 如果是PDF或其他文件，显示文件路径
                    ttk.Label(scan_window, text=f"文件路径: {result[0]}").pack(padx=10, pady=10)
                    ttk.Button(scan_window, text="打开文件", 
                              command=lambda: os.startfile(result[0]) if os.path.exists(result[0]) else None).pack(padx=10, pady=10)
            except Exception as e:
                ttk.Label(scan_window, text=f"无法加载扫描件: {e}").pack(padx=10, pady=10)
        else:
            messagebox.showinfo("提示", "没有可用的扫描件")
    
    def upload_new_scan(self):
        # 检查是否选择了教师
        selected = self.selected_teacher_scan.get()
        if not selected:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 检查是否选择了教育记录
        selected_item = self.scan_tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请先选择一个教育记录")
            return
        
        # 获取记录ID
        record_id = self.scan_tree.item(selected_item[0], "values")[0]
        
        # 打开文件对话框选择扫描件
        file_path = filedialog.askopenfilename(title="选择扫描件", filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.pdf")])
        
        if file_path:
            try:
                # 创建扫描件目录
                os.makedirs('scans', exist_ok=True)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"scan_{uuid.uuid4().hex}{file_ext}"
                new_path = os.path.join('scans', new_filename)
                
                # 复制扫描件到应用程序目录
                shutil.copy2(file_path, new_path)
                
                # 更新数据库中的扫描件路径
                self.cursor.execute("UPDATE education SET scan_file_path = ?, update_time = ? WHERE record_id = ?",
                                   (new_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id))
                self.conn.commit()
                
                # 刷新扫描件列表
                self.on_scan_teacher_selected(None)
                
                messagebox.showinfo("成功", "扫描件上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"扫描件上传失败: {e}")
    
    def delete_scan(self):
        # 检查是否选择了教育记录
        selected_item = self.scan_tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请先选择一个教育记录")
            return
        
        # 获取记录ID
        record_id = self.scan_tree.item(selected_item[0], "values")[0]
        
        # 查询扫描件路径
        self.cursor.execute("SELECT scan_file_path FROM education WHERE record_id = ?", (record_id,))
        result = self.cursor.fetchone()
        
        if result and result[0] and os.path.exists(result[0]):
            # 确认删除
            if messagebox.askyesno("确认", "确定要删除该扫描件吗？"):
                try:
                    # 删除文件
                    os.remove(result[0])
                    
                    # 更新数据库
                    self.cursor.execute("UPDATE education SET scan_file_path = NULL, update_time = ? WHERE record_id = ?",
                                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id))
                    self.conn.commit()
                    
                    # 刷新扫描件列表
                    self.on_scan_teacher_selected(None)
                    
                    messagebox.showinfo("成功", "扫描件已删除")
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {e}")
        else:
            messagebox.showinfo("提示", "没有可删除的扫描件")
            
    #====================== 业务情况管理 ======================
    def show_business_management(self):
        self.clear_content_frame()
        
        # 创建业务情况管理页面
        ttk.Label(self.content_frame, text="业务情况管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建子功能按钮框架
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        # 添加子功能按钮
        ttk.Button(btn_frame, text="教学工作情况", command=self.show_teaching_records).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="教育工作情况", command=self.show_education_work).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="荣誉管理", command=self.show_awards).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="公开课管理", command=self.show_public_lessons).grid(row=0, column=3, padx=10, pady=5)
        ttk.Button(btn_frame, text="论文管理", command=self.show_papers).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="课题管理", command=self.show_research_projects).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="学生竞赛辅导", command=self.show_student_competitions).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="青蓝工程", command=self.show_mentoring).grid(row=1, column=3, padx=10, pady=5)
        ttk.Button(btn_frame, text="专业引领", command=self.show_professional_leadership).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="考试成绩", command=self.show_exam_results).grid(row=2, column=1, padx=10, pady=5)
        
        # 显示提示信息
        ttk.Label(self.content_frame, text="请选择上方功能按钮进行操作", font=("Arial", 12)).pack(pady=50)