import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

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
      className={`block px-4 py-2 rounded-md text-sm font-medium ${
        location.pathname === to
          ? 'bg-purple-700 text-white'
          : 'text-gray-300 hover:bg-purple-600 hover:text-white'
      } transition-colors duration-200`}
    >
      {children}
    </Link>
  );

  return (
    <nav className="fixed top-0 right-0 z-50 p-4">
      <div className="relative">
        {/* Menu Button */}
        <button
          onClick={toggleMenu}
          className="p-2 rounded-md bg-gray-900 bg-opacity-80 text-purple-300 hover:text-white hover:bg-purple-600 transition-colors duration-200 border border-purple-500 border-opacity-20"
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute right-0 mt-2 w-48 rounded-lg bg-gray-900 bg-opacity-95 border border-purple-500 border-opacity-20 shadow-lg"
               style={{ backdropFilter: 'blur(8px)' }}>
            <div className="py-2">
              <NavLink to="/">Home </NavLink>
              <NavLink to="/about"> About Me </NavLink>
              <NavLink to="/changelog"> Changelog</NavLink>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}