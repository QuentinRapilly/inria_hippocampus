from ntpath import join
import os
import sys
from os.path import join as opj, exists as ope, basename as opb
from time import sleep


ASHS_T1_KEY = "455103a0295cbf85b267d40b0350d12784b198cc"

TICKETS_LIMIT = 10


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
    cmd = 'itksnap-wt -i {} -dss-tickets-create {}'.format(itk_workspace_file, service_code)
    infos = os.popen(cmd)
    job_info = infos.read()
    job_id = job_info.split(" ")[-1]
    print("job id is : {}".format(job_id))
    return job_id


def download_ticket(ticket_id, out_dir):
    """itksnap-wt -dss-tickets-download [ticket-id] [directory]"""
    cmd = 'itksnap-wt -dss-tickets-download {} {}'.format(ticket_id,out_dir)
    os.system(cmd)


def delete_ticket(ticket_id):
    cmd = 'itksnap -dss-tickets-delete {}'.format(ticket_id)
    os.system(cmd)

def get_tickets_id():
    cmd = 'itksnap-wt -dss-tickets-list'
    info = os.popen(cmd)

    info = info.read()
    info = info.split("\n")
    job_idx = [line.split()[1] for line in info if len(line)>0]

    return job_idx


def job_state(ticket_id):
    cmd = 'itksnap-wt -dss-tickets-progress {}'.format(ticket_id)
    info = os.popen(cmd)
    info = info.read()
    value = float(info.split()[-1])
    return value

if __name__ == "__main__":
    img_dir = sys.argv[1]
    seg_dir = sys.argv[2]

    ##### Pre-processing input files#####
    # allows to keep only sub* files (that corresponds to subjects files)
    files = [file for file in os.listdir(img_dir) if file.find("sub")==0] 
    
    # the following lines group the files referencing to the same person
    sub_dic = {}
    for file in files :
        subject = file.split("_")[0]
        if sub_dic.get(subject) == None:
            sub_dic[subject] = [file]
        else :
            sub_dic[subject].append(file)

    # from each group we keep only the last MRI
    file_list = list()
    for key in sub_dic :
        file_list.append(sorted(sub_dic[key])[-1])
    
    nb_files = len(file_list)
    already_processed = 0

    ##### Starting the segmentations #####
    job_dic = {}
    workspace_dir = create_dir(opj(seg_dir,"workspace"))

    print("Nombre de segmentations a effectuer : {}".format(len(file_list)))
    print("Debut des segmentations ...")

    while already_processed < nb_files:

        current_tickets = get_tickets_id()
        print("Nouvelle iteration :")
        for ticket in current_tickets :
            state = job_state(ticket)
            print("Etat du job {} : {}".format(ticket, state))
            if state == 1.0 :
                download_ticket(ticket, seg_dir)
                print("Segmentation de {} terminee".format(job_dic[ticket]))
                delete_ticket(ticket)
                already_processed += 1

        if len(get_tickets_id()) < TICKETS_LIMIT and len(file_list) > 0:
            current = file_list.pop()
            idx_sub = current.split("_")[0]
            workspace = opj(workspace_dir,idx_sub+".itksnap")
            create_workspace(opj(img_dir,current),workspace)
            job_id = create_ticket_cloud(workspace, ASHS_T1_KEY)
            print(job_id)
            job_dic[job_id] = idx_sub
            print("Lancement de la segmentation de {}".format(idx_sub))

        else :
            sleep(30)

    with open(join(seg_dir,"info.txt"),"w") as f_out :
        print(job_dic, file=f_out)
