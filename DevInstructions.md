# Developing on MacOS

## Install PostgreSQL

To install postgresql:
```bash
brew install postgresql@16
```

To create start postgres:
```bash

```

## Overview of Database

```
                  +---------+
                  |  Area   |
                  +---------+
                      |
        +-------------+-------------+
        |                           |
(1..*)  |                           | (1..*)
        V                           V
   +---------+                   +---------+
   |  Admin  |                   |   Well  |
   +---------+                   +---------+
                                      |
                        +-------------+-------------+
                        |                           |
                 (1..1) |                           | (1..*)
                        V                           V
               +---------------+           +-----------------+
               |  WellProject  |           | BreakageReport  |
               +---------------+           +-----------------+
```



