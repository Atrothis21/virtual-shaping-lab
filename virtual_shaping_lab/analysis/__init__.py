"""
Analysis package initialization.

Force a non-interactive Matplotlib backend so report generation is safe when
FastAPI runs handlers in worker threads.
"""

import matplotlib

# Thread-safe, headless backend for server/report rendering.
matplotlib.use("Agg", force=True)
