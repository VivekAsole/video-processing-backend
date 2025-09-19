def get_task_status(task_id: str) -> dict:
    """
    Check the status of a Celery task by ID.

    Returns:
        dict: {
            "task_id": str,
            "status": str,      # PENDING, STARTED, SUCCESS, FAILURE, etc.
            "result": any       # result if SUCCESS, error info if FAILURE, else None
        }
    """
    from app.celery_app import celery_app
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)
    status = result.status
    res = None

    if status == "SUCCESS":
        res = result.result  # the returned value of the task
    elif status == "FAILURE":
        res = str(result.result)  # exception info

    return {
        "task_id": task_id,
        "status": status,
        "result": res
    }
