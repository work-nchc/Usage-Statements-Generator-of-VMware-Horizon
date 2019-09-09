# The Usage Statements Generator of VMware Horizon from NCHC

Ported from [Log-Analyzer-of-VMware-Horizon-for-Usage-Calculation](https://github.com/work-nchc/Log-Analyzer-of-VMware-Horizon-for-Usage-Calculation)

Dependency: pymssql

Tested in Python 3.6

---
Configure beginning time, database ip, state file, query strings in io_log.py, and the SU per hour for each pool in suph.csv first.

---
Routine Reporting:

```
PATH/TO/python.exe vdi_sql.py
```

Enter username and password.

Usage statement of each user will present in directory ./users, updated in real-time, listing log-in time, log-off time, duration in hour, pool, SU per hour, and SU.  There will also be report.log, error.log, state.sav, entitlement.log, pool.log in working directory.  The execution time will be printed on the standard output.

---
One-off Reporting:

```
PATH/TO/python.exe report_vdi.py
```

Enter username, password, beginning date, ending date, initial vdi state file, and output base name.

3 files will present after running this script, a report [base_name].csv with login/out data, an error file [base_name].err logging insufficient or inconsistent data, and a state file [base_name].sav.

---
2019-09-09 by 1803031@narlabs.org.tw
