import React from "react";

const OurModelPage = () => {
  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Our Model</h1>

      {/* Section: Introduction */}
      <p>
        PlantWise employs advanced ecological niche modeling techniques to predict the suitability of native plant species for ecological restoration projects in the Western Ghats Biodiversity Hotspot. Our predictive tools are designed to assist restoration practitioners in selecting the most appropriate species to plant in degraded areas, ensuring ecological balance and maximizing restoration success.
      </p>

      {/* Section: Broad Methodology */}
      <h2 className="mt-4">How It Works</h2>
      <p>
        Our model is built using the <strong>MaxEnt</strong> algorithm, a popular tool for species distribution modeling<sup>[1]</sup>. MaxEnt works by analyzing presence-only data of species along with environmental variables such as rainfall, temperature, and soil type to predict the likelihood of a species thriving in a given location.
      </p>

      {/* Section: Data Sources */}
      <h2 className="mt-4">Data Sources</h2>
      <p>
        The plant species occurrence data used for training the species distribution models (SDMs) was contributed by the following teams:
      </p>
      <ul>
        <li>
          <strong>Northern Western Ghats:</strong> Nayantara Biswas, Vishal Sadekar, Siddharth Biniwale, Yukti Taneja, Navendu Page, and Rohit Naniwadekar<sup>[2]</sup>
        </li>
        <li>
          <strong>Across the Western Ghats:</strong> Navendu Page et al.<sup>[3]</sup>
        </li>
        <li>
          <strong>Additional Contributions:</strong> R. Krishnamani and Ajith Kumar<sup>[4]</sup>
        </li>
        <li><strong>French Institute of Pondicherry</strong></li>
      </ul>
      <p>
        We used
        <a href="/species_presence.csv" download>
          <strong> 14,067 locations</strong> of <strong>368 species </strong>
        </a>
        to train the SDMs. Further details on the modeling approach will be available in our upcoming publication
        (<em>Suri et al., in preparation</em>).
      </p>

      {/* Section: Disclaimer */}
      <h2 className="mt-4">Disclaimer</h2>
      <p>
        Species distribution models may overpredict or underpredict species distributions, leading to commission or omission errors.<sup>[5]</sup> While we have taken care to minimize these errors, we strongly recommend that restoration practitioners consult an experienced plant ecologist to vet the suggested species list before restoration. For additional information on the shortlisted species, you may contact <strong>Dr. Navendu Page</strong>.
      </p>

      <h2 className="mt-4">References</h2>
      <ol>
        <li>
          Steven J. Phillips, Miroslav Dudík, Robert E. Schapire. [Internet] Maxent software for modeling species niches and distributions (Version 3.4.1). Available from: <a href="http://biodiversityinformatics.amnh.org/open_source/maxent/" target="_blank" rel="noopener noreferrer">http://biodiversityinformatics.amnh.org/open_source/maxent/</a>. Accessed on 2025-4-7.
        </li>
        <li>
          Biswas, N., Sadekar, V., Biniwale, S., Taneja, Y., Osuri, A. M., Page, N., ... & Naniwadekar, R. (2024). Chronic disturbance of moist tropical forests favours deciduous over evergreen tree communities across a climate gradient in the Western Ghats. bioRxiv, 2024-01.
        </li>
        <li>
          Page, N. V., & Shanker, K. (2020). Climatic stability drives latitudinal trends in range size and richness of woody plants in the Western Ghats, India. PLoS One, 15(7), e0235733.
        </li>
        <li>
          Gopal, A., Bharti, D. K., Page, N., Dexter, K. G., Krishnamani, R., Kumar, A., & Joshi, J. (2023). Range restricted old and young lineages show the southern Western Ghats to be both a museum and a cradle of diversity for woody plants. Proceedings of the Royal Society B, 290(1997), 20222513.
        </li>
        <li>
          Sandel, B., Merow, C., Serra‐Diaz, J. M., & Svenning, J. C. (2025). Disequilibrium in plant distributions: Challenges and approaches for species distribution models. Journal of Ecology.
        </li>
      </ol>
    </div>
  );
};

export default OurModelPage;
