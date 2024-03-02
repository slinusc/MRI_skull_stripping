Files:
-----------------------------
dicom_import_2d.ipynb
-----------------------------
- rename folders in PATH_DICOM to 03d (45 --> 045)
- create list with all patients and corresponding MR sequences --> stored in PATH_IMAGE_INFO
- import DICOM to h5py add dummy labels (all labels are 3) --> stored in PATH_2D_H5_RAW
- cleanup and add correct labels from jpg_2d_192x192.h5 --> stored in PATH_2D_H5_CLEAN
- plot and compare jpg and dicom data

----------------------------
dicom_import_3d.ipynb
-----------------------------
- folders in PATH_DICOM should be named in 03d format
- create list with all patients and corresponding MR sequences --> stored in PATH_IMAGE_INFO
- import DICOM to h5py add labels from PATH_CLEAN_UP --> stored in PATH_3D_H5
- plot dicom data

----------------------------
functions/_init_.py
----------------------------
- empty file, only used for python to recognize folder content

----------------------------
functions/config.py
----------------------------
- config file where different configuration variables are stored

----------------------------
/functions/data_import.py
----------------------------
- automated import of dicom images
- 2D dicom to h5py
- 3D dicom to h5py

----------------------------
/functions/plot_sequence.py
----------------------------
- functions for plotting MRIs

----------------------------
./data/baseline_data_DWI.csv
----------------------------
- baseline data corresponding to jpg_2d_192x192.h5

----------------------------
./data/Data_Import.csv
----------------------------
- most extensive database with all patients
- used for import of 2d dicoms to h5py
- used for the assignement of labels to 3d images

----------------------------
./data/data_info.csv
----------------------------
- all dicom files orderes by patient

----------------------------
./data/image_info.csv
----------------------------
- all dicom files orderes by patient

----------------------------

----------------------------
- jpg dataset
