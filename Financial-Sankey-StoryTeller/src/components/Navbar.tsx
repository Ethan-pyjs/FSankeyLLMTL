import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react'; // Import icons from lucide-react

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const NavLink = ({ to, children }: { to: string; children: React.ReactNode }) => (
    <Link
      to={to}
      onClick={() => setIsOpen(false)}
      className={`px-4 py-2 rounded-md text-sm font-medium w-full ${
        location.pathname === to
          ? 'bg-purple-700 text-white'
          : 'text-gray-300 hover:bg-purple-600 hover:text-white'
      } transition-colors duration-200`}
    >
      {children}
    </Link>
  );

  return (
    <nav className="bg-gray-900 bg-opacity-40 border-b border-purple-500 border-opacity-20 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <span className="text-purple-300 font-bold text-xl">Financial Storyteller</span>
          </div>

          {/* Menu Button */}
          <button
            onClick={toggleMenu}
            className="p-2 rounded-md text-purple-300 hover:text-white hover:bg-purple-600 transition-colors duration-200"
            aria-label="Toggle menu"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Dropdown Menu */}
      <div
        className={`absolute right-0 mt-0 w-48 rounded-b-lg bg-gray-900 bg-opacity-95 border border-purple-500 border-opacity-20 shadow-lg transform transition-all duration-200 ease-in-out ${
          isOpen
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 -translate-y-2 pointer-events-none'
        }`}
        style={{ backdropFilter: 'blur(8px)' }}
      >
        <div className="p-2 space-y-1">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/about">About Me</NavLink>
          <NavLink to="/changelog">Changelog</NavLink>
        </div>
      </div>
    </nav>
  );
}