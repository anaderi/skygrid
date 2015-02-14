from api import MetaschedulerResource

class StatusResource(MetaschedulerResource):
    def get(self):
        return {
            'alive': True
        }