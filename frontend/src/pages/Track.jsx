import { useState } from 'react';

const Track = () => {
  const [refId, setRefId] = useState('');
  const [result, setResult] = useState(null);

  const mockTrack = () => {
    // Mock data (you can replace this with real API call)
    if (refId === 'TXN001') {
      setResult({
        status: 'Success',
        recipient: 'John Doe',
        country: 'Kenya',
        amountSent: '100 USD',
        received: '10900 KES',
        date: '2025-05-06',
        progress: ['Initiated', 'Processed', 'Completed'],
      });
    } else {
      setResult({ error: 'Transaction not found. Please check your reference ID.' });
    }
  };

  const statusColors = {
    Success: 'bg-green-100 text-green-700',
    Pending: 'bg-yellow-100 text-yellow-700',
    Failed: 'bg-red-100 text-red-700',
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] p-6">
      <h2 className="text-3xl font-bold text-[#2C3E50] mb-6">Track Transfer</h2>

      <div className="max-w-xl bg-white p-6 rounded-xl shadow-md mx-auto">
        <label className="block text-sm text-gray-600 mb-2">Enter Transaction Reference ID</label>
        <input
          value={refId}
          onChange={(e) => setRefId(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg mb-4"
          placeholder="e.g. TXN001"
        />
        <button
          onClick={mockTrack}
          className="bg-[#2C3E50] text-white px-6 py-2 rounded-lg hover:bg-[#1f2c3e]"
        >
          Track
        </button>

        {result && (
          <div className="mt-6">
            {result.error ? (
              <p className="text-red-600">{result.error}</p>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-500">Status</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[result.status]}`}>
                    {result.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Recipient</span>
                  <span>{result.recipient}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Country</span>
                  <span>{result.country}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Amount Sent</span>
                  <span>{result.amountSent}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Amount Received</span>
                  <span>{result.received}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Date</span>
                  <span>{result.date}</span>
                </div>

                <div className="mt-6">
                  <h4 className="font-semibold text-gray-700 mb-2">Progress</h4>
                  <ol className="relative border-l border-gray-200">
                    {result.progress.map((step, index) => (
                      <li key={index} className="mb-4 ml-4">
                        <div className="absolute w-3 h-3 bg-[#2C3E50] rounded-full -left-1.5 top-1" />
                        <p className="text-gray-700">{step}</p>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Track;
