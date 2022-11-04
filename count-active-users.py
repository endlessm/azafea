#!/usr/bin/env python3
"""
In brief, if we get a ping with config M at time T with count C, then a ping with config M at time
>= T + 24h with count C + 1 can be assumed to be either the same computer, or an equivalent one. So
we can calculate a lower bound on the online computers in a given window of time (e.g. 1 calendar
month) based only on the pings that are sent every 24h, and the number of days each computer is
online in that time.

It's a lower bound for at least 2 reasons:

1. Suppose we have the following pings, all with the same ping configuration:

    P1: Ping from computer A on 2022-09-30 with count 100
    P2: Ping from computer B on 2022-10-02 with count 100
    P3: Ping from computer A on 2022-10-15 with count 101

   (Remember, we don't have a per-computer identifier, only the OS image + hardware manufacturer +
   model.)

   If we are only considering pings in the range 2022-10-01 to 2022-10-31, then we will identify P2
   with P3 and assume there is only 1 computer.

2. Pings are sent slightly less frequently than every 24 hours. If you don't use your computer for
   very long each day, you can "miss" a day in your pings. So you might be undercounted for any
   given month.

"""
import argparse
import psycopg2
import collections
import datetime as dt

X = collections.namedtuple("X", "config_id created_at last_count times_seen")
TWENTY_FOUR_HOURS = dt.timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("where", nargs="?", default="1=1")
    args = ap.parse_args()

    machines: [X] = []

    with psycopg2.connect(args.db) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                    select
                        p.created_at,
                        p.count,
                        p.config_id
                    from
                        ping_v1 p
                    join
                        ping_configuration_v1 pc
                    on
                        p.config_id = pc.id
                    where
                        p.created_at between %s and %s
                    and
                        -- Forgive me father for I have sinned
                        {args.where}
                    order by
                        p.created_at asc,
                        p.count asc
                """,
                (args.start, args.end),
            )

            for j, (created_at, count, config_id) in enumerate(cur):
                for i, x in enumerate(machines):
                    if (
                        x.config_id == config_id
                        and x.last_count + 1 == count
                        and x.created_at + TWENTY_FOUR_HOURS <= created_at
                    ):
                        machines.pop(i)
                        previous_times = x.times_seen
                        break
                else:
                    previous_times = set()

                machines.append(
                    X(config_id, created_at, count, previous_times | {created_at})
                )

    for i, x in enumerate(sorted(machines, key=lambda x: len(x.times_seen))):
        print(f"Machine {i+1:3} seen on {len(x.times_seen):2} days")


if __name__ == "__main__":
    main()
