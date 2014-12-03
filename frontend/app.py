import json
from flask import Flask, render_template
from libscheduler import Metascheduler

app = Flask(__name__)
app.config.from_envvar('SKYGRID_FRONTEND_CONFIG')
ms = Metascheduler(app.config['METASCHEDULER_URL'])


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/datasets")
def datasets():
    return render_template("datasets.html")


@app.route("/classifiers")
def classifiers():
    return render_template("classifiers.html")


@app.route("/metascheduler/jobs/<job_id>")
def ms_job(job_id):
    job = ms.job(job_id, from_api=True)

    return render_template(
        "job.html",
        job=job
    )


@app.route("/metascheduler")
def queues(job_id):
    return render_template("queues.html")



@app.template_filter('to_json')
def to_json(value):
    return json.dumps(value, indent=4)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
