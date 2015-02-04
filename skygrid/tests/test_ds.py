from common import *

class DatasetTest(BasicSkygridTest):
    def hashfile(self, path):
        hasher = hashlib.sha512()
        blocksize = 65536

        afile = open(path, 'rb')
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.hexdigest()

    def test_upload_and_delete_csv(self):
        payload = dict(
            name=str(uuid.uuid4().hex),
            type="csv"
        )
        files = {'dataset': open('test_data.csv', 'rb')}

        r = requests.put(
            self.datasets_url,
            data=payload,
            files=files
        ).json()

        self.assertTrue(r['success'])
        data = r['data']

        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['type'], payload['type'])

        self.assertEqual(
            data['hash'],
            self.hashfile('test_data.csv')
        )

        r = requests.delete(
            os.path.join(self.datasets_url, data['id'])
        ).json()

        self.assertTrue(r['success'])

    def test_upload_and_delete_by_uri(self):
        payload = dict(
            name=str(uuid.uuid4().hex),
            type="root",
            uri="/eos/lhcb/user/a/albarano/test.root"
        )

        r = requests.put(
            self.datasets_url,
            data=payload
        ).json()

        self.assertTrue(r['success'])
        data = r['data']

        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['type'], payload['type'])

        self.assertEqual(
            data['hash'],
            None
        )

        r = requests.delete(
            os.path.join(self.datasets_url, data['id'])
        ).json()

        self.assertTrue(r['success'])