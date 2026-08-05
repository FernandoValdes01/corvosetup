#!/usr/bin/env python3
"""Desktop UI and background profile keeper for Logitech lighting."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
import tkinter as tk
from tkinter import colorchooser, ttk

from hardware import HardwareError, LogitechLights
from settings import CONFIG_FILE, hardware_lock, load_settings, save_settings

COLORS = ["#00AEEF", "#7C5CFC", "#FF3B81", "#FF6B35", "#20D991", "#FFFFFF"]
ZONE_NAMES = ["Izquierda", "Centro izq.", "Centro der.", "Flechas", "Numerico"]


def apply_available(lights: LogitechLights, settings: dict, keyboard: bool = True, headset: bool = True) -> list[str]:
    errors: list[str] = []
    with hardware_lock():
        statuses = lights.statuses()
        for selected, key, label, apply in (
            (keyboard, "keyboard", "G213", lights.apply_keyboard),
            (headset, "headset", "G733", lights.apply_headset),
        ):
            if selected and statuses[key].accessible:
                try:
                    apply(settings[key])
                except HardwareError as error:
                    errors.append(f"{label}: {error}")
            elif selected and statuses[key].connected:
                errors.append(f"{label}: sin permisos HID")
    return errors


def run_daemon() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    try:
        lights = LogitechLights()
    except HardwareError as error:
        logging.error("No se pudo iniciar: %s", error)
        return 1
    running = True

    def stop(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    last_headset_connected = False
    last_config_mtime = -1.0
    while running:
        settings = load_settings()
        try:
            config_mtime = CONFIG_FILE.stat().st_mtime
        except OSError:
            config_mtime = 0.0
        statuses = lights.statuses()
        errors = apply_available(
            lights,
            settings,
            keyboard=True,
            headset=(statuses["headset"].accessible and not last_headset_connected) or config_mtime != last_config_mtime,
        )
        for error in errors:
            logging.warning(error)
        last_headset_connected = statuses["headset"].accessible
        last_config_mtime = config_mtime
        for _ in range(25):
            if not running:
                break
            time.sleep(1)
    return 0


class LightManagerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Logitech Light Manager")
        self.geometry("820x660")
        self.minsize(700, 590)
        self.configure(bg="#10131A")
        self.settings = load_settings()
        self.lights: LogitechLights | None = None
        self.selected_keyboard_zone = 0
        self.keyboard_enabled = tk.BooleanVar(value=self.settings["keyboard"]["enabled"])
        self.headset_enabled = tk.BooleanVar(value=self.settings["headset"]["enabled"])
        self.headset_sync = tk.BooleanVar(value=self.settings["headset"].get("sync", True))
        self.brightness = tk.IntVar(value=self.settings["headset"].get("brightness", 100))
        self.status_text = tk.StringVar(value="Detectando dispositivos...")
        self._configure_styles()
        self._build_ui()
        try:
            self.lights = LogitechLights()
        except HardwareError as error:
            self.status_text.set(str(error))
        self.after(100, self.refresh_status)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        for name, background in (("App.TFrame", "#10131A"), ("Card.TFrame", "#1A1F2B")):
            style.configure(name, background=background)
        style.configure("Title.TLabel", background="#10131A", foreground="#F7F9FC", font=("Sans", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#10131A", foreground="#8F9AAD", font=("Sans", 10))
        style.configure("CardTitle.TLabel", background="#1A1F2B", foreground="#F7F9FC", font=("Sans", 15, "bold"))
        style.configure("Body.TLabel", background="#1A1F2B", foreground="#B7C0D1", font=("Sans", 10))
        style.configure("Status.TLabel", background="#10131A", foreground="#7ED6A5", font=("Sans", 10))
        style.configure("TCheckbutton", background="#1A1F2B", foreground="#E8ECF3")
        style.configure("Accent.TButton", background="#5E7DFF", foreground="white", borderwidth=0, padding=(18, 10))
        style.configure("Zone.TButton", background="#282F3F", foreground="#DDE3EE", borderwidth=0, padding=(10, 8))

    def _build_ui(self) -> None:
        root = ttk.Frame(self, style="App.TFrame", padding=28)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Luces Logitech", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Control para G213 y G733", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 18))
        self._build_keyboard_card(root)
        self._build_headset_card(root)
        footer = ttk.Frame(root, style="App.TFrame")
        footer.pack(fill="x", pady=(18, 0))
        ttk.Label(footer, textvariable=self.status_text, style="Status.TLabel").pack(side="left")
        ttk.Button(footer, text="Guardar y aplicar", style="Accent.TButton", command=self.save_and_apply).pack(side="right")

    def _build_keyboard_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 14))
        heading = ttk.Frame(card, style="Card.TFrame")
        heading.pack(fill="x")
        ttk.Label(heading, text="Teclado G213", style="CardTitle.TLabel").pack(side="left")
        ttk.Checkbutton(heading, text="Encendido", variable=self.keyboard_enabled).pack(side="right")
        zones = ttk.Frame(card, style="Card.TFrame")
        zones.pack(fill="x", pady=(12, 0))
        for index, name in enumerate(ZONE_NAMES):
            ttk.Button(zones, text=name, style="Zone.TButton", command=lambda value=index: self.select_keyboard_zone(value)).pack(side="left", expand=True, fill="x", padx=2)
        palette = ttk.Frame(card, style="Card.TFrame")
        palette.pack(fill="x", pady=(14, 0))
        self.keyboard_preview = tk.Label(palette, width=5, height=2, bg=self.settings["keyboard"]["zones"][0])
        self.keyboard_preview.pack(side="left", padx=(0, 12))
        for color in COLORS:
            self._color_button(palette, color, lambda value=color: self.set_keyboard_color(value))
        ttk.Button(palette, text="Personalizado", command=self.pick_keyboard_color).pack(side="left", padx=8)
        ttk.Button(palette, text="Mismo color en todo", command=self.copy_keyboard_color).pack(side="right")

    def _build_headset_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x")
        heading = ttk.Frame(card, style="Card.TFrame")
        heading.pack(fill="x")
        ttk.Label(heading, text="Audifonos G733", style="CardTitle.TLabel").pack(side="left")
        ttk.Checkbutton(heading, text="Encendidos", variable=self.headset_enabled).pack(side="right")
        self.headset_previews: dict[str, tk.Label] = {}
        zones = ttk.Frame(card, style="Card.TFrame")
        zones.pack(fill="x", pady=(12, 0))
        for key, label in (("top", "Zona superior"), ("bottom", "Zona inferior")):
            area = ttk.Frame(zones, style="Card.TFrame")
            area.pack(side="left", fill="x", expand=True)
            ttk.Label(area, text=label, style="Body.TLabel").pack(anchor="w")
            row = ttk.Frame(area, style="Card.TFrame")
            row.pack(fill="x", pady=6)
            preview = tk.Label(row, width=5, height=2, bg=self.settings["headset"][key])
            preview.pack(side="left", padx=(0, 10))
            self.headset_previews[key] = preview
            for color in COLORS[:5]:
                self._color_button(row, color, lambda value=color, zone=key: self.set_headset_color(zone, value))
            ttk.Button(row, text="+", command=lambda zone=key: self.pick_headset_color(zone)).pack(side="left")
        controls = ttk.Frame(card, style="Card.TFrame")
        controls.pack(fill="x")
        ttk.Checkbutton(controls, text="Mismo color en ambas zonas", variable=self.headset_sync, command=self.sync_headset_colors).pack(side="left")
        ttk.Label(controls, text="Brillo", style="Body.TLabel").pack(side="left", padx=(30, 8))
        tk.Scale(controls, from_=10, to=100, orient="horizontal", variable=self.brightness, bg="#1A1F2B", fg="#DDE3EE", highlightthickness=0).pack(side="left")

    @staticmethod
    def _color_button(parent: ttk.Frame, color: str, command: object) -> None:
        tk.Button(parent, bg=color, activebackground=color, width=2, height=1, relief="flat", bd=0, command=command).pack(side="left", padx=3)

    def select_keyboard_zone(self, index: int) -> None:
        self.selected_keyboard_zone = index
        self.keyboard_preview.configure(bg=self.settings["keyboard"]["zones"][index])

    def set_keyboard_color(self, color: str) -> None:
        self.settings["keyboard"]["zones"][self.selected_keyboard_zone] = color.upper()
        self.keyboard_preview.configure(bg=color)

    def pick_keyboard_color(self) -> None:
        selected = colorchooser.askcolor(self.settings["keyboard"]["zones"][self.selected_keyboard_zone])[1]
        if selected:
            self.set_keyboard_color(selected)

    def copy_keyboard_color(self) -> None:
        color = self.settings["keyboard"]["zones"][self.selected_keyboard_zone]
        self.settings["keyboard"]["zones"] = [color] * 5

    def set_headset_color(self, zone: str, color: str) -> None:
        self.settings["headset"][zone] = color.upper()
        self.headset_previews[zone].configure(bg=color)
        if self.headset_sync.get():
            other = "bottom" if zone == "top" else "top"
            self.settings["headset"][other] = color.upper()
            self.headset_previews[other].configure(bg=color)

    def pick_headset_color(self, zone: str) -> None:
        selected = colorchooser.askcolor(self.settings["headset"][zone])[1]
        if selected:
            self.set_headset_color(zone, selected)

    def sync_headset_colors(self) -> None:
        if self.headset_sync.get():
            self.set_headset_color("top", self.settings["headset"]["top"])

    def refresh_status(self) -> None:
        if self.lights:
            statuses = self.lights.statuses()
            self.status_text.set(" | ".join(f"{label}: {statuses[key].detail}" for label, key in (("G213", "keyboard"), ("G733", "headset"))))
        self.after(2000, self.refresh_status)

    def save_and_apply(self) -> None:
        self.settings["keyboard"]["enabled"] = self.keyboard_enabled.get()
        self.settings["headset"].update(enabled=self.headset_enabled.get(), sync=self.headset_sync.get(), brightness=self.brightness.get())
        save_settings(self.settings)
        if self.lights:
            errors = apply_available(self.lights, self.settings)
            self.status_text.set("Cambios aplicados" if not errors else " | ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Administrador de luces Logitech")
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.daemon:
        return run_daemon()
    if args.apply:
        try:
            errors = apply_available(LogitechLights(), load_settings())
        except HardwareError as error:
            print(error, file=sys.stderr)
            return 1
        return bool(errors)
    LightManagerApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
