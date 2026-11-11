import React from 'react';
import logo from './logo.png'; // Make sure this path is correct
import teamData from './teamData.js'

const AboutPage = () => {
  return (
    <div className="container mt-5">
      <h1 className="text-center mb-5">About Us</h1>

      <div className="row">
        {/* Main content */}
        <div className="col-lg-8">
          <h2>PlantWise Team</h2>
          <p>The PlantWise Habitat Tool has been developed by:</p>
          <ul>
            <li>Viswesh Suri</li>
            <li>Sharvani Deshpande</li>
            <li>Akanksha Rathore</li>
            <li>Navendu Page</li>
            <li>Rohit Naniwadekar</li>
          </ul>

          <h2>Suggested Citation</h2>
          <p>Suri, V., S. Deshpande, N. Page, A. Gopal, R. Krishnamani, A. Kumar,  A. Rathore and R. Naniwadekar. 2025. PlantWise: A tool for selecting native plant species for ecological restoration in the Western Ghats, India. Version 1.0. <a href="https://plantwise-india.org" target="_blank" rel="noopener noreferrer">https://plantwise-india.org</a>.</p>

          <h2>Funding & Acknowledgments</h2>
          <p>We sincerely thank the following for their generous support and guidance:</p>
          <ul>
            <li>Funding Support: Mr. Rajesh Nair, Dr. Manish Gupta, and Godrej Consumer Products Limited</li>
            <li>Technical Support: Dr. Bharti Dharapuram, Mr. Abhishek Gopal and Dr. Jahnavi Joshi for sharing their R scripts and Mr. Ravi Rathore for support to launch the website</li>
            <li>Scientific Feedback: Dr. Divya Mudappa, Dr. T. R. Shankar Raman, and Dr. Anand Osuri</li>
            <li>Akanksha Rathore and Viswesh Suri express their gratitude to BITS Pilani, Hyderabad for the administrative and funding support that made this work possible.</li>
          </ul>

          <h2>We Value Your Feedback!</h2>
          <p>We would love to hear from you. Please write to us at <a href="mailto:plantwise30@gmail.com">plantwise30@gmail.com</a> with any suggestions, feedback, or queries.</p>

          <div className="row align-items-center mt-4">
            {/* Image Section */}
            <div className="col-md-4">
              <img
                src="/images/Ajith_Kumar.jpg" // Replace with the actual image path
                alt="Dr. Ajith Kumar"
                className="img-fluid rounded"
              />
              <p className="mt-2 mb-0">© T. R. Shankar Raman</p>
            </div>

            {/* Dedication Text Section */}
            <div className="col-md-8">
              <p>
                We dedicate this tool to <strong>Dr. Ajith Kumar</strong>, a pioneering Indian wildlife biologist and educator, whose contributions to conservation science and mentorship have left an enduring legacy. Dr. Ajith Kumar was deeply passionate about the rainforests of the Western Ghats and ecological restoration. His generosity in sharing invaluable plant distribution data played a crucial role in developing the species distribution models that power this tool.
              </p>
            </div>
          </div>
        <p></p>
        <p><strong>Thank you for using PlantWise!</strong></p>
        </div>

        {/* Team members in the right corner */}
        <div className="col-lg-4">
          <h2 className="text-center mb-4">PlantWise Team</h2>
          {teamData.map((member, index) => (
            <div key={index} className="card mb-3">
              <img
                src={member.image} // Dynamically reference the image from teamData
                className="card-img-top"
                alt={`${member.name}'s photo`}
                style={{ height: '300px', objectFit: 'cover' }} // Keep existing styles
              />
              <div className="card-body">
                <h5 className="card-title">{member.name}</h5>
                <p className="card-text">
                  {member.description}{" "}
                  {member.link && (
                    <a
                      href={member.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary"
                    >
                      Learn more
                    </a>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
