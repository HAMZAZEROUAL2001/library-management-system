// Types pour l'API
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
}

export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  available: boolean;
  created_at: string;
}

export interface BookCreate {
  title: string;
  author: string;
  isbn: string;
}

export interface BookUpdate {
  title?: string;
  author?: string;
  isbn?: string;
  available?: boolean;
}

export interface Loan {
  id: number;
  user_id: number;
  book_id: number;
  loan_date: string;
  return_date?: string;
  is_returned: boolean;
  book: Book;
  user: User;
}

export interface LoanCreate {
  book_id: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface SearchParams extends PaginationParams {
  search?: string;
}

export interface LibraryStats {
  total_books: number;
  available_books: number;
  total_loans: number;
  active_loans: number;
}