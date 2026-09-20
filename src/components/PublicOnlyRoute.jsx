import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const PublicOnlyRoute = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const destination = location.state?.from?.pathname || '/';

  return isAuthenticated ? <Navigate to={destination} replace /> : <Outlet />;
};

export default PublicOnlyRoute;
