import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const handleOAuthCallback = () => {
      // Get token from URL
      const params = new URLSearchParams(location.search);
      const token = params.get('token');
      const error = params.get('error');

      if (error) {
        console.error('OAuth error:', error);
        navigate('/login?error=' + error);
        return;
      }

      if (!token) {
        console.error('No token received');
        navigate('/login?error=no_token');
        return;
      }

      // Store token and redirect
      login(token);
      navigate('/admin');
    };

    handleOAuthCallback();
  }, [location, navigate, login]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <p className="text-muted-foreground">Completing authentication...</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
