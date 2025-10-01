import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BooksPage } from '../components/BooksPage';
import { AuthProvider } from '../contexts/AuthContext';
import { apiService } from '../services/api';

// Mock API service
jest.mock('../services/api');
const mockApiService = apiService as jest.Mocked<typeof apiService>;

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

// Mock Material-UI components that might cause issues
jest.mock('@mui/material/Fab', () => {
  return function MockFab({ children, onClick }: any) {
    return <button onClick={onClick}>{children}</button>;
  };
});

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>
    {children}
  </AuthProvider>
);

describe('BooksPage', () => {
  const mockBooks = [
    {
      id: 1,
      title: 'Test Book 1',
      author: 'Test Author 1',
      isbn: '978-0123456789',
      available: true,
      created_at: '2024-01-01T00:00:00'
    },
    {
      id: 2,
      title: 'Test Book 2',
      author: 'Test Author 2',
      isbn: '978-0987654321',
      available: false,
      created_at: '2024-01-02T00:00:00'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    mockApiService.getBooks.mockResolvedValue(mockBooks);
  });

  test('renders books list', async () => {
    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Gestion des Livres')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Test Book 1')).toBeInTheDocument();
      expect(screen.getByText('Test Book 2')).toBeInTheDocument();
    });
  });

  test('shows available and unavailable book status', async () => {
    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Disponible')).toBeInTheDocument();
      expect(screen.getByText('Emprunté')).toBeInTheDocument();
    });
  });

  test('opens add book dialog when clicking add button', async () => {
    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    const addButton = screen.getByRole('button', { name: /add/i });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Ajouter un livre')).toBeInTheDocument();
    });
  });

  test('handles book search', async () => {
    const searchResults = [mockBooks[0]];
    mockApiService.searchBooks.mockResolvedValue(searchResults);

    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    const searchInput = screen.getByLabelText(/rechercher un livre/i);
    const searchButton = screen.getByRole('button', { name: /rechercher/i });

    fireEvent.change(searchInput, { target: { value: 'Test Book 1' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockApiService.searchBooks).toHaveBeenCalledWith('Test Book 1');
    });
  });

  test('handles book creation', async () => {
    const newBook = {
      id: 3,
      title: 'New Book',
      author: 'New Author',
      isbn: '978-1111111111',
      available: true,
      created_at: '2024-01-03T00:00:00'
    };

    mockApiService.createBook.mockResolvedValue(newBook);

    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    // Open add dialog
    const addButton = screen.getByRole('button', { name: /add/i });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Ajouter un livre')).toBeInTheDocument();
    });

    // Fill form
    fireEvent.change(screen.getByLabelText(/titre/i), { target: { value: 'New Book' } });
    fireEvent.change(screen.getByLabelText(/auteur/i), { target: { value: 'New Author' } });
    fireEvent.change(screen.getByLabelText(/isbn/i), { target: { value: '978-1111111111' } });

    // Submit
    const submitButton = screen.getByRole('button', { name: /ajouter/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiService.createBook).toHaveBeenCalledWith({
        title: 'New Book',
        author: 'New Author',
        isbn: '978-1111111111'
      });
    });
  });

  test('handles book borrowing', async () => {
    const loanResponse = {
      id: 1,
      user_id: 1,
      book_id: 1,
      loan_date: '2024-01-01T00:00:00',
      return_date: null,
      is_returned: false,
      book: mockBooks[0]
    };

    mockApiService.createLoan.mockResolvedValue(loanResponse);

    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Book 1')).toBeInTheDocument();
    });

    const borrowButton = screen.getByRole('button', { name: /emprunter/i });
    fireEvent.click(borrowButton);

    await waitFor(() => {
      expect(mockApiService.createLoan).toHaveBeenCalledWith({ book_id: 1 });
    });
  });

  test('displays error message when API call fails', async () => {
    mockApiService.getBooks.mockRejectedValue(new Error('API Error'));

    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/erreur lors du chargement des livres/i)).toBeInTheDocument();
    });
  });

  test('shows empty state when no books found', async () => {
    mockApiService.getBooks.mockResolvedValue([]);

    render(
      <TestWrapper>
        <BooksPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/aucun livre trouvé/i)).toBeInTheDocument();
    });
  });
});