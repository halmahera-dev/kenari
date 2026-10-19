import uuid
from datetime import datetime

from core.database import db_client
from core.models import ApplicationCreate, TaskCreate


class ApplicationService:
    @staticmethod
    async def list_applications():
        """Fetch all scholarship applications from the database."""
        try:
            query = "SELECT * FROM scholarship_applications"
            results = await db_client.fetch(query)
            return [dict(record) for record in results]
        except Exception as e:
            print(f"❌ Error listing applications: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_application_by_id(application_id: str):
        """Fetch a scholarship application by its ID."""
        try:
            query = "SELECT * FROM scholarship_applications WHERE id = $1"
            result = await db_client.fetchrow(query, application_id)
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Error fetching application by ID: {e}")
            return {"error": str(e)}

    @staticmethod
    async def create_application(application_data: ApplicationCreate):
        """Membuat aplikasi beasiswa baru"""
        try:
            application_id = str(uuid.uuid4())
            query = """
                INSERT INTO scholarship_applications (id, scholarship_id, user_id, status, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """

            result = await db_client.fetchrow(
                query,
                application_id,
                application_data.scholarship_id,
                # application_data.user_id,
                "HdaynXVC0R3JGKaBlSJCB4zPu1IvwLRV",
                application_data.status,
                datetime.now(),
            )

            return dict(result) if result else None

        except Exception as e:
            print(f"❌ Error creating application: {e}")
            return {"error": str(e)}

    @staticmethod
    async def create_task(task_data: TaskCreate):
        """Membuat task baru untuk aplikasi"""
        try:
            task_id = str(uuid.uuid4())

            # Konversi string (YYYY-MM-DD) ke datetime.date
            start_date = datetime.strptime(task_data.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(task_data.end_date, "%Y-%m-%d").date()

            query = """
                INSERT INTO scholarship_application_tasks (
                    id, name, application_id, description, is_completed, start_date, due_date
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
            """

            result = await db_client.fetchrow(
                query,
                task_id,
                task_data.name,
                task_data.application_id,
                task_data.description,
                task_data.is_completed,
                start_date,
                end_date,
            )

            return dict(result) if result else None

        except Exception as e:
            print(f"❌ Error creating task: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_tasks_by_application_id(application_id: str):
        """Fetch all tasks associated with a specific application ID."""
        try:
            query = "SELECT * FROM scholarship_application_tasks WHERE id = $1"
            results = await db_client.fetch(query, application_id)
            return [dict(record) for record in results]
        except Exception as e:
            print(f"❌ Error fetching tasks by application ID: {e}")
            return {"error": str(e)}
