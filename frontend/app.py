from flask import Flask, render_template
app = Flask(__name__)
app.config.from_envvar('SKYGRID_FRONTEND_CONFIG')

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/datasets")
def datasets():
    return render_template("datasets.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)