# app_ui.py - Single-Page Layout
import tkinter as tk
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import BG, SURFACE, SURFACE2, TEXT, PRI_COL, SRTF_COL, ACCENT, DANGER, SUCCESS, SCENARIOS, PROCESS_COLORS
from scheduler_logic import simulate_priority, simulate_srtf, avg, detect_starvation, generate_comparison


def validate_pid(pid, existing_pids):
    if not pid:
        return "Process ID cannot be empty."
    if not pid.isalnum():
        return "Process ID must be letters and numbers only (e.g. P1, A2)."
    if pid in existing_pids:
        return f"Process ID '{pid}' already exists."
    return None


def validate_number(value, field_name, allow_zero=True):
    try:
        v = int(value)
        if not allow_zero and v <= 0:
            return f"{field_name} must be a positive integer greater than 0."
        if allow_zero and v < 0:
            return f"{field_name} must be 0 or greater."
        return None
    except ValueError:
        return f"{field_name} must be a whole number (e.g. 0, 3, 10). No letters or decimals."


class SchedulerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Priority vs SRTF Scheduling Simulator")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=BG)
        self.processes = []
        self.gantt_canvas_widget = None
        self.gantt_fig = None
        self.build_ui()

    def build_ui(self):
        title_bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=56)
        title_bar.pack(fill="x", padx=0, pady=0)
        title_bar.pack_propagate(False)
        ctk.CTkLabel(title_bar, text="Priority vs SRTF Scheduling Simulator",
                     font=("Consolas", 20, "bold"), text_color="#818cf8").pack(side="left", padx=20, pady=10)

    
        self.main_canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self, command=self.main_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = ctk.CTkFrame(self.main_canvas, fg_color=BG)
        self.scroll_window = self.main_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

      
        self._build_input_section()
        self._build_process_table_section()
        self._build_gantt_section()
        self._build_results_section()
        self._build_comparison_section()
        self._build_conclusion_section()

    
    def _on_frame_configure(self, event=None):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.scroll_window, width=event.width)

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

  
    def _section_header(self, parent, text, color="#818cf8", icon=""):
        hdr = ctk.CTkFrame(parent, fg_color=SURFACE2, corner_radius=8, height=40)
        hdr.pack(fill="x", padx=16, pady=(16, 6))
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"{icon}  {text}" if icon else text,
                     font=("Consolas", 13, "bold"), text_color=color).pack(side="left", padx=14)
  

    
    def _build_input_section(self):
        self._section_header(self.scroll_frame, "Input Panel", "#818cf8", "①")

        panel = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10)
        panel.pack(fill="x", padx=16, pady=(0, 4))

        lbl_row = ctk.CTkFrame(panel, fg_color="transparent")
        lbl_row.pack(fill="x", padx=12, pady=(10, 2))
        for lbl in ["Process ID", "Arrival Time", "Burst Time", "Priority (1=highest)"]:
            ctk.CTkLabel(lbl_row, text=lbl, font=("Consolas", 11),
                         text_color="#94a3b8", width=140).pack(side="left", padx=4)

        entry_kw = {"width": 140, "fg_color": SURFACE2, "text_color": TEXT,
                    "border_color": "#4a4d5a", "font": ("Consolas", 12)}
        form = ctk.CTkFrame(panel, fg_color="transparent")
        form.pack(fill="x", padx=12, pady=(0, 10))

        self.pid_entry = ctk.CTkEntry(form, placeholder_text="e.g. P1", **entry_kw)
        self.pid_entry.pack(side="left", padx=4)
        self.at_entry = ctk.CTkEntry(form, placeholder_text="e.g. 0", **entry_kw)
        self.at_entry.pack(side="left", padx=4)
        self.bt_entry = ctk.CTkEntry(form, placeholder_text="e.g. 5", **entry_kw)
        self.bt_entry.pack(side="left", padx=4)
        self.pr_entry = ctk.CTkEntry(form, placeholder_text="e.g. 2", **entry_kw)
        self.pr_entry.pack(side="left", padx=4)

        add_btn = ctk.CTkButton(form, text="+ Add Process", width=140,
                                fg_color="#3b82f6", hover_color="#2563eb",
                                font=("Consolas", 12, "bold"), command=self.add_process)
        add_btn.pack(side="left", padx=10)

        self.warn_label = ctk.CTkLabel(panel, text="", font=("Consolas", 11), text_color=DANGER)
        self.warn_label.pack(pady=(0, 4))

      
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(pady=(0, 8))

        run_btn = ctk.CTkButton(btn_row, text="▶  RUN SIMULATION",
                                fg_color="#10b981", hover_color="#059669",
                                font=("Consolas", 14, "bold"), width=200, height=38,
                                command=self.run_simulation)
        run_btn.pack(side="left", padx=8)

        clear_btn = ctk.CTkButton(btn_row, text="Clear All",
                                  fg_color=SURFACE2, hover_color="#374151",
                                  font=("Consolas", 12), width=100, height=38,
                                  command=self.clear_all)
        clear_btn.pack(side="left", padx=4)

        ctk.CTkLabel(panel, text="Load Test Scenario:",
                     font=("Consolas", 11), text_color="#64748b").pack()
        sc_frame = ctk.CTkFrame(panel, fg_color="transparent")
        sc_frame.pack(pady=(2, 12))
        colors = ["#4b5563", "#1d4ed8", "#7c3aed", "#b45309", "#991b1b"]
        for i, name in enumerate(SCENARIOS):
            c = colors[i % len(colors)]
            ctk.CTkButton(sc_frame, text=name, width=130, height=28,
                          fg_color=c, hover_color="#374151",
                          font=("Consolas", 11),
                          command=lambda n=name: self.load_scenario(n)).pack(side="left", padx=4)

    
    def _build_process_table_section(self):
        self._section_header(self.scroll_frame, "Process Table", "#38bdf8", "②")

        table_outer = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10)
        table_outer.pack(fill="x", padx=16, pady=(0, 4))

        hdr_frame = ctk.CTkFrame(table_outer, fg_color=SURFACE2, corner_radius=6)
        hdr_frame.pack(fill="x", padx=8, pady=(8, 0))
        for col, (lbl, w) in enumerate([("PID", 80), ("Arrival", 100), ("Burst", 100), ("Priority", 120), ("", 60)]):
            ctk.CTkLabel(hdr_frame, text=lbl, font=("Consolas", 11, "bold"),
                         text_color="#818cf8", width=w).grid(row=0, column=col, padx=6, pady=6)

        self.proc_scroll = ctk.CTkScrollableFrame(table_outer, fg_color=SURFACE, height=160, corner_radius=6)
        self.proc_scroll.pack(fill="x", padx=8, pady=(2, 10))

    
    def _build_gantt_section(self):
        self._section_header(self.scroll_frame, "Gantt Chart — Priority Scheduling", PRI_COL, "③")
        self.gantt_pri_frame = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10, height=180)
        self.gantt_pri_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(self.gantt_pri_frame, text="Run simulation to see Gantt Chart",
                     font=("Consolas", 13), text_color="#475569").pack(expand=True, pady=60)

        self._section_header(self.scroll_frame, "Gantt Chart — SRTF Scheduling", SRTF_COL, "④")
        self.gantt_srtf_frame = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10, height=180)
        self.gantt_srtf_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(self.gantt_srtf_frame, text="Run simulation to see Gantt Chart",
                     font=("Consolas", 13), text_color="#475569").pack(expand=True, pady=60)

  

    def _build_results_section(self):
        self._section_header(self.scroll_frame, "Results Table — Priority Scheduling", PRI_COL, "⑤")
        self.pri_results_frame = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10)
        self.pri_results_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(self.pri_results_frame, text="Run simulation to see results.",
                     font=("Consolas", 12), text_color="#475569").pack(pady=20)

        self._section_header(self.scroll_frame, "Results Table — SRTF Scheduling", SRTF_COL, "⑥")
        self.srtf_results_frame = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10)
        self.srtf_results_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(self.srtf_results_frame, text="Run simulation to see results.",
                     font=("Consolas", 12), text_color="#475569").pack(pady=20)

    
    def _build_comparison_section(self):
        self._section_header(self.scroll_frame, "Comparison Summary", ACCENT, "⑦")
        self.comparison_frame = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10)
        self.comparison_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(self.comparison_frame, text="Run simulation to see comparison.",
                     font=("Consolas", 12), text_color="#475569").pack(pady=20)

    
    def _build_conclusion_section(self):
        self._section_header(self.scroll_frame, "Final Conclusion", SUCCESS, "⑧")
        self.conclusion_outer = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE, corner_radius=10)
        self.conclusion_outer.pack(fill="x", padx=16, pady=(0, 24))
        self.conclusion_text = tk.Text(self.conclusion_outer, bg="#0d0f14", fg="#facc15",
                                       font=("Consolas", 12), relief="flat",
                                       padx=20, pady=16, insertbackground="white",
                                       height=8)
        self.conclusion_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.conclusion_text.insert("end", "Run simulation to see Final Conclusion.\n")
        self.conclusion_text.configure(state="disabled")

  
    def add_process(self):
        self.warn_label.configure(text="")
        pid = self.pid_entry.get().strip()
        at_raw = self.at_entry.get().strip()
        bt_raw = self.bt_entry.get().strip()
        pr_raw = self.pr_entry.get().strip()

        existing_pids = [p['pid'] for p in self.processes]

        err = validate_pid(pid, existing_pids)
        if err:
            self.warn_label.configure(text=f"WARNING: {err}")
            return
        err = validate_number(at_raw, "Arrival Time", allow_zero=True)
        if err:
            self.warn_label.configure(text=f"WARNING: {err}")
            return
        err = validate_number(bt_raw, "Burst Time", allow_zero=False)
        if err:
            self.warn_label.configure(text=f"WARNING: {err}")
            return
        err = validate_number(pr_raw, "Priority", allow_zero=False)
        if err:
            self.warn_label.configure(text=f"WARNING: {err}")
            return

        self.processes.append({"pid": pid, "at": int(at_raw), "bt": int(bt_raw), "pr": int(pr_raw)})
        self.refresh_process_table()
        for e in [self.pid_entry, self.at_entry, self.bt_entry, self.pr_entry]:
            e.delete(0, "end")
        self.pid_entry.focus()

    def refresh_process_table(self):
        for widget in self.proc_scroll.winfo_children():
            widget.destroy()
        for i, p in enumerate(self.processes):
            color = PROCESS_COLORS[i % len(PROCESS_COLORS)]
            row_bg = SURFACE if i % 2 == 0 else SURFACE2
            row = ctk.CTkFrame(self.proc_scroll, fg_color=row_bg, corner_radius=4)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=p['pid'], font=("Consolas", 12, "bold"),
                         text_color=color, width=80).grid(row=0, column=0, padx=6, pady=4)
            ctk.CTkLabel(row, text=str(p['at']), font=("Consolas", 12),
                         text_color=TEXT, width=100).grid(row=0, column=1, padx=6)
            ctk.CTkLabel(row, text=str(p['bt']), font=("Consolas", 12),
                         text_color=TEXT, width=100).grid(row=0, column=2, padx=6)
            ctk.CTkLabel(row, text=str(p['pr']), font=("Consolas", 12),
                         text_color=TEXT, width=120).grid(row=0, column=3, padx=6)
            idx = i
            del_btn = ctk.CTkButton(row, text="x", width=30, height=24,
                                    fg_color=DANGER, hover_color="#b91c1c",
                                    font=("Consolas", 11),
                                    command=lambda ix=idx: self.delete_process(ix))
            del_btn.grid(row=0, column=4, padx=6)

    def delete_process(self, idx):
        self.processes.pop(idx)
        self.refresh_process_table()

    def clear_all(self):
        self.processes = []
        self.refresh_process_table()
        self.warn_label.configure(text="")

    def load_scenario(self, name):
        self.processes = [dict(p) for p in SCENARIOS[name]]
        self.refresh_process_table()
        self.warn_label.configure(text="")

    
    def run_simulation(self):
        self.warn_label.configure(text="")
        if len(self.processes) < 2:
            self.warn_label.configure(text="WARNING: Please add at least 2 processes before running.")
            return

        pri_ps, pri_tl = simulate_priority(self.processes)
        srtf_ps, srtf_tl = simulate_srtf(self.processes)

        self._draw_gantt_chart(self.gantt_pri_frame, pri_tl, pri_ps + srtf_ps,
                               "Priority Scheduling", PRI_COL)
        self._draw_gantt_chart(self.gantt_srtf_frame, srtf_tl, pri_ps + srtf_ps,
                               "SRTF (Shortest Remaining Time First)", SRTF_COL)

        self.render_results_table(self.pri_results_frame, pri_ps, PRI_COL)
        self.render_results_table(self.srtf_results_frame, srtf_ps, SRTF_COL)

        self._render_comparison(pri_ps, srtf_ps)
        self._render_conclusion(pri_ps, srtf_ps)

        self.main_canvas.yview_moveto(0)

    
    def _draw_gantt_chart(self, parent_frame, timeline, all_ps, title, title_color):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        plt.style.use("dark_background")
        fig, ax = plt.subplots(1, 1, figsize=(13, 2.6))
        fig.patch.set_facecolor(BG)

        all_pids = list(dict.fromkeys([p['pid'] for p in all_ps]))
        color_map = {pid: PROCESS_COLORS[i % len(PROCESS_COLORS)] for i, pid in enumerate(all_pids)}

        for pid, s, e in timeline:
            ax.barh(0, e - s, left=s, color=color_map.get(pid, "#818cf8"),
                    edgecolor="#0d0f14", linewidth=0.8, height=0.5)
            if e - s > 0.5:
                ax.text((s + e) / 2, 0, pid, ha="center", va="center",
                        color="white", fontweight="bold", fontsize=9, fontfamily="monospace")
            ax.text(s, -0.38, str(s), ha="center", va="top",
                    color="#64748b", fontsize=7)
        if timeline:
            last_end = timeline[-1][2]
            ax.text(last_end, -0.38, str(last_end), ha="center", va="top",
                    color="#64748b", fontsize=7)

        ax.set_title(title, color=title_color, fontsize=11,
                     fontfamily="monospace", loc="left", pad=8)
        ax.set_yticks([])
        ax.set_facecolor(SURFACE)
        for sp in ["top", "left", "right"]:
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color("#334155")
        ax.tick_params(colors="#475569", labelsize=8)

        legend_patches = [mpatches.Patch(color=color_map[pid], label=pid) for pid in all_pids]
        fig.legend(handles=legend_patches, loc="lower right", ncol=len(all_pids),
                   framealpha=0.2, fontsize=9)

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig)

    
    def render_results_table(self, parent, ps, color):
        for w in parent.winfo_children():
            w.destroy()
        headers = ["PID", "Arrival", "Burst", "Priority", "Finish", "WT", "TAT", "RT"]
        widths  = [70,     80,       70,     90,        80,       70,   70,   70]
        hdr = ctk.CTkFrame(parent, fg_color=SURFACE2, corner_radius=6)
        hdr.pack(fill="x", padx=8, pady=(8, 0))
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(hdr, text=h, font=("Consolas", 11, "bold"),
                         text_color=color, width=w).grid(row=0, column=i, padx=4, pady=6)
        for ri, p in enumerate(ps):
            bg = SURFACE if ri % 2 == 0 else SURFACE2
            row = ctk.CTkFrame(parent, fg_color=bg, corner_radius=0)
            row.pack(fill="x", padx=8, pady=1)
            vals = [p['pid'], p['at'], p['bt'], p['pr'], p['ft'], p['wt'], p['tat'], p['rt']]
            for i, (val, w) in enumerate(zip(vals, widths)):
                tc = color if i == 0 else TEXT
                ctk.CTkLabel(row, text=str(val), font=("Consolas", 11),
                             text_color=tc, width=w).grid(row=0, column=i, padx=4, pady=4)
        avg_row = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=0)
        avg_row.pack(fill="x", padx=8, pady=(2, 10))
        ctk.CTkLabel(avg_row, text="AVERAGE", font=("Consolas", 11, "bold"),
                     text_color=ACCENT, width=70).grid(row=0, column=0, padx=4, pady=4)
        for i in range(1, 5):
            ctk.CTkLabel(avg_row, text="", width=widths[i]).grid(row=0, column=i, padx=4)
        for i, key in enumerate(['wt', 'tat', 'rt']):
            ctk.CTkLabel(avg_row, text=f"{avg(ps, key):.2f}",
                         font=("Consolas", 11, "bold"), text_color=ACCENT,
                         width=widths[5 + i]).grid(row=0, column=5 + i, padx=4, pady=4)


    def _render_comparison(self, pri_ps, srtf_ps):
        for w in self.comparison_frame.winfo_children():
            w.destroy()

        p_awt  = avg(pri_ps, 'wt');   s_awt  = avg(srtf_ps, 'wt')
        p_atat = avg(pri_ps, 'tat');  s_atat = avg(srtf_ps, 'tat')
        p_art  = avg(pri_ps, 'rt');   s_art  = avg(srtf_ps, 'rt')

        metrics = [
            ("Avg Waiting Time",    p_awt,  s_awt),
            ("Avg Turnaround Time", p_atat, s_atat),
            ("Avg Response Time",   p_art,  s_art),
        ]

        hdr = ctk.CTkFrame(self.comparison_frame, fg_color=SURFACE2, corner_radius=6)
        hdr.pack(fill="x", padx=8, pady=(10, 0))
        for col, (lbl, w, clr) in enumerate([
            ("Metric", 220, "#94a3b8"),
            ("Priority", 160, PRI_COL),
            ("SRTF", 160, SRTF_COL),
            ("Winner", 160, ACCENT),
        ]):
            ctk.CTkLabel(hdr, text=lbl, font=("Consolas", 12, "bold"),
                         text_color=clr, width=w).grid(row=0, column=col, padx=10, pady=8)

        for i, (name, pv, sv) in enumerate(metrics):
            bg = SURFACE if i % 2 == 0 else SURFACE2
            row = ctk.CTkFrame(self.comparison_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x", padx=8, pady=1)
            winner = "SRTF" if sv < pv else ("Priority" if pv < sv else "TIE")
            wc = SRTF_COL if winner == "SRTF" else (PRI_COL if winner == "Priority" else ACCENT)
            ctk.CTkLabel(row, text=name, font=("Consolas", 12),
                         text_color=TEXT, width=220).grid(row=0, column=0, padx=10, pady=6)
            ctk.CTkLabel(row, text=f"{pv:.2f}", font=("Consolas", 12, "bold"),
                         text_color=PRI_COL, width=160).grid(row=0, column=1, padx=10)
            ctk.CTkLabel(row, text=f"{sv:.2f}", font=("Consolas", 12, "bold"),
                         text_color=SRTF_COL, width=160).grid(row=0, column=2, padx=10)
            ctk.CTkLabel(row, text=f"◀ {winner}", font=("Consolas", 12, "bold"),
                         text_color=wc, width=160).grid(row=0, column=3, padx=10)

        from scheduler_logic import detect_starvation
        p_starved = detect_starvation(pri_ps)
        s_starved = detect_starvation(srtf_ps)
        star_row = ctk.CTkFrame(self.comparison_frame, fg_color="#1e293b", corner_radius=6)
        star_row.pack(fill="x", padx=8, pady=(4, 2))
        p_star_txt = f"Risk: {', '.join(p_starved)}" if p_starved else "No starvation"
        s_star_txt = f"Risk: {', '.join(s_starved)}" if s_starved else "No starvation"
        ctk.CTkLabel(star_row, text="Starvation", font=("Consolas", 12),
                     text_color="#94a3b8", width=220).grid(row=0, column=0, padx=10, pady=6)
        ctk.CTkLabel(star_row, text=p_star_txt, font=("Consolas", 11),
                     text_color=DANGER if p_starved else SUCCESS, width=160).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(star_row, text=s_star_txt, font=("Consolas", 11),
                     text_color=DANGER if s_starved else SUCCESS, width=160).grid(row=0, column=2, padx=10)

      
        max_pr   = max(p['pr'] for p in pri_ps)
        avg_bt_p = avg(pri_ps, 'bt')
        short_low = [p for p in pri_ps if p['bt'] <= avg_bt_p and p['pr'] == max_pr]
        short_low_txt = f"Waited avg {avg(short_low, 'wt'):.2f}" if short_low else "No such jobs"

        min_pr   = min(p['pr'] for p in srtf_ps)
        avg_bt_s = avg(srtf_ps, 'bt')
        long_urgent = [p for p in srtf_ps if p['bt'] >= avg_bt_s and p['pr'] == min_pr]
        long_urgent_txt = f"Waited avg {avg(long_urgent, 'wt'):.2f}" if long_urgent else "No such jobs"

        row1 = ctk.CTkFrame(self.comparison_frame, fg_color=SURFACE, corner_radius=6)
        row1.pack(fill="x", padx=8, pady=(2, 0))
        ctk.CTkLabel(row1, text="Short low-priority job", font=("Consolas", 12),
                     text_color="#94a3b8", width=220).grid(row=0, column=0, padx=10, pady=6)
        ctk.CTkLabel(row1, text=short_low_txt, font=("Consolas", 11),
                     text_color=DANGER, width=160).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(row1, text="N/A", font=("Consolas", 11),
                     text_color="#475569", width=160).grid(row=0, column=2, padx=10)

        row2 = ctk.CTkFrame(self.comparison_frame, fg_color=SURFACE2, corner_radius=6)
        row2.pack(fill="x", padx=8, pady=(2, 10))
        ctk.CTkLabel(row2, text="Long high-priority job", font=("Consolas", 12),
                     text_color="#94a3b8", width=220).grid(row=0, column=0, padx=10, pady=6)
        ctk.CTkLabel(row2, text="N/A", font=("Consolas", 11),
                     text_color="#475569", width=160).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(row2, text=long_urgent_txt, font=("Consolas", 11),
                     text_color=DANGER, width=160).grid(row=0, column=2, padx=10)

    
    def _render_conclusion(self, pri_ps, srtf_ps):
        text = generate_comparison(pri_ps, srtf_ps)
        self.conclusion_text.configure(state="normal")
        self.conclusion_text.delete("1.0", "end")
        self.conclusion_text.insert("end", text)
        self.conclusion_text.configure(state="disabled")

        
        lines = text.count('\n') + 1
        self.conclusion_text.configure(height=min(lines + 2, 30))
