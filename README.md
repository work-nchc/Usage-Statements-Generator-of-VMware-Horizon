# Usage-Statements-Generator-of-VMware-Horizon

Ported from [Log-Analyzer-of-VMware-Horizon-for-Usage-Calculation](https://github.com/work-nchc/Log-Analyzer-of-VMware-Horizon-for-Usage-Calculation)

Dependency: pymssql

Tested in Python 3.6

---

Configure begin time, database ip, state file, query strings in io_log.py, and the SU per hour for each pool in suph.csv, running

```
PATH/TO/python.exe vdi_sql.py
```
