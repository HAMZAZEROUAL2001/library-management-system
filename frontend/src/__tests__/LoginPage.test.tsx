import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import userEvent from '@testing-library/user-event';
import { LoginPage } from '../components/LoginPage';
import { AuthProvider } from '../contexts/AuthContext';
import { apiService } from '../services/api';

// Mock API service
jest.mock('../services/api');
const mockApiService = apiService as jest.Mocked<typeof apiService>;

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  </BrowserRouter>
);

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form by default', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByText('Connexion')).toBeInTheDocument();
    expect(screen.getByLabelText(/nom d'utilisateur/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  test('switches to registration form when clicking inscription tab', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    await user.click(screen.getByText('Inscription'));

    expect(screen.getByText('Inscription')).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /s'inscrire/i })).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    const user = userEvent.setup();
    const mockToken = { access_token: 'mock-token', token_type: 'bearer' };
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com', is_active: true };

    mockApiService.login.mockResolvedValue(mockToken);
    mockApiService.getCurrentUser.mockResolvedValue(mockUser);

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/nom d'utilisateur/i), 'testuser');
    await user.type(screen.getByLabelText(/mot de passe/i), 'password123');
    await user.click(screen.getByRole('button', { name: /se connecter/i }));

    await waitFor(() => {
      expect(mockApiService.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('displays error message on failed login', async () => {
    const user = userEvent.setup();
    
    mockApiService.login.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/nom d'utilisateur/i), 'wronguser');
    await user.type(screen.getByLabelText(/mot de passe/i), 'wrongpassword');
    await user.click(screen.getByRole('button', { name: /se connecter/i }));

    await waitFor(() => {
      expect(screen.getByText(/nom d'utilisateur ou mot de passe incorrect/i)).toBeInTheDocument();
    });
  });

  test('handles successful registration', async () => {
    const user = userEvent.setup();
    const mockUser = { id: 1, username: 'newuser', email: 'new@example.com', is_active: true };
    const mockToken = { access_token: 'mock-token', token_type: 'bearer' };

    mockApiService.register.mockResolvedValue(mockUser);
    mockApiService.login.mockResolvedValue(mockToken);
    mockApiService.getCurrentUser.mockResolvedValue(mockUser);

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    // Switch to registration tab
    await user.click(screen.getByText('Inscription'));

    await user.type(screen.getByLabelText(/nom d'utilisateur/i), 'newuser');
    await user.type(screen.getByLabelText(/email/i), 'new@example.com');
    await user.type(screen.getByLabelText(/mot de passe/i), 'password123');
    await user.click(screen.getByRole('button', { name: /s'inscrire/i }));

    await waitFor(() => {
      expect(mockApiService.register).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('shows loading state during form submission', async () => {
    const user = userEvent.setup();
    
    // Mock delayed response
    mockApiService.login.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ access_token: 'token', token_type: 'bearer' }), 1000))
    );

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/nom d'utilisateur/i), 'testuser');
    await user.type(screen.getByLabelText(/mot de passe/i), 'password123');
    await user.click(screen.getByRole('button', { name: /se connecter/i }));

    expect(screen.getByText('Connexion...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /connexion\.\.\./i })).toBeDisabled();
  });
});