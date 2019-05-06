#!/usr/bin/env python
# coding: utf-8


"""
run_CMIP6_queued_clef.py
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
    status = []
    files = []
    insts = []

    file_p1  = open("/home/900/kxs900/CMIP6_clef_table.csv", "w")
    #sort through sql entries to get info wanted (from dataset_id)
    datasets=[]
    stats = []
    for i in range(len(content)):
        paths = content[i]
        split = paths.split(',')

        #Get the indices for the required info... most of which comes from the file_functionl_id
        if "CREATE TABLE file " in split[0]:
            for i in range(len(split)):
                split[i]=split[i].strip()
            idx_stat = split.index("status TEXT")
            idx_file_func_id = split.index("file_functional_id TEXT")
            idx_date = split.index("end_date TEXT")

        if "INSERT INTO \"file\"" in split[0]:
            stat=split[idx_stat]
            dataset_id = (split[idx_file_func_id]).split('.')

            inst=[]
            inst.append((".".join(dataset_id[:-2])).strip("'"))
            end_date = split[idx_date].strip("'")

            #find compelted datasets from past week and determine if already accounted for
            if stat!="'done'":
                if inst[0] not in datasets:
                    datasets.append(inst[0])
                    stats.append('queued')
                if inst[0] in datasets:
                    if stats[datasets.index(inst[0])] == "'done'":
                        del datasets[datasets.index(inst[0])]
                        del stats[datasets.index(inst[0])]
                        datasets.append(inst[0])
                        stats.append('queued')
            else:
                days_diff = (datetime.datetime.strptime(st,"%Y-%m-%d %H:%M:%S")-datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S.%f")).days
                if days_diff < 7:
                    if inst[0] not in datasets:
                        datasets.append(inst[0])
                        stats.append('done')
    #write the datasets to file
    for i in range(len(datasets)):
        file_p1.write("%s,%s \n"%(datasets[i],stats[i]))

    file_p1.close()

    return 

if __name__ =='__main__':
    main()
