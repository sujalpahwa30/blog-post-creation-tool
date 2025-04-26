from flask import Flask, render_template_string, send_from_directory, abort
import os

app = Flask(__name__)
OUTPUT_DIR = os.path.join(os.getcwd(), "output", "html")

@app.route("/")
def index():
    try:
        files = os.listdir(OUTPUT_DIR)
        html_files = [f for f in files if f.endswith(".html")]
        list_items = "".join(f"<li><a href='/post/{f}'>{f.replace('_', ' ').rsplit('.', 1)[0]}</a></li>" for f in html_files)
        html_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Blog Posts</title>
        </head>
        <body>
            <h1>Generated Blog Posts</h1>
            <ul>
                {list_items}
            </ul>
        </body>
        </html>
        """
        return html_page
    except Exception as e:
        return f"Error: {e}", 500

@app.route("/post/<filename>")
def post(filename):
    try:
        return send_from_directory(OUTPUT_DIR, filename)
    except Exception as e:
        abort(404, description=f"Post not found: {e}")

if __name__ == "__main__":
    app.run(debug=True)
