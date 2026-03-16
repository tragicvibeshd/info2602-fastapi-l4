from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models import Todo, TodoCreate, TodoResponse, TodoUpdate
from app.auth import AuthDep

todo_router = APIRouter(tags=["Todo Management"])


@todo_router.get("/todos", response_model=list[TodoResponse])
def get_todos(db: SessionDep, user: AuthDep):
    return user.todos


@todo_router.get("/todo/{id}", response_model=TodoResponse)
def get_todo_by_id(id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(
        select(Todo).where(Todo.id == id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return todo


@todo_router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(db: SessionDep, user: AuthDep, todo_data: TodoCreate):
    todo = Todo(text=todo_data.text, user_id=user.id)
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating an item",
        )


@todo_router.put("/todo/{id}", response_model=TodoResponse)
def update_todo(id: int, db: SessionDep, user: AuthDep, todo_data: TodoUpdate):
    todo = db.exec(
        select(Todo).where(Todo.id == id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    if todo_data.text is not None:
        todo.text = todo_data.text

    if todo_data.done is not None:
        todo.done = todo_data.done

    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while updating an item",
        )


@todo_router.delete("/todo/{id}", status_code=status.HTTP_200_OK)
def delete_todo(id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(
        select(Todo).where(Todo.id == id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        db.delete(todo)
        db.commit()
        return {"message": "Todo deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while deleting an item",
        )