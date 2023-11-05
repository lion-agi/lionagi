"""   
Copyright 2023 HaiyangLi <ocean@lionagi.ai>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
from .SyncService import SyncAPIService
from .AsyncService import AsyncAPIService

async_api_service = AsyncAPIService(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=5, 
    max_tokens_per_minute=10000,
    token_encoding_name="cl100k_base",
    max_attempts=3
)

sync_api_service = SyncAPIService(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=500,
    max_tokens_per_minute=10000,
    token_encoding_name="cl100k_base",
    max_attempts=3
)