import json
import requests

from libskygrid.common import u

from flask import render_template, request, current_app, redirect
from flask.views import View, MethodView

class RenderTemplateView(View):
    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        return render_template(self.template)


class JobView(MethodView):
    def get(self, job_id):
        job = ms.job(job_id, from_api=True)
        return render_template("job.html", job=job)




from flask_wtf import Form
from wtforms import TextAreaField, IntegerField
from wtforms import validators



class MCSubmitForm(Form):
    descriptor = TextAreaField(u'MC descriptor', [validators.required()])
    multiply = IntegerField(
        u'Multiply',
        [validators.required()],
        default=1
    )


class MCSubmitView(MethodView):
    def __init__(self):
        self.template = 'mc_create.html'
    def get(self):
        form = MCSubmitForm()
        return render_template(self.template, form=form)

    def post(self):
        form = MCSubmitForm()
        if form.validate_on_submit():
            description = json.loads(form.data['descriptor'])

            if 'input' in description:
                payload = {
                    'descriptor': description['descriptor'],
                    'input': description['input'],
                    'multiplier': form.data['multiply']
                }
                print payload
            else:
                payload = {
                    'descriptor': description,
                    'multiplier': form.data['multiply']
                }

            mc_url = u(current_app.config['SKYGRID_URL']) + 'montecarlo'
            r = requests.put(
                mc_url,
                data=json.dumps(payload),
                headers={'content-type': 'application/json'}
            ).json()

            assert r['success']

            return redirect('/mc/list')


        return render_template(self.template, form=form)




# class MCSubmitView(MethodView):
#     def __init__(self):
#         self.

#     def get(self):
#         job = ms.job(job_id, from_api=True)
#         return render_template("mc_create.html", form)

#     def post(self):
#         pass
