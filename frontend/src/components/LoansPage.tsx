import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Box,
  Chip,
  Button,
  Alert
} from '@mui/material';
import { Loan } from '../types';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export const LoansPage: React.FC = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    loadLoans();
  }, []);

  const loadLoans = async () => {
    try {
      setLoading(true);
      const loansData = await apiService.getUserLoans();
      setLoans(loansData);
    } catch (err) {
      setError('Erreur lors du chargement des emprunts');
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (loanId: number) => {
    try {
      await apiService.returnBook(loanId);
      loadLoans();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du retour');
    }
  };

  if (loading) {
    return (
      <Container>
        <Typography>Chargement...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Mes Emprunts
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {loans.length === 0 ? (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Vous n'avez aucun emprunt en cours
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {loans.map((loan) => (
            <Grid item xs={12} sm={6} md={4} key={loan.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {loan.book.title}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    par {loan.book.author}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    ISBN: {loan.book.isbn}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Emprunté le : {new Date(loan.loan_date).toLocaleDateString('fr-FR')}
                  </Typography>
                  {loan.return_date && (
                    <Typography variant="body2" gutterBottom>
                      Retourné le : {new Date(loan.return_date).toLocaleDateString('fr-FR')}
                    </Typography>
                  )}
                  <Box sx={{ mt: 2, mb: 2 }}>
                    <Chip
                      label={loan.is_returned ? 'Retourné' : 'En cours'}
                      color={loan.is_returned ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  {!loan.is_returned && (
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleReturn(loan.id)}
                      sx={{ mt: 2 }}
                    >
                      Retourner le livre
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};