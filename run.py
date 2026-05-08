from app import create_app

app = create_app()

if __name__ == '__main__':\
    # debug=True enables auto-reload on file changes and detailed error pages.
    # Never run with debug=True in production.
    app.run(debug=True)