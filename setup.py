"""
setup.py — PyPI packaging for LevelUp CLI

Install globally: pip install .
Or publish to PyPI: python setup.py sdist bdist_wheel && twine upload dist/*
"""

from setuptools import setup, find_packages

setup(
    name="levelup-cli",
    version="2.1.0",
    description="🎮 Gamified Productivity for Developers — Pomodoro + Tasks + XP + Boss Fights",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="KAZ",
    license="MIT",
    python_requires=">=3.9",
    py_modules=[
        "levelup", "database", "gamification", "pet", "anti_cheat",
        "git_sync", "strict_mode", "audio", "visuals", "boss", "config",
    ],
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "audio": ["playsound>=1.3.0"],
        "notifications": ["plyer>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "levelup=levelup:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Topic :: Office/Business",
    ],
)
