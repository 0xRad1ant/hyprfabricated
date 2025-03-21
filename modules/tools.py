from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command_async, get_relative_path
import modules.icons as icons
from gi.repository import Gdk, GLib
import os
import subprocess

SCREENSHOT_SCRIPT = get_relative_path("../scripts/screenshot.sh")
OCR_SCRIPT = get_relative_path("../scripts/ocr.sh")
GAMEMODE_SCRIPT = get_relative_path("../scripts/gamemode.sh")
GAMEMODE_CHECK_SCRIPT = get_relative_path("../scripts/gamemode_check.sh")
SCREENRECORD_SCRIPT = get_relative_path("../scripts/screenrecord.sh")
GAMEMODE_SCRIPT = get_relative_path("../scripts/gamemode.sh")


class Toolbox(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="toolbox",
            orientation="h",
            spacing=4,
            v_align="center",
            h_align="center",
            visible=True,
            **kwargs,
        )

        self.notch = kwargs["notch"]

        self.btn_ssregion = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.ssregion),
            on_clicked=self.ssregion,
            tooltip_text="Screenshot Region",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )
        # Enable keyboard focus and connect events
        self.btn_ssregion.set_can_focus(True)
        self.btn_ssregion.connect("button-press-event", self.on_ssregion_click)
        self.btn_ssregion.connect("key-press-event", self.on_ssregion_key)

        self.btn_ssfull = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.ssfull),
            on_clicked=self.ssfull,
            tooltip_text="Screenshot Fullscreen",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )
        # Enable keyboard focus and connect events
        self.btn_ssfull.set_can_focus(True)
        self.btn_ssfull.connect("button-press-event", self.on_ssfull_click)
        self.btn_ssfull.connect("key-press-event", self.on_ssfull_key)

        self.btn_screenrecord = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.screenrecord),
            on_clicked=self.screenrecord,
            tooltip_text="Screen Record",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.btn_ocr = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.ocr),
            on_clicked=self.ocr,
            tooltip_text="Text Recognition",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.btn_color = Button(
            name="toolbox-button",
            tooltip_text="Color Picker\nLeft Click: HEX\nMiddle Click: HSV\nRight Click: RGB\n\nKeyboard:\nEnter: HEX\nShift+Enter: RGB\nCtrl+Enter: HSV",
            child=Label(name="button-bar-label", markup=icons.colorpicker),
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.btn_gamemode = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.gamemode),
            on_clicked=self.gamemode,
            h_expand=False,
            tooltip_text="Toggle Game Mode",
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        # Enable keyboard focus for the colorpicker button.
        self.btn_color.set_can_focus(True)
        # Connect both mouse and keyboard events.
        self.btn_color.connect("button-press-event", self.colorpicker)
        self.btn_color.connect("key_press_event", self.colorpicker_key)

        self.btn_emoji = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.emoji),
            on_clicked=self.emoji,
            h_expand=False,
            tooltip_text="Emoji Picker",
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.btn_screenshots_folder = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.screenshots),
            on_clicked=self.open_screenshots_folder,
            tooltip_text="Open Screenshots Folder",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.btn_recordings_folder = Button(
            name="toolbox-button",
            child=Label(name="button-label", markup=icons.recordings),
            on_clicked=self.open_recordings_folder,
            tooltip_text="Open Recordings Folder",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.buttons = [
            self.btn_ssregion,
            self.btn_ssfull,
            self.btn_screenshots_folder,
            Box(name="tool-sep", h_expand=False, v_expand=False, h_align="center", v_align="center"),
            self.btn_screenrecord,
            self.btn_recordings_folder,
            Box(name="tool-sep", h_expand=False, v_expand=False, h_align="center", v_align="center"),
            self.btn_ocr,
            self.btn_color,
            Box(name="tool-sep", h_expand=False, v_expand=False, h_align="center", v_align="center"),
            self.btn_gamemode,
            self.btn_emoji,
        ]

        for button in self.buttons:
            self.add(button)

        self.show_all()

        # Start polling for process state every second.
        self.recorder_timer_id = GLib.timeout_add_seconds(1, self.update_screenrecord_state)
        self.gamemode_updater = GLib.timeout_add_seconds(1, self.gamemode_check)

    def close_menu(self):
        self.notch.close_notch()

    # Action methods
    def ssfull(self, *args):
        exec_shell_command_async(f"bash {SCREENSHOT_SCRIPT} p")
        self.close_menu()

    def on_ssfull_click(self, button, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:  # Left click
                self.ssfull()
            elif event.button == 3:  # Right click
                exec_shell_command_async(f"bash {SCREENSHOT_SCRIPT} p mockup")
                self.close_menu()
            return True
        return False

    def on_ssfull_key(self, widget, event):
        if event.keyval in {Gdk.KEY_Return, Gdk.KEY_KP_Enter}:
            modifiers = event.get_state()
            if modifiers & Gdk.ModifierType.SHIFT_MASK:
                exec_shell_command_async(f"bash {SCREENSHOT_SCRIPT} p mockup")
                self.close_menu()
            else:
                self.ssfull()
            return True
        return False


    def on_ssregion_click(self, button, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:  # Left click
                self.ssregion()
            elif event.button == 3:  # Right click
                exec_shell_command_async(f"bash {SCREENSHOT_SCRIPT} sf mockup")
                self.close_menu()
            return True
        return False

    def on_ssregion_key(self, widget, event):
        if event.keyval in {Gdk.KEY_Return, Gdk.KEY_KP_Enter}:
            modifiers = event.get_state()
            if modifiers & Gdk.ModifierType.SHIFT_MASK:
                exec_shell_command_async(f"bash {SCREENSHOT_SCRIPT} sf mockup")
                self.close_menu()
            else:
                self.ssregion()
            return True
        return False

    def screenrecord(self, *args):
        # Launch screenrecord script in detached mode so that it remains running independently of this program.
        exec_shell_command_async(
            f"bash -c 'nohup bash {SCREENRECORD_SCRIPT} > /dev/null 2>&1 & disown'"
        )
        self.close_menu()

    def ocr(self, *args):
        exec_shell_command_async(f"bash {OCR_SCRIPT} sf")
        self.close_menu()

    def ssregion(self, *args):
        exec_shell_command_async(f"bash {SCREENSHOT_SCRIPT} sf")
        self.close_menu()

    def colorpicker(self, button, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            cmd = {
                1: "-hex",  # Left click
                2: "-hsv",  # Middle click
                3: "-rgb",  # Right click
            }.get(event.button)

            if cmd:
                exec_shell_command_async(
                    f"bash {get_relative_path('../scripts/hyprpicker.sh')} {cmd}"
                )
                self.close_menu()

    def colorpicker_key(self, widget, event):
        if event.keyval in {Gdk.KEY_Return, Gdk.KEY_KP_Enter}:
            modifiers = event.get_state()
            cmd = "-hex"  # Default

            match modifiers & (
                Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK
            ):
                case Gdk.ModifierType.SHIFT_MASK:
                    cmd = "-rgb"
                case Gdk.ModifierType.CONTROL_MASK:
                    cmd = "-hsv"

            exec_shell_command_async(
                f"bash {get_relative_path('../scripts/hyprpicker.sh')} {cmd}"
            )
            self.close_menu()
            return True
        return False

    def gamemode(self, *args):
        exec_shell_command_async(f"bash {GAMEMODE_SCRIPT} toggle")
        self.gamemode_check()
        self.close_menu()

    def gamemode_check(self, *args):
        try:
            result = subprocess.run(
                f"bash {GAMEMODE_SCRIPT} check",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            enabled = result.stdout == b"1\n"
        except Exception:
            enabled = False

        if enabled:
            self.btn_gamemode.get_child().set_markup(icons.gamemode_off)
            self.btn_gamemode.set_tooltip_text("GameMode : OFF")
        else:
            self.btn_gamemode.get_child().set_markup(icons.gamemode)
            self.btn_gamemode.set_tooltip_text("GameMode : ON")

        return True

    def update_screenrecord_state(self):
        """
        Checks if the 'gpu-screen-recorder' process is running.
        If it is, updates the btn_screenrecord icon to icons.stop and adds the 'recording' style class.
        Otherwise, sets the icon back to icons.screenrecord and removes the 'recording' style class.
        This function is called periodically every second.
        """
        try:
            # Use pgrep with -f to check for the process name anywhere in the command line
            result = subprocess.run(
                "pgrep -f gpu-screen-recorder",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            running = result.returncode == 0
        except Exception:
            running = False

        if running:
            self.btn_screenrecord.get_child().set_markup(icons.stop)
            self.btn_screenrecord.add_style_class("recording")
        else:
            self.btn_screenrecord.get_child().set_markup(icons.screenrecord)
            self.btn_screenrecord.remove_style_class("recording")

        # Return True to keep this callback active.
        return True

    def open_screenshots_folder(self, *args):
        screenshots_dir = os.path.join(os.environ.get('XDG_PICTURES_DIR',
                                                    os.path.expanduser('~/Pictures')),
                                     'Screenshots')
        # Create directory if it doesn't exist
        os.makedirs(screenshots_dir, exist_ok=True)
        exec_shell_command_async(f"xdg-open {screenshots_dir}")
        self.close_menu()

    def open_recordings_folder(self, *args):
        recordings_dir = os.path.join(os.environ.get('XDG_VIDEOS_DIR',
                                                   os.path.expanduser('~/Videos')),
                                    'Recordings')
        # Create directory if it doesn't exist
        os.makedirs(recordings_dir, exist_ok=True)
        exec_shell_command_async(f"xdg-open {recordings_dir}")
        self.close_menu()

    def emoji(self, *args):
        self.notch.open_notch("emoji")
