#!/usr/bin/env python

"""
CEP to coordinates (latitude and longitude).

This scripts receives a brazilian postal code and returns the latitude
and longitude coordinates related to this postal code, based on info
provided by Open Street Map.

"""

import sys
import urllib
import json
import pycep_correios
import pandas as pd

def get_name(cep):
    """Get the street name from postal office website."""
    try:
        address = pycep_correios.get_address_from_cep(cep)
    except (ValueError, KeyError, pycep_correios.exceptions.BaseException):
        return False
    return pycep_correios.get_address_from_cep(cep)

def get_json(query, cep):
    """Get the coordinates based on the street name."""
    query_quote = "'" + query + " " + cep + "'"
    query_parse = urllib.parse.quote(query_quote.encode('utf-8'))
    url = "https://nominatim.openstreetmap.org/search?q=" \
        + query_parse + "&format=json"
    try:
        with urllib.request.urlopen(url) as data:
            obj = json.loads(data.read().decode())[0]
    except IndexError:
        if cep == "":
            return False, False
        else:
            return get_json(query, "")
    else:
        return obj['lat'], obj['lon']

def main(filename):
    """Run the main function of script."""
    print("Loading file " + str(filename))
    df = pd.read_excel(filename) # loads excel file
    ceps = df['CEP'].values # get cep values in file
    ids = df['ID'].values # get id values in file
    latloncep, latlon, cepfound, cepnotfound, last = csvthings()
    print("Processing ids (this will only be updated in multiples " \
          + "of 1000)")
    for cep, id in zip(ceps, ids):
        if id <= last: # run the code below from the last cep searched
            continue
        try:
            address = get_name(cep) # try to get query from correios
        except AttributeError:
            print("API limit, preparing to exit")
            break # if something wrong happens then stop searching
        if id % 1000 == 0:
            print("Processing id " + str(id))
        if address: # do the following if cep is found on correios
            query = address['logradouro'] + " " + address['bairro'] \
                    + " " + address['cidade'] + " brasil"
            lat, lon = get_json(query, cep) # try to get coordinates
            if lat: # checks if coordinates were found
                row_cep = {'id': id, 'lat': lat, 'lon': lon, 'cep': cep}
                row = {'id': id, 'lat': lat, 'lon': lon}
                latloncep = latloncep.append(row_cep, ignore_index=True)
                latlon = latlon.append(row, ignore_index=True)
            else: # if coordinates were not found
                address['id'] = id # and append the id
                cepfound = cepfound.append(address, ignore_index=True)
        else: # do the following if cep is not found on correios
            row = {'id': id, 'cep': cep}
            cepnotfound = cepnotfound.append(row, ignore_index=True)
    files = {'latloncep': latloncep, 'latlon': latlon, 'cepfound': cepfound,
             'cepnotfound': cepnotfound} # creates a dict with all dfs
    print("Writing .csv files")
    for name, dt in files.items():  # it was supposed to be df in here
        dt = dt.astype({'id': int}) # but I mistyped :)
        dt.to_csv(str(name) + '.csv', index=False) # write csv file
    print("Done!")

def csvthings():
    """Do things to handle with .csv files."""
    try: # checks if already exists a csv file
        latlon = pd.read_csv('latlon.csv')
    except FileNotFoundError: # if not, creates empty df's
        latloncep = pd.DataFrame({'id': [], 'lat': [], 'lon': [], 'cep': []})
        latlon = pd.DataFrame({'id': [], 'lat': [], 'lon': []})
        cepfound = pd.DataFrame({'bairro': [], 'cep': [], 'cidade': [],
                                 'logradouro': [], 'uf': [],
                                 'complemento': [], 'id': []})
        cepnotfound = pd.DataFrame({'id': [], 'cep': []})
        return latloncep, latlon, cepfound, cepnotfound, 0
    else: # if the file exists, loads df's (or create empty)
        print(".csv file found. Loading")
        try:
            latloncep = pd.read_csv('latloncep.csv')
        except FileNotFoundError:
            latloncep = pd.DataFrame({'id': [], 'lat': [],
                                      'lon': [], 'cep': []})
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
        last = latlon['id'].max()       # search for the last cep
        if cepfound['id'].max() > last: # evaluated in each file 
            last = cepfound['id'].max()
        if cepnotfound['id'].max() > last:
            last = cepnotfound['id'].max()
        return latloncep, latlon, cepfound, cepnotfound, last

if __name__ == "__main__":
    print(__doc__)
    try:
        main(sys.argv[1])
    except IndexError:
        print("You should add a .xlsx file as arg")
