import pandas as pd
import os
import re


def sanitize_filename(filename):
    """Replace invalid characters in filenames with underscores."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1F\s]', '_', filename)


def separate_species_to_csv(input_csv, output_folder):
    # Read the dataset
    df = pd.read_csv(input_csv)

    # Check if required columns are present
    if not all(col in df.columns for col in ['Species', 'Latitude', 'Longitude']):
        raise ValueError("Input CSV must contain 'Species', 'Latitude', and 'Longitude' columns.")

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a new file to store the number of presence points for each species
    presence_count_file = os.path.join(output_folder, 'species_presence_counts.csv')

    # Prepare data to write the species presence counts
    species_presence_counts = []

    # Group by species and save or append each group to a CSV file
    species_groups = df.groupby('Species')
    for species, group in species_groups:
        sanitized_species = sanitize_filename(species)
        output_file = os.path.join(output_folder, f'{sanitized_species}.csv')

        # Get the number of presence points (rows) for the species
        num_presence_points = group.shape[0]
        species_presence_counts.append([species, num_presence_points])

        # Append to the species-specific CSV file or create a new one
        if 0:
            # Append to existing file
            group[['Species', 'Latitude', 'Longitude']].to_csv(output_file, mode='a', header=False, index=False)
            print(f'Appended to {output_file}')
        else:
            # Create a new file
            group[['Species', 'Latitude', 'Longitude']].to_csv(output_file, index=False)
            print(f'Saved {output_file}')

    # Create or append to the species presence counts CSV file
    presence_counts_df = pd.DataFrame(species_presence_counts, columns=['Species', 'Presence_Count'])
    presence_counts_df.to_csv(presence_count_file, index=False)
    print(f'Saved species presence counts to {presence_count_file}')


# Example usage
input_csv = 'Final_Species.csv'
output_folder = 'sp_data_final'
separate_species_to_csv(input_csv, output_folder)

# import pandas as pd
#
# # Load the original CSV file
# input_csv_path = "biodiv_final_all_470sp_6Dec22.csv"  # Update with your input CSV file path
# df = pd.read_csv(input_csv_path)
#
# # List to hold summary data for presence points
# summary_data = []
#
# # Loop through each species column (assuming the first two columns are 'x' and 'y')
# for species in df.columns[2:]:  # Start from the third column
#     # Create a list to hold presence points
#     presence_points = []
#
#     # Iterate through the rows
#     for index, row in df.iterrows():
#         if row[species] == 1:  # Check for presence
#             # Extract latitude and longitude
#             latitude = row['y']  # Assuming 'y' is Latitude
#             longitude = row['x']  # Assuming 'x' is Longitude
#             presence_points.append([species, latitude, longitude])
#
#     # Convert the list to a DataFrame
#     if presence_points:  # Only create a CSV if there are presence points
#         species_df = pd.DataFrame(presence_points, columns=['Species', 'latitude', 'longitude'])
#
#         # Format species name for the file name
#         species_name = species.replace(" ", "_")  # Replace spaces with underscores for file naming
#         output_csv_path = f"final_species_data/{species_name}.csv"
#
#         # Save the DataFrame to a new CSV file
#         species_df.to_csv(output_csv_path, index=False)
#
#         # Append the species name and count of presence points to summary data
#         summary_data.append({'Species': species_name, 'Presence_Count': len(presence_points)})
#
# # Create a summary DataFrame from the summary data
# summary_df = pd.DataFrame(summary_data)
#
# # Save the summary DataFrame to a new CSV file
# summary_csv_path = "final_species_data/presence_summary.csv"
# summary_df.to_csv(summary_csv_path, index=False)
#
# print(f"Saved presence summary to {summary_csv_path}.")
# print("Processing complete.")


