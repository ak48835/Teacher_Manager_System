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
            info_frame = tk.Frame(tab)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 显示照片
            photo_frame = tk.Frame(info_frame)
            photo_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
            
            if teacher[7] and os.path.exists(teacher[7]):  # photo_path
                try:
                    img = Image.open(teacher[7])
                    img = img.resize((150, 200), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    photo_label = tk.Label(photo_frame, image=photo)
                    photo_label.image = photo  # 保持引用
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
                self.photo_label.configure(image=photo)
                self.photo_label.image = photo  # 保持引用
                
                # 保存照片路径
                self.photo_path = new_path
                
                messagebox.showinfo("成功", "照片上传成功")
            except Exception as e:
                messagebox.showerror("错误", f"照片上传失败: {e}")
    
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
    
    def show_teaching_records(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="教学工作情况", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_education_work(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="教育工作情况", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_awards(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="荣誉管理", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_public_lessons(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="公开课管理", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_papers(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="论文管理", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_research_projects(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="课题管理", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_student_competitions(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="学生竞赛辅导", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_mentoring(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="青蓝工程", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_professional_leadership(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="专业引领", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
    def show_exam_results(self):
        self.clear_content_frame()
        ttk.Label(self.content_frame, text="考试成绩", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_frame, text="此功能正在开发中...", font=("Arial", 12)).pack(pady=50)
    
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
    
    def import_data(self):
        messagebox.showinfo("提示", "数据导入功能正在开发中...")
    
    def export_data(self):
        messagebox.showinfo("提示", "数据导出功能正在开发中...")
    
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
    
    def perform_query(self, keyword, query_type):
        messagebox.showinfo("提示", f"正在查询: {query_type} - {keyword}\n此功能正在开发中...")
    
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
    
    def generate_statistics(self, stats_type):
        messagebox.showinfo("提示", f"正在生成统计: {stats_type}\n此功能正在开发中...")
    
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
    
    def upload_photo(self):
        messagebox.showinfo("提示", "上传照片功能正在开发中...")
    
    def upload_scan(self):
        messagebox.showinfo("提示", "上传扫描件功能正在开发中...")
    
    def view_documents(self):
        messagebox.showinfo("提示", "查看文件功能正在开发中...")
        
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
                img = img.resize((150, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.edit_photo_label.configure(image=photo)
                self.edit_photo_label.image = photo  # 保持引用
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
                img = img.resize((150, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.edit_photo_label.configure(image=photo)
                self.edit_photo_label.image = photo  # 保持引用
                
                # 保存照片路径
                self.edit_photo_path = new_path
                
                messagebox.showinfo("成功", "照片更新成功")
            except Exception as e:
                messagebox.showerror("错误", f"照片更新失败: {e}")
    
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
        self.title_edit_tree.configure(yscroll=scrollbar.set)
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
    
    def create_education_edit_form(self, parent, teacher_id):
        # 创建表单框架
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 从数据库加载教师教育背景
        self.cursor.execute("SELECT * FROM education WHERE teacher_id = ? ORDER BY obtain_date DESC", (teacher_id,))
        educations = self.cursor.fetchall()
        
        # 创建教育背景列表
        list_frame = ttk.Frame(form_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("记录ID", "类型", "学位", "院校", "取得时间", "扫描件")
        self.education_edit_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.education_edit_tree.heading(col, text=col)
            self.education_edit_tree.column(col, width=100)
        
        # 隐藏记录ID列
        self.education_edit_tree.column("记录ID", width=0, stretch=tk.NO)
        
        # 添加滚动条
        scrollbar = ttk