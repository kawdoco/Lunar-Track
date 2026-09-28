#!/usr/bin/env python3
"""
run.py
-------
Convenience launcher at the project root, so the app can still be started
the same way as before:

    python run.py

All the real code lives inside the `moon_visualizer` package next to this
file - this script just imports and calls its `main()` function.
"""

from moon_visualizer.main import main

if __name__ == "__main__":
    main()
