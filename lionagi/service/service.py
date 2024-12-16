class Service:

    def list_tasks(self):
        pass


def register_service(cls):
    original_init = cls.__init__

    def wrapped_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        service_name = self.name
        ServiceSetting().add_service(self, service_name)

    cls.__init__ = wrapped_init
    return cls


class ServiceSetting:
    _instance = None
    services = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_service(self, service: Service, name: str = None):
        if name:
            if self.services.get(name):
                raise ValueError(
                    "Invalid name. There is a service using the name, please change a name."
                )
            self.services[name] = service
        else:
            name = service.__class__.__name__ + "_" + str(len(self.services))
            self.services[name] = service
