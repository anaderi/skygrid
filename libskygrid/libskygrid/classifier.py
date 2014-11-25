from .common import *
from . import Dataset

JSON_HEADER =  {'content-type': 'application/json'}

class Classifier(object):

    def __init__(
            self, api_url,
            cl_id=None, 
            cl_type=None, parameters=None, description=None, dataset=None,
            start_train=True,
        ):
        self.api_url = u(api_url)
        self.cl_url = self.api_url + "classifiers"

        if cl_id:
            self.cl_id = cl_id
            self.load_from_api()
        elif all(( description, parameters, cl_type, dataset)):
            self.description = description
            self.parameters = parameters
            self.cl_type = cl_type

            if isinstance(dataset, Dataset):
                self.dataset = dataset
            else:
                self.dataset = Dataset(self.api_url, ds_id=ds_id)
        else:
            raise Exception("Neither cl_id nor classifier parameters are sepcified")


    def _update_with_dict(self, data):
        self.cl_id = data['classifier_id']
        self.dataset = Dataset(self.api_url, ds_id=data['dataset_id'])

        self.status = data['status']
        self.description = data['description']
        self.parameters = data['parameters']
        self.cl_type = data['type']


    def load_from_api(self):
        data = sg_get(self.cl_url + self.cl_id)
        self._update_with_dict(data)


    def upload(self):
        payload = {
            'description' : self.description,
            'type' : self.cl_type,
            'parameters' : self.parameters,
            'dataset': self.dataset.ds_id
        }

        data = sg_put(
            self.cl_url,
            data=json.dumps(payload),
            headers=JSON_HEADER
        )

        self._update_with_dict(data)

        return True


    def delete(self):
        if not hasattr(self, 'cl_id'):
            raise Exception('Classifier id is not set. Seems like dataset is not uploaded.')

        result = sg_delete(self.cl_url + self.cl_id)
        assert result == {}

        return True

    def __eq__(self, other):
        if type(self) !=  type(other):
            return False

        attrs = ('cl_id', 'cl_type', 'parameters', 'description', 'dataset')
        return all(
            tuple(
                getattr(self, attr) == getattr(other, attr) for attr in attrs
            )
        )