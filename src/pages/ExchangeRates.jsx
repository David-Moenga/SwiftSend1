import { useMemo, useState } from 'react';
import { ArrowDownUp, Clock3, Info, TrendingUp } from 'lucide-react';

const currencies = { USD: { symbol: '$', flag: '🇺🇸', name: 'US Dollar' }, KES: { symbol: 'KSh', flag: '🇰🇪', name: 'Kenyan Shilling' }, NGN: { symbol: '₦', flag: '🇳🇬', name: 'Nigerian Naira' }, GHS: { symbol: 'GH₵', flag: '🇬🇭', name: 'Ghanaian Cedi' }, PHP: { symbol: '₱', flag: '🇵🇭', name: 'Philippine Peso' }, GBP: { symbol: '£', flag: '🇬🇧', name: 'British Pound' } };
const rates = { 'USD-KES': 129.42, 'USD-NGN': 1547.8, 'USD-GHS': 15.32, 'USD-PHP': 58.21, 'GBP-KES': 167.45, 'GBP-NGN': 2000.13 };
const usdValues = { USD: 1, KES: 129.42, NGN: 1547.8, GHS: 15.32, PHP: 58.21, GBP: 0.7729 };
const getRate = (from, to) => {
  if (from === to) return 1;
  if (rates[`${from}-${to}`]) return rates[`${from}-${to}`];
  if (rates[`${to}-${from}`]) return 1 / rates[`${to}-${from}`];
  return usdValues[to] / usdValues[from];
};

const ExchangeRates = () => {
  const [from, setFrom] = useState('USD'); const [to, setTo] = useState('KES'); const [amount, setAmount] = useState('100');
  const rate = getRate(from, to); const output = useMemo(() => (Number(amount) || 0) * rate, [amount, rate]);
  const swap = () => { const before = from; setFrom(to); setTo(before); };
  return <div className="bg-[#f7f9fc] py-14 lg:py-20"><div className="mx-auto max-w-5xl px-5 lg:px-8"><div className="text-center"><p className="text-sm font-bold uppercase tracking-[.17em] text-[#0f8c76]">Exchange rates</p><h1 className="mt-3 text-4xl font-bold tracking-[-.055em] text-slate-950 sm:text-5xl">A rate that works harder for you.</h1><p className="mx-auto mt-4 max-w-2xl text-lg leading-8 text-slate-600">See exactly what your money is worth. We keep our rates competitive and our pricing crystal clear.</p></div>
    <section className="mt-12 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8"><div className="grid items-end gap-4 md:grid-cols-[1fr_auto_1fr]"><CurrencyInput label="You send" amount={amount} onAmount={setAmount} value={from} onChange={setFrom} /><button onClick={swap} className="mx-auto grid h-10 w-10 place-items-center rounded-full border border-slate-200 text-[#0f766e] transition hover:bg-[#ecfaf5] md:mb-4" aria-label="Swap currencies"><ArrowDownUp size={18} /></button><CurrencyInput label="They receive" amount={output.toLocaleString('en-US', { maximumFractionDigits: 2 })} value={to} onChange={setTo} readOnly /></div>
      <div className="mt-7 grid gap-3 border-t border-slate-100 pt-6 sm:grid-cols-3"><RateInfo icon={<TrendingUp size={17} />} title="Current rate" text={`1 ${from} = ${rate.toLocaleString()} ${to}`} /><RateInfo icon={<Clock3 size={17} />} title="Rate updated" text="Just now" /><RateInfo icon={<Info size={17} />} title="Transfer fee" text="From $4.99" /></div></section>
    <section className="mt-10"><h2 className="text-xl font-bold tracking-[-.025em] text-slate-900">Popular corridors</h2><div className="mt-4 grid gap-3 sm:grid-cols-2"><Popular from="USD" to="KES" rate="129.42" /><Popular from="USD" to="NGN" rate="1,547.80" /><Popular from="USD" to="PHP" rate="58.21" /><Popular from="GBP" to="KES" rate="167.45" /></div></section>
  </div></div>;
};

const CurrencyInput = ({ label, amount, onAmount, value, onChange, readOnly }) => <div className="rounded-2xl border border-slate-200 p-4"><label className="text-sm font-semibold text-slate-600">{label}</label><div className="mt-2 flex items-center gap-2"><input value={amount} onChange={(e) => onAmount?.(e.target.value)} readOnly={readOnly} inputMode="decimal" className="min-w-0 flex-1 bg-transparent text-2xl font-bold tracking-[-.04em] outline-none read-only:text-slate-900" /><select value={value} onChange={(e) => onChange(e.target.value)} className="max-w-[125px] rounded-lg bg-slate-100 px-2 py-2 text-sm font-bold text-slate-700 outline-none">{Object.entries(currencies).map(([code, data]) => <option key={code} value={code}>{data.flag} {code}</option>)}</select></div><p className="mt-2 text-xs text-slate-400">{currencies[value].name}</p></div>;
const RateInfo = ({ icon, title, text }) => <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3"><span className="text-[#0f8c76]">{icon}</span><div><p className="text-xs text-slate-500">{title}</p><p className="mt-0.5 text-sm font-semibold text-slate-800">{text}</p></div></div>;
const Popular = ({ from, to, rate }) => <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-4"><div className="flex items-center gap-2"><span>{currencies[from].flag}</span><span className="font-semibold text-slate-800">{from}</span><span className="text-slate-400">→</span><span>{currencies[to].flag}</span><span className="font-semibold text-slate-800">{to}</span></div><span className="text-sm font-bold text-[#087869]">{rate}</span></div>;

export default ExchangeRates;
