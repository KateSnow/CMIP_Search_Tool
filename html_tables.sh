#!/bin/bash
python /home/900/kxs900/make_CMIP6_search_table.py
python /home/900/kxs900/make_CMIP5_search_table.py
scp -i /home/900/kxs900/.ssh/kxs900-nopp /home/900/kxs900/index_CMIP*.html kxs900@atlantis.nci.org.au:/home/900/kxs900/public_html/cmip_tables/.
scp -i /home/900/kxs900/.ssh/kxs900-nopp /home/900/kxs900/CMIP*_tabl.csv kxs900@atlantis.nci.org.au:/home/900/kxs900/public_html/cmip_tables/.
python /home/900/kxs900/run_CMIP5_queued_clef.py
python /home/900/kxs900/run_CMIP6_queued_clef.py
scp -i /home/900/kxs900/.ssh/kxs900-nopp /home/900/kxs900/CMIP*_clef_table.csv kxs900@raijin.nci.org.au:/g/data/ua8/Download/CMIP6/.
