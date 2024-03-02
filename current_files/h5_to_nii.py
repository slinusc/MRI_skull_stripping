import h5py
import nibabel as nib
import numpy as np
from NeuroImageProcessor import  NeuroImageProcessor


# Specify your desired output directory path here
output_directory = '/home/saxermi1/test_data/'

# Ensure your file name is as desired
output_file_name = 'test_volume.nii'

# Combine the directory path and file name to create a full output path
output_file_path = output_directory + output_file_name

# Open the H5 file for reading
with h5py.File('/home/hezo/stroke_zurich/data/dicom_2d_192x192x3_clean_interpolated_18_02_2021_preprocessed2.h5', 'r') as file:
    # Extract the first volume from the dataset "X"
    first_volume = file['X'][0]  #  extracts the first 3D volume (128x128x28) (adjust number to extract different one)

    # Assuming an identity matrix for the affine transformation
    affine_matrix = np.eye(4)
    
    # Create a NIfTI image object from the extracted volume
    nifti_image = nib.Nifti1Image(first_volume, affine=affine_matrix)

    # Save the NIfTI image to the specified file path
    nib.save(nifti_image, output_file_path)
    print("finished succsessfully under")
    print(output_file_path)
    
    
    
