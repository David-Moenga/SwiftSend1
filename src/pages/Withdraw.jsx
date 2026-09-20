import { useState } from 'react';
import { useAuth } from '../auth/AuthContext';

const Withdraw = () => {
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('bank');
  const [accountDetails, setAccountDetails] = useState('');
  const [message, setMessage] = useState('');
  const { authFetch } = useAuth();

  const handleWithdraw = async (e) => {
    e.preventDefault();

    try {
      const response = await authFetch('/api/withdrawals/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount,
          method,
          account_details: accountDetails,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Withdrawal request submitted successfully!');
        setAmount('');
        setAccountDetails('');
      } else {
        setMessage(data.error || 'Something went wrong.');
      }
    } catch {
      setMessage('Network error. Please try again.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">Withdraw Funds</h2>

      {message && (
        <div className="mb-4 text-sm text-blue-600">
          {message}
        </div>
      )}

      <form onSubmit={handleWithdraw} className="space-y-4">
        <div>
          <label className="block mb-1 text-sm font-medium text-gray-700">Amount</label>
          <input
            type="number"
            className="w-full px-4 py-2 border rounded-md"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium text-gray-700">Withdrawal Method</label>
          <select
            className="w-full px-4 py-2 border rounded-md"
            value={method}
            onChange={(e) => setMethod(e.target.value)}
          >
            <option value="bank">Bank Transfer</option>
            <option value="mobile">Mobile Money</option>
            <option value="crypto">Cryptocurrency</option>
          </select>
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium text-gray-700">Account Details</label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded-md"
            value={accountDetails}
            onChange={(e) => setAccountDetails(e.target.value)}
            placeholder="e.g., Bank account or wallet ID"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Submit Withdrawal
        </button>
      </form>
    </div>
  );
};

export default Withdraw;
