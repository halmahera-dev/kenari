from elasticsearch import Elasticsearch
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames
from config.settings import (
    HOST_ELASTICSEARCH, WATSONX_API_KEY, WATSONX_URL, 
    WATSONX_PROJECT_ID, WATSONX_MODEL_ID
)

class ElasticsearchClient:
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        try:
            self.client = Elasticsearch([HOST_ELASTICSEARCH])
            if not self.client.ping():
                raise ConnectionError("Koneksi ke Elasticsearch gagal.")
            print("✅ Terhubung ke Elasticsearch!")
        except Exception as e:
            print(f"❌ Error koneksi ke Elasticsearch: {e}")
            exit()
    
    def get_client(self):
        return self.client

class WatsonxClient:
    def __init__(self):
        self.embedding = None
        self._initialize()
    
    def _initialize(self):
        embed_params = {
            EmbedTextParamsMetaNames.TRUNCATE_INPUT_TOKENS: 512,
            EmbedTextParamsMetaNames.RETURN_OPTIONS: {"input_text": True},
        }
        
        try:
            self.embedding = WatsonxEmbeddings(
                apikey=WATSONX_API_KEY,
                model_id=WATSONX_MODEL_ID,
                url=WATSONX_URL,
                project_id=WATSONX_PROJECT_ID,
                params=embed_params,
            )
            print(f"✅ Watsonx model '{WATSONX_MODEL_ID}' siap digunakan.")
        except Exception as e:
            print(f"❌ Error inisialisasi WatsonxEmbeddings: {e}")
            exit()
    
    def get_embedding(self):
        return self.embedding

# Singleton instances
es_client = ElasticsearchClient().get_client()
watsonx_embedding = WatsonxClient().get_embedding()