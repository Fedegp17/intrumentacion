"""
Entry point for Vercel deployment
"""

import sys
import traceback

try:
    from principal_code_simple import app
except Exception as e:
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    app.run()

