import json
import os

from elasticsearch import Elasticsearch, helpers
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env", override=True)

ES_INDEX = "scholarship_vector_index"
HOST_ELASTICSEARCH = os.getenv('HOST_ELASTICSEARCH')
WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
WATSONX_URL = os.getenv('WATSONX_URL')
WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
WATSONX_MODEL_ID = os.getenv('WATSONX_MODEL_ID')

# Validasi environment variables
if not HOST_ELASTICSEARCH:
    print("❌ HOST_ELASTICSEARCH tidak ditemukan di .env")
    exit()
if not WATSONX_API_KEY:
    print("❌ WATSONX_API_KEY tidak ditemukan di .env")
    exit()
if not WATSONX_PROJECT_ID:
    print("❌ WATSONX_PROJECT_ID tidak ditemukan di .env")
    exit()

try:
    print(f"Mencoba koneksi ke: {HOST_ELASTICSEARCH}")
    es_client = Elasticsearch([HOST_ELASTICSEARCH])
    if not es_client.ping():
        raise ConnectionError("Koneksi ke Elasticsearch gagal.")
    print("✅ Berhasil terhubung ke Elasticsearch!")
except Exception as e:
    print(f"❌ Error koneksi: {e}")
    print("Pastikan Elasticsearch berjalan di http://localhost:9200")
    exit()

embed_params = {
    EmbedTextParamsMetaNames.TRUNCATE_INPUT_TOKENS: 512,
    EmbedTextParamsMetaNames.RETURN_OPTIONS: {"input_text": True},
}

try:
    watsonx_embedding = WatsonxEmbeddings(
        apikey=WATSONX_API_KEY,
        model_id=WATSONX_MODEL_ID,
        url=WATSONX_URL,
        project_id=WATSONX_PROJECT_ID,
        params=embed_params,
    )
    EMBEDDING_DIM = 384
    print(f"Watsonx Embedding Model '{WATSONX_MODEL_ID}' siap. Dimensi diasumsikan: {EMBEDDING_DIM}")
except Exception as e:
    print(f"Error inisialisasi WatsonxEmbeddings: {e}")
    exit()


def delete_index_if_exists(index_name):
    try:
        es = Elasticsearch([HOST_ELASTICSEARCH])
        es.indices.delete(index='*', ignore=[400, 404])
        es.indices.delete(index=index_name, ignore=[404])
        print("✅ Semua indices berhasil dihapus!")
    except Exception as e:
        print(f"Error menghapus indeks: {e}")


def load_data_from_json(filepath="beasiswa.json"):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Berhasil memuat {len(data)} dokumen dari {filepath}.")
        return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' tidak ditemukan.")
        return []
    except json.JSONDecodeError:
        print(f"Error: File '{filepath}' bukan JSON yang valid.")
        return []


def create_vector_index():
    if es_client.indices.exists(index=ES_INDEX):
        print(f"Indeks '{ES_INDEX}' sudah ada. Melewati pembuatan mapping.")
        return

    mapping = {
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "dense_vector",
                    "dims": EMBEDDING_DIM  
                },
                
                "id": {"type": "text"},
                "name": {"type": "text"},
                "description": {"type": "text"},
                "deadline": {"type": "date"},
                
                "location": {"type": "text"},
                "university": {"type": "text"},
                "image": {"type": "text"},
                "degree": {"type": "text"},
                "fields": {"type": "text"},
                "tags": {"type": "text"},
                "url": {"type": "text"},
                "need_ielts": {"type": "boolean"},
                "need_scholastic": {"type": "boolean"},
                "need_essay": {"type": "boolean"},
            }
        }
    }
    es_client.indices.create(index=ES_INDEX, ignore=400, body=mapping)
    print(f"Indeks '{ES_INDEX}' berhasil dibuat dengan mapping yang sesuai.")

def generate_and_index_data(documents):
    actions = []

    def to_bool(value):
        """Konversi aman ke boolean untuk field seperti need_ielts, need_essay, dll"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "yes", "y", "1"]
        if isinstance(value, int):
            return value == 1
        return False

    for idx, doc in enumerate(documents, 1):
        try:
            text_to_embed = f"{doc.get('name', '')}. {doc.get('description', '')}"
            print(f"({idx}/{len(documents)}) Membuat embedding untuk: {doc.get('name', 'Unknown')}")
            vector = watsonx_embedding.embed_query(text_to_embed)

            if isinstance(vector, list) and isinstance(vector[0], list):
                final_vector = vector[0]
            else:
                final_vector = vector
            
            document_to_index = {
                "_index": ES_INDEX,
                "_source": {
                    "id": doc.get("id", ""),
                    "name": doc.get("name", ""),
                    "description": doc.get("description", ""),
                    "deadline": doc.get("deadline", None),  
                    "location": doc.get("location", ""),
                    "university": doc.get("university", ""),
                    "image": doc.get("image", ""),
                    "degree": doc.get("degree", ""),
                    "fields": doc.get("fields", ""),
                    "tags": doc.get("tags", []),
                    "url": doc.get("url", ""),

                    "need_ielts": to_bool(doc.get("need_ielts", False)),
                    "need_scholastic": to_bool(doc.get("need_scholastic", False)),
                    "need_essay": to_bool(doc.get("need_essay", False)),

                    "embedding": final_vector
                }
            }

            actions.append(document_to_index)

        except Exception as e:
            print(f"⚠️ Gagal memproses dokumen '{doc.get('name', 'Unknown')}': {e}")
            continue

    print(f"\nMemulai indexing untuk {len(actions)} dokumen...")
    success, errors = helpers.bulk(es_client, actions, raise_on_error=False)
    print(f"Indeks selesai. Berhasil mengindeks {success} dokumen. Total error: {len(errors)}")

def perform_knn_search(query_text, k=5):
    print(f"\n🔍 Mencari: '{query_text}'...")

    query_vector = watsonx_embedding.embed_query(query_text.lower())

    search_fields = [
        "name^5",          
        "description^4",
        "university^3",
        "degree^2",
        "fields^2",
        "location^1",
        "tags^1"
    ]

    search_body = {
        "size": k,
        "query": {
            "script_score": {
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": search_fields,
                        "type": "best_fields",
                        "operator": "or",
                        "fuzziness": "AUTO"
                    }
                },
                "script": {
                    "source": """
                        double textScore = _score;
                        double vectorScore = cosineSimilarity(params.query_vector, 'embedding');
                        return 0.7 * vectorScore + 0.3 * textScore;  // rasio bobot dapat disesuaikan
                    """,
                    "params": {"query_vector": query_vector}
                }
            }
        },
        "_source": [
            "id",
            "name",
            "description",
            "deadline",
            "location",
            "university",
            "degree",
            "fields",
            "tags",
            "url"
        ]
    }

    try:
        results = es_client.search(index=ES_INDEX, body=search_body)
        hits = results["hits"]["hits"]

        print(f"\n*** Hasil Pencarian untuk: '{query_text}' ***")
        print(f"Ditemukan {len(hits)} hasil\n")

        for i, hit in enumerate(hits, 1):
            src = hit["_source"]
            print(f"{i}. Skor gabungan: {hit['_score']:.4f}")
            print(f"   🎓 {src.get('name', '-')}")
            print(f"   🏛️ Universitas: {src.get('university', '-')}")
            print(f"   📍 Lokasi: {src.get('location', '-')}")
            print(f"   🎯 Bidang: {src.get('fields', '-')}")
            if src.get("deadline"):
                print(f"   ⏰ Deadline: {src['deadline']}")
            print(f"   🔗 URL: {src.get('url', '-')}")
            print(f"   📝 Deskripsi: {src.get('description', '')[:250]}...\n")

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    scholarship_data = load_data_from_json("scholarships.json")
    regenerate_index = True

    if regenerate_index:
        delete_index_if_exists(ES_INDEX)
        create_vector_index()
        generate_and_index_data(scholarship_data)

    if scholarship_data:
        perform_knn_search("I want to apply for a scholarship in the field of Artificial Intelligence.")
        perform_knn_search("I want to apply for scholarship in Sweden")