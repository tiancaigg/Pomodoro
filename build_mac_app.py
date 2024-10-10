import PyInstaller.__main__
import os

# Get the absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
png_icon_path = os.path.join(current_dir, "pomodoro.png")

# Check if the icon file exists
if not os.path.exists(png_icon_path):
    print(f"Warning: Icon file not found at {png_icon_path}")
    print("The app will be built without an icon.")
    icon_option = []
else:
    icon_option = [f'--icon={png_icon_path}']

# Prepare PyInstaller command
pyinstaller_command = [
    os.path.join(src_dir, 'main.py'),
    '--name=Pomodoro',
    '--windowed',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--hidden-import=PyQt6',
    '--hidden-import=yaml',
    '--hidden-import=playsound',
    f'--osx-bundle-identifier=com.yourcompany.pomodoro',
    f'--add-data={src_dir}:src'
] + icon_option

# Run PyInstaller
PyInstaller.__main__.run(pyinstaller_command)

print("Build process completed.")