import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import PublicOnlyRoute from './components/PublicOnlyRoute';

import Home from './pages/Home';
import ReceiveMoney from './pages/ReceiveMoney';
import ExchangeRates from './pages/ExchangeRates';
import Dashboard from './pages/Dashboard';
import Help from './pages/Help';
import Verify from './pages/Verify';
import SendMoney from './pages/SendMoney';
import Wallet from './pages/Wallet';
import History from './pages/History';
import Track from './pages/Track';
import Profile from './pages/Profile';
import Withdraw from './pages/Withdraw';
import Login from './pages/Login';
import Register from './pages/Register';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="receive" element={<ReceiveMoney />} />
        <Route path="rates" element={<ExchangeRates />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="help" element={<Help />} />
        <Route path="verify" element={<Verify />} />

        <Route element={<ProtectedRoute />}>
          <Route path="send" element={<SendMoney />} />
          <Route path="wallet" element={<Wallet />} />
          <Route path="history" element={<History />} />
          <Route path="track" element={<Track />} />
          <Route path="profile" element={<Profile />} />
          <Route path="withdraw" element={<Withdraw />} />
        </Route>

        <Route element={<PublicOnlyRoute />}>
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
