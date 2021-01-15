#!/bin/bash
for year in 2019 2020
do
    for month in 01 02 03 04 05 06 07 08 09 10 11 12
    do python feed_data.py --year $year --month $month config.ini
        if [[ $year -eq 2020 && $month -eq 06 ]]
        then
        break
        fi
    done
done