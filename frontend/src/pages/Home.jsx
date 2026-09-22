import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full bg-gradient-to-br from-[#2C3E50] to-[#1ABC9C] text-white text-center py-20 px-4">
        <h1 className="text-5xl font-bold mb-4">Send Money Anywhere, Instantly</h1>
        <p className="text-lg mb-6 max-w-2xl mx-auto">SwiftSend is the fastest way to transfer money across borders using Stellar blockchain technology — secure, fast, and cost-effective.</p>
        <Link
          to="/send"
          className="bg-white text-[#2C3E50] px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition"
        >
          Get Started
        </Link>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 max-w-6xl w-full">
        <h2 className="text-3xl font-bold text-center mb-10 text-[#2C3E50]">Why Choose SwiftSend?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { title: "Cross-Border Transfers", desc: "Send money globally with minimal fees." },
            { title: "Stellar-Powered", desc: "Blockchain speed and transparency at your fingertips." },
            { title: "Multi-Currency Wallet", desc: "Manage and store multiple assets easily." },
            { title: "Track Transfers", desc: "Real-time status updates and notifications." },
            { title: "Low Fees", desc: "Save more with extremely low transaction costs." },
            { title: "Secure & Compliant", desc: "Your data and funds are always protected." },
          ].map(({ title, desc }) => (
            <div key={title} className="bg-white rounded-xl shadow p-6 hover:shadow-lg transition border">
              <h3 className="text-xl font-semibold text-[#2C3E50] mb-2">{title}</h3>
              <p className="text-gray-600">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 px-4 bg-[#F8F9FA] w-full">
        <h2 className="text-3xl font-bold text-center mb-12 text-[#2C3E50]">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8 text-center max-w-5xl mx-auto">
          {[
            { step: "1", title: "Send", desc: "Enter amount and recipient details." },
            { step: "2", title: "Confirm", desc: "Review details and approve the transfer." },
            { step: "3", title: "Receive", desc: "Recipient gets funds instantly." },
          ].map(({ step, title, desc }) => (
            <div key={step} className="p-6 bg-white rounded-xl shadow hover:shadow-md border transition">
              <div className="text-4xl font-bold text-[#1ABC9C] mb-2">{step}</div>
              <h4 className="text-xl font-semibold mb-2 text-[#2C3E50]">{title}</h4>
              <p className="text-gray-600">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-16 px-4 w-full bg-gradient-to-r from-[#1ABC9C] to-[#2C3E50] text-white text-center">
        <h2 className="text-3xl font-bold mb-4">Join SwiftSend Today</h2>
        <p className="text-lg mb-6">Sign up and start sending money faster than ever before.</p>
        <Link
          to="/register"
          className="bg-white text-[#2C3E50] px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition"
        >
          Create Account
        </Link>
      </section>
    </div>
  );
};

export default Home;
