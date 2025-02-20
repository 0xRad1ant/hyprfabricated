import subprocess
import re
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox  # <-- use our EventBox
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.overlay import Overlay
from fabric.widgets.revealer import Revealer
from fabric.core.fabricator import Fabricator
from fabric.utils.helpers import exec_shell_command_async

from gi.repository import GLib

import modules.icons as icons

class Battery(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="battery",
            orientation="h",
            spacing=0,
        )

        # Create three buttons for power modes.
        self.bat_save = Button(
            name="battery-save",
            child=Label(name="battery-save-label", markup=icons.power_saving),
            on_clicked=lambda *_: self.set_power_mode("powersave"),
        )
        self.bat_balanced = Button(
            name="battery-balanced",
            child=Label(name="battery-balanced-label", markup=icons.power_balanced),
            on_clicked=lambda *_: self.set_power_mode("balanced"),
        )
        self.bat_perf = Button(
            name="battery-performance",
            child=Label(name="battery-performance-label", markup=icons.power_performance),
            on_clicked=lambda *_: self.set_power_mode("performance"),
        )

        # Attach mouse enter/leave events to buttons as well
        for btn in [self.bat_save, self.bat_balanced, self.bat_perf]:
            btn.connect("enter-notify-event", self.on_mouse_enter)
            btn.connect("leave-notify-event", self.on_mouse_leave)

        # Group the mode buttons into a container.
        self.mode_switcher = Box(
            name="power-mode-switcher",
            orientation="h",
            spacing=4,
            children=[self.bat_save, self.bat_balanced, self.bat_perf],
        )

        self.bat_icon = Label(name="battery-icon", markup=icons.battery)

        self.bat_circle = CircularProgressBar(
            name="battery-circle",
            value=0,
            size=28,
            line_width=2,
        )

        self.bat_overlay = Overlay(
            name="battery-overlay",
            visible=False,
            child=self.bat_circle,
            overlays=[self.bat_icon],
        )

        self.bat_level = Label(
            name="battery-level",
            label="100%",
        )

        self.bat_revealer = Revealer(
            name="battery-revealer",
            transition_duration=250,
            transition_type="slide-left",
            child=self.bat_level,
            child_revealed=False,
        )

        # Create an inner container to hold the battery elements.
        inner_container = Box(orientation="h", spacing=0)
        inner_container.add(self.bat_overlay)
        inner_container.add(self.bat_revealer)
        inner_container.add(self.mode_switcher)

        # Wrap the inner container in an EventBox.
        self.event_box = EventBox(
            events=["enter-notify-event", "leave-notify-event"],
            name="battery-eventbox",
        )
        self.event_box.connect("enter-notify-event", self.on_mouse_enter)
        self.event_box.connect("leave-notify-event", self.on_mouse_leave)
        self.event_box.add(inner_container)

        # Add the EventBox to the Battery widget.
        self.add(self.event_box)

        self.current_mode = None
        # Initialize hide_timer for delayed hiding.
        self.hide_timer = None
        # Initialize counter to track hover status across all related widgets.
        self.hover_counter = 0

        # Initialize Fabricator for battery polling every 5 seconds.
        self.batt_fabricator = Fabricator(lambda *args, **kwargs: self.poll_battery(), interval=5000, stream=False, default_value=0)
        self.batt_fabricator.changed.connect(self.update_battery)

        # Run update_battery immediately at startup.
        GLib.idle_add(self.update_battery, None, self.poll_battery())
        self.set_power_mode("balanced")

    def on_mouse_enter(self, widget, event):
        """Reveal battery level on hover."""
        self.hover_counter += 1
        if self.hide_timer is not None:
            GLib.source_remove(self.hide_timer)
            self.hide_timer = None
        self.bat_revealer.set_reveal_child(True)
        return False

    def on_mouse_leave(self, widget, event):
        """Schedule hiding the battery level after a 0.5s delay only if not hovering any element."""
        if self.hover_counter > 0:
            self.hover_counter -= 1
        if self.hover_counter == 0:
            if self.hide_timer is not None:
                GLib.source_remove(self.hide_timer)
            self.hide_timer = GLib.timeout_add(500, self.hide_revealer)
        return False

    def hide_revealer(self):
        self.bat_revealer.set_reveal_child(False)
        self.hide_timer = None
        return False

    def poll_battery(self):
        """
        Polls the battery status by running the "acpi -b" command.
        If no battery information is found, returns 0.
        Otherwise, returns the battery percentage as a float between 0 and 1.
        """
        try:
            output = subprocess.check_output(["acpi", "-b"]).decode("utf-8").strip()
            if "Battery" not in output:
                return 0
            match = re.search(r'(\d+)%', output)
            if match:
                percent = int(match.group(1))
                return percent / 100.0
        except Exception:
            pass
        return 0

    def update_battery(self, sender, value):
        """
        Updates the battery widget.
          - Hides the battery overlay if no battery is found (value == 0).
          - Otherwise, makes sure the overlay is visible and updates the circular progress bar.
        Additionally, updates the battery level label to show the current percentage.
        """
        if value == 0:
            self.bat_overlay.set_visible(False)
            self.bat_revealer.set_visible(False)
        else:
            self.bat_overlay.set_visible(True)
            self.bat_revealer.set_visible(True)
            self.bat_circle.set_value(value)
        
        # Update the battery level label with the current percentage.
        percentage = int(value * 100)
        self.bat_level.set_label(f"{percentage}%")

    def set_power_mode(self, mode):
        """
        Switches power mode by running the corresponding auto-cpufreq command.
        mode: one of 'powersave', 'balanced', or 'performance'
        """
        commands = {
            "powersave": "sudo auto-cpufreq --force powersave",
            "balanced": "sudo auto-cpufreq --force reset",
            "performance": "sudo auto-cpufreq --force performance",
        }
        if mode in commands:
            try:
                exec_shell_command_async(commands[mode])
                self.current_mode = mode
                self.update_button_styles()
            except Exception as err:
                # Optionally, handle errors or display a notification.
                print(f"Error setting power mode: {err}")

    def update_button_styles(self):
        """
        Optionally updates button styles to reflect the current mode.
        Adjust the styling method based on your toolkit's capabilities.
        """
        if self.current_mode == "powersave":
            self.bat_save.add_style_class("active")
            self.bat_balanced.remove_style_class("active")
            self.bat_perf.remove_style_class("active")
        elif self.current_mode == "balanced":
            self.bat_save.remove_style_class("active")
            self.bat_balanced.add_style_class("active")
            self.bat_perf.remove_style_class("active")
        elif self.current_mode == "performance":
            self.bat_save.remove_style_class("active")
            self.bat_balanced.remove_style_class("active")
            self.bat_perf.add_style_class("active")
