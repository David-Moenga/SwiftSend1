import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';

const Register = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.register(form);
      navigate('/login');
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
      <div className="bg-white shadow-lg rounded-xl p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold text-center text-[#2C3E50] mb-6">Create Account</h2>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="relative">
            <input
              type="text"
              id="name"
              name="name"
              value={form.name}
              onChange={handleChange}
              required
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
              name="email"
              value={form.email}
              onChange={handleChange}
              required
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
              name="password"
              value={form.password}
              onChange={handleChange}
              required
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

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#2C3E50] text-white py-2 rounded-md hover:bg-[#1B2B3A] transition duration-200 disabled:opacity-60"
          >
            {loading ? 'Creating account...' : 'Register'}
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
