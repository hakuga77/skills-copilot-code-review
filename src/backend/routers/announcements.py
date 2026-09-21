"""
Announcement endpoints for the High School Management System API

Announcements are shown to all visitors as a banner on the homepage, and can
be managed (created, updated, deleted) by signed-in teachers/admins.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _serialize(announcement: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a MongoDB announcement document into a JSON-friendly dict"""
    announcement["id"] = str(announcement.pop("_id"))
    return announcement


def _require_teacher(teacher_username: Optional[str]) -> Dict[str, Any]:
    """Ensure the request is made by a signed-in teacher/admin"""
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    return teacher


def _parse_date(value: str, field_name: str) -> date:
    """Parse a YYYY-MM-DD date string, raising a 400 error if invalid"""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid {field_name}, expected format YYYY-MM-DD")


def _validate_dates(start_date: Optional[str], expiration_date: str) -> None:
    """Validate that dates are well-formed and start_date is before expiration_date"""
    expiration = _parse_date(expiration_date, "expiration_date")

    if start_date:
        start = _parse_date(start_date, "start_date")
        if start > expiration:
            raise HTTPException(
                status_code=400,
                detail="start_date must be on or before expiration_date")


@router.get("/active", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements (public, no authentication required)"""
    today = date.today().isoformat()

    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$lte": today}},
        ],
    }

    announcements = announcements_collection.find(
        query).sort("expiration_date", 1)
    return [_serialize(announcement) for announcement in announcements]


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """Get all announcements, including expired ones (requires teacher authentication)"""
    _require_teacher(teacher_username)

    announcements = announcements_collection.find().sort("expiration_date", -1)
    return [_serialize(announcement) for announcement in announcements]


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_announcement(
    message: str,
    expiration_date: str,
    teacher_username: Optional[str] = Query(None),
    start_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new announcement (requires teacher authentication)"""
    _require_teacher(teacher_username)

    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    _validate_dates(start_date, expiration_date)

    document = {
        "message": message.strip(),
        "start_date": start_date,
        "expiration_date": expiration_date,
    }
    result = announcements_collection.insert_one(document)
    document["_id"] = result.inserted_id
    return _serialize(document)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    message: str,
    expiration_date: str,
    teacher_username: Optional[str] = Query(None),
    start_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing announcement (requires teacher authentication)"""
    _require_teacher(teacher_username)

    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    _validate_dates(start_date, expiration_date)

    try:
        object_id = ObjectId(announcement_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid announcement id")

    update = {
        "message": message.strip(),
        "start_date": start_date,
        "expiration_date": expiration_date,
    }
    result = announcements_collection.update_one(
        {"_id": object_id}, {"$set": update})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    updated = announcements_collection.find_one({"_id": object_id})
    return _serialize(updated)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None),
) -> Dict[str, str]:
    """Delete an announcement (requires teacher authentication)"""
    _require_teacher(teacher_username)

    try:
        object_id = ObjectId(announcement_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid announcement id")

    result = announcements_collection.delete_one({"_id": object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
