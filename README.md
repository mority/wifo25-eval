# wifo25-eval

- gtfs timetable used: DELFI gtfs germany (21.07.2025)
- osm used: geofabrik osm germany (21.07.2025)

generate queries:

```shell
./motis generate -n 1000 --first_day 2025-07-28 --last_day 2025-08-04 -m WALK,ODM --max_dist 10000 --max_travel_time 1440 --max_matching_distance 250 --fastest_direct_factor 1.6
```