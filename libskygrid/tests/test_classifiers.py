from common import SkygridTest, SkygridServerError


from libskygrid import Classifier, Dataset
      


class TestClassifier(SkygridTest):

    def setUp(self):
        super(TestClassifier, self).setUp()

        self.ds = Dataset(self.api_url, path='test_data.csv')
        self.ds.upload()

    def tearDown(self):
        self.ds.delete()

    def test_uploading(self):
        CL_TYPE = "mn"
        PARAMETERS = {'1': 2, '3': 4}
        DESCRIPTION = "test description"
        DATASET = self.ds

        cl = Classifier(
            self.api_url,
            cl_type=CL_TYPE,
            parameters=PARAMETERS,
            description=DESCRIPTION,
            dataset=DATASET
        )

        self.assertTrue(cl.upload())

        self.assertEqual(cl.cl_type, CL_TYPE)
        self.assertEqual(cl.parameters, PARAMETERS)
        self.assertEqual(cl.description, DESCRIPTION)
        self.assertEqual(cl.dataset, DATASET)
        self.assertEqual(cl.status, 'in_queue')

        cl.delete()
