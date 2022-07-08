from ntpath import join
import os
import sys
from os.path import join as opj, exists as ope, basename as opb
from time import sleep, time
import argparse


ASHS_T1_KEY = "455103a0295cbf85b267d40b0350d12784b198cc"

TICKETS_LIMIT = 10


def create_dir(dir):
    if not ope(dir):
        os.mkdir(dir)
    return dir


def create_workspace(t1_file, itk_workspace_file):
    """
        Create a workspace with the MRI given in t1_file and then store it at itk_workspace_file.

        cmd : itksnap-wt -layers-set-main t1_wholebrain.nii -tags-add T1-MRI -layers-list -o mywork.itksnap
        (see itksnap-wt -h for help)
    """
    cmd = "itksnap-wt -layers-set-main {} -tags-add T1-MRI -o {}". \
        format(t1_file, itk_workspace_file)
    os.system(cmd)


def create_ticket_cloud(itk_workspace_file, service_code):
    """
        Create a ticket to start a distant segmentation using the workspace given in argument and using
        the method defined by service_code (to see every service available, see itksnap-wt -dss-services-list)
        
        cmd : itksnap-wt -i mywork.itksnap -dss-tickets-create [service_code]
    """
    cmd = 'itksnap-wt -i {} -dss-tickets-create {}'.format(itk_workspace_file, service_code)
    # os.popen(cmd) allows to store the output returned by cmd
    # we can then extract some infos we may need in it (such as the ticket_id).
    infos = os.popen(cmd)
    job_info = infos.read()
    job_id = job_info.replace("\n","").split(" ")[-1]
    return job_id


def download_ticket(ticket_id, out_dir):
    """
        Download the result of a segmentation of the ticket given in argument.

        cmd : itksnap-wt -dss-tickets-download [ticket-id] [directory]
    """
    cmd = 'itksnap-wt -dss-tickets-download {} {}'.format(ticket_id,out_dir)
    os.system(cmd)


def delete_ticket(ticket_id):
    """
        Delete the ticket given in argument (after you've download the results)

        cmd : itksnap-wt -dss-tickets-delete <ticket_id>
    """
    cmd = 'itksnap-wt -dss-tickets-delete {}'.format(ticket_id)
    os.system(cmd)

def get_tickets_id():
    """
        Return every ticket currently processed and their corresponding states (ready, claimed, success).

        cmd : itksnap-wt -dss-tickets-list
    """
    cmd = 'itksnap-wt -dss-tickets-list'
    info = os.popen(cmd)
    # os.popen(cmd) allows to store the output returned by cmd
    # we can then extract some infos we may need in it (such as the ticket_ids).
    info = info.read()
    info = info.split("\n")
    job_idx = [(line.split()[1],line.split()[3]) for line in info if len(line)>0]

    return job_idx


def job_state(ticket_id):
    """
        Get the progress of a given ticket (between 0 : start => 1 : end)

        cmd : itksnap-wt -dss-tickets-progress <ticket_id>
    """
    cmd = 'itksnap-wt -dss-tickets-progress {}'.format(ticket_id)
    info = os.popen(cmd)
    info = info.read()
    value = float(info.split()[-1])
    return value

def print_all_tickets():
    """
        Print the state of every remaining tickets (used only for debugging).
    """
    cmd = 'itksnap-wt -dss-tickets-list'
    info = os.popen(cmd)
    info = info.read()
    print(info)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Path to MRIs to segment", required=True)
    parser.add_argument("-o", "--out_path", help="Path to dir where to store segmetations", required=True)
    
    args = parser.parse_args()

    img_dir = args.in_path
    seg_dir = args.out_path

    ##### Pre-processing input files#####
    # allows to keep only sub* files (that corresponds to subjects files) in the image directory
    files = [file for file in os.listdir(img_dir)] # if file.find("sub")==0] 
    
    file_list = files

    # Uncomment to process only one segmentation by subject :
    """
    # the following lines group the files/MRI referencing to the same subject
    sub_dic = {}
    for file in files :
        subject = file.split("_")[0]
        if sub_dic.get(subject) == None:
            sub_dic[subject] = [file]
        else :
            sub_dic[subject].append(file)

    # for each subject we keep only the last MRI that was made
    file_list = list()
    for key in sub_dic :
        file_list.append(sorted(sub_dic[key])[0]) # 0 for first MRI captured, -1 for last MRI captured
    """
    
    nb_files = len(file_list)
    already_processed = 0

    ##### Starting the segmentations #####
    job_dic = {}
    workspace_dir = create_dir(opj(seg_dir,"workspace"))

    print("Nombre de segmentations a effectuer : {}".format(len(file_list)))
    print("Debut des segmentations ...")

    start = time()

    with open(join(seg_dir,"info.csv"),"w") as f_out :


        while already_processed < nb_files:

            current_tickets = get_tickets_id()
            print("Temps ecoule : {} min".format((time()-start)//60))

            # For every remaining ticket, print its state
            for ticket in current_tickets :
                ticket, state = ticket
                progress = job_state(ticket)
                print("Etat du job {} : {} ({}%)".format(ticket, state, round(progress*100,ndigits=2)))

                # If the segmentation is finished, download the result and delete the ticket.
                if state == "success" :
                    print("Segmentation de {} terminee".format(job_dic[ticket]))
                    print(job_dic[ticket]+","+ticket, file=f_out)
                    dwnl_dir = join(seg_dir,job_dic[ticket])
                    os.mkdir(dwnl_dir)
                    download_ticket(ticket, dwnl_dir)
                    delete_ticket(ticket)
                    already_processed += 1

            # If the maximum number of tickets in parallel isn't reached and some subject remain
            # we submit a new one.
            if len(get_tickets_id()) < TICKETS_LIMIT and len(file_list) > 0:
                current = file_list.pop()
                crt_splitted = current.split("_")
                idx_sub = crt_splitted[0] + "_" + crt_splitted[1]
                workspace = opj(workspace_dir,idx_sub+".itksnap")
                create_workspace(opj(img_dir,current),workspace)
                job_id = create_ticket_cloud(workspace, ASHS_T1_KEY)
                job_dic[job_id] = idx_sub
                print("Lancement de la segmentation de {}".format(idx_sub))
            
            # If there is nothing to do (no new segmentation to submit) but some results are still missing
            # (segmentation in progress), we wait for them to finish.
            else :
                sleep(60)

    
