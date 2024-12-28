from setuptools import setup, find_packages

setup(
    name="FastYouTrack",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyperclip>=1.9.0",
        "pydantic>=2.10.4",
        "requests>=2.32.3",
        "cryptography>=44.0.0",
        "pyautogui>=0.9.54",
        "dependency-injector>=4.44.0",
        "tkcalendar>=1.6.1",
        "pynput",
    ],
    python_requires=">=3.8",
    author="KMRH47",
    description="A Windows desktop utility for quick time tracking in YouTrack, featuring encrypted token storage and global hotkey access via AutoHotkey ",
)
