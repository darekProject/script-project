#!/usr/bin/python
# Dariusz Skiciak, gr 1

from __future__ import division
import sys
import re
from doctest import debug

from suds.wsse import *
from suds.client import Client

from pip._vendor.distlib.compat import raw_input

toSave = False


def print_request(_pack_info):
    global file
    for key in _pack_info:
        if toSave:
            file = open(key + ".txt", "w", encoding="utf8")
        print('\n ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        if toSave:
            file.write('\n ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('   PRZESYLKA NUMER nr.: ' + str(key))
        if toSave:
            file.write('\n   PRZESYLKA NUMER nr.: ' + str(key))

        events = _pack_info.get(key)[0]
        prop = _pack_info.get(key)[1]

        if prop.get('zakonczono_obsl'):
            print('  \n Status: przesylka dostarczona')
            if toSave:
                file.write(' \n Status: przesylka dostarczona')
        else:
            print('  \n Status: przesylka jeszcze nie dostarczona dostarczona')
            if toSave:
                file.write('  \n Status: przesylka jeszcze nie dostarczona dostarczona')

        ###
        print('\n ----------------------------------------------------------- \n')
        if toSave:
            file.write('\n ----------------------------------------------------------- \n')

        ##
        print(' Opis przesylki:')
        if toSave:
            file.write(' Opis przesylki: \n')

        ##
        print('   -> kraj nadania        : ' + str(prop.get('kraj_nadania')))
        if toSave:
            file.write('   -> kraj nadania        : ' + str(prop.get('kraj_nadania')) + '\n')

        ##
        print('   -> masa                : ' + str(prop.get('masa')))
        if toSave:
            file.write('   -> masa                : ' + str(prop.get('masa')) + '\n')

        ##
        print('   -> rodzaj przesylki    : ' + str(prop.get('rodzaj_przesylki')))
        if toSave:
            file.write('   -> rodzaj przesylki    : ' + str(prop.get('rodzaj_przesylki')) + '\n')

        ##
        if prop.get('urzad_nadania') == 'None':
            print('   -> urzad nadania       : ' + 'Brak')
            if toSave:
                file.write('   -> urzad nadania       : ' + 'Brak \n')
        else:
            print('   -> urzad nadania       : ' + str(prop.get('urzad_nadania')) + '\n')
            if toSave:
                file.write('   -> urzad nadania       : ' + str(prop.get('urzad_nadania')) + '\n')

        ##
        if prop.get('urzad_przezn') == 'None':
            print('   -> urzad przeznaczenia : ' + 'Brak')
            if toSave:
                file.write('   -> urzad przeznaczenia : ' + 'Brak \n')
        else:
            print('   -> urzad przeznaczenia : ' + str(prop.get('urzad_przezn')) + '\n')
            if toSave:
                file.write('   -> urzad przeznaczenia : ' + str(prop.get('urzad_przezn')) + '\n')

        print('\n ----------------------------------------------------------- \n')
        print(' Opis wydarzen:')
        print()
        print('                 START                ')
        print()

        if toSave:
            file.write('\n ----------------------------------------------------------- \n')
            file.write(' Opis wydarzen: \n')
            file.write('\n')
            file.write('                 START                \n')
            file.write('\n')

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

        if toSave:
            for event in events:
                file.write('   -> Nazwa       : ' + str(event.get('nazwa')) + '\n')
                file.write('   -> Urzad       : ' + str(event.get('jednostka')) + '\n')
                file.write('   -> Data i czas : ' + str(event.get('czas')) + '\n')

                file.write('                   ||                 \n')
                file.write('                   ||                 \n')
                file.write('                  \  /                \n')
                file.write('                   \/                 \n')
                file.write('\n')

            if prop.get('zakonczono_obsl'):
                file.write('          PRZESYLKA DOSTRACZONA               \n ')
            else:
                file.write("           PRZESYLKA W DRODZE              \n ")


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

    valuesOfRequest = {}
    for j in range(0, len(_id_pack)):
        data_request = client.service.sprawdzPrzesylke(_id_pack[j])
        if data_request.status != -2:
            valuesOfRequest.update({_id_pack[j]: data_request})
        else:
            print('\n =====================================================')
            print('       Brak przesylki o nr: ' + str(_id_pack[j]))
            print(' =====================================================')
    if len(valuesOfRequest) != 0:
        response_parser(valuesOfRequest)
    else:
        sys.exit(1)


def help_print():
    print()
    print(' ################      DOKUMENTACJA       ################\n')
    print()
    print(
        '   Glowne zalozenie skryptu to spradzenie statusu przesylki lub listu\n'
        '   wyslanego za pomoca poczty polskiej. Skrypt przedstawia rowniez\n'
        '   informacje o przesylce oraz o drodze jak przedbyla\n'
        '   lub gdzie alkualnie jest jesli jeszcze nie dotarla.')
    print()
    print('   Skrypt dziala w ten sposob ze odpytuje API udostepnione\n'
          '   przez poczte polska o informacje na temat danej paczki. \n'
          '   Do API przekazywany jest unikatowy numer przesylki.')
    print()
    print('   Skrypt uruchamia sie bez zadnych paramaterow. Program zapyta najpierw\n'
          '   o liczbe przesylek, ktora uzytkownik chce sprawdzic. Kolejny krok to\n'
          '   podanie numerow id paczek. Program umozliwa tez zapisanie inforamcji\n'
          '   przeslanych przez API do pliku jest to opcjonalne. Jezeli uzytkownik\n'
          '   n wyrazi chcec zapisania informacji do pliku to wowacz dla kazdej\n'
          '   przesylki wygeneruje sie plik z informacjami.')
    print()
    print('   Przykladowe numery do sprawdzenia w skrypcie: ')
    print('      -> 00959007731943615153')
    print('      -> 00959007731940566823')
    print()



arg = len(sys.argv) - 1
if arg > 0:
    if sys.argv[arg] == '-h' or sys.argv[arg] == '--help':
        help_print()
        sys.exit(0)

print('\n =====================================================')
print('          API POCZTA! - SPRAWDZ LIST/PACZKE           ')
print(' =====================================================')

tmpBoolean = True
tmpValue = raw_input('\n Podaj liczbę paczek/listow, ktore chcesz sprawdzic: ')
amount_pack = 0
while tmpBoolean:
    if len(tmpValue) == 0:
        tmpValue = raw_input('\n Podaj liczbę paczek/listow, ktore chcesz sprawdzic: ')
    elif not re.match(r'^[0-9]*$', tmpValue):
        tmpValue = raw_input('\n Podaj liczbę paczek/listow, ktore chcesz sprawdzic: ')
    else:
        amount_pack = int(tmpValue)
        tmpBoolean = False

if amount_pack == 0:
    print(" \n Podales ze chesz sprawdzic 0 paczek! Program zakonczyl dzialanie")
    sys.exit(1)

id_pack = []

for i in range(0, amount_pack):
    tmpValue = raw_input("\n Podaj id paczki/listu nr " + str(i + 1) + ': ').strip()
    tmpBoolean = True
    while tmpBoolean:
        if len(tmpValue) == 0:
            tmpValue = raw_input("\n Podaj id paczki/listu nr " + str(i + 1) + ': ').strip()
        elif not re.match(r'^[0-9]*$', tmpValue):
            tmpValue = raw_input("\n Podaj id paczki/listu nr " + str(i + 1) + ': ').strip()
        else:
            tmpBoolean = False
    id_pack.append(tmpValue)

print(id_pack)

tmpValueFile = raw_input("\n Czy chcesz zapisać dane na temat paczki do pliku[Y/N]: ").lower()
tmpBoolean = True
while tmpBoolean:
    if len(tmpValueFile) == 0 and (tmpValueFile == 'y' or tmpValueFile == 'n'):
        tmpValueFile = raw_input("\n Czy chcesz zapisać dane na temat paczki do pliku[Y/N]: ").lower()
    else:
        tmpBoolean = False

if tmpValueFile == 'y':
    toSave = True
request(id_pack)

print('\n =====================================================')
print('       API POCZTA! - SPRAWDZ LIST/PACZKE WYLACZONE      ')
print(' =====================================================')
