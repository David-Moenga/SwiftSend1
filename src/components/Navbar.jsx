import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X, ArrowUpRight } from 'lucide-react';

const linkClass = ({ isActive }) => `text-sm font-medium transition ${isActive ? 'text-[#0f766e]' : 'text-slate-600 hover:text-slate-950'}`;

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const close = () => setIsOpen(false);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/75 bg-white/90 backdrop-blur-xl">
      <nav className="mx-auto flex h-[76px] max-w-7xl items-center justify-between px-5 lg:px-8">
        <Link to="/" className="flex items-center gap-2.5" onClick={close}>
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#0f766e] shadow-lg shadow-teal-900/15">
            <span className="relative block h-4 w-5"><i className="absolute left-0 top-1 block h-1.5 w-4 rounded-full bg-white" /><i className="absolute right-0 top-4 block h-1.5 w-5 rounded-full bg-[#9ff4dc]" /></span>
          </span>
          <span className="text-xl font-bold tracking-[-0.04em] text-slate-950">SwiftSend</span>
        </Link>

        <div className="hidden items-center gap-8 lg:flex">
          <NavLink to="/send" className={linkClass}>Send money</NavLink>
          <NavLink to="/receive" className={linkClass}>Receive money</NavLink>
          <NavLink to="/rates" className={linkClass}>Exchange rates</NavLink>
          <NavLink to="/track" className={linkClass}>Track a transfer</NavLink>
          <NavLink to="/help" className={linkClass}>Help</NavLink>
        </div>

        <div className="hidden items-center gap-3 lg:flex">
          <Link to="/login" className="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">Log in</Link>
          <Link to="/register" className="inline-flex items-center gap-1.5 rounded-lg bg-[#0f766e] px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-900/15 transition hover:bg-[#0b645e]">Get started <ArrowUpRight size={15} /></Link>
        </div>

        <button className="rounded-lg p-2 text-slate-800 lg:hidden" onClick={() => setIsOpen(!isOpen)} aria-label="Toggle navigation">{isOpen ? <X size={23} /> : <Menu size={23} />}</button>
      </nav>

      {isOpen && <div className="border-t border-slate-100 bg-white px-5 pb-5 pt-3 lg:hidden">
        <div className="mx-auto flex max-w-7xl flex-col gap-1">
          {[['/send', 'Send money'], ['/receive', 'Receive money'], ['/rates', 'Exchange rates'], ['/track', 'Track a transfer'], ['/help', 'Help center']].map(([to, label]) => <Link key={to} to={to} onClick={close} className="rounded-lg px-3 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50">{label}</Link>)}
          <div className="mt-2 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4"><Link to="/login" onClick={close} className="rounded-lg border border-slate-200 py-2.5 text-center text-sm font-semibold">Log in</Link><Link to="/register" onClick={close} className="rounded-lg bg-[#0f766e] py-2.5 text-center text-sm font-semibold text-white">Get started</Link></div>
        </div>
      </div>}
    </header>
  );
};

export default Navbar;
