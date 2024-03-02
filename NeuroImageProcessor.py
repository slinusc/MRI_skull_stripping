import h5py
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
class NeuroImageProcessor:
    """
    The NeuroImageProcessor class provides a flexible framework for neuroimaging data manipulation and analysis. It supports operations such as visualization, format conversion, and data preprocessing, with the ability to extend its functionality to accommodate evolving neuroimaging processing requirements.
    """

    def __init__(self):
        """
        Initializes the NeuroImageProcessor without a specific file path.
        This implementation allows for the instance to be reused for different files.
        """
        pass

    
    def visualize_middle_slice(self, nifti_file_path):
        """
        Visualizes the middle slice of a NIfTI image file.

        :param nifti_file_path: String (path to the NIfTI file).
        """
        # Load the NIfTI file
        nifti_file = nib.load(nifti_file_path)
        
        # Convert the image data to a NumPy array
        image_data = nifti_file.get_fdata()
        
        # Middle slice from the z-axis (axis 2)
        middle_index = image_data.shape[2] // 2
        middle_slice = image_data[:, :, middle_index]
        
        # Display the middle slice
        plt.imshow(middle_slice.T, cmap="gray", origin="lower")
        plt.axis('off')  # Do not display axes
        plt.show()
        
    def h5_to_nifti(self, h5_file_path, output_directory, output_file_name, volume_index=0):
        """
        Converts a specified volume from an H5 file to a NIfTI file.
        for reasons unclear to me there seems to be an issue with h5py library unresolved for now
        :param h5_file_path: String (path to the H5 file).
        :param output_directory: String (path to the output directory).
        :param output_file_name: String (desired name of the output NIfTI file).
        :param volume_index: Integer (index of the volume to extract and save).
        """
        print(h5py.__version__)

        output_file_path = output_directory + output_file_name
        with h5py.file(h5_file_path, 'r') as file:   
            # Extract the specified volume from the dataset "X"
            volume = file['X'][volume_index]  # Adjusted to select a specific volume

            affine_matrix = np.eye(4)
            nifti_image = nib.Nifti1Image(volume, affine=affine_matrix)
            nib.save(nifti_image, output_file_path)
            print("Conversion finished successfully. NIfTI file saved at:", output_file_path)