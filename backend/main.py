from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from database import get_db, BookModel, Base, engine
import re

# Recreate tables (for development, remove in production)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic model for request/response with validation
class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    author: str = Field(..., min_length=2, max_length=100, description="Author name")
    isbn: str = Field(..., description="ISBN-13 or ISBN-10")
    quantity: int = Field(default=0, ge=0, description="Number of books in stock")

    @validator('isbn')
    def validate_isbn(cls, v):
        # Validate ISBN-10 and ISBN-13 formats
        isbn_10_pattern = r'^\d{9}[\dX]$'
        isbn_13_pattern = r'^\d{13}$'
        
        if not (re.match(isbn_10_pattern, v) or re.match(isbn_13_pattern, v)):
            raise ValueError('Invalid ISBN format. Must be ISBN-10 or ISBN-13')
        
        return v

    class Config:
        orm_mode = True

@app.get('/')
def read_root():
    return {'message': 'Bienvenue dans le système de gestion de bibliothèque'}

@app.post('/books')
def create_book(book: Book, db: Session = Depends(get_db)):
    # Check if book with same ISBN already exists
    existing_book = db.query(BookModel).filter(BookModel.isbn == book.isbn).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
    # Create new book
    db_book = BookModel(
        title=book.title, 
        author=book.author, 
        isbn=book.isbn, 
        quantity=book.quantity
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return book

@app.get('/books')
def list_books(db: Session = Depends(get_db)):
    books = db.query(BookModel).all()
    return books

@app.get('/books/{isbn}')
def get_book(isbn: str, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put('/books/{isbn}')
def update_book(isbn: str, book: Book, db: Session = Depends(get_db)):
    # Validate that the ISBN in the path matches the book's ISBN
    if isbn != book.isbn:
        raise HTTPException(status_code=400, detail="ISBN in path must match book's ISBN")
    
    db_book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update book details
    db_book.title = book.title
    db_book.author = book.author
    db_book.quantity = book.quantity
    
    db.commit()
    db.refresh(db_book)
    
    return book

@app.delete('/books/{isbn}')
def delete_book(isbn: str, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.isbn == isbn).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    
    return {"message": "Book deleted successfully"}
