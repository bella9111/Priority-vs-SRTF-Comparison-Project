# main.py
from config import setup_ctk_theme
from app_ui import SchedulerApp

if __name__ == "__main__":
    setup_ctk_theme()
    app = SchedulerApp()
    app.mainloop()
