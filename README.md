# Overview
Roomies is a scraper to obtain information on the real estate industry


# Usage
init
```
from scraper import compartoDepto
web = compartoDepto()
```

Get general stats of compartoDepto by pais -> return a directory with data in jsonfiles
```
web.general_stats()
```

Get details of depto in Chile -> return a directory with data in jsonfiles
```
web.get_info_rooms()
```