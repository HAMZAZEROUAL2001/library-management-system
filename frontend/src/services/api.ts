import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Book, 
  BookCreate, 
  BookUpdate, 
  Loan, 
  LoanCreate, 
  LoginCredentials, 
  RegisterData, 
  Token, 
  SearchParams,
  LibraryStats
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Intercepteur pour ajouter le token d'authentification
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Intercepteur pour gérer les erreurs d'authentification
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentification
  async login(credentials: LoginCredentials): Promise<Token> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response: AxiosResponse<Token> = await this.api.post('/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  }

  async register(userData: RegisterData): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/users/me');
    return response.data;
  }

  // Gestion des livres
  async getBooks(params?: SearchParams): Promise<Book[]> {
    const response: AxiosResponse<Book[]> = await this.api.get('/books', { params });
    return response.data;
  }

  async getBook(id: number): Promise<Book> {
    const response: AxiosResponse<Book> = await this.api.get(`/books/${id}`);
    return response.data;
  }

  async createBook(book: BookCreate): Promise<Book> {
    const response: AxiosResponse<Book> = await this.api.post('/books', book);
    return response.data;
  }

  async updateBook(id: number, book: BookUpdate): Promise<Book> {
    const response: AxiosResponse<Book> = await this.api.put(`/books/${id}`, book);
    return response.data;
  }

  async deleteBook(id: number): Promise<void> {
    await this.api.delete(`/books/${id}`);
  }

  async searchBooks(query: string, params?: SearchParams): Promise<Book[]> {
    const response: AxiosResponse<Book[]> = await this.api.get('/books/search', {
      params: { q: query, ...params }
    });
    return response.data;
  }

  // Gestion des emprunts
  async getLoans(params?: SearchParams): Promise<Loan[]> {
    const response: AxiosResponse<Loan[]> = await this.api.get('/loans', { params });
    return response.data;
  }

  async getUserLoans(params?: SearchParams): Promise<Loan[]> {
    const response: AxiosResponse<Loan[]> = await this.api.get('/loans/my-loans', { params });
    return response.data;
  }

  async createLoan(loan: LoanCreate): Promise<Loan> {
    const response: AxiosResponse<Loan> = await this.api.post('/loans', loan);
    return response.data;
  }

  async returnBook(loanId: number): Promise<Loan> {
    const response: AxiosResponse<Loan> = await this.api.patch(`/loans/${loanId}/return`);
    return response.data;
  }

  // Statistiques
  async getLibraryStats(): Promise<LibraryStats> {
    const response: AxiosResponse<LibraryStats> = await this.api.get('/stats');
    return response.data;
  }
}

export const apiService = new ApiService();