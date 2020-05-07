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

def get_name(cep, first=True):
    """Get the street name from postal office website."""
    if first:
        if pycep_correios.validate_cep(cep) is False:
            return False
        try:
            address = pycep_correios.get_address_from_cep(cep)
        except (ValueError, KeyError, pycep_correios.exceptions.BaseException):
            return False
        return address['logradouro'] + " " + address['bairro'] \
            + " " + address['cidade']
    else:
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
    df = pd.read_excel(filename) # loads excel file
    ceps = df['CEP'].values # get cep values in file
    ids = df['ID'].values # get id values in file
    latloncep = pd.DataFrame({'id': [], 'lat': [], 'lon': [], 'cep': []})
    latlon = pd.DataFrame({'id': [], 'lat': [], 'lon': []})
    cepfound = pd.DataFrame({'bairro': [], 'cep': [], 'cidade': [],
                             'logradouro': [], 'uf': [], 'complemento': [],
                             'id': []})
    cepnotfound = pd.DataFrame({'id': [], 'cep': []})
    for cep, id in zip(ceps, ids):
        try:
            query = get_name(cep) # try to get query from correios
        except AttributeError:
            break # if something wrong happens then stop searching
        if id % 100 == 0:
            print("Processando id " + str(id))
        if query: # do the following if cep is found on correios
            lat, lon = get_json(query, cep)
            if lat:
                row_cep = {'id': id, 'lat': lat, 'lon': lon, 'cep': cep}
                row = {'id': id, 'lat': lat, 'lon': lon}
                latloncep = latloncep.append(row_cep, ignore_index=True)
                latlon = latlon.append(row, ignore_index=True)
            else:
                row = get_name(cep, False)
                row['id'] = id
                cepfound = cepfound.append(row, ignore_index=True)
        else: # do the following if cep is not found on correios
            row = {'id': id, 'cep': cep}
            cepnotfound = cepnotfound.append(row, ignore_index=True)
    files = {'latloncep': latloncep, 'latlon': latlon, 'cepfound': cepfound,
             'cepnotfound': cepnotfound}
    for name, dt in files.items():
        dt = dt.astype({'id': int})
        dt.to_csv(str(name) + '.csv', index=False)

if __name__ == "__main__":
    main(sys.argv[1])
