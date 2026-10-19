from core.clients import es_client, watsonx_embedding
from config.settings import ES_INDEX, SEARCH_FIELDS, EXCLUDED_FIELDS, RESULT_FIELDS

class ScholarshipService:
    
    @staticmethod
    def get_all_scholarships(limit: int = 100):
        """Ambil semua dokumen beasiswa dari Elasticsearch."""
        try:
            search_body = {
                "size": limit,
                "query": {"match_all": {}},
                "_source": {
                    "excludes": EXCLUDED_FIELDS
                }
            }
            results = es_client.search(index=ES_INDEX, body=search_body)
            
            all_scholarships = [
                hit["_source"]
                for hit in results["hits"]["hits"]
            ]
            
            return {"count": len(all_scholarships), "results": all_scholarships}
            
        except Exception as e:
            print(f"❌ Error saat mengambil semua beasiswa: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def search_scholarships(query: str, k: int = 5):
        """Pencarian beasiswa berbasis KNN dan text matching."""
        try:
            query_vector = watsonx_embedding.embed_query(query.lower())
            
            search_body = {
                "size": k,
                "query": {
                    "script_score": {
                        "query": {
                            "multi_match": {
                                "query": query,
                                "fields": SEARCH_FIELDS,
                                "type": "best_fields",
                                "operator": "or",
                                "fuzziness": "AUTO"
                            }
                        },
                        "script": {
                            "source": """
                                double textScore = _score;
                                double vectorScore = cosineSimilarity(params.query_vector, 'embedding');
                                return 0.7 * vectorScore + 0.3 * textScore;
                            """,
                            "params": {"query_vector": query_vector}
                        }
                    }
                },
                "_source": RESULT_FIELDS
            }
            
            results = es_client.search(index=ES_INDEX, body=search_body)
            
            formatted_results = [
                hit["_source"]
                for hit in results["hits"]["hits"]
            ]
            
            return {"query": query, "results": formatted_results}
            
        except Exception as e:
            print(f"❌ Error saat search: {e}")
            return {"error": str(e)}