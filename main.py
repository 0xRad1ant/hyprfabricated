import setproctitle
import os
from fabric import Application
from fabric.utils import get_relative_path, exec_shell_command_async
from modules.bar import Bar
from modules.notch import Notch
from modules.dock import Dock
from modules.corners import Corners
from config.config import open_config, ensure_fonts
import config.data as data
from datetime import datetime

fonts_updated_file = f"{data.CACHE_DIR}/fonts_updated"

if __name__ == "__main__":
    setproctitle.setproctitle(data.APP_NAME)

    # Check if the current date is after February 25, 2025
    current_date = datetime.now()
    target_date = datetime(2025, 2, 25)

    #Check if fonts_updated file exist, so we dont repeat this part every time.
    if current_date > target_date and not os.path.exists(fonts_updated_file):
        tabler_icons_path = os.path.expanduser("~/.fonts/tabler-icons")
        if os.path.exists(tabler_icons_path):
            import shutil
            try:
                shutil.rmtree(tabler_icons_path)
                print(f"Removed directory: {tabler_icons_path}")
            except Exception as e:
                print(f"Error removing {tabler_icons_path}: {e}")
        ensure_fonts()
        # Create the fonts_updated file to indicate that the process has been done.
        os.makedirs(data.CACHE_DIR, exist_ok=True)
        with open(fonts_updated_file, "w") as f:
            f.write("Fonts updated after February 25, 2025")

    if not os.path.isfile(data.CONFIG_FILE):
        exec_shell_command_async(f"python {get_relative_path('../config/config.py')}")
    corners = Corners()
    bar = Bar()
    notch = Notch()
    dock = Dock() 
    bar.notch = notch
    notch.bar = bar
    app = Application(f"{data.APP_NAME}", bar, notch, dock)

    def set_css():
        app.set_stylesheet_from_file(
            get_relative_path("main.css"),
            exposed_functions={
                "overview_width": lambda: f"min-width: {data.CURRENT_WIDTH * 0.1 * 5 + 92}px;",
                "overview_height": lambda: f"min-height: {data.CURRENT_HEIGHT * 0.1 * 2 + 32}px;",
            },
        )

    app.set_css = set_css

    app.set_css()

    app.run()
