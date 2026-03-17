# import os
# import subprocess
# import pandas as pd
# import rasterio
# from rasterio.transform import from_origin
# import numpy as np
#
#
# def generate_file_paths(species_file):
#     # Extract the base name without the extension
#     base_name = os.path.splitext(species_file)[0]
#
#     # Create the paths for the .asc and .tif files
#     asc_file = f'res/{base_name}.asc'
#     tiff_file = f'res/{base_name}.tif'
#
#     return asc_file, tiff_file
# def convert_asc_to_tiff(asc_file, tif_file):
#     with open(asc_file, 'r') as f:
#         # Read header information
#         header = {}
#         for line in f:
#             if line.startswith('ncols'):
#                 header['ncols'] = int(line.split()[1])
#             elif line.startswith('nrows'):
#                 header['nrows'] = int(line.split()[1])
#             elif line.startswith('xllcorner'):
#                 header['xllcorner'] = float(line.split()[1])
#             elif line.startswith('yllcorner'):
#                 header['yllcorner'] = float(line.split()[1])
#             elif line.startswith('cellsize'):
#                 header['cellsize'] = float(line.split()[1])
#             elif line.startswith('NODATA_value'):
#                 header['nodata'] = float(line.split()[1])
#             if len(header) >= 6:
#                 break
#
#         # Read grid data into a NumPy array
#         data = np.loadtxt(f, dtype=np.float32)
#
#         # Create transform
#         transform = from_origin(
#             header['xllcorner'],
#             header['yllcorner'] + header['cellsize'] * header['nrows'],
#             header['cellsize'],
#             header['cellsize']
#         )
#
#         # Write the TIFF file
#         with rasterio.open(
#                 tif_file, 'w',
#                 driver='GTiff',
#                 height=header['nrows'],
#                 width=header['ncols'],
#                 count=1,
#                 dtype=data.dtype,
#                 crs='EPSG:4326',
#                 transform=transform
#         ) as dst:
#             dst.write(data, 1)
# def run_java_command(species_file):
#     # Define the Java command and its arguments
#     java_command = [
#         "java", "density.MaxEnt",
#         "nowarnings", "noprefixes", "nopictures", "jackknife",
#         "outputdirectory=results", f"samplesfile=species_data/{species_file}",
#         "environmentallayers=attributes1", "autoRun", "visible=False", "randomtestpoints=30"
#     ]
#
#     # Run the command
#     try:
#         # Execute the Java command
#         result = subprocess.run(java_command, check=True, text=True, capture_output=True)
#
#         # Print the standard output and error
#         print("Output:", result.stdout)
#         print("Error:", result.stderr)
#     except subprocess.CalledProcessError as e:
#         # Handle errors in case the command fails
#         print("Error occurred while running the Java command:", e)
#     asc_file, tiff_file = generate_file_paths(species_file)
#     convert_asc_to_tiff(asc_file, tiff_file)
#
#
# def take_first_n_samples(species_folder, n=1):
#     # Get all CSV files in the folder
#     csv_files = [f for f in os.listdir(species_folder) if f.endswith('.csv')]
#
#     # Take the first n files
#     csv_files_to_process = csv_files[:n]
#
#     print(f'Processing the following files: {csv_files_to_process}')
#
#     for filename in csv_files_to_process:
#         print(f'Running  {filename}')
#         run_java_command(filename)
#
# take_first_n_samples('species_data')


# import os
# import subprocess
# import pandas as pd
# import rasterio
# from rasterio.transform import from_origin
# import numpy as np
# from bs4 import BeautifulSoup
#
#
# def generate_file_paths(species_file):
#     base_name = os.path.splitext(species_file)[0]
#     asc_file = f'res/{base_name}.asc'
#     tiff_file = f'final_tif_files/{base_name}.tif'
#     html_file = f'res/{base_name}.html'  # Assuming the HTML is named this way
#     return asc_file, tiff_file, html_file
#
#
# def extract_auc_from_html(html_file):
#     try:
#         with open(html_file, 'r') as file:
#             soup = BeautifulSoup(file, 'html.parser')
#
#         # Find the line that contains "Test AUC"
#         auc_line = soup.find(string=lambda text: text and "Test AUC" in text)
#
#         if auc_line:
#             # Extract the AUC value
#             auc_value_str = auc_line.split("Test AUC is ")[1].split(",")[0].strip()
#             auc_value = float(auc_value_str)
#             return auc_value
#         else:
#             print(f"No AUC line found in {html_file}.")
#             return None
#     except Exception as e:
#         print(f"Error reading {html_file}: {e}")
#         return None
#
#
# def convert_asc_to_tiff(asc_file, tif_file):
#     with open(asc_file, 'r') as f:
#         # Read header information
#         header = {}
#         for line in f:
#             if line.startswith('ncols'):
#                 header['ncols'] = int(line.split()[1])
#             elif line.startswith('nrows'):
#                 header['nrows'] = int(line.split()[1])
#             elif line.startswith('xllcorner'):
#                 header['xllcorner'] = float(line.split()[1])
#             elif line.startswith('yllcorner'):
#                 header['yllcorner'] = float(line.split()[1])
#             elif line.startswith('cellsize'):
#                 header['cellsize'] = float(line.split()[1])
#             elif line.startswith('NODATA_value'):
#                 header['nodata'] = float(line.split()[1])
#             if len(header) >= 6:
#                 break
#
#         # Read grid data into a NumPy array
#         data = np.loadtxt(f, dtype=np.float32)
#
#         # Create transform
#         transform = from_origin(
#             header['xllcorner'],
#             header['yllcorner'] + header['cellsize'] * header['nrows'],
#             header['cellsize'],
#             header['cellsize']
#         )
#
#         # Write the TIFF file
#         with rasterio.open(
#                 tif_file, 'w',
#                 driver='GTiff',
#                 height=header['nrows'],
#                 width=header['ncols'],
#                 count=1,
#                 dtype=data.dtype,
#                 crs='EPSG:4326',
#                 transform=transform
#         ) as dst:
#             dst.write(data, 1)
#
# def run_java_command(species_file):
#     java_command = [
#         "java", "density.MaxEnt",
#         "nowarnings", "noprefixes", "nopictures", "jackknife",
#         "outputdirectory=res", f"samplesfile=final_species_data/{species_file}",
#         "environmentallayers=final_attributes", "autoRun", "visible=False", "randomtestpoints=30"
#     ]
#     try:
#         result = subprocess.run(java_command, check=True, text=True, capture_output=True)
#         print("Output:", result.stdout)
#         print("Error:", result.stderr)
#     except subprocess.CalledProcessError as e:
#         print("Error occurred while running the Java command:", e)
#
#     asc_file, tiff_file, html_file = generate_file_paths(species_file)
#     convert_asc_to_tiff(asc_file, tiff_file)
#
#     # Extract AUC from HTML
#     auc_value = extract_auc_from_html(html_file)
#     if auc_value is not None:
#         save_auc_to_csv(species_file, auc_value)
#
#
# def save_auc_to_csv(species_file, auc_value):
#     base_name = os.path.splitext(species_file)[0]
#     auc_data = pd.DataFrame({'Species': [base_name], 'Test AUC': [auc_value]})
#
#     csv_file = 'auc_results.csv'
#     if os.path.exists(csv_file):
#         # Append to existing CSV
#         auc_data.to_csv(csv_file, mode='a', header=False, index=False)
#     else:
#         # Create new CSV
#         auc_data.to_csv(csv_file, index=False)
#
# def clear_res_folder(res_folder):
#     """Delete all files in the specified folder."""
#     for filename in os.listdir(res_folder):
#         file_to_delete = os.path.join(res_folder, filename)
#         if os.path.isfile(file_to_delete):  # Check if it's a file
#             os.remove(file_to_delete)
#             #print(f'Deleted {file_to_delete}')
# def take_first_n_samples(species_folder, n=1):
#     csv_files = [f for f in os.listdir(species_folder) if f.endswith('.csv')]
#     csv_files_to_process = csv_files[:n]
#     print(f'Processing the following files: {csv_files_to_process}')
#
#     for filename in csv_files_to_process:
#         print(f'Running  {filename}')
#         run_java_command(filename)
#         clear_res_folder("res")
#         clear_res_folder("res/plots")
#
#
# take_first_n_samples('final_species_data')

import os
import shutil
import subprocess
import pandas as pd
import rasterio
from rasterio.transform import from_origin
import numpy as np
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor


def generate_file_paths(species_file):
    # print(7)
    base_name = os.path.splitext(species_file)[0]
    asc_file = f'res/{base_name}.asc'
    tiff_file = f'tif_data_final/{base_name}.tif'
    html_file = f'res/{base_name}.html'
    return asc_file, tiff_file, html_file


def extract_auc_from_html(html_file):
    try:
        with open(html_file, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        auc_line = soup.find(string=lambda text: text and "Test AUC" in text)
        if auc_line:
            auc_value_str = auc_line.split("Test AUC is ")[1].split(",")[0].strip()
            auc_value = float(auc_value_str)
            return auc_value
        else:
            print(f"No AUC line found in {html_file}.")
            return None
    except Exception as e:
        print(f"Error reading {html_file}: {e}")
        return None


def convert_asc_to_tiff(asc_file, tif_file):
    # print(6)
    with open(asc_file, 'r') as f:
        header = {}
        for line in f:
            if line.startswith('ncols'):
                header['ncols'] = int(line.split()[1])
            elif line.startswith('nrows'):
                header['nrows'] = int(line.split()[1])
            elif line.startswith('xllcorner'):
                header['xllcorner'] = float(line.split()[1])
            elif line.startswith('yllcorner'):
                header['yllcorner'] = float(line.split()[1])
            elif line.startswith('cellsize'):
                header['cellsize'] = float(line.split()[1])
            elif line.startswith('NODATA_value'):
                header['nodata'] = float(line.split()[1])
            if len(header) >= 6:
                break

        data = np.loadtxt(f, dtype=np.float32)

        transform = from_origin(
            header['xllcorner'],
            header['yllcorner'] + header['cellsize'] * header['nrows'],
            header['cellsize'],
            header['cellsize']
        )

        with rasterio.open(
                tif_file, 'w',
                driver='GTiff',
                height=header['nrows'],
                width=header['ncols'],
                count=1,
                dtype=data.dtype,
                crs='EPSG:4326',
                transform=transform
        ) as dst:
            dst.write(data, 1)


def run_java_command(species_file):
    # print(5)
    java_command = [
        "java", "-Djava.awt.headless=true", "-cp", "maxent.jar", "density.MaxEnt",
        "nowarnings", "noprefixes", "jackknife",
        "outputdirectory=res", f"samplesfile=sp_data_final/{species_file}",
        "environmentallayers=final_attributes", "autoRun", "visible=False"
    ]

    try:
        result = subprocess.run(java_command, check=True, text=True, capture_output=True)
        print("Output:", result.stdout)
        print("Error:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error occurred while running the Java command:", e)
        print("Output:", e.stdout)
        print("Error:", e.stderr)
        return

    asc_file, tiff_file, html_file = generate_file_paths(species_file)
    if not os.path.exists(asc_file):
        print(f"Expected ASC output not found: {asc_file}")
        return
    convert_asc_to_tiff(asc_file, tiff_file)
    # auc_value = extract_auc_from_html(html_file)
    # if auc_value is not None:
    #     save_auc_to_csv(species_file, auc_value)
    #
    # # Extract both AUC and variable contributions
    # auc_value, contributions = extract_auc_and_contributions_from_html(html_file)
    # if auc_value is not None:
    #     save_auc_and_contributions_to_csv(species_file, auc_value, contributions)

    # Delete files containing species name
    delete_species_files(species_file)


# def extract_auc_and_contributions_from_html(html_file):
#     try:
#         with open(html_file, 'r') as file:
#             soup = BeautifulSoup(file, 'html.parser')
#
#         # Extracting AUC value
#         auc_line = soup.find(string=lambda text: text and "Test AUC" in text)
#         auc_value = None
#         if auc_line:
#             auc_value_str = auc_line.split("Test AUC is ")[1].split(",")[0].strip()
#             auc_value = float(auc_value_str)
#
#         # Extracting variable contributions from the table
#         table = soup.find_all('table')[1]
#         rows = table.find_all('tr')[1:]  # Skip header row
#
#         contributions = {}
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) >= 3:
#                 variable = cols[0].text.strip()
#                 percent_contribution = float(cols[1].text.strip())
#                 contributions[variable] = percent_contribution
#
#         return auc_value, contributions
#     except Exception as e:
#         print(f"Error reading {html_file}: {e}")
#         return None, None
#
#
# def save_auc_and_contributions_to_csv(species_file, auc_value, contributions):
#     base_name = os.path.splitext(species_file)[0]
#
#     # Ensure all columns are present in the contributions
#     all_variables = [
#         "wc2.1_30s_bio_1_fc", "wc2.1_30s_bio_2_fc", "wc2.1_30s_bio_3_fc", "wc2.1_30s_bio_4_fc",
#         "wc2.1_30s_bio_5_fc", "wc2.1_30s_bio_6_fc", "wc2.1_30s_bio_7_fc", "wc2.1_30s_bio_8_fc",
#         "wc2.1_30s_bio_9_fc", "wc2.1_30s_bio_10_fc", "wc2.1_30s_bio_11_fc", "wc2.1_30s_bio_12_fc",
#         "wc2.1_30s_bio_13_fc", "wc2.1_30s_bio_14_fc", "wc2.1_30s_bio_15_fc", "wc2.1_30s_bio_16_fc",
#         "wc2.1_30s_bio_17_fc", "wc2.1_30s_bio_18_fc", "wc2.1_30s_bio_19_fc", "wc2.1_30s_bio_20_fc"
#     ]
#     # Prepare row for CSV
#     row = {'Species': base_name, 'Test AUC': auc_value}
#
#     # Add contributions for each variable, use 0 if missing
#     for variable in all_variables:
#         row[variable] = contributions.get(variable, 0)
#
#     # Save or append to CSV
#     csv_file = 'auc_and_contributions_final.csv'
#     auc_data = pd.DataFrame([row])
#
#     if os.path.exists(csv_file):
#         auc_data.to_csv(csv_file, mode='a', header=False, index=False)
#     else:
#         auc_data.to_csv(csv_file, index=False)
#
# def save_auc_to_csv(species_file, auc_value):
#     base_name = os.path.splitext(species_file)[0]
#     auc_data = pd.DataFrame({'Species': [base_name], 'Test AUC': [auc_value]})
#     csv_file = 'auc_results.csv'
#     if os.path.exists(csv_file):
#         auc_data.to_csv(csv_file, mode='a', header=False, index=False)
#     else:
#         auc_data.to_csv(csv_file, index=False)


def delete_species_files(species_file):
    # print(4)
    base_name = os.path.splitext(species_file)[0]
    if os.path.isdir('res'):
        for filename in os.listdir('res'):
            if base_name in filename:
                file_to_delete = os.path.join('res', filename)
                os.remove(file_to_delete)
                print(f'Deleted {file_to_delete}')
    if os.path.isdir('res/plots'):
        for filename in os.listdir('res/plots'):
            if base_name in filename:
                file_to_delete = os.path.join('res/plots', filename)
                os.remove(file_to_delete)
                print(f'Deleted {file_to_delete}')


def move_processed_csv(species_file, destination_folder):
    # print(3)
    src = os.path.join('sp_data_final', species_file)
    dst = os.path.join(destination_folder, species_file)
    shutil.move(src, dst)
    print(f'Moved {src} to {dst}')


def check_presence_points(species_file):
    # print(2)
    presence_df = pd.read_csv('sp_data_final/species_presence_counts.csv')
    species_name = os.path.splitext(species_file)[0]
    presence_points = presence_df[presence_df['Species'] == species_name]['Presence_Count'].values

    if presence_points.size > 0 and presence_points[0] > 2:
        return True
    return False


def process_species_file(species_file):
    # print(1)
    if check_presence_points(species_file):
        run_java_command(species_file)
        move_processed_csv(species_file, 'pr_sp_data_final')
    else:
        move_processed_csv(species_file, 'pr_sp_data_final')


def take_first_n_samples(species_folder, n=600, destination_folder='processed_species_data'):
    presence_count_file = os.path.join(species_folder, 'species_presence_counts.csv')
    if not os.path.isdir(species_folder) or not os.path.exists(presence_count_file):
        raise FileNotFoundError(
            "Missing split species input state. Run `python3 separateSpecies.py` first "
            "to create `sp_data_final/` and `sp_data_final/species_presence_counts.csv`."
        )

    csv_files = [f for f in os.listdir(species_folder) if f.endswith('.csv')]
    csv_files_to_process = csv_files[:n]
    print(f'Processing the following files: {csv_files_to_process}')

    with ProcessPoolExecutor() as executor:
        executor.map(process_species_file, csv_files_to_process)


if __name__ == '__main__':
    take_first_n_samples('sp_data_final')
