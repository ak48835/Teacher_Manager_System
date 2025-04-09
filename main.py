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
# 创建应用程序主类
class ArchiveManagementSystem:
    #---------------------------------初始化--------------------------------
    #初始化
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
    # 数据库设置
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
    # 文件夹设置
    def setup_folders(self):
        # 创建存储照片和扫描件的文件夹
        os.makedirs('photos', exist_ok=True)
        os.makedirs('scans', exist_ok=True)
    # 主界面
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
    # 清除内容区域
    def clear_content_frame(self):
        # 清除内容区域的所有小部件
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    #----------------------------------模块一---------------------------------
    # 基本信息管理
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
        ttk.Button(btn_frame, text="照片/扫描件管理", command=self.show_document_management).grid(row=0, column=4, padx=10, pady=5)
        # 创建删除按钮并设置样式
        ttk.Button(btn_frame, text="档案删除", command=self.delete_teacher).grid(row=0, column=3, padx=10, pady=5)
        # 显示教师列表
        self.show_teacher_list()
    # 档案录入
    def delete_teacher(self):
        # 检查是否选择了教师
        try:
            selected_item = self.teacher_tree.selection()[0]
            teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择要删除的教师")
            return
            
        # 获取教师姓名
        self.cursor.execute("SELECT name FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        teacher_name = self.cursor.fetchone()[0]
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除教师 {teacher_name} 的所有档案信息吗？\n此操作不可恢复！"):
            return
            
        try:
            # 开始事务
            self.cursor.execute("BEGIN TRANSACTION")
            
            # 删除相关表中的记录
            tables = [
                "title_history", "education", "work_experience",
                "teaching_records", "education_work", "award_recipients",
                "public_lessons", "papers", "project_members",
                "student_competitions", "mentoring", "professional_leadership",
                "exam_results"
            ]
            
            # 删除各个关联表中的数据
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table} WHERE teacher_id = ?", (teacher_id,))
            
            # 删除教师照片
            self.cursor.execute("SELECT photo_path FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
            photo_path = self.cursor.fetchone()[0]
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
                
            # 删除教育背景扫描件
            self.cursor.execute("SELECT scan_file_path FROM education WHERE teacher_id = ?", (teacher_id,))
            scan_files = self.cursor.fetchall()
            for scan_file in scan_files:
                if scan_file[0] and os.path.exists(scan_file[0]):
                    os.remove(scan_file[0])
            
            # 最后删除教师基本信息
            self.cursor.execute("DELETE FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
            
            # 提交事务
            self.conn.commit()
            
            # 从树形视图中移除
            self.teacher_tree.delete(selected_item)
            
            messagebox.showinfo("成功", f"已删除教师 {teacher_name} 的所有档案信息")
            
        except Exception as e:
            # 发生错误时回滚事务
            self.conn.rollback()
            messagebox.showerror("错误", f"删除失败: {e}")
    # 档案修改
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
        self.teacher_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teacher_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.teacher_tree.bind("<Double-1>", self.on_teacher_selected)
        
        # 加载教师数据
        self.load_teacher_data()
    # 加载教师数据
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
    # 搜索教师
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
    # 双击事件
    def on_teacher_selected(self, event):
        # 获取选中的教师ID
        selected_item = self.teacher_tree.selection()[0]
        teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        
        # 显示教师详细信息
        self.show_teacher_details(teacher_id)
    # 显示教师详细信息
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
        
        # 创建教学工作情况选项卡
        teaching_tab = ttk.Frame(tab_control)
        tab_control.add(teaching_tab, text="教学工作情况")
        
        # 创建教育工作情况选项卡
        edu_work_tab = ttk.Frame(tab_control)
        tab_control.add(edu_work_tab, text="教育工作情况")
        
        # 创建荣誉情况选项卡
        honor_tab = ttk.Frame(tab_control)
        tab_control.add(honor_tab, text="荣誉情况")
        
        # 创建公开课情况选项卡
        lesson_tab = ttk.Frame(tab_control)
        tab_control.add(lesson_tab, text="公开课情况")
        
        # 创建论文发表情况选项卡
        paper_tab = ttk.Frame(tab_control)
        tab_control.add(paper_tab, text="论文发表情况")
        
        # 创建课题管理情况选项卡
        project_tab = ttk.Frame(tab_control)
        tab_control.add(project_tab, text="课题管理情况")
        
        # 创建学生竞赛辅导情况选项卡
        competition_tab = ttk.Frame(tab_control)
        tab_control.add(competition_tab, text="学生竞赛辅导情况")
        
        # 创建青蓝工程情况选项卡
        mentoring_tab = ttk.Frame(tab_control)
        tab_control.add(mentoring_tab, text="青蓝工程情况")
        
        tab_control.pack(expand=1, fill="both")
        
        # 加载基本信息
        self.load_basic_info(basic_tab, teacher_id)
        
        # 加载职称信息
        self.load_title_info(title_tab, teacher_id)
        
        # 加载教育背景
        self.load_education_info(education_tab, teacher_id)
        
        # 加载工作简历
        self.load_work_experience(work_tab, teacher_id)
        
        # 加载教学工作情况
        self.load_teaching_info(teaching_tab, teacher_id)
        
        # 加载教育工作情况
        self.load_edu_work_info(edu_work_tab, teacher_id)
        
        # 加载荣誉情况
        self.load_honor_info(honor_tab, teacher_id)
        
        # 加载公开课情况
        self.load_lesson_info(lesson_tab, teacher_id)
        
        # 加载论文发表情况
        self.load_paper_info(paper_tab, teacher_id)
        
        # 加载课题管理情况
        self.load_project_info(project_tab, teacher_id)
        
        # 加载学生竞赛辅导情况
        self.load_competition_info(competition_tab, teacher_id)
        
        # 加载青蓝工程情况
        self.load_mentoring_info(mentoring_tab, teacher_id)
    # 加载基本信息
    def load_basic_info(self, tab, teacher_id):
        # 从数据库加载教师基本信息
        self.cursor.execute("SELECT * FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        teacher = self.cursor.fetchone()
        
        if teacher:
            # 创建信息显示框架
            info_frame = tk.Frame(tab)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 显示照片
            photo_frame = tk.Frame(info_frame)
            photo_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
            
            if teacher[7] and os.path.exists(teacher[7]):  # photo_path
                try:
                    img = Image.open(teacher[7])
                    img = img.resize((150, 200), Image.Resampling.LANCZOS)
                    self.current_photo = ImageTk.PhotoImage(img)  # 保存为实例属性
                    photo_label = tk.Label(photo_frame, image=self.current_photo)
                    photo_label.pack()
                except Exception as e:
                    tk.Label(photo_frame, text="无法加载照片").pack()
            else:
                tk.Label(photo_frame, text="无照片", width=20, height=10).pack()
            
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
    # 加载职称信息
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
        title_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        title_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for title in titles:
            title_tree.insert("", tk.END, values=(title[2], title[3], title[4], title[5]))
    # 加载教学工作情况
    def load_teaching_info(self, tab, teacher_id):
        # 从数据库加载教学工作情况
        self.cursor.execute("""
        SELECT academic_year, semester, subject, classes, student_count, weekly_hours 
        FROM teaching_records 
        WHERE teacher_id = ? 
        ORDER BY academic_year DESC, semester DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建教学工作情况列表
        columns = ("学年", "学期", "学科", "任教班级", "学生人数", "周课时数")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
    # 加载教育工作情况
    def load_edu_work_info(self, tab, teacher_id):
        # 从数据库加载教育工作情况
        self.cursor.execute("""
        SELECT academic_year, semester, work_type, description 
        FROM education_work 
        WHERE teacher_id = ? 
        ORDER BY academic_year DESC, semester DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建教育工作情况列表
        columns = ("学年", "学期", "工作类型", "工作描述")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
    # 加载荣誉情况
    def load_honor_info(self, tab, teacher_id):
        # 从数据库加载荣誉信息
        self.cursor.execute("""
        SELECT a.award_name, a.award_level, a.award_unit, a.award_date, a.award_type, ar.rank 
        FROM awards a 
        JOIN award_recipients ar ON a.award_id = ar.award_id 
        WHERE ar.teacher_id = ? 
        ORDER BY a.award_date DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建荣誉情况列表
        columns = ("奖项名称", "获奖级别", "颁奖单位", "获奖时间", "奖项类型", "获奖等第")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
    # 加载公开课情况
    def load_lesson_info(self, tab, teacher_id):
        # 从数据库加载公开课信息
        self.cursor.execute("""
        SELECT lesson_name, lesson_scope, lesson_date 
        FROM public_lessons 
        WHERE teacher_id = ? 
        ORDER BY lesson_date DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建公开课情况列表
        columns = ("课程名称", "课程范围", "授课时间")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
    # 加载论文发表情况
    def load_paper_info(self, tab, teacher_id):
        # 从数据库加载论文信息
        self.cursor.execute("""
        SELECT paper_title, journal_name, paper_level, publish_date 
        FROM papers 
        WHERE teacher_id = ? 
        ORDER BY publish_date DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建论文发表情况列表
        columns = ("论文题目", "期刊名称", "论文级别", "发表时间")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
    # 加载课题管理情况
    def load_project_info(self, tab, teacher_id):
        # 从数据库加载课题信息
        self.cursor.execute("""
        SELECT rp.project_name, rp.project_level, rp.completion_date, pm.is_leader, pm.member_rank 
        FROM research_projects rp 
        JOIN project_members pm ON rp.project_id = pm.project_id 
        WHERE pm.teacher_id = ? 
        ORDER BY rp.completion_date DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建课题管理情况列表
        columns = ("课题名称", "课题级别", "完成时间", "是否负责人", "成员排序")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            # 将布尔值转换为是/否
            is_leader = "是" if record[3] else "否"
            values = (record[0], record[1], record[2], is_leader, record[4])
            tree.insert("", tk.END, values=values)
    
    # 加载学生竞赛辅导情况
    def load_competition_info(self, tab, teacher_id):
        # 从数据库加载竞赛辅导信息
        self.cursor.execute("""
        SELECT competition_name, winner_count, award_level, competition_date 
        FROM student_competitions 
        WHERE teacher_id = ? 
        ORDER BY competition_date DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建竞赛辅导情况列表
        columns = ("竞赛名称", "获奖学生数", "获奖级别", "竞赛时间")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
    # 加载青蓝工程情况
    def load_mentoring_info(self, tab, teacher_id):
        # 从数据库加载青蓝工程信息
        self.cursor.execute("""
        SELECT t.name, m.start_date, m.end_date, m.achievements 
        FROM mentoring m 
        JOIN teacher_info t ON m.apprentice_id = t.teacher_id 
        WHERE m.teacher_id = ? 
        ORDER BY m.start_date DESC
        """, (teacher_id,))
        records = self.cursor.fetchall()
        
        # 创建青蓝工程情况列表
        columns = ("徒弟姓名", "开始时间", "结束时间", "指导成果")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for record in records:
            tree.insert("", tk.END, values=record)
    
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
# 设置教育背景列表的垂直滚动条
        edu_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        edu_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for edu in educations:
            has_scan = "有" if edu[6] and os.path.exists(edu[6]) else "无"  # scan_file_path
            edu_tree.insert("", tk.END, values=(edu[2], edu[3], edu[4], edu[5], has_scan))
        
        # 绑定双击事件查看扫描件
        edu_tree.bind("<Double-1>", lambda event, tree=edu_tree, data=educations: self.view_scan_file(event, tree, data))
    # 查看扫描件
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
                img = img.resize((150, 200), Image.Resampling.LANCZOS)
                self.current_scan_photo = ImageTk.PhotoImage(img)  # 保存为实例属性
                photo_label = tk.Label(scan_window, image=self.current_scan_photo)
                photo_label.pack(padx=10, pady=10)
            except Exception as e:
                ttk.Label(scan_window, text=f"无法加载扫描件: {e}").pack(padx=10, pady=10)
        else:
            messagebox.showinfo("提示", "没有可用的扫描件")
    # 加载工作简历
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
        work_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        work_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加数据
        for exp in experiences:
            work_tree.insert("", tk.END, values=(exp[2], exp[3], exp[4], exp[5], exp[6]))
    # 档案录入
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
    # 创建基本信息表单
    def create_basic_info_form(self, parent):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建照片上传区域
        photo_frame = tk.LabelFrame(form_frame, text="照片")
        photo_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=10, sticky="nw")
        
        self.photo_path = None
        self.photo_label = tk.Label(photo_frame, text="无照片", width=20, height=10)
        self.photo_label.pack(padx=10, pady=10)
        
        # 添加照片上传按钮
        tk.Button(photo_frame, text="上传照片", command=self.upload_photo).pack(padx=10, pady=5)
        
        # 创建基本信息表单
        form_grid = tk.Frame(form_frame)
        form_grid.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        # 创建表单字段
        fields = [
            ("姓名:", "name"),
            ("性别:", "gender"),
            ("出生年月:", "birth_date"),
            ("民族:", "ethnicity"),
            ("籍贯:", "hometown"),
            ("身份证号:", "id_number"),
            ("入党时间:", "party_join_date"),
            ("参加工作时间:", "work_start_date"),
            ("健康状况:", "health_status"),
            ("任教学科:", "teaching_subject"),
            ("现任职务:", "current_position")
        ]
        
        # 创建表单输入框
        self.basic_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_grid, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form_grid, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.basic_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="保存基本信息", command=self.save_basic_info).grid(row=7, column=1, padx=10, pady=20)
    # 上传照片
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
                img = img.resize((150, 200), Image.Resampling.LANCZOS)
                self.current_photo = ImageTk.PhotoImage(img)  # 保存为实例属性
                self.photo_label.configure(image=self.current_photo)
                
                # 保存照片路径
                self.photo_path = new_path
                
                messagebox.showinfo("成功", "照片上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"照片上传失败: {e}")
    # 保存基本信息
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
    # 创建职称信息表单
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
    # 保存职称信息
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
    # 创建教育背景表单
    def create_education_form(self, parent):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建扫描件上传区域
        scan_frame = ttk.LabelFrame(form_frame, text="扫描件")
        scan_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="nw")
        
        self.scan_path = None
        self.scan_label = tk.Label(scan_frame, text="无扫描件", width=20, height=10)
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
    # 上传扫描件
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
                        img = img.resize((150, 200), Image.Resampling.LANCZOS)
                        self.current_scan_photo = ImageTk.PhotoImage(img)  # 保存为实例属性
                        self.scan_label.configure(image=self.current_scan_photo)
                    except Exception:
                        self.scan_label.configure(text="扫描件已上传", image="")
                else:
                    self.scan_label.configure(text="扫描件已上传", image="")
                
                # 保存扫描件路径
                self.scan_path = new_path
                
                messagebox.showinfo("成功", "扫描件上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"扫描件上传失败: {e}")
    # 保存教育背景
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
            self.scan_label.configure(text="无扫描件", image="")
            if hasattr(self, 'current_scan_photo'):
                self.current_scan_photo = None
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    # 创建工作简历表单
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
    # 保存工作经历
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
    # 显示档案编辑窗口
    def show_archive_edit(self):
        # 检查是否选择了教师
        try:
            selected_item = self.teacher_tree.selection()[0]
            teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个教师")
            return
        
        # 创建档案修改窗口（新增以下代码）
        edit_window = tk.Toplevel(self.root)
        edit_window.title("档案修改")
        edit_window.geometry("800x600")
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(edit_window)
        
        # 创建各个选项卡
        tabs = {
            "基本信息": ttk.Frame(tab_control),
            "职称信息": ttk.Frame(tab_control),
            "教育背景": ttk.Frame(tab_control),
            "工作简历": ttk.Frame(tab_control)
        }
        
        for tab_name, tab_frame in tabs.items():
            tab_control.add(tab_frame, text=tab_name)
        
        tab_control.pack(expand=1, fill="both")
        
        # 加载各个编辑表单（新增以下调用）
        self.create_basic_info_edit_form(tabs["基本信息"], teacher_id)
        self.create_title_info_edit_form(tabs["职称信息"], teacher_id)
        self.create_education_edit_form(tabs["教育背景"], teacher_id) 
        self.create_work_experience_edit_form(tabs["工作简历"], teacher_id)                                         

    # 显示业务情况管理页面
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
        ttk.Button(btn_frame, text="教学比武获奖", command=self.show_teachingfight_records).grid(row=0, column=3, padx=10, pady=5)
        ttk.Button(btn_frame, text="公开课管理", command=self.show_public_lessons).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="论文发表情况", command=self.show_papers).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="课题管理", command=self.show_research_projects).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="学生竞赛辅导", command=self.show_student_competitions).grid(row=1, column=3, padx=10, pady=5)
        ttk.Button(btn_frame, text="青蓝工程", command=self.show_mentoring).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="专业引领", command=self.show_professional_leadership).grid(row=2, column=1, padx=10, pady=5)
        ttk.Button(btn_frame,text="变化情况",command=self.change_situation).grid(row=2, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="考试成绩", command=self.show_exam_results).grid(row=2, column=3, padx=10, pady=5)
        
        # 显示提示信息
        ttk.Label(self.content_frame, text="请选择上方功能按钮进行操作", font=("Arial", 12)).pack(pady=50)
    # 显示教学工作情况页面
    def show_teaching_records(self):
        self.clear_content_frame()
        
        # 创建标题和按钮框架
        ttk.Label(self.content_frame, text="教学工作情况", font=("Arial", 16, "bold")).pack(pady=10)
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=5)
        
        # 添加新记录按钮
        ttk.Button(btn_frame, text="添加教学记录", command=self.add_teaching_record).pack(side=tk.LEFT, padx=5)
        
        # 创建教师列表框架
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建搜索框架
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="搜索教师:").pack(side=tk.LEFT, padx=5)
        self.teaching_search_entry = ttk.Entry(search_frame, width=30)
        self.teaching_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", command=lambda: self.search_teaching(self.teaching_search_entry.get())).pack(side=tk.LEFT, padx=5)
        
        # 创建教师列表
        columns = ("教师ID", "姓名", "任教学科", "班级数量")
        self.teaching_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.teaching_tree.heading(col, text=col)
            self.teaching_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.teaching_tree.yview)
        self.teaching_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teaching_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.teaching_tree.bind("<Double-1>", self.show_teaching_details)
        
        # 加载教师教学数据
        self.load_teaching_data()
    # 加载教师教学数据
    def load_teaching_data(self):
        # 清除现有数据
        for item in self.teaching_tree.get_children():
            self.teaching_tree.delete(item)
        
        # 查询每个教师的教学记录
        self.cursor.execute("""
        SELECT t.teacher_id, t.name, t.teaching_subject,
               COUNT(DISTINCT tr.classes) as class_count
        FROM teacher_info t
        LEFT JOIN teaching_records tr ON t.teacher_id = tr.teacher_id
        GROUP BY t.teacher_id
        """)
        
        teachers = self.cursor.fetchall()
        for teacher in teachers:
            self.teaching_tree.insert("", tk.END, values=teacher)
            
    def search_teaching(self, keyword):
        # 清除现有数据
        for item in self.teaching_tree.get_children():
            self.teaching_tree.delete(item)
        
        # 搜索教师
        self.cursor.execute("""
        SELECT t.teacher_id, t.name, t.teaching_subject,
               COUNT(DISTINCT tr.classes) as class_count
        FROM teacher_info t
        LEFT JOIN teaching_records tr ON t.teacher_id = tr.teacher_id
        WHERE t.name LIKE ? OR t.teaching_subject LIKE ?
        GROUP BY t.teacher_id
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        teachers = self.cursor.fetchall()
        for teacher in teachers:
            self.teaching_tree.insert("", tk.END, values=teacher)
    # 显示教学详细信息
    def show_teaching_details(self, event):
        # 获取选中的教师ID
        try:
            selected_item = self.teaching_tree.selection()[0]
            teacher_id = self.teaching_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择教师")
            return
        
        # 创建新窗口显示教学详细信息
        details_window = tk.Toplevel(self.root)
        details_window.title("教学工作详细信息")
        details_window.geometry("600x400")
        
        # 获取教师基本信息
        self.cursor.execute("SELECT name, teaching_subject FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        teacher_info = self.cursor.fetchone()
        
        # 显示教师信息
        info_frame = ttk.Frame(details_window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text=f"教师姓名：{teacher_info[0]}").pack(side=tk.LEFT, padx=5)
        ttk.Label(info_frame, text=f"任教学科：{teacher_info[1]}").pack(side=tk.LEFT, padx=5)
        
        # 创建班级列表
        list_frame = ttk.Frame(details_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("学年", "学期", "班级", "学生人数", "周课时数")
        class_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            class_tree.heading(col, text=col)
            class_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=class_tree.yview)
        class_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        class_tree.pack(fill=tk.BOTH, expand=True)
        
        # 定义删除班级记录的函数
        def delete_class_record():
            try:
                selected_item = class_tree.selection()[0]
                class_info = class_tree.item(selected_item, "values")
                
                if not messagebox.askyesno("确认删除", f"确定要删除{class_info[2]}班的记录吗？\n此操作不可恢复！"):
                    return
                
                # 从数据库中删除记录
                self.cursor.execute("""
                DELETE FROM teaching_records
                WHERE teacher_id = ? AND academic_year = ? AND semester = ? AND classes = ?
                """, (teacher_id, class_info[0], class_info[1], class_info[2]))
                
                self.conn.commit()
                
                # 从树形视图中删除
                class_tree.delete(selected_item)
                
                messagebox.showinfo("成功", "已删除班级记录")
                
                # 刷新教师列表显示
                self.load_teaching_data()
                
            except IndexError:
                messagebox.showerror("错误", "请先选择要删除的班级记录")
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {e}")
        
        # 加载班级数据
        self.cursor.execute("""
        SELECT academic_year, semester, classes, student_count, weekly_hours
        FROM teaching_records
        WHERE teacher_id = ?
        ORDER BY academic_year DESC, semester DESC
        """, (teacher_id,))
        
        classes = self.cursor.fetchall()
        for class_info in classes:
            class_tree.insert("", tk.END, values=class_info)
        
        # 添加按钮框架
        btn_frame = ttk.Frame(details_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加编辑、删除和关闭按钮
        ttk.Button(btn_frame, text="编辑", command=lambda: self.edit_teaching_record(teacher_id, details_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除班级", command=delete_class_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=details_window.destroy).pack(side=tk.RIGHT, padx=5)
    # 添加教学记录
    def add_teaching_record(self):
        self.edit_teaching_record()
    # 编辑教学记录
    def edit_teaching_record(self, teacher_id=None, parent_window=None):
        # 创建编辑窗口
        edit_window = tk.Toplevel(parent_window if parent_window else self.root)
        edit_window.title("编辑教学记录")
        edit_window.geometry("500x600")
        
        # 如果没有指定教师ID，创建教师选择下拉框
        if not teacher_id:
            teacher_frame = ttk.Frame(edit_window)
            teacher_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(teacher_frame, text="选择教师：").pack(side=tk.LEFT)
            
            # 获取所有教师
            self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
            teachers = self.cursor.fetchall()
            teacher_names = [f"{t[1]}" for t in teachers]
            teacher_ids = [t[0] for t in teachers]
            
            teacher_var = tk.StringVar()
            teacher_combo = ttk.Combobox(teacher_frame, textvariable=teacher_var, values=teacher_names)
            teacher_combo.pack(side=tk.LEFT, padx=5)
        
        # 创建输入框架
        input_frame = ttk.Frame(edit_window)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建学年和学期输入
        ttk.Label(input_frame, text="学年：").grid(row=0, column=0, padx=5, pady=5)
        academic_year = ttk.Entry(input_frame)
        academic_year.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="学期：").grid(row=1, column=0, padx=5, pady=5)
        semester = ttk.Combobox(input_frame, values=["第一学期", "第二学期"])
        semester.grid(row=1, column=1, padx=5, pady=5)
        
        # 创建班级信息列表框架
        class_frame = ttk.LabelFrame(input_frame, text="班级信息")
        class_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # 创建班级信息列表
        class_list = []
        
        def add_class_row():
            row_frame = ttk.Frame(class_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            class_entry = ttk.Entry(row_frame, width=15)
            class_entry.pack(side=tk.LEFT, padx=2)
            ttk.Label(row_frame, text="班级").pack(side=tk.LEFT)
            
            count_entry = ttk.Entry(row_frame, width=8)
            count_entry.pack(side=tk.LEFT, padx=2)
            ttk.Label(row_frame, text="人数").pack(side=tk.LEFT)
            
            hours_entry = ttk.Entry(row_frame, width=8)
            hours_entry.pack(side=tk.LEFT, padx=2)
            ttk.Label(row_frame, text="周课时").pack(side=tk.LEFT)
            
            def delete_class_row():
                if not teacher_id and not teacher_var.get():
                    messagebox.showerror("错误", "请先选择教师")
                    return
                row_frame.destroy()
                class_list.remove(row_data)
                
            del_btn = ttk.Button(row_frame, text="删除", width=8, command=delete_class_row)
            del_btn.pack(side=tk.LEFT, padx=2)
            
            row_data = {"frame": row_frame, "class": class_entry,
                       "count": count_entry, "hours": hours_entry}
            class_list.append(row_data)
        
        # 添加班级按钮
        ttk.Button(class_frame, text="添加班级", command=add_class_row).pack(pady=5)
        
        # 如果是编辑现有记录，加载数据
        if teacher_id:
            self.cursor.execute("""
            SELECT academic_year, semester, classes, student_count, weekly_hours
            FROM teaching_records
            WHERE teacher_id = ?
            ORDER BY academic_year DESC, semester DESC
            """, (teacher_id,))
            
            existing_records = self.cursor.fetchall()
            if existing_records:
                academic_year.insert(0, existing_records[0][0])
                semester.set(existing_records[0][1])
                
                for record in existing_records:
                    add_class_row()
                    class_list[-1]["class"].insert(0, record[2])
                    class_list[-1]["count"].insert(0, str(record[3]))
                    class_list[-1]["hours"].insert(0, str(record[4]))
        
        # 添加保存按钮
        def save_records():
            try:
                # 获取选择的教师ID
                current_teacher_id = teacher_id if teacher_id else teacher_ids[teacher_names.index(teacher_var.get())]
                
                # 验证输入
                if not academic_year.get() or not semester.get() or not class_list:
                    raise ValueError("请填写完整的学年、学期和至少一个班级信息")
                
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                # 删除该教师在该学年学期的所有记录
                self.cursor.execute("""
                DELETE FROM teaching_records
                WHERE teacher_id = ? AND academic_year = ? AND semester = ?
                """, (current_teacher_id, academic_year.get(), semester.get()))
                
                # 插入新记录
                for class_data in class_list:
                    class_name = class_data["class"].get()
                    student_count = class_data["count"].get()
                    weekly_hours = class_data["hours"].get()
                    
                    if not all([class_name, student_count, weekly_hours]):
                        raise ValueError("请填写完整的班级信息")
                    
                    try:
                        student_count = int(student_count)
                        weekly_hours = int(weekly_hours)
                        if student_count <= 0 or weekly_hours <= 0:
                            raise ValueError
                    except ValueError:
                        raise ValueError("人数和周课时必须是正整数")
                    
                    self.cursor.execute("""
                    INSERT INTO teaching_records
                    (record_id, teacher_id, academic_year, semester, classes,
                     student_count, weekly_hours, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (str(uuid.uuid4()), current_teacher_id, academic_year.get(),
                           semester.get(), class_name, student_count, weekly_hours))
                
                # 提交事务
                self.conn.commit()
                
                messagebox.showinfo("成功", "教学记录保存成功")
                edit_window.destroy()
                self.load_teaching_data()
                
                # 如果父窗口存在，刷新其显示
                if parent_window:
                    self.show_teaching_details(None)
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", str(e))
        
        # 添加按钮框架
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="保存", command=save_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=edit_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 添加一个默认的班级行
        if not teacher_id or not existing_records:
            add_class_row()
    # 显示教学工作情况页面
    def show_education_work(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="教育工作情况", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建左侧录入框架
        input_frame = ttk.LabelFrame(main_frame, text="录入教育工作信息")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建录入表单
        # 教师选择
        ttk.Label(input_frame, text="选择教师:").grid(row=0, column=0, padx=5, pady=5)
        self.teacher_combobox = ttk.Combobox(input_frame, width=20)
        self.teacher_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # 学年选择
        ttk.Label(input_frame, text="学年:").grid(row=1, column=0, padx=5, pady=5)
        self.academic_year_entry = ttk.Entry(input_frame, width=20)
        self.academic_year_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 学期选择
        ttk.Label(input_frame, text="学期:").grid(row=2, column=0, padx=5, pady=5)
        self.semester_combobox = ttk.Combobox(input_frame, values=["全部","第一学期", "第二学期"], width=20)
        self.semester_combobox.grid(row=2, column=1, padx=5, pady=5)
        
        # 职务类型输入
        ttk.Label(input_frame, text="职务类型:").grid(row=3, column=0, padx=5, pady=5)
        self.work_type_entry = ttk.Entry(input_frame, width=20)
        self.work_type_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 描述信息
        ttk.Label(input_frame, text="工作描述:").grid(row=4, column=0, padx=5, pady=5)
        self.description_text = tk.Text(input_frame, width=30, height=5)
        self.description_text.grid(row=4, column=1, padx=5, pady=5)
        
        # 添加按钮
        ttk.Button(input_frame, text="保存信息", command=self.save_education_work).grid(row=5, column=0, columnspan=2, pady=10)
        
        # 创建右侧显示框架
        display_frame = ttk.LabelFrame(main_frame, text="教育工作信息列表")
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建筛选框架
        filter_frame = ttk.Frame(display_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="筛选教师:").pack(side=tk.LEFT, padx=5)
        self.filter_teacher = ttk.Combobox(filter_frame, width=10)
        self.filter_teacher.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="筛选学年:").pack(side=tk.LEFT, padx=5)
        self.filter_year = ttk.Entry(filter_frame, width=10)
        self.filter_year.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="筛选学期:").pack(side=tk.LEFT, padx=5)
        self.filter_semester = ttk.Combobox(filter_frame, values=["全部", "第一学期", "第二学期"], width=10)
        self.filter_semester.pack(side=tk.LEFT, padx=5)
        self.filter_semester.set("全部")
        
        ttk.Label(filter_frame, text="职务类型:").pack(side=tk.LEFT, padx=5)
        self.filter_work_type = ttk.Entry(filter_frame, width=10)
        self.filter_work_type.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="筛选", command=self.filter_education_work).pack(side=tk.LEFT, padx=5)
        
        # 创建表格
        columns = ("教师姓名", "学年", "学期", "职务类型", "工作描述")
        self.work_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.work_tree.heading(col, text=col)
            self.work_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.work_tree.yview)
        self.work_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.work_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加删除按钮
        ttk.Button(display_frame, text="删除选中记录", command=self.delete_education_work).pack(pady=5)
        
        # 加载教师列表
        self.load_teacher_list()
        # 加载教育工作数据
        self.load_education_work_data()
        
    def load_teacher_list(self):
        # 从数据库加载教师列表
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
        teachers = self.cursor.fetchall()
        self.teacher_combobox['values'] = [teacher[1] for teacher in teachers]
        self.teacher_dict = {teacher[1]: teacher[0] for teacher in teachers}
    
    def save_education_work(self):
        # 获取输入数据
        teacher_name = self.teacher_combobox.get()
        academic_year = self.academic_year_entry.get()
        semester = self.semester_combobox.get()
        work_type = self.work_type_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        
        # 验证输入
        if not all([teacher_name, academic_year, semester, work_type, description]):
            messagebox.showerror("错误", "请填写所有必填项")
            return
        
        try:
            # 获取教师ID
            teacher_id = self.teacher_dict[teacher_name]
            
            # 生成记录ID
            record_id = str(uuid.uuid4())
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存到数据库
            self.cursor.execute("""
            INSERT INTO education_work 
            (record_id, teacher_id, academic_year, semester, work_type, description, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (record_id, teacher_id, academic_year, semester, work_type, description, current_time, current_time))
            
            self.conn.commit()
            
            # 清空输入框
            self.academic_year_entry.delete(0, tk.END)
            self.semester_combobox.set("")
            self.work_type_entry.delete(0, tk.END)
            self.description_text.delete("1.0", tk.END)
            
            # 刷新显示
            self.load_education_work_data()
            
            messagebox.showinfo("成功", "教育工作信息保存成功")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def load_education_work_data(self, year=None, semester=None, teacher_name=None, work_type=None):
        # 清除现有数据
        for item in self.work_tree.get_children():
            self.work_tree.delete(item)
        
        # 构建查询语句
        query = """
        SELECT t.name, e.academic_year, e.semester, e.work_type, e.description
        FROM education_work e
        JOIN teacher_info t ON e.teacher_id = t.teacher_id
        """
        
        conditions = []
        params = []
        
        if year:
            conditions.append("e.academic_year = ?")
            params.append(year)
        if semester and semester != "全部":
            conditions.append("e.semester = ?")
            params.append(semester)
        if teacher_name:
            conditions.append("t.name LIKE ?")
            params.append(f"%{teacher_name}%")
        if work_type:
            conditions.append("e.work_type LIKE ?")
            params.append(f"%{work_type}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY e.academic_year DESC, e.semester DESC"
        
        # 执行查询
        self.cursor.execute(query, params)
        records = self.cursor.fetchall()
        
        # 显示数据
        for record in records:
            self.work_tree.insert("", tk.END, values=record)
    
    def filter_education_work(self):
        year = self.filter_year.get()
        semester = self.filter_semester.get()
        teacher_name = self.filter_teacher.get()
        work_type = self.filter_work_type.get()
        self.load_education_work_data(year, semester, teacher_name, work_type)
        
    def delete_education_work(self):
        # 获取选中的记录
        selected_item = self.work_tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请先选择要删除的记录")
            return
            
        # 获取选中记录的信息
        item_values = self.work_tree.item(selected_item[0], 'values')
        teacher_name = item_values[0]
        academic_year = item_values[1]
        semester = item_values[2]
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除{teacher_name}在{academic_year}{semester}的教育工作记录吗？\n此操作不可恢复！"):
            return
            
        try:
            # 获取教师ID
            teacher_id = self.teacher_dict[teacher_name]
            
            # 从数据库中删除记录
            self.cursor.execute("""
            DELETE FROM education_work
            WHERE teacher_id = ? AND academic_year = ? AND semester = ?
            """, (teacher_id, academic_year, semester))
            
            self.conn.commit()
            
            # 从树形视图中删除
            self.work_tree.delete(selected_item[0])
            
            messagebox.showinfo("成功", "教育工作记录已删除")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"删除失败: {str(e)}")
    # 荣誉管理
    def show_awards(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="荣誉管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建筛选框架
        filter_frame = ttk.LabelFrame(main_frame, text="筛选条件")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        # 创建筛选条件输入框
        filter_entries = {}
        
        # 第一行筛选条件
        row1_frame = ttk.Frame(filter_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 表彰名称筛选
        ttk.Label(row1_frame, text="表彰名称:").pack(side=tk.LEFT, padx=5)
        filter_entries['award_name'] = ttk.Entry(row1_frame, width=15)
        filter_entries['award_name'].pack(side=tk.LEFT, padx=5)
        
        # 表彰级别筛选
        ttk.Label(row1_frame, text="表彰级别:").pack(side=tk.LEFT, padx=5)
        filter_entries['award_level'] = ttk.Combobox(row1_frame, values=['', '全球级', '国家级', '省级', '市级', '校级'], width=12)
        filter_entries['award_level'].pack(side=tk.LEFT, padx=5)
        
        # 表彰单位筛选
        ttk.Label(row1_frame, text="表彰单位:").pack(side=tk.LEFT, padx=5)
        filter_entries['award_unit'] = ttk.Entry(row1_frame, width=15)
        filter_entries['award_unit'].pack(side=tk.LEFT, padx=5)
        
        # 第二行筛选条件
        row2_frame = ttk.Frame(filter_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 表彰时间筛选
        ttk.Label(row2_frame, text="表彰时间:").pack(side=tk.LEFT, padx=5)
        filter_entries['award_date'] = ttk.Entry(row2_frame, width=15)
        filter_entries['award_date'].pack(side=tk.LEFT, padx=5)
        
        # 获奖教师筛选
        ttk.Label(row2_frame, text="获奖教师:").pack(side=tk.LEFT, padx=5)
        filter_entries['teacher_name'] = ttk.Entry(row2_frame, width=15)
        filter_entries['teacher_name'].pack(side=tk.LEFT, padx=5)

        # 创建筛选按钮
        def apply_filter():
            load_awards(filter_entries)

        ttk.Button(row2_frame, text="筛选", command=apply_filter).pack(side=tk.LEFT, padx=20)
        ttk.Button(row2_frame, text="重置", command=lambda: reset_filter(filter_entries)).pack(side=tk.LEFT)

        def reset_filter(entries):
            for entry in entries.values():
                if isinstance(entry, ttk.Entry):
                    entry.delete(0, tk.END)
                elif isinstance(entry, ttk.Combobox):
                    entry.set('')
            load_awards(entries)
        
        # 创建左侧录入框架
        input_frame = ttk.LabelFrame(main_frame, text="表彰信息录入")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建录入表单
        form_frame = ttk.Frame(input_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 表彰名称
        ttk.Label(form_frame, text="表彰名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        award_name_entry = ttk.Entry(form_frame, width=30)
        award_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 表彰级别
        ttk.Label(form_frame, text="表彰级别:").grid(row=1, column=0, sticky=tk.W, pady=5)
        award_level_combobox = ttk.Combobox(form_frame, values=["全球级", "国家级", "省级", "市级", "校级"], state="readonly")
        award_level_combobox.grid(row=1, column=1, sticky=tk.W, pady=5)
        award_level_combobox.set("校级")
        
        # 表彰单位
        ttk.Label(form_frame, text="表彰单位:").grid(row=2, column=0, sticky=tk.W, pady=5)
        award_unit_entry = ttk.Entry(form_frame, width=30)
        award_unit_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 表彰时间
        ttk.Label(form_frame, text="表彰时间:").grid(row=3, column=0, sticky=tk.W, pady=5)
        award_date_entry = ttk.Entry(form_frame, width=30)
        award_date_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        award_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 获奖教师
        ttk.Label(form_frame, text="获奖教师:").grid(row=4, column=0, sticky=tk.W, pady=5)
        teacher_frame = ttk.Frame(form_frame)
        teacher_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 选择教师按钮
        def select_teacher():
            # 创建选择教师的对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("选择教师")
            dialog.geometry("400x300")
            
            # 创建教师列表
            teacher_listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE)
            teacher_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 加载教师列表
            self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
            teachers = self.cursor.fetchall()
            for teacher in teachers:
                teacher_listbox.insert(tk.END, f"{teacher[1]} (ID: {teacher[0]})")
            
            # 确认选择按钮
            def confirm_selection():
                selected_indices = teacher_listbox.curselection()
                selected_teachers = [teacher_listbox.get(i) for i in selected_indices]
                teacher_var.set(", ".join(selected_teachers))
                dialog.destroy()
            
            ttk.Button(dialog, text="确认", command=confirm_selection).pack(pady=5)
        
        teacher_var = tk.StringVar()
        ttk.Label(teacher_frame, textvariable=teacher_var).pack(side=tk.LEFT)
        ttk.Button(teacher_frame, text="选择教师", command=select_teacher).pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        def save_award():
            # 获取表单数据
            award_name = award_name_entry.get().strip()
            award_level = award_level_combobox.get()
            award_unit = award_unit_entry.get().strip()
            award_date = award_date_entry.get().strip()
            selected_teachers = teacher_var.get().strip()
            
            # 验证数据
            if not all([award_name, award_level, award_unit, award_date, selected_teachers]):
                messagebox.showerror("错误", "请填写所有必填项")
                return
            
            try:
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                # 插入奖项记录
                award_id = str(uuid.uuid4())
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.cursor.execute("""
                INSERT INTO awards (award_id, award_name, award_level, award_unit, award_date, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (award_id, award_name, award_level, award_unit, award_date, current_time, current_time))
                
                # 插入获奖教师关联记录
                for i, teacher_info in enumerate(selected_teachers.split(", ")):
                    teacher_id = teacher_info.split("ID: ")[1].rstrip(")")
                    relation_id = str(uuid.uuid4())
                    
                    self.cursor.execute("""
                    INSERT INTO award_recipients (relation_id, award_id, teacher_id, rank, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (relation_id, award_id, teacher_id, i + 1, current_time, current_time))
                
                # 提交事务
                self.conn.commit()
                
                # 清空表单
                award_name_entry.delete(0, tk.END)
                award_level_combobox.set("校级")
                award_unit_entry.delete(0, tk.END)
                award_date_entry.delete(0, tk.END)
                award_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                teacher_var.set("")
                
                # 刷新列表
                load_awards()
                
                messagebox.showinfo("成功", "表彰信息保存成功")
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"保存失败: {e}")
        
        ttk.Button(form_frame, text="保存", command=save_award).grid(row=5, column=1, sticky=tk.E, pady=10)
        
        # 创建右侧显示框架
        display_frame = ttk.LabelFrame(main_frame, text="表彰信息列表")
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格和按钮框架
        table_frame = ttk.Frame(display_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(display_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建表格
        columns = ("award_id", "表彰名称", "表彰级别", "表彰单位", "表彰时间", "获奖教师")
        award_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        award_tree.heading("award_id", text="ID")
        award_tree.column("award_id", width=0, stretch=False)
        
        for col in columns[1:]:
            award_tree.heading(col, text=col)
            award_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=award_tree.yview)
        award_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        award_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加删除按钮
        def delete_award():
            selected_items = award_tree.selection()
            if not selected_items:
                messagebox.showerror("错误", "请先选择要删除的表彰记录")
                return
            
            if not messagebox.askyesno("确认删除", "确定要删除选中的表彰记录吗？\n此操作不可恢复！"):
                return
            
            try:
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                for item in selected_items:
                    award_id = award_tree.item(item, "values")[0]
                    
                    # 删除获奖记录
                    self.cursor.execute("DELETE FROM award_recipients WHERE award_id = ?", (award_id,))
                    
                    # 删除奖项记录
                    self.cursor.execute("DELETE FROM awards WHERE award_id = ?", (award_id,))
                
                # 提交事务
                self.conn.commit()
                
                # 刷新列表
                load_awards()
                
                messagebox.showinfo("成功", "表彰记录已删除")
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {e}")
        
        ttk.Button(button_frame, text="删除选中", command=delete_award).pack(side=tk.RIGHT, padx=5)
        
        # 加载表彰数据
        def load_awards(filter_entries=None):
            # 清除现有数据
            for item in award_tree.get_children():
                award_tree.delete(item)
            
            # 构建查询条件
            conditions = []
            params = []
            
            if filter_entries:
                if filter_entries['award_name'].get().strip():
                    conditions.append("a.award_name LIKE ?")
                    params.append(f"%{filter_entries['award_name'].get().strip()}%")
                
                if filter_entries['award_level'].get().strip():
                    conditions.append("a.award_level = ?")
                    params.append(filter_entries['award_level'].get().strip())
                
                if filter_entries['award_unit'].get().strip():
                    conditions.append("a.award_unit LIKE ?")
                    params.append(f"%{filter_entries['award_unit'].get().strip()}%")
                
                if filter_entries['award_date'].get().strip():
                    conditions.append("a.award_date LIKE ?")
                    params.append(f"%{filter_entries['award_date'].get().strip()}%")
                
                if filter_entries['teacher_name'].get().strip():
                    conditions.append("t.name LIKE ?")
                    params.append(f"%{filter_entries['teacher_name'].get().strip()}%")
            
            # 构建SQL查询
            query = """
            SELECT a.award_id, a.award_name, a.award_level, a.award_unit, a.award_date, GROUP_CONCAT(t.name) as teachers
            FROM awards a
            LEFT JOIN award_recipients ar ON a.award_id = ar.award_id
            LEFT JOIN teacher_info t ON ar.teacher_id = t.teacher_id
            """
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
            GROUP BY a.award_id
            ORDER BY 
                CASE a.award_level
                    WHEN '全球级' THEN 1
                    WHEN '国家级' THEN 2
                    WHEN '省级' THEN 3
                    WHEN '市级' THEN 4
                    WHEN '校级' THEN 5
                    ELSE 6
                END,
                a.award_date DESC
            """
            
            # 执行查询
            self.cursor.execute(query, params)
            awards = self.cursor.fetchall()
            
            for award in awards:
                award_tree.insert("", tk.END, values=award)
        
        # 初始加载数据
        load_awards()
    #教学比武获奖
    def show_teachingfight_records(self):
        self.clear_content_frame()
        
        # 创建标题
        ttk.Label(self.content_frame, text="教学比武获奖", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建筛选框架
        filter_frame = ttk.LabelFrame(main_frame, text="筛选条件")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建筛选条件
        ttk.Label(filter_frame, text="教师姓名:").grid(row=0, column=0, padx=5, pady=5)
        name_filter = ttk.Entry(filter_frame)
        name_filter.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="获奖名称:").grid(row=0, column=2, padx=5, pady=5)
        award_filter = ttk.Entry(filter_frame)
        award_filter.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="获奖级别:").grid(row=0, column=4, padx=5, pady=5)
        level_filter = ttk.Combobox(filter_frame, values=["", "全球级", "国家级", "省级", "市级", "校级"], state="readonly")
        level_filter.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="获奖时间:").grid(row=0, column=6, padx=5, pady=5)
        date_filter = ttk.Entry(filter_frame)
        date_filter.grid(row=0, column=7, padx=5, pady=5)
        
        # 创建左侧录入框架
        input_frame = ttk.LabelFrame(main_frame, text="录入获奖信息")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建录入表单
        ttk.Label(input_frame, text="获奖名称:").grid(row=0, column=0, padx=5, pady=5)
        award_name_entry = ttk.Entry(input_frame)
        award_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="获奖级别:").grid(row=1, column=0, padx=5, pady=5)
        award_level_combobox = ttk.Combobox(input_frame, values=["全球级", "国家级", "省级", "市级", "校级"], state="readonly")
        award_level_combobox.grid(row=1, column=1, padx=5, pady=5)
        award_level_combobox.set("校级")
        
        ttk.Label(input_frame, text="获奖时间:").grid(row=2, column=0, padx=5, pady=5)
        award_date_entry = ttk.Entry(input_frame)
        award_date_entry.grid(row=2, column=1, padx=5, pady=5)
        award_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 创建右侧显示框架
        display_frame = ttk.LabelFrame(main_frame, text="获奖记录")
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建教师选择框架
        teacher_frame = ttk.Frame(input_frame)
        teacher_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(teacher_frame, text="选择教师:").pack(side=tk.LEFT, padx=5)
        teacher_combobox = ttk.Combobox(teacher_frame, state="readonly")
        teacher_combobox.pack(side=tk.LEFT, padx=5)
        
        # 加载教师列表
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
        teachers = self.cursor.fetchall()
        teacher_combobox['values'] = [f"{t[1]}" for t in teachers]
        teacher_dict = {t[1]: t[0] for t in teachers}
        
        # 创建表格显示获奖记录
        columns = ("教师姓名", "获奖名称", "获奖级别", "获奖时间")
        award_tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        
        for col in columns:
            award_tree.heading(col, text=col)
            award_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=award_tree.yview)
        award_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        award_tree.pack(fill=tk.BOTH, expand=True)
        
        def load_awards():
            # 清除现有数据
            for item in award_tree.get_children():
                award_tree.delete(item)
            
            # 构建查询条件
            conditions = ["a.award_type = '教学比武'"]
            params = []
            
            if name_filter.get().strip():
                conditions.append("t.name LIKE ?")
                params.append(f'%{name_filter.get().strip()}%')
            
            if award_filter.get().strip():
                conditions.append("a.award_name LIKE ?")
                params.append(f'%{award_filter.get().strip()}%')
            
            if level_filter.get():
                conditions.append("a.award_level = ?")
                params.append(level_filter.get())
            
            if date_filter.get().strip():
                conditions.append("a.award_date LIKE ?")
                params.append(f'%{date_filter.get().strip()}%')
            
            # 构建SQL查询
            query = """
                SELECT t.name, a.award_name, a.award_level, a.award_date, a.award_id
                FROM awards a 
                JOIN award_recipients ar ON a.award_id = ar.award_id 
                JOIN teacher_info t ON ar.teacher_id = t.teacher_id 
                WHERE " + " AND ".join(conditions) + "
                ORDER BY 
                    CASE a.award_level 
                        WHEN '全球级' THEN 1 
                        WHEN '国家级' THEN 2 
                        WHEN '省级' THEN 3 
                        WHEN '市级' THEN 4 
                        WHEN '校级' THEN 5 
                        ELSE 6 
                    END
            """
            
            # 执行查询
            self.cursor.execute(query, params)
            awards = self.cursor.fetchall()
            
            for award in awards:
                award_tree.insert("", tk.END, values=award[:-1], tags=(award[-1],))
        
        def save_award():
            # 获取输入数据
            award_name = award_name_entry.get().strip()
            award_level = award_level_combobox.get()
            award_date = award_date_entry.get().strip()
            teacher_name = teacher_combobox.get()
            
            # 验证输入
            if not all([award_name, award_level, award_date, teacher_name]):
                messagebox.showerror("错误", "请填写所有必填项")
                return
            
            try:
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                # 插入奖项记录
                award_id = str(uuid.uuid4())
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.cursor.execute("""
                    INSERT INTO awards (award_id, award_name, award_level, award_date, award_type, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (award_id, award_name, award_level, award_date, "教学比武", current_time, current_time))
                
                # 插入获奖人员关联记录
                relation_id = str(uuid.uuid4())
                teacher_id = teacher_dict[teacher_name]
                
                self.cursor.execute("""
                    INSERT INTO award_recipients (relation_id, award_id, teacher_id, rank, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (relation_id, award_id, teacher_id, 1, current_time, current_time))
                
                # 提交事务
                self.conn.commit()
                messagebox.showinfo("成功", "获奖记录已保存")
                
                # 清空输入框
                award_name_entry.delete(0, tk.END)
                award_level_combobox.set("校级")
                award_date_entry.delete(0, tk.END)
                award_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                teacher_combobox.set("")
                
                # 刷新显示
                load_awards()
                
            except Exception as e:
                # 发生错误时回滚事务
                self.conn.rollback()
                messagebox.showerror("错误", f"保存失败: {e}")
        
        def delete_award():
            # 检查是否选择了记录
            selected_item = award_tree.selection()
            if not selected_item:
                messagebox.showerror("错误", "请先选择要删除的记录")
                return
            
            # 获取选中记录的信息
            award_id = award_tree.item(selected_item[0], "tags")[0]
            award_values = award_tree.item(selected_item[0], "values")
            
            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除教师 {award_values[0]} 的 {award_values[1]} 获奖记录吗？\n此操作不可恢复！"):
                return
            
            try:
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                # 删除获奖人员关联记录
                self.cursor.execute("DELETE FROM award_recipients WHERE award_id = ?", (award_id,))
                
                # 删除奖项记录
                self.cursor.execute("DELETE FROM awards WHERE award_id = ?", (award_id,))
                
                # 提交事务
                self.conn.commit()
                
                # 从树形视图中移除
                award_tree.delete(selected_item[0])
                
                messagebox.showinfo("成功", "已删除获奖记录")
                
            except Exception as e:
                # 发生错误时回滚事务
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {e}")
        
        # 创建按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 添加保存和删除按钮
        ttk.Button(button_frame, text="保存", command=save_award).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=delete_award).pack(side=tk.LEFT, padx=5)
        
        # 绑定筛选条件变化事件
        def on_filter_change(*args):
            load_awards()
        
        name_filter.bind('<KeyRelease>', on_filter_change)
        award_filter.bind('<KeyRelease>', on_filter_change)
        level_filter.bind('<<ComboboxSelected>>', on_filter_change)
        date_filter.bind('<KeyRelease>', on_filter_change)
        
        # 初始加载获奖记录
        load_awards()
    #公开课管理
    def show_public_lessons(self):
        self.clear_content_frame()
        
        # 创建标题
        ttk.Label(self.content_frame, text="公开课管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建录入框架
        input_frame = ttk.LabelFrame(self.content_frame, text="录入公开课信息")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建录入表单
        ttk.Label(input_frame, text="教师:").grid(row=0, column=0, padx=5, pady=5)
        teacher_combobox = ttk.Combobox(input_frame, width=20)
        teacher_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="公开课名称:").grid(row=0, column=2, padx=5, pady=5)
        lesson_name_entry = ttk.Entry(input_frame, width=30)
        lesson_name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="开设范围:").grid(row=1, column=0, padx=5, pady=5)
        scope_combobox = ttk.Combobox(input_frame, width=20, values=["校级", "区级", "市级", "省级", "国家级"])
        scope_combobox.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="开设时间:").grid(row=1, column=2, padx=5, pady=5)
        lesson_date_entry = ttk.Entry(input_frame, width=30)
        lesson_date_entry.grid(row=1, column=3, padx=5, pady=5)
        lesson_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 加载教师列表
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
        teachers = self.cursor.fetchall()
        teacher_combobox['values'] = [f"{t[1]}" for t in teachers]
        teacher_dict = {t[1]: t[0] for t in teachers}
        
        # 创建保存按钮
        def save_lesson():
            # 获取输入值
            teacher_name = teacher_combobox.get()
            lesson_name = lesson_name_entry.get()
            scope = scope_combobox.get()
            lesson_date = lesson_date_entry.get()
            
            # 验证输入
            if not all([teacher_name, lesson_name, scope, lesson_date]):
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            try:
                # 获取教师ID
                teacher_id = teacher_dict[teacher_name]
                
                # 生成记录ID
                lesson_id = str(uuid.uuid4())
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 保存到数据库
                self.cursor.execute("""
                INSERT INTO public_lessons 
                (lesson_id, teacher_id, lesson_name, lesson_scope, lesson_date, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (lesson_id, teacher_id, lesson_name, scope, lesson_date, current_time, current_time))
                
                self.conn.commit()
                messagebox.showinfo("成功", "公开课信息已保存")
                
                # 清空输入框
                lesson_name_entry.delete(0, tk.END)
                scope_combobox.set('')
                lesson_date_entry.delete(0, tk.END)
                lesson_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                
                # 刷新列表
                load_lessons()
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(input_frame, text="保存", command=save_lesson).grid(row=1, column=4, padx=10, pady=5)
        
        # 创建筛选框架
        filter_frame = ttk.LabelFrame(self.content_frame, text="筛选条件")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加筛选条件
        ttk.Label(filter_frame, text="教师姓名:").grid(row=0, column=0, padx=5, pady=5)
        filter_teacher = ttk.Entry(filter_frame, width=15)
        filter_teacher.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="公开课名称:").grid(row=0, column=2, padx=5, pady=5)
        filter_lesson = ttk.Entry(filter_frame, width=15)
        filter_lesson.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="开设范围:").grid(row=0, column=4, padx=5, pady=5)
        filter_scope = ttk.Combobox(filter_frame, width=12, values=["", "校级", "区级", "市级", "省级", "国家级"])
        filter_scope.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="开设时间:").grid(row=0, column=6, padx=5, pady=5)
        filter_date = ttk.Entry(filter_frame, width=15)
        filter_date.grid(row=0, column=7, padx=5, pady=5)
        
        # 创建列表框架
        list_frame = ttk.LabelFrame(self.content_frame, text="公开课列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ("教师", "公开课名称", "开设范围", "开设时间")
        lesson_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            lesson_tree.heading(col, text=col)
            lesson_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=lesson_tree.yview)
        lesson_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lesson_tree.pack(fill=tk.BOTH, expand=True)
        
        # 加载公开课列表
        def load_lessons():
            # 清除现有数据
            for item in lesson_tree.get_children():
                lesson_tree.delete(item)
            
            # 构建查询条件
            conditions = []
            params = []
            
            if filter_teacher.get().strip():
                conditions.append("t.name LIKE ?")
                params.append(f"%{filter_teacher.get().strip()}%")
            
            if filter_lesson.get().strip():
                conditions.append("p.lesson_name LIKE ?")
                params.append(f"%{filter_lesson.get().strip()}%")
            
            if filter_scope.get():
                conditions.append("p.lesson_scope = ?")
                params.append(filter_scope.get())
            
            if filter_date.get().strip():
                conditions.append("p.lesson_date LIKE ?")
                params.append(f"%{filter_date.get().strip()}%")
            
            # 构建SQL查询
            query = """
            SELECT t.name, p.lesson_name, p.lesson_scope, p.lesson_date 
            FROM public_lessons p 
            JOIN teacher_info t ON p.teacher_id = t.teacher_id
            """
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.lesson_date DESC"
            
            # 执行查询
            self.cursor.execute(query, params)
            lessons = self.cursor.fetchall()
            
            # 添加到表格
            for lesson in lessons:
                lesson_tree.insert("", tk.END, values=lesson)
        
        # 绑定筛选条件变化事件
        def on_filter_change(*args):
            load_lessons()
        
        filter_teacher.bind('<KeyRelease>', on_filter_change)
        filter_lesson.bind('<KeyRelease>', on_filter_change)
        filter_scope.bind('<<ComboboxSelected>>', on_filter_change)
        filter_date.bind('<KeyRelease>', on_filter_change)
        
        # 定义删除公开课记录的函数
        def delete_lesson():
            try:
                selected_item = lesson_tree.selection()[0]
                lesson_info = lesson_tree.item(selected_item, "values")
                
                if not messagebox.askyesno("确认删除", f"确定要删除{lesson_info[0]}老师的{lesson_info[1]}公开课记录吗？\n此操作不可恢复！"):
                    return
                
                # 从数据库中删除记录
                self.cursor.execute("""
                DELETE FROM public_lessons
                WHERE teacher_id = (SELECT teacher_id FROM teacher_info WHERE name = ?)
                AND lesson_name = ? AND lesson_scope = ? AND lesson_date = ?
                """, (lesson_info[0], lesson_info[1], lesson_info[2], lesson_info[3]))
                
                self.conn.commit()
                
                # 从树形视图中删除
                lesson_tree.delete(selected_item)
                
                messagebox.showinfo("成功", "已删除公开课记录")
                
            except IndexError:
                messagebox.showerror("错误", "请先选择要删除的公开课记录")
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {e}")
        
        # 添加删除按钮
        ttk.Button(input_frame, text="删除", command=delete_lesson).grid(row=1, column=5, padx=10, pady=5)
        
        # 初始加载数据
        load_lessons()
    #论文管理
    def show_papers(self):
        self.clear_content_frame()
        
        # 创建标题和按钮框架
        ttk.Label(self.content_frame, text="论文发表情况", font=("Arial", 16, "bold")).pack(pady=10)
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=5)
        
        # 添加新记录按钮
        ttk.Button(btn_frame, text="添加论文记录", command=self.add_paper_record).pack(side=tk.LEFT, padx=5)
        
        # 创建教师列表框架
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建搜索框架
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="搜索教师:").pack(side=tk.LEFT, padx=5)
        self.paper_search_entry = ttk.Entry(search_frame, width=30)
        self.paper_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", command=lambda: self.search_papers(self.paper_search_entry.get())).pack(side=tk.LEFT, padx=5)
        
        # 创建论文列表
        columns = ("教师ID", "教师姓名", "论文数量")
        self.papers_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        for col in columns:
            self.papers_tree.heading(col, text=col)
            self.papers_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.papers_tree.yview)
        self.papers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.papers_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.papers_tree.bind("<Double-1>", self.on_paper_selected)
        
        # 加载论文数据
        self.load_papers_data()
    
    # 加载论文数据
    def load_papers_data(self):
        # 清除现有数据
        for item in self.papers_tree.get_children():
            self.papers_tree.delete(item)
        
        # 查询每个教师的论文数量
        self.cursor.execute("""
        SELECT t.teacher_id, t.name, COUNT(p.paper_id) as paper_count
        FROM teacher_info t
        LEFT JOIN papers p ON t.teacher_id = p.teacher_id
        GROUP BY t.teacher_id, t.name
        ORDER BY t.name
        """)
        
        teachers_papers = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for teacher in teachers_papers:
            self.papers_tree.insert("", tk.END, values=teacher)
    
    # 搜索论文
    def search_papers(self, keyword):
        # 清除现有数据
        for item in self.papers_tree.get_children():
            self.papers_tree.delete(item)
        
        # 搜索教师及其论文
        self.cursor.execute("""
        SELECT t.teacher_id, t.name, COUNT(p.paper_id) as paper_count
        FROM teacher_info t
        LEFT JOIN papers p ON t.teacher_id = p.teacher_id
        WHERE t.name LIKE ? OR t.id_number LIKE ?
        GROUP BY t.teacher_id, t.name
        ORDER BY t.name
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        teachers_papers = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for teacher in teachers_papers:
            self.papers_tree.insert("", tk.END, values=teacher)
    
    # 双击论文记录事件
    def on_paper_selected(self, event):
        # 获取选中的教师ID
        selected_item = self.papers_tree.selection()[0]
        teacher_id = self.papers_tree.item(selected_item, "values")[0]
        teacher_name = self.papers_tree.item(selected_item, "values")[1]
        
        # 显示教师论文详情
        self.show_teacher_papers(teacher_id, teacher_name)
    
    # 显示教师论文详情
    def show_teacher_papers(self, teacher_id, teacher_name):
        # 创建新窗口显示教师论文详情
        papers_window = tk.Toplevel(self.root)
        papers_window.title(f"{teacher_name}的论文情况")
        papers_window.geometry("800x500")
        
        # 创建标题和按钮框架
        header_frame = ttk.Frame(papers_window)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text=f"{teacher_name}的论文情况", font=("Arial", 14, "bold")).pack(side=tk.LEFT, pady=5)
        ttk.Button(header_frame, text="添加论文", command=lambda: self.add_paper_record(teacher_id, papers_window)).pack(side=tk.RIGHT, padx=5)
        
        # 添加删除按钮
        def delete_selected_paper():
            try:
                selected_item = papers_tree.selection()[0]
                paper_id = papers_tree.item(selected_item, "values")[0]
                paper_title = papers_tree.item(selected_item, "values")[1]
                
                if messagebox.askyesno("确认删除", f"确定要删除论文《{paper_title}》吗？"):
                    try:
                        self.cursor.execute("DELETE FROM papers WHERE paper_id = ?", (paper_id,))
                        self.conn.commit()
                        messagebox.showinfo("成功", "论文记录已删除")
                        papers_tree.delete(selected_item)
                    except Exception as e:
                        self.conn.rollback()
                        messagebox.showerror("错误", f"删除失败: {e}")
            except IndexError:
                messagebox.showerror("错误", "请先选择要删除的论文")
        
        ttk.Button(header_frame, text="删除论文", command=delete_selected_paper).pack(side=tk.RIGHT, padx=5)
        
        # 创建论文列表
        columns = ("论文ID", "论文标题", "发表期刊", "论文级别", "发表时间")
        papers_tree = ttk.Treeview(papers_window, columns=columns, show="headings")
        
        # 设置列标题和宽度
        papers_tree.heading("论文ID", text="论文ID")
        papers_tree.column("论文ID", width=80)
        papers_tree.heading("论文标题", text="论文标题")
        papers_tree.column("论文标题", width=250)
        papers_tree.heading("发表期刊", text="发表期刊")
        papers_tree.column("发表期刊", width=150)
        papers_tree.heading("论文级别", text="论文级别")
        papers_tree.column("论文级别", width=100)
        papers_tree.heading("发表时间", text="发表时间")
        papers_tree.column("发表时间", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(papers_window, orient=tk.VERTICAL, command=papers_tree.yview)
        papers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        papers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 绑定双击事件
        papers_tree.bind("<Double-1>", lambda event, t_id=teacher_id, tree=papers_tree, win=papers_window: 
                        self.edit_paper(event, t_id, tree, win))
        
        # 加载教师论文数据
        self.cursor.execute("""
        SELECT paper_id, paper_title, journal_name, paper_level, publish_date
        FROM papers
        WHERE teacher_id = ?
        ORDER BY publish_date DESC
        """, (teacher_id,))
        
        papers = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for paper in papers:
            papers_tree.insert("", tk.END, values=paper)
    
    # 添加论文记录
    def add_paper_record(self, teacher_id=None, parent_window=None):
        if teacher_id is None:
            # 如果没有指定教师ID，则打开教师选择窗口
            self.select_teacher_for_paper()
            return
        
        # 创建添加论文窗口
        paper_window = tk.Toplevel(parent_window if parent_window else self.root)
        paper_window.title("添加论文记录")
        paper_window.geometry("500x400")
        
        # 创建表单框架
        form_frame = ttk.Frame(paper_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加表单字段
        ttk.Label(form_frame, text="论文标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        paper_title_entry = ttk.Entry(form_frame, width=40)
        paper_title_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="发表期刊:").grid(row=1, column=0, sticky=tk.W, pady=5)
        journal_name_entry = ttk.Entry(form_frame, width=40)
        journal_name_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text="论文级别:").grid(row=2, column=0, sticky=tk.W, pady=5)
        paper_level_combo = ttk.Combobox(form_frame, values=["国家级", "省级", "市级", "校级", "其他"])
        paper_level_combo.grid(row=2, column=1, pady=5)
        
        ttk.Label(form_frame, text="发表时间:").grid(row=3, column=0, sticky=tk.W, pady=5)
        publish_date_entry = ttk.Entry(form_frame, width=40)
        publish_date_entry.grid(row=3, column=1, pady=5)
        publish_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 添加保存按钮
        def save_paper():
            # 获取表单数据
            paper_title = paper_title_entry.get().strip()
            journal_name = journal_name_entry.get().strip()
            paper_level = paper_level_combo.get()
            publish_date = publish_date_entry.get().strip()
            
            # 验证数据
            if not paper_title:
                messagebox.showerror("错误", "请输入论文标题")
                return
            
            # 生成唯一ID
            paper_id = str(uuid.uuid4())
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # 插入数据
                self.cursor.execute("""
                INSERT INTO papers (paper_id, teacher_id, paper_title, journal_name, paper_level, publish_date, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (paper_id, teacher_id, paper_title, journal_name, paper_level, publish_date, current_time, current_time))
                
                self.conn.commit()
                messagebox.showinfo("成功", "论文记录已添加")
                
                # 关闭窗口
                paper_window.destroy()
                
                # 刷新论文列表
                if parent_window:
                    self.show_teacher_papers(teacher_id, self.get_teacher_name(teacher_id))
                else:
                    self.load_papers_data()
                    
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"添加失败: {e}")
        
        # 添加按钮框架
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="保存", command=save_paper).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=paper_window.destroy).pack(side=tk.LEFT, padx=10)
    
    # 选择教师添加论文
    def select_teacher_for_paper(self):
        # 创建教师选择窗口
        select_window = tk.Toplevel(self.root)
        select_window.title("选择教师")
        select_window.geometry("600x400")
        
        # 创建搜索框架
        search_frame = ttk.Frame(select_window, padding=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="搜索教师:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # 创建教师列表
        columns = ("教师ID", "姓名", "性别", "任教学科")
        teacher_tree = ttk.Treeview(select_window, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            teacher_tree.heading(col, text=col)
            teacher_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(select_window, orient=tk.VERTICAL, command=teacher_tree.yview)
        teacher_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        teacher_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 加载教师数据
        self.cursor.execute("SELECT teacher_id, name, gender, teaching_subject FROM teacher_info ORDER BY name")
        teachers = self.cursor.fetchall()
        
        for teacher in teachers:
            teacher_tree.insert("", tk.END, values=teacher)
        
        # 搜索功能
        def search_teacher():
            keyword = search_entry.get().strip()
            
            # 清除现有数据
            for item in teacher_tree.get_children():
                teacher_tree.delete(item)
            
            # 搜索教师
            self.cursor.execute("""
            SELECT teacher_id, name, gender, teaching_subject 
            FROM teacher_info 
            WHERE name LIKE ? OR id_number LIKE ?
            ORDER BY name
            """, (f'%{keyword}%', f'%{keyword}%'))
            
            teachers = self.cursor.fetchall()
            
            for teacher in teachers:
                teacher_tree.insert("", tk.END, values=teacher)
        
        ttk.Button(search_frame, text="搜索", command=search_teacher).pack(side=tk.LEFT, padx=5)
        
        # 选择教师
        def select_teacher():
            try:
                selected_item = teacher_tree.selection()[0]
                teacher_id = teacher_tree.item(selected_item, "values")[0]
                teacher_name = teacher_tree.item(selected_item, "values")[1]
                
                select_window.destroy()
                self.add_paper_record(teacher_id)
                
            except IndexError:
                messagebox.showerror("错误", "请选择一名教师")
        
        # 添加按钮框架
        btn_frame = ttk.Frame(select_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="选择", command=select_teacher).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=select_window.destroy).pack(side=tk.LEFT, padx=10)
    
    # 编辑论文
    def edit_paper(self, event, teacher_id, tree, parent_window):
        try:
            selected_item = tree.selection()[0]
            paper_id = tree.item(selected_item, "values")[0]
            
            # 获取论文数据
            self.cursor.execute("""
            SELECT paper_title, journal_name, paper_level, publish_date
            FROM papers
            WHERE paper_id = ?
            """, (paper_id,))
            
            paper_data = self.cursor.fetchone()
            
            if not paper_data:
                messagebox.showerror("错误", "未找到论文数据")
                return
            
            # 创建编辑窗口
            edit_window = tk.Toplevel(parent_window)
            edit_window.title("编辑论文记录")
            edit_window.geometry("500x400")
            
            # 创建表单框架
            form_frame = ttk.Frame(edit_window, padding=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            # 添加表单字段
            ttk.Label(form_frame, text="论文标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
            paper_title_entry = ttk.Entry(form_frame, width=40)
            paper_title_entry.grid(row=0, column=1, pady=5)
            paper_title_entry.insert(0, paper_data[0])
            
            ttk.Label(form_frame, text="发表期刊:").grid(row=1, column=0, sticky=tk.W, pady=5)
            journal_name_entry = ttk.Entry(form_frame, width=40)
            journal_name_entry.grid(row=1, column=1, pady=5)
            journal_name_entry.insert(0, paper_data[1] if paper_data[1] else "")
            
            ttk.Label(form_frame, text="论文级别:").grid(row=2, column=0, sticky=tk.W, pady=5)
            paper_level_combo = ttk.Combobox(form_frame, values=["国家级", "省级", "市级", "校级", "其他"])
            paper_level_combo.grid(row=2, column=1, pady=5)
            if paper_data[2]:
                paper_level_combo.set(paper_data[2])
            
            ttk.Label(form_frame, text="发表时间:").grid(row=3, column=0, sticky=tk.W, pady=5)
            publish_date_entry = ttk.Entry(form_frame, width=40)
            publish_date_entry.grid(row=3, column=1, pady=5)
            publish_date_entry.insert(0, paper_data[3] if paper_data[3] else datetime.now().strftime("%Y-%m-%d"))
            
            # 添加保存按钮
            def update_paper():
                # 获取表单数据
                paper_title = paper_title_entry.get().strip()
                journal_name = journal_name_entry.get().strip()
                paper_level = paper_level_combo.get()
                publish_date = publish_date_entry.get().strip()
                
                # 验证数据
                if not paper_title:
                    messagebox.showerror("错误", "请输入论文标题")
                    return
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                try:
                    # 更新数据
                    self.cursor.execute("""
                    UPDATE papers
                    SET paper_title = ?, journal_name = ?, paper_level = ?, publish_date = ?, update_time = ?
                    WHERE paper_id = ?
                    """, (paper_title, journal_name, paper_level, publish_date, current_time, paper_id))
                    
                    self.conn.commit()
                    messagebox.showinfo("成功", "论文记录已更新")
                    
                    # 关闭窗口
                    edit_window.destroy()
                    
                    # 刷新论文列表
                    self.show_teacher_papers(teacher_id, self.get_teacher_name(teacher_id))
                        
                except Exception as e:
                    self.conn.rollback()
                    messagebox.showerror("错误", f"更新失败: {e}")
            
            # 添加删除按钮功能
            def delete_paper():
                if messagebox.askyesno("确认删除", "确定要删除这条论文记录吗？"):
                    try:
                        self.cursor.execute("DELETE FROM papers WHERE paper_id = ?", (paper_id,))
                        self.conn.commit()
                        messagebox.showinfo("成功", "论文记录已删除")
                        edit_window.destroy()
                        self.show_teacher_papers(teacher_id, self.get_teacher_name(teacher_id))
                    except Exception as e:
                        self.conn.rollback()
                        messagebox.showerror("错误", f"删除失败: {e}")
            
            # 添加按钮框架
            btn_frame = ttk.Frame(form_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
            
            ttk.Button(btn_frame, text="保存", command=update_paper).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="删除", command=delete_paper).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="取消", command=edit_window.destroy).pack(side=tk.LEFT, padx=10)
            
        except IndexError:
            messagebox.showerror("错误", "请选择一条论文记录")
    
    # 获取教师姓名
    def get_teacher_name(self, teacher_id):
        self.cursor.execute("SELECT name FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "未知教师"
    # 显示课题解题管理页面
    def show_research_projects(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="课题结题管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧课题列表框架
        list_frame = ttk.Frame(main_frame, width=600)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建右侧操作框架
        action_frame = ttk.Frame(main_frame, width=400)
        action_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # 在右侧框架添加新增课题按钮
        ttk.Button(action_frame, text="新增课题", command=self.add_research_project).pack(pady=10, fill=tk.X)
        
        # 创建搜索框架
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="搜索课题:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", command=lambda: self.search_projects(search_entry.get())).pack(side=tk.LEFT, padx=5)
        
        # 创建课题列表
        columns = ("课题ID", "课题名称", "课题级别", "结题时间", "主持人")
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        self.project_tree.heading("课题ID", text="课题ID")
        self.project_tree.column("课题ID", width=80)
        self.project_tree.heading("课题名称", text="课题名称")
        self.project_tree.column("课题名称", width=200)
        self.project_tree.heading("课题级别", text="课题级别")
        self.project_tree.column("课题级别", width=80)
        self.project_tree.heading("结题时间", text="结题时间")
        self.project_tree.column("结题时间", width=100)
        self.project_tree.heading("主持人", text="主持人")
        self.project_tree.column("主持人", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.project_tree.bind("<Double-1>", self.edit_research_project)
        
        # 加载课题数据
        self.load_research_projects()

    def add_research_project(self, project_data=None):
        # 创建新窗口
        project_window = tk.Toplevel(self.root)
        project_window.title("添加课题")
        project_window.geometry("600x500")
        
        # 创建表单框架
        form_frame = ttk.Frame(project_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 课题名称
        ttk.Label(form_frame, text="课题名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # 课题级别
        ttk.Label(form_frame, text="课题级别:").grid(row=1, column=0, sticky=tk.W, pady=5)
        level_combobox = ttk.Combobox(form_frame, values=["校级", "市级", "省级", "国家级"], width=37)
        level_combobox.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # 结题时间
        ttk.Label(form_frame, text="结题时间:").grid(row=2, column=0, sticky=tk.W, pady=5)
        completion_entry = ttk.Entry(form_frame, width=40)
        completion_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)
        completion_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 主持人选择
        ttk.Label(form_frame, text="主持人:").grid(row=3, column=0, sticky=tk.W, pady=5)
        leader_combobox = ttk.Combobox(form_frame, width=37)
        leader_combobox.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # 获取所有教师列表
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
        teachers = self.cursor.fetchall()
        teacher_list = [f"{t[1]}" for t in teachers]
        teacher_ids = [t[0] for t in teachers]
        leader_combobox['values'] = teacher_list
        
        # 核心成员选择
        ttk.Label(form_frame, text="核心成员:").grid(row=4, column=0, sticky=tk.W, pady=5)
        members_listbox = tk.Listbox(form_frame, selectmode=tk.MULTIPLE, width=40, height=6)
        members_listbox.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)
        for teacher in teacher_list:
            members_listbox.insert(tk.END, teacher)
        
        # 保存按钮
        def save_project():
            # 获取表单数据
            project_name = name_entry.get().strip()
            project_level = level_combobox.get().strip()
            completion_date = completion_entry.get().strip()
            leader_index = teacher_list.index(leader_combobox.get())
            leader_id = teacher_ids[leader_index]
            
            # 验证必填字段
            if not all([project_name, project_level, completion_date, leader_combobox.get()]):
                messagebox.showerror("错误", "请填写所有必填字段")
                return
            
            try:
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                # 生成项目ID
                project_id = str(uuid.uuid4())
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 插入课题信息
                self.cursor.execute("""
                INSERT INTO research_projects 
                (project_id, project_name, project_level, completion_date, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (project_id, project_name, project_level, completion_date, current_time, current_time))
                
                # 插入主持人信息
                self.cursor.execute("""
                INSERT INTO project_members 
                (relation_id, project_id, teacher_id, is_leader, member_rank, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), project_id, leader_id, True, 1, current_time, current_time))
                
                # 插入核心成员信息
                selected_indices = members_listbox.curselection()
                for rank, idx in enumerate(selected_indices, start=2):
                    if teacher_list[idx] != leader_combobox.get():  # 避免重复添加主持人
                        member_id = teacher_ids[idx]
                        self.cursor.execute("""
                        INSERT INTO project_members 
                        (relation_id, project_id, teacher_id, is_leader, member_rank, create_time, update_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (str(uuid.uuid4()), project_id, member_id, False, rank, current_time, current_time))
                
                # 提交事务
                self.conn.commit()
                messagebox.showinfo("成功", "课题信息保存成功")
                project_window.destroy()
                self.load_research_projects()  # 刷新课题列表
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(form_frame, text="保存", command=save_project).grid(row=5, column=1, pady=20)
        ttk.Button(form_frame, text="取消", command=project_window.destroy).grid(row=5, column=2, pady=20)
        
        if project_data:
            # 如果是编辑模式，填充现有数据
            name_entry.insert(0, project_data['project_name'])
            level_combobox.set(project_data['project_level'])
            completion_entry.insert(0, project_data['completion_date'])
            leader_combobox.set(project_data['leader_name'])
            
            # 选择核心成员
            for member in project_data['members']:
                if member in teacher_list:
                    idx = teacher_list.index(member)
                    members_listbox.selection_set(idx)
    
    def load_research_projects(self):
        # 清除现有数据
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # 查询课题信息，包括主持人姓名
        self.cursor.execute("""
        SELECT rp.project_id, rp.project_name, rp.project_level, rp.completion_date, 
               ti.name as leader_name
        FROM research_projects rp
        LEFT JOIN project_members pm ON rp.project_id = pm.project_id AND pm.is_leader = 1
        LEFT JOIN teacher_info ti ON pm.teacher_id = ti.teacher_id
        ORDER BY rp.completion_date DESC
        """)
        
        projects = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for project in projects:
            self.project_tree.insert("", tk.END, values=project)
    
    def search_projects(self, keyword):
        # 清除现有数据
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # 搜索课题
        self.cursor.execute("""
        SELECT rp.project_id, rp.project_name, rp.project_level, rp.completion_date, 
               ti.name as leader_name
        FROM research_projects rp
        LEFT JOIN project_members pm ON rp.project_id = pm.project_id AND pm.is_leader = 1
        LEFT JOIN teacher_info ti ON pm.teacher_id = ti.teacher_id
        WHERE rp.project_name LIKE ? OR rp.project_level LIKE ? OR ti.name LIKE ?
        ORDER BY rp.completion_date DESC
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        projects = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for project in projects:
            self.project_tree.insert("", tk.END, values=project)
    
    def edit_research_project(self, event):
        # 获取选中的课题信息
        selected_item = self.project_tree.selection()[0]
        project_id = self.project_tree.item(selected_item, "values")[0]
        
        # 查询课题详细信息
        self.cursor.execute("""
        SELECT rp.*, ti.name as leader_name,
               GROUP_CONCAT(t2.name) as member_names
        FROM research_projects rp
        LEFT JOIN project_members pm ON rp.project_id = pm.project_id AND pm.is_leader = 1
        LEFT JOIN teacher_info ti ON pm.teacher_id = ti.teacher_id
        LEFT JOIN project_members pm2 ON rp.project_id = pm2.project_id AND pm2.is_leader = 0
        LEFT JOIN teacher_info t2 ON pm2.teacher_id = t2.teacher_id
        WHERE rp.project_id = ?
        GROUP BY rp.project_id
        """, (project_id,))
        
        project = self.cursor.fetchone()
        
        if project:
            # 准备编辑数据
            project_data = {
                'project_name': project[1],
                'project_level': project[2],
                'completion_date': project[3],
                'leader_name': project[6],
                'members': project[7].split(',') if project[7] else []
            }
            
            # 打开编辑窗口
            self.add_research_project(project_data)
    # 显示学生竞赛辅导页面
    def show_student_competitions(self):
        self.clear_content_frame()
        
        # 创建标题
        ttk.Label(self.content_frame, text="学生竞赛辅导管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建按钮框架
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        # 添加新竞赛按钮和删除按钮
        ttk.Button(btn_frame, text="添加竞赛记录", command=self.show_add_competition_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中记录", command=lambda: self.delete_competition(self.competition_tree)).pack(side=tk.LEFT, padx=5)
        
        # 创建筛选框架
        filter_frame = ttk.LabelFrame(self.content_frame, text="筛选条件")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建筛选输入框
        # 第一行
        row1_frame = ttk.Frame(filter_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1_frame, text="竞赛名称:").pack(side=tk.LEFT, padx=5)
        self.competition_name_filter = ttk.Entry(row1_frame, width=20)
        self.competition_name_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1_frame, text="辅导教师:").pack(side=tk.LEFT, padx=5)
        self.teacher_filter = ttk.Entry(row1_frame, width=20)
        self.teacher_filter.pack(side=tk.LEFT, padx=5)
        
        # 第二行
        row2_frame = ttk.Frame(filter_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2_frame, text="获奖人数:").pack(side=tk.LEFT, padx=5)
        self.winner_count_filter = ttk.Entry(row2_frame, width=10)
        self.winner_count_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2_frame, text="获奖级别:").pack(side=tk.LEFT, padx=5)
        self.award_level_filter = ttk.Combobox(row2_frame, values=["全部", "省级", "国家级", "国际级"], width=10, state="readonly")
        self.award_level_filter.set("全部")
        self.award_level_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2_frame, text="竞赛日期:").pack(side=tk.LEFT, padx=5)
        self.competition_date_filter = ttk.Entry(row2_frame, width=15)
        self.competition_date_filter.pack(side=tk.LEFT, padx=5)
        
        # 绑定筛选事件
        self.competition_name_filter.bind('<KeyRelease>', lambda e: self.apply_competition_filters())
        self.teacher_filter.bind('<KeyRelease>', lambda e: self.apply_competition_filters())
        self.winner_count_filter.bind('<KeyRelease>', lambda e: self.apply_competition_filters())
        self.award_level_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_competition_filters())
        self.competition_date_filter.bind('<KeyRelease>', lambda e: self.apply_competition_filters())
        
        # 创建竞赛列表
        self.create_competition_list()

    def show_add_competition_dialog(self):
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加竞赛记录")
        dialog.geometry("600x400")
        
        # 创建输入框架
        input_frame = ttk.Frame(dialog)
        input_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 竞赛名称
        ttk.Label(input_frame, text="竞赛名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        competition_name = ttk.Entry(input_frame, width=40)
        competition_name.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # 辅导教师输入框
        ttk.Label(input_frame, text="辅导教师:").grid(row=1, column=0, sticky=tk.W, pady=5)
        teachers_entry = ttk.Entry(input_frame, width=40)
        teachers_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(input_frame, text="多个教师请用逗号分隔").grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # 获奖人数
        ttk.Label(input_frame, text="获奖人数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        winner_count = ttk.Entry(input_frame, width=10)
        winner_count.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 获奖级别
        ttk.Label(input_frame, text="获奖级别:").grid(row=3, column=0, sticky=tk.W, pady=5)
        award_level = ttk.Combobox(input_frame, values=["省级", "国家级", "国际级"], state="readonly")
        award_level.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 竞赛日期
        ttk.Label(input_frame, text="竞赛日期:").grid(row=4, column=0, sticky=tk.W, pady=5)
        competition_date = ttk.Entry(input_frame, width=20)
        competition_date.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Label(input_frame, text="格式: YYYY-MM-DD").grid(row=4, column=2, sticky=tk.W, pady=5)
        
        # 保存按钮
        def save_competition():
            # 获取输入的教师姓名
            teachers_input = teachers_entry.get().strip()
            if not teachers_input:
                messagebox.showerror("错误", "请输入辅导教师姓名")
                return
            
            # 将输入的教师姓名分割成列表
            teacher_names = [name.strip() for name in teachers_input.split(',')]
            
            # 查询教师ID
            selected_teachers = []
            for name in teacher_names:
                self.cursor.execute("SELECT teacher_id FROM teacher_info WHERE name = ?", (name,))
                result = self.cursor.fetchone()
                if result:
                    selected_teachers.append(result[0])
                else:
                    messagebox.showerror("错误", f"找不到教师：{name}")
                    return
                
            # 验证输入
            if not all([competition_name.get(), winner_count.get(), award_level.get(), competition_date.get()]):
                messagebox.showerror("错误", "请填写所有必填项")
                return
                
            try:
                # 保存竞赛记录
                for teacher_id in selected_teachers:
                    competition_id = str(uuid.uuid4())
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    self.cursor.execute("""
                    INSERT INTO student_competitions 
                    (competition_id, teacher_id, competition_name, winner_count, award_level, competition_date, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (competition_id, teacher_id, competition_name.get(), int(winner_count.get()),
                           award_level.get(), competition_date.get(), current_time, current_time))
                
                self.conn.commit()
                messagebox.showinfo("成功", "竞赛记录已保存")
                dialog.destroy()
                self.show_student_competitions()
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(input_frame, text="保存", command=save_competition).grid(row=5, column=1, pady=20)

    def create_competition_list(self):
        # 创建列表框架
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格
        columns = ("竞赛ID", "竞赛名称", "辅导教师", "获奖人数", "获奖级别", "竞赛日期")
        self.competition_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        for col in columns:
            self.competition_tree.heading(col, text=col)
            self.competition_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.competition_tree.yview)
        self.competition_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.competition_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.competition_tree.bind('<Double-1>', lambda e: self.edit_competition(self.competition_tree))
        
        # 加载竞赛数据
        self.apply_competition_filters()

    def apply_competition_filters(self, event=None):
        # 清空现有数据
        for item in self.competition_tree.get_children():
            self.competition_tree.delete(item)
        
        # 构建查询条件
        conditions = []
        params = []
        
        # 竞赛名称筛选
        if hasattr(self, 'competition_name_filter') and self.competition_name_filter.get():
            conditions.append("c.competition_name LIKE ?")
            params.append(f"%{self.competition_name_filter.get()}%")
        
        # 辅导教师筛选
        if hasattr(self, 'teacher_filter') and self.teacher_filter.get():
            conditions.append("t.name LIKE ?")
            params.append(f"%{self.teacher_filter.get()}%")
        
        # 获奖人数筛选
        if hasattr(self, 'winner_count_filter') and self.winner_count_filter.get():
            try:
                count = int(self.winner_count_filter.get())
                conditions.append("c.winner_count = ?")
                params.append(count)
            except ValueError:
                pass
        
        # 获奖级别筛选
        if hasattr(self, 'award_level_filter') and self.award_level_filter.get() != "全部":
            conditions.append("c.award_level = ?")
            params.append(self.award_level_filter.get())
        
        # 竞赛日期筛选
        if hasattr(self, 'competition_date_filter') and self.competition_date_filter.get():
            conditions.append("c.competition_date LIKE ?")
            params.append(f"%{self.competition_date_filter.get()}%")
        
        # 构建SQL查询
        query = """
        SELECT DISTINCT c.competition_id, c.competition_name, 
        GROUP_CONCAT(t.name) as teachers, c.winner_count, c.award_level, c.competition_date
        FROM student_competitions c
        JOIN teacher_info t ON c.teacher_id = t.teacher_id
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY c.competition_id
        ORDER BY c.competition_date DESC
        """
        
        # 执行查询
        self.cursor.execute(query, params)
        competitions = self.cursor.fetchall()
        
        # 更新表格
        for comp in competitions:
            self.competition_tree.insert("", tk.END, values=comp)

    def edit_competition(self, tree):
        try:
            selected_item = tree.selection()[0]
            competition_id = tree.item(selected_item, "values")[0]
            
            # 获取竞赛数据
            self.cursor.execute("""
            SELECT c.competition_name, c.winner_count, c.award_level, c.competition_date,
                   GROUP_CONCAT(c.teacher_id) as teacher_ids
            FROM student_competitions c
            WHERE c.competition_id = ?
            GROUP BY c.competition_id
            """, (competition_id,))
            
            comp_data = self.cursor.fetchone()
            if not comp_data:
                messagebox.showerror("错误", "未找到竞赛数据")
                return
            
            # 创建编辑窗口
            edit_window = tk.Toplevel(self.root)
            edit_window.title("编辑竞赛记录")
            edit_window.geometry("600x400")
            
            # 创建输入框架
            input_frame = ttk.Frame(edit_window)
            input_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
            
            # 竞赛名称
            ttk.Label(input_frame, text="竞赛名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
            competition_name = ttk.Entry(input_frame, width=40)
            competition_name.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
            competition_name.insert(0, comp_data[0])
            
            # 辅导教师选择
            ttk.Label(input_frame, text="辅导教师:").grid(row=1, column=0, sticky=tk.W, pady=5)
            teacher_frame = ttk.Frame(input_frame)
            teacher_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
            
            # 获取所有教师列表
            self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
            teachers = self.cursor.fetchall()
            
            # 获取当前选中的教师ID列表
            selected_teacher_ids = comp_data[4].split(',') if comp_data[4] else []
            
            # 创建教师选择框
            teacher_vars = {}
            for i, (tid, name) in enumerate(teachers):
                var = tk.BooleanVar(value=tid in selected_teacher_ids)
                teacher_vars[tid] = var
                ttk.Checkbutton(teacher_frame, text=name, variable=var).grid(row=i//3, column=i%3, padx=5)
            
            # 获奖人数
            ttk.Label(input_frame, text="获奖人数:").grid(row=2, column=0, sticky=tk.W, pady=5)
            winner_count = ttk.Entry(input_frame, width=10)
            winner_count.grid(row=2, column=1, sticky=tk.W, pady=5)
            winner_count.insert(0, str(comp_data[1]))
            
            # 获奖级别
            ttk.Label(input_frame, text="获奖级别:").grid(row=3, column=0, sticky=tk.W, pady=5)
            award_level = ttk.Combobox(input_frame, values=["省级", "国家级", "国际级"], state="readonly")
            award_level.grid(row=3, column=1, sticky=tk.W, pady=5)
            award_level.set(comp_data[2])
            
            # 竞赛日期
            ttk.Label(input_frame, text="竞赛日期:").grid(row=4, column=0, sticky=tk.W, pady=5)
            competition_date = ttk.Entry(input_frame, width=20)
            competition_date.grid(row=4, column=1, sticky=tk.W, pady=5)
            competition_date.insert(0, comp_data[3])
            ttk.Label(input_frame, text="格式: YYYY-MM-DD").grid(row=4, column=2, sticky=tk.W, pady=5)
            
            def update_competition():
                # 获取选中的教师
                selected_teachers = [tid for tid, var in teacher_vars.items() if var.get()]
                if not selected_teachers:
                    messagebox.showerror("错误", "请至少选择一名辅导教师")
                    return
                
                # 验证输入
                if not all([competition_name.get(), winner_count.get(), award_level.get(), competition_date.get()]):
                    messagebox.showerror("错误", "请填写所有必填项")
                    return
                
                try:
                    # 开始事务
                    self.cursor.execute("BEGIN TRANSACTION")
                    
                    # 删除原有记录
                    self.cursor.execute("DELETE FROM student_competitions WHERE competition_id = ?", (competition_id,))
                    
                    # 插入更新后的记录
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for teacher_id in selected_teachers:
                        self.cursor.execute("""
                        INSERT INTO student_competitions 
                        (competition_id, teacher_id, competition_name, winner_count, award_level, competition_date, create_time, update_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (competition_id, teacher_id, competition_name.get(), int(winner_count.get()),
                               award_level.get(), competition_date.get(), current_time, current_time))
                    
                    # 提交事务
                    self.conn.commit()
                    messagebox.showinfo("成功", "竞赛记录已更新")
                    edit_window.destroy()
                    self.show_student_competitions()
                    
                except Exception as e:
                    # 发生错误时回滚事务
                    self.conn.rollback()
                    messagebox.showerror("错误", f"更新失败: {str(e)}")
            
            # 添加保存按钮
            ttk.Button(input_frame, text="保存", command=update_competition).grid(row=5, column=1, pady=20)
            ttk.Button(input_frame, text="取消", command=edit_window.destroy).grid(row=5, column=2, pady=20)
            
        except IndexError:
            messagebox.showerror("错误", "请选择一条竞赛记录")
    
    def delete_competition(self, tree):
        try:
            selected_item = tree.selection()[0]
            competition_id = tree.item(selected_item, "values")[0]
            competition_name = tree.item(selected_item, "values")[1]
            
            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除竞赛 '{competition_name}' 的记录吗？\n此操作不可恢复！"):
                return
            
            try:
                # 删除竞赛记录
                self.cursor.execute("DELETE FROM student_competitions WHERE competition_id = ?", (competition_id,))
                self.conn.commit()
                
                # 从树形视图中移除
                tree.delete(selected_item)
                
                messagebox.showinfo("成功", "竞赛记录已删除")
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {str(e)}")
                
        except IndexError:
            messagebox.showerror("错误", "请选择一条竞赛记录")
            
    def delete_selected_competitions(self):
        try:
            # 获取选中的项目
            selected_items = self.competition_tree.selection()
            if not selected_items:
                messagebox.showerror("错误", "请选择要删除的竞赛记录")
                return
            
            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_items)} 条竞赛记录吗？\n此操作不可恢复！"):
                return
            
            try:
                # 开始事务
                self.cursor.execute("BEGIN TRANSACTION")
                
                # 删除每条选中的记录
                for item in selected_items:
                    competition_id = self.competition_tree.item(item, "values")[0]
                    self.cursor.execute("DELETE FROM student_competitions WHERE competition_id = ?", (competition_id,))
                    self.competition_tree.delete(item)
                
                # 提交事务
                self.conn.commit()
                messagebox.showinfo("成功", f"已删除 {len(selected_items)} 条竞赛记录")
                
            except Exception as e:
                # 发生错误时回滚事务
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {str(e)}")
    
    # 显示青蓝工程页面    
    def show_mentoring(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="青蓝工程", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建左侧录入框架
        input_frame = ttk.LabelFrame(main_frame, text="师徒关系录入")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 指导教师选择
        ttk.Label(input_frame, text="指导教师:").grid(row=0, column=0, padx=5, pady=5)
        self.mentor_combobox = ttk.Combobox(input_frame, width=20)
        self.mentor_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # 徒弟选择
        ttk.Label(input_frame, text="徒弟:").grid(row=1, column=0, padx=5, pady=5)
        self.apprentice_combobox = ttk.Combobox(input_frame, width=20)
        self.apprentice_combobox.grid(row=1, column=1, padx=5, pady=5)
        
        # 开始日期
        ttk.Label(input_frame, text="开始日期:").grid(row=2, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(input_frame, width=20)
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 结束日期
        ttk.Label(input_frame, text="结束日期:").grid(row=3, column=0, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(input_frame, width=20)
        self.end_date_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 成果描述
        ttk.Label(input_frame, text="成果描述:").grid(row=4, column=0, padx=5, pady=5)
        self.achievements_text = tk.Text(input_frame, width=30, height=4)
        self.achievements_text.grid(row=4, column=1, padx=5, pady=5)
        
        # 保存按钮
        ttk.Button(input_frame, text="保存", command=self.save_mentoring).grid(row=5, column=0, columnspan=2, pady=10)
        
        # 创建右侧显示框架
        display_frame = ttk.LabelFrame(main_frame, text="师徒关系列表")
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建筛选和按钮框架
        filter_frame = ttk.Frame(display_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加筛选输入框
        ttk.Label(filter_frame, text="筛选指导教师:").pack(side=tk.LEFT, padx=5)
        self.mentor_filter = ttk.Entry(filter_frame, width=15)
        self.mentor_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="筛选徒弟:").pack(side=tk.LEFT, padx=5)
        self.apprentice_filter = ttk.Entry(filter_frame, width=15)
        self.apprentice_filter.pack(side=tk.LEFT, padx=5)
        
        # 绑定筛选事件
        self.mentor_filter.bind('<KeyRelease>', lambda e: self.load_mentoring_data())
        self.apprentice_filter.bind('<KeyRelease>', lambda e: self.load_mentoring_data())
        
        # 添加删除按钮
        delete_btn = ttk.Button(filter_frame, text="删除", command=self.delete_mentoring)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # 创建表格
        columns = ("指导教师", "徒弟", "开始日期", "结束日期", "成果描述")
        self.mentoring_tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.mentoring_tree.heading(col, text=col)
            self.mentoring_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.mentoring_tree.yview)
        self.mentoring_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mentoring_tree.pack(fill=tk.BOTH, expand=True)
        
        # 加载教师数据到下拉框
        self.load_teacher_data_to_combobox()
        
        # 加载现有师徒关系数据
        self.load_mentoring_data()
        
    def load_teacher_data_to_combobox(self):
        # 从数据库加载教师数据
        self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
        teachers = self.cursor.fetchall()
        
        # 创建教师ID到姓名的映射
        self.teacher_id_map = {teacher[0]: teacher[1] for teacher in teachers}
        
        # 设置下拉框选项
        teacher_names = [teacher[1] for teacher in teachers]
        self.mentor_combobox['values'] = teacher_names
        self.apprentice_combobox['values'] = teacher_names
    
    def save_mentoring(self):
        # 获取输入数据
        mentor_name = self.mentor_combobox.get()
        apprentice_name = self.apprentice_combobox.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        achievements = self.achievements_text.get("1.0", tk.END).strip()
        
        # 验证输入
        if not all([mentor_name, apprentice_name, start_date]):
            messagebox.showerror("错误", "请填写必要信息（指导教师、徒弟、开始日期）")
            return
        
        # 获取教师ID
        mentor_id = None
        apprentice_id = None
        for teacher_id, name in self.teacher_id_map.items():
            if name == mentor_name:
                mentor_id = teacher_id
            if name == apprentice_name:
                apprentice_id = teacher_id
        
        if mentor_id == apprentice_id:
            messagebox.showerror("错误", "指导教师和徒弟不能是同一人")
            return
        
        try:
            # 生成记录ID
            mentoring_id = str(uuid.uuid4())
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存到数据库
            self.cursor.execute("""
            INSERT INTO mentoring (
                mentoring_id, teacher_id, apprentice_id, start_date, end_date,
                achievements, create_time, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mentoring_id, mentor_id, apprentice_id, start_date, end_date,
                  achievements, current_time, current_time))
            
            self.conn.commit()
            
            # 清空输入框
            self.mentor_combobox.set('')
            self.apprentice_combobox.set('')
            self.start_date_entry.delete(0, tk.END)
            self.end_date_entry.delete(0, tk.END)
            self.achievements_text.delete("1.0", tk.END)
            
            # 刷新显示
            self.load_mentoring_data()
            
            messagebox.showinfo("成功", "师徒关系保存成功")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def load_mentoring_data(self):
        # 清除现有数据
        for item in self.mentoring_tree.get_children():
            self.mentoring_tree.delete(item)
        
        # 获取筛选条件
        mentor_filter = self.mentor_filter.get().strip()
        apprentice_filter = self.apprentice_filter.get().strip()
        
        # 构建SQL查询
        query = """
        SELECT m.mentoring_id, t1.teacher_id, t2.teacher_id, m.start_date, m.end_date, m.achievements
        FROM mentoring m
        JOIN teacher_info t1 ON m.teacher_id = t1.teacher_id
        JOIN teacher_info t2 ON m.apprentice_id = t2.teacher_id
        WHERE 1=1
        """
        
        params = []
        if mentor_filter:
            query += " AND t1.name LIKE ?"
            params.append(f'%{mentor_filter}%')
        if apprentice_filter:
            query += " AND t2.name LIKE ?"
            params.append(f'%{apprentice_filter}%')
            
        query += " ORDER BY m.start_date DESC"
        
        # 执行查询
        self.cursor.execute(query, params)
        mentoring_records = self.cursor.fetchall()
        
        # 将数据添加到表格
        for record in mentoring_records:
            mentor_name = self.teacher_id_map.get(record[1], "未知")
            apprentice_name = self.teacher_id_map.get(record[2], "未知")
            self.mentoring_tree.insert("", tk.END, values=(
                record[0],  # mentoring_id
                mentor_name,
                apprentice_name,
                record[3],  # start_date
                record[4] if record[4] else "",  # end_date
                record[5] if record[5] else ""  # achievements
            ))

    def delete_mentoring(self):
        # 检查是否选择了记录
        selected_items = self.mentoring_tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要删除的师徒关系记录")
            return

        # 获取选中记录的信息
        selected_item = selected_items[0]
        mentoring_id = self.mentoring_tree.item(selected_item, "values")[0]
        mentor_name = self.mentoring_tree.item(selected_item, "values")[1]
        apprentice_name = self.mentoring_tree.item(selected_item, "values")[2]

        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除{mentor_name}和{apprentice_name}的师徒关系记录吗？\n此操作不可恢复！"):
            return

        try:
            # 从数据库中删除记录
            self.cursor.execute("DELETE FROM mentoring WHERE mentoring_id = ?", (mentoring_id,))
            self.conn.commit()

            # 从树形视图中删除记录
            self.mentoring_tree.delete(selected_item)

            messagebox.showinfo("成功", "师徒关系记录已删除")

        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"删除失败: {e}")
    # 显示专业引领页面
    def show_professional_leadership(self):
        self.clear_content_frame()
        
        # 创建标题
        ttk.Label(self.content_frame, text="名师工作室", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建录入框架
        input_frame = ttk.LabelFrame(self.content_frame, text="录入信息")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 主持人输入
        ttk.Label(input_frame, text="工作室主持人:").grid(row=0, column=0, padx=5, pady=5)
        host_entry = ttk.Entry(input_frame, width=30)
        host_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 命题输入
        ttk.Label(input_frame, text="命题:").grid(row=1, column=0, padx=5, pady=5)
        topic_entry = ttk.Entry(input_frame, width=30)
        topic_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 主要内容输入
        ttk.Label(input_frame, text="主要内容:").grid(row=2, column=0, padx=5, pady=5)
        content_text = tk.Text(input_frame, width=50, height=5)
        content_text.grid(row=2, column=1, padx=5, pady=5)
        
        # 保存按钮
        def save_leadership():
            host = host_entry.get().strip()
            topic = topic_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not all([host, topic, content]):
                messagebox.showerror("错误", "请填写所有必填项")
                return
            
            try:
                leadership_id = str(uuid.uuid4())
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.cursor.execute("""
                INSERT INTO professional_leadership 
                (leadership_id, leadership_type, description, create_time, update_time)
                VALUES (?, ?, ?, ?, ?)
                """, (leadership_id, f"{host} - {topic}", content, current_time, current_time))
                
                self.conn.commit()
                messagebox.showinfo("成功", "名师工作室信息保存成功")
                
                # 清空输入框
                host_entry.delete(0, tk.END)
                topic_entry.delete(0, tk.END)
                content_text.delete("1.0", tk.END)
                
                # 刷新显示
                refresh_display()
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(input_frame, text="保存", command=save_leadership).grid(row=3, column=1, pady=10)
        
        # 创建显示框架
        display_frame = ttk.LabelFrame(self.content_frame, text="已有记录")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ("ID", "主持人和命题", "主要内容")
        tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        
        # 设置列标题
        tree.heading("ID", text="ID")
        tree.column("ID", width=0, stretch=False)
        tree.heading("主持人和命题", text="主持人和命题")
        tree.column("主持人和命题", width=200)
        tree.heading("主要内容", text="主要内容")
        tree.column("主要内容", width=400)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 删除按钮
        def delete_selected():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("错误", "请先选择要删除的记录")
                return
            
            if messagebox.askyesno("确认", "确定要删除选中的记录吗？"):
                try:
                    leadership_id = tree.item(selected_item[0], 'values')[0]
                    self.cursor.execute("DELETE FROM professional_leadership WHERE leadership_id = ?", (leadership_id,))
                    self.conn.commit()
                    tree.delete(selected_item[0])
                    messagebox.showinfo("成功", "记录已删除")
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {str(e)}")
        
        ttk.Button(display_frame, text="删除选中记录", command=delete_selected).pack(pady=5)
        
        def refresh_display():
            # 清除现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 从数据库加载数据
            self.cursor.execute("""
            SELECT leadership_id, leadership_type, description 
            FROM professional_leadership 
            ORDER BY create_time DESC
            """)
            
            records = self.cursor.fetchall()
            for record in records:
                tree.insert("", tk.END, values=record)
        
        # 初始显示数据
        refresh_display()
    #变化情况
    def change_situation(self):
        self.clear_content_frame()
        
        # 创建标题
        ttk.Label(self.content_frame, text="变化情况", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建左侧教师列表框架
        teacher_list_frame = ttk.LabelFrame(main_frame, text="教师列表")
        teacher_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建搜索框架
        search_frame = ttk.Frame(teacher_list_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建搜索输入框
        ttk.Label(search_frame, text="教师姓名:").pack(side=tk.LEFT)
        self.teacher_search_var = tk.StringVar()
        self.teacher_search_var.trace('w', lambda name, index, mode: self.load_teachers_for_change())
        ttk.Entry(search_frame, textvariable=self.teacher_search_var).pack(side=tk.LEFT, padx=5)
        
        # 创建教师列表
        columns = ("教师ID", "姓名")
        self.change_teacher_tree = ttk.Treeview(teacher_list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.change_teacher_tree.heading(col, text=col)
            self.change_teacher_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(teacher_list_frame, orient=tk.VERTICAL, command=self.change_teacher_tree.yview)
        self.change_teacher_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.change_teacher_tree.pack(fill=tk.BOTH, expand=True)
        
        # 创建右侧变化情况框架
        change_frame = ttk.LabelFrame(main_frame, text="变化情况")
        change_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建选项卡
        tab_control = ttk.Notebook(change_frame)
        
        # 创建学历变化选项卡
        education_tab = ttk.Frame(tab_control)
        tab_control.add(education_tab, text="学历变化")
        
        # 创建职称变化选项卡
        title_tab = ttk.Frame(tab_control)
        tab_control.add(title_tab, text="职称变化")
        
        tab_control.pack(expand=True, fill="both")
        
        # 加载教师列表
        self.load_teachers_for_change()
        
        # 绑定选择事件
        self.change_teacher_tree.bind("<<TreeviewSelect>>", self.on_change_teacher_selected)
    
    def load_teachers_for_change(self):
        # 清除现有数据
        for item in self.change_teacher_tree.get_children():
            self.change_teacher_tree.delete(item)
        
        # 获取搜索关键词
        search_keyword = self.teacher_search_var.get().strip()
        
        # 从数据库加载教师数据
        if search_keyword:
            self.cursor.execute("SELECT teacher_id, name FROM teacher_info WHERE name LIKE ?", (f'%{search_keyword}%',))
        else:
            self.cursor.execute("SELECT teacher_id, name FROM teacher_info")
        teachers = self.cursor.fetchall()
        
        # 将数据添加到树形视图
        for teacher in teachers:
            self.change_teacher_tree.insert("", tk.END, values=teacher)
    
    def on_change_teacher_selected(self, event):
        # 获取选中的教师ID
        try:
            selected_item = self.change_teacher_tree.selection()[0]
            teacher_id = self.change_teacher_tree.item(selected_item, "values")[0]
            self.show_teacher_changes(teacher_id)
        except IndexError:
            return
    
    def show_teacher_changes(self, teacher_id):
        # 获取教师姓名
        self.cursor.execute("SELECT name FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        teacher_name = self.cursor.fetchone()[0]
        
        # 获取学历变化记录
        self.cursor.execute("""
        SELECT edu_type, degree, institution, obtain_date 
        FROM education 
        WHERE teacher_id = ? 
        ORDER BY obtain_date DESC
        """, (teacher_id,))
        education_changes = self.cursor.fetchall()
        
        # 获取职称变化记录
        self.cursor.execute("""
        SELECT title, obtain_date, post, appointment_date 
        FROM title_history 
        WHERE teacher_id = ? 
        ORDER BY obtain_date DESC
        """, (teacher_id,))
        title_changes = self.cursor.fetchall()
        
        # 显示学历变化
        education_tab = self.content_frame.winfo_children()[1].winfo_children()[1].winfo_children()[0].winfo_children()[0]
        
        # 清除现有内容
        for widget in education_tab.winfo_children():
            widget.destroy()
        
        # 创建学历变化表格
        columns = ("教育类型", "学位", "院校", "获得时间")
        edu_tree = ttk.Treeview(education_tab, columns=columns, show="headings", height=10)
        
        for col in columns:
            edu_tree.heading(col, text=col)
            edu_tree.column(col, width=120)
        
        # 添加数据
        for change in education_changes:
            edu_tree.insert("", tk.END, values=change)
        
        edu_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加按钮框架
        edu_btn_frame = ttk.Frame(education_tab)
        edu_btn_frame.pack(pady=5)
        
        # 添加新增按钮
        ttk.Button(edu_btn_frame, text="添加学历变化", command=lambda: self.add_education_change(teacher_id)).pack(side=tk.LEFT, padx=5)
        
        # 添加删除按钮
        ttk.Button(edu_btn_frame, text="删除学历变化", command=lambda: self.delete_education_change(teacher_id, edu_tree)).pack(side=tk.LEFT, padx=5)
        
        # 显示职称变化
        title_tab = self.content_frame.winfo_children()[1].winfo_children()[1].winfo_children()[0].winfo_children()[1]
        
        # 清除现有内容
        for widget in title_tab.winfo_children():
            widget.destroy()
        
        # 创建职称变化表格
        columns = ("职称", "获得时间", "职务", "任职时间")
        title_tree = ttk.Treeview(title_tab, columns=columns, show="headings", height=10)
        
        for col in columns:
            title_tree.heading(col, text=col)
            title_tree.column(col, width=120)
        
        # 添加数据
        for change in title_changes:
            title_tree.insert("", tk.END, values=change)
        
        title_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加按钮框架
        title_btn_frame = ttk.Frame(title_tab)
        title_btn_frame.pack(pady=5)
        
        # 添加新增按钮
        ttk.Button(title_btn_frame, text="添加职称变化", command=lambda: self.add_title_change(teacher_id)).pack(side=tk.LEFT, padx=5)
        
        # 添加删除按钮
        ttk.Button(title_btn_frame, text="删除职称变化", command=lambda: self.delete_title_change(teacher_id, title_tree)).pack(side=tk.LEFT, padx=5)
    
    def delete_education_change(self, teacher_id, edu_tree):
        # 获取选中的项目
        selected_item = edu_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的学历变化记录")
            return
        
        # 获取选中项的值
        values = edu_tree.item(selected_item[0], 'values')
        
        # 确认删除
        if messagebox.askyesno("确认", "确定要删除这条学历变化记录吗？"):
            try:
                # 从数据库中删除记录
                self.cursor.execute("""
                DELETE FROM education 
                WHERE teacher_id = ? AND edu_type = ? AND degree = ? AND institution = ? AND obtain_date = ?
                """, (teacher_id, values[0], values[1], values[2], values[3]))
                self.conn.commit()
                
                # 从树形视图中删除
                edu_tree.delete(selected_item)
                messagebox.showinfo("成功", "学历变化记录已删除")
            except sqlite3.Error as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
                self.conn.rollback()
    
    def delete_title_change(self, teacher_id, title_tree):
        # 获取选中的项目
        selected_item = title_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的职称变化记录")
            return
        
        # 获取选中项的值
        values = title_tree.item(selected_item[0], 'values')
        
        # 确认删除
        if messagebox.askyesno("确认", "确定要删除这条职称变化记录吗？"):
            try:
                # 从数据库中删除记录
                self.cursor.execute("""
                DELETE FROM title_history 
                WHERE teacher_id = ? AND title = ? AND obtain_date = ? AND post = ? AND appointment_date = ?
                """, (teacher_id, values[0], values[1], values[2], values[3]))
                self.conn.commit()
                
                # 从树形视图中删除
                title_tree.delete(selected_item)
                messagebox.showinfo("成功", "职称变化记录已删除")
            except sqlite3.Error as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
                self.conn.rollback()
    
    def add_education_change(self, teacher_id):
        # 创建新窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("添加学历变化")
        dialog.geometry("400x300")
        
        # 创建输入框架
        input_frame = ttk.Frame(dialog)
        input_frame.pack(padx=20, pady=20)
        
        # 教育类型
        ttk.Label(input_frame, text="教育类型:").grid(row=0, column=0, padx=5, pady=5)
        edu_type_var = tk.StringVar()
        edu_type_combo = ttk.Combobox(input_frame, textvariable=edu_type_var)
        edu_type_combo['values'] = ('全日制', '在职', '函授', '自考')
        edu_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # 学位
        ttk.Label(input_frame, text="学位:").grid(row=1, column=0, padx=5, pady=5)
        degree_var = tk.StringVar()
        degree_combo = ttk.Combobox(input_frame, textvariable=degree_var)
        degree_combo['values'] = ('学士', '硕士', '博士')
        degree_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # 院校
        ttk.Label(input_frame, text="院校:").grid(row=2, column=0, padx=5, pady=5)
        institution_entry = ttk.Entry(input_frame)
        institution_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 获得时间
        ttk.Label(input_frame, text="获得时间:").grid(row=3, column=0, padx=5, pady=5)
        obtain_date_entry = ttk.Entry(input_frame)
        obtain_date_entry.grid(row=3, column=1, padx=5, pady=5)
        obtain_date_entry.insert(0, "YYYY-MM-DD")
        
        # 保存按钮
        def save_education():
            # 获取输入值
            edu_type = edu_type_var.get()
            degree = degree_var.get()
            institution = institution_entry.get()
            obtain_date = obtain_date_entry.get()
            
            # 验证输入
            if not all([edu_type, degree, institution, obtain_date]):
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            try:
                # 生成记录ID
                record_id = str(uuid.uuid4())
                
                # 插入数据
                self.cursor.execute("""
                INSERT INTO education (record_id, teacher_id, edu_type, degree, institution, obtain_date, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (record_id, teacher_id, edu_type, degree, institution, obtain_date,
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                self.conn.commit()
                messagebox.showinfo("成功", "学历变化信息已添加")
                dialog.destroy()
                
                # 刷新显示
                self.show_teacher_changes(teacher_id)
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(dialog, text="保存", command=save_education).pack(pady=10)
    
    def add_title_change(self, teacher_id):
        # 创建新窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("添加职称变化")
        dialog.geometry("400x300")
        
        # 创建输入框架
        input_frame = ttk.Frame(dialog)
        input_frame.pack(padx=20, pady=20)
        
        # 职称
        ttk.Label(input_frame, text="职称:").grid(row=0, column=0, padx=5, pady=5)
        title_var = tk.StringVar()
        title_combo = ttk.Combobox(input_frame, textvariable=title_var)
        title_combo['values'] = ('初级', '中级', '副高级', '正高级')
        title_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # 获得时间
        ttk.Label(input_frame, text="获得时间:").grid(row=1, column=0, padx=5, pady=5)
        obtain_date_entry = ttk.Entry(input_frame)
        obtain_date_entry.grid(row=1, column=1, padx=5, pady=5)
        obtain_date_entry.insert(0, "YYYY-MM-DD")
        
        # 职务
        ttk.Label(input_frame, text="职务:").grid(row=2, column=0, padx=5, pady=5)
        post_entry = ttk.Entry(input_frame)
        post_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 任职时间
        ttk.Label(input_frame, text="任职时间:").grid(row=3, column=0, padx=5, pady=5)
        appointment_date_entry = ttk.Entry(input_frame)
        appointment_date_entry.grid(row=3, column=1, padx=5, pady=5)
        appointment_date_entry.insert(0, "YYYY-MM-DD")
        
        # 保存按钮
        def save_title():
            # 获取输入值
            title = title_var.get()
            obtain_date = obtain_date_entry.get()
            post = post_entry.get()
            appointment_date = appointment_date_entry.get()
            
            # 验证输入
            if not all([title, obtain_date, post, appointment_date]):
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            try:
                # 生成记录ID
                record_id = str(uuid.uuid4())
                
                # 插入数据
                self.cursor.execute("""
                INSERT INTO title_history (record_id, teacher_id, title, obtain_date, post, appointment_date, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (record_id, teacher_id, title, obtain_date, post, appointment_date,
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                self.conn.commit()
                messagebox.showinfo("成功", "职称变化信息已添加")
                dialog.destroy()
                
                # 刷新显示
                self.show_teacher_changes(teacher_id)
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(dialog, text="保存", command=save_title).pack(pady=10)
    #显示考试成绩页面
    def show_exam_results(self):
        self.clear_content_frame()
        
        # 创建标题和按钮框架
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(title_frame, text="考试成绩", font=("Arial", 16, "bold")).pack(side=tk.LEFT, pady=10)
        
        # 创建按钮框架
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="添加考试记录", command=self.add_exam_record).pack(side=tk.LEFT, padx=5, pady=10)
        ttk.Button(btn_frame, text="删除考试记录", command=self.delete_exam_record).pack(side=tk.LEFT, padx=5, pady=10)
        
        # 创建考试记录列表
        columns = ("考试ID", "考试名称", "考试年级", "考试日期")
        self.exam_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        for col in columns:
            self.exam_tree.heading(col, text=col)
            self.exam_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.exam_tree.yview)
        self.exam_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exam_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 绑定双击事件
        self.exam_tree.bind("<Double-1>", self.show_exam_details)
        
        # 加载考试记录
        self.load_exam_records()
    
    # 加载考试记录
    def load_exam_records(self):
        # 清除现有数据
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
        
        # 从数据库加载考试记录
        self.cursor.execute("""
        SELECT DISTINCT exam_name, exam_date
        FROM exam_results
        GROUP BY exam_name, exam_date
        ORDER BY exam_date DESC
        """)
        
        exams = self.cursor.fetchall()
        for exam in exams:
            exam_id = str(uuid.uuid4())  # 生成唯一ID
            grade = exam[0].split()[0]  # 从考试名称中提取年级
            self.exam_tree.insert("", tk.END, values=(exam_id, exam[0], grade, exam[1]))
    
    # 添加考试记录
    def delete_exam_record(self):
        try:
            selected_item = self.exam_tree.selection()[0]
            exam_info = self.exam_tree.item(selected_item, "values")
            
            if not messagebox.askyesno("确认删除", f"确定要删除{exam_info[1]}的考试记录吗？\n此操作不可恢复！"):
                return
            
            # 从数据库中删除记录
            self.cursor.execute("DELETE FROM exam_results WHERE exam_name = ? AND exam_date = ?", 
                               (exam_info[1], exam_info[3]))
            self.conn.commit()
            
            # 从树形视图中删除
            self.exam_tree.delete(selected_item)
            
            messagebox.showinfo("成功", "已删除考试记录")
            
        except IndexError:
            messagebox.showerror("错误", "请先选择要删除的考试记录")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"删除失败: {e}")
    
    def add_exam_record(self):
        # 创建添加考试记录窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("添加考试记录")
        add_window.geometry("400x300")
        
        # 创建输入框架
        input_frame = ttk.Frame(add_window)
        input_frame.pack(padx=20, pady=20)
        
        # 考试名称
        ttk.Label(input_frame, text="考试名称:").grid(row=0, column=0, padx=5, pady=5)
        exam_name = ttk.Entry(input_frame, width=30)
        exam_name.grid(row=0, column=1, padx=5, pady=5)
        
        # 考试年级
        ttk.Label(input_frame, text="考试年级:").grid(row=1, column=0, padx=5, pady=5)
        grade = ttk.Entry(input_frame, width=30)
        grade.grid(row=1, column=1, padx=5, pady=5)
        
        # 考试日期
        ttk.Label(input_frame, text="考试日期:").grid(row=2, column=0, padx=5, pady=5)
        exam_date = ttk.Entry(input_frame, width=30)
        exam_date.grid(row=2, column=1, padx=5, pady=5)
        exam_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 保存按钮
        def save_exam():
            name = exam_name.get().strip()
            grade_val = grade.get().strip()
            date = exam_date.get().strip()
            
            if not all([name, grade_val, date]):
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            try:
                # 生成考试记录ID
                exam_id = str(uuid.uuid4())
                
                # 插入考试记录
                self.cursor.execute("""
                INSERT INTO exam_results (result_id, exam_name, exam_date, create_time, update_time)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """, (exam_id, name, date))
                
                self.conn.commit()
                add_window.destroy()
                self.load_exam_records()
                messagebox.showinfo("成功", "考试记录添加成功")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(add_window, text="保存", command=save_exam).pack(pady=20)
    
    # 显示考试详细信息
    def show_exam_details(self, event):
        # 获取选中的考试记录
        selected_item = self.exam_tree.selection()[0]
        exam_values = self.exam_tree.item(selected_item, "values")
        exam_name = exam_values[1]
        exam_date = exam_values[3]
        
        # 创建详细信息窗口
        details_window = tk.Toplevel(self.root)
        details_window.title(f"考试详细信息 - {exam_name}")
        details_window.geometry("600x400")
        
        # 创建班级成绩列表
        columns = ("班级", "均分", "名次")
        class_tree = ttk.Treeview(details_window, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            class_tree.heading(col, text=col)
            class_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(details_window, orient=tk.VERTICAL, command=class_tree.yview)
        class_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        class_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加班级按钮框架
        btn_frame = ttk.Frame(details_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def delete_class_score():
            try:
                selected_item = class_tree.selection()[0]
                class_info = class_tree.item(selected_item, "values")
                
                if not messagebox.askyesno("确认删除", f"确定要删除{class_info[0]}的成绩记录吗？\n此操作不可恢复！"):
                    return
                
                # 从数据库中删除记录
                self.cursor.execute("DELETE FROM exam_results WHERE exam_name = ? AND exam_date = ? AND class_average = ? AND rank = ?", 
                                   (exam_name, exam_date, float(class_info[1]), int(class_info[2])))
                self.conn.commit()
                
                # 从树形视图中删除
                class_tree.delete(selected_item)
                
                messagebox.showinfo("成功", "已删除班级成绩记录")
                
            except IndexError:
                messagebox.showerror("错误", "请先选择要删除的班级成绩记录")
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("错误", f"删除失败: {e}")
        
        def add_class_score():
            # 创建添加班级成绩窗口
            add_score_window = tk.Toplevel(details_window)
            add_score_window.title("添加班级成绩")
            add_score_window.geometry("300x200")
            
            # 创建输入框架
            input_frame = ttk.Frame(add_score_window)
            input_frame.pack(padx=20, pady=20)
            
            # 班级
            ttk.Label(input_frame, text="班级:").grid(row=0, column=0, padx=5, pady=5)
            class_name = ttk.Entry(input_frame, width=20)
            class_name.grid(row=0, column=1, padx=5, pady=5)
            
            # 均分
            ttk.Label(input_frame, text="均分:").grid(row=1, column=0, padx=5, pady=5)
            avg_score = ttk.Entry(input_frame, width=20)
            avg_score.grid(row=1, column=1, padx=5, pady=5)
            
            # 名次
            ttk.Label(input_frame, text="名次:").grid(row=2, column=0, padx=5, pady=5)
            rank = ttk.Entry(input_frame, width=20)
            rank.grid(row=2, column=1, padx=5, pady=5)
            
            def save_score():
                try:
                    # 更新数据库
                    result_id = str(uuid.uuid4())
                    self.cursor.execute("""
                    INSERT INTO exam_results 
                    (result_id, exam_name, exam_date, class_average, rank, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (result_id, exam_name, exam_date, float(avg_score.get()), int(rank.get())))
                    
                    self.conn.commit()
                    
                    # 更新显示
                    class_tree.insert("", tk.END, values=(class_name.get(), avg_score.get(), rank.get()))
                    add_score_window.destroy()
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
            
            ttk.Button(add_score_window, text="保存", command=save_score).pack(pady=10)
        
        ttk.Button(btn_frame, text="添加班级成绩", command=add_class_score).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除班级成绩", command=delete_class_score).pack(side=tk.LEFT, padx=5)
        
        # 加载已有的班级成绩
        self.cursor.execute("""
        SELECT class_average, rank
        FROM exam_results
        WHERE exam_name = ? AND exam_date = ? AND class_average IS NOT NULL
        ORDER BY rank
        """, (exam_name, exam_date))
        
        scores = self.cursor.fetchall()
        for i, score in enumerate(scores, 1):
            class_tree.insert("", tk.END, values=(f"班级{i}", score[0], score[1]))
    # 显示数据导入导出页面
    def show_data_io(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="数据导入导出", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建子功能按钮框架
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        # 添加子功能按钮
        ttk.Button(btn_frame, text="导入数据", command=self.import_data).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="导出数据", command=self.export_data).grid(row=0, column=1, padx=10, pady=5)
        
        # 显示提示信息
        ttk.Label(self.content_frame, text="请选择上方功能按钮进行操作", font=("Arial", 12)).pack(pady=50)
    # 数据导入导出功能
    def import_data(self):
        messagebox.showinfo("提示", "数据导入功能正在开发中...")
    # 数据导入导出功能
    def export_data(self):
        messagebox.showinfo("提示", "数据导出功能正在开发中...")
    # 综合查询功能
    def show_query(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="综合查询功能", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建查询框架
        query_frame = ttk.Frame(self.content_frame)
        query_frame.pack(pady=10)
        
        # 添加查询条件输入框
        ttk.Label(query_frame, text="关键字:").grid(row=0, column=0, padx=5, pady=5)
        keyword_entry = ttk.Entry(query_frame, width=20)
        keyword_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(query_frame, text="查询类型:").grid(row=0, column=2, padx=5, pady=5)
        query_type = ttk.Combobox(query_frame, values=["基本信息", "职称信息", "教育背景", "工作简历", "教学工作", "获奖情况"])
        query_type.grid(row=0, column=3, padx=5, pady=5)
        query_type.current(0)
        
        ttk.Button(query_frame, text="查询", command=lambda: self.perform_query(keyword_entry.get(), query_type.get())).grid(row=0, column=4, padx=10, pady=5)
        
        # 显示结果区域
        result_frame = ttk.Frame(self.content_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建结果显示区
        ttk.Label(result_frame, text="查询结果将显示在这里", font=("Arial", 12)).pack(pady=50)
    # 执行查询
    def perform_query(self, keyword, query_type):
        messagebox.showinfo("提示", f"正在查询: {query_type} - {keyword}\n此功能正在开发中...")
    # 统计分析功能
    def show_statistics(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="统计分析", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建统计类型选择框架
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(pady=10)
        
        # 添加统计类型选择
        ttk.Label(stats_frame, text="统计类型:").grid(row=0, column=0, padx=5, pady=5)
        stats_type = ttk.Combobox(stats_frame, values=["教师年龄分布", "职称分布", "学历分布", "获奖情况统计"])
        stats_type.grid(row=0, column=1, padx=5, pady=5)
        stats_type.current(0)
        
        ttk.Button(stats_frame, text="生成统计", command=lambda: self.generate_statistics(stats_type.get())).grid(row=0, column=2, padx=10, pady=5)
        
        # 显示统计图表区域
        chart_frame = ttk.Frame(self.content_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建提示信息
        ttk.Label(chart_frame, text="统计图表将显示在这里", font=("Arial", 12)).pack(pady=50)
    # 生成统计
    def generate_statistics(self, stats_type):
        messagebox.showinfo("提示", f"正在生成统计: {stats_type}\n此功能正在开发中...")
    # 照片/扫描件管理功能
    def show_document_management(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="照片/扫描件管理", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建子功能按钮框架
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        # 添加子功能按钮
        ttk.Button(btn_frame, text="上传照片", command=self.upload_photo).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="上传扫描件", command=self.upload_scan).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="查看文件", command=self.view_documents).grid(row=0, column=2, padx=10, pady=5)
        
        # 显示提示信息
        ttk.Label(self.content_frame, text="请选择上方功能按钮进行操作", font=("Arial", 12)).pack(pady=50)
    # 上传照片/扫描件功能
    def upload_photo_new(self):
        messagebox.showinfo("提示", "上传照片功能正在开发中...")
    # 上传照片/扫描件功能
    def upload_scan_new(self):
        messagebox.showinfo("提示", "上传扫描件功能正在开发中...")
    # 查看文件功能
    def view_documents(self):
        # 检查是否选择了教师
        try:
            selected_item = self.teacher_tree.selection()[0]
            teacher_id = self.teacher_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个教师")
            return
            
        # 创建档案修改窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("档案修改")
        edit_window.geometry("800x600")
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(edit_window)
        
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
        
        # 加载并创建基本信息编辑表单
        self.create_basic_info_edit_form(basic_tab, teacher_id)
        
        # 加载并创建职称信息编辑表单
        self.create_title_info_edit_form(title_tab, teacher_id)
        
        # 加载并创建教育背景编辑表单
        self.create_education_edit_form(education_tab, teacher_id)
        
        # 加载并创建工作简历编辑表单
        self.create_work_experience_edit_form(work_tab, teacher_id)
    # 创建基本信息编辑表单
    def create_basic_info_edit_form(self, parent, teacher_id):
        # 从数据库加载教师基本信息
        self.cursor.execute("SELECT * FROM teacher_info WHERE teacher_id = ?", (teacher_id,))
        teacher = self.cursor.fetchone()
        
        if not teacher:
            messagebox.showerror("错误", "找不到教师信息")
            return
        
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建照片上传区域
        photo_frame = ttk.LabelFrame(form_frame, text="照片")
        photo_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=10, sticky="nw")
        
        self.edit_photo_path = teacher[7]  # photo_path
        self.edit_photo_label = tk.Label(photo_frame, width=20, height=10)
        
        # 显示现有照片
        if self.edit_photo_path and os.path.exists(self.edit_photo_path):
            try:
                img = Image.open(self.edit_photo_path)
                img = img.resize((150, 200), Image.Resampling.LANCZOS)
                self.current_edit_photo = ImageTk.PhotoImage(img)  # 保存为实例属性
                self.edit_photo_label.configure(image=self.current_edit_photo)
            except Exception:
                self.edit_photo_label.configure(text="无法加载照片")
        else:
            self.edit_photo_label.configure(text="无照片")
        
        self.edit_photo_label.pack(padx=10, pady=10)
        
        # 添加照片上传按钮
        ttk.Button(photo_frame, text="更新照片", command=self.update_photo).pack(padx=10, pady=5)
        
        # 创建基本信息表单
        form_grid = ttk.Frame(form_frame)
        form_grid.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        # 创建表单字段
        fields = [
            ("姓名:", "name", teacher[1]),
            ("性别:", "gender", teacher[2]),
            ("出生年月:", "birth_date", teacher[3]),
            ("民族:", "ethnicity", teacher[4]),
            ("籍贯:", "hometown", teacher[5]),
            ("身份证号:", "id_number", teacher[6]),
            ("入党时间:", "party_join_date", teacher[8]),
            ("参加工作时间:", "work_start_date", teacher[9]),
            ("健康状况:", "health_status", teacher[10]),
            ("任教学科:", "teaching_subject", teacher[11]),
            ("现任职务:", "current_position", teacher[12])
        ]
        
        # 创建表单输入框
        self.edit_basic_entries = {}
        for i, (label, field, value) in enumerate(fields):
            ttk.Label(form_grid, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form_grid, width=30)
            entry.insert(0, value if value else "")
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.edit_basic_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="更新基本信息", command=lambda: self.update_basic_info(teacher_id)).grid(row=7, column=1, padx=10, pady=20)
    # 更新照片
    def update_photo(self):
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
                img = img.resize((150, 200), Image.Resampling.LANCZOS)
                self.current_edit_photo = ImageTk.PhotoImage(img)  # 保存为实例属性
                self.edit_photo_label.configure(image=self.current_edit_photo)
                
                # 保存照片路径
                self.edit_photo_path = new_path
                
                messagebox.showinfo("成功", "照片更新成功")
            except Exception as e:
                messagebox.showerror("错误", f"照片更新失败: {e}")
    # 更新基本信息
    def update_basic_info(self, teacher_id):
        # 获取表单数据
        name = self.edit_basic_entries["name"].get()
        gender = self.edit_basic_entries["gender"].get()
        birth_date = self.edit_basic_entries["birth_date"].get()
        ethnicity = self.edit_basic_entries["ethnicity"].get()
        hometown = self.edit_basic_entries["hometown"].get()
        id_number = self.edit_basic_entries["id_number"].get()
        party_join_date = self.edit_basic_entries["party_join_date"].get()
        work_start_date = self.edit_basic_entries["work_start_date"].get()
        health_status = self.edit_basic_entries["health_status"].get()
        teaching_subject = self.edit_basic_entries["teaching_subject"].get()
        current_position = self.edit_basic_entries["current_position"].get()
        
        # 验证必填字段
        if not name:
            messagebox.showerror("错误", "姓名不能为空")
            return
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 更新数据到数据库
            self.cursor.execute("""
            UPDATE teacher_info SET
                name = ?, gender = ?, birth_date = ?, ethnicity = ?, hometown = ?, id_number = ?,
                photo_path = ?, party_join_date = ?, work_start_date = ?, health_status = ?,
                teaching_subject = ?, current_position = ?, update_time = ?
            WHERE teacher_id = ?
            """, (
                name, gender, birth_date, ethnicity, hometown, id_number,
                self.edit_photo_path, party_join_date, work_start_date, health_status,
                teaching_subject, current_position, current_time, teacher_id
            ))
            
            self.conn.commit()
            messagebox.showinfo("成功", "基本信息更新成功")
            
            # 刷新教师列表
            self.load_teacher_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "身份证号已存在")
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {e}")
    # 创建职称信息编辑表单
    def create_title_info_edit_form(self, parent, teacher_id):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 从数据库加载教师职称信息
        self.cursor.execute("SELECT * FROM title_history WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
        titles = self.cursor.fetchall()
        
        # 创建职称信息列表
        list_frame = ttk.Frame(form_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("记录ID", "职称", "取得时间", "岗位", "聘任时间")
        self.title_edit_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.title_edit_tree.heading(col, text=col)
            self.title_edit_tree.column(col, width=120)
        
        # 隐藏记录ID列
        self.title_edit_tree.column("记录ID", width=0, stretch=tk.NO)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.title_edit_tree.yview)
        self.title_edit_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.title_edit_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加数据
        for title in titles:
            self.title_edit_tree.insert("", tk.END, values=(title[0], title[2], title[3], title[4], title[5]))
        
        # 添加按钮框架
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 添加按钮
        ttk.Button(btn_frame, text="添加职称", command=lambda: self.add_title_info(teacher_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑职称", command=self.edit_title_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除职称", command=self.delete_title_info).pack(side=tk.LEFT, padx=5)
    # 添加职称信息
    def add_title_info(self, teacher_id):
        # 创建添加职称窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("添加职称信息")
        add_window.geometry("400x300")
        
        # 创建表单框架
        form_frame = ttk.Frame(add_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建表单字段
        fields = [
            ("职称:", "title"),
            ("取得时间:", "obtain_date"),
            ("岗位:", "post"),
            ("聘任时间:", "appointment_date")
        ]
        
        # 创建表单输入框
        add_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            add_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="保存", command=lambda: self.save_new_title(teacher_id, add_entries, add_window)).grid(row=len(fields), column=1, padx=10, pady=20)
    # 保存新职称
    def save_new_title(self, teacher_id, entries, window):
        # 获取表单数据
        title = entries["title"].get()
        obtain_date = entries["obtain_date"].get()
        post = entries["post"].get()
        appointment_date = entries["appointment_date"].get()
        
        # 验证必填字段
        if not title or not obtain_date:
            messagebox.showerror("错误", "职称和取得时间不能为空")
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
            messagebox.showinfo("成功", "职称信息添加成功")
            
            # 刷新职称列表
            self.cursor.execute("SELECT * FROM title_history WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
            titles = self.cursor.fetchall()
            
            # 清空列表
            for item in self.title_edit_tree.get_children():
                self.title_edit_tree.delete(item)
            
            # 添加数据
            for title in titles:
                self.title_edit_tree.insert("", tk.END, values=(title[0], title[2], title[3], title[4], title[5]))
            
            # 关闭窗口
            window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    # 编辑职称信息
    def edit_title_info(self):
        # 检查是否选择了职称记录
        try:
            selected_item = self.title_edit_tree.selection()[0]
            record_id = self.title_edit_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个职称记录")
            return
        
        # 从数据库加载职称信息
        self.cursor.execute("SELECT * FROM title_history WHERE record_id = ?", (record_id,))
        title_record = self.cursor.fetchone()
        
        if not title_record:
            messagebox.showerror("错误", "找不到职称记录")
            return
        
        # 创建编辑职称窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑职称信息")
        edit_window.geometry("400x300")
        
        # 创建表单框架
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建表单字段
        fields = [
            ("职称:", "title", title_record[2]),
            ("取得时间:", "obtain_date", title_record[3]),
            ("岗位:", "post", title_record[4]),
            ("聘任时间:", "appointment_date", title_record[5])
        ]
        
        # 创建表单输入框
        edit_entries = {}
        for i, (label, field, value) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form_frame, width=30)
            entry.insert(0, value if value else "")
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            edit_entries[field] = entry
        
        # 添加保存按钮
        ttk.Button(form_frame, text="更新", command=lambda: self.update_title_info(record_id, edit_entries, edit_window)).grid(row=len(fields), column=1, padx=10, pady=20)
    # 更新职称信息
    def update_title_info(self, record_id, entries, window):
        # 获取表单数据
        title = entries["title"].get()
        obtain_date = entries["obtain_date"].get()
        post = entries["post"].get()
        appointment_date = entries["appointment_date"].get()
        
        # 验证必填字段
        if not title or not obtain_date:
            messagebox.showerror("错误", "职称和取得时间不能为空")
            return
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 更新数据到数据库
            self.cursor.execute("""
            UPDATE title_history SET
                title = ?, obtain_date = ?, post = ?, appointment_date = ?, update_time = ?
            WHERE record_id = ?
            """, (
                title, obtain_date, post, appointment_date, current_time, record_id
            ))
            
            self.conn.commit()
            messagebox.showinfo("成功", "职称信息更新成功")
            
            # 获取教师ID
            self.cursor.execute("SELECT teacher_id FROM title_history WHERE record_id = ?", (record_id,))
            teacher_id = self.cursor.fetchone()[0]
            
            # 刷新职称列表
            self.cursor.execute("SELECT * FROM title_history WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
            titles = self.cursor.fetchall()
            
            # 清空列表
            for item in self.title_edit_tree.get_children():
                self.title_edit_tree.delete(item)
            
            # 添加数据
            for title in titles:
                self.title_edit_tree.insert("", tk.END, values=(title[0], title[2], title[3], title[4], title[5]))
            
            # 关闭窗口
            window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {e}")
    # 删除职称信息
    def delete_title_info(self):
        # 检查是否选择了职称记录
        try:
            selected_item = self.title_edit_tree.selection()[0]
            record_id = self.title_edit_tree.item(selected_item, "values")[0]
        except IndexError:
            messagebox.showerror("错误", "请先选择一个职称记录")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除这条职称记录吗？"):
            return
        
        try:
            # 获取教师ID
            self.cursor.execute("SELECT teacher_id FROM title_history WHERE record_id = ?", (record_id,))
            teacher_id = self.cursor.fetchone()[0]
            
            # 从数据库删除记录
            self.cursor.execute("DELETE FROM title_history WHERE record_id = ?", (record_id,))
            self.conn.commit()
            
            messagebox.showinfo("成功", "职称记录已删除")
            
            # 刷新职称列表
            self.cursor.execute("SELECT * FROM title_history WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
            titles = self.cursor.fetchall()
            
            # 清空列表
            for item in self.title_edit_tree.get_children():
                self.title_edit_tree.delete(item)
            
            # 添加数据
            for title in titles:
                self.title_edit_tree.insert("", tk.END, values=(title[0], title[2], title[3], title[4], title[5]))
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {e}")
    # 创建教育背景编辑表单
    def create_education_edit_form(self, parent, teacher_id):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加新记录按钮
        add_button = ttk.Button(button_frame, text="添加教育背景", command=lambda: self.add_education_record(teacher_id))
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 添加删除按钮
        delete_button = ttk.Button(button_frame, text="删除教育背景", command=lambda: self.delete_education_record(teacher_id))
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # 创建教育背景列表框架
        list_frame = ttk.Frame(form_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 定义列
        columns = ("记录ID", "类型", "学位", "院校", "取得时间", "扫描件")
        self.education_edit_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        for col in columns:
            self.education_edit_tree.heading(col, text=col)
            if col == "记录ID":
                self.education_edit_tree.column(col, width=0, stretch=tk.NO)
            elif col in ["类型", "学位"]:
                self.education_edit_tree.column(col, width=100)
            elif col == "院校":
                self.education_edit_tree.column(col, width=200)
            else:
                self.education_edit_tree.column(col, width=150)
        
        # 添加垂直滚动条
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.education_edit_tree.yview)
        self.education_edit_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # 添加水平滚动条
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.education_edit_tree.xview)
        self.education_edit_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 放置滚动条和树形视图
        self.education_edit_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置grid权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.education_edit_tree.bind("<Double-1>", lambda event: self.edit_education_record(event, teacher_id))
        
        # 加载教育背景数据
        self.load_education_records(teacher_id)

    def add_education_record(self, teacher_id):
        # 创建新窗口
        education_window = tk.Toplevel(self.root)
        education_window.title("添加教育背景")
        education_window.geometry("500x400")
        
        # 创建表单框架
        form_frame = ttk.Frame(education_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建表单字段
        fields = [
            ("教育类型:", "edu_type", ["全日制", "非全日制"]),
            ("学位:", "degree", ["博士", "硕士", "学士", "其他"]),
            ("院校:", "institution", None),
            ("取得时间:", "obtain_date", None)
        ]
        
        entries = {}
        for i, (label, field, values) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            if values:
                entry = ttk.Combobox(form_frame, values=values, width=30)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            entries[field] = entry
        
        # 添加扫描件上传按钮
        ttk.Label(form_frame, text="扫描件:").grid(row=len(fields), column=0, sticky=tk.W, pady=5)
        self.scan_path = None
        self.scan_label = ttk.Label(form_frame, text="无扫描件")
        self.scan_label.grid(row=len(fields), column=1, sticky=tk.W, pady=5)
        
        def upload_scan():
            file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
            if file_path:
                # 复制文件到scans目录
                if not os.path.exists("scans"):
                    os.makedirs("scans")
                file_name = f"scan_{uuid.uuid4().hex}{os.path.splitext(file_path)[1]}"
                new_path = os.path.join("scans", file_name)
                shutil.copy2(file_path, new_path)
                self.scan_path = new_path
                self.scan_label.configure(text=os.path.basename(file_path))
        
        ttk.Button(form_frame, text="上传扫描件", command=upload_scan).grid(row=len(fields)+1, column=1, sticky=tk.W, pady=5)
        
        # 保存按钮
        def save_education():
            # 获取表单数据
            edu_type = entries["edu_type"].get().strip()
            degree = entries["degree"].get().strip()
            institution = entries["institution"].get().strip()
            obtain_date = entries["obtain_date"].get().strip()
            
            # 验证必填字段
            if not all([edu_type, degree, institution, obtain_date]):
                messagebox.showerror("错误", "请填写所有必填字段")
                return
            
            # 生成记录ID
            record_id = uuid.uuid4().hex
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
                education_window.destroy()
                self.load_education_records(teacher_id)
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(form_frame, text="保存", command=save_education).grid(row=len(fields)+2, column=1, sticky=tk.E, pady=20)

    def edit_education_record(self, event, teacher_id):
        # 获取选中的记录
        selected_item = self.education_edit_tree.selection()
        if not selected_item:
            return
        
        record_id = self.education_edit_tree.item(selected_item[0], "values")[0]
        
        # 查询记录详细信息
        self.cursor.execute("SELECT * FROM education WHERE record_id = ?", (record_id,))
        record = self.cursor.fetchone()
        if not record:
            return
        
        # 创建编辑窗口
        education_window = tk.Toplevel(self.root)
        education_window.title("编辑教育背景")
        education_window.geometry("500x400")
        
        # 创建表单框架
        form_frame = ttk.Frame(education_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建表单字段
        fields = [
            ("教育类型:", "edu_type", ["全日制", "非全日制"]),
            ("学位:", "degree", ["博士", "硕士", "学士", "其他"]),
            ("院校:", "institution", None),
            ("取得时间:", "obtain_date", None)
        ]
        
        entries = {}
        for i, (label, field, values) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            if values:
                entry = ttk.Combobox(form_frame, values=values, width=30)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
                entry.set(record[fields.index((label, field, values)) + 2])
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
                entry.insert(0, record[fields.index((label, field, values)) + 2])
            entries[field] = entry
        
        # 添加扫描件上传按钮
        ttk.Label(form_frame, text="扫描件:").grid(row=len(fields), column=0, sticky=tk.W, pady=5)
        self.scan_path = record[6]
        self.scan_label = ttk.Label(form_frame, text=os.path.basename(record[6]) if record[6] else "无扫描件")
        self.scan_label.grid(row=len(fields), column=1, sticky=tk.W, pady=5)
        
        def upload_scan():
            file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
            if file_path:
                # 复制文件到scans目录
                if not os.path.exists("scans"):
                    os.makedirs("scans")
                file_name = f"scan_{uuid.uuid4().hex}{os.path.splitext(file_path)[1]}"
                new_path = os.path.join("scans", file_name)
                shutil.copy2(file_path, new_path)
                self.scan_path = new_path
                self.scan_label.configure(text=os.path.basename(file_path))
        
        ttk.Button(form_frame, text="上传扫描件", command=upload_scan).grid(row=len(fields)+1, column=1, sticky=tk.W, pady=5)
        
        # 保存按钮
        def save_education():
            # 获取表单数据
            edu_type = entries["edu_type"].get().strip()
            degree = entries["degree"].get().strip()
            institution = entries["institution"].get().strip()
            obtain_date = entries["obtain_date"].get().strip()
            
            # 验证必填字段
            if not all([edu_type, degree, institution, obtain_date]):
                messagebox.showerror("错误", "请填写所有必填字段")
                return
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # 更新数据库记录
                self.cursor.execute("""
                UPDATE education SET
                    edu_type = ?, degree = ?, institution = ?, obtain_date = ?, 
                    scan_file_path = ?, update_time = ?
                WHERE record_id = ?
                """, (
                    edu_type, degree, institution, obtain_date, 
                    self.scan_path, current_time, record_id
                ))
                
                self.conn.commit()
                messagebox.showinfo("成功", "教育背景更新成功")
                education_window.destroy()
                self.load_education_records(teacher_id)
            except Exception as e:
                messagebox.showerror("错误", f"更新失败: {str(e)}")
        
        ttk.Button(form_frame, text="保存", command=save_education).grid(row=len(fields)+2, column=1, sticky=tk.E, pady=20)

    def delete_education_record(self, teacher_id):
        # 获取选中的记录
        selected_item = self.education_edit_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的教育背景记录")
            return
        
        # 获取记录ID
        record_id = self.education_edit_tree.item(selected_item[0], "values")[0]
        
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的教育背景记录吗？"):
            return
        
        try:
            # 删除扫描件文件
            self.cursor.execute("SELECT scan_file_path FROM education WHERE record_id = ?", (record_id,))
            scan_file_path = self.cursor.fetchone()[0]
            if scan_file_path and os.path.exists(scan_file_path):
                os.remove(scan_file_path)
            
            # 从数据库中删除记录
            self.cursor.execute("DELETE FROM education WHERE record_id = ?", (record_id,))
            self.conn.commit()
            
            # 刷新显示
            self.load_education_records(teacher_id)
            
            messagebox.showinfo("成功", "教育背景记录已删除")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")
    
    def load_education_records(self, teacher_id):
        # 清除现有数据
        for item in self.education_edit_tree.get_children():
            self.education_edit_tree.delete(item)
        
        # 从数据库加载教育背景记录
        self.cursor.execute("""
        SELECT record_id, edu_type, degree, institution, obtain_date, scan_file_path 
        FROM education 
        WHERE teacher_id = ? 
        ORDER BY obtain_date DESC
        """, (teacher_id,))
        
        records = self.cursor.fetchall()
        
        # 添加记录到树形视图
        for record in records:
            values = list(record)
            values[5] = os.path.basename(values[5]) if values[5] else "无"
            self.education_edit_tree.insert("", tk.END, values=values)

    def create_work_experience_edit_form(self, parent, teacher_id):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建左侧的工作经历列表
        list_frame = ttk.Frame(form_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # 创建工作经历树形视图
        columns = ("record_id", "开始时间", "结束时间", "单位", "职务", "描述")
        self.work_edit_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.work_edit_tree.heading("record_id", text="ID")
        self.work_edit_tree.column("record_id", width=0, stretch=False)
        for col in columns[1:]:
            self.work_edit_tree.heading(col, text=col)
            self.work_edit_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.work_edit_tree.yview)
        self.work_edit_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置树形视图和滚动条
        self.work_edit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建右侧的编辑表单
        edit_frame = ttk.Frame(form_frame)
        edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # 创建表单字段
        fields = [
            ("开始时间:", "start_date"),
            ("结束时间:", "end_date"),
            ("单位:", "organization"),
            ("职务:", "position"),
            ("描述:", "description")
        ]
        
        # 创建表单输入框
        self.work_edit_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(edit_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            
            if field == "description":
                entry = tk.Text(edit_frame, width=30, height=4)
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            else:
                entry = ttk.Entry(edit_frame, width=30)
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            
            self.work_edit_entries[field] = entry
        
        # 创建按钮框架
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        # 添加按钮
        ttk.Button(button_frame, text="新增", command=lambda: self.save_work_experience_edit(teacher_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self.delete_work_experience).pack(side=tk.LEFT, padx=5)
        
        # 绑定选择事件
        self.work_edit_tree.bind("<<TreeviewSelect>>", self.on_work_experience_select)
        
        # 加载工作经历数据
        self.load_work_experience_data(teacher_id)
    
    def load_work_experience_data(self, teacher_id):
        # 清空现有数据
        for item in self.work_edit_tree.get_children():
            self.work_edit_tree.delete(item)
        
        # 从数据库加载工作经历记录
        self.cursor.execute("""
        SELECT record_id, start_date, end_date, organization, position, description 
        FROM work_experience 
        WHERE teacher_id = ? 
        ORDER BY start_date DESC
        """, (teacher_id,))
        
        records = self.cursor.fetchall()
        
        # 添加记录到树形视图
        for record in records:
            self.work_edit_tree.insert("", tk.END, values=record)
    
    def on_work_experience_select(self, event):
        # 获取选中的项目
        selected_items = self.work_edit_tree.selection()
        if not selected_items:
            return
        
        # 获取选中项目的数据
        item = selected_items[0]
        values = self.work_edit_tree.item(item, "values")
        
        # 填充表单
        self.work_edit_entries["start_date"].delete(0, tk.END)
        self.work_edit_entries["start_date"].insert(0, values[1])
        
        self.work_edit_entries["end_date"].delete(0, tk.END)
        self.work_edit_entries["end_date"].insert(0, values[2])
        
        self.work_edit_entries["organization"].delete(0, tk.END)
        self.work_edit_entries["organization"].insert(0, values[3])
        
        self.work_edit_entries["position"].delete(0, tk.END)
        self.work_edit_entries["position"].insert(0, values[4])
        
        self.work_edit_entries["description"].delete("1.0", tk.END)
        self.work_edit_entries["description"].insert("1.0", values[5])
    
    def save_work_experience_edit(self, teacher_id):
        # 获取表单数据
        start_date = self.work_edit_entries["start_date"].get()
        end_date = self.work_edit_entries["end_date"].get()
        organization = self.work_edit_entries["organization"].get()
        position = self.work_edit_entries["position"].get()
        description = self.work_edit_entries["description"].get("1.0", tk.END).strip()
        
        # 验证必填字段
        if not start_date or not organization:
            messagebox.showerror("错误", "开始时间和单位不能为空")
            return
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 检查是否是编辑现有记录
            selected_items = self.work_edit_tree.selection()
            if selected_items:
                # 更新现有记录
                record_id = self.work_edit_tree.item(selected_items[0], "values")[0]
                self.cursor.execute("""
                UPDATE work_experience 
                SET start_date=?, end_date=?, organization=?, position=?, description=?, update_time=?
                WHERE record_id=?
                """, (start_date, end_date, organization, position, description, current_time, record_id))
            else:
                # 插入新记录
                record_id = uuid.uuid4().hex
                self.cursor.execute("""
                INSERT INTO work_experience (
                    record_id, teacher_id, start_date, end_date, organization, position, description, 
                    create_time, update_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (record_id, teacher_id, start_date, end_date, organization, position, description,
                       current_time, current_time))
            
            self.conn.commit()
            messagebox.showinfo("成功", "工作经历保存成功")
            
            # 重新加载数据
            self.load_work_experience_data(teacher_id)
            
            # 清空表单
            for entry in self.work_edit_entries.values():
                if isinstance(entry, tk.Text):
                    entry.delete("1.0", tk.END)
                else:
                    entry.delete(0, tk.END)
                    
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def delete_work_experience(self):
        # 获取选中的项目
        selected_items = self.work_edit_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的记录")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的工作经历记录吗？"):
            return
        
        try:
            # 删除记录
            record_id = self.work_edit_tree.item(selected_items[0], "values")[0]
            self.cursor.execute("DELETE FROM work_experience WHERE record_id=?", (record_id,))
            self.conn.commit()
            
            # 从树形视图中移除
            self.work_edit_tree.delete(selected_items[0])
            
            # 清空表单
            for entry in self.work_edit_entries.values():
                if isinstance(entry, tk.Text):
                    entry.delete("1.0", tk.END)
                else:
                    entry.delete(0, tk.END)
                    
            messagebox.showinfo("成功", "工作经历删除成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {e}")
