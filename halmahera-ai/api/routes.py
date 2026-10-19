from fastapi import APIRouter, Query

from controller.application_controller import ApplicationController
from controller.scholarship_controller import ScholarshipController
from core.models import ApplicationCreate, TaskCreate

router = APIRouter()

@router.get("/")
def get_all_scholarships(limit: int = 100):
    """
    Retrieve a list of all available scholarships.
    The model should summarize or present scholarship options clearly to the user.
    Limit the result to 100 items per request to avoid information overload.
    """
    return ScholarshipController.get_all_scholarships(limit)

@router.get("/search")
def search_scholarship(query: str = Query(..., description="Search query text")):
    """
    Search for scholarships that best match the user's input query using Elasticsearch.

    Steps:
    1. Return a clear, easy-to-read list of the most relevant scholarships.
    2. Ask the user if they want to apply for any specific scholarship.
    3. If the user selects a scholarship, guide them to create a new application via the create_application endpoint.

    The model should:
    - Interpret the query semantically (not just keyword-based).
    - Present results in a user-friendly format (e.g., bullet points with key details such as name, deadline, and eligibility).
    - Only ask about applications after presenting the list.
    - Explain that the next step is filling out the application for the chosen scholarship.
    
    Note: This endpoint is the first step in a multi-step flow that continues to create_application and create_task.
    """
    return ScholarshipController.search_scholarship(query, k=10)

@router.post("/applications")
async def create_application(application_data: ApplicationCreate):
    """
    Create a new scholarship application record for the scholarship selected by the user.

    Steps:
    1. Guide the user through filling in all required fields for the selected scholarship.
    2. Proactively ask for clarification if any information is missing or unclear.
    3. After successful creation, confirm to the user that they have been successfully registered for the chosen scholarship.
    4. Provide a brief summary of the submitted application (e.g., scholarship name, deadlines, next steps).
    5. Ask the user if they want to create a personalized preparation plan (task roadmap) for this scholarship, including suggested tasks and timelines.

    The model should:
    - Ensure the user understands each step and provide guidance when needed.
    - Only suggest creating a task roadmap after confirming with the user.
    
    Note: This endpoint continues the interactive flow started by search_scholarship and can lead to create_task if the user agrees.
    """
    return await ApplicationController.create_application(application_data)


@router.get("/applications")
async def list_applications():
    """
    Retrieve all scholarship applications submitted by the user.
    The model can summarize each application's current status, deadlines, and progress.
    """
    return await ApplicationController.list_applications()

@router.get("/applications/{application_id}")
async def get_application_by_id(application_id: str):
    """
    Retrieve detailed information for a specific scholarship application identified by its ID.
    The model can highlight key details such as deadlines, required documents, or next steps.
    """
    return await ApplicationController.get_application_by_id(application_id)

@router.post("/tasks")
async def create_task(task_data: TaskCreate):
    """
    Create a new task roadmap for the user's scholarship application process.

    Steps:
    1. Ask the user if they want a detailed task plan based on their chosen scholarship.
    2. If the user agrees, help define specific tasks with start and end dates.
    3. Suggest realistic deadlines and organize tasks to optimize the scholarship preparation process.
    4. Encourage the user to confirm or adjust each task as needed.
    5. Optionally summarize the full task roadmap once created.

    The model should:
    - Guide the user step-by-step in creating each task.
    - Ensure clarity and confirm the user's agreement before finalizing the roadmap.
    - Remain flexible: after completing this step, the user may still ask for
      - Details about scholarships they have already applied for,
      - Task progress or summaries,
      - Searching or applying for other scholarships.
    - Handle such queries by referencing the relevant endpoints or data without restarting the main flow unnecessarily.
    
    Note: This endpoint is the final step in the interactive flow starting from search_scholarship → create_application, 
    but the user can still perform other queries or continue exploring additional options.
    """
    return await ApplicationController.create_task(task_data)

@router.get("/tasks/{task_id}")
async def get_task_by_id(task_id: str):
    """
    Retrieve details and progress for a specific task in the user's scholarship roadmap.
    The model can provide suggestions or reminders to help the user complete their tasks on time.
    """
    return await ApplicationController.get_task_by_id(task_id)