import { useState } from 'react';

const Wallet = () => {
  const [balance] = useState(420.50); // In USD
  const [transactions] = useState([
    {
      id: 'TXN1001',
      type: 'Credit',
      amount: 150,
      date: '2025-05-06',
      status: 'Success',
    },
    {
      id: 'TXN1000',
      type: 'Debit',
      amount: 80,
      date: '2025-05-04',
      status: 'Success',
    },
    {
      id: 'TXN0999',
      type: 'Debit',
      amount: 50,
      date: '2025-05-03',
      status: 'Pending',
    },
  ]);

  const statusColor = {
    Success: 'text-green-600',
    Pending: 'text-yellow-500',
    Failed: 'text-red-500',
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] p-6">
      <h2 className="text-3xl font-bold text-[#2C3E50] mb-6">My Wallet</h2>

      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Wallet Summary */}
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-gray-600 mb-2">Current Balance</h3>
          <div className="text-4xl font-bold text-[#2C3E50] mb-4">${balance.toFixed(2)}</div>

          <div className="flex gap-4">
            <button className="flex-1 bg-[#2C3E50] text-white px-4 py-2 rounded-lg hover:bg-[#1f2c3e]">
              Fund Wallet
            </button>
            <button className="flex-1 border border-[#2C3E50] text-[#2C3E50] px-4 py-2 rounded-lg hover:bg-gray-100">
              Withdraw
            </button>
          </div>
        </div>

        {/* Transaction History */}
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-xl font-semibold text-[#2C3E50] mb-4">Recent Activity</h3>
          <ul className="divide-y">
            {transactions.map(txn => (
              <li key={txn.id} className="py-3 flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium">{txn.type} — ${txn.amount.toFixed(2)}</p>
                  <p className="text-xs text-gray-500">{txn.date}</p>
                </div>
                <span className={`text-sm font-medium ${statusColor[txn.status]}`}>
                  {txn.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Wallet;
