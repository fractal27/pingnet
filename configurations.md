## Configurations

You can setup configurations really easily, you simply edit the config.ini file in the sources

here are the parameters:

>NOTE: * is a symbol to represent to insert any number the number of the same network *MUST* be equal



> `networks.*.ip`

    used for setting the base ip, without the last section (e.g. `networks.1.ip=172.107.225.` will scan from `172.107.225.<from>` to `172.107.225.<to>`)

> `networks.*.name`

    used to give a description to a particular network
> `networks.*.to`

    parameter to give the end ip of the scan (e.g. `networks.1.to=0;networks.1.ip=172.107.225;networks.1.to=50` will scan from ip `172.107.225.0` to `172.107.225.50`)

> `networks.*.from`

    parameter to give the start ip of the scan (e.g. `networks.1.to=0;networks.1.ip=172.107.225;networks.1.to=50` will scan from ip `172.107.225.0` to `172.107.225.50`)

> `times.path`

    parameter to specify the path where the resultant files from the `times scan` will go

> `webmode.date_format`

    specify the date format to use in the webfile

> `webmode.prettify`

    1 if you want to prettify the content of the webpage, else 0
    NOTE:the value must be integer
