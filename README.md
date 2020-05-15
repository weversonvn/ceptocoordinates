# CEP to coordinates (latitude and longitude)

## Description

This script receives a list of brazilian postal codes and returns the latitude and longitude coordinates related to each postal code, based on information provided by Open Street Map (OSM). If no latitude and longitude data were found then it stores data for further manual searching.

## Requirements

* [pycep_correios](https://pycep-correios.readthedocs.io/pt/develop/)
* [Pandas](https://pandas.pydata.org/)
* [tqdm](https://tqdm.github.io/)

Requirements can be easily installed using [**requirements.txt**](requirements.txt) file.

## Usage

You should simple run `ceptocoordinates.py` file parsing a _.xlsx_ file as argument. The _.xlsx_ must contain a column named **CEP**, with CEP values, and a column named **ID**, with ID values related to CEP. Column names are case sensitive. It's recommended to name the **.xlsx** file only with uncapitalized letters, without spaces or special characters (see **.csv** files style), because this might deny file loading as the code don't handle complex filenames. Data will be saved on three **.csv** files:

* **latloncep.csv**: the main data file, it will store latitude and longitude values. It has the columns **id**, **lat**, **lon** and **cep**
* **cepfound.csv**: this file stores venue information from CEPs that were found on post office system, but latitude and longitude values couldn't be found by this code. It's useful for manual search. It has the columns **bairro**, **cep**, **cidade**, **logradouro**, **uf**, **complemento** and **id**
* **cepnotfound.csv**: this file stores CEPs that couldn't be found on postal office system, probably due to mistyping or missing characters on CEP value. It has the columns **id** and **cep**

### Note

Due to API limitation while using **pycep_correios** lib the values in **.xlsx** file may not be processed in just one running of the code, and more than one run will be necessary (actually, if the list is big then probably it will take lots of runnings). In this case, data will be stored in **.csv** files, and these files will be loaded on the next execution of the code (assuming they still are on the same folder of the code), so the code can run starting from where it stopped on the last running.

## License

MIT License

Copyright (c) 2020 Weverson Nascimento

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
