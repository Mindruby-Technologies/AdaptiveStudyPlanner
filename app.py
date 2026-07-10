from flask import Flask, render_template
from routes.tests import tests_bp
from routes.subjects import subjects_bp
from routes.topics import topics_bp

app = Flask(__name__)

# Register API blueprints
app.register_blueprint(tests_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(topics_bp)

# UI Routes
@app.route("/")
def dashboard():
    return render_template("index.html", active_page="dashboard")

@app.route("/tests-page")
def tests_page():
    return render_template("tests.html", active_page="tests")

@app.route("/subjects-page")
def subjects_page():
    return render_template("subjects.html", active_page="subjects")

@app.route("/topics-page")
def topics_page():
    return render_template("topics.html", active_page="topics")

if __name__ == "__main__":
    app.run(debug=True)
