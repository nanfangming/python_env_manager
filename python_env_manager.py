import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from pathlib import Path

class PythonEnvManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Python环境管理器")
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        
        # 配置文件路径
        self.config_path = Path.home() / ".python_env_manager.json"
        
        # 默认配置
        self.config = {
            "base_envs": [],
            "project_envs": [],
            "last_project_dir": str(Path.home())
        }
        
        # 加载配置
        self.load_config()
        
        # 获取已有的conda环境
        self.refresh_conda_envs()
        
        # 创建界面
        self.create_ui()
        
        # 刷新环境列表
        self.refresh_env_lists()

    def create_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(main_frame)
        
        # 创建三个选项卡
        base_tab = ttk.Frame(tab_control)
        project_tab = ttk.Frame(tab_control)
        tools_tab = ttk.Frame(tab_control)
        
        tab_control.add(base_tab, text="基础环境管理")
        tab_control.add(project_tab, text="项目环境管理")
        tab_control.add(tools_tab, text="工具与设置")
        
        tab_control.pack(expand=True, fill="both")
        
        # 创建基础环境选项卡内容
        self.create_base_tab(base_tab)
        
        # 创建项目环境选项卡内容
        self.create_project_tab(project_tab)
        
        # 创建工具选项卡内容
        self.create_tools_tab(tools_tab)
        
        # 创建状态栏
        status_frame = ttk.Frame(self.root, relief="sunken", padding=(5, 2))
        status_frame.pack(side="bottom", fill="x")
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side="left")
        
        # 设置样式
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TFrame", background="#f5f5f5")
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))

    def create_base_tab(self, parent):
        # 左侧：现有基础环境列表
        left_frame = ttk.Frame(parent, padding="10")
        left_frame.pack(side="left", fill="both", expand=True)
        
        ttk.Label(left_frame, text="已有基础环境", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 环境列表框架
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 环境列表
        self.base_env_listbox = tk.Listbox(list_frame, height=15, width=40)
        self.base_env_listbox.pack(side="left", fill="both", expand=True)
        
        # 配置滚动条
        self.base_env_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.base_env_listbox.yview)
        
        # 按钮框架
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="刷新列表", command=self.refresh_env_lists).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="删除环境", command=self.delete_base_env).pack(side="left", padx=5)
        
        # 右侧：创建新的基础环境
        right_frame = ttk.Frame(parent, padding="10")
        right_frame.pack(side="right", fill="both", expand=True)
        
        ttk.Label(right_frame, text="创建新基础环境", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 环境名称
        name_frame = ttk.Frame(right_frame)
        name_frame.pack(fill="x", pady=5)
        ttk.Label(name_frame, text="环境名称:").pack(side="left")
        self.base_name_var = tk.StringVar(value="py3x_base")
        ttk.Entry(name_frame, textvariable=self.base_name_var, width=20).pack(side="left", padx=5, fill="x", expand=True)
        
        # Python版本
        version_frame = ttk.Frame(right_frame)
        version_frame.pack(fill="x", pady=5)
        ttk.Label(version_frame, text="Python版本:").pack(side="left")
        self.py_version_var = tk.StringVar(value="3.9")
        version_cb = ttk.Combobox(version_frame, textvariable=self.py_version_var, width=5)
        version_cb['values'] = ('3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12')
        version_cb.pack(side="left", padx=5)
        
        # 基础包
        packages_frame = ttk.Frame(right_frame)
        packages_frame.pack(fill="x", pady=5)
        ttk.Label(packages_frame, text="基础包:").pack(side="left")
        self.packages_var = tk.StringVar(value="pip virtualenv")
        ttk.Entry(packages_frame, textvariable=self.packages_var).pack(side="left", padx=5, fill="x", expand=True)
        
        # 创建按钮
        ttk.Button(right_frame, text="创建基础环境", command=self.create_base_env).pack(anchor="w", pady=10)
        
        # 控制台输出
        ttk.Label(right_frame, text="控制台输出", style="Header.TLabel").pack(anchor="w", pady=10)
        console_frame = ttk.Frame(right_frame)
        console_frame.pack(fill="both", expand=True)
        
        console_scroll = ttk.Scrollbar(console_frame)
        console_scroll.pack(side="right", fill="y")
        
        self.console_output = tk.Text(console_frame, height=10, width=40, wrap="word")
        self.console_output.pack(side="left", fill="both", expand=True)
        
        self.console_output.config(yscrollcommand=console_scroll.set)
        console_scroll.config(command=self.console_output.yview)
        
        # 设置只读
        self.console_output.config(state="disabled")

    def create_project_tab(self, parent):
        # 左侧：项目环境列表
        left_frame = ttk.Frame(parent, padding="10")
        left_frame.pack(side="left", fill="both", expand=True)
        
        ttk.Label(left_frame, text="已有项目环境", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 环境列表框架
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 环境列表
        self.project_env_listbox = tk.Listbox(list_frame, height=15, width=40)
        self.project_env_listbox.pack(side="left", fill="both", expand=True)
        
        # 配置滚动条
        self.project_env_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.project_env_listbox.yview)
        
        # 按钮框架
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="刷新列表", command=self.refresh_env_lists).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="激活环境", command=self.activate_project_env).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="删除环境", command=self.delete_project_env).pack(side="left", padx=5)
        
        # 右侧：创建新的项目环境
        right_frame = ttk.Frame(parent, padding="10")
        right_frame.pack(side="right", fill="both", expand=True)
        
        ttk.Label(right_frame, text="创建新项目环境", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 项目名称
        name_frame = ttk.Frame(right_frame)
        name_frame.pack(fill="x", pady=5)
        ttk.Label(name_frame, text="项目名称:").pack(side="left")
        self.project_name_var = tk.StringVar(value="my_project")
        ttk.Entry(name_frame, textvariable=self.project_name_var, width=20).pack(side="left", padx=5, fill="x", expand=True)
        
        # 基础环境
        base_frame = ttk.Frame(right_frame)
        base_frame.pack(fill="x", pady=5)
        ttk.Label(base_frame, text="基础环境:").pack(side="left")
        self.base_env_var = tk.StringVar()
        self.base_env_combo = ttk.Combobox(base_frame, textvariable=self.base_env_var, width=20)
        self.base_env_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # 项目目录
        dir_frame = ttk.Frame(right_frame)
        dir_frame.pack(fill="x", pady=5)
        ttk.Label(dir_frame, text="项目目录:").pack(side="left")
        self.project_dir_var = tk.StringVar(value=self.config["last_project_dir"])
        ttk.Entry(dir_frame, textvariable=self.project_dir_var).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(dir_frame, text="浏览", command=self.browse_project_dir).pack(side="left")
        
        # 环境类型
        type_frame = ttk.Frame(right_frame)
        type_frame.pack(fill="x", pady=5)
        ttk.Label(type_frame, text="环境类型:").pack(side="left")
        self.env_type_var = tk.StringVar(value="venv")
        type_rb1 = ttk.Radiobutton(type_frame, text="venv", variable=self.env_type_var, value="venv")
        type_rb1.pack(side="left", padx=5)
        type_rb2 = ttk.Radiobutton(type_frame, text="virtualenv", variable=self.env_type_var, value="virtualenv")
        type_rb2.pack(side="left", padx=5)
        
        # 安装依赖
        req_frame = ttk.Frame(right_frame)
        req_frame.pack(fill="x", pady=5)
        ttk.Label(req_frame, text="依赖文件:").pack(side="left")
        self.req_file_var = tk.StringVar()
        ttk.Entry(req_frame, textvariable=self.req_file_var).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(req_frame, text="浏览", command=self.browse_req_file).pack(side="left")
        
        # 创建按钮
        ttk.Button(right_frame, text="创建项目环境", command=self.create_project_env).pack(anchor="w", pady=10)
        
        # 控制台输出
        ttk.Label(right_frame, text="控制台输出", style="Header.TLabel").pack(anchor="w", pady=10)
        console_frame = ttk.Frame(right_frame)
        console_frame.pack(fill="both", expand=True)
        
        console_scroll = ttk.Scrollbar(console_frame)
        console_scroll.pack(side="right", fill="y")
        
        self.project_console_output = tk.Text(console_frame, height=10, width=40, wrap="word")
        self.project_console_output.pack(side="left", fill="both", expand=True)
        
        self.project_console_output.config(yscrollcommand=console_scroll.set)
        console_scroll.config(command=self.project_console_output.yview)
        
        # 设置只读
        self.project_console_output.config(state="disabled")

    def create_tools_tab(self, parent):
        tools_frame = ttk.Frame(parent, padding="20")
        tools_frame.pack(fill="both", expand=True)
        
        ttk.Label(tools_frame, text="环境管理工具", style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # 生成快速激活脚本
        generate_frame = ttk.Frame(tools_frame)
        generate_frame.pack(fill="x", pady=10)
        
        ttk.Button(generate_frame, text="生成环境激活脚本", command=self.generate_activation_scripts).pack(side="left")
        ttk.Label(generate_frame, text="为所有环境生成快速启动脚本").pack(side="left", padx=10)
        
        # 导出环境列表
        export_frame = ttk.Frame(tools_frame)
        export_frame.pack(fill="x", pady=10)
        
        ttk.Button(export_frame, text="导出环境列表", command=self.export_env_list).pack(side="left")
        ttk.Label(export_frame, text="将所有环境信息导出为JSON文件").pack(side="left", padx=10)
        
        # 清理缓存
        cache_frame = ttk.Frame(tools_frame)
        cache_frame.pack(fill="x", pady=10)
        
        ttk.Button(cache_frame, text="清理Conda缓存", command=self.clean_conda_cache).pack(side="left")
        ttk.Label(cache_frame, text="清理Conda下载缓存和未使用的包").pack(side="left", padx=10)
        
        # 设置区域
        ttk.Separator(tools_frame, orient="horizontal").pack(fill="x", pady=20)
        ttk.Label(tools_frame, text="设置", style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Conda路径设置
        conda_frame = ttk.Frame(tools_frame)
        conda_frame.pack(fill="x", pady=10)
        
        ttk.Label(conda_frame, text="Conda路径:").pack(side="left")
        self.conda_path_var = tk.StringVar(value=self.get_conda_path())
        ttk.Entry(conda_frame, textvariable=self.conda_path_var).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(conda_frame, text="浏览", command=self.browse_conda_path).pack(side="left")
        ttk.Button(conda_frame, text="应用", command=self.apply_conda_path).pack(side="left", padx=5)
        
        # 关于信息
        ttk.Separator(tools_frame, orient="horizontal").pack(fill="x", pady=20)
        about_frame = ttk.Frame(tools_frame)
        about_frame.pack(fill="x", pady=10)
        
        ttk.Label(about_frame, text="Python环境管理器 v1.0").pack(anchor="w")
        ttk.Label(about_frame, text="一个简单的Python环境创建和管理工具").pack(anchor="w")

    def refresh_conda_envs(self):
        try:
            conda_path = self.get_conda_path()
            if sys.platform == 'win32':
                # Windows平台
                output = subprocess.check_output(['cmd.exe', '/c', f"{conda_path} env list"], 
                                               stderr=subprocess.STDOUT, 
                                               universal_newlines=True)
            else:
                # Linux/Mac平台
                output = subprocess.check_output(['/bin/bash', '-c', f"{conda_path} env list"], 
                                               stderr=subprocess.STDOUT, 
                                               universal_newlines=True)
                
            self.conda_envs = []
            for line in output.splitlines():
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.split()
                if parts:
                    self.conda_envs.append(parts[0])
            
            # 过滤出基础环境
            self.base_envs = [env for env in self.conda_envs if 'base' in env.lower()]
            
        except Exception as e:
            messagebox.showerror("错误", f"无法获取Conda环境列表: {str(e)}")
            self.conda_envs = []
            self.base_envs = []

    def get_conda_path(self):
        """获取conda可执行文件路径"""
        # 尝试从配置获取
        if hasattr(self, 'config') and self.config.get('conda_path'):
            return self.config['conda_path']
        
        # 默认conda路径
        if sys.platform == 'win32':
            return "conda.exe"
        else:
            return "conda"

    def refresh_env_lists(self):
        """刷新环境列表"""
        self.refresh_conda_envs()
        
        # 清空列表
        self.base_env_listbox.delete(0, tk.END)
        self.project_env_listbox.delete(0, tk.END)
        
        # 添加基础环境
        for env in self.base_envs:
            self.base_env_listbox.insert(tk.END, env)
        
        # 添加项目环境
        for env in self.config["project_envs"]:
            self.project_env_listbox.insert(tk.END, f"{env['name']} ({env['base_env']})")
        
        # 更新基础环境下拉框
        self.base_env_combo['values'] = self.base_envs
        if self.base_envs:
            self.base_env_var.set(self.base_envs[0])

    def create_base_env(self):
        """创建新的基础环境"""
        name = self.base_name_var.get()
        version = self.py_version_var.get()
        packages = self.packages_var.get()
        
        if not name or not version:
            messagebox.showerror("错误", "环境名称和Python版本不能为空")
            return
        
        self.console_output.config(state="normal")
        self.console_output.delete(1.0, tk.END)
        self.console_output.insert(tk.END, f"正在创建环境 {name} 使用Python {version}...\n")
        self.console_output.config(state="disabled")
        self.status_var.set(f"正在创建环境 {name}...")
        self.root.update()
        
        # 在后台线程执行
        threading.Thread(target=self._create_base_env, args=(name, version, packages)).start()

    def _create_base_env(self, name, version, packages):
        """在后台线程创建基础环境"""
        try:
            conda_path = self.get_conda_path()
            cmd = f"{conda_path} create -n {name} python={version} {packages} -y"
            
            if sys.platform == 'win32':
                process = subprocess.Popen(['cmd.exe', '/c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            else:
                process = subprocess.Popen(['/bin/bash', '-c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                self.update_console(line)
                if not line:
                    break
            
            process.stdout.close()
            returncode = process.wait()
            
            if returncode == 0:
                self.update_console(f"\n✅ 环境 {name} 创建成功！\n")
                self.update_status(f"环境 {name} 创建成功")
                
                # 添加到基础环境列表
                if name not in self.base_envs:
                    self.base_envs.append(name)
                    self.save_config()
                
                # 刷新列表
                self.root.after(0, self.refresh_env_lists)
            else:
                self.update_console(f"\n❌ 环境创建失败，退出代码: {returncode}\n")
                self.update_status("环境创建失败")
        
        except Exception as e:
            self.update_console(f"\n❌ 异常: {str(e)}\n")
            self.update_status(f"异常: {str(e)}")

    def update_console(self, text):
        """更新控制台输出"""
        def _update():
            self.console_output.config(state="normal")
            self.console_output.insert(tk.END, text)
            self.console_output.see(tk.END)
            self.console_output.config(state="disabled")
            
            self.project_console_output.config(state="normal")
            self.project_console_output.insert(tk.END, text)
            self.project_console_output.see(tk.END)
            self.project_console_output.config(state="disabled")
        
        self.root.after(0, _update)

    def update_status(self, text):
        """更新状态栏"""
        self.root.after(0, lambda: self.status_var.set(text))

    def delete_base_env(self):
        """删除基础环境"""
        selection = self.base_env_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要删除的环境")
            return
        
        env_name = self.base_env_listbox.get(selection[0])
        if messagebox.askyesno("确认", f"确定要删除环境 {env_name} 吗？这个操作不可撤销。"):
            self.status_var.set(f"正在删除环境 {env_name}...")
            threading.Thread(target=self._delete_env, args=(env_name, True)).start()

    def _delete_env(self, env_name, is_base=True):
        """在后台线程删除环境"""
        try:
            conda_path = self.get_conda_path()
            cmd = f"{conda_path} env remove -n {env_name} -y"
            
            if sys.platform == 'win32':
                process = subprocess.Popen(['cmd.exe', '/c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            else:
                process = subprocess.Popen(['/bin/bash', '-c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                self.update_console(line)
                if not line:
                    break
            
            process.stdout.close()
            returncode = process.wait()
            
            if returncode == 0:
                self.update_console(f"\n✅ 环境 {env_name} 删除成功！\n")
                self.update_status(f"环境 {env_name} 删除成功")
                
                if is_base:
                    # 从基础环境列表中移除
                    if env_name in self.base_envs:
                        self.base_envs.remove(env_name)
                else:
                    # 从项目环境列表中移除
                    self.config["project_envs"] = [env for env in self.config["project_envs"] if env["name"] != env_name]
                
                self.save_config()
                # 刷新列表
                self.root.after(0, self.refresh_env_lists)
            else:
                self.update_console(f"\n❌ 环境删除失败，退出代码: {returncode}\n")
                self.update_status("环境删除失败")
        
        except Exception as e:
            self.update_console(f"\n❌ 异常: {str(e)}\n")
            self.update_status(f"异常: {str(e)}")

    def browse_project_dir(self):
        """浏览项目目录"""
        directory = filedialog.askdirectory(initialdir=self.project_dir_var.get())
        if directory:
            self.project_dir_var.set(directory)
            self.config["last_project_dir"] = directory
            self.save_config()

    def browse_req_file(self):
        """浏览依赖文件"""
        file_path = filedialog.askopenfilename(
            initialdir=self.project_dir_var.get(),
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.req_file_var.set(file_path)

    def create_project_env(self):
        """创建新的项目环境"""
        project_name = self.project_name_var.get()
        base_env = self.base_env_var.get()
        project_dir = self.project_dir_var.get()
        env_type = self.env_type_var.get()
        req_file = self.req_file_var.get()
        
        if not project_name or not base_env or not project_dir:
            messagebox.showerror("错误", "项目名称、基础环境和项目目录不能为空")
            return
        
        # 检查目录是否存在
        if not os.path.isdir(project_dir):
            if messagebox.askyesno("提示", f"目录 {project_dir} 不存在，是否创建？"):
                try:
                    os.makedirs(project_dir)
                except Exception as e:
                    messagebox.showerror("错误", f"无法创建目录: {str(e)}")
                    return
            else:
                return
        
        self.project_console_output.config(state="normal")
        self.project_console_output.delete(1.0, tk.END)
        self.project_console_output.insert(tk.END, f"正在创建项目环境 {project_name} 基于 {base_env}...\n")
        self.project_console_output.config(state="disabled")
        self.status_var.set(f"正在创建项目环境 {project_name}...")
        self.root.update()
        
        # 在后台线程执行
        threading.Thread(target=self._create_project_env, 
                        args=(project_name, base_env, project_dir, env_type, req_file)).start()

    def _create_project_env(self, project_name, base_env, project_dir, env_type, req_file):
        """在后台线程创建项目环境"""
        try:
            env_path = os.path.join(project_dir, f"{project_name}_env")
            
            # 激活基础环境并创建venv/virtualenv环境
            if sys.platform == 'win32':
                if env_type == "venv":
                    cmd = f"conda activate {base_env} && python -m venv {env_path}"
                else:
                    cmd = f"conda activate {base_env} && virtualenv {env_path}"
                
                process = subprocess.Popen(['cmd.exe', '/c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            else:
                if env_type == "venv":
                    cmd = f"source $(conda info --base)/etc/profile.d/conda.sh && conda activate {base_env} && python -m venv {env_path}"
                else:
                    cmd = f"source $(conda info --base)/etc/profile.d/conda.sh && conda activate {base_env} && virtualenv {env_path}"
                
                process = subprocess.Popen(['/bin/bash', '-c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                self.update_console(line)
                if not line:
                    break
            
            process.stdout.close()
            returncode = process.wait()
            
            if returncode == 0:
                self.update_console(f"✅ 环境 {project_name}_env 创建成功！\n")
                
                # 如果有依赖文件，安装依赖
                if req_file and os.path.isfile(req_file):
                    self.update_console(f"正在安装依赖...\n")
                    
                    if sys.platform == 'win32':
                        pip_cmd = f"{env_path}\\Scripts\\pip install -r {req_file}"
                        process = subprocess.Popen(['cmd.exe', '/c', pip_cmd], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.STDOUT, 
                                                universal_newlines=True)
                    else:
                        pip_cmd = f"{env_path}/bin/pip install -r {req_file}"
                        process = subprocess.Popen(['/bin/bash', '-c', pip_cmd], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.STDOUT, 
                                                universal_newlines=True)
                    
                    # 读取输出
                    for line in iter(process.stdout.readline, ''):
                        self.update_console(line)
                        if not line:
                            break
                    
                    process.stdout.close()
                    pip_returncode = process.wait()
                    
                    if pip_returncode == 0:
                        self.update_console(f"✅ 依赖安装成功！\n")
                    else:
                        self.update_console(f"❌ 依赖安装失败，退出代码: {pip_returncode}\n")
                
                # 添加到项目环境列表
                new_env = {
                    "name": f"{project_name}_env",
                    "base_env": base_env,
                    "path": env_path,
                    "type": env_type
                }
                
                self.config["project_envs"].append(new_env)
                self.save_config()
                
                self.update_console(f"\n✅ 项目环境设置完成！\n")
                self.update_status(f"项目环境 {project_name} 创建成功")
                
                # 刷新列表
                self.root.after(0, self.refresh_env_lists)
            else:
                self.update_console(f"\n❌ 环境创建失败，退出代码: {returncode}\n")
                self.update_status("环境创建失败")
        
        except Exception as e:
            self.update_console(f"\n❌ 异常: {str(e)}\n")
            self.update_status(f"异常: {str(e)}")

    def delete_project_env(self):
        """删除项目环境"""
        selection = self.project_env_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要删除的环境")
            return
        
        env_info = self.project_env_listbox.get(selection[0])
        env_name = env_info.split(" ")[0]
        
        if messagebox.askyesno("确认", f"确定要删除环境 {env_name} 吗？这个操作不可撤销。"):
            # 查找环境详细信息
            env_details = next((env for env in self.config["project_envs"] if env["name"] == env_name), None)
            
            if env_details:
                if os.path.exists(env_details["path"]):
                    try:
                        # 在Windows上，有些文件可能被锁定，需要特殊处理
                        if sys.platform == 'win32':
                            import shutil
                            shutil.rmtree(env_details["path"], ignore_errors=True)
                        else:
                            import shutil
                            shutil.rmtree(env_details["path"])
                        
                        self.update_console(f"✅ 已删除目录 {env_details['path']}\n")
                    except Exception as e:
                        self.update_console(f"❌ 删除目录时出错: {str(e)}\n")
                
                # 从配置中移除
                self.config["project_envs"] = [env for env in self.config["project_envs"] if env["name"] != env_name]
                self.save_config()
                
                self.update_status(f"项目环境 {env_name} 已删除")
                self.refresh_env_lists()

    def activate_project_env(self):
        """激活项目环境（打开终端）"""
        selection = self.project_env_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要激活的环境")
            return
        
        env_info = self.project_env_listbox.get(selection[0])
        env_name = env_info.split(" ")[0]
        
        # 查找环境详细信息
        env_details = next((env for env in self.config["project_envs"] if env["name"] == env_name), None)
        
        if not env_details:
            messagebox.showerror("错误", f"找不到环境 {env_name} 的详细信息")
            return
        
        # 获取激活脚本路径
        if sys.platform == 'win32':
            activate_script = os.path.join(env_details["path"], "Scripts", "activate.bat")
        else:
            activate_script = os.path.join(env_details["path"], "bin", "activate")
        
        if not os.path.exists(activate_script):
            messagebox.showerror("错误", f"找不到激活脚本: {activate_script}")
            return
        
        # 打开终端并激活环境
        try:
            if sys.platform == 'win32':
                # Windows
                script_content = f"@echo off\necho 正在激活环境 {env_name}...\ncmd /k \"{activate_script}\""
                temp_script = os.path.join(os.environ["TEMP"], "activate_env.bat")
                with open(temp_script, "w") as f:
                    f.write(script_content)
                
                os.startfile(temp_script)
            elif sys.platform == 'darwin':
                # macOS
                script_content = f"#!/bin/bash\necho '正在激活环境 {env_name}...'\nsource \"{activate_script}\"\nexec bash"
                temp_script = os.path.join("/tmp", "activate_env.sh")
                with open(temp_script, "w") as f:
                    f.write(script_content)
                os.chmod(temp_script, 0o755)
                
                os.system(f"open -a Terminal {temp_script}")
            else:
                # Linux
                script_content = f"#!/bin/bash\necho '正在激活环境 {env_name}...'\nsource \"{activate_script}\"\nexec bash"
                temp_script = os.path.join("/tmp", "activate_env.sh")
                with open(temp_script, "w") as f:
                    f.write(script_content)
                os.chmod(temp_script, 0o755)
                
                # 尝试几种不同的终端
                for terminal in ["gnome-terminal", "xterm", "konsole", "terminator"]:
                    try:
                        subprocess.Popen([terminal, "-e", temp_script])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    messagebox.showerror("错误", "无法找到终端程序")
            
            self.update_status(f"已打开终端并激活环境 {env_name}")
        
        except Exception as e:
            messagebox.showerror("错误", f"激活环境时出错: {str(e)}")

    def generate_activation_scripts(self):
        """为所有环境生成激活脚本"""
        script_dir = filedialog.askdirectory(title="选择保存脚本的目录")
        if not script_dir:
            return
        
        try:
            # 为基础环境生成脚本
            for env_name in self.base_envs:
                if sys.platform == 'win32':
                    script_path = os.path.join(script_dir, f"activate_{env_name}.bat")
                    with open(script_path, "w") as f:
                        f.write(f"@echo off\necho 正在激活环境 {env_name}...\nconda activate {env_name}\ncmd /k")
                else:
                    script_path = os.path.join(script_dir, f"activate_{env_name}.sh")
                    with open(script_path, "w") as f:
                        f.write(f"#!/bin/bash\necho '正在激活环境 {env_name}...'\nsource $(conda info --base)/etc/profile.d/conda.sh\nconda activate {env_name}\nexec bash")
                    os.chmod(script_path, 0o755)
            
            # 为项目环境生成脚本
            for env in self.config["project_envs"]:
                env_name = env["name"]
                if sys.platform == 'win32':
                    activate_script = os.path.join(env["path"], "Scripts", "activate.bat")
                    script_path = os.path.join(script_dir, f"activate_{env_name}.bat")
                    
                    with open(script_path, "w") as f:
                        f.write(f"@echo off\necho 正在激活环境 {env_name}...\ncall \"{activate_script}\"\ncmd /k")
                else:
                    activate_script = os.path.join(env["path"], "bin", "activate")
                    script_path = os.path.join(script_dir, f"activate_{env_name}.sh")
                    
                    with open(script_path, "w") as f:
                        f.write(f"#!/bin/bash\necho '正在激活环境 {env_name}...'\nsource \"{activate_script}\"\nexec bash")
                    os.chmod(script_path, 0o755)
            
            messagebox.showinfo("成功", f"所有激活脚本已保存到 {script_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成脚本时出错: {str(e)}")

    def export_env_list(self):
        """导出环境列表"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            export_data = {
                "base_envs": self.base_envs,
                "project_envs": self.config["project_envs"]
            }
            
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("成功", f"环境列表已导出到 {file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出环境列表时出错: {str(e)}")

    def clean_conda_cache(self):
        """清理Conda缓存"""
        if messagebox.askyesno("确认", "确定要清理Conda缓存吗？"):
            self.status_var.set("正在清理Conda缓存...")
            threading.Thread(target=self._clean_conda_cache).start()

    def _clean_conda_cache(self):
        """在后台线程清理Conda缓存"""
        try:
            conda_path = self.get_conda_path()
            cmd = f"{conda_path} clean --all -y"
            
            if sys.platform == 'win32':
                process = subprocess.Popen(['cmd.exe', '/c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            else:
                process = subprocess.Popen(['/bin/bash', '-c', cmd], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                self.update_console(line)
                if not line:
                    break
            
            process.stdout.close()
            returncode = process.wait()
            
            if returncode == 0:
                self.update_console("\n✅ Conda缓存清理成功！\n")
                self.update_status("Conda缓存清理成功")
            else:
                self.update_console(f"\n❌ 缓存清理失败，退出代码: {returncode}\n")
                self.update_status("缓存清理失败")
        
        except Exception as e:
            self.update_console(f"\n❌ 异常: {str(e)}\n")
            self.update_status(f"异常: {str(e)}")

    def browse_conda_path(self):
        """浏览Conda可执行文件路径"""
        file_path = filedialog.askopenfilename(
            title="选择Conda可执行文件",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")] if sys.platform == 'win32' else [("All files", "*")]
        )
        if file_path:
            self.conda_path_var.set(file_path)

    def apply_conda_path(self):
        """应用Conda路径设置"""
        conda_path = self.conda_path_var.get()
        if conda_path:
            self.config['conda_path'] = conda_path
            self.save_config()
            messagebox.showinfo("成功", "Conda路径已更新")
            
            # 刷新环境列表
            self.refresh_env_lists()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythonEnvManager(root)
    root.mainloop()