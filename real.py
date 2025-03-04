import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import os  # Added to ensure process handling works across platforms...

class ProcessMonitor:
    def _init_(self, root):
        self.root = root
        self.root.title("Real-Time Process Monitoring Dashboard")
        self.root.geometry("1000x600")
        self.start_time = time.time()  # Moved inside

        # CPU Usage
        self.cpu_label = ttk.Label(root, text="CPU Usage: ", font=("Arial", 12))
        self.cpu_label.pack()
        self.cpu_progress = ttk.Progressbar(root, length=200, mode='determinate')
        self.cpu_progress.pack()

        # Memory Usage
        self.mem_label = ttk.Label(root, text="Memory Usage: ", font=("Arial", 12))
        self.mem_label.pack()
        self.mem_progress = ttk.Progressbar(root, length=200, mode='determinate')
        self.mem_progress.pack()

        # Graph Frame
        self.graph_frame = ttk.Frame(root)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.cpu_usage_data = []
        self.mem_usage_data = []
        self.time_data = []
        self.line_cpu, = self.ax.plot([], [], label="CPU Usage (%)", color='r')
        self.line_mem, = self.ax.plot([], [], label="Memory Usage (%)", color='b')
        self.ax.legend()
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Usage (%)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Process List
        self.process_tree = ttk.Treeview(root, columns=("PID", "Name", "CPU%", "Memory%"), show='headings')
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Name")
        self.process_tree.heading("CPU%", text="CPU%", command=lambda: self.sort_tree(2))
        self.process_tree.heading("Memory%", text="Memory%", command=lambda: self.sort_tree(3))
        self.process_tree.pack(fill=tk.BOTH, expand=True)

        # Buttons for process control
        self.kill_button = ttk.Button(root, text="Kill Process", command=self.kill_process)
        self.kill_button.pack()

        self.suspend_button = ttk.Button(root, text="Suspend Process", command=self.suspend_process)
        self.suspend_button.pack()

        self.resume_button = ttk.Button(root, text="Resume Process", command=self.resume_process)
        self.resume_button.pack()

        # Start updating UI
        self.update_ui()
        self.update_graph()

    def update_ui(self):
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.cpu_progress['value'] = cpu_usage
        self.mem_label.config(text=f"Memory Usage: {mem_usage}%")
        self.mem_progress['value'] = mem_usage

        # Update Process List
        for row in self.process_tree.get_children():
            self.process_tree.delete(row)

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            self.process_tree.insert("", tk.END, values=(proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], proc.info['memory_percent']))

        # Refresh every second
        self.root.after(1000, self.update_ui)

    def update_graph(self):
        self.cpu_usage_data.append(psutil.cpu_percent())
        self.mem_usage_data.append(psutil.virtual_memory().percent)
        self.time_data.append(time.time() - self.start_time)

        if len(self.time_data) > 50:
            self.cpu_usage_data.pop(0)
            self.mem_usage_data.pop(0)
            self.time_data.pop(0)

        self.line_cpu.set_data(self.time_data, self.cpu_usage_data)
        self.line_mem.set_data(self.time_data, self.mem_usage_data)

        self.ax.set_xlim(self.time_data[0] if self.time_data else 0, self.time_data[-1] if self.time_data else 50)
        self.ax.set_ylim(0, 100)

        self.canvas.draw()
        self.root.after(1000, self.update_graph)

    def kill_process(self):
        selected_item = self.process_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No process selected!")
            return

        pid = self.process_tree.item(selected_item)['values'][0]
        try:
            process = psutil.Process(pid)
            process.terminate()
            messagebox.showinfo("Success", f"Process {pid} terminated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def suspend_process(self):
        selected_item = self.process_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No process selected!")
            return

        pid = self.process_tree.item(selected_item)['values'][0]
        try:
            process = psutil.Process(pid)
            process.suspend()
            messagebox.showinfo("Success", f"Process {pid} suspended.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def resume_process(self):
        selected_item = self.process_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No process selected!")
            return

        pid = self.process_tree.item(selected_item)['values'][0]
        try:
            process = psutil.Process(pid)
            process.resume()
            messagebox.showinfo("Success", f"Process {pid} resumed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def sort_tree(self, col):
        items = [(self.process_tree.set(k, col), k) for k in self.process_tree.get_children('')]
        items.sort(reverse=True, key=lambda x: float(x[0]) if x[0] else 0)
        for index, (val, k) in enumerate(items):
            self.process_tree.move(k, '', index)

if _name_ == "_main_":
    root = tk.Tk()
    app = ProcessMonitor(root)
    root.mainloop()
