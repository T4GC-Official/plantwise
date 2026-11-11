import React, { useState, useRef, useEffect, useCallback } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import MapComponent from './MapComponent';
import './ToolPage.css';
import { Button, Popover, PopoverHeader, PopoverBody, Modal, ModalHeader, ModalBody, ModalFooter, Spinner } from 'reactstrap';

// Backend base URL. Local: REACT_APP_API_URL=http://localhost:8080 npm start
const API_BASE = ''; // Requests always use this site's active release.

// Add this hook to your component
const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

const ToolPage = () => {
  const requestRef = useRef(null);
  const imageRequestRef = useRef(null);
  const [error, setError] = useState('');
  const [health, setHealth] = useState(null);
  useEffect(() => { fetch('/api/health').then(r => r.json()).then(setHealth).catch(() => setError('Service unavailable')); return () => { requestRef.current?.abort(); imageRequestRef.current?.abort(); }; }, []);
  const [threshold, setThreshold] = useState(50); // Threshold for probability
  const [latitude, setLatitude] = useState(null); // Latitude from the map click
  const [longitude, setLongitude] = useState(null); // Longitude from the map click
  const [results, setResults] = useState([]); // Store the results (species, probabilities, AUC)
  const [popoverOpen, setPopoverOpen] = useState(false); // State for Popover toggle
  const [selectedSpecies, setSelectedSpecies] = useState(null); // Selected species name
  const [speciesImage, setSpeciesImage] = useState(null); // Species map image
  const [loadingImage, setLoadingImage] = useState(false); // Loading state for map image
  const [loading, setLoading] = useState(false); // Spinner for "Enter" button
  const [hasSearched, setHasSearched] = useState(false); // Track if "Enter" is clicked
  const resultsSectionRef = useRef(null); // Reference to the results section
  const { width } = useWindowSize();
  const popoverRef = useRef(null);

  // Function to scroll to the results section
  const scrollToResults = useCallback(() => {
    if(window.innerWidth < 768){
      console.log('Scrolling to results section...');
      if (resultsSectionRef.current) {
          resultsSectionRef.current.scrollIntoView({ behavior: 'smooth' });
      } else {
          console.error('resultsSectionRef is null or undefined');
      }
    }

  }, []);



  // Handle changes in the threshold slider
  const handleThresholdChange = (event) => {
    setThreshold(event.target.value);
  };

  // Handle "Enter" button click to fetch results
  const handleEnterClick = () => {
    if (latitude !== '' && longitude !== '' && latitude !== null && longitude !== null && Number.isFinite(Number(latitude)) && Number.isFinite(Number(longitude))) {
      setLoading(true); // Show spinner
      setHasSearched(false);
      fetchResults(latitude, longitude, threshold);
    } else {
      alert('Please provide valid coordinates (either by clicking on the map or entering them manually).');
    }
  };

  // Function to fetch results from backend
  const fetchResults = (lat, lng, minProbability) => {
    requestRef.current?.abort();
    const controller = new AbortController(); requestRef.current = controller;
    setError(''); setResults([]);
    fetch(`${API_BASE}/api/get-results`, {
      signal: controller.signal,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude: Number(lat),
        longitude: Number(lng),
        minProbability: Number(minProbability),
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          const body = await response.json(); throw new Error(typeof body.detail === 'string' ? body.detail : 'Invalid coordinates or threshold');
        }
        return response.json();
      })
      .then((data) => {
        console.log('Received data:', data);
        if (Array.isArray(data)) {
          setResults(data);
        } else {
          console.error('Unexpected data format:', data);
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') setError(error.message);
      })
      .finally(() => {
        if (controller.signal.aborted) return;
        setLoading(false); // Hide spinner once fetch is complete
        setHasSearched(true); // Mark search as initiated
      });
  };

  // Function to update latitude and longitude from map click
  const handleMapClick = useCallback((lat, lng) => {
    setLatitude(lat);
    setLongitude(lng);
    scrollToResults();
  }, [scrollToResults]);

  // Function to toggle the Popover
  const togglePopover = () => {
    setPopoverOpen(!popoverOpen);
  };

  // Function to generate POWO URL for a species
  const getPowoUrl = (speciesName) => {
    const powoBaseUrl = 'https://powo.science.kew.org/results?q=';
    return `${powoBaseUrl}${speciesName.replace(/_/g, '%20')}`;
  };

  // Function to handle species click and fetch map image
  const handleSpeciesClick = async (speciesName) => {
    imageRequestRef.current?.abort();
    const imageController = new AbortController(); imageRequestRef.current = imageController;
    setSpeciesImage(null);
    setSelectedSpecies(speciesName);
    setLoadingImage(true);
    try {
      const response = await fetch(`${API_BASE}/api/species/${encodeURIComponent(speciesName)}/map`, {signal: imageController.signal});
      if (!response.ok) throw new Error('Failed to load map');
      const imageBlob = await response.blob();
      if (!imageController.signal.aborted) setSpeciesImage(URL.createObjectURL(imageBlob));
    } catch (error) {
      console.error('Error loading species map:', error);
      setSpeciesImage(null);
    } finally {
      setLoadingImage(false);
    }
  };

  // Debugging: Check map container dimensions
  useEffect(() => {
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) {
      console.log('Map Container Height:', mapContainer.offsetHeight);
    }
  }, []);

  // Close popover when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popoverOpen && popoverRef.current &&
          !popoverRef.current.contains(event.target)) {
        setPopoverOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [popoverOpen]);

  useEffect(() => () => { if (speciesImage) URL.revokeObjectURL(speciesImage); }, [speciesImage]);

  // Function to close the modal
  const closeModal = () => {
    imageRequestRef.current?.abort();
    setSelectedSpecies(null);
    setSpeciesImage(null);
  };

  const exportToCSV = (data, latitude, longitude) => {
    // Format coordinates for filename (6 decimal places)
    const lat = Number(latitude).toFixed(4);
    const lng = Number(longitude).toFixed(4);

    // Create CSV content
    const csvContent =
      "Species,Suitability (%)\n" +
      data.map(row =>
        `"${row.species.replace(/"/g, '""')}",${row.probability}`
      ).join("\n");

    // Create a Blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.setAttribute("href", url);
    link.setAttribute("download", `plantwise-results_${lat}_${lng}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };


  return (
    <div className="tool-page container-fluid">
      <div className="row">
        {/* Map Section */}
        <div className="col-md-6">
          <div className="map-container">
            <MapComponent onMapClick={handleMapClick} />
          </div>
        </div>

        {/* Tool Explanation and Controls */}
        <div className="col-md-6 d-flex flex-column justify-content-center align-items-center">
          <h3>Tool Instructions</h3>
          <div className="mb-3" ref={popoverRef}>
            <Button id="Popover1" onClick={togglePopover} color="info">
              How to Use the Tool
            </Button>
            <Popover placement="right" isOpen={popoverOpen} target="Popover1" toggle={togglePopover}>
              <PopoverHeader>How to Use the Tool</PopoverHeader>
              <PopoverBody>
                <ul>
                  <li><strong>Enter Coordinates:</strong> Input the latitude and longitude of your site, or select the "Current Location" option to automatically detect your position, or click on the map to select the location.</li>
                  <li><strong>Set Threshold:</strong> Use the slider to adjust the minimum model suitability for evergreen plant species based on your site's bioclimatic conditions. Keep in mind that species with a low model suitability may not be suitable for planting at your site.</li>
                  <li><strong>Discover Species:</strong> Click "Enter" to generate a list of recommended native species that are well-suited to your location.</li>
                  <li><strong>No Results?:</strong> If no results are found, try selecting a nearby location or lowering the threshold to expand your options.</li>
                </ul>
                <div className="text-end mt-3">
                  <button
                    className="btn btn-sm btn-secondary"
                  >
                    Close
                  </button>
                </div>
              </PopoverBody>
            </Popover>
          </div>

          <p>{health ? `Release: ${health.release} · ${health.species_count} species` : 'Loading release…'}</p><p>ENMeval Java Maxent · four spatial blocks · effort-weighted background · cloglog suitability.</p><p>Suitability is a model score, not planting success probability.</p>{error && <div role="alert" className="alert alert-danger">{error}</div>}
          {/* Coordinates Input */}
          <div ref={resultsSectionRef} className="mt-4">
            <h5>Coordinates:</h5>
            <div className="d-flex">
              <div className="me-2">
                <label htmlFor="latitude" className="form-label">Latitude:</label>
                <input
                  type="number"
                  id="latitude"
                  className="form-control"
                  value={latitude ?? ''}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="Enter latitude"
                />
              </div>
              <div>
                <label htmlFor="longitude" className="form-label">Longitude:</label>
                <input
                  type="number"
                  id="longitude"
                  className="form-control"
                  value={longitude ?? ''}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="Enter longitude"
                />
              </div>
            </div>
          </div>

          {/* Button to use current location */}
          <button
            className="btn btn-secondary mt-2"
            onClick={() =>
              navigator.geolocation.getCurrentPosition((pos) => {
                setLatitude(pos.coords.latitude);
                setLongitude(pos.coords.longitude);
              })
            }
          >
            Use Current Location
          </button>

          {/* Threshold Slider */}
          <div className="mb-4">
            <input
              type="range"
              min="0"
              max="100"
              value={threshold}
              onChange={handleThresholdChange}
              className="form-range"
            />
            <div>Suitability: {threshold}</div>
          </div>

          <button className="btn btn-primary" onClick={handleEnterClick} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Enter'}
          </button>

          {/* Display Results */}

          {hasSearched && results.length === 0 && threshold === 0 && (
            <div className="mt-4 text-center">
              <p>No results found for this location.</p>
            </div>
          )}

          {hasSearched && results.length === 0 && (
            <div className="mt-4 text-center">
              <p>No results found. Please lower the threshold.</p>
            </div>
          )}

          {results.length > 0 && (
          <div className="mt-4">
            <h5>Results (Species above {threshold}% suitability):</h5>

            <button
              className="btn btn-success mb-3"
              onClick={() => exportToCSV(results, latitude, longitude)}
            >
              <i className="fas fa-download me-2"></i>
              Download CSV
            </button>

            {/* Results Table */}
            <div className="table-responsive">
              <table className="table table-bordered">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Species Name</th>
                    <th>Suitability (%)</th><th>Block-CV AUC</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>
                        <Button
                          color="link"
                          className="p-0"
                          onClick={() => handleSpeciesClick(result.species)}
                        >
                          <strong>{result.species}</strong>
                        </Button>
                      </td>
                      <td>{result.probability.toFixed(2)}%</td><td>{result.auc == null ? 'Unavailable' : result.auc.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Disclaimer Section */}
            <div className="alert alert-warning mt-3 d-flex align-items-center" role="alert">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                className="bi bi-exclamation-triangle me-2"
                viewBox="0 0 16 16"
              >
                <path d="M7.938 2.016a.13.13 0 0 1 .125 0l6.857 11.708c.03.051.03.112 0 .164a.145.145 0 0 1-.125.059H1.205a.145.145 0 0 1-.125-.059.148.148 0 0 1 0-.164L7.937 2.016Zm.532-.303A1.145 1.145 0 0 0 8 1.123c-.397 0-.761.2-.962.59L.18 13.416C-.143 13.966.318 14.623 1.024 14.623h13.952c.706 0 1.167-.657.844-1.207L8.47 1.713Z" />
                <path d="M7.002 13a1 1 0 1 1 2 0 1 1 0 0 1-2 0Zm.93-7.481c.352 0 .644.285.644.636v3.043c0 .351-.292.636-.644.636-.352 0-.643-.285-.643-.636V6.155c0-.351.291-.636.643-.636Z" />
              </svg>
              <span>
                Predictions may not be fully accurate. Please consult an expert before implementation.
              </span>
            </div>
          </div>
        )}

        {/* Logos Section */}
        <footer className="d-flex justify-content-center align-items-center mt-4" style={{ paddingBottom: '20px' }}>
          <a href="https://www.ncf-india.org/" target="_blank" rel="noopener noreferrer" className="mb-2">
            <img src="/images/NCF_logo.jpeg" alt="Nature Conservation Foundation Logo" className="img-fluid" style={{ height: '100px' }} />
          </a>
          <a href="https://www.akanksharathore.in" target="_blank" rel="noopener noreferrer" className="mb-2">
            <img src="/images/DSC_logo.jpeg" alt="DSCover Lab Logo" className="img-fluid" style={{ height: '100px' }} />
          </a>
          <a href="https://www.instagram.com/thackeraywildlifefoundation/?hl=en" target="_blank" rel="noopener noreferrer">
            <img src="/images/TTW_logo.jpeg" alt="Thackeray Wildlife Foundation Logo" className="img-fluid" style={{ height: '100px' }} />
          </a>
        </footer>
        {/* Supported by section */}
        <div className="text-center mt-5">
          <p
            className="text-black mb-3"
            style={{
            fontWeight: '600',  // Matching font weight
            fontSize: '1.1rem',
            opacity: 0.9
          }}>
            In partnership with
          </p>
          <div className="d-flex justify-content-center">
            <a href="https://era-india.org" target="_blank" rel="noopener noreferrer">
              <img
                src="/images/ERA-Logo-Colour.png"
                alt="Partner Organization Logo"
                className="img-fluid"
                style={{
                  height: '80px',
                  filter: 'brightness(1.1)', // Slightly brightens the logo for better visibility on dark background
                  transition: 'transform 0.2s ease'
                }}
                onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
              />
            </a>
          </div>
        </div>
        </div>
      </div>

      {/* Species Detail Modal */}
      <Modal isOpen={!!selectedSpecies} toggle={closeModal} size="lg">
        <ModalHeader toggle={closeModal}>{selectedSpecies || 'Species Details'}</ModalHeader>
        <ModalBody>
          {loadingImage ? (
            <div className="text-center">
              <Spinner color="primary" />
              <p>Loading species map...</p>
            </div>
          ) : speciesImage ? (
            <div className="d-flex justify-content-center align-items-center">
              <img
                src={speciesImage}
                alt={`${selectedSpecies} map`}
                className="img-fluid mb-3"
                style={{ maxHeight: '60vh', objectFit: 'contain' }}
              />
              <div className="text-center">
                <Button
                  color="primary"
                  href={getPowoUrl(selectedSpecies)}
                  target="_blank"
                  rel="noopener"
                >
                  View {selectedSpecies} on POWO
                </Button>
              </div>
            </div>
          ) : (
            <p>No map available for this species</p>
          )}
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={closeModal}>
            Close
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
};

export default ToolPage;

