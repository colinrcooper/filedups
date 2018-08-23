# FileDups

A python script to provide a highly-customizable way to scan one or more folders for duplicate files.

## Getting Started

* Create a folder c:\filedups
* Copy find_dups.py to c:\filedups
* Copy sample-config.txt to c:\filedups
* Copy sample-exclude-filters to c:\filedups
* Copy sample-include-filters to c:\filedups

If you use a different folder name than c:\filedups then you will need to edit and change the FilterFile setting in the [General] section of sample-config.txt if you plan to use a configuration file for your scan settings.

### Prerequisites

This software was built and tested with Python 3.6.

### Installing

See "Getting Started"

## Running the tests

To run automated units tests, you will need to copy the unittests folder and all subfolders to c:\filedups.

If you use a different folder, then you will need to edit the rootdir variablle in \unittests\myunittest_settings.py.

To run the unit tests, run python from a command line as follows:

```
python c:\filedups\unittests\myunittest.py
```

## Deployment

See Getting Started and Prerequisites

## Usage

```
find_dups.py [-h] [-cfg CONFIGFILE] [-fm {INCLUDE,EXCLUDE,NONE}]
                [-ff FILTERFILE] [-s {TRUE,FALSE}] [-ms MAXFILESIZE]
                [-emp {TRUE,FALSE}] [-bs BLOCKSIZE] [-ha HASHALGORITHM]
                -dirs DIRECTORIES [DIRECTORIES ...]
                    
optional arguments:
  -h, --help            show this help message and exit
  -cfg CONFIGFILE, --configFile CONFIGFILE
                        Configuration File for script
  -fm {INCLUDE,EXCLUDE,NONE}, --filterMode {INCLUDE,EXCLUDE,NONE}
                        Filter Mode
  -ff FILTERFILE, --filterFile FILTERFILE
                        File containing list of filters to be applied if Filter Mode in not NONE
  -s {TRUE,FALSE}, --subDirs {TRUE,FALSE}
                        Scan subdirectories of selected folders?
  -ms MAXFILESIZE, --maxFileSize MAXFILESIZE
                        Maximum size of files to be scanned
  -emp {TRUE,FALSE}, --includeEmptyFiles {TRUE,FALSE}
                        Include files with no content in results?
  -bs BLOCKSIZE, --blocksize BLOCKSIZE
                        Blocksize for file reads
  -ha HASHALGORITHM, --hashAlgorithm HASHALGORITHM
                        Algorithm(s) to be used for file hashing
  -dirs DIRECTORIES [DIRECTORIES ...], --directories DIRECTORIES [DIRECTORIES ...]
```
  
  Values supplied through the commandline take precedence over values supplied in a config file.

## Authors

* **Colin Cooper** - *Initial work* - [ColinRCooper](https://github.com/colinrcooper)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Hat tip to Andres Torres @ https://www.pythoncentral.io/finding-duplicate-files-with-python/ for the initial code.

