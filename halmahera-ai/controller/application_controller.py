from core.models import ApplicationCreate, TaskCreate
from service.application_service import ApplicationService


class ApplicationController:
    @staticmethod
    async def list_applications():
        """Return list of all scholarship applications."""
        return await ApplicationService.list_applications()

    @staticmethod
    async def get_application_by_id(application_id: str):
        """Return a scholarship application by its ID."""
        return await ApplicationService.get_application_by_id(application_id)

    @staticmethod
    async def create_application(application_data: ApplicationCreate):
        """Controller untuk membuat aplikasi beasiswa"""
        return await ApplicationService.create_application(application_data)

    @staticmethod
    async def create_task(task_data: TaskCreate):
        """Controller untuk membuat task"""
        return await ApplicationService.create_task(task_data)

    @staticmethod
    async def get_task_by_id(task_id: str):
        """Return a task by its ID."""
        return await ApplicationService.get_tasks_by_application_id(task_id)
