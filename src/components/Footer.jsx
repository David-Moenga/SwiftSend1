import { Link } from 'react-router-dom';

const Footer = () => (
  <footer className="bg-[#102522] text-white">
    <div className="mx-auto max-w-7xl px-5 pb-8 pt-14 lg:px-8">
      <div className="grid gap-10 md:grid-cols-[1.45fr_repeat(3,1fr)]">
        <div><Link to="/" className="flex items-center gap-2.5"><span className="grid h-9 w-9 place-items-center rounded-xl bg-[#35d3a6] text-xl font-black text-[#102522]">S</span><span className="text-xl font-bold tracking-[-0.04em]">SwiftSend</span></Link><p className="mt-4 max-w-xs text-sm leading-6 text-slate-300">A simpler way to move money across borders — built for speed, security, and real life.</p></div>
        <FooterColumn title="Personal" links={[['Send money', '/send'], ['Receive money', '/receive'], ['Exchange rates', '/rates'], ['Track a transfer', '/track']]} />
        <FooterColumn title="Company" links={[['About us', '/help'], ['Security', '/help'], ['Careers', '/help'], ['Contact', '/help']]} />
        <FooterColumn title="Support" links={[['Help centre', '/help'], ['Status', '/help'], ['Terms of use', '/help'], ['Privacy policy', '/help']]} />
      </div>
      <div className="mt-12 flex flex-col gap-3 border-t border-white/10 pt-6 text-xs text-slate-400 sm:flex-row sm:items-center sm:justify-between"><span>© {new Date().getFullYear()} SwiftSend. All rights reserved.</span><span>Payments made simple, wherever life takes you.</span></div>
    </div>
  </footer>
);

const FooterColumn = ({ title, links }) => <div><h3 className="text-sm font-semibold text-white">{title}</h3><ul className="mt-4 space-y-3">{links.map(([label, to]) => <li key={label}><Link to={to} className="text-sm text-slate-300 transition hover:text-[#7ee7ca]">{label}</Link></li>)}</ul></div>;

export default Footer;
