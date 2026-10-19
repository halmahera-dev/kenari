import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

# Elasticsearch Configuration
ES_INDEX = "scholarship_vector_index"
HOST_ELASTICSEARCH = os.getenv('HOST_ELASTICSEARCH')

# Watsonx Configuration
WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
WATSONX_URL = os.getenv('WATSONX_URL')
WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
WATSONX_MODEL_ID = os.getenv('WATSONX_MODEL_ID')

# Database Configuration
DATABASE_URL = "postgresql://neondb_owner:npg_QlZRKn6aEJW1@ep-gentle-hill-a110pntw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Search Configuration
SEARCH_FIELDS = [
    "name^5",          
    "description^4",
    "university^3",
    "degree^2",
    "fields^2",
    "location^1",
    "tags^1"
]

EXCLUDED_FIELDS = ["embedding", "score", "image"]
RESULT_FIELDS = [
    "id", "name", "description", "deadline", 
    "location", "university", "degree", "fields", "tags", "url"
]