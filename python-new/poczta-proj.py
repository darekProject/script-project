#!/usr/bin/python
# Dariusz Skiciak, gr 1

from __future__ import division
import sys
from doctest import debug

from suds.wsse import *
from suds.client import Client
from termcolor import colored

from pip._vendor.distlib.compat import raw_input

print('\n =====================================================')
print('          API POCZTA! - SPRAWDZ LIST/PACZKE           ')
print(' =====================================================')


def print_request(_pack_info):
    print(_pack_info)
    for key in _pack_info:
        print('\n ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('   PRZESYLKA NUMER nr.: ' + str(key))

        events = _pack_info.get(key)[0]
        prop = _pack_info.get(key)[1]

        if prop.get('zakonczono_obsl'):
            print('  \n Status: przesylka dostarczona')
        else:
            print('  \n Status: przesylka jeszcze nie dostarczona dostarczona')

        print('\n ----------------------------------------------------------- \n')
        print(' Opis przesylki:')
        print('   -> kraj nadania        : ' + str(prop.get('kraj_nadania')))
        print('   -> masa                : ' + str(prop.get('masa')))
        print('   -> rodzaj przesylki    : ' + str(prop.get('rodzaj_przesylki')))
        if prop.get('urzad_nadania') == 'None':
            print('   -> urzad nadania       : ' + 'Brak')
        else:
            print('   -> urzad nadania       : ' + str(prop.get('urzad_nadania')))
        if prop.get('urzad_przezn') == 'None':
            print('   -> urzad przeznaczenia : ' + 'Brak')
        else:
            print('   -> urzad przeznaczenia : ' + str(prop.get('urzad_przezn')))

        print('\n ----------------------------------------------------------- \n')
        print(' Opis wydarzen:')
        print()
        print('                 START                ')
        print()
        for event in events:
            print('   -> Nazwa       : ' + str(event.get('nazwa')))
            print('   -> Urzad       : ' + str(event.get('jednostka')))
            print('   -> Data i czas : ' + str(event.get('czas')))

            print('                   ||                 ')
            print('                   ||                 ')
            print('                  \  /                ')
            print('                   \/                 ')
            print()

        if prop.get('zakonczono_obsl'):
            print('          PRZESYLKA DOSTRACZONA               \n ')
        else:
            print("           PRZESYLKA W DRODZE              \n ")


def response_parser(value_of_request):
    pack_info = {}

    for key in value_of_request:
        events = []
        data_pack = {}
        for value in value_of_request.get(key).danePrzesylki.zdarzenia.zdarzenie:
            events.append({'czas': value.czas, 'jednostka': value.jednostka.nazwa, 'nazwa': value.nazwa})
        prop = value_of_request.get(key).danePrzesylki
        data_pack.update({
            'kraj_nadania': prop.krajNadania,
            'masa': prop.masa,
            'rodzaj_przesylki': prop.rodzPrzes,
            'urzad_nadania': prop.urzadNadania.nazwa,
            'urzad_przezn': prop.urzadPrzezn.nazwa,
            'zakonczono_obsl': prop.zakonczonoObsluge
        })
        pack_info.update({
            key: [events, data_pack]
        })
    print_request(pack_info)


def request(_id_pack):
    url = 'https://tt.poczta-polska.pl/Sledzenie/services/Sledzenie?wsdl'
    client = Client(url)
    security = Security()
    token = UsernameToken('sledzeniepp', 'PPSA')
    security.tokens.append(token)
    client.set_options(wsse=security)

    try:
        valuesOfRequest = {}
        for j in range(0, len(_id_pack)):
            data_request = client.service.sprawdzPrzesylke(_id_pack[j])
            valuesOfRequest.update({_id_pack[j]: data_request})
        response_parser(valuesOfRequest)
    except AttributeError as e:
        print('\n =====================================================')
        print('       Brak przesylki o nr: ' + str(_id_pack) + str(e))
        print(' =====================================================')


tmpBoolean = True
tmpValue = raw_input('\n Podaj liczbę paczek/listow, ktore chcesz sprawdzic: ')
amount_pack = 0
while tmpBoolean:
    if len(tmpValue) == 0:
        tmpValue = raw_input("\n Podaj paczke/list nr " + str(i + 1) + ': ')
    else:
        amount_pack = int(tmpValue)
        tmpBoolean = False

if amount_pack == 0:
    print(" \n Podales ze chesz sprawdzic 0 paczek! Program zakonczyl dzialanie")
    sys.exit(1)

id_pack = []

for i in range(0, amount_pack):
    tmpValue = raw_input("\n Podaj paczke/list nr " + str(i + 1) + ': ')
    tmpBoolean = True
    while tmpBoolean:
        if len(tmpValue) == 0:
            tmpValue = raw_input("\n Podaj paczke/list nr " + str(i + 1) + ': ')
        else:
            tmpBoolean = False
    id_pack.append(tmpValue)

request(id_pack)

print('\n =====================================================')
print('       API POCZTA! - SPRAWDZ LIST/PACZKE WYLACZONE      ')
print(' =====================================================')
