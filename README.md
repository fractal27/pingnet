# PingNet
PingNet is a pinging project in python that pings the local network using threads,
the project is multiplatform and could have multiple configurations.

## project's steps

1. importing modules and the parsing the arguments
2. getting the configuration desired
3. getting the number of pcs to analyze
4. define addresses,desc_pc,scan_results,pc_type with the numbers from 0 to the number of pcs
5. looping over the networks and filling the lists previously mentioned.
6. initalizing and joining the threads to ping.
7. if the argument webmode is inserted, it'll skip much visualization as possible to build the webfile
8. if the argument '--save-time-dataframe' is inserted it'll save the times in different formats using pandas.

## Configurations
different configurations are avaiable for both of the versions:

the documentation for the configuration is avaiable only in [english](/en/configurations.md)
