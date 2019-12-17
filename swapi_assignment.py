import json, requests

ENDPOINT = 'https://swapi.co/api'

int_props = ('height', 'mass', 'rotation_period', 'orbital_period', 'diameter', 'surface_water', 'population', 'average_height', 'average_lifespan', 'max_atmosphering_speed', 'MGLT', 'crew', 'passengers', 'cargo_capacity', 'max_atmosphering_speed', 'crew', 'passengers', 'cargo_capacity', 'system_position', 'natural_satellites')
float_props = ('gravity', 'length', 'width', 'hyperdrive_rating')
list_props = ('hair_color', 'skin_color', 'climate', 'terrain', 'skin_colors', 'hair_colors', 'eye_colors', 'indigenous_life_forms')
dict_props = ('homeworld', 'species')

PERSON_KEYS = ('url', 'name','height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender', 'homeworld', 'species')
PLANET_KEYS = ('url', 'name', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 'terrain', 'surface_water', 'population')
PLANET_KEYS_HOTH = ('url', 'name', 'system_position', 'natural_satellites', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 'terrain', 'surface_water', 'population', 'indigenous_life_forms')
SPECIES_KEYS = ('url', 'name', 'classification', 'designation', 'average_height', 'skin_colors', 'hair_colors', 'eye_colors', 'average_lifespan', 'language')
STARSHIP_KEYS = ('url', 'starship_class', 'name','model', 'manufacturer', 'length','width', 'max_atmosphering_speed', 'hyperdrive_rating', 'MGLT','crew', 'passengers', 'cargo_capacity', 'consumables', 'armament')
VEHICLE_KEYS = ('url', 'vehicle_class', 'name', 'model', 'manufacturer', 'length', 'max_atmosphering_speed', 'crew', 'passengers', 'cargo_capacity', 'consumables', 'armament')

def assign_crew(entity, crew):
    """This function assigns crew members to a starship.

    Parameters:
        entity (dict): the dictionary to add new key-values defined in crew.
        crew (dict): the dictionary containing the new key-value pairs to be added to the entity dictionary.

    Returns:
        dict: dictionary representations of the updated input entity with the key-values defined in crew.
    """
    for key in crew.keys():
        entity[key] = crew[key]
    
    return entity


def clean_data(entity):
    """This function converts dictionary string values to more appropriate types such as float, int,
       list, or, in certain cases, None. Also, retrieves the resource in some cases to add back into the dictionary
       - Converts keys to appropriate types based on globally defined props tuples.
       - all keys defined in int_props tuple are converted to int.
       - all keys defined in float_props tuple are converted to float.
       - all keys defined in list_props tuple are converted to list.
       - all keys defined in dict_props tuple are converted to dictionary (by fetching from swapi).

    Parameters:
        entity (dict): the data to update the key types of.

    Returns:
        dict: the updated version of the input with keys of appropriate types.
    """
    for key in entity.keys():
        if type(entity[key]).__name__ == 'str':
            if is_unknown(entity[key]):
                entity[key] = None

    try: 
        if 'gravity' in entity.keys():
            entity['gravity'] = entity['gravity'].split(' ')[0]
    except:
        entity['gravity'] = entity['gravity']

    for key in entity.keys():
        if key in int_props:
            if type(entity[key]).__name__ == 'str':
                entity[key] = convert_string_to_int(entity[key])
        elif key in float_props:
            if type(entity[key]).__name__ == 'str':
                entity[key] = convert_string_to_float(entity[key])
        elif key in list_props:
            if type(entity[key]).__name__ == 'str':
                entity[key] = convert_string_to_list(entity[key])
        elif key in dict_props:
            if key == 'species':
                response = get_swapi_resource(entity[key][0])
                response = filter_data(response, SPECIES_KEYS)
                entity[key][0] = clean_data(response)
            else:
                response = get_swapi_resource(entity[key])
                response = filter_data(response, PLANET_KEYS)
                entity[key] = clean_data(response)

    return entity


def combine_data(default_data, override_data):
    """This function creates a shallow copy of the default dictionary and then updates the copy with
       key-value pairs from the ‘override’ dictionary.

    Parameters:
        default_data (dict): the default data to be updated.
        override_data (dict): the data used to override and combine with the default data.

    Returns:
        dict: dictionary representations of the combined data.
    """
    result_data = default_data.copy()

    for key in override_data.keys():
        result_data[key] = override_data[key]
    
    return result_data


def convert_string_to_float(value):
    """This function attempts to convert a string to a floating point value.

    Parameters:
        value (str): value to convert to float.

    Returns:
        str: the input value, if it cannot be converted to float.
        float: the float conversion of the input string
    """
    try:
        return float(value)
    except ValueError:
        return value


def convert_string_to_int(value):
    """This function attempts to convert a string to a integer value.

    Parameters:
        value (str): value to convert to int.

    Returns:
        str: the input value, if it cannot be converted to int.
        int: the int conversion of the input string
    """
    try:
        return int(value)
    except ValueError:
        return value


def convert_string_to_list(value, delimiter=','):
    """This function converts a string of delimited text values to a list.

    Parameters:
        value (str): the string to be converted to list.
        delimiter (str): the delimiter to use as the basis for splitting the string

    Returns:
        list: list representations of input string splitted at the delimiter.
    """
    temp = list(value.split(delimiter))
    result = []
    for val in temp:
        val = val.strip()
        result.append(val)
    return result


def filter_data(data, filter_keys):
    """This function applies a key name filter to a dictionary in order to return an ordered subset of
       key-values.

    Parameters:
        data (dict): the data to filter.
        filter_keys (tuple): the keys to filter the data with. The order of the keys in this will define the order of keys in the returned data.

    Returns:
        dict: filtered collection of key-value pairs.
    """
    result = {}

    for key in filter_keys:
        if key in data.keys():
            result[key] = data[key]

    return result


def get_swapi_resource(url, params=None):
    """This function initiates an HTTP GET request to the SWAPI service in order to return a
       representation of a resource

    Parameters:
        url (str): url for the GET request.
        params (dict): parameters for the GET request.

    Returns:
        dict: dictionary representations of the decoded JSON response.
    """
    result = requests.get(url, params).json()
    return result


def is_unknown(value):
    """This function applies a case-insensitive truth value test for string values that equal
       unknown or n/a.

    Parameters:
        value (str): value to check for being unknown or n/a.

    Returns:
        bool: True/False depending on the value of the string (True if its unknown or n/a).
    """
    try: 
        value = value.lower()
        value = value.strip()
        if value == 'unknown' or value == 'n/a':
            return True
        else:
            return False
    except:
        return False


def read_json(filepath):
    """Given a valid filepath reads a JSON document and returns a dictionary.

    Parameters:
        filepath (str): path to file.

    Returns:
        dict: dictionary representations of the decoded JSON document.
    """
    result = json.load(open(filepath, encoding='utf-8'))
    return result


def write_json(filepath, data):
    """Given a valid filepath reads data (JSONable) and writes it to the filepath specified.

    Parameters:
        filepath (str): path to file.
        data (JSONable object): data to store to file

    Returns:
       None
    """
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=True)

def main():
    """Entry point. This program will interact with local file assets and the Star Wars
    API to create two data files required by Rebel Alliance Intelligence.

    - A JSON file comprising a list of likely uninhabited planets where a new rebel base could be
      situated if Imperial forces discover the location of Echo Base.

    - A JSON file of Echo Base information including an evacuation plan of base personnel
      along with passenger assignments for Princess Leia, the communications droid C-3PO aboard
      the transport Bright Hope escorted by two X-wing starfighters piloted by Luke Skywalker
      (with astromech droid R2-D2) and Wedge Antilles (with astromech droid R5-D4).

    Parameters:
        None

    Returns:
        None
    """

    inputFileName = 'swapi_planets-v1p0.json'
    outputFileName = 'swapi_planets_uninhabited-v1p1.json'
    planetList = read_json(inputFileName)
    outputPlanetList = []

    for planet in planetList:
        if is_unknown(planet['population']):
            outputPlanetList.append(clean_data(filter_data(planet, PLANET_KEYS)))
    
    write_json(outputFileName, outputPlanetList)

    inputFileName = 'swapi_echo_base-v1p0.json'
    outputFileName = 'swapi_echo_base-v1p1.json'
    echo_base = read_json(inputFileName)
    
    swapi_planets_url = f"{ENDPOINT}/planets/"
    swapi_hoth = get_swapi_resource(swapi_planets_url, {'search': 'Hoth'})['results'][0]
    echo_base_hoth = echo_base['location']['planet']
    hoth = combine_data(echo_base_hoth, swapi_hoth)
    hoth = filter_data(hoth, PLANET_KEYS_HOTH)
    hoth = clean_data(hoth)
    echo_base['location']['planet'] = hoth


    echo_base_commander = echo_base['garrison']['commander']
    echo_base_commander = clean_data(echo_base_commander)
    echo_base['garrison']['commander'] = echo_base_commander

    dashRendar = echo_base['visiting_starships']['freighters'][1]['pilot']
    dashRendar = clean_data(dashRendar)
    echo_base['visiting_starships']['freighters'][1]['pilot'] = dashRendar

    
    swapi_vehicles_url = f"{ENDPOINT}/vehicles/"
    echo_base_snowspeeder = echo_base['vehicle_assets']['snowspeeders'][0]['type']
    swapi_snowspeeder = get_swapi_resource(swapi_vehicles_url, {'search': 'snowspeeder'})['results'][0]
    snowspeeder = combine_data(echo_base_snowspeeder, swapi_snowspeeder)
    snowspeeder = filter_data(snowspeeder, VEHICLE_KEYS)
    snowspeeder = clean_data(snowspeeder)
    echo_base['vehicle_assets']['snowspeeders'][0]['type'] = snowspeeder


    swapi_starships_url = f"{ENDPOINT}/starships/"

    echo_base_t65_xWing = echo_base['starship_assets']['starfighters'][0]['type']
    swapi_t65_xWing = get_swapi_resource(swapi_starships_url, {'search': 't-65 x-wing'})['results'][0]
    t65_xWing = combine_data(echo_base_t65_xWing, swapi_t65_xWing)
    t65_xWing = filter_data(t65_xWing, STARSHIP_KEYS)
    t65_xWing = clean_data(t65_xWing)
    echo_base['starship_assets']['starfighters'][0]['type'] = t65_xWing

    echo_base_medium = echo_base['starship_assets']['transports'][0]['type']
    swapi_medium = get_swapi_resource(swapi_starships_url, {'search': 'gr-75 medium transport'})['results'][0]
    medium = combine_data(echo_base_medium, swapi_medium)
    medium = filter_data(medium, STARSHIP_KEYS)
    medium = clean_data(medium)
    echo_base['starship_assets']['transports'][0]['type'] = medium

    echo_base_millenium = echo_base['visiting_starships']['freighters'][0]
    swapi_millenium = get_swapi_resource(swapi_starships_url, {'search': 'millennium falcon'})['results'][0]
    millenium = combine_data(echo_base_millenium, swapi_millenium)
    millenium = filter_data(millenium, STARSHIP_KEYS)
    millenium = clean_data(millenium)
    

    swapi_people_url = f"{ENDPOINT}/people/"

    han = get_swapi_resource(swapi_people_url, {'search': 'han solo'})['results'][0]
    han = filter_data(han, PERSON_KEYS)
    han = clean_data(han)

    chewbacca = get_swapi_resource(swapi_people_url, {'search': 'chewbacca'})['results'][0]
    chewbacca = filter_data(chewbacca, PERSON_KEYS)
    chewbacca = clean_data(chewbacca)

    millenium = assign_crew(millenium, {'pilot': han, 'copilot': chewbacca})
    echo_base['visiting_starships']['freighters'][0] = millenium


    evac_plan = echo_base['evacuation_plan']

    echo_base_personnel = echo_base['garrison']['personnel']

    max_base_personnel = 0

    for key in echo_base_personnel.keys():
        max_base_personnel = max_base_personnel + echo_base_personnel[key]
    
    evac_plan['max_base_personnel'] = max_base_personnel

    transportBase = echo_base['starship_assets']['transports'][0]
    max_available_transports = transportBase['num_available']
    transport = transportBase['type']
    passengers = transport['passengers']
    evac_plan['max_available_transports'] = max_available_transports;
    evac_plan['max_passenger_overload_capacity'] = passengers*max_available_transports*evac_plan['passenger_overload_multiplier']


    evac_transport = transport.copy()
    evac_transport['passenger_manifest'] = []
    evac_transport['name'] = 'Bright Hope'

    princess = get_swapi_resource(swapi_people_url, {'search': 'leia organa'})['results'][0]
    princess = filter_data(princess, PERSON_KEYS)
    princess = clean_data(princess)

    c3po = get_swapi_resource(swapi_people_url, {'search': 'c-3po'})['results'][0]
    c3po = filter_data(c3po, PERSON_KEYS)
    c3po = clean_data(c3po)

    evac_transport['passenger_manifest'].append(princess)
    evac_transport['passenger_manifest'].append(c3po)

    evac_transport['escorts'] = []
    luke_x_wing = echo_base['starship_assets']['starfighters'][0]['type'].copy()
    wedge_x_wing = echo_base['starship_assets']['starfighters'][0]['type'].copy()

    luke = get_swapi_resource(swapi_people_url, {'search': 'luke skywalker'})['results'][0]
    luke = filter_data(luke, PERSON_KEYS)
    luke = clean_data(luke)

    r2_d2 = get_swapi_resource(swapi_people_url, {'search': 'R2-D2'})['results'][0]
    r2_d2 = filter_data(r2_d2, PERSON_KEYS)
    r2_d2 = clean_data(r2_d2)

    luke_x_wing = assign_crew(luke_x_wing, {'pilot': luke, 'astromech_droid': r2_d2})
    evac_transport['escorts'].append(luke_x_wing)

    wedge = get_swapi_resource(swapi_people_url, {'search': 'wedge antilles'})['results'][0]
    wedge = filter_data(wedge, PERSON_KEYS)
    wedge = clean_data(wedge)

    r5_d4 = get_swapi_resource(swapi_people_url, {'search': 'R5-D4'})['results'][0]
    r5_d4 = filter_data(r5_d4, PERSON_KEYS)
    r5_d4 = clean_data(r5_d4)

    wedge_x_wing = assign_crew(wedge_x_wing, {'pilot': wedge, 'astromech_droid': r5_d4})
    evac_transport['escorts'].append(wedge_x_wing)
    
    evac_plan['transport_assignments'].append(evac_transport)


    echo_base['evacuation_plan'] = evac_plan
    write_json(outputFileName, echo_base)

if __name__ == '__main__':
    main()