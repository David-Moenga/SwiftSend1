import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { apiUrl } from '../auth/api';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await fetch(apiUrl('/api/auth/register/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ name, email, password }),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || data.error || data.message || 'Unable to create your account.');
      }

      const authData = data.data ?? data;
      const hasSession = Boolean(
        authData.accessToken
        || authData.access_token
        || authData.access
        || authData.token
        || authData.authenticated,
      );

      if (hasSession) {
        signIn(data);
        navigate('/', { replace: true });
        return;
      }

      navigate('/login', { replace: true, state: { registrationSuccess: true } });
    } catch (requestError) {
      setError(requestError.message || 'Unable to create your account. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
      <div className="bg-white shadow-lg rounded-xl p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold text-center text-[#2C3E50] mb-6">Create Account</h2>

        {error && (
          <p className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">
            {error}
          </p>
        )}

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="relative">
            <input
              type="text"
              id="name"
              required
              autoComplete="name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="peer w-full px-3 pt-5 pb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#2C3E50] focus:border-transparent"
              placeholder=" "
            />
            <label
              htmlFor="name"
              className="absolute left-3 top-2 text-sm text-gray-500 transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:top-2 peer-focus:text-sm peer-focus:text-[#2C3E50]"
            >
              Full Name
            </label>
          </div>

          <div className="relative">
            <input
              type="email"
              id="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="peer w-full px-3 pt-5 pb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#2C3E50] focus:border-transparent"
              placeholder=" "
            />
            <label
              htmlFor="email"
              className="absolute left-3 top-2 text-sm text-gray-500 transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:top-2 peer-focus:text-sm peer-focus:text-[#2C3E50]"
            >
              Email
            </label>
          </div>

          <div className="relative">
            <input
              type="password"
              id="password"
              required
              autoComplete="new-password"
              minLength="8"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="peer w-full px-3 pt-5 pb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#2C3E50] focus:border-transparent"
              placeholder=" "
            />
            <label
              htmlFor="password"
              className="absolute left-3 top-2 text-sm text-gray-500 transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:top-2 peer-focus:text-sm peer-focus:text-[#2C3E50]"
            >
              Password
            </label>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-[#2C3E50] text-white py-2 rounded-md hover:bg-[#1B2B3A] transition duration-200"
          >
            {isSubmitting ? 'Creating account…' : 'Register'}
          </button>
        </form>

        <p className="mt-4 text-sm text-center text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-[#2C3E50] hover:underline">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
