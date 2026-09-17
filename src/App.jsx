import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';

import Home from './pages/Home';
import SendMoney from './pages/SendMoney';
import ReceiveMoney from './pages/ReceiveMoney';
import ExchangeRates from './pages/ExchangeRates';
import Dashboard from './pages/Dashboard';
import Wallet from './pages/Wallet';
import History from './pages/History';
import Track from './pages/Track';
import Profile from './pages/Profile';
import Withdraw from './pages/Withdraw';
import Help from './pages/Help';
import Login from './pages/Login';
import Register from './pages/Register';
import Verify from './pages/Verify';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="send" element={<SendMoney />} />
        <Route path="receive" element={<ReceiveMoney />} />
        <Route path="rates" element={<ExchangeRates />} />
        <Route path="track" element={<Track />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="wallet" element={<Wallet />} />
        <Route path="history" element={<History />} />
        <Route path="profile" element={<Profile />} />
        <Route path="withdraw" element={<Withdraw />} />
        <Route path="help" element={<Help />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="verify" element={<Verify />} />
      </Route>
    </Routes>
  );
}

export default App;
