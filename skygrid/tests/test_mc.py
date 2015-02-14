from common import *

DESCRIPTOR = """
{
  "app_container": {
    "name": "leoredi/ship-dev:0.0.17",
    "volume": "/opt/ship"
  },
  "args": {
    "--output": "$OUTPUT_DIR/root",
    "--num-events": 1000,
    "-d": true,
    "-f": true
  },
  "cmd": ". ./config.sh; export PYTHONPATH+=:/opt/ship/FairShip/build/python; python muonShieldOptimization/g4Ex_CHARMpit5_QGSP_BERT_EMV.py",
  "cpu_per_container": 1,
  "email": "flr09@ic.ac.uk",
  "env_container": {
    "app_volume": "$APP_CONTAINER",
    "name": "anaderi/ocean:latest",
    "output_volume": "$JOB_OUTPUT_DIR:/output",
    "workdir": "/opt/ship/FairShip/build"
  },
  "job_id": 20699,
  "job_parent_id": 4,
  "job_super_id": 4,
  "max_memoryMB": 1024,
  "min_memoryMB": 512,
  "name": "SHIP-MC.test",
  "num_containers": 48,
  "status": "SUCCESS"
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


        r = requests.delete(
            os.path.join(self.montecarlo_url, data['montecarlo_id'])
        ).json()

        self.assertTrue(r['success'])

