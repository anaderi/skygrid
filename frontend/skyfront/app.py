import json

from flask import Flask

from views import *
from libscheduler import Metascheduler

app = Flask(__name__)
app.config.from_envvar('SKYGRID_FRONTEND_CONFIG')
ms = Metascheduler(app.config['METASCHEDULER_URL'])

app.secret_key = r'k%s&,HjU$^UMBFR(pkdfbu)*&'


@app.template_filter('to_json')
def to_json(value):
    return json.dumps(value, indent=4)





app.add_url_rule('/', view_func=RenderTemplateView.as_view('index_page', template='index.html'))
app.add_url_rule('/datasets', view_func=RenderTemplateView.as_view('datasets_page', template='datasets.html'))
app.add_url_rule('/classifiers', view_func=RenderTemplateView.as_view('classifiers_page', template='classifiers.html'))
app.add_url_rule('/metascheduler', view_func=RenderTemplateView.as_view('ms_page', template='queues.html'))



app.add_url_rule('/metascheduler/jobs/<job_id>', view_func=JobView.as_view('job_page'))


app.add_url_rule('/mc/submit', view_func=MCSubmitView.as_view('mc_submit'))
app.add_url_rule('/mc/list', view_func=RenderTemplateView.as_view('mc_list', 'mc_list.html'))

if __name__ == "__main__":
    app.run(host=app.config["HOSTNAME"], debug=True, port=5002)
