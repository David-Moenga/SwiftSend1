import { useState } from 'react';

const History = () => {
  const [transactions] = useState([
    {
      id: 'TXN001',
      recipient: 'John Doe',
      country: 'Kenya',
      amountSent: 100,
      currency: 'USD',
      amountReceived: 10900,
      status: 'Success',
      date: '2025-05-06',
    },
    {
      id: 'TXN002',
      recipient: 'Amina Yusuf',
      country: 'Nigeria',
      amountSent: 50,
      currency: 'USD',
      amountReceived: 72000,
      status: 'Pending',
      date: '2025-05-05',
    },
    {
      id: 'TXN003',
      recipient: 'Carlos Mendez',
      country: 'Mexico',
      amountSent: 120,
      currency: 'USD',
      amountReceived: 2050,
      status: 'Failed',
      date: '2025-05-01',
    },
  ]);

  const statusColor = {
    Success: 'bg-green-100 text-green-700',
    Pending: 'bg-yellow-100 text-yellow-700',
    Failed: 'bg-red-100 text-red-700',
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] p-6">
      <h2 className="text-3xl font-bold text-[#2C3E50] mb-6">Transaction History</h2>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-xl shadow-md border">
          <thead className="bg-[#2C3E50] text-white">
            <tr>
              <th className="py-3 px-4 text-left">Recipient</th>
              <th className="py-3 px-4 text-left">Country</th>
              <th className="py-3 px-4 text-left">Amount Sent</th>
              <th className="py-3 px-4 text-left">Received</th>
              <th className="py-3 px-4 text-left">Status</th>
              <th className="py-3 px-4 text-left">Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.id} className="border-b hover:bg-gray-50">
                <td className="py-3 px-4">{txn.recipient}</td>
                <td className="py-3 px-4">{txn.country}</td>
                <td className="py-3 px-4">
                  {txn.amountSent} {txn.currency}
                </td>
                <td className="py-3 px-4">{txn.amountReceived.toLocaleString()}</td>
                <td className="py-3 px-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor[txn.status]}`}>
                    {txn.status}
                  </span>
                </td>
                <td className="py-3 px-4">{txn.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default History;
