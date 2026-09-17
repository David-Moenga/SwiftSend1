import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

const Layout = () => (
  <div className="min-h-screen overflow-x-hidden bg-[#f7f9fc] text-slate-900">
    <Navbar />
    <main><Outlet /></main>
    <Footer />
  </div>
);

export default Layout;
