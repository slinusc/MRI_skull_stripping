import shutil
import glob
import os
import subprocess
import nibabel as nib
#from utils.registration import register_images

# Author: Ezequiel de la Rosa (ezequieldlrosa@gmail.com)
# Date: 10.03.2022

#ELASTIX_PATH = 'path_to_elastix' #todo fill in with your elastix path!

def generate_brain_mask(input_image_path, 
                        output_image_path, 
                        gpu=False, 
                        save_mask=1, 
                        mode='accurate'
                       ):
    '''Generates brain mask using HD-BET (Isensee et al. 2019).
    input_image_path = Flair image.'''

    print('Segmenting brain ', input_image_path)
    if gpu:
        command = f'hd-bet -i {input_image_path} -o {output_image_path} -s {save_mask} -mode {mode}'
    else:
        command = f'hd-bet -i {input_image_path} -o {output_image_path} -s{save_mask} -device cpu -mode {mode} -tta 0'
        print('HD-BET IN CPU')
    subprocess.call(command, shell=True)

def main(input_case_dir,
         output_case_dir,
         reference_image='flair',
         moving_image='dwi',
         mode='accurate',
         gpu=True,
         debug=False,
         nii_suffix='.nii'):

    """ Skull-strip flair, dwi and adc from a single subject.
    input_case_dir: path to folder with dwi, adc and flair.
    output_case_dir: path where skull-stripped images are saved.
    mode: options: 'accurate' (preferred, takes long), and 'fast' (for testing, but less precise)
    gpu:  Preferred option. If False, runs in CPU (takes way longer and is less accurate).
    debug: preserves a /tmp folder with Elastix registration files.
    """
    # Create output directory.
    if not os.path.exists((output_case_dir)):
        os.makedirs(output_case_dir)
        os.makedirs(output_case_dir + '/tmp')

    # 1. Skull-strip the reference image (FLAIR) with HD-BET.
    path_fixed_image = glob.glob(input_case_dir+'/*{}{}'.format(reference_image, nii_suffix))[0]
    output_brain_msk_path = os.path.join(output_case_dir, path_fixed_image.split("/")[-1:][0]).replace(nii_suffix, '')
    print('FLAIR skull stripping...')
    generate_brain_mask(input_image_path=path_fixed_image,
                        output_image_path=output_brain_msk_path,
                        gpu=gpu,
                        save_mask=1,
                        mode=mode)

    # Rename skull-stripped image file
    os.rename(output_brain_msk_path+'.nii.gz', output_brain_msk_path+'_skull-stripped.nii.gz')

    # 2. Image registration
    path_moving_image = glob.glob(input_case_dir+'/*{}{}'.format(moving_image, nii_suffix))[0]
    path_fixed_mask = glob.glob(output_case_dir+'/*_mask.nii.gz')[0]
    print('DWI-FLAIR registration...')

    register_images(path_moving_image,
                    path_fixed_image,
                    path_fixed_mask,
                    output_case_dir,
                    ELASTIX_PATH)

    # 3. Skull-strip  adc and dwi images.
    path_reg_mask = os.path.join(output_case_dir, 'tmp', 'result.nii')
    shutil.copy(path_reg_mask, output_case_dir+'/dwi_mask.nii')
    reg_mask = nib.load(path_reg_mask).get_fdata()

    # iterate over modalities and skull-strip
    print('DWI-ADC skull-stripping...')

    for mri_mod in ['dwi', 'adc']:
        path_vol2_strip = glob.glob(input_case_dir + '/*{}.nii'.format(mri_mod))[0]
        vol = nib.load(path_vol2_strip)
        vol_data = vol.get_fdata()*reg_mask

        # New skull stripped nib object
        skull_stripped_obj = nib.Nifti1Image(vol_data, vol.affine, vol.header)
        path_output_image = os.path.join(output_case_dir, path_vol2_strip.split("/")[-1:][0]).replace('.nii', '_skull-stripped.nii.gz')
        # Save image
        nib.save(skull_stripped_obj, path_output_image)

    if not debug:
        shutil.rmtree(output_case_dir + '/tmp')


if __name__ == "__main__":
    INPUT_CASE_DIR = '/secure-data/scientific/stroke_tum/bern/0'
    OUTPUT_CASE_DIR = '/secure-data/scientific/stroke_tum/bern/prepro'

    main(input_case_dir=INPUT_CASE_DIR,
         output_case_dir=OUTPUT_CASE_DIR,
         reference_image='flair',
         moving_image='dwi',
         mode='accurate',
         gpu=True,
         debug=False)
