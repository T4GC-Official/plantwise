//import React from 'react';
//import { Link } from 'react-router-dom';
//import logo from './logo.png'; // Make sure this path is correct
//
//const Header = () => {
//  return (
//    <nav className="navbar navbar-expand-lg navbar-light bg-light">
//      <div className="container-fluid">
//        {/* Logo and Brand Name */}
//        <Link className="navbar-brand d-flex align-items-center" to="/">
//          <img
//            src={logo}
//            alt="PlantWise Logo"
//            style={{
//              height: '40px', // Adjust the height of the logo
//              marginRight: '10px', // Add some spacing between the logo and the text
//            }}
//          />
//          PlantWise
//        </Link>
//        <button
//          className="navbar-toggler"
//          type="button"
//          data-bs-toggle="collapse"
//          data-bs-target="#navbarNav"
//          aria-controls="navbarNav"
//          aria-expanded="false"
//          aria-label="Toggle navigation"
//        >
//          <span className="navbar-toggler-icon"></span>
//        </button>
//        <div className="collapse navbar-collapse" id="navbarNav">
//          <ul className="navbar-nav ms-auto">
//            <li className="nav-item">
//              <Link className="nav-link" to="/">Home</Link>
//            </li>
//            <li className="nav-item">
//              <Link className="nav-link" to="/tool">Tool</Link>
//            </li>
//            <li className="nav-item">
//              <Link className="nav-link" to="/about">About Us</Link>
//            </li>
//          </ul>
//        </div>
//      </div>
//    </nav>
//  );
//};
//
//export default Header;

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
        <NavLink className="navbar-brand d-flex align-items-center" to="/" exact>

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
                exact
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
