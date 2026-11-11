import React from 'react';
import { HashRouter as Router, Route, Routes, useLocation, Outlet } from 'react-router-dom';
import HomePage from './HomePage';
import Header from './Header';
import AboutPage from './AboutPage';
import PredictionsPage from './PredictionsPage';
import ToolPage from './ToolPage'; // Import your new ToolPage component
import OurModelPage from './OurModelPage';

// A component to conditionally render Header
const Layout = () => {
  const location = useLocation();

  // Only render Header if the current route is not the HomePage
  return (
    <>
      {/* Conditionally render Header based on route */}
      {location.pathname !== '/' && <Header />}

      {/* Render child routes inside the Layout */}
      <Outlet />
    </>
  );
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* HomePage does not have the Header */}
          <Route path="/" element={<HomePage />} />

          {/* Wrap all other routes with Layout (which includes Header) */}
          <Route element={<Layout />}>
            <Route path="/about" element={<AboutPage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/tool" element={<ToolPage />} />
            <Route path="/model" element={<OurModelPage />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;

//import React, { useEffect } from 'react';
//import { HashRouter as Router, Route, Routes, useLocation, Outlet } from 'react-router-dom';
//import HomePage from './HomePage';
//import Header from './Header';
//import AboutPage from './AboutPage';
//import PredictionsPage from './PredictionsPage';
//import ToolPage from './ToolPage';
//
//// Component to render Header conditionally
//const Layout = () => {
//  const location = useLocation();
//
//  return (
//    <>
//      {/* Render Header conditionally */}
//      {location.pathname !== '/' && <Header />}
//
//      {/* Render children routes */}
//      <Outlet />
//    </>
//  );
//};
//
//function App() {
//  useEffect(() => {
//    console.log("App component mounted");
//  }, []);
//  return (
//    <Router basename="/PlantWise">
//      <div className="App">
//        <Routes>
//          <Route path="/" element={<HomePage />} />
//          <Route element={<Layout />}>
//            <Route path="/about" element={<AboutPage />} />
//            <Route path="/predictions" element={<PredictionsPage />} />
//            <Route path="/tool" element={<ToolPage />} />
//          </Route>
//        </Routes>
//      </div>
//    </Router>
//  );
//}
//
//export default App;

//import { HashRouter as Router, Route, Routes } from 'react-router-dom';
//import React, { useEffect } from 'react';
//import HomePage from './HomePage';
//import Header from './Header';
//import AboutPage from './AboutPage';
//import PredictionsPage from './PredictionsPage';
//import ToolPage from './ToolPage';
//
//function App() {
//  return (
//    <Router>
//      <div className="App">
//        <Routes>
//          <Route path="/" element={<HomePage />} />
//        </Routes>
//      </div>
//    </Router>
//  );
//}
//
//export default App;











