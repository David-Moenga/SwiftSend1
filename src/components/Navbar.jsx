import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react'; // Optional: install lucide-react for icons
import DarkModeToggle from './DarkModeToggle';
import { useAuth } from '../auth/AuthContext';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, signOut } = useAuth();

  const closeMenu = () => setIsOpen(false);

  const handleSignOut = async () => {
    await signOut();
    closeMenu();
  };

  return (
    <nav className="bg-[#2C3E50] text-white p-4">
      <div className="flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">SwiftSend</Link>
        
        {/* Hamburger for mobile */}
        <button
          className="md:hidden"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Desktop links */}
        <div className="hidden md:flex space-x-4">
          <Link to="/">Home</Link>
          {isAuthenticated ? (
            <>
              <Link to="/send">Send</Link>
              <Link to="/wallet">Wallet</Link>
              <Link to="/history">History</Link>
              <Link to="/track">Track</Link>
              <Link to="/profile">Profile</Link>
              <Link to="/withdraw">Withdraw</Link>
              <button type="button" onClick={handleSignOut}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
        <DarkModeToggle />
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="flex flex-col space-y-2 mt-2 md:hidden">
          <Link to="/" onClick={closeMenu}>Home</Link>
          {isAuthenticated ? (
            <>
              <Link to="/send" onClick={closeMenu}>Send</Link>
              <Link to="/wallet" onClick={closeMenu}>Wallet</Link>
              <Link to="/history" onClick={closeMenu}>History</Link>
              <Link to="/track" onClick={closeMenu}>Track</Link>
              <Link to="/profile" onClick={closeMenu}>Profile</Link>
              <Link to="/withdraw" onClick={closeMenu}>Withdraw</Link>
              <button type="button" className="text-left" onClick={handleSignOut}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={closeMenu}>Login</Link>
              <Link to="/register" onClick={closeMenu}>Register</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
