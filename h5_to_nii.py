import h5py
import nibabel as nib
import numpy as np

# Step 1: Read data from .h5 file
with h5py.File('/home/saxermi1/test_data/test.h5', 'r') as h5_file:
    image_data = h5_file['dataset_name'][()]  # Adjust 'dataset_name' to your specific dataset

# Step 2: Process the data if necessary (e.g., reshaping)
# This step depends on your data and might not always be necessary

# Step 3: Create a NIfTI image
nifti_img = nib.Nifti1Image(image_data, affine=np.eye(4))

# Step 4: Save the NIfTI image to a file
nib.save(nifti_img, '/home/saxermi1/test_data/output_filename.nii')

