import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react'; // Optional: install lucide-react for icons
import DarkModeToggle from './DarkModeToggle';
import { useAuth } from '../auth/AuthContext';

import { useEffect, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X, ArrowUpRight, ChevronRight, CircleHelp, Send, ArrowDownToLine, BarChart3, MapPin } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

const linkClass = ({ isActive }) => `text-sm font-medium transition ${isActive ? 'text-[#0f766e]' : 'text-slate-600 hover:text-slate-950'}`;


const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, signOut } = useAuth();

  const close = () => setIsOpen(false);


  const closeMenu = () => setIsOpen(false);

  const handleSignOut = async () => {
    await signOut();
    closeMenu();
  };

  const handleSignOut = async () => {
    await signOut();
    close();
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

          <>
            <header className="sticky top-0 z-[60] border-b border-slate-200/75 bg-white/90 backdrop-blur-xl">
              <nav className="mx-auto flex h-[76px] max-w-7xl items-center justify-between px-5 lg:px-8">
                <Link to="/" className="flex items-center gap-2.5" onClick={close}>
                  <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#0f766e] shadow-lg shadow-teal-900/15">
                    <span className="relative block h-4 w-5">
                      <i className="absolute left-0 top-1 block h-1.5 w-4 rounded-full bg-white" />
                      <i className="absolute right-0 top-4 block h-1.5 w-5 rounded-full bg-[#9ff4dc]" />
                    </span>
                  </span>
                  <span className="text-xl font-bold tracking-[-0.04em] text-slate-950">SwiftSend</span>
                </Link>

                <div className="hidden items-center gap-8 lg:flex">
                  <NavLink to="/send" className={linkClass}>Send money</NavLink>
                  <NavLink to="/receive" className={linkClass}>Receive money</NavLink>
                  <NavLink to="/rates" className={linkClass}>Exchange rates</NavLink>
                  <NavLink to="/track" className={linkClass}>Track a transfer</NavLink>
                  <NavLink to="/help" className={linkClass}>Help</NavLink>

                  {isAuthenticated && (
                    <>
                      <NavLink to="/wallet" className={linkClass}>Wallet</NavLink>
                      <NavLink to="/history" className={linkClass}>History</NavLink>
                      <NavLink to="/profile" className={linkClass}>Profile</NavLink>
                      <NavLink to="/withdraw" className={linkClass}>Withdraw</NavLink>
                    </>
                  )}
                </div>

                <div className="hidden items-center gap-3 lg:flex">
                  {isAuthenticated ? (
                    <button
                      type="button"
                      onClick={handleSignOut}
                      className="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                    >
                      Log out
                    </button>
                  ) : (
                    <>
                      <Link to="/login" className="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">Log in</Link>
                      <Link to="/register" className="inline-flex items-center gap-1.5 rounded-lg bg-[#0f766e] px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-900/15 transition hover:bg-[#0b645e]">
                        Get started <ArrowUpRight size={15} />
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
            </header>

            {isOpen && (
              <div id="mobile-navigation" className="fixed inset-x-0 bottom-0 top-[76px] z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Mobile navigation">
                <button className="absolute inset-0 cursor-default bg-[#102522]/20 backdrop-blur-[1px]" onClick={close} aria-label="Close navigation menu" />
                <div className="absolute inset-x-3 top-3 max-h-[calc(100vh-100px)] overflow-y-auto rounded-2xl border border-slate-200 bg-white p-3 shadow-[0_24px_55px_-18px_rgba(15,35,31,.32)] sm:left-auto sm:right-5 sm:w-[380px]">
                  <div className="flex items-center justify-between px-2 pb-3 pt-1">
                    <div>
                      <p className="text-sm font-bold text-slate-900">Explore SwiftSend</p>
                      <p className="mt-0.5 text-xs text-slate-500">Move money, simply.</p>
                    </div>
                    <button onClick={close} className="grid h-9 w-9 place-items-center rounded-lg text-slate-500 hover:bg-slate-100" aria-label="Close navigation menu">
                      <X size={19} />
                    </button>
                  </div>

                  <div className="space-y-1 border-y border-slate-100 py-2">
                    <MobileNavLink to="/send" label="Send money" description="Start a secure transfer" icon={<Send size={18} />} onClick={close} />
                    <MobileNavLink to="/receive" label="Receive money" description="Choose where it arrives" icon={<ArrowDownToLine size={18} />} onClick={close} />
                    <MobileNavLink to="/rates" label="Exchange rates" description="Check today’s rate" icon={<BarChart3 size={18} />} onClick={close} />
                    <MobileNavLink to="/track" label="Track a transfer" description="Follow your money" icon={<MapPin size={18} />} onClick={close} />
                    <MobileNavLink to="/help" label="Help centre" description="Find answers quickly" icon={<CircleHelp size={18} />} onClick={close} />

                    {isAuthenticated && (
                      <>
                        <MobileNavLink to="/wallet" label="Wallet" description="Manage your balance" icon={<BarChart3 size={18} />} onClick={close} />
                        <MobileNavLink to="/history" label="History" description="Review recent activity" icon={<MapPin size={18} />} onClick={close} />
                        <MobileNavLink to="/profile" label="Profile" description="Update your account" icon={<CircleHelp size={18} />} onClick={close} />
                        <MobileNavLink to="/withdraw" label="Withdraw" description="Move funds out" icon={<ArrowUpRight size={18} />} onClick={close} />
                      </>
                    )}
                  </div>

                  {isAuthenticated ? (
                    <div className="pt-3">
                      <button type="button" onClick={handleSignOut} className="w-full rounded-xl border border-slate-200 py-3 text-center text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                        Log out
                      </button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-3 pt-3">
                      <Link to="/login" onClick={close} className="rounded-xl border border-slate-200 py-3 text-center text-sm font-semibold text-slate-700 transition hover:bg-slate-50">Log in</Link>
                      <Link to="/register" onClick={close} className="rounded-xl bg-[#0f766e] py-3 text-center text-sm font-semibold text-white shadow-lg shadow-teal-900/15 transition hover:bg-[#0b645e]">
                        Get started
                      </Link>
                    </div>
                  )}
                </div>
                e3232b2 (enhanced the structure of the app)
              </div>
            )}
          </nav>
          );
};



          const MobileNavLink = ({to, label, description, icon, onClick}) => (
          <NavLink
            to={to}
            onClick={onClick}
            className={({ isActive }) => `group flex items-center gap-3 rounded-xl px-3 py-3 transition ${isActive ? 'bg-[#eafaf4] text-[#087869]' : 'text-slate-700 hover:bg-slate-50'}`}
          >
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-slate-100 text-slate-600 transition group-hover:bg-[#e7faf3] group-hover:text-[#087869]">{icon}</span>
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-bold">{label}</span>
              <span className="mt-0.5 block text-xs font-medium text-slate-500">{description}</span>
            </span>
            <ChevronRight size={17} className="text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-[#087869]" />
          </NavLink>
          );

          
          export default Navbar;
