# Fencing Webscraper
A webscraper that pulls public fencing tournament result data from https://askfred.net/ into a MySQL database.

## Prerequisites
* Python 3
* MySQL
* MySQLDB
* Beautiful Soup 4

## Installing
1. Retrieve all tournament links and proceed to scrape each of them for their CSV download link. The links are then stored in    all_csv_links.json.
```
python3 all_csvlinks.py
```
2. Download all CSVs into a folder.
`python3 download_csvs.py`
3. Create a database named fencing in MySQL.
4. Modify the database credentials in build_database.py and run the file to build a database.
```
python3 ./database/build_databases.py
```
5. Generate statistics on tournament results and save them to the database.
 ```
 python3 ./database/add_stats_table.py
 ```

## Authors
* Colin Fong
* Tony Cheang
  
