# Overview
Roomies is a scraper to obtain information on the real estate industry


# Usage
init
```
from scrapper import compartoDepto
web = compartoDepto()
```

Get general stats of compartoDepto by pais
```
general_stats_csv = web.general_stats()
```

Get details of depto in Chile
deptos_chile_csv = web.get_info_rooms()