"""
tools.py – Scholarship Search Assistant tools for watsonx Orchestrate
"""
from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections

###############################################################################
# 1. Student Profile Retrieval
###############################################################################
@tool(name="retrieve_student_profile", permission=ToolPermission.READ_ONLY)
def retrieve_student_profile(student_id: str) -> Dict[str, Any]:
    """Retrieve the student's profile from the database.
    
    :param student_id: The student's unique identifier.
    :returns: The student's profile including education, GPA, field of study, etc.
    """
    # Mock implementation - replace with actual DB call or API
    return {
        "student_id": student_id,
        "name": "Budi Santoso",
        "age": 21,
        "nationality": "Indonesian",
        "current_education_level": "S1",  # Sarjana (Bachelor)
        "field_of_study": "Computer Science",
        "gpa": 3.75,
        "university": "Universitas Indonesia",
        "semester": 6,
        "financial_need": "medium",
        "achievements": [
            "Best Student Award 2024",
            "Hackathon Winner 2023"
        ],
        "languages": ["Indonesian", "English"],
        "citizenship": "Indonesian",
        "province": "DKI Jakarta"
    }

###############################################################################
# 2. Elasticsearch Scholarship Search
###############################################################################
@tool(name="search_scholarships_elasticsearch",
     permission=ToolPermission.READ_ONLY,
     expected_credentials=[ExpectedCredentials(
         app_id="elasticsearch_connection",
         type=ConnectionType.BASIC_AUTH
     )])
def search_scholarships_elasticsearch(
    field_of_study: Optional[str] = None,
    education_level: Optional[str] = None,
    min_gpa: Optional[float] = None,
    nationality: Optional[str] = None,
    query: Optional[str] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search scholarships from Elasticsearch based on student criteria.
    
    :param field_of_study: Field of study (e.g., "Computer Science", "Engineering")
    :param education_level: Education level (e.g., "S1", "S2", "S3")
    :param min_gpa: Minimum GPA requirement
    :param nationality: Student nationality
    :param query: Free-text search query
    :param max_results: Maximum number of results to return
    :returns: List of matching scholarships with relevance scores
    """
    # Get Elasticsearch connection
    es_connection = connections.basic_auth("elasticsearch_connection")
    
    # Initialize Elasticsearch client
    es = Elasticsearch(
        [es_connection.server_url],
        basic_auth=(es_connection.username, es_connection.password),
        verify_certs=True
    )
    
    # Build Elasticsearch query
    must_clauses = []
    should_clauses = []
    
    # Field of study matching
    if field_of_study:
        should_clauses.append({
            "match": {
                "eligible_fields": {
                    "query": field_of_study,
                    "boost": 2.0
                }
            }
        })
    
    # Education level matching
    if education_level:
        must_clauses.append({
            "term": {
                "education_level.keyword": education_level
            }
        })
    
    # GPA filtering
    if min_gpa:
        must_clauses.append({
            "range": {
                "min_gpa_requirement": {
                    "lte": min_gpa
                }
            }
        })
    
    # Nationality matching
    if nationality:
        should_clauses.append({
            "match": {
                "eligible_nationalities": nationality
            }
        })
    
    # Free-text search
    if query:
        should_clauses.append({
            "multi_match": {
                "query": query,
                "fields": [
                    "scholarship_name^3",
                    "description^2",
                    "provider",
                    "benefits"
                ],
                "type": "best_fields"
            }
        })
    
    # Construct the final query
    es_query = {
        "bool": {
            "must": must_clauses if must_clauses else [{"match_all": {}}],
            "should": should_clauses,
            "minimum_should_match": 1 if should_clauses else 0,
            "filter": [
                {
                    "range": {
                        "deadline": {
                            "gte": datetime.datetime.now().isoformat()
                        }
                    }
                }
            ]
        }
    }
    
    # Execute search
    try:
        response = es.search(
            index="scholarships",
            query=es_query,
            size=max_results,
            sort=[
                {"_score": {"order": "desc"}},
                {"deadline": {"order": "asc"}}
            ]
        )
        
        # Format results
        scholarships = []
        for hit in response['hits']['hits']:
            scholarship = hit['_source']
            scholarship['relevance_score'] = hit['_score']
            scholarship['scholarship_id'] = hit['_id']
            scholarships.append(scholarship)
        
        return {
            "total_found": response['hits']['total']['value'],
            "scholarships": scholarships,
            "search_criteria": {
                "field_of_study": field_of_study,
                "education_level": education_level,
                "min_gpa": min_gpa,
                "nationality": nationality,
                "query": query
            }
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "total_found": 0,
            "scholarships": []
        }

###############################################################################
# 3. Scholarship Eligibility Check
###############################################################################
@tool(name="check_scholarship_eligibility", permission=ToolPermission.READ_ONLY)
def check_scholarship_eligibility(
    student_id: str,
    scholarship_id: str
) -> Dict[str, Any]:
    """
    Check if a student is eligible for a specific scholarship.
    
    :param student_id: The student's unique identifier
    :param scholarship_id: The scholarship's unique identifier
    :returns: Eligibility status with detailed requirements check
    """
    # Get student profile
    student = retrieve_student_profile(student_id)
    
    # Mock scholarship data - in production, fetch from Elasticsearch
    scholarship = {
        "scholarship_id": scholarship_id,
        "scholarship_name": "LPDP Scholarship 2025",
        "min_gpa_requirement": 3.0,
        "eligible_nationalities": ["Indonesian"],
        "eligible_fields": ["Computer Science", "Engineering", "Technology"],
        "education_level": "S2",
        "age_limit": 35,
        "required_documents": ["Transcript", "Recommendation Letter", "Essay"]
    }
    
    # Check eligibility criteria
    eligibility_checks = {
        "gpa_requirement": {
            "required": scholarship["min_gpa_requirement"],
            "student_gpa": student["gpa"],
            "passed": student["gpa"] >= scholarship["min_gpa_requirement"]
        },
        "nationality": {
            "required": scholarship["eligible_nationalities"],
            "student_nationality": student["nationality"],
            "passed": student["nationality"] in scholarship["eligible_nationalities"]
        },
        "field_of_study": {
            "required": scholarship["eligible_fields"],
            "student_field": student["field_of_study"],
            "passed": student["field_of_study"] in scholarship["eligible_fields"]
        },
        "age_requirement": {
            "max_age": scholarship["age_limit"],
            "student_age": student["age"],
            "passed": student["age"] <= scholarship["age_limit"]
        }
    }
    
    # Overall eligibility
    is_eligible = all(check["passed"] for check in eligibility_checks.values())
    
    return {
        "student_id": student_id,
        "scholarship_id": scholarship_id,
        "scholarship_name": scholarship["scholarship_name"],
        "is_eligible": is_eligible,
        "eligibility_checks": eligibility_checks,
        "required_documents": scholarship["required_documents"]
    }

###############################################################################
# 4. Save Scholarship Application
###############################################################################
@tool(name="save_scholarship_application", permission=ToolPermission.WRITE_ONLY)
def save_scholarship_application(
    student_id: str,
    scholarship_id: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Save a scholarship to student's application list.
    
    :param student_id: The student's unique identifier
    :param scholarship_id: The scholarship's unique identifier
    :param notes: Optional notes about the application
    :returns: Confirmation of saved application
    """
    # Mock implementation - replace with actual database operation
    application_id = f"APP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "status": "success",
        "application_id": application_id,
        "student_id": student_id,
        "scholarship_id": scholarship_id,
        "saved_at": datetime.datetime.now().isoformat(),
        "notes": notes,
        "next_steps": [
            "Prepare required documents",
            "Complete online application form",
            "Submit before deadline"
        ]
    }

###############################################################################
# 5. Get Scholarship Recommendations
###############################################################################
@tool(name="get_scholarship_recommendations", permission=ToolPermission.READ_ONLY)
def get_scholarship_recommendations(
    student_id: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Get personalized scholarship recommendations based on student profile.
    
    :param student_id: The student's unique identifier
    :param limit: Number of recommendations to return
    :returns: List of recommended scholarships with match scores
    """
    # Get student profile
    student = retrieve_student_profile(student_id)
    
    # Search scholarships based on student profile
    search_results = search_scholarships_elasticsearch(
        field_of_study=student["field_of_study"],
        education_level=student["current_education_level"],
        min_gpa=student["gpa"],
        nationality=student["nationality"],
        max_results=limit
    )
    
    # Calculate match scores
    recommendations = []
    for scholarship in search_results.get("scholarships", []):
        match_score = scholarship.get("relevance_score", 0)
        
        # Add personalized insights
        match_reasons = []
        if student["field_of_study"] in scholarship.get("eligible_fields", []):
            match_reasons.append(f"Matches your field: {student['field_of_study']}")
        if student["gpa"] >= scholarship.get("min_gpa_requirement", 0):
            match_reasons.append(f"Your GPA ({student['gpa']}) meets requirement")
        
        recommendations.append({
            "scholarship": scholarship,
            "match_score": match_score,
            "match_reasons": match_reasons
        })
    
    return {
        "student_id": student_id,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "generated_at": datetime.datetime.now().isoformat()
    }