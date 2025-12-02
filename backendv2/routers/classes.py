from fastapi import APIRouter, HTTPException
from models import classes, CreateClassRequest, JoinClassRequest
import uuid

router = APIRouter()

@router.post("/classes/create")
def create_class(data: CreateClassRequest):
    new_class = {
        "id": str(uuid.uuid4()),
        "title": data.title,
        "teacher": "teacher1",
        "code": uuid.uuid4().hex[:6].upper(),
        "status": "live",
        "participants": 0
    }
    classes.append(new_class)
    return new_class

@router.post("/classes/join")
def join_class(data: JoinClassRequest):
    c = next((c for c in classes if c["code"] == data.code), None)
    if not c:
        raise HTTPException(status_code=404, detail="Invalid class code")
    c["participants"] += 1
    return {"success": True, "classId": c["id"]}
