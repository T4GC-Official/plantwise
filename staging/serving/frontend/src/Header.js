import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { NavbarToggler, Collapse } from 'reactstrap';
import logo from './logo.png';

const Header = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggle = () => setIsOpen(!isOpen);

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="container-fluid">
        {/* Logo and Brand Name */}
        <NavLink className="navbar-brand d-flex align-items-center" to="/" end>

          <img
            src={logo}
            alt="PlantWise Logo"
            style={{
              height: '40px',
              marginRight: '10px',
            }}
          />
          PlantWise
        </NavLink>

        {/* Mobile Toggle Button */}
        <NavbarToggler onClick={toggle} />

        {/* Navigation Links */}
        <Collapse isOpen={isOpen} navbar className="justify-content-end">
          <ul className="navbar-nav">
            <li className="nav-item">
              <NavLink
                end
                className="nav-link"
                to="/"
                style={({ isActive }) => ({
                  backgroundColor: isActive ? '#007bff' : 'transparent',
                  color: isActive ? '#fff' : '#000',
                  fontWeight: isActive ? 'bold' : 'normal',
                  borderRadius: '20px', // Rounded corners for softer appearance
                  padding: '5px 15px', // Less padding to minimize size
                  margin: '5px', // Add spacing between links
                  transition: 'background-color 0.3s ease',
                })}
              >
                Home
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                className="nav-link"
                to="/tool"
                style={({ isActive }) => ({
                  backgroundColor: isActive ? '#007bff' : 'transparent',
                  color: isActive ? '#fff' : '#000',
                  fontWeight: isActive ? 'bold' : 'normal',
                  borderRadius: '20px',
                  padding: '5px 15px',
                  margin: '5px',
                  transition: 'background-color 0.3s ease',
                })}
              >
                Tool
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                className="nav-link"
                to="/model"
                style={({ isActive }) => ({
                  backgroundColor: isActive ? '#007bff' : 'transparent',
                  color: isActive ? '#fff' : '#000',
                  fontWeight: isActive ? 'bold' : 'normal',
                  borderRadius: '20px',
                  padding: '5px 15px',
                  margin: '5px',
                  transition: 'background-color 0.3s ease',
                })}
              >
                Our Model
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                className="nav-link"
                to="/about"
                style={({ isActive }) => ({
                  backgroundColor: isActive ? '#007bff' : 'transparent',
                  color: isActive ? '#fff' : '#000',
                  fontWeight: isActive ? 'bold' : 'normal',
                  borderRadius: '20px',
                  padding: '5px 15px',
                  margin: '5px',
                  transition: 'background-color 0.3s ease',
                })}
              >
                About Us
              </NavLink>
            </li>
          </ul>
        </Collapse>
      </div>
    </nav>
  );
};

export default Header;
