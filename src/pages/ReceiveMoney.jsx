import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BadgeCheck, Building2, CheckCircle2, Copy, Smartphone, WalletCards } from 'lucide-react';

const options = [
  { id: 'mobile', icon: <Smartphone size={21} />, title: 'Mobile money', detail: 'Receive directly to your mobile wallet', time: 'In minutes' },
  { id: 'bank', icon: <Building2 size={21} />, title: 'Bank account', detail: 'Deposit into your local bank account', time: '1–2 business days' },
  { id: 'wallet', icon: <WalletCards size={21} />, title: 'SwiftSend wallet', detail: 'Hold, send or withdraw when you choose', time: 'Instant' },
];

const ReceiveMoney = () => {
  const [selected, setSelected] = useState('mobile');
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard?.writeText('SS-994-218-KE'); setCopied(true); setTimeout(() => setCopied(false), 1600); };

  return <div className="bg-[#f7f9fc]">
    <section className="mx-auto max-w-7xl px-5 py-14 lg:px-8 lg:py-20">
      <div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-[.17em] text-[#0f8c76]">Receive money</p><h1 className="mt-3 text-4xl font-bold tracking-[-.055em] text-slate-950 sm:text-5xl">Getting paid from abroad, made easy.</h1><p className="mt-5 text-lg leading-8 text-slate-600">Choose how you’d like to receive. Your sender can pay in their local currency, and you’ll get the money where it works best for you.</p></div>
      <div className="mt-12 grid gap-7 lg:grid-cols-[1fr_.85fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"><h2 className="text-xl font-bold tracking-[-.03em]">Where should your money arrive?</h2><div className="mt-6 space-y-3">{options.map((option) => <button key={option.id} onClick={() => setSelected(option.id)} className={`flex w-full items-center gap-4 rounded-2xl border p-4 text-left transition ${selected === option.id ? 'border-[#4cbfa5] bg-[#f3fcf9] ring-1 ring-[#4cbfa5]' : 'border-slate-200 hover:border-slate-300'}`}><span className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl ${selected === option.id ? 'bg-[#d9f6eb] text-[#087869]' : 'bg-slate-100 text-slate-600'}`}>{option.icon}</span><span className="min-w-0 flex-1"><span className="block font-bold text-slate-900">{option.title}</span><span className="mt-0.5 block text-sm text-slate-500">{option.detail}</span></span><span className="hidden text-xs font-semibold text-[#087869] sm:block">{option.time}</span></button>)}</div><Link to="/register" className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-[#0f766e] py-3.5 text-sm font-semibold text-white hover:bg-[#0b645e]">Set up to receive <ArrowRight size={17} /></Link></div>
        <aside className="rounded-3xl bg-[#102522] p-6 text-white sm:p-8"><span className="grid h-11 w-11 place-items-center rounded-xl bg-white/10 text-[#83e5c8]"><BadgeCheck size={22} /></span><h2 className="mt-5 text-2xl font-bold tracking-[-.04em]">Share your receive details</h2><p className="mt-3 leading-7 text-slate-300">Give this reference to someone sending money to you with SwiftSend.</p><div className="mt-7 rounded-2xl bg-white/[.08] p-4"><p className="text-xs font-semibold uppercase tracking-[.14em] text-[#8be3c9]">Your SwiftSend ID</p><div className="mt-2 flex items-center justify-between gap-2"><span className="font-mono text-lg font-semibold tracking-wide">SS-994-218-KE</span><button onClick={copy} className="rounded-lg bg-white/10 p-2 text-white hover:bg-white/20" aria-label="Copy SwiftSend ID">{copied ? <CheckCircle2 size={17} className="text-[#83e5c8]" /> : <Copy size={17} />}</button></div></div><div className="mt-6 space-y-3 text-sm text-slate-200"><p className="flex gap-2"><CheckCircle2 size={18} className="shrink-0 text-[#83e5c8]" />No fee to receive into your SwiftSend wallet</p><p className="flex gap-2"><CheckCircle2 size={18} className="shrink-0 text-[#83e5c8]" />We’ll notify you the moment it arrives</p></div></aside>
      </div>
    </section>
  </div>;
};

export default ReceiveMoney;
