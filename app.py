from flask import Flask, render_template
from routes.tests import tests_bp
from routes.subjects import subjects_bp
from routes.topics import topics_bp
from routes.mocktests import mocktests_bp
from routes.schedules import schedules_bp
from routes.auth import auth_bp, login_required
from routes.ai_mocktest import ai_mocktest_bp

app = Flask(__name__)
app.secret_key = "asp_secret_key_2025"

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(tests_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(topics_bp)
app.register_blueprint(mocktests_bp)
app.register_blueprint(schedules_bp)
app.register_blueprint(ai_mocktest_bp)

# UI Routes
@app.route("/")
@login_required
def dashboard():
    return render_template("index.html", active_page="dashboard")

@app.route("/tests-page")
@login_required
def tests_page():
    return render_template("tests.html", active_page="tests")

@app.route("/subjects-page")
@login_required
def subjects_page():
    return render_template("subjects.html", active_page="subjects")

@app.route("/topics-page")
@login_required
def topics_page():
    return render_template("topics.html", active_page="topics")

@app.route("/mocktests-page")
@login_required
def mocktests_page():
    return render_template("mocktests.html", active_page="mocktests")

@app.route("/schedules-page")
@login_required
def schedules_page():
    return render_template("schedules.html", active_page="schedules")

if __name__ == "__main__":
    app.run(debug=True)
