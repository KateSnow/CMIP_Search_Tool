#!/usr/bin/env python
# coding: utf-8

"""
run_CMIP5_queued_clef.py
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Contributors:       Kate Snow (kate.snow@anu.edu.au)
This code provides the details of the datasets downloaded or added to the
synda queue in the past week. This data is sent to ua8 for use with clef
to permit users of the clef tool to see if their data is being downloaded.
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

    #Get the latest db backup from al33
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
    insts=[]

    file_p1  = open("/home/900/kxs900/CMIP5_clef_table.csv", "w")
    #sort through sql entries to get info wanted (from dataset_id)
    datasets=[]
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
            idx_date = split.index("end_date TEXT")
            idx_var = idx_var - len(split)

        if "INSERT INTO \"file\"" in split[0]:
            stat=split[idx_stat]
            var=split[idx_var]
            dataset_id = (split[idx_file_func_id]).split('.')

            inst=[]
            inst.append((".".join(dataset_id[:-2])).strip("'"))
            end_date = split[idx_date].strip("'")

            #find completed and queued datasets from the past week and write to file
            if stat!="'done'":
                if "%s,%s"%(var.strip("'"),inst[0]) not in datasets:
                    datasets.append("%s,%s"%(var.strip("'"),inst[0]))
                    file_p1.write("%s,%s,%s \n"%(var.strip("'"),inst[0],'queued'))
            else:
                days_diff = (datetime.datetime.strptime(st,"%Y-%m-%d %H:%M:%S")-datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S.%f")).days
                if days_diff < 7:
                    if "%s,%s"%(var.strip("'"),inst[0]) not in datasets:
                        datasets.append("%s,%s"%(var.strip("'"),inst[0]))
                        file_p1.write("%s,%s,%s \n"%(var.strip("'"),inst[0],'done'))

    file_p1.close()

    return 

if __name__ =='__main__':
    main()
