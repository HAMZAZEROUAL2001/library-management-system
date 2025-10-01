import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Checkbox,
  Box,
  Alert,
  Fab,
  IconButton,
  Chip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { Book, BookCreate, BookUpdate } from '../types';
import { apiService } from '../services/api';

export const BooksPage: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [bookForm, setBookForm] = useState<BookCreate & { available?: boolean }>({
    title: '',
    author: '',
    isbn: '',
    available: true
  });

  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const booksData = await apiService.getBooks();
      setBooks(booksData);
    } catch (err) {
      setError('Erreur lors du chargement des livres');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadBooks();
      return;
    }

    try {
      setLoading(true);
      const searchResults = await apiService.searchBooks(searchQuery);
      setBooks(searchResults);
    } catch (err) {
      setError('Erreur lors de la recherche');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (book?: Book) => {
    if (book) {
      setEditingBook(book);
      setBookForm({
        title: book.title,
        author: book.author,
        isbn: book.isbn,
        available: book.available
      });
    } else {
      setEditingBook(null);
      setBookForm({
        title: '',
        author: '',
        isbn: '',
        available: true
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingBook(null);
    setError('');
  };

  const handleSubmit = async () => {
    try {
      if (editingBook) {
        const updateData: BookUpdate = {
          title: bookForm.title,
          author: bookForm.author,
          isbn: bookForm.isbn,
          available: bookForm.available
        };
        await apiService.updateBook(editingBook.id, updateData);
      } else {
        const createData: BookCreate = {
          title: bookForm.title,
          author: bookForm.author,
          isbn: bookForm.isbn
        };
        await apiService.createBook(createData);
      }
      handleCloseDialog();
      loadBooks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde');
    }
  };

  const handleDelete = async (bookId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce livre ?')) {
      try {
        await apiService.deleteBook(bookId);
        loadBooks();
      } catch (err) {
        setError('Erreur lors de la suppression');
      }
    }
  };

  const handleBorrow = async (bookId: number) => {
    try {
      await apiService.createLoan({ book_id: bookId });
      loadBooks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'emprunt');
    }
  };

  if (loading && books.length === 0) {
    return (
      <Container>
        <Typography>Chargement...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Gestion des Livres
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Barre de recherche */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          label="Rechercher un livre..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button
          variant="contained"
          startIcon={<SearchIcon />}
          onClick={handleSearch}
        >
          Rechercher
        </Button>
      </Box>

      {/* Liste des livres */}
      <Grid container spacing={3}>
        {books.map((book) => (
          <Grid item xs={12} sm={6} md={4} key={book.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                  {book.title}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  par {book.author}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  ISBN: {book.isbn}
                </Typography>
                <Box sx={{ mt: 2, mb: 2 }}>
                  <Chip
                    label={book.available ? 'Disponible' : 'Emprunté'}
                    color={book.available ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(book)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(book.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  {book.available && (
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => handleBorrow(book.id)}
                    >
                      Emprunter
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {books.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Aucun livre trouvé
          </Typography>
        </Box>
      )}

      {/* Bouton flottant pour ajouter un livre */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => handleOpenDialog()}
      >
        <AddIcon />
      </Fab>

      {/* Dialog pour ajouter/modifier un livre */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingBook ? 'Modifier le livre' : 'Ajouter un livre'}
        </DialogTitle>
        <DialogContent>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Titre"
            value={bookForm.title}
            onChange={(e) => setBookForm({ ...bookForm, title: e.target.value })}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Auteur"
            value={bookForm.author}
            onChange={(e) => setBookForm({ ...bookForm, author: e.target.value })}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="ISBN"
            value={bookForm.isbn}
            onChange={(e) => setBookForm({ ...bookForm, isbn: e.target.value })}
          />
          {editingBook && (
            <FormControlLabel
              control={
                <Checkbox
                  checked={bookForm.available || false}
                  onChange={(e) => setBookForm({ ...bookForm, available: e.target.checked })}
                />
              }
              label="Disponible"
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Annuler</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingBook ? 'Modifier' : 'Ajouter'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};