from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, update
from app.schemas import CreateTask, UpdateTask

from slugify import slugify
from sqlalchemy import select

router_task = APIRouter(prefix="/task", tags=["task"])


@router_task.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task).where(Task.completed == False)).all()
    return tasks


@router_task.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task_temp = db.scalars(select(Task).where(Task.id == task_id))
    return task_temp


@router_task.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], create_task: CreateTask):
    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   slug=slugify(create_task.title)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router_task.get("/update")
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, update_task: UpdateTask):
    task = db.scalars((select(Task).where(Task.id == task_id)))
    if task is None:
        raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no task found'
        )

    db.execute(update_task(Task).where(Task.id == task_id).values(
        title=update_task.title,
        content=update_task.content,
        priority=update_task.priority,
        slug=slugify(update_task.title)))

    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful'
    }



@router_task.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalars((select(Task).where(Task.id == task_id)))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no task found'
        )

    db.execute(update(Task).where(Task.id == task_id).values(complited=True))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task delete is successful'
    }