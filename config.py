# config.py
import customtkinter as ctk

BG = "#0d0f14"
SURFACE = "#13161e"
SURFACE2 = "#1a1d27"
TEXT = "#e2e8f0"
PRI_COL = "#818cf8"
SRTF_COL = "#34d399"
ACCENT = "#f59e0b"
DANGER = "#ef4444"
SUCCESS = "#22c55e"

PROCESS_COLORS = ["#818cf8", "#34d399", "#f59e0b", "#ec4899", "#38bdf8", "#a78bfa", "#fb923c"]

SCENARIOS = {
    "A: Basic": [
        {"pid": "P1", "at": 0, "bt": 8, "pr": 3},
        {"pid": "P2", "at": 1, "bt": 4, "pr": 1},
        {"pid": "P3", "at": 2, "bt": 9, "pr": 4},
        {"pid": "P4", "at": 3, "bt": 5, "pr": 2}
    ],
    "B: Priority vs Burst": [
        {"pid": "P1", "at": 0, "bt": 12, "pr": 1},
        {"pid": "P2", "at": 2, "bt": 2, "pr": 4},
        {"pid": "P3", "at": 3, "bt": 3, "pr": 5},
        {"pid": "P4", "at": 5, "bt": 1, "pr": 3}
    ],
    "C: Starvation": [
        {"pid": "P1", "at": 0, "bt": 15, "pr": 5},
        {"pid": "P2", "at": 1, "bt": 2,  "pr": 1},
        {"pid": "P3", "at": 2, "bt": 2,  "pr": 1},
        {"pid": "P4", "at": 3, "bt": 2,  "pr": 1},
        {"pid": "P5", "at": 4, "bt": 2,  "pr": 1}
    ],
    "Same Priority": [
        {"pid": "P1", "at": 0, "bt": 6, "pr": 2},
        {"pid": "P2", "at": 1, "bt": 2, "pr": 2},
        {"pid": "P3", "at": 3, "bt": 8, "pr": 2},
        {"pid": "P4", "at": 4, "bt": 3, "pr": 2}
    ],
    "Same Burst": [
        {"pid": "P1", "at": 0, "bt": 5, "pr": 3},
        {"pid": "P2", "at": 1, "bt": 5, "pr": 1},
        {"pid": "P3", "at": 2, "bt": 5, "pr": 4},
        {"pid": "P4", "at": 3, "bt": 5, "pr": 2}
    ],
    "Same Arrival": [
        {"pid": "P1", "at": 0, "bt": 7, "pr": 2},
        {"pid": "P2", "at": 0, "bt": 3, "pr": 4},
        {"pid": "P3", "at": 0, "bt": 5, "pr": 1},
        {"pid": "P4", "at": 0, "bt": 2, "pr": 3}
    ],
    "SRTF Starvation": [
        {"pid": "P1", "at": 0, "bt": 20, "pr": 1},
        {"pid": "P2", "at": 2, "bt": 3, "pr": 3},
        {"pid": "P3", "at": 4, "bt": 2, "pr": 3},
        {"pid": "P4", "at": 6, "bt": 1, "pr": 3},
        {"pid": "P5", "at": 8, "bt": 2, "pr": 3}
    ]
}

def setup_ctk_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
