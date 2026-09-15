from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Todo API",
    description="A simple in-memory To-Do API built with FastAPI without a database.",
    version="1.0.0"
)

# Temporary in-memory dictionary storage
todos: dict[int, dict] = {}
todo_id_counter: int = 1


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["Buy groceries"])
    description: Optional[str] = Field(None, max_length=300, examples=["Milk, bread, eggs"])
    completed: bool = Field(default=False)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Buy groceries and snacks"])
    description: Optional[str] = Field(None, max_length=300, examples=["Milk, bread, eggs, chips"])
    completed: Optional[bool] = Field(None)


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool


@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint providing basic API info."""
    return {
        "message": "Welcome to the FastAPI To-Do API!",
        "docs_url": "/docs",
        "total_todos": len(todos)
    }


@app.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
def get_todos(completed: Optional[bool] = None):
    """Retrieve all todo items with optional filter by completion status."""
    items = list(todos.values())
    if completed is not None:
        items = [item for item in items if item["completed"] == completed]
    return items


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
def get_todo(todo_id: int):
    """Retrieve a single todo item by ID."""
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    return todos[todo_id]


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED, tags=["Todos"])
def create_todo(todo: TodoCreate):
    """Create a new todo item."""
    global todo_id_counter
    new_todo = {
        "id": todo_id_counter,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }
    todos[todo_id_counter] = new_todo
    todo_id_counter += 1
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update fields of an existing todo item."""
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )

    current_todo = todos[todo_id]
    update_data = todo_update.model_dump(exclude_unset=True)
    current_todo.update(update_data)
    return current_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_200_OK, tags=["Todos"])
def delete_todo(todo_id: int):
    """Delete a todo item by ID."""
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    deleted_item = todos.pop(todo_id)
    return {"message": f"Todo with ID {todo_id} deleted successfully", "deleted_todo": deleted_item}