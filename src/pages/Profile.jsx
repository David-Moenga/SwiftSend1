import { useState } from 'react';

const Profile = () => {
  const [user] = useState({
    name: 'Dave',
    email: 'dave@swiftsend.com',
    phone: '+254 712 345 678',
    country: 'Kenya',
  });

  return (
    <div className="min-h-screen bg-[#F8F9FA] p-6">
      <h2 className="text-3xl font-bold text-[#2C3E50] mb-6">My Profile</h2>

      <div className="bg-white rounded-xl shadow-md p-6 max-w-xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-[#2C3E50] text-white flex items-center justify-center text-xl font-semibold">
            {user.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div>
            <h3 className="text-xl font-semibold text-[#2C3E50]">{user.name}</h3>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-500">Phone Number</label>
            <div className="mt-1 border rounded-lg px-4 py-2 bg-gray-50 text-gray-800">{user.phone}</div>
          </div>

          <div>
            <label className="text-sm text-gray-500">Country</label>
            <div className="mt-1 border rounded-lg px-4 py-2 bg-gray-50 text-gray-800">{user.country}</div>
          </div>

          <div className="pt-4">
            <button className="bg-[#2C3E50] text-white px-6 py-2 rounded-lg hover:bg-[#1f2c3e]">
              Edit Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
