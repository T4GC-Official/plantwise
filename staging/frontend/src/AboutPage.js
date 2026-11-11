//import React from 'react';
//
//const AboutPage = () => {
//  return (
//    <div className="container mt-5">
//      <div className="row">
//        {/* About Us Header */}
//        <div className="col-12 text-center mb-4">
//          <h1>About Us</h1>
//          <p className="lead">
//            Learn more about the Habitability Tool and the team behind it.
//          </p>
//        </div>
//
//        {/* Section 1: Introduction */}
//        <div className="col-md-6 mb-4">
//          <div className="card shadow-sm">
//            <div className="card-body">
//              <h4 className="card-title">Our Mission</h4>
//              <p className="card-text">
//                The Habitability Tool is designed to provide accurate, real-time predictions on the habitability of various locations. By analyzing environmental factors, this tool helps users understand how different locations may be suitable for habitation, helping researchers, scientists, and decision-makers make informed decisions.
//              </p>
//            </div>
//          </div>
//        </div>
//
//        {/* Section 2: Our Team */}
//        <div className="col-md-6 mb-4">
//          <div className="card shadow-sm">
//            <div className="card-body">
//              <h4 className="card-title">Our Team</h4>
//              <p className="card-text">
//                The development of the Habitability Tool is a collaborative effort between passionate students, scientists, and experts. We are committed to harnessing the power of technology and data to bring valuable insights to environmental research.
//              </p>
//              <h5>The Developer</h5>
//              <p>
//                <strong>Viswesh Suri</strong> - Student at BITS Hyderabad
//              </p>
//              <h5>Our Mentor</h5>
//              <p>
//                <strong>Akanksha Rathore</strong> - Mentor, BITS Hyderabad.
//              </p>
//              <h5>Our Collaborators</h5>
//              <p>
//                <strong>Rohit Naniwadekar</strong> - Scientist at ERA (Environmental Research Associates).
//              </p>
//              <p>
//                <strong>Sharwani Deshpande</strong> - Scientist at ERA (Environmental Research Associates).
//              </p>
//            </div>
//          </div>
//        </div>
//
//          <h2>Data Sources</h2>
//          <p>The plant species occurrence data used for training the species distribution models (SDMs) was contributed by the following teams:</p>
//          <ul>
//            <li>Northern Western Ghats: Nayantara Biswas, Vishal Sadekar, Siddharth Biniwale, Yukti Taneja, Navendu Page, and Rohit Naniwadekar</li>
//            <li>Across the Western Ghats: Navendu Page et al.</li>
//            <li>Additional Contributions: R. Krishnamani and Ajith Kumar</li>
//            <li>French Institute of Pondicherry</li>
//          </ul>
//          <p>We used 15,335 locations of 515 species to train the SDMs. Further details on the modeling approach will be available in our upcoming publication (Suri et al., in preparation).</p>
//
//          <h2>Disclaimer</h2>
//          <p>Species distribution models may overpredict or underpredict species distributions, leading to commission or omission errors. While we have taken care to minimize these errors, we strongly recommend that restoration practitioners consult an experienced plant ecologist to vet the suggested species list before restoration. For additional information on the shortlisted species, you may contact Dr. Navendu Page.</p>
//
//
//        {/* Section 3: Contact Information */}
//        <div className="col-12 mt-5">
//          <h3 className="text-center mb-3">Contact Us</h3>
//          <div className="text-center">
//            <p>
//              Have any questions or suggestions? Feel free to reach out to us:
//            </p>
//            <p>
//              <strong>Email:</strong> <a href="mailto:visweshsuri@gmail.com">visweshsuri@gmail.com</a>
//            </p>
//          </div>
//        </div>
//      </div>
//    </div>
//  );
//};
//
//export default AboutPage;


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
