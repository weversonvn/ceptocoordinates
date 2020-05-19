#!/usr/bin/env python

"""
CEP to coordinates (latitude and longitude).

This script receives list of brazilian postal code and returns the
latitude and longitude coordinates related to this postal code, based
on information provided by Open Street Map (OSM).

"""

import sys # basic system library
import urllib # to open urls
import json # to get lat and lon from open street map
import logging # to record log events
# log config is because pycep_correios generates a config and it
# couldn't be overwritten later before python 3.8
logging.basicConfig(filename='exec.log', level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%b %d %H:%M:%S')
import pycep_correios # to get venue from correios
import pandas as pd # to handle with data
from tqdm import tqdm # te quiero demasiado <3 (shows progress bar)

def get_name(cep):
    """Get the street name from postal office website."""
    try:
        address = pycep_correios.get_address_from_cep(cep)
    except (ValueError, KeyError, pycep_correios.exceptions.BaseException):
        return False
    return pycep_correios.get_address_from_cep(cep)

def get_json(query, cep):
    """Get the coordinates based on the street name."""
    query_quote = "'" + query + " " + cep + "'" # to search on OSM
    query_parse = urllib.parse.quote(
        query_quote.encode('utf-8')) # convert non-url characters
    url = "https://nominatim.openstreetmap.org/search?q=" \
        + query_parse + "&format=json" # url to get lat lon data
    try: # nominatim returns a json, the first data is stored
        with urllib.request.urlopen(url) as data:
            obj = json.loads(data.read().decode())[0]
    except IndexError: # if there is no data
        if cep == "": # if already tried twice
            return False, False # return false so no latlon were got
        else: # if its second time then search again without cep value
            return get_json(query, "")
    else: # if everything's ok then returns latlon values
        return obj['lat'], obj['lon']

def main(filename):
    """Run the main function of script."""
    logging.info(f"Loading file {filename}")
    df = pd.read_excel(filename) # loads excel file
    ceps = df['CEP'].values # get cep values in file
    ids = df['ID'].values # get id values in file
    latloncep, cepfound, cepnotfound, last, lastdf = csvthings()
    logging.debug(f"Last ID evaluated: {last}")
    for cep, id in zip(ceps, tqdm(ids)):
        if id <= last: # run the code below from the last cep searched
            continue
        lastcep = ceps[id-2] # stores last cep evaluated
        if cep == lastcep: # if it's same cep again it just copys it
            if lastdf == 'latloncep':
                latloncep = copy_row(latloncep, id)
            elif lastdf == 'cepfound':
                cepfound = copy_row(cepfound, id)
            else:
                cepnotfound = copy_row(cepnotfound, id)
            continue

        try: # here starts the real search
            address = get_name(cep) # try to get query from correios
        except AttributeError:
            logging.error("API limit, preparing to exit")
            logging.debug(f"IDs processed: {id-last-1}")
            break # if something wrong happens then stop searching
        if address: # do the following if cep is found on correios
            query = address['logradouro'] + " " + address['bairro'] \
                    + " " + address['cidade'] + " brasil"
            lat, lon = get_json(query, cep) # try to get coordinates
            if lat: # checks if coordinates were found
                row = {'id': id, 'lat': lat, 'lon': lon, 'cep': cep}
                latloncep = latloncep.append(row, ignore_index=True)
                lastdf = 'latloncep'
            else: # if coordinates were not found
                address['id'] = id # and append the id
                cepfound = cepfound.append(address, ignore_index=True)
                lastdf = 'cepfound'
        else: # do the following if cep is not found on correios
            row = {'id': id, 'cep': cep}
            cepnotfound = cepnotfound.append(row, ignore_index=True)
            lastdf = 'cepnotfound'

    files = {'latloncep': latloncep, 'cepfound': cepfound,
             'cepnotfound': cepnotfound} # creates a dict with all dfs
    logging.info("Writing .csv files")
    for name, dt in files.items():  # it was supposed to be df in here
        dt = dt.astype({'id': int}) # but I mistyped :)
        dt.to_csv(str(name) + '.csv', index=False) # write csv file
    logging.info("Done!")

def csvthings():
    """Do things to handle with .csv files."""
    try: # checks if already exists a csv file
        latloncep = pd.read_csv('latloncep.csv')
    except FileNotFoundError: # if not, creates empty df's
        latloncep = pd.DataFrame({'id': [], 'lat': [], 'lon': [], 'cep': []})
        cepfound = pd.DataFrame({'bairro': [], 'cep': [], 'cidade': [],
                                 'logradouro': [], 'uf': [],
                                 'complemento': [], 'id': []})
        cepnotfound = pd.DataFrame({'id': [], 'cep': []})
        lastdf = 'latloncep'
        return latloncep, cepfound, cepnotfound, 0, lastdf
    else: # if the file exists, loads df's (or create empty)
        logging.info("File latloncep.csv found. Loading others")
        try:
            cepfound = pd.read_csv('cepfound.csv')
        except FileNotFoundError:
            cepfound = pd.DataFrame({'bairro': [], 'cep': [], 'cidade': [],
                                     'logradouro': [], 'uf': [],
                                     'complemento': [], 'id': []})
        try:
            cepnotfound = pd.read_csv('cepnotfound.csv')
        except FileNotFoundError:
            cepnotfound = pd.DataFrame({'id': [], 'cep': []})
        last = latloncep['id'].max()       # search for the last cep
        lastdf = 'latloncep'
        if cepfound['id'].max() > last: # evaluated in each file 
            last = cepfound['id'].max()
            lastdf = 'cepfound'
        if cepnotfound['id'].max() > last:
            last = cepnotfound['id'].max()
            lastdf = 'cepfound'
        return latloncep, cepfound, cepnotfound, last, lastdf

def copy_row(df, id):
    """Copies the last row of df and writes it again."""
    row = df.loc[[df['id'].idxmax()]]
    row['id'] = id
    return df.append(row, ignore_index=True)

if __name__ == "__main__":
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    print(__doc__)
    logging.info('Starting')
    try:
        main(sys.argv[1])
    except IndexError:
        logging.ERROR("A .xlsx file wasn't parsed as an argument")
        logging.INFO("You should add a .xlsx file as an argument")
