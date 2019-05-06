#!/usr/bin/env python
# coding: utf-8

"""
make_CMIP6_search_table.py
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Contributors:       Kate Snow (kate.snow@anu.edu.au)
This code reads the database back-up information recorded from NCI project
oi10 detailing the datasets and files of all the CMIP6 replica data. The
file information are back-up commands for the sql database and is sorted 
via key facets and dumped into a csv table that can be more easily read with js.
Unlike the CMIP5 table, this also includes the priorities of the download 
"""

import os
import glob
import numpy as np
import gzip
import time
import datetime

def main():

    # define the lists of priority datasets
    P1_mon=['cl', 'clt', 'evspsbl', 'hfds', 'hfls', 'hfss', 'hurs', 'hus', 'huss', 'mrros', 'mrsos', 'msftmrhoz', 'pr', 'ps', 'psl', 'rho', 'rlds', 'rlut', 'rsds', 'rsdt', 'rsus', 'rsut', 'sfcWind', 'siconc', 'sithick', 'so', 'sos', 'tas', 'tasmax', 'tasmin', 'tauu', 'tauv', 'thetao', 'tos', 'ts', 'ua', 'uas', 'uo', 'va', 'vas', 'vo', 'wap', 'zg', 'zos', 'zosga', 'orog', 'sftlf', 'areacello', 'areacella']
    P1_exp=['piControl', 'historical', 'ssp585', 'ssp245']
    P1_day=['pr', 'rsds', 'tas', 'tasmax', 'tasmin', 'ts', 'uas', 'vas', 'siconc', 'sithick', 'sfcWind']
    P1_6hr=['psl']
    P1_3hr=['pr','tas','uas','vas']

    P2_mon=['cct', 'cli', 'clivi', 'evap', 'gpp', 'hur', 'mrro', 'mrso', 'msftbarot', 'msftmyz', 'omlmax', 'prc', 'prsn', 'prw', 'rldscs', 'rlutcs', 'rsdscs', 'rsuscs', 'rsutcs', 'soga', 'ta', 'tauuo', 'tauvo', 'thetaoga', 'thkcello', 'tsl', 'umo', 'vmo', 'wfo', 'wmo', 'zossga', 'zostoga']
    P2_exp=['1pctCO2', 'amip', 'abrupt-4xCO2', 'ssp126']
    P2_day=['hur', 'hus', 'ta', 'ua', 'va', 'zg', 'sfcWindmax']
    P2_6hr=['tas','uas','vas','hus4','zg1000']
    P2_3hr=['hfls', 'hfss', 'huss', 'prc', 'ps', 'rlds', 'rlus', 'rsds', 'rsus', 'mrro']
 
    Tmon = ['AERmon', 'Amon', 'Omon', 'Lmon', 'SImon', 'LImon', 'fx']
    Tday = ['AERday', 'Oday', 'SIday', 'day']
    T6hr = ['6hrPLev']
    T3hr = ['3hr']

    # get date of the update
    ts=time.time()
    st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    #Get the latest db backup from al33
    list_of_files = glob.glob('/g/data/oi10/admin/dtn/db/*')
    latest_file = sorted(list_of_files, key=os.path.getctime)[-2] #get second latest in case latest is still writing...

    #open the db
    f=gzip.open(latest_file,'rb')
    content = f.readlines()
    content = [(x.decode()).strip() for x in content]

    dataset_id_variable = []
    variable = []
    priority = []
    status = []
    files = []
    ensembles = []
    insts = []
    #sort through sql entries to get info wanted (from dataset_id)
    for i in range(len(content)):
        paths = content[i]
        split = paths.split(',')

        #Get the indices for the required info... most of which comes from the file_functionl_id
        if "CREATE TABLE file " in split[0]:
            for i in range(len(split)):
                split[i]=split[i].strip()
            idx_stat = split.index("status TEXT")
            idx_var = split.index("variable TEXT")
            idx_var = idx_var - len(split)
            idx_file_func_id = split.index("file_functional_id TEXT")

        if "INSERT INTO \"file\"" in split[0]:
            stat=split[idx_stat]
            var=split[idx_var]
            dataset_id = (split[idx_file_func_id]).split('.')

            #assuming the dataset_ids do not change in synda!
            idx_model=3
            idx_exp=4
            idx_freq=6
            idx_ensm=5

            model=dataset_id[idx_model]
            exp=dataset_id[idx_exp]
            freq=dataset_id[idx_freq]
            ensemble=dataset_id[idx_ensm]
            inst=[]
            inst.append((".".join(dataset_id[:-2])).strip("'"))

            # I want to group all the enesemble information together
            if [var,model,exp,freq] in dataset_id_variable:
                idx = dataset_id_variable.index([var,model,exp,freq])
                if ((status[idx] == "'done'") and (stat!="'done'")):
                    status[idx] = "'queued'"
                if ensemble not in ensembles[idx]:
                    ensembles = ensembles + ensemble
                    insts = insts + inst[0]
            else:
                dataset_id_variable.append([var,model,exp,freq]) 
                variable.append(var)
                if stat!="'done'":
                    status.append("'queued'")
                else:
                    status.append(stat)
                files.append(dataset_id)
                ensembles.append([ensemble])
                insts.append(inst)
                # define the priority
                if freq in Tmon:
                    if ((var.strip("'") in P1_mon) and (exp in P1_exp)):
                        pr = 1
                    elif (((var.strip("'") in P1_mon) and (exp in P2_exp)) or ((var.strip("'") in P2_mon) and (exp in P1_exp))):
                        pr = 2
                    else:
                        pr='U'
                elif freq in Tday:
                    if ((var.strip("'") in P1_day) and (exp in P1_exp)):
                        pr = 1
                    elif ((var.strip("'") in P2_day) and (exp in P1_exp)):
                        pr = 2
                    else:
                        pr='U'
                elif freq in T6hr:
                    if ((var.strip("'") in P1_6hr) and (exp in P1_exp)):
                        pr = 1
                    elif ((var.strip("'") in P2_6hr) and (exp in P1_exp)):
                        pr = 2
                    else:
                        pr='U'
                elif freq in T3hr:
                    if ((var.strip("'") in P1_3hr) and (exp in P1_exp)):
                        pr = 1
                    elif ((var.strip("'") in P2_3hr) and (exp in P1_exp)):
                        pr = 2
                    else:
                        pr='U'
                else:
                    pr='U'

                priority.append(pr)

    file_p2  = open("/home/900/kxs900/CMIP6_tabl.csv", "w")

    #Make the table of all the CMIP5 data
    for i in range(len(status)):
        if i == 0:
            # Enter csv header info
            file_p2.write("variable,")
            file_p2.write("source_id,")
            file_p2.write("experiment,")
            file_p2.write("table_id,")
            file_p2.write("other,")
            file_p2.write("status priority,\n")

        file_p2.write("%s ,"%(variable[i].strip("'")))
        for j in range(len(files[i])):
            if (j==idx_model) or (j==idx_exp) or (j==idx_freq): 
                file_p2.write("%s,"%(files[i][j]))
        for j in range(len(ensembles[i])):
            file_p2.write("%s "%(ensembles[i][j]))
        file_p2.write(",")

        file_p2.write("%s %s"%(status[i].strip("'"),priority[i]))
        file_p2.write("\n")

    file_p2.close()

    return 

if __name__ =='__main__':
    main()
