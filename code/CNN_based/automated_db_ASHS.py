import os
import sys
from os.path import join as opj, exists as ope, basename as opb


ASHS_T1_KEY = "455103a0295cbf85b267d40b0350d12784b198cc"
ITKSNAP_WT = 'itksnap-wt'


def create_dir(dir):
    if not ope(dir):
        os.mkdir(dir)
    return dir


def create_workspace(t1_file, itk_workspace_file):
    """itksnap-wt
        -layers-set-main t1_wholebrain.nii -tags-add T1-MRI
        -layers-list -o mywork.itksnap
    """
    cmd = "itksnap-wt -layers-set-main {} -tags-add T1-MRI -o {}". \
        format(t1_file, itk_workspace_file)
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




if __name__ == "__main__":
    img_dir = sys.argv[1]
    seg_dir = sys.argv[2]

    # allows to keep only sub* (that corresponds to subjects files)
    files = [file for file in os.listdir(img_dir) if file.find("sub")==0] 
    sub_dic = {}
    for file in files :
        subject = file.split("_")[0]
        if sub_dic.get(subject) == None:
            sub_dic[subject] = [file]
        else :
            sub_dic[subject].append(file)
    for key in sub_dic :
        print(sorted(sub_dic[key]))
