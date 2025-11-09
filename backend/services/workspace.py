from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.workspace import Workspace as WorkspaceModel
from utils.schema_validators import WorkspaceCreate, WorkspaceOut
from utils.auth_deps import get_current_user
from services.db import get_db


router = APIRouter()


@router.post("/save", response_model=WorkspaceOut)
def save_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ws = WorkspaceModel(name=payload.name, data=payload.data.dict(), owner_id=user.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@router.get("/{workspace_id}", response_model=WorkspaceOut)
def load_workspace(workspace_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ws = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@router.get("/", response_model=List[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(WorkspaceModel)
        .filter(WorkspaceModel.owner_id == user.id)
        .order_by(WorkspaceModel.updated_at.desc())
        .limit(50)
        .all()
    )
