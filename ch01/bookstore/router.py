from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel

from ch01.bookstore.models import Book

"""
EXERCISE
Using the APIRouter class, refactor each endpoint in a separate file and
add the route to the FastAPI server.
"""
book_router = APIRouter()
author_router = APIRouter()


@book_router.get("/books/{book_id}")
async def read_book(book_id: int):
    return {
        "book_id": book_id,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
    }


@author_router.get("/authors/{author_id}")
async def read_author(author_id: int):
    return {
        "author_id": author_id,
        "name": "Ernest Hemingway",
    }


@book_router.get("/books")
async def read_books(year: int | None = None):
    if year:
        return {
            "year": year,
            "books": ["Book 1", "Book 2"],
        }
    return {"books": ["All Books"]}


@book_router.post("/books")
async def create_book(book: Book):
    return book


"""
Defining and using request and response models
"""


class BookResponse(BaseModel):
    title: str
    author: str


@book_router.get("/allbooks", response_model=list[BookResponse])
async def read_all_books():
    return [
        {
            "id": 1,
            "title": "1984",
            "author": "George Orwell",
        },
        {
            "id": 2,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
        },
    ]
