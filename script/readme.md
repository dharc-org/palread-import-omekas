## Guidelines for the ```omeka_handler.py``` script

### Define the Omeka's configuration parameters:

* Using the argument ```-conf``` followed by the a .json file containing the Omeka's configuration parameters. The configuration file should specify: ```CONTENT_TYPE```, ```KEY_IDENTITY```, ```KEY_CREDENTIALS```, and ```OMEKA_API_URL```. For example:
```
{
    "CONTENT_TYPE": "application/json",
    "KEY_IDENTITY": "MY_IDENTITY",
    "KEY_CREDENTIALS": "MY_CREDENTIALS",
    "OMEKA_API_URL": "MY_OMEKAS_API"
}
```  
To define the configuration parameters of Omeka-S use the following command:
```python3 omeka_handler.py -conf <PATH-TO-CONF-FILE>```

* Define the parameters singularly. Use the arguments: ```-api```, ```-kid```, and ```-kcr```. For example: ```omeka_handler.py -api MYURL -kid MYID -kcr MYCREDENTIALS``` 

* Note, you can combine both the options. In case you want to modify only some specific values. For example:
```omeka_handler.py -conf <PATH-TO-CONF-FILE> -kid MYID```

### The operations
To call an operation use the ```-opr``` argument. Right after ```-opr``` you must specify the operation and its inputs (if any). Here we list all the handled operations:

1. ```get_rsctemp_class```: returns the resource class. It needs the <resource_template_id> as input. E.g. ```python3 omeka_handler.py -conf omeka_conf.json -opr get_rsctemp_class 2```
2. ```get_rsctemp_prop```: returns basic info about the properties in a resource template including: property term, property id, data type. It needs the <resource_template_id> as input. ```python3 omeka_handler.py -conf omeka_conf.json -opr get_rsctemp_prop 2```
3. ```prepare_payload```: creates and returns a skeleton payload for the creation of a new item based on the given resource template. It needs the <resource_template_id> as input. ```python3 omeka_handler.py -conf omeka_conf.json -opr prepare_payload 2```
4. ```get_rsctemp_id```: returns the resource template's id. It needs the <resource_template_name> as input. ```python3 omeka_handler.py -conf omeka_conf.json -opr get_rsctemp_id RSC_TEMP_NAME```
5. ```get_item```: returns an item stored in Omeka-S. It needs the <item_id> and the <template_resource_id> as input. E.g. ```python3 omeka_handler.py -conf omeka_conf.json -opr get_item 62 2```
6. ```add_item```: [TODO]

