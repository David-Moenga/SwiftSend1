import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import DarkModeToggle from './DarkModeToggle';
import { useAuth } from '../auth/AuthContext';

const linkClass = ({ isActive }) => `text-sm font-medium transition ${isActive ? 'text-[#0f766e]' : 'text-slate-600 hover:text-slate-950'}`;

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, signOut } = useAuth();

  const closeMenu = () => setIsOpen(false);

  const handleSignOut = async () => {
    await signOut();
    closeMenu();
  };

  const publicLinks = [
    { to: '/', label: 'Home' },
    { to: '/login', label: 'Login' },
    { to: '/register', label: 'Register' },
  ];

  const protectedLinks = [
    { to: '/', label: 'Home' },
    { to: '/send', label: 'Send' },
    { to: '/wallet', label: 'Wallet' },
    { to: '/history', label: 'History' },
    { to: '/track', label: 'Track' },
    { to: '/profile', label: 'Profile' },
    { to: '/withdraw', label: 'Withdraw' },
  ];

  const links = isAuthenticated ? protectedLinks : publicLinks;

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/75 bg-white/90 backdrop-blur-xl">
      <nav className="mx-auto flex h-[76px] max-w-7xl items-center justify-between px-5 lg:px-8">
        <Link to="/" className="flex items-center gap-2.5" onClick={closeMenu}>
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#0f766e] shadow-lg shadow-teal-900/15">
            <span className="relative block h-4 w-5">
              <i className="absolute left-0 top-1 block h-1.5 w-4 rounded-full bg-white" />
              <i className="absolute right-0 top-4 block h-1.5 w-5 rounded-full bg-[#9ff4dc]" />
            </span>
          </span>
          <span className="text-xl font-bold tracking-[-0.04em] text-slate-950">SwiftSend</span>
        </Link>

        <div className="hidden items-center gap-8 lg:flex">
          {links.map(({ to, label }) => (
            <NavLink key={to + label} to={to} className={linkClass} onClick={closeMenu}>
              {label}
            </NavLink>
          ))}

          {isAuthenticated && (
            <button
              type="button"
              onClick={handleSignOut}
              className="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Log out
            </button>
          )}
        </div>

        <div className="hidden items-center gap-3 lg:flex">
          <DarkModeToggle />
          {!isAuthenticated && (
            <>
              <Link to="/login" className="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
                Log in
              </Link>
              <Link to="/register" className="inline-flex items-center gap-1.5 rounded-lg bg-[#0f766e] px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-900/15 transition hover:bg-[#0b645e]">
                Get started
              </Link>
            </>
          )}
        </div>

        <button
          className="inline-flex min-h-11 items-center gap-2 rounded-xl px-3 text-sm font-semibold text-slate-800 transition hover:bg-slate-100 focus:outline-none focus:ring-4 focus:ring-[#dff7ef] lg:hidden"
          onClick={() => setIsOpen(!isOpen)}
          aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={isOpen}
          aria-controls="mobile-navigation"
        >
          <span className="hidden sm:inline">Menu</span>
          {isOpen ? <X size={21} /> : <Menu size={21} />}
        </button>
      </nav>

      {isOpen && (
        <div id="mobile-navigation" className="fixed inset-x-0 bottom-0 top-[76px] z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Mobile navigation">
          <button className="absolute inset-0 cursor-default bg-[#102522]/20 backdrop-blur-[1px]" onClick={closeMenu} aria-label="Close navigation menu" />
          <div className="absolute inset-x-3 top-3 max-h-[calc(100vh-100px)] overflow-y-auto rounded-2xl border border-slate-200 bg-white p-3 shadow-[0_24px_55px_-18px_rgba(15,35,31,.32)] sm:left-auto sm:right-5 sm:w-[380px]">
            <div className="flex items-center justify-between px-2 pb-3 pt-1">
              <div>
                <p className="text-sm font-bold text-slate-900">Explore SwiftSend</p>
                <p className="mt-0.5 text-xs text-slate-500">Move money, simply.</p>
              </div>
              <button onClick={closeMenu} className="grid h-9 w-9 place-items-center rounded-lg text-slate-500 hover:bg-slate-100" aria-label="Close navigation menu">
                <X size={19} />
              </button>
            </div>

            <div className="space-y-1 border-y border-slate-100 py-2">
              {links.map(({ to, label }) => (
                <NavLink
                  key={to + label}
                  to={to}
                  onClick={closeMenu}
                  className={({ isActive }) => `group flex items-center gap-3 rounded-xl px-3 py-3 transition ${isActive ? 'bg-[#eafaf4] text-[#087869]' : 'text-slate-700 hover:bg-slate-50'}`}
                >
                  <span className="block text-sm font-bold">{label}</span>
                </NavLink>
              ))}
            </div>

            <div className="mt-3 flex items-center justify-between">
              <DarkModeToggle />
              {isAuthenticated && (
                <button type="button" onClick={handleSignOut} className="rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                  Log out
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
