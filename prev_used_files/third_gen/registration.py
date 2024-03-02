import subprocess
import numpy as np
import math
import SimpleITK as sitk
import os
from uuid import uuid4

def registration_schedule(voxel_size, image_size):
    """
    Given the voxel and image size, return a sensible registration schedule
    :param voxel_size:
    :param image_size:
    :return:
    """
    # Chose a sensible registration schedule

    # heuristically determined, how large can voxel be and still make sense
    max_voxel_size = (8, 8, 8)
    # using the voxel size criterion, what is the max downsampling rate
    max_downsampling_ratio_per_dim = np.array(max_voxel_size)/voxel_size

    for d in range(3):
        max_downsampling_ratio_per_dim[d] = min(max_downsampling_ratio_per_dim[d], image_size[d]//4)
    # we do not upsample so the rate is minimally 1
    max_downsampling_ratio_per_dim = np.maximum(1, max_downsampling_ratio_per_dim)
    # Each downsampling is with a factor of 2, how many do we need
    nb_downsamplings_per_dim = [int(math.log2(r)) for r in max_downsampling_ratio_per_dim]
    nb_resolutions = min(4, max(nb_downsamplings_per_dim)+1)  # Cap the nb of resolution on 4

    return [
        [
            min(2 ** (res - 1), int(max_downsampling_ratio_per_dim[dim]))
            for dim in range(3)
        ]
        for res in range(nb_resolutions, 0, -1)
    ]

def register_images(
        path_fixed_image,
        path_moving_image,
        path_fixed_mask,
        ELASTIX_PATH,
        output_directory="."):
    """
    :param path_fixed_image:
    :param path_moving_image:
    :param output_directory:        important, this path cannot be shared with other
    """
    output_directory = output_directory + '/tmp'
    # Get some image info
    fixed_image = sitk.ReadImage(path_fixed_image)
    voxel_size = fixed_image.GetSpacing()
    image_size = fixed_image.GetSize()[0:3]

    fixed_mask = sitk.ReadImage(path_fixed_mask)
    reg_mask = sitk.Cast(sitk.BinaryDilate(fixed_mask, [2, 2, 2]), sitk.sitkUInt8)
    path_reg_mask = os.path.join(output_directory, 'reg_mask.nii.gz')
    sitk.WriteImage(reg_mask, path_reg_mask)

    # Create parameter file
    sched = registration_schedule(voxel_size, image_size)
    params = {
        'AutomaticParameterEstimation': ('true',),
        'AutomaticScalesEstimation': ('true',),
        'AutomaticTransformInitialization': ('true',),
        'AutomaticTransformInitializationMethod': ('CenterOfGravity',),  
        'HowToCombineTransforms': ('Compose',),
        'CheckNumberOfSamples': ('true',),
        'UseDirectionCosines': ('true',),
        'DefaultPixelValue': ('0',),  # ,(str(invalid_value),),
        'ErodeFixedMask': ('false',),
        'ErodeMovingMask': ('false',),
        'FixedImagePyramid': ('FixedRecursiveImagePyramid',),
        'MovingImagePyramid': ('MovingRecursiveImagePyramid',),
        'NumberOfResolutions': (str(len(sched)),), #
        'ImagePyramidSchedule': (str(factor) for level in sched for factor in level),#
        'ImageSampler': ('RandomSparseMask',),  # random
        'Interpolator': ('BSplineInterpolator',),  # LinearInterpolator
        'MaximumNumberOfIterations': ('1500',),
        'MaximumNumberOfSamplingAttempts': ('2000',),
        'MaximumStepLength': ('1',),
        'Metric': ('AdvancedNormalizedCorrelation',),  # AdvancedMeanSquares  AdvancedNormalizedCorrelation
        'NumberOfHistogramBins': ('128',),  # mutual informatin
        'NewSamplesEveryIteration': ('true',),
        'NumberOfSamplesForExactGradient': ('4096',),
        'NumberOfSpatialSamples': ('2048',),
        'Optimizer': ('AdaptiveStochasticGradientDescent',),
        'Registration': ('MultiResolutionRegistration',),
        'ResampleInterpolator': ('FinalBSplineInterpolator',),
        'Resampler': ('DefaultResampler',),
        'ResultImageFormat': ('nii',),
        'Transform': ('EulerTransform',),
        'WriteIterationInfo': ('false',),
        'WriteResultImage': ('false',),
        'ResultImagePixelType': ('float',),
        'FinalBSplineInterpolationOrder': ('0',), #todo not sure if 3 or 0?
        'WriteResultImage': ('true',),
        'BSplineInterpolationOrder': ('3',), #new
        'CheckNumberOfSamples': ('true',)
    }

    # 1. Find direct transform for the images.
    # Write parameter file to disk
    path_params = os.path.join(output_directory, 'params_%s.txt' % uuid4())
    with open(path_params, "w") as f:
        for k, vs in params.items():
            line = "(" + k + " " + " ".join(vs) + ")"
            f.write(line + "\n")

    # Create command Elastix
    command = os.path.join(ELASTIX_PATH, "elastix")
    command += f' -f {path_fixed_image} -m {path_moving_image} -out {output_directory} -p {path_params}' \
               f' -fMask {path_reg_mask}'  # -threads 1
    subprocess.call(command, shell=True)


    #  Create command Transformix and apply to mask
    path_transform_parameters_file = os.path.join(output_directory, "TransformParameters.0.txt")
    command = os.path.join(ELASTIX_PATH, "transformix")
    command += f' -in {path_fixed_mask} -out {output_directory} -tp {path_transform_parameters_file}'
    subprocess.call(command, shell=True)