from common import *

DESCRIPTOR = """
{
    "descriptor" : {
        "name" : "SHIP-MC.test",
        "env_container" : {
            "workdir" : "/opt/ship/FairShip/build",
            "name" : "anaderi/ocean:0.6.1",
            "needed_containers" : [
                {
                    "name" : "anaderi/ship-dev:0.1.0",
                    "volumes" : [
                        "/opt/ship"
                    ]
                }
            ]
        },
        "output_uri" : "local:/srv/skygrid/demo_result/$JOB_ID",
        "args" : {
            "--nEvents" : 10,
            "-f" : "$INPUT_DIR/Genie-mu+_nu_mu-gntp.113.gst_0.root",
            "--output" : "$OUTPUT_DIR/root",
            "--seed" : "$TIMEHASH",
            "--Genie" : true,
            "-Y" : 10
        },
        "cpu_per_container" : 1,
        "cmd" : "cd /opt/ship/FairShip/build; . ./config.sh; cp -r gconfig geometry python ..; export PYTHONPATH+=:/opt/ship/FairShip/build/python; python macro/run_simScript.py",
        "max_memoryMB" : 1024,
        "min_memoryMB" : 512
    },

    "input" : [
        "local:/srv/skygrid/barbara_splitted/mu/Genie-mu+_nu_mu-gntp.113.gst_0.root"
    ]
}
"""




class MonteCarloTest(BasicSkygridTest):
    def test_create(self):
        payload = {
            'descriptor': json.loads(DESCRIPTOR),
            'multiplier': 1
        }

        r = requests.put(
            self.montecarlo_url,
            data=json.dumps(payload),
            headers=self.json_headers
        ).json()

        self.assertTrue(r['success'])
        data = r['data']

        self.assertEqual(data['descriptor'], payload['descriptor'])
        self.assertEqual(data['multiplier'], payload['multiplier'])
        self.assertEqual(data['status'], 'in_queue')


        r = requests.delete(
            os.path.join(self.montecarlo_url, data['montecarlo_id'])
        ).json()

        self.assertTrue(r['success'])

    def test_create_multiple(self):
        payload = {
            'descriptor': json.loads(DESCRIPTOR),
            'multiplier': 5
        }

        r = requests.put(
            self.montecarlo_url,
            data=json.dumps(payload),
            headers=self.json_headers
        ).json()

        self.assertTrue(r['success'])
        data = r['data']

        self.assertEqual(data['descriptor'], payload['descriptor'])
        self.assertEqual(data['multiplier'], payload['multiplier'])
        self.assertEqual(data['status'], 'in_queue')

        for job_id in data['jobs']:
            r = requests.post(
                os.path.join(self.montecarlo_url, data['montecarlo_id'], "callback"),
                data=json.dumps(dict(job_id=job_id, status="completed")),
                headers=self.json_headers
            ).json()

            self.assertTrue(r['success'])

        # Some bad id
        r = requests.post(
            os.path.join(self.montecarlo_url, data['montecarlo_id'], "callback"),
            data=json.dumps(dict(job_id=str(uuid.uuid4()), status="completed")),
            headers=self.json_headers
        ).json()

        self.assertFalse(r['success'])



        r = requests.delete(
            os.path.join(self.montecarlo_url, data['montecarlo_id'])
        ).json()

        self.assertTrue(r['success'])

