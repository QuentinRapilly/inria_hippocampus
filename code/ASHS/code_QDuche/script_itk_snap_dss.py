#!/usr/bin/env python3
"""
script_itk_snap_dss.py allows to perform ITK SNAP DSS stuff

Usage:
script_itk_snap_dss.py [-d] [-c] [-p] [-P] [-S] [-l] [-s=su_id] [-t=tick] [-a=atlas]

 Options:
    -h, --help        Show this message.
    --version         Print the version.

Options
    -d, --download    Download and delete results of subject ID associated with ticket number
    -c, --create      Creates ticket
    -p, --plot        Plot segmentation result
    -S, --SegStats    Get segmentation statistics
    -P, --PlotStats   Plot segmentation statistics
    -l, --list        List current ITK-DSS tickets
Subject selection options
    -s, --sub=su_id   Specific subject (can be repeated)
    -t, --ticket=tick ITK-SNAP DSS Ticket Number
Atlas option
    -a, --atlas=atlas Chooses Atlas
"""
from os.path import join as opj, exists as ope, basename as opb
import warnings

warnings.filterwarnings('ignore', message="Fetchers from the nilearn.datasets module will be ")
warnings.filterwarnings('ignore', message="Casting data from")  # MNI152TEMPLATE
from glob import glob
import os
import sys

sys.path.append('../')
import docopt
import pandas as pd
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nilearn.plotting import plot_roi
from scripts.list_subjects import SUBJECTS, CATEGORY_SUBJECTS
from scripts.list_ashs_labels import PMC_VALS_LOI, MAG_VALS_LOI, LIST_LOI

# ASHS information
ASHS_PMC = 'ASHS-PMC'  # PMC atlas (Agés)
ASHS_MAG = 'ASHS-Magdeburg'  # Magdeburg atlas (Jeunes)
SER_KEY_PMC = '19a90669caedbb4fdb1718f699f614f46f9dc4cc'
SER_KEY_MAG = '9ae16cec4606c4e5d6d9e5dafb01a36f5fa89e2f'
MRI_LAYERS = ['000', '001']  # T2 and T1
SEG_LAYERS = ['002', '003', '004']  # Segmentation layers

DSS_SERVICES_KEYS = {ASHS_PMC: SER_KEY_PMC, ASHS_MAG: SER_KEY_MAG}
# Output directory for segmentation results
SEG_OUT_DIR = '/home/qduche/Projects/Aneravimm/results/itksnap_segmentations'

# Define labels of interest common to PMC and Magdeburg
IMAGING_DIR = '/home/qduche/Projects/Aneravimm/data/imaging'
ITKSNAP_WT = 'itksnap-wt'
CMD_LIST = ITKSNAP_WT + ' -dss-tickets-list'

ERROR_MSG_ATLAS = 'Error when specifying an atlas.\nChoose among : ' + str([ASHS_PMC, ASHS_MAG])

# Data Frame Columns
[C_SUB, C_GRP, C_ATL, C_LAY, C_ROI, C_VOL] = ['sub-id', 'gr-id', 'atlas', 'layer', 'ROI', 'volume (mm3)']


def create_dir(dir):
    if not ope(dir):
        os.mkdir(dir)
    return dir


def create_workspace(t1_file, t2_file, itk_workspace_file):
    """itksnap-wt
        -layers-set-main t2_oblique.nii -tags-add T2-MRI
        -layers-add-anat t1_wholebrain.nii -tags-add T1-MRI
        -layers-list -o mywork.itksnap
    """
    cmd = "itksnap-wt -layers-set-main {} -tags-add T2-MRI -layers-add-anat {} -tags-add T1-MRI -layers-list -o {}". \
        format(t2_file, t1_file, itk_workspace_file)
    os.system(cmd)


def create_ticket_cloud(itk_workspace_file, service_code):
    """itksnap-wt -i mywork.itksnap -dss-tickets-create [service_code]"""
    cmd = ITKSNAP_WT + ' -i ' + itk_workspace_file + ' -dss-tickets-create ' + service_code
    os.system(cmd)
    return cmd


def download_ticket(ticket_id, out_dir):
    """itksnap-wt -dss-tickets-download [ticket-id] [directory]"""
    cmd = ITKSNAP_WT + ' -dss-tickets-download ' + ticket_id + ' ' + out_dir
    os.system(cmd)


def delete_ticket(ticket_id):
    cmd = ITKSNAP_WT + ' -dss-tickets-delete ' + ticket_id
    os.system(cmd)


class ResultITKDSS:
    """
    Class to deal with ITK-DSS Results.
    """
    def __init__(self, directory):
        """
        Initializes the class instance
        :param directory: path to the result directory
        """
        self.dir = directory
        self.computed = len(os.listdir(self.dir)) > 0  # Files exist in the directory
        self.layer000 = None
        self.layer001 = None
        self.layer002 = None
        self.layer003 = None
        self.layer004 = None
        self.ticket = None
        if self.computed:
            self.set_results()

    def is_computed(self):
        """
        Tell whether results exist
        :return: boolean
        """
        return self.computed

    def set_results(self):
        """
        https://sites.google.com/view/ashs-dox/cloud-ashs/cloud-ashs-for-t2-mri?authuser=0
        layer_000_f2f2df776758efe78a3188a6b10dc4f2.nii.gz (T2)
        layer_001_d6f0b35af199a9a64c2ae1e10ce52182.nii.gz (T1)
        layer_002_880d4dc3a2fa54476115982185f07950.nii.gz (lfseg_heur ??)
        layer_003_93c7a8d791ba3e462170853b2fb017a6.nii.gz (lfseg_corr_usegray ??)
        layer_004_f79e8eafef77cbeb5db60d760810b443.nii.gz (lfseg_corr_nogray ??)
        """
        self.layer000 = glob(opj(self.dir, 'layer_000*'))[0]
        self.layer001 = glob(opj(self.dir, 'layer_001*'))[0]
        self.layer002 = glob(opj(self.dir, 'layer_002*'))[0]
        self.layer003 = glob(opj(self.dir, 'layer_003*'))[0]
        self.layer004 = glob(opj(self.dir, 'layer_004*'))[0]
        self.ticket = glob(opj(self.dir, 'ticket*'))[0]

    def get_layer(self, layer):
        if layer == '000':
            return self.layer000
        elif layer == '001':
            return self.layer001
        elif layer == '002':
            return self.layer002
        elif layer == '003':
            return self.layer003
        elif layer == '004':
            return self.layer004
        else:
            sys.exit('Unknown layer ' + layer)


class AneravimmMRISubject:
    def __init__(self, su_id):
        """
        Initializes an Anervimm subject
        :param su_id:
        """
        if not su_id in SUBJECTS:
            msg = "Wrong subject ID {}\n".format(su_id)
            msg += "Pick subject code among the following list : \n\t- " + '\n\t- '.join(SUBJECTS)
            sys.exit(msg)
        self.su_id = su_id  # Subject identification number
        self.gr_id = self.su_id[:2]  # Group identification
        self.su_dir = opj(IMAGING_DIR, self.su_id)  # Set subject imaging data dir
        # Output folder and subfolders
        self.save_dir = create_dir(opj(self.su_dir, 'results'))  # Set results directory (for ASHS results)
        self.results_pmc_dir = create_dir(opj(self.save_dir, 'ASHS-PMC'))
        self.results_mag_dir = create_dir(opj(self.save_dir, 'ASHS-Magdeburg'))
        # Look for MRI files
        self.list_t1 = glob(opj(self.su_dir, '*t1_mprage*.nii.gz'))  # List potential candidates for T1 file
        self.list_t2 = glob(opj(self.su_dir, '*t2_tse_HR*.nii.gz'))  # List potential candidates for T2 file
        self.n_t1 = len(self.list_t1)  # Count potential candidates for T1 file
        self.n_t2 = len(self.list_t2)  # Count potential candidates for T2 file
        self.t1_file = None  # Final T1 file
        self.t2_file = None  # Final T2 file
        if self.n_t1 > 1 or self.n_t2 > 1:
            sys.exit('Subject ID ' + self.su_id + ' has multiple T1 or T2.')
        # Define age category and chooses appropriate atlas
        self.age_cat = CATEGORY_SUBJECTS[self.su_id]
        if self.age_cat == "a":
            self.atlas = ASHS_PMC
            self.seg_loi = PMC_VALS_LOI  # Segmentation labels of interest
        elif self.age_cat == "j":
            self.atlas = ASHS_MAG
            self.service_code = DSS_SERVICES_KEYS[ASHS_MAG]
            self.seg_loi = MAG_VALS_LOI  # Segmentation labels of interest
        else:
            sys.exit('Unknown age category for subject ' + self.su_id)
        # Define itksnap-wt service code for the subject
        self.service_code = DSS_SERVICES_KEYS[self.atlas]  # Service code
        # I/O
        self.itk_workspace_file = None  # ITK workspace file (to be sent)
        # Resulting segmentation maps
        self.results_PMC = ResultITKDSS(self.results_pmc_dir)
        self.results_MAG = ResultITKDSS(self.results_mag_dir)
        # Initializes stuff
        self.set_mri_files()
        self.create_workspace_file()

    def set_mri_files(self):
        self.t1_file = self.list_t1[0]
        self.t2_file = self.list_t2[0]

    def __str__(self):
        return '{}\n\tT1: {}\n\tT2:{}'.format(self.su_id, self.t1_file, self.t2_file)

    def create_workspace_file(self):
        self.itk_workspace_file = opj(self.su_dir, 'workspace_ITK_{}.itksnap'.format(self.su_id))
        if not ope(self.itk_workspace_file):
            create_workspace(t1_file=self.t1_file, t2_file=self.t2_file, itk_workspace_file=self.itk_workspace_file)

    def create_ticket_cloud(self, service_code=None):
        if service_code:
            create_ticket_cloud(itk_workspace_file=self.itk_workspace_file, service_code=service_code)
        else:
            create_ticket_cloud(itk_workspace_file=self.itk_workspace_file, service_code=self.service_code)

    def download_ticket(self, ticket_id, atlas=None):
        if atlas:
            if atlas == ASHS_PMC:
                download_ticket(ticket_id=ticket_id, out_dir=self.results_pmc_dir)
            elif atlas == ASHS_MAG:
                download_ticket(ticket_id=ticket_id, out_dir=self.results_mag_dir)
            else:
                sys.exit(ERROR_MSG_ATLAS)
        else:
            print('Downloading ticket {} into {}'.format(ticket_id, self.save_dir))
            download_ticket(ticket_id=ticket_id, out_dir=self.save_dir)

    def has_results(self, atlas):
        if atlas == ASHS_PMC:
            return self.has_pmc_results()
        elif atlas == ASHS_MAG:
            return self.has_mag_results()
        else:
            sys.exit(ERROR_MSG_ATLAS)

    def has_pmc_results(self):
        return self.results_PMC.is_computed()

    def has_mag_results(self):
        return self.results_MAG.is_computed()

    def has_all_results(self):
        return self.has_pmc_results() and self.has_mag_results()

    def get_layer(self, layer, atlas):
        if atlas == ASHS_PMC:
            return self.results_PMC.get_layer(layer=layer)
        elif atlas == ASHS_MAG:
            return self.results_MAG.get_layer(layer=layer)
        else:
            sys.exit(ERROR_MSG_ATLAS)

    def plot_t2(self, atlas, layer='002'):
        """
        Creates a nilearn roiplot with T2 as bg img
        :param atlas: str, "ASHS-PMC" or "ASHS-Magdeburg"
        :param layer: chooses segmentation result
        :return:
        """
        roi_img = self.get_layer(layer=layer, atlas=atlas)  # Segmentation file
        bg_img = self.get_layer('000', atlas=atlas)  # T2 file
        al_str = atlas + '_layer_' + layer
        out_dir = create_dir(opj(SEG_OUT_DIR, 'seg_plots', al_str))
        out_file = opj(out_dir, '{}_seg_plot_{}.png'.format(self.su_id, al_str))
        if not ope(out_file):
            plot_roi(roi_img=roi_img, bg_img=bg_img, output_file=out_file, title=self.su_id, draw_cross=False,
                     black_bg=True)
            plt.close()
            print('\t T2 + layer {} ({}) file saved : {}'.format(layer, atlas, opb(out_file)))

    def get_seg_stats_labels_of_interest(self, atlas=ASHS_PMC, layer='003'):
        """

        :param atlas:
        :param layer:
        :return:
        """
        if atlas == ASHS_PMC:
            result_file = self.results_PMC
        elif atlas == ASHS_MAG:
            result_file = self.results_MAG
        else:
            sys.exit(ERROR_MSG_ATLAS)
        if layer in ['002', '003', '004']:
            seg_file = result_file.get_layer(layer)
        else:
            sys.exit('Unknown layer ' + layer)
        # Load nifti, get voxel volume, extract segmentation labels, computes volumes
        nifti_info = nib.load(seg_file)  # get Nifti information
        vox_vol = np.prod(np.abs(nifti_info.header['pixdim'][1:4]))  # Get voxel volume
        y = nifti_info.get_fdata()  # data array as y
        volumes = [np.sum(y == seg_label) * vox_vol for seg_label in self.seg_loi]
        return volumes


def find_subjects_with_several_identical_files():
    list_su_with_multiple_files = []
    list_su_with_single_files = []
    for su in SUBJECTS:
        ams = AneravimmMRISubject(su_id=su)
        if ams.n_t1 > 1 or ams.n_t2 > 1:
            list_su_with_multiple_files.append(su)
            if ams.n_t1 > 1:
                print(su, 'a', ams.n_t1, 'T1')
            else:
                print(su, 'a', ams.n_t2, 'T2')
        else:
            list_su_with_single_files.append(su)
    print(len(list_su_with_single_files), "correct subjects")
    print(len(list_su_with_multiple_files), "subjects with multiple files")
    print(list_su_with_single_files)
    print(list_su_with_multiple_files)


def get_segmentation_stats(atlas):
    """
    Creates a CSV file containing volumic information of structures of interest
    :return:
    """
    for layer in SEG_LAYERS:
        csv_file = opj(SEG_OUT_DIR, '{}_seg_stats_layer_{}.csv'.format(atlas, layer))
        if not ope(csv_file):
            print('Computing csv file {}'.format(csv_file))
            subjects = []
            atlases = []
            groups = []
            dict_volumes = {}
            for label_name in LIST_LOI:
                dict_volumes[label_name] = []
            # Iterate over the subjects with MRI files
            for su_id in SUBJECTS:
                ams = AneravimmMRISubject(su_id=su_id)
                # Append information concerning subject ID, group ID, atlas used
                subjects.append(ams.su_id)
                atlases.append(atlas)
                groups.append(ams.gr_id)
                # Gather volumetric information
                if ams.has_all_results():
                    volumes = ams.get_seg_stats_labels_of_interest(atlas=atlas, layer=layer)
                    for label_name, volume in zip(LIST_LOI, volumes):
                        dict_volumes[label_name].append(volume)
                else:
                    for label_name in LIST_LOI:
                        dict_volumes[label_name].append('')
            # Create the data frame
            data = {'sub-id': subjects, 'grp-id': groups, "Atlas": atlases}
            for s, seg_label in enumerate(LIST_LOI):
                data[seg_label] = dict_volumes[seg_label]  # Create the key and set values inside the columns
            df = pd.DataFrame(data=data, columns=['sub-id', 'grp-id', 'Atlas'] + LIST_LOI)
            df.to_csv(csv_file, index=False)
            print('Saving ASHS segmentation results into csv file : ' + csv_file)
        else:
            print('CSV file {} already exists'.format(csv_file))


def create_data_frame_all_atlases_all_layers():
    """
    Creates a data frame with all atlases, all layers, all ROIs
    sub-id, gr-id, atlas, layer, ROI,volume (mm3)
    PA01, PA, ASHS-Magdeburg, 2, MAG_Left CA1, 389
    PA01, PA, ASHS-Magdeburg, 2, MAG_Left CA2, 6
    PA01, PA, ASHS-Magdeburg, 2, MAG_Left CA3, 71
    """
    csv_file = opj(SEG_OUT_DIR, 'df_all_layers_all_atlases.csv')
    if ope(csv_file):
        return pd.read_csv(csv_file)
    else:
        print('Calculating Maxi Data Frame segmentation results...')
        l_su, l_gr, l_at, l_la, l_ro, l_vo = [], [], [], [], [], []
        for atlas in [ASHS_MAG, ASHS_PMC]:
            # prefix_roi = {ASHS_MAG: 'MAG', ASHS_PMC: 'PMC'}[atlas]
            for layer in SEG_LAYERS:
                for su_id in SUBJECTS:
                    ams = AneravimmMRISubject(su_id=su_id)
                    if ams.has_all_results():
                        volumes = ams.get_seg_stats_labels_of_interest(atlas=atlas, layer=layer)
                        for label_name, volume in zip(LIST_LOI, volumes):
                            # Append information concerning subject ID, group ID, atlas used
                            l_su.append(ams.su_id)
                            l_gr.append(ams.gr_id)
                            l_at.append(atlas)
                            l_la.append(layer)
                            l_ro.append(label_name.replace('Left ', 'L ').replace('Right ', 'R '))
                            l_vo.append(volume)
        # Create the data frame
        data = {C_SUB: l_su, C_GRP: l_gr, C_ATL: l_at, C_LAY: l_la, C_ROI: l_ro, C_VOL: l_vo}
        cols = [C_SUB, C_GRP, C_ATL, C_LAY, C_ROI, C_VOL]
        # for s, seg_label in enumerate(LIST_LOI):
        #     data[seg_label] = dict_volumes[seg_label]  # Create the key and set values inside the columns
        df = pd.DataFrame(data=data, columns=cols)
        df.to_csv(csv_file, index=False)
        print('Saving ASHS segmentation Maxi Data Frame into csv file : ' + csv_file)
        return df


def barplot_in_rois():
    df = create_data_frame_all_atlases_all_layers()
    out_dir = create_dir(opj(SEG_OUT_DIR, 'volume_stat_plots'))
    for atlas in [ASHS_MAG, ASHS_PMC]:
        df_at = df[df[C_ATL] == atlas]
        for layer in SEG_LAYERS:
            df_f = df_at[df_at[C_LAY] == int(layer)]
            png_file = opj(out_dir, '{}_layer_{}_barplot.png'.format(atlas, layer))
            if not ope(png_file) or True:
                bp = sns.barplot(x=C_ROI, y=C_VOL, hue=C_GRP, data=df_f)
                plt.title('{} layer {}'.format(atlas, layer))
                # Rotate x tick labels
                for item in bp.get_xticklabels():
                    item.set_rotation(90)
                plt.savefig(png_file, bbox_inches='tight')
                plt.close()
    sys.exit()



def main():
    args = docopt.docopt(__doc__)
    # Actions
    do_download = args['--download']  # Download ticket
    do_create_ticket = args['--create']  # Create ticket
    do_plot_anat = args['--plot']  # Plot T2 and layer
    do_get_seg_stats = args['--SegStats']  # Get Segmentation Statistics
    do_plot_stats = args['--PlotStats']  # Stat Plots
    do_list = args['--list']
    # Subject selection options
    sub_id = args['--sub']  # Subject ID
    ticket = args['--ticket']  # DSS Ticket
    # Atlas option
    atlas = args['--atlas']

    atlas_list = [None, ASHS_MAG, ASHS_PMC]
    if atlas not in [None, ASHS_MAG, ASHS_PMC]:
        sys.exit('Choose atlas among ' + str(atlas_list))

    if do_plot_anat:
        for su_id in SUBJECTS:
            ams = AneravimmMRISubject(su_id=su_id)
            if ams.has_all_results():
                for atlas in [ASHS_MAG, ASHS_PMC]:
                    for layer in SEG_LAYERS:
                        ams.plot_t2(atlas=atlas, layer=layer)
            else:
                print(su_id, 'has no results')
        sys.exit('Plotting of subjects performed.')

    if do_get_seg_stats:
        if atlas is None:
            create_data_frame_all_atlases_all_layers()
        else:
            get_segmentation_stats(atlas=atlas)
        sys.exit('Segmentation stats performed.')

    if do_plot_stats:
        barplot_in_rois()

    if do_list:
        print(CMD_LIST)
        os.system(CMD_LIST)
        sys.exit()

    # Create Aneravimm MRI Subject instance
    ams = AneravimmMRISubject(su_id=sub_id)

    if do_create_ticket:
        ams.create_ticket_cloud(atlas)

    if do_download:
        ams.download_ticket(ticket_id=ticket, atlas=atlas)
        delete_ticket(ticket_id=ticket)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    main()
