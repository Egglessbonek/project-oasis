# Developing on MacOS

## Install PostgreSQL

To install postgresql:
```bash
brew install postgresql@16
```

The terminal output will tell you to add something to your PATH, do that.
Then use a new terminal to proceed:

To create start postgres:
```bash
brew services start postgresql
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



