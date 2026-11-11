//import React from 'react';
//import { useNavigate } from 'react-router-dom';
//import 'bootstrap/dist/css/bootstrap.min.css';
//import treesImage from './trees.jpeg';
//
//const HomePage = () => {
//  const navigate = useNavigate();
//
//  const handleEnterClick = () => {
//    navigate('/tool'); // Navigate to the tool page
//  };
//
//  return (
//    <div
//      className="homepage d-flex flex-column justify-content-center align-items-center"
//      style={{
//        minHeight: '100vh',
//        backgroundImage: `url(${treesImage})`,
//        backgroundSize: 'cover',
//        backgroundPosition: 'center',
//        position: 'relative',
//        overflow: 'hidden',
//      }}
//    >
//      {/* Dark overlay applied only over the background image */}
//      <div
//        style={{
//          position: 'absolute',
//          top: 0,
//          left: 0,
//          right: 0,
//          bottom: 0,
//          backgroundColor: 'rgba(0, 0, 0, 0.2)', // Dark overlay with 40% opacity
//          zIndex: 0, // Ensure it's behind the content
//        }}
//      ></div>
//
//      {/* Content container */}
//      <div className="text-center text-light position-relative z-index-1">
//        <h1 style={{ fontWeight: '600' }} className="display-4 mb-4">
//            Welcome to PlantWise
//           </h1>
//
//        <p style={{ fontWeight: '600' }} className="lead font-weight-bold mb-4">
//            Find the right native evergreen plant species for your restoration site!
//        </p>
//        <p style={{ fontWeight: '600' }} className="lead font-weight-bold mb-4">
//            Plantwise is the go-to tool for identifying native evergreen species suitable for planting at your restoration site in the Western Ghats Biodiversity Hotspot.
//        </p>
//        <button className="btn btn-primary btn-lg mt-4" onClick={handleEnterClick}>
//          Enter
//        </button>
//      </div>
//    </div>
//  );
//};
//
//export default HomePage;

//import React from 'react';
//import { useNavigate } from 'react-router-dom';
//import 'bootstrap/dist/css/bootstrap.min.css';
//import treesImage from './divya_image.jpg'; // Use the provided image
//
//const HomePage = () => {
//  const navigate = useNavigate();
//
//  const handleEnterClick = () => {
//    navigate('/tool'); // Navigate to the tool page
//  };
//
//  return (
//    <div>
//      {/* Fullscreen welcome section */}
//      <div
//        className="d-flex flex-column justify-content-center align-items-center text-light"
//        style={{
//          minHeight: '100vh',
//          backgroundImage: `url(${treesImage})`, // Set the background image
//          backgroundSize: 'cover',
//          backgroundPosition: 'center',
//          position: 'relative',
//          overflow: 'hidden',
//        }}
//      >
//
//        {/* Dark overlay */}
//        <div
//          style={{
//            position: 'absolute',
//            top: 0,
//            left: 0,
//            right: 0,
//            bottom: 0,
//            backgroundColor: 'rgba(0, 0, 0, 0.5)', // Darken the image
//            zIndex: 0,
//          }}
//        ></div>
//
//        {/* Content on top of the image */}
//        <div className="text-center position-relative z-index-1">
//          <h1 style={{ fontWeight: '600' }} className="display-4 mb-4">
//            Welcome to PlantWise
//          </h1>
//          <p style={{ fontWeight: '600' }} className="lead mb-4">
//            Find the right native evergreen plant species for your restoration site!
//          </p>
//          <p style={{ fontWeight: '600' }} className="lead mb-4">
//            Plantwise is the go-to tool for identifying native evergreen species suitable for planting at your restoration site in the Western Ghats Biodiversity Hotspot.
//          </p>
//          <button className="btn btn-primary btn-lg mt-4" onClick={handleEnterClick}>
//            Enter
//          </button>
//        </div>
//      </div>
//
//      {/* Section: Why plant native trees */}
//      <div className="container py-5">
//        <h2 className="text-center mb-4">Why plant native trees?</h2>
//        <p>
//          Planting native trees that are adapted to local environmental conditions is critical for restoring degraded ecosystems. These trees provide nesting and roosting habitats, food resources for local biodiversity, and play an essential role in maintaining soil integrity, conserving water, and mitigating climate change.
//        </p>
//        <p>
//          Many species of non-native plants, introduced over centuries from different parts of the world, have caused tremendous damage to our ecosystems. Examples include Lantana camara, Senna spectabilis, and Chromolaena odorata. These invasive species outcompete native plants, disrupt ecosystems, and reduce biodiversity.
//Given the extensive negative impact of human activities on native plants over centuries, it is imperative to prioritize planting native trees that historically thrived in the area. By doing so, we can help in partially restoring the native biodiversitysupport ecological restoration, enhance biodiversity, and foster resilience in our natural systems.
//        </p>
//      </div>
//
//      {/* Section: Why plant evergreen trees */}
//      <div className="container py-5 bg-light">
//        <h2 className="text-center mb-4">Why plant evergreen trees?</h2>
//        <p>
//          The Western Ghats is one of the world’s most important biodiversity hotspots, receiving high rainfall and supporting an exceptional diversity of evergreen plant species. Due to its long-term isolation from other tropical wet forest regions, more than 60% of the evergreen plant species found here are endemic, meaning they occur nowhere else in the world.
//However, over centuries, extensive deforestation driven by monoculture plantations, agriculture, and infrastructure development has led to the loss and fragmentation of large swathes of these forests. This has severely impacted native tree species, leaving many rare and endangered, such as: Dipterocarpus bourdilloni (a large, emergent rainforest tree), Myristica malabarica (a key food plant of birds like hornbills and also a key non-timber forest produce collected by local communities).
//        </p>
//        <p>
//          Our goal is to aid restoration practitioners in selecting the right evergreen tree species for restoration. Planting appropriate evergreen trees will facilitate recovery of wet evergreen tree species in the region, contribute to plant conservation and provide food resources to threatened wildlife in the region.
//        </p>
//      </div>
//    </div>
//  );
//};
//
//export default HomePage;

import React, { useRef } from 'react'; // Import useRef
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import treesImage from './images/divya_image.jpeg'; // Use the provided image

const HomePage = () => {
  const navigate = useNavigate();

  // Reference for the "Learn More" scrolling target
  const learnMoreSectionRef = useRef(null);

  // Function to handle "Learn More" button scrolling
  const handleLearnMoreClick = () => {
    learnMoreSectionRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  const handleEnterClick = () => {
    navigate('/tool'); // Navigate to the tool page
  };

  return (
    <div>
      {/* Fullscreen welcome section */}
      <div
        className="d-flex flex-column justify-content-center align-items-center text-light"
        style={{
          minHeight: '100vh',
          backgroundImage: `url(${treesImage})`, // Set the background image
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Dark overlay */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)', // Darken the image
            zIndex: 0,
          }}
        ></div>

        {/* Content on top of the image */}
        <div className="text-center position-relative z-index-1">
          <h1 style={{ fontWeight: '600' }} className="display-4 mb-4">
            Welcome to PlantWise
          </h1>
          <p style={{ fontWeight: '600' }} className="lead mb-4">
            The go-to tool for identifying native species suitable at your restoration site in the Western Ghats.
          </p>
          <button className="btn btn-primary btn-lg mt-4" onClick={handleEnterClick}>
            Enter
          </button>
          <button
            className="btn btn-outline-light btn-lg mt-4 ms-3"
            onClick={handleLearnMoreClick} // Trigger smooth scrolling
            style={{
              border: '2px solid white',
              color: 'white',
              borderRadius: '5px',
            }}
          >
            Learn More
          </button>
        </div>

      </div>

      {/* Section: Why plant native trees */}
      <div className="container py-5" ref={learnMoreSectionRef}> {/* Assign the scrolling ref */}
        <h2 className="text-center mb-4">Why plant native trees?</h2>
        <p>
          Planting native trees that are adapted to local environmental conditions is critical for restoring degraded ecosystems. These trees provide nesting and roosting habitats, food resources for local biodiversity, and play an essential role in maintaining soil integrity, conserving water, and mitigating climate change.
        </p>
        <p>
          Many species of non-native plants, introduced over centuries from different parts of the world, have caused tremendous damage to our ecosystems. Examples include Lantana camara, Senna spectabilis, and Chromolaena odorata. These invasive species outcompete native plants, disrupt ecosystems, and reduce biodiversity.
          Given the extensive negative impact of human activities on native plants over centuries, it is imperative to prioritize planting native trees that historically thrived in the area. By doing so, we can help in partially restoring the native biodiversity, support ecological restoration, enhance biodiversity, and foster resilience in our natural systems.
        </p>
        <h2 className="text-center mb-4">Why restoration in Western Ghats? </h2>
        <p>
          The Western Ghats is one of the world’s most important biodiversity hotspots, receiving high rainfall and supporting an exceptional diversity of evergreen plant species. Due to its long-term isolation from other tropical wet forest regions, more than 60% of the evergreen plant species found here are endemic, meaning they occur nowhere else in the world.
        </p>
        <p>
          However, over centuries, extensive deforestation driven by monoculture plantations, agriculture, and infrastructure development has led to the loss and fragmentation of large swathes of these forests. This has severely impacted native tree species, leaving many rare and endangered, such as Dipterocarpus bourdilloni (a large, emergent rainforest tree), Myristica malabarica (a key food plant of birds like hornbills and also a key non-timber forest produce collected by local communities).
        </p>
        <p>
          Our goal is to aid restoration practitioners in selecting the right tree species for restoration. Planting appropriate tree species will facilitate the recovery of forests in the region, contribute to plant conservation and provide food resources to threatened wildlife in the area. This tool has been developed by using location information of 368 evergreen tree species. We hope to add more species as more information becomes available.
        </p>
      </div>
    </div>
  );
};

export default HomePage;

