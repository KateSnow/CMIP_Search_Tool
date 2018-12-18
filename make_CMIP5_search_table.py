#!/usr/bin/env python
# coding: utf-8

"""
make_CMIP5_search_table.py
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Contributors:       Kate Snow (kate.snow@anu.edu.au)
This code reads the database back-up information recorded from NCI project
al33 detailing the datasets and files of all the CMIP5 replica data. The
file information are back-up commands for the sql database and is sorted 
via key facets and dumped into a csv table that can be more easily read with js. 
"""

import os
import glob
import numpy as np
import gzip
import time
import datetime

def main():

    ts=time.time()
    st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    #Get the latest db backup from al33 - the nci project for CMIP5 replicas
    list_of_files = glob.glob('/g/data/al33/admin/dtn/db/*')
    latest_file = sorted(list_of_files, key=os.path.getctime)[-2] #get second latest in case latest is still writing...

    #open the db
    f=gzip.open(latest_file,'rb')
    content = f.readlines()
    content = [(x.decode()).strip() for x in content]

    dataset_id_variable = []
    variable = []
    status = []
    files = []
    ensembles = []
    insts=[]
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
            idx_file_func_id = split.index("file_functional_id TEXT")
            idx_var = idx_var - len(split)

        if "INSERT INTO \"file\"" in split[0]:
            stat=split[idx_stat]
            var=split[idx_var]
            dataset_id = (split[idx_file_func_id]).split('.')

            #assuming the dataset_ids do not change!
            idx_model=3
            idx_exp=4
            idx_freq=5
            idx_realm=6
            idx_ensm=8

            model=dataset_id[idx_model]
            exp=dataset_id[idx_exp]
            freq=dataset_id[idx_freq]
            realm=dataset_id[idx_realm]
            ensemble=dataset_id[idx_ensm]

            # I want to group all the enesemble information together
            if [var,model,exp,freq,realm] in dataset_id_variable:
                idx = dataset_id_variable.index([var,model,exp,freq,realm])
                if ((status[idx] == "'done'") and (stat!="'done'")):
                    status[idx] = "'queued'"
                if ensemble not in ensembles[idx]:
                    ensembles[idx].append(ensemble)
            else:
                dataset_id_variable.append([var,model,exp,freq,realm]) 
                variable.append(var)
                if stat!="'done'":
                    status.append("'queued'")
                else:
                    status.append(stat)
                files.append(dataset_id)
                ensembles.append([ensemble])

    file_p2  = open("/home/900/kxs900/CMIP5_tabl.csv", "w")
    #Make the table of all the CMIP5 data
    for i in range(len(status)):
        if i == 0:

            # Enter csv header info
            file_p2.write("variable,")
            file_p2.write("model,")
            file_p2.write("experiment,")
            file_p2.write("frequency,")
            file_p2.write("realm,")
            file_p2.write("other,")
            file_p2.write("status,\n")
            
        file_p2.write("%s ,"%(variable[i].strip("'")))
        for j in range(len(files[i])):
            if (j==idx_model) or (j==idx_exp) or (j==idx_freq) or (j==idx_realm): 
                file_p2.write("%s,"%(files[i][j]))
        for j in range(len(ensembles[i])):
            file_p2.write("%s "%(ensembles[i][j]))
        file_p2.write(",")

        file_p2.write("%s"%(status[i].strip("'")))
        file_p2.write("\n")

    file_p2.close()

    return 

if __name__ =='__main__':
    main()
