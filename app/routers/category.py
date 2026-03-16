from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models import Category, CategoryCreate, CategoryResponse, Todo, TodoResponse
from app.auth import AuthDep

category_router = APIRouter(tags=["Category Management"])


@category_router.post("/category", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: SessionDep, user: AuthDep):
    category = Category(text=category_data.text, user_id=user.id)
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating category",
        )


@category_router.post("/todo/{todo_id}/category/{cat_id}", response_model=TodoResponse)
def add_category_to_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized todo access",
        )

    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
    ).one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized category access",
        )

    if category not in todo.categories:
        todo.categories.append(category)

    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while assigning category",
        )


@category_router.delete("/todo/{todo_id}/category/{cat_id}", response_model=TodoResponse)
def remove_category_from_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized todo access",
        )

    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
    ).one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized category access",
        )

    if category in todo.categories:
        todo.categories.remove(category)

    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while removing category",
        )


@category_router.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(cat_id: int, db: SessionDep, user: AuthDep):
    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
    ).one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized category access",
        )

    return category.todos