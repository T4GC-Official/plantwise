# from flask import Flask, render_template, request
# import os
# import rasterio
#
# app = Flask(__name__)
#
#
# def get_probability_from_tif(tif_file, x, y):
#     with rasterio.open(tif_file) as src:
#         transform = src.transform
#         px, py = ~transform * (x, y)
#         band = src.read(1)
#         if 0 <= px < src.width and 0 <= py < src.height:
#             value = band[int(py), int(px)]
#         else:
#             value = None
#     return value
#
#
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         latitude = float(request.form['latitude'])
#         longitude = float(request.form['longitude'])
#         min_probability = float(request.form['min_probability'])
#
#         results = []
#         for filename in os.listdir('FinalProbabilityData'):
#             if filename.endswith('.tif'):
#                 tif_file = os.path.join('FinalProbabilityData', filename)
#                 prob = get_probability_from_tif(tif_file, longitude, latitude)
#                 if prob is not None and prob > min_probability:
#                     results.append((filename, prob))
#
#         # Sort results in descending order
#         results.sort(key=lambda x: x[1], reverse=True)
#
#         return render_template('results.html', results=results)
#
#     return render_template('index.html')
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import rasterio
import os

# app = Flask(__name__)
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/api/get-results', methods=['POST'])
# def get_results():
#     data = request.json
#     latitude = data.get('latitude')
#     longitude = data.get('longitude')
#     min_probability = data.get('minProbability')
#
#     results = []
#
#     # Folder where .tif files are saved
#     results_folder = 'FinalProbabilityData'
#
#     # Iterate over each .tif file
#     for filename in os.listdir(results_folder):
#         if filename.endswith('.tif'):
#             tif_file = os.path.join(results_folder, filename)
#             probability = get_probability_from_tif(tif_file, float(longitude), float(latitude))
#             if probability is not None and probability >= float(min_probability)/100:
#                 species = filename.replace('.tif', '')
#                 results.append({'species': species, 'probability': int(probability*100)})
#
#     # Sort results by probability in descending order
#     results.sort(key=lambda x: x['probability'], reverse=True)
#
#     return jsonify(results)
#
# def get_probability_from_tif(tif_file, x, y):
#     with rasterio.open(tif_file) as src:
#         transform = src.transform
#         px, py = ~transform * (x, y)
#         band = src.read(1)
#         if 0 <= px < src.width and 0 <= py < src.height:
#             return band[int(py), int(px)]
#         return None
#
# if __name__ == '__main__':
#     app.run(debug=True)

import os
import pandas as pd
import rasterio
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, supports_credentials=True)

# Load the AUC data from the CSV file into a DataFrame
auc_file = 'data/auc_and_contributions.csv'
auc_data = pd.read_csv(auc_file)

# Map species names to their AUC values for quick lookup
species_auc_map = dict(zip(auc_data['Species'], auc_data['Test AUC']))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-results', methods=['POST'])
def get_results():
    data = request.json
    print(data)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    min_probability = data.get('minProbability')

    if latitude is None or longitude is None or min_probability is None:
        return jsonify({'error': 'Missing required parameters'}), 400

    results = []

    # Folder where .tif files are saved
    results_folder = 'data/final_tif_files_withNWG'

    # Iterate over each .tif file
    for filename in os.listdir(results_folder):
        if filename.endswith('.tif'):
            tif_file = os.path.join(results_folder, filename)
            probability = get_probability_from_tif(tif_file, float(longitude), float(latitude))
            print(tif_file)
            print(probability)
            if probability is not None and probability >= float(min_probability) / 100:
                species = filename.replace('.tif', '')
                print(species)

                # Get the AUC for the species from the CSV data
                auc_value = species_auc_map.get(species, None)

                # If AUC is found, add it to the results
                if auc_value is not None:
                    results.append({
                        'species': species,
                        'probability': int(probability * 100),
                        'auc': auc_value
                    })

    # Sort results by probability in descending order
    results.sort(key=lambda x: x['probability'], reverse=True)

    print("Results being returned:", results)

    return jsonify(results)

def get_probability_from_tif(tif_file, x, y):
    with rasterio.open(tif_file) as src:
        transform = src.transform
        px, py = ~transform * (x, y)
        band = src.read(1)
        if 0 <= px < src.width and 0 <= py < src.height:
            return band[int(py), int(px)]
        return None

if __name__ == '__main__':
    app.run(debug=True)


