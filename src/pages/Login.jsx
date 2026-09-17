import { Link } from 'react-router-dom';

const Login = () => {
  return (
    <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
      <div className="bg-white shadow-lg rounded-xl p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold text-center text-[#2C3E50] mb-6">Login to SwiftSend</h2>
        
        <form className="space-y-5">
          <div className="relative">
            <input
              type="email"
              id="email"
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

          <button
            type="submit"
            className="w-full bg-[#2C3E50] text-white py-2 rounded-md hover:bg-[#1B2B3A] transition duration-200"
          >
            Login
          </button>
        </form>

        <p className="mt-4 text-sm text-center text-gray-600">
          Don&apos;t have an account?{" "}
          <Link to="/register" className="text-[#2C3E50] hover:underline">Register here</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
