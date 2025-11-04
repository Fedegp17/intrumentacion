try:
    from principal_code_simple import app
except Exception as e:
    import sys
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    app.run()
