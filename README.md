# Searchable Table of CMIP5 data at NCI
  
**The resultant CMIP5 searchable table can be seen here: http://atlantis.nci.org.au/~kxs900/cmip_tables/index_CMIP5.html**

This code is used to make a searchable table of CMIP5 replica data hosted at NCI. Such a table exist to permit a simple interface for the Australian climate community to quickly search the CMIP5 data hosted at NCI, both the data currently available and that in the download queue. An equivalent script exists for CMIP6 and the result can be seen here: http://atlantis.nci.org.au/~kxs900/cmip_tables/index_CMIP6.html

"make_CMIP5_search_table.py" reads the sql database back-up commands recorded for all the CMIP5 replica files at NCI and sorts it into a simple csv format that is more easily read via javascript to create the online table. The multitable.js script reads the csv file and provides a searchable interface for users to search across the CMIP5 data. The final html view is seen under index_CMIP5.html

## Authors

This code was developed by Kate Snow at NCI. "multitable.js" was produced with the aid of Paul Redman, ANU, and uses the open-source papaparse csv parser.


