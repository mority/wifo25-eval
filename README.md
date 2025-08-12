# wifo25-eval

- gtfs timetable used: DELFI gtfs germany (21.07.2025)
- osm used: geofabrik osm germany (21.07.2025)
- motis config: see config.yml in this repo
- set availability in prima: 18.08.25 - 25.08.25, 1 Taxi, all day (03:00 - 00:00)

location completly random:
```shell
./motis generate -n 1000 --first_day 2025-08-17 --last_day 2025-08-24 --time_of_day 22 -m WALK,ODM -a --max_dist 50000 --max_travel_time 1440 --max_matching_distance 250 --fastest_direct_factor 1.6
```

location close to pt station (500m beeline):
```shell
./motis generate -n 1000 --first_day 2025-08-17 --last_day 2025-08-24 --time_of_day 22 -m WALK,ODM -a --max_dist 500 --max_travel_time 1440 --max_matching_distance 250 --fastest_direct_factor 1.6
```