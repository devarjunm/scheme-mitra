from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import current_user
from ..models import FarmerCrop, FarmerDocument, FarmerLand, Notification, User
from ..schemas import CropCreate, DocumentStateUpdate, LandCreate, ProfileUpdate
from ..services.farmers import profile_dict, serialize_profile, update_profile
from .common import record_event

router = APIRouter(prefix="/api/v1", tags=["farmer profile"])


@router.get("/profile")
def read_profile(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return serialize_profile(db, user)


@router.put("/profile")
def write_profile(payload: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    result = update_profile(db, user, payload.model_dump(exclude_unset=True))
    record_event(db, user.id, "profile_updated")
    db.commit()
    return result


def _land_out(item: FarmerLand) -> dict:
    return {"id": item.id, "label": item.label, "area_acres": item.area_acres, "ownership_type": item.ownership_type,
            "irrigation_available": item.irrigation_available, "irrigation_type": item.irrigation_type,
            "water_source": item.water_source, "survey_reference": item.survey_reference,
            "is_primary": item.is_primary, "created_at": item.created_at.isoformat()}


@router.get("/land")
def list_land(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(FarmerLand).where(FarmerLand.user_id == user.id).order_by(FarmerLand.is_primary.desc(), FarmerLand.created_at)).all()
    return {"land": [_land_out(row) for row in rows]}


@router.post("/land", status_code=status.HTTP_201_CREATED)
def create_land(payload: LandCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if payload.is_primary:
        for row in db.scalars(select(FarmerLand).where(FarmerLand.user_id == user.id)).all():
            row.is_primary = False
    item = FarmerLand(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"land": _land_out(item)}


@router.put("/land/{land_id}")
def update_land(land_id: str, payload: LandCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(FarmerLand).where(FarmerLand.id == land_id, FarmerLand.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Land record not found.")
    if payload.is_primary:
        for row in db.scalars(select(FarmerLand).where(FarmerLand.user_id == user.id, FarmerLand.id != land_id)).all():
            row.is_primary = False
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return {"land": _land_out(item)}


@router.delete("/land/{land_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_land(land_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(FarmerLand).where(FarmerLand.id == land_id, FarmerLand.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Land record not found.")
    db.delete(item)
    db.commit()


def _crop_out(item: FarmerCrop) -> dict:
    return {"id": item.id, "crop_name": item.crop_name, "crop_category": item.crop_category, "season": item.season,
            "area_acres": item.area_acres, "year": item.year, "is_current": item.is_current, "created_at": item.created_at.isoformat()}


@router.get("/crops")
def list_crops(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(FarmerCrop).where(FarmerCrop.user_id == user.id).order_by(FarmerCrop.is_current.desc(), FarmerCrop.created_at.desc())).all()
    return {"crops": [_crop_out(row) for row in rows]}


@router.post("/crops", status_code=status.HTTP_201_CREATED)
def create_crop(payload: CropCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if payload.is_current:
        for row in db.scalars(select(FarmerCrop).where(FarmerCrop.user_id == user.id)).all():
            row.is_current = False
    item = FarmerCrop(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"crop": _crop_out(item)}


@router.put("/crops/{crop_id}")
def update_crop(crop_id: str, payload: CropCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(FarmerCrop).where(FarmerCrop.id == crop_id, FarmerCrop.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Crop record not found.")
    if payload.is_current:
        for row in db.scalars(select(FarmerCrop).where(FarmerCrop.user_id == user.id, FarmerCrop.id != crop_id)).all():
            row.is_current = False
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return {"crop": _crop_out(item)}


@router.delete("/crops/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop(crop_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(FarmerCrop).where(FarmerCrop.id == crop_id, FarmerCrop.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Crop record not found.")
    db.delete(item)
    db.commit()


@router.get("/documents")
def list_documents(db: Session = Depends(get_db), user: User = Depends(current_user)):
    data = profile_dict(db, user)["documents"]
    return {"documents": [{"document_id": key, "state": value, "validated": False} for key, value in data.items()],
            "note": "This API stores checklist state only; it does not accept or validate document files."}


@router.patch("/documents/{document_id}")
def update_document(document_id: str, payload: DocumentStateUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    allowed = {"land_7_12", "land_8a", "electricity_bill", "purchase_invoice", "prior_consent", "caste_certificate", "equipment_quote", "self_declaration"}
    if document_id not in allowed:
        raise HTTPException(status_code=404, detail="Document checklist item not found.")
    item = db.scalar(select(FarmerDocument).where(FarmerDocument.user_id == user.id, FarmerDocument.document_id == document_id))
    if item is None:
        item = FarmerDocument(user_id=user.id, document_id=document_id, state=payload.state)
        db.add(item)
    else:
        item.state = payload.state
    record_event(db, user.id, "document_state_changed", {"document_id": document_id, "state": payload.state})
    db.commit()
    return {"document_id": document_id, "state": payload.state, "validated": False,
            "note": "Self-reported status only; no document file was uploaded or validated."}


@router.delete("/documents/{document_id}")
def clear_document(document_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(FarmerDocument).where(FarmerDocument.user_id == user.id, FarmerDocument.document_id == document_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Document checklist item not found.")
    item.state = "not_provided"
    db.commit()
    return {"document_id": document_id, "state": "not_provided", "validated": False}


@router.get("/notifications")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(current_user)):
    items = db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100)).all()
    return {"notifications": [{"id": x.id, "title": x.title, "message": x.message, "source_url": x.source_url,
                                "notification_type": x.notification_type, "is_read": x.is_read, "created_at": x.created_at.isoformat()} for x in items]}


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    item.is_read = True
    record_event(db, user.id, "notification_read", {"notification_id": notification_id})
    db.commit()
    return {"id": item.id, "is_read": item.is_read}
