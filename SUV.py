import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
import nrrd
import inspect
import SimpleITK as sitk
import pydicom
from pydicom import dcmread
from skimage.measure import label, regionprops
import argparse
import json
import ast
import re


def dicom_hhmmss(t):
    t = str(t)
    if '.' in t:
        t = t.split('.')[0]
    if len(t) == 5:
        t = '0' + t
    h_t = float(t[0:2])
    m_t = float(t[2:4])
    s_t = float(t[4:6])
    new_t = h_t * 3600 + m_t * 60 + s_t
    return new_t


from pydicom import dcmread


def SUV_jisuan(dicom_path, PET, norm):
    dcm = dcmread(dicom_path)
    Units = dcm.Units
    # print(dicom_path,Units)
    RadiopharmaceuticalInformationSequence = dcm.RadiopharmaceuticalInformationSequence[0]
    RadiopharmaceuticalStartTime = str(RadiopharmaceuticalInformationSequence['RadiopharmaceuticalStartTime'].value)
    RadionuclideTotalDose = str(RadiopharmaceuticalInformationSequence['RadionuclideTotalDose'].value)
    RadionuclideHalfLife = str(RadiopharmaceuticalInformationSequence['RadionuclideHalfLife'].value)
    ST = str(dcm.SeriesTime)
    AT = str(dcm.AcquisitionTime)
    PW = str(dcm.PatientWeight)
    RST = RadiopharmaceuticalStartTime
    RTD = RadionuclideTotalDose
    RHL = RadionuclideHalfLife
    RS = str(dcm.RescaleSlope)
    RI = str(dcm.RescaleIntercept)
    decay_time = dicom_hhmmss(ST) - dicom_hhmmss(RST)
    decay_dose = float(RTD) * pow(2, -float(decay_time) / float(RHL))
    SUVbwScaleFactor = (1000 * float(PW)) / decay_dose
    if Units == 'BQML':
        if norm:
            PET_SUV = (PET * float(RS) + float(RI)) * SUVbwScaleFactor
        else:
            PET_SUV = PET * SUVbwScaleFactor
    if Units == 'CNTS':
        # # 先转成BQML在做SUV计算
        # factor=dcm[(0X7053,0X1009)].value
        # BQML = (PET * float(RS) + float(RI)) * factor
        # if norm:
        #     PET_SUV = (BQML* float(RS) + float(RI)) * SUVbwScaleFactor
        # else:
        #     PET_SUV = BQML* SUVbwScaleFactor
        # 直接转换SUV
        factor = dcm[(0X7053, 0X1000)].value
        if norm:
            PET_SUV = (PET * float(RS) + float(RI)) * factor
        else:
            PET_SUV = PET * factor
    return PET_SUV


def dcmseries_nrrd(filepath1, filepath2):
    datapath = filepath1
    dcms_name = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(datapath)
    dcms_read = sitk.ImageSeriesReader()
    dcms_read.SetFileNames(dcms_name)
    dcms_series = dcms_read.Execute()
    sitk.WriteImage(dcms_series, filepath2)


if __name__ == '__main__':
    # image_DCM_path = 'D:/radshap/lymphoma-302/2.886 x 600 WB/'
    # image_savepath = 'D:/radshap/lymphoma-302/lymphoma-302.nrrd'
    # single_dicom_path = 'D:/MiDose/raw/C11/PET WB_filter4.5mm/9.dcm'
    # SUV_savepath = 'D:/MiDose/suv/C11/PET WB_filter4.5mm.nrrd'
    # dcmseries_nrrd(image_DCM_path, image_savepath)
    # 查看是否为pet图像
    # modality = dcmread(single_dicom_path)['Modality'].value
    # if modality == 'PT':
    #     image_data, image_options = nrrd.read(image_savepath)
    #     ### 调用方式，注意norm参数应设置为0
    #     SUV_data = SUV_jisuan(single_dicom_path, image_data, 0)
    #     nrrd.write(SUV_savepath, SUV_data, image_options)

    folder_path = 'D:/radshap'
    dir_path = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isdir(full_path):
            dir_path.append(full_path)
    for i in range(len(dir_path)):
        for folder in os.listdir(dir_path[i]):
            if folder == 'ROI':
                print('ROI folder')
            else:
                dcm_folder = os.path.join(dir_path[i], folder)
                image_DCM_path = dcm_folder
                single_dicom_path = os.path.join(dcm_folder, (os.listdir(dcm_folder)[-1]))
                modality = dcmread(single_dicom_path)['Modality'].value
                if modality == 'PT':
                    name = 'PET'
                else:
                    name = 'CT'
                image_savepath = os.path.join(dir_path[i], f'NRRD_{name}.nrrd')
                SUV_savepath = os.path.join(dir_path[i], f'SUV_{name}.nrrd')
                dcmseries_nrrd(image_DCM_path, image_savepath)
                if modality == 'PT':
                    image_data, image_options = nrrd.read(image_savepath)
                    ### 调用方式，注意norm参数应设置为0
                    SUV_data = SUV_jisuan(single_dicom_path, image_data, 0)
                    nrrd.write(SUV_savepath, SUV_data, image_options)



    # folder_path = 'D:/MiDose/raw/'
    # entries = os.listdir(folder_path)
    # file_paths = [os.path.join(folder_path, entry) for entry in entries]
    # path_lst = []
    # # 打印所有文件和文件夹的完整路径
    # for path in file_paths:
    #     path_lst.append(path)
    # save_lst = []
    # name_lst = []
    # for i in range(0, 79):
    #     # print(path_lst[i])
    #     filefolder = os.listdir(path_lst[i])
    #     filtered_items = [item for item in filefolder if 'PET WB' in item]
    #     # if len(filtered_items) == 0:
    #     #     filtered_items = [item for item in filefolder if '173_1' in item or '160_1' in item]
    #     # if len(filtered_items) == 2:
    #     #     filtered_items = [item for item in filefolder if 'PET_1' in item]
    #     # print(filefolder):
    #     # matches = re.findall(r'_(.*?)_', os.path.basename(path_lst[i]))
    #     # for match in matches:
    #     #     # print(match)
    #     #     name_lst.append(match)
    #     name_lst.append(filtered_items)
    #     filepth = os.path.join(path_lst[i], filtered_items[0])
    #     single_dcm = os.path.join(filepth, os.listdir(filepth)[-1])
    #     # print(single_dcm)
    #     image_DCM_path = filepth
    #     image_savepath = "D:/MiDose/nrrd/{}.nrrd".format(filtered_items)
    #     single_dicom_path = single_dcm
    #     SUV_savepath1 = "D:/MiDose/SUV/{}.nrrd".format(filtered_items)
    #     # SUV_savepath2 = "C:/Users/jiayu.sun/Desktop/work/MSI/SUV/CNTS/{}_PET.nrrd".format(match)
    #     dcmseries_nrrd(image_DCM_path, image_savepath)
    #     image_data, image_options = nrrd.read(image_savepath)
    #     ### 调用方式，注意norm参数应设置为0
    #     SUV_data, Unit = SUV_jisuan(single_dicom_path, image_data, 0)
    #
    #     # if Unit=='BQML':
    #     #     nrrd.write(SUV_savepath1, SUV_data, image_options)
    #     # elif Unit=='CNTS':
    #     #     nrrd.write(SUV_savepath2, SUV_data, image_options)
    #     # else:
    #     #     print('Units type error, Unit type is {}'.format(Unit))
    print('done')
