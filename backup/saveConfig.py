import configparser
import os

def saveConfig(section,field,data,filename):
    try:
        config = configparser.ConfigParser()
        config.read(filename)
        config[section][field] = data
        with open(filename, 'w') as filedata:
            config.write(filedata)
    except KeyError:
        config = configparser.ConfigParser()
        config.read(filename)
        config.add_section(section)
        config[section][field] = data
        with open(filename, 'w') as filedata:
            config.write(filedata)

def readConfig(block,field,filename):
    try:
        config = configparser.ConfigParser()
        config.read(filename)
        return config[block][field]
    except KeyError:
        return ''
    


saveConfig('test1111','id48','444444','config.ini')


# print(readConfig('notify','id','config.ini'))