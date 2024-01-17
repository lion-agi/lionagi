import aiohttp
from .service_utils import StatusTracker, EndPoint
from ..utils import nget
from ..utils import APIUtil as au


class BaseService:
    """Abstract base class for services.

    This class defines the basic interface for services that can be started
    and serve requests. It is intended to be subclassed with specific
    implementations for different types of services.

    Methods:
        serve: Abstract method to start serving requests.
    """

    base_url = ''
    available_endpoints = ['chat/completions']
    
    def __init__(
        self, 
        api_key: str = None, 
        schema=None,    # service level schema
    ) -> None:
        self.api_key = api_key
        self.schema = schema
        self.status_tracker = StatusTracker
        self.endpoints={}
        self._has_initiated = False

    def add_endpoint(self, config, **kwargs):
        endpoint_ = EndPoint(config=config, **kwargs)
        self.endpoints[endpoint_.endpoint] = endpoint_ 
        
    async def _serve(self, input_, endpoint, method="post"):

        endpoint_ = self.endpoints[endpoint]
    
        payload_ = au._create_payload(
            input_=input_,  
            config=endpoint_.config,
            required_=self.schema[endpoint]['required'],
            optional_=self.schema[endpoint]['optional']
            )

        async def call_api():
            async with aiohttp.ClientSession() as http_session:
                completion = endpoint_.rate_limiter._call_api(
                    http_session=http_session,
                    endpoint=endpoint,
                    base_url=self.base_url,
                    api_key=self.api_key,
                    method=method,
                    payload=payload_
                )
                return completion
        
        try:
            return await call_api()
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise ValueError(f"API call failed with error: {e}")

# need to make it endpoint specific 
    async def _init(self):
        if not self._has_initiated:
            for endpoint_ in self.available_endpoints:
                config = nget(self.schema, [endpoint_, 'config'])
                token_requirements = nget(self.schema, [endpoint_, 'token'])
                self.add_endpoint(config=config, endpoint_=endpoint_, **token_requirements)        
            
            for key, item in self.endpoints:
                if item is not None:
                    await item._init()
            
            self._has_initiated = True
        else: 
            pass