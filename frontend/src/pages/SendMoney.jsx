import { useState } from 'react';

const SendMoney = () => {
  const [recipient, setRecipient] = useState({
    name: '',
    email: '',
    country: '',
  });

  const [amount, setAmount] = useState({
    send: '',
    currency: 'USD',
  });

  const [method, setMethod] = useState('wallet');

  const fee = 1.5; // static for now
  const exchangeRate = 110.3; // sample rate USD → local

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Transfer initiated!');
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] py-12 px-4 flex justify-center">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-2xl shadow max-w-2xl w-full space-y-6 border"
      >
        <h2 className="text-3xl font-bold text-[#2C3E50] text-center mb-4">Send Money</h2>

        {/* Recipient Details */}
        <div>
          <label className="block mb-1 text-sm font-semibold text-[#2C3E50]">Recipient Name</label>
          <input
            type="text"
            value={recipient.name}
            onChange={(e) => setRecipient({ ...recipient, name: e.target.value })}
            className="w-full px-4 py-2 rounded border outline-none"
            required
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block mb-1 text-sm font-semibold text-[#2C3E50]">Email / Phone</label>
            <input
              type="text"
              value={recipient.email}
              onChange={(e) => setRecipient({ ...recipient, email: e.target.value })}
              className="w-full px-4 py-2 rounded border outline-none"
              required
            />
          </div>
          <div>
            <label className="block mb-1 text-sm font-semibold text-[#2C3E50]">Country</label>
            <select
              value={recipient.country}
              onChange={(e) => setRecipient({ ...recipient, country: e.target.value })}
              className="w-full px-4 py-2 rounded border"
              required
            >
              <option value="">Select country</option>
              <option value="Kenya">Kenya</option>
              <option value="Ghana">Ghana</option>
              <option value="Nigeria">Nigeria</option>
              <option value="Mexico">Mexico</option>
            </select>
          </div>
        </div>

        {/* Amount Section */}
        <div className="grid md:grid-cols-2 gap-4 items-end">
          <div>
            <label className="block mb-1 text-sm font-semibold text-[#2C3E50]">Amount to Send</label>
            <input
              type="number"
              value={amount.send}
              onChange={(e) => setAmount({ ...amount, send: e.target.value })}
              className="w-full px-4 py-2 rounded border outline-none"
              required
            />
          </div>
          <div>
            <label className="block mb-1 text-sm font-semibold text-[#2C3E50]">Currency</label>
            <select
              value={amount.currency}
              onChange={(e) => setAmount({ ...amount, currency: e.target.value })}
              className="w-full px-4 py-2 rounded border"
              required
            >
              <option value="USD">USD</option>
              <option value="KES">KES</option>
              <option value="NGN">NGN</option>
              <option value="MXN">MXN</option>
            </select>
          </div>
        </div>

        {/* Payment Method */}
        <div>
          <label className="block mb-1 text-sm font-semibold text-[#2C3E50]">Payment Method</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="w-full px-4 py-2 rounded border"
          >
            <option value="wallet">Wallet</option>
            <option value="card">Debit/Credit Card</option>
            <option value="bank">Bank Transfer</option>
          </select>
        </div>

        {/* Summary Card */}
        <div className="bg-[#F1F3F5] p-4 rounded-lg border">
          <h4 className="text-lg font-semibold mb-2 text-[#2C3E50]">Transfer Summary</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>Recipient: {recipient.name || '—'}</li>
            <li>Amount: {amount.send || 0} {amount.currency}</li>
            <li>Fee: ${fee}</li>
            <li>
              Estimated Receive: {(amount.send - fee) * exchangeRate || 0}{' '}
              {recipient.country === 'Kenya' ? 'KES' : 'local'}
            </li>
          </ul>
        </div>

        {/* Submit */}
        <button
          type="submit"
          className="bg-[#1ABC9C] text-white px-6 py-3 rounded-full w-full font-semibold hover:bg-[#16a085] transition"
        >
          Send Now
        </button>
      </form>
    </div>
  );
};

export default SendMoney;
