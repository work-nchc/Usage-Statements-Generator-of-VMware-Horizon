# The Usage Statements Generator of VMware Horizon from NCHC

Ported from [Log-Analyzer-of-VMware-Horizon-for-Usage-Calculation](https://github.com/work-nchc/Log-Analyzer-of-VMware-Horizon-for-Usage-Calculation)

Dependency: pymssql

Tested in Python 3.6

---
Configure begin time, database ip, state file, query strings in io_log.py, and the SU per hour for each pool in suph.csv first.

---
Routine Reporting

```
PATH/TO/python.exe vdi_sql.py
```

Enter username and password.  Usage statement of each user will present in directory /users, updated in real-time, listing log-in time, log-off time, duration in hour, pool, SU per hour and SU.  There will also be report.log, error.log, state.sav, entitlement.log, pool.log in current directory.
