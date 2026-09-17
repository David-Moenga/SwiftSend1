import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowDownLeft, ArrowUpRight, BadgeCheck, Check, ChevronDown, CircleDollarSign, Clock3, Globe2, Landmark, LockKeyhole, MoveRight, ShieldCheck, Smartphone, Sparkles, WalletCards } from 'lucide-react';

const destinations = {
  KES: { name: 'Kenya', flag: '🇰🇪', rate: 129.42 },
  NGN: { name: 'Nigeria', flag: '🇳🇬', rate: 1547.8 },
  GHS: { name: 'Ghana', flag: '🇬🇭', rate: 15.32 },
  PHP: { name: 'Philippines', flag: '🇵🇭', rate: 58.21 },
};

const Home = () => {
  const [amount, setAmount] = useState('1,000');
  const [currency, setCurrency] = useState('KES');
  const [open, setOpen] = useState(false);
  const amountNumber = Number(amount.replace(/,/g, '')) || 0;
  const destination = destinations[currency];
  const received = useMemo(() => new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(amountNumber * destination.rate), [amountNumber, destination.rate]);

  const changeAmount = (value) => {
    const cleaned = value.replace(/[^0-9.]/g, '');
    setAmount(cleaned ? Number(cleaned).toLocaleString('en-US') : '');
  };

  return (
    <div className="bg-white">
      <section className="relative overflow-hidden bg-[#f4fbf9]">
        <div className="absolute inset-0 dot-grid opacity-40" />
        <div className="absolute -right-36 top-10 h-[440px] w-[440px] rounded-full bg-[#d5f7ec] blur-3xl" />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-5 pb-20 pt-16 lg:grid-cols-[1.05fr_.95fr] lg:items-center lg:px-8 lg:pb-24 lg:pt-24">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#bdebdc] bg-white px-3 py-1.5 text-xs font-semibold text-[#087869] shadow-sm"><Sparkles size={14} /> Fast payments, wherever life takes you</div>
            <h1 className="mt-6 text-5xl font-bold leading-[.98] tracking-[-0.065em] text-slate-950 sm:text-6xl lg:text-7xl">Money moves<br /><span className="text-[#0f766e]">with you.</span></h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">Send money to the people you care about, quickly and securely. Great rates. Low fees. No surprises.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="inline-flex items-center gap-2 rounded-xl bg-[#0f766e] px-5 py-3.5 text-sm font-semibold text-white shadow-xl shadow-teal-900/15 transition hover:-translate-y-0.5 hover:bg-[#0b645e]">Get started free <ArrowUpRight size={17} /></Link>
              <Link to="/track" className="rounded-xl border border-slate-200 bg-white px-5 py-3.5 text-sm font-semibold text-slate-800 transition hover:border-slate-300 hover:bg-slate-50">Track a transfer</Link>
            </div>
            <div className="mt-10 flex flex-wrap items-center gap-x-7 gap-y-3 text-sm text-slate-600"><span className="inline-flex items-center gap-2"><BadgeCheck className="text-[#0f9e82]" size={18} /> FCA-regulated partner</span><span className="inline-flex items-center gap-2"><ShieldCheck className="text-[#0f9e82]" size={18} /> Bank-level security</span></div>
          </div>

          <div className="relative mx-auto w-full max-w-[470px] lg:mx-0 lg:justify-self-end">
            <div className="absolute -inset-5 rounded-[36px] bg-[#c5f2e3]/70 blur-2xl" />
            <div className="relative rounded-[28px] border border-white bg-white p-5 shadow-[0_28px_65px_-22px_rgba(15,75,65,.28)] sm:p-6">
              <div className="mb-6 flex items-center justify-between"><div><p className="text-sm font-semibold text-slate-900">Send money</p><p className="mt-1 text-xs text-slate-500">You&apos;ll always see the full cost upfront.</p></div><span className="grid h-9 w-9 place-items-center rounded-full bg-[#e7faf3] text-[#0f766e]"><Globe2 size={18} /></span></div>
              <div className="rounded-2xl border border-slate-200 p-4 transition focus-within:border-[#4ebda5] focus-within:ring-4 focus-within:ring-[#dff7ef]">
                <div className="flex items-center justify-between text-xs font-medium text-slate-500"><label htmlFor="send-amount">You send</label><span>USD</span></div>
                <div className="mt-1 flex items-center justify-between"><input id="send-amount" value={amount} onChange={(event) => changeAmount(event.target.value)} inputMode="decimal" className="min-w-0 w-44 bg-transparent text-3xl font-bold tracking-[-.04em] text-slate-900 outline-none" /><span className="rounded-lg bg-slate-100 px-2.5 py-1.5 text-sm font-semibold text-slate-700">USD</span></div>
              </div>
              <div className="relative my-2 flex justify-center"><span className="absolute top-1/2 h-px w-full bg-slate-200" /><span className="relative grid h-8 w-8 place-items-center rounded-full border border-slate-200 bg-white text-[#0f766e]"><ArrowDownLeft size={16} /></span></div>
              <div className="relative rounded-2xl border border-[#a8e5d4] bg-[#f5fcfa] p-4">
                <div className="flex items-center justify-between text-xs font-medium text-slate-500"><span>They receive</span><span>Estimated</span></div>
                <div className="mt-1 flex items-center justify-between"><span className="text-3xl font-bold tracking-[-.04em] text-slate-900">{received}</span><button type="button" onClick={() => setOpen(!open)} className="flex items-center gap-1.5 rounded-lg bg-white px-2 py-1.5 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-slate-100">{destination.flag} {currency} <ChevronDown size={14} /></button></div>
                {open && <div className="absolute right-0 top-[82px] z-10 w-44 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl">{Object.entries(destinations).map(([code, item]) => <button key={code} onClick={() => { setCurrency(code); setOpen(false); }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-slate-50">{item.flag} <span>{item.name}</span><span className="ml-auto text-xs text-slate-400">{code}</span></button>)}</div>}
              </div>
              <div className="mt-5 space-y-3 border-b border-slate-100 pb-5 text-sm"><div className="flex justify-between text-slate-600"><span>Our fee</span><span className="font-medium text-slate-800">$4.99</span></div><div className="flex justify-between text-slate-600"><span>Rate</span><span className="font-medium text-slate-800">1 USD = {destination.rate} {currency}</span></div><div className="flex justify-between text-slate-600"><span>Delivery</span><span className="font-medium text-[#087869]">In minutes</span></div></div>
              <Link to="/send" className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-[#0f766e] px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-[#0b645e]">Continue to send <MoveRight size={17} /></Link>
            </div>
            <div className="absolute -bottom-6 -left-7 hidden items-center gap-3 rounded-2xl border border-slate-100 bg-white px-4 py-3 shadow-xl shadow-slate-900/10 sm:flex"><span className="grid h-9 w-9 place-items-center rounded-full bg-[#e7faf3] text-[#0f766e]"><Check size={17} strokeWidth={3} /></span><div><p className="text-xs font-semibold text-slate-900">Delivered in 2 minutes</p><p className="mt-0.5 text-[11px] text-slate-500">Your money is on its way</p></div></div>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-100 bg-white"><div className="mx-auto grid max-w-7xl grid-cols-2 divide-x divide-y divide-slate-100 px-5 sm:grid-cols-4 sm:divide-y-0 lg:px-8"><Stat number="70+" label="countries supported" /><Stat number="4.9/5" label="average customer rating" /><Stat number="$0" label="hidden fees, ever" /><Stat number="24/7" label="transfer tracking" /></div></section>

      <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8 lg:py-28">
        <div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-[.17em] text-[#0f8c76]">Made for real life</p><h2 className="mt-3 text-3xl font-bold tracking-[-.045em] text-slate-950 sm:text-4xl">Less waiting. More together.</h2><p className="mt-4 text-lg leading-8 text-slate-600">Whether you&apos;re supporting family, paying tuition, or managing a life across borders, SwiftSend makes every transfer feel effortless.</p></div>
        <div className="mt-12 grid gap-5 md:grid-cols-3"><Feature icon={<Clock3 />} title="Fast by default" text="Most transfers arrive in minutes, with real-time updates from start to finish." /><Feature icon={<CircleDollarSign />} title="Fair, clear pricing" text="A great exchange rate and one low fee — shown before you send." /><Feature icon={<LockKeyhole />} title="Safe in every step" text="Your money and personal details are protected with industry-leading security." /></div>
      </section>

      <section className="bg-[#102522] py-20 text-white lg:py-28"><div className="mx-auto grid max-w-7xl gap-12 px-5 lg:grid-cols-[.85fr_1.15fr] lg:items-center lg:px-8"><div><p className="text-sm font-bold uppercase tracking-[.17em] text-[#76dfbf]">How it works</p><h2 className="mt-3 text-3xl font-bold tracking-[-.05em] sm:text-4xl">Three easy steps. One less thing to worry about.</h2><p className="mt-5 max-w-md leading-7 text-slate-300">From your phone to theirs, we’ve made sending money feel refreshingly simple.</p><Link to="/send" className="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-[#86e8cb] hover:text-white">Send money now <MoveRight size={16} /></Link></div><div className="grid gap-3"><Step number="01" icon={<WalletCards size={19} />} title="Set up your transfer" text="Tell us where it's going and how much you want to send." /><Step number="02" icon={<Landmark size={19} />} title="Choose how to pay" text="Pay with a card, bank transfer, or your SwiftSend wallet." /><Step number="03" icon={<Smartphone size={19} />} title="We deliver it safely" text="Your recipient gets money straight to their bank or mobile wallet." /></div></div></section>

      <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8 lg:py-28"><div className="overflow-hidden rounded-[28px] bg-[#ddf7ee] px-7 py-10 sm:px-12 lg:flex lg:items-center lg:justify-between lg:px-16 lg:py-14"><div className="max-w-xl"><p className="text-sm font-bold uppercase tracking-[.17em] text-[#087869]">Ready when you are</p><h2 className="mt-3 text-3xl font-bold tracking-[-.05em] text-slate-950 sm:text-4xl">The distance is no longer the hard part.</h2><p className="mt-4 text-slate-600">Create your free account and send your first transfer in minutes.</p></div><Link to="/register" className="mt-7 inline-flex items-center gap-2 rounded-xl bg-[#0f766e] px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-teal-900/15 transition hover:bg-[#0b645e] lg:mt-0">Create free account <ArrowUpRight size={17} /></Link></div></section>
    </div>
  );
};

const Stat = ({ number, label }) => <div className="px-4 py-7 text-center sm:py-8"><p className="text-2xl font-bold tracking-[-.04em] text-slate-950">{number}</p><p className="mt-1 text-xs text-slate-500">{label}</p></div>;
const Feature = ({ icon, title, text }) => <article className="rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-900/5"><span className="grid h-11 w-11 place-items-center rounded-xl bg-[#e7faf3] text-[#087869]">{icon}</span><h3 className="mt-5 text-lg font-bold tracking-[-.02em] text-slate-900">{title}</h3><p className="mt-2 leading-6 text-slate-600">{text}</p></article>;
const Step = ({ number, icon, title, text }) => <article className="flex gap-5 rounded-2xl border border-white/10 bg-white/[.06] p-5"><span className="text-sm font-bold text-[#70daba]">{number}</span><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white/10 text-[#86e8cb]">{icon}</span><div><h3 className="font-bold">{title}</h3><p className="mt-1 text-sm leading-6 text-slate-300">{text}</p></div></article>;

export default Home;
