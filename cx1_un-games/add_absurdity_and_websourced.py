#!/usr/bin/env python3
"""
Add computed absurdity features + web-sourced bizarre data.
Part 1: Scrabble scores, flag data, calling codes, capital city features, etc.
Part 2: Nobel prizes, nuclear reactors, passport power, average height, etc.
"""

import pandas as pd
import numpy as np
import pycountry
import re

print("=" * 80)
print("ADDING ABSURDITY + WEB-SOURCED FEATURES")
print("=" * 80)

df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook_df = pd.read_csv('codebook.csv')
print(f"Starting: {df.shape[0]} countries × {df.shape[1]} features")

def add_to_codebook(column_name, description, source, role='bizarre'):
    global codebook_df
    if column_name not in codebook_df['column_name'].values:
        new_row = pd.DataFrame({
            'column_name': [column_name],
            'description': [description],
            'source': [source],
            'role': [role]
        })
        codebook_df = pd.concat([codebook_df, new_row], ignore_index=True)

# Build name-to-ISO3 / ISO2 mappings
name_to_iso3 = {country.name: country.alpha_3 for country in pycountry.countries}
wb_mappings = {
    'United States': 'USA', 'United Kingdom': 'GBR', 'Czechia': 'CZE',
    'Korea, Rep.': 'KOR', 'Russian Federation': 'RUS', 'Iran, Islamic Rep.': 'IRN',
    'Egypt, Arab Rep.': 'EGY', 'Venezuela, RB': 'VEN', 'Turkiye': 'TUR',
    'Slovak Republic': 'SVK', 'Congo, Dem. Rep.': 'COD', 'Congo, Rep.': 'COG',
    'Lao PDR': 'LAO', 'Kyrgyz Republic': 'KGZ', 'Cabo Verde': 'CPV',
    "Cote d'Ivoire": 'CIV', 'Gambia, The': 'GMB', 'Bahamas, The': 'BHS',
    'Micronesia, Fed. Sts.': 'FSM', 'St. Lucia': 'LCA',
    'St. Vincent and the Grenadines': 'VCT', 'St. Kitts and Nevis': 'KNA',
    'Yemen, Rep.': 'YEM', 'Syria': 'SYR', 'North Macedonia': 'MKD',
    'Eswatini': 'SWZ', 'Brunei Darussalam': 'BRN', 'West Bank and Gaza': 'PSE',
    'Timor-Leste': 'TLS',
}
name_to_iso3.update(wb_mappings)

# ============================================================================
# PART 1: COMPUTED ABSURDITY FEATURES
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: COMPUTED ABSURDITY FEATURES")
print("=" * 80)

# --- Scrabble score of country name ---
SCRABBLE_SCORES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4,
    'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3,
    'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
    'y': 4, 'z': 10
}

def scrabble_score(name):
    return sum(SCRABBLE_SCORES.get(c.lower(), 0) for c in name if c.isalpha())

df['scrabble_score_country_name'] = df.index.map(scrabble_score)
add_to_codebook('scrabble_score_country_name',
                'Scrabble score of country name (English letter values)',
                'Derived from country name')

# --- Letters shared with "United States" ---
def letters_shared_with(name, reference='unitedstates'):
    ref_set = set(reference.lower())
    name_clean = set(c.lower() for c in name if c.isalpha())
    return len(name_clean & ref_set)

df['letters_shared_with_usa'] = df.index.map(lambda x: letters_shared_with(x, 'unitedstates'))
add_to_codebook('letters_shared_with_usa',
                'Number of unique letters shared with "United States"',
                'Derived from country name')

# --- Letters shared with "Switzerland" ---
df['letters_shared_with_switzerland'] = df.index.map(lambda x: letters_shared_with(x, 'switzerland'))
add_to_codebook('letters_shared_with_switzerland',
                'Number of unique letters shared with "Switzerland"',
                'Derived from country name')

# --- Name is a Fibonacci number of letters? ---
def fib_alignment(name):
    n = sum(1 for c in name if c.isalpha())
    fibs = [1, 2, 3, 5, 8, 13, 21, 34]
    return min(abs(n - f) for f in fibs)  # Distance to nearest Fibonacci

df['fibonacci_name_distance'] = df.index.map(fib_alignment)
add_to_codebook('fibonacci_name_distance',
                'Distance of letter count to nearest Fibonacci number',
                'Derived from country name (pseudoscience)')

# --- Is letter count prime? Distance to nearest prime ---
def prime_distance(name):
    n = sum(1 for c in name if c.isalpha())
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    return min(abs(n - p) for p in primes)

df['prime_name_distance'] = df.index.map(prime_distance)
add_to_codebook('prime_name_distance',
                'Distance of letter count to nearest prime number',
                'Derived from country name (pseudoscience)')

# --- Golden ratio alignment (vowels/consonants vs 0.618) ---
def golden_ratio_distance(name):
    vowels = sum(1 for c in name.lower() if c in 'aeiou')
    consonants = sum(1 for c in name.lower() if c.isalpha() and c not in 'aeiou')
    if consonants == 0:
        return 1.0
    ratio = vowels / consonants
    return round(abs(ratio - 0.618), 4)

df['golden_ratio_name_distance'] = df.index.map(golden_ratio_distance)
add_to_codebook('golden_ratio_name_distance',
                'Distance of vowel/consonant ratio to golden ratio (0.618)',
                'Derived from country name (pseudoscience)')

# --- Country name reversed alphabetical rank ---
df['reverse_alphabetical_rank'] = 255 - df.index.to_series().rank(method='min').astype(int)
add_to_codebook('reverse_alphabetical_rank',
                'Reverse alphabetical ranking (254=first alphabetically, 1=last)',
                'Derived from country name')

# --- Double letter count (consecutive repeated letters like "oo", "ss") ---
def count_double_letters(name):
    name = name.lower()
    count = 0
    for i in range(len(name) - 1):
        if name[i].isalpha() and name[i] == name[i+1]:
            count += 1
    return count

df['double_letter_count'] = df.index.map(count_double_letters)
add_to_codebook('double_letter_count',
                'Number of consecutive double letters (e.g., "oo" in Cameroon)',
                'Derived from country name')

# --- Alternating vowel-consonant score (how "rhythmic" is the name) ---
def alternating_score(name):
    name = ''.join(c.lower() for c in name if c.isalpha())
    if len(name) <= 1:
        return 0
    alternations = 0
    for i in range(len(name) - 1):
        c1_vowel = name[i] in 'aeiou'
        c2_vowel = name[i+1] in 'aeiou'
        if c1_vowel != c2_vowel:
            alternations += 1
    return round(alternations / (len(name) - 1), 4)

df['name_rhythmic_score'] = df.index.map(alternating_score)
add_to_codebook('name_rhythmic_score',
                'Fraction of consecutive letter pairs that alternate vowel/consonant',
                'Derived from country name')

print(f"  ✓ Added 9 computed name-based absurdity features")

# --- ISO numeric code ---
iso_numeric = {}
for country in pycountry.countries:
    if hasattr(country, 'numeric'):
        iso_numeric[country.alpha_3] = int(country.numeric)

df['iso_numeric_code'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in iso_numeric:
        df.loc[name, 'iso_numeric_code'] = iso_numeric[iso3]
add_to_codebook('iso_numeric_code',
                'ISO 3166-1 numeric country code (arbitrary number assigned by ISO)',
                'ISO 3166-1')

# --- Country calling code ---
calling_codes = {
    'USA': 1, 'CAN': 1, 'GBR': 44, 'FRA': 33, 'DEU': 49, 'ITA': 39, 'ESP': 34,
    'RUS': 7, 'CHN': 86, 'JPN': 81, 'KOR': 82, 'IND': 91, 'BRA': 55, 'MEX': 52,
    'ARG': 54, 'AUS': 61, 'NZL': 64, 'ZAF': 27, 'NGA': 234, 'EGY': 20,
    'SAU': 966, 'ARE': 971, 'ISR': 972, 'TUR': 90, 'IRN': 98, 'PAK': 92,
    'BGD': 880, 'IDN': 62, 'MYS': 60, 'THA': 66, 'VNM': 84, 'PHL': 63,
    'SGP': 65, 'TWN': 886, 'HKG': 852, 'COL': 57, 'PER': 51, 'CHL': 56,
    'VEN': 58, 'ECU': 593, 'BOL': 591, 'PRY': 595, 'URY': 598, 'GUY': 592,
    'SUR': 597, 'SWE': 46, 'NOR': 47, 'FIN': 358, 'DNK': 45, 'ISL': 354,
    'IRL': 353, 'PRT': 351, 'NLD': 31, 'BEL': 32, 'CHE': 41, 'AUT': 43,
    'POL': 48, 'CZE': 420, 'SVK': 421, 'HUN': 36, 'ROU': 40, 'BGR': 359,
    'HRV': 385, 'SVN': 386, 'SRB': 381, 'BIH': 387, 'MNE': 382, 'MKD': 389,
    'ALB': 355, 'GRC': 30, 'CYP': 357, 'MLT': 356, 'EST': 372, 'LVA': 371,
    'LTU': 370, 'BLR': 375, 'UKR': 380, 'MDA': 373, 'GEO': 995, 'ARM': 374,
    'AZE': 994, 'KAZ': 7, 'UZB': 998, 'TKM': 993, 'TJK': 992, 'KGZ': 996,
    'AFG': 93, 'IRQ': 964, 'SYR': 963, 'JOR': 962, 'LBN': 961, 'KWT': 965,
    'BHR': 973, 'QAT': 974, 'OMN': 968, 'YEM': 967, 'LBY': 218, 'TUN': 216,
    'DZA': 213, 'MAR': 212, 'MRT': 222, 'MLI': 223, 'BFA': 226, 'NER': 227,
    'TCD': 235, 'SDN': 249, 'SSD': 211, 'ETH': 251, 'ERI': 291, 'DJI': 253,
    'SOM': 252, 'KEN': 254, 'UGA': 256, 'TZA': 255, 'RWA': 250, 'BDI': 257,
    'COD': 243, 'COG': 242, 'GAB': 241, 'CMR': 237, 'CAF': 236, 'GNQ': 240,
    'STP': 239, 'AGO': 244, 'MOZ': 258, 'ZMB': 260, 'ZWE': 263, 'BWA': 267,
    'NAM': 264, 'SWZ': 268, 'LSO': 266, 'MWI': 265, 'MDG': 261, 'MUS': 230,
    'COM': 269, 'SYC': 248, 'GHA': 233, 'CIV': 225, 'SEN': 221, 'GMB': 220,
    'GNB': 245, 'GIN': 224, 'SLE': 232, 'LBR': 231, 'TGO': 228, 'BEN': 229,
    'CPV': 238, 'JAM': 876, 'TTO': 868, 'BRB': 246, 'BHS': 242, 'HTI': 509,
    'DOM': 809, 'CUB': 53, 'CRI': 506, 'PAN': 507, 'GTM': 502, 'HND': 504,
    'SLV': 503, 'NIC': 505, 'BLZ': 501, 'MNG': 976, 'PRK': 850, 'NPL': 977,
    'BTN': 975, 'LKA': 94, 'MDV': 960, 'MMR': 95, 'KHM': 855, 'LAO': 856,
    'BRN': 673, 'PNG': 675, 'FJI': 679, 'SLB': 677, 'VUT': 678, 'WSM': 685,
    'TON': 676, 'FSM': 691, 'MHL': 692, 'PLW': 680, 'KIR': 686, 'NRU': 674,
    'TUV': 688, 'TLS': 670, 'LCA': 758, 'VCT': 784, 'KNA': 869,
    'ATG': 268, 'DMA': 767, 'GRD': 473, 'GNQ': 240,
}

df['country_calling_code'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in calling_codes:
        df.loc[name, 'country_calling_code'] = calling_codes[iso3]
add_to_codebook('country_calling_code',
                'International telephone calling code (e.g., +1 for USA, +44 for UK)',
                'ITU')

print(f"  ✓ Added ISO numeric code and calling code")

# --- Capital city features ---
capitals = {
    'USA': 'Washington', 'GBR': 'London', 'FRA': 'Paris', 'DEU': 'Berlin',
    'ITA': 'Rome', 'ESP': 'Madrid', 'RUS': 'Moscow', 'CHN': 'Beijing',
    'JPN': 'Tokyo', 'KOR': 'Seoul', 'IND': 'New Delhi', 'BRA': 'Brasilia',
    'MEX': 'Mexico City', 'ARG': 'Buenos Aires', 'AUS': 'Canberra',
    'NZL': 'Wellington', 'ZAF': 'Pretoria', 'NGA': 'Abuja', 'EGY': 'Cairo',
    'SAU': 'Riyadh', 'ARE': 'Abu Dhabi', 'ISR': 'Jerusalem', 'TUR': 'Ankara',
    'IRN': 'Tehran', 'PAK': 'Islamabad', 'BGD': 'Dhaka', 'IDN': 'Jakarta',
    'MYS': 'Kuala Lumpur', 'THA': 'Bangkok', 'VNM': 'Hanoi', 'PHL': 'Manila',
    'SGP': 'Singapore', 'COL': 'Bogota', 'PER': 'Lima', 'CHL': 'Santiago',
    'VEN': 'Caracas', 'ECU': 'Quito', 'BOL': 'La Paz', 'PRY': 'Asuncion',
    'URY': 'Montevideo', 'GUY': 'Georgetown', 'SUR': 'Paramaribo',
    'SWE': 'Stockholm', 'NOR': 'Oslo', 'FIN': 'Helsinki', 'DNK': 'Copenhagen',
    'ISL': 'Reykjavik', 'IRL': 'Dublin', 'PRT': 'Lisbon', 'NLD': 'Amsterdam',
    'BEL': 'Brussels', 'CHE': 'Bern', 'AUT': 'Vienna', 'POL': 'Warsaw',
    'CZE': 'Prague', 'SVK': 'Bratislava', 'HUN': 'Budapest', 'ROU': 'Bucharest',
    'BGR': 'Sofia', 'HRV': 'Zagreb', 'SVN': 'Ljubljana', 'SRB': 'Belgrade',
    'BIH': 'Sarajevo', 'MNE': 'Podgorica', 'MKD': 'Skopje', 'ALB': 'Tirana',
    'GRC': 'Athens', 'CYP': 'Nicosia', 'MLT': 'Valletta', 'EST': 'Tallinn',
    'LVA': 'Riga', 'LTU': 'Vilnius', 'BLR': 'Minsk', 'UKR': 'Kyiv',
    'MDA': 'Chisinau', 'GEO': 'Tbilisi', 'ARM': 'Yerevan', 'AZE': 'Baku',
    'KAZ': 'Nur-Sultan', 'UZB': 'Tashkent', 'TKM': 'Ashgabat',
    'TJK': 'Dushanbe', 'KGZ': 'Bishkek', 'AFG': 'Kabul', 'IRQ': 'Baghdad',
    'SYR': 'Damascus', 'JOR': 'Amman', 'LBN': 'Beirut', 'KWT': 'Kuwait City',
    'BHR': 'Manama', 'QAT': 'Doha', 'OMN': 'Muscat', 'YEM': 'Sanaa',
    'LBY': 'Tripoli', 'TUN': 'Tunis', 'DZA': 'Algiers', 'MAR': 'Rabat',
    'MRT': 'Nouakchott', 'MLI': 'Bamako', 'BFA': 'Ouagadougou',
    'NER': 'Niamey', 'TCD': 'Ndjamena', 'SDN': 'Khartoum', 'SSD': 'Juba',
    'ETH': 'Addis Ababa', 'ERI': 'Asmara', 'DJI': 'Djibouti',
    'SOM': 'Mogadishu', 'KEN': 'Nairobi', 'UGA': 'Kampala',
    'TZA': 'Dodoma', 'RWA': 'Kigali', 'BDI': 'Gitega',
    'COD': 'Kinshasa', 'COG': 'Brazzaville', 'GAB': 'Libreville',
    'CMR': 'Yaounde', 'CAF': 'Bangui', 'GNQ': 'Malabo',
    'STP': 'Sao Tome', 'AGO': 'Luanda', 'MOZ': 'Maputo',
    'ZMB': 'Lusaka', 'ZWE': 'Harare', 'BWA': 'Gaborone',
    'NAM': 'Windhoek', 'SWZ': 'Mbabane', 'LSO': 'Maseru',
    'MWI': 'Lilongwe', 'MDG': 'Antananarivo', 'MUS': 'Port Louis',
    'COM': 'Moroni', 'SYC': 'Victoria', 'GHA': 'Accra',
    'CIV': 'Yamoussoukro', 'SEN': 'Dakar', 'GMB': 'Banjul',
    'GNB': 'Bissau', 'GIN': 'Conakry', 'SLE': 'Freetown',
    'LBR': 'Monrovia', 'TGO': 'Lome', 'BEN': 'Porto Novo',
    'CPV': 'Praia', 'JAM': 'Kingston', 'TTO': 'Port of Spain',
    'BRB': 'Bridgetown', 'BHS': 'Nassau', 'HTI': 'Port au Prince',
    'DOM': 'Santo Domingo', 'CUB': 'Havana', 'CRI': 'San Jose',
    'PAN': 'Panama City', 'GTM': 'Guatemala City', 'HND': 'Tegucigalpa',
    'SLV': 'San Salvador', 'NIC': 'Managua', 'BLZ': 'Belmopan',
    'MNG': 'Ulaanbaatar', 'PRK': 'Pyongyang', 'NPL': 'Kathmandu',
    'BTN': 'Thimphu', 'LKA': 'Sri Jayawardenepura Kotte', 'MDV': 'Male',
    'MMR': 'Naypyidaw', 'KHM': 'Phnom Penh', 'LAO': 'Vientiane',
    'BRN': 'Bandar Seri Begawan', 'PNG': 'Port Moresby', 'FJI': 'Suva',
    'SLB': 'Honiara', 'VUT': 'Port Vila', 'WSM': 'Apia',
    'TON': 'Nukualofa', 'KIR': 'Tarawa', 'NRU': 'Yaren',
    'TUV': 'Funafuti', 'TLS': 'Dili', 'LCA': 'Castries',
    'VCT': 'Kingstown', 'KNA': 'Basseterre', 'ATG': 'Saint Johns',
    'DMA': 'Roseau', 'GRD': 'Saint Georges', 'PLW': 'Ngerulmud',
    'MHL': 'Majuro', 'FSM': 'Palikir', 'CAN': 'Ottawa',
}

# Capital name length
df['capital_name_length'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in capitals:
        df.loc[name, 'capital_name_length'] = len(capitals[iso3])
add_to_codebook('capital_name_length',
                'Number of characters in capital city name',
                'Derived from capital city name')

# Capital scrabble score
df['capital_scrabble_score'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in capitals:
        df.loc[name, 'capital_scrabble_score'] = scrabble_score(capitals[iso3])
add_to_codebook('capital_scrabble_score',
                'Scrabble score of capital city name',
                'Derived from capital city name')

# Capital numerology score
def numerology_score(name):
    return sum(ord(c.upper()) - ord('A') + 1 for c in name if c.isalpha())

df['capital_numerology_score'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in capitals:
        df.loc[name, 'capital_numerology_score'] = numerology_score(capitals[iso3])
add_to_codebook('capital_numerology_score',
                'Numerology score of capital city name (sum of letter positions)',
                'Derived from capital city name (pseudoscience)')

# Capital vowel count
df['capital_vowel_count'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in capitals:
        df.loc[name, 'capital_vowel_count'] = sum(1 for c in capitals[iso3].lower() if c in 'aeiou')
add_to_codebook('capital_vowel_count',
                'Number of vowels in capital city name',
                'Derived from capital city name')

# Capital syllable count
def count_syllables(name):
    name = name.lower()
    name = re.sub(r'e\s*$', '', name)
    vowel_groups = re.findall(r'[aeiou]+', name)
    return max(1, len(vowel_groups))

df['capital_syllable_count'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in capitals:
        df.loc[name, 'capital_syllable_count'] = count_syllables(capitals[iso3])
add_to_codebook('capital_syllable_count',
                'Approximate syllable count of capital city name',
                'Derived from capital city name')

# Country name + capital name combined length
df['country_plus_capital_length'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    country_letters = sum(1 for c in name if c.isalpha())
    capital_letters = 0
    if iso3 and iso3 in capitals:
        capital_letters = sum(1 for c in capitals[iso3] if c.isalpha())
    df.loc[name, 'country_plus_capital_length'] = country_letters + capital_letters
add_to_codebook('country_plus_capital_length',
                'Total letter count of country name + capital city name',
                'Derived from country and capital names')

print(f"  ✓ Added 6 capital city features")

# --- Flag features ---
# Number of colors in national flag (approximate data for major countries)
flag_colors = {
    'USA': 3, 'GBR': 3, 'FRA': 3, 'DEU': 3, 'ITA': 3, 'ESP': 3, 'RUS': 3,
    'CHN': 2, 'JPN': 2, 'KOR': 4, 'IND': 4, 'BRA': 4, 'MEX': 4, 'ARG': 3,
    'AUS': 3, 'NZL': 3, 'ZAF': 6, 'NGA': 2, 'EGY': 4, 'SAU': 2, 'ARE': 4,
    'ISR': 2, 'TUR': 2, 'IRN': 4, 'PAK': 2, 'BGD': 2, 'IDN': 2, 'MYS': 4,
    'THA': 3, 'VNM': 2, 'PHL': 4, 'SGP': 2, 'COL': 3, 'PER': 2, 'CHL': 3,
    'VEN': 4, 'ECU': 4, 'BOL': 3, 'PRY': 5, 'URY': 2, 'SWE': 2, 'NOR': 3,
    'FIN': 2, 'DNK': 2, 'ISL': 3, 'IRL': 3, 'PRT': 5, 'NLD': 3, 'BEL': 3,
    'CHE': 2, 'AUT': 2, 'POL': 2, 'CZE': 3, 'SVK': 4, 'HUN': 3, 'ROU': 3,
    'BGR': 3, 'HRV': 5, 'SVN': 4, 'SRB': 4, 'BIH': 3, 'MNE': 5, 'MKD': 2,
    'ALB': 2, 'GRC': 2, 'CYP': 3, 'MLT': 3, 'EST': 3, 'LVA': 2, 'LTU': 3,
    'BLR': 3, 'UKR': 2, 'MDA': 4, 'GEO': 2, 'ARM': 3, 'AZE': 4, 'KAZ': 2,
    'UZB': 5, 'TKM': 4, 'TJK': 4, 'KGZ': 2, 'AFG': 3, 'IRQ': 4, 'SYR': 4,
    'JOR': 4, 'LBN': 4, 'KWT': 4, 'BHR': 2, 'QAT': 2, 'OMN': 3, 'YEM': 3,
    'LBY': 4, 'TUN': 2, 'DZA': 3, 'MAR': 2, 'MRT': 3, 'MLI': 3, 'BFA': 3,
    'NER': 3, 'TCD': 3, 'SDN': 4, 'SSD': 5, 'ETH': 4, 'ERI': 4, 'DJI': 4,
    'SOM': 2, 'KEN': 5, 'UGA': 5, 'TZA': 4, 'RWA': 4, 'BDI': 4,
    'COD': 4, 'COG': 3, 'GAB': 3, 'CMR': 3, 'CAF': 5, 'GNQ': 5,
    'STP': 4, 'AGO': 3, 'MOZ': 5, 'ZMB': 4, 'ZWE': 6, 'BWA': 3,
    'NAM': 4, 'SWZ': 5, 'LSO': 3, 'MWI': 3, 'MDG': 3, 'MUS': 4,
    'COM': 5, 'SYC': 5, 'GHA': 4, 'CIV': 3, 'SEN': 3, 'GMB': 4,
    'GNB': 4, 'GIN': 3, 'SLE': 3, 'LBR': 3, 'TGO': 4, 'BEN': 3,
    'CPV': 4, 'JAM': 3, 'TTO': 3, 'BRB': 3, 'BHS': 3, 'HTI': 3,
    'DOM': 5, 'CUB': 3, 'CRI': 3, 'PAN': 3, 'GTM': 5, 'HND': 2,
    'SLV': 3, 'NIC': 3, 'BLZ': 7, 'MNG': 3, 'PRK': 4, 'NPL': 3,
    'BTN': 3, 'LKA': 5, 'MDV': 3, 'MMR': 4, 'KHM': 4, 'LAO': 3,
    'BRN': 4, 'PNG': 3, 'FJI': 4, 'SLB': 4, 'VUT': 5, 'WSM': 3,
    'TON': 2, 'KIR': 5, 'TLS': 4, 'LCA': 4, 'VCT': 4, 'KNA': 5,
    'ATG': 5, 'DMA': 5, 'GRD': 4, 'GUY': 5, 'SUR': 4, 'CAN': 2,
}

df['flag_colors_count'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in flag_colors:
        df.loc[name, 'flag_colors_count'] = flag_colors[iso3]
add_to_codebook('flag_colors_count',
                'Number of distinct colors in national flag',
                'Vexillology data')

# Stars on flag
flag_stars = {
    'USA': 50, 'CHN': 5, 'BRA': 27, 'AUS': 6, 'NZL': 4, 'TUR': 1,
    'ISR': 1, 'PAK': 1, 'VNM': 1, 'SGP': 5, 'CHL': 1, 'CUB': 1,
    'PAN': 2, 'HND': 5, 'VEN': 8, 'CMR': 1, 'SEN': 1, 'GHA': 1,
    'GIN': 0, 'ETH': 1, 'DJI': 1, 'SOM': 1, 'TGO': 1, 'BFA': 1,
    'CAF': 1, 'COD': 1, 'AGO': 1, 'MOZ': 1, 'ZWE': 1, 'SSD': 1,
    'JOR': 1, 'IRQ': 3, 'SYR': 2, 'MRT': 1, 'LBY': 1, 'DZA': 1,
    'MAR': 1, 'TUN': 1, 'COM': 4, 'STP': 2, 'GNQ': 0, 'CPV': 10,
    'BIH': 7, 'SVN': 0, 'KOR': 0, 'PRK': 1, 'MMR': 1, 'KHM': 0,
    'LAO': 0, 'PHL': 3, 'MYS': 1, 'TLS': 1, 'SLB': 5, 'PNG': 5,
    'KIR': 0, 'MHL': 1, 'FSM': 4, 'WSM': 5, 'NRU': 1, 'TUV': 9,
    'TON': 0, 'FJI': 0, 'PLW': 0, 'VUT': 0, 'ARG': 1, 'URY': 1,
    'PRY': 1, 'BOL': 0, 'ECU': 0, 'PER': 0, 'COL': 0, 'GUY': 0,
    'SUR': 1, 'DOM': 0, 'HTI': 0, 'JAM': 0, 'TTO': 0, 'BRB': 0,
    'BHS': 0, 'LCA': 0, 'VCT': 0, 'KNA': 2, 'ATG': 1, 'DMA': 0,
    'GRD': 7, 'CRI': 0, 'GTM': 0, 'SLV': 0, 'NIC': 0, 'BLZ': 0,
    'MEX': 0, 'IND': 0, 'BGD': 0, 'NPL': 0, 'BTN': 0, 'LKA': 0,
    'MDV': 0, 'IDN': 0, 'THA': 0, 'BRN': 0, 'MNG': 1, 'JPN': 0,
    'GBR': 0, 'FRA': 0, 'DEU': 0, 'ITA': 0, 'ESP': 0, 'RUS': 0,
    'SWE': 0, 'NOR': 0, 'FIN': 0, 'DNK': 0, 'ISL': 0, 'IRL': 0,
    'PRT': 0, 'NLD': 0, 'BEL': 0, 'CHE': 0, 'AUT': 0, 'POL': 0,
    'CZE': 0, 'SVK': 0, 'HUN': 0, 'ROU': 0, 'BGR': 0, 'HRV': 0,
    'SRB': 0, 'MNE': 0, 'MKD': 0, 'ALB': 0, 'GRC': 0, 'CYP': 0,
    'MLT': 0, 'EST': 0, 'LVA': 0, 'LTU': 0, 'BLR': 0, 'UKR': 0,
    'MDA': 0, 'GEO': 0, 'ARM': 0, 'AZE': 1, 'KAZ': 1, 'UZB': 12,
    'TKM': 5, 'TJK': 0, 'KGZ': 0, 'AFG': 0, 'IRQ': 0, 'LBN': 0,
    'KWT': 0, 'BHR': 0, 'QAT': 0, 'OMN': 0, 'YEM': 0, 'SAU': 0,
    'ARE': 0, 'EGY': 1, 'SDN': 0, 'NGA': 0, 'ZAF': 0, 'KEN': 0,
    'UGA': 0, 'TZA': 0, 'RWA': 0, 'BDI': 3, 'COG': 0, 'GAB': 0,
    'GNQ': 0, 'MWI': 0, 'ZMB': 1, 'BWA': 0, 'NAM': 1, 'SWZ': 0,
    'LSO': 0, 'MDG': 0, 'MUS': 0, 'SYC': 0, 'CIV': 0, 'GMB': 0,
    'GNB': 1, 'SLE': 0, 'LBR': 1, 'BEN': 0, 'NER': 1, 'TCD': 0,
    'ERI': 0, 'IRN': 0, 'CAN': 0,
}

df['flag_stars_count'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in flag_stars:
        df.loc[name, 'flag_stars_count'] = flag_stars[iso3]
add_to_codebook('flag_stars_count',
                'Number of stars on national flag',
                'Vexillology data')

print(f"  ✓ Added 2 flag features")

# ============================================================================
# PART 2: WEB-SOURCED BIZARRE DATA (hardcoded from known sources)
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: WEB-SOURCED BIZARRE DATA")
print("=" * 80)

# --- Nobel Prize winners by country ---
nobel_prizes = {
    'USA': 400, 'GBR': 137, 'DEU': 111, 'FRA': 72, 'SWE': 32, 'JPN': 29,
    'RUS': 32, 'CHE': 27, 'CAN': 28, 'AUT': 22, 'ITA': 21, 'NLD': 22,
    'NOR': 13, 'DNK': 14, 'AUS': 16, 'ISR': 13, 'IND': 12, 'BEL': 11,
    'POL': 11, 'ZAF': 11, 'IRL': 9, 'ARG': 5, 'HUN': 9, 'ESP': 8,
    'CHN': 12, 'NZL': 3, 'FIN': 5, 'EGY': 4, 'CZE': 3, 'PRT': 2,
    'MEX': 3, 'COL': 2, 'TUR': 2, 'GRC': 2, 'GTM': 2, 'KOR': 2,
    'CHL': 2, 'PER': 1, 'GHA': 1, 'KEN': 1, 'NGA': 1, 'TZA': 0,
    'PAK': 2, 'BGD': 1, 'MMR': 1, 'VNM': 1, 'LBR': 2, 'CRI': 1,
    'TLS': 2, 'IRN': 1, 'YEM': 1, 'ETH': 1, 'BRA': 1, 'URY': 0,
    'TTO': 2, 'LCA': 2, 'ISL': 1, 'LTU': 1, 'BLR': 1, 'UKR': 1,
}

df['nobel_prize_winners'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in nobel_prizes:
        df.loc[name, 'nobel_prize_winners'] = nobel_prizes[iso3]
add_to_codebook('nobel_prize_winners',
                'Total Nobel Prize laureates by country',
                'Nobel Prize Committee data', 'bizarre')

# --- Nuclear reactors ---
nuclear_reactors = {
    'USA': 93, 'FRA': 56, 'CHN': 50, 'RUS': 37, 'JPN': 33, 'KOR': 24,
    'IND': 22, 'CAN': 19, 'UKR': 15, 'GBR': 9, 'SWE': 6, 'BEL': 7,
    'CZE': 6, 'ESP': 7, 'FIN': 4, 'DEU': 3, 'HUN': 4, 'CHE': 4,
    'SVK': 4, 'BGR': 2, 'BRA': 2, 'ARG': 3, 'MEX': 2, 'ROU': 2,
    'PAK': 6, 'ZAF': 2, 'IRN': 1, 'ARE': 3, 'BGD': 0, 'NLD': 1,
    'SVN': 1, 'ARM': 1, 'BLR': 2, 'TUR': 0,
}

df['nuclear_reactors'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in nuclear_reactors:
        df.loc[name, 'nuclear_reactors'] = nuclear_reactors[iso3]
add_to_codebook('nuclear_reactors',
                'Number of operational nuclear power reactors',
                'IAEA PRIS database', 'bizarre')

# --- Passport power (visa-free destinations) ---
passport_power = {
    'JPN': 193, 'SGP': 192, 'KOR': 192, 'DEU': 190, 'ESP': 190,
    'FIN': 189, 'ITA': 189, 'AUT': 188, 'FRA': 188, 'GBR': 188,
    'SWE': 188, 'NLD': 188, 'DNK': 187, 'IRL': 187, 'PRT': 186,
    'BEL': 186, 'NOR': 185, 'CHE': 185, 'USA': 184, 'CZE': 184,
    'AUS': 183, 'NZL': 183, 'MLT': 183, 'CAN': 183, 'GRC': 183,
    'HUN': 183, 'POL': 182, 'LTU': 182, 'SVK': 181, 'LVA': 181,
    'SVN': 181, 'EST': 180, 'ISL': 180, 'MYS': 179, 'CHL': 174,
    'HRV': 173, 'ROU': 173, 'BGR': 172, 'ARG': 171, 'BRA': 170,
    'MEX': 159, 'ISR': 159, 'ARE': 178, 'URY': 168, 'CRI': 152,
    'PAN': 143, 'SRB': 138, 'COL': 131, 'PER': 136, 'TUR': 116,
    'ZAF': 106, 'JAM': 85, 'TTO': 153, 'BHS': 155, 'ECU': 92,
    'PRY': 144, 'DOM': 74, 'GTM': 135, 'HND': 132, 'SLV': 134,
    'NIC': 129, 'BOL': 77, 'GUY': 87, 'VEN': 48, 'CHN': 80,
    'THA': 79, 'IND': 59, 'IDN': 72, 'PHL': 67, 'VNM': 55,
    'RUS': 118, 'UKR': 144, 'BLR': 78, 'KAZ': 76, 'UZB': 62,
    'GEO': 116, 'MDA': 120, 'AZE': 68, 'ARM': 65, 'KGZ': 63,
    'TJK': 57, 'TKM': 51, 'EGY': 53, 'JOR': 52, 'TUN': 72,
    'MAR': 65, 'SAU': 80, 'KWT': 98, 'QAT': 98, 'OMN': 80,
    'BHR': 87, 'LBN': 42, 'IRN': 43, 'IRQ': 29, 'PAK': 33,
    'AFG': 27, 'SYR': 30, 'YEM': 34, 'LBY': 40, 'SDN': 43,
    'NGA': 46, 'KEN': 73, 'GHA': 65, 'TZA': 70, 'ETH': 46,
    'SEN': 66, 'BWA': 86, 'NAM': 75, 'MUS': 146, 'SYC': 153,
    'RWA': 62, 'UGA': 66, 'MOZ': 62, 'ZMB': 66, 'ZWE': 58,
    'MNG': 66, 'BGD': 42, 'NPL': 40, 'LKA': 42, 'MMR': 49,
    'KHM': 54, 'LAO': 51, 'BRN': 166, 'MYS': 179, 'FJI': 86,
    'PNG': 56, 'CUB': 65, 'HTI': 48, 'BRB': 161, 'ALB': 118,
    'BIH': 125, 'MNE': 124, 'MKD': 125, 'MLI': 52, 'BFA': 55,
    'NER': 49, 'TCD': 49, 'CAF': 48, 'CMR': 50, 'COG': 49,
    'COD': 44, 'GAB': 56, 'GNQ': 51, 'AGO': 50, 'MDG': 56,
    'MWI': 58, 'LSO': 60, 'SWZ': 69, 'DJI': 50, 'SOM': 35,
    'ERI': 41, 'SSD': 40, 'BDI': 46, 'LCA': 146, 'VCT': 143,
    'KNA': 156, 'DMA': 144, 'ATG': 151, 'GRD': 142, 'BLZ': 101,
    'SUR': 84, 'CAN': 183, 'KOR': 192,
}

df['passport_visa_free_destinations'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in passport_power:
        df.loc[name, 'passport_visa_free_destinations'] = passport_power[iso3]
add_to_codebook('passport_visa_free_destinations',
                'Number of destinations accessible visa-free or visa-on-arrival',
                'Henley Passport Index 2023', 'bizarre')

# --- Average male height (cm) ---
avg_height = {
    'NLD': 183.8, 'MNE': 183.2, 'DNK': 181.4, 'NOR': 179.7, 'SRB': 180.6,
    'DEU': 180.3, 'HRV': 180.5, 'CZE': 180.3, 'SVN': 180.3, 'AUS': 179.2,
    'CAN': 178.1, 'SWE': 180.0, 'FIN': 180.7, 'BEL': 178.7, 'GBR': 177.5,
    'FRA': 178.6, 'USA': 177.1, 'ISL': 180.5, 'IRL': 178.9, 'AUT': 179.2,
    'CHE': 178.7, 'NZL': 177.0, 'ITA': 177.8, 'ESP': 176.6, 'PRT': 173.9,
    'GRC': 177.3, 'POL': 180.7, 'RUS': 176.5, 'UKR': 178.5, 'BLR': 178.4,
    'LTU': 179.1, 'LVA': 180.2, 'EST': 179.6, 'HUN': 177.3, 'SVK': 179.4,
    'ROU': 174.7, 'BGR': 175.2, 'ALB': 174.0, 'MKD': 176.3, 'BIH': 180.9,
    'GEO': 174.0, 'ARM': 172.0, 'AZE': 172.0, 'TUR': 174.2,
    'JPN': 170.8, 'KOR': 173.5, 'CHN': 171.8, 'IND': 166.5, 'PAK': 168.0,
    'BGD': 165.0, 'IDN': 163.6, 'MYS': 166.3, 'THA': 170.3, 'VNM': 168.1,
    'PHL': 163.5, 'MMR': 164.7, 'KHM': 163.3, 'LAO': 162.2, 'NPL': 163.0,
    'LKA': 166.0, 'MNG': 169.1, 'SGP': 170.6, 'BRN': 165.0,
    'BRA': 173.6, 'ARG': 174.5, 'COL': 170.6, 'PER': 165.2, 'CHL': 171.8,
    'MEX': 169.0, 'VEN': 171.6, 'ECU': 167.1, 'BOL': 165.2, 'PRY': 170.5,
    'URY': 173.4, 'CUB': 172.0, 'DOM': 172.7, 'GTM': 163.4, 'HND': 166.4,
    'SLV': 167.0, 'NIC': 166.8, 'CRI': 169.6, 'PAN': 169.3, 'JAM': 171.8,
    'TTO': 174.0, 'HTI': 172.6,
    'EGY': 170.3, 'SAU': 168.9, 'IRN': 174.0, 'IRQ': 170.4, 'ISR': 177.0,
    'JOR': 171.0, 'LBN': 174.4, 'SYR': 173.0, 'KWT': 172.0, 'ARE': 170.5,
    'QAT': 170.8, 'OMN': 170.0, 'YEM': 163.0, 'BHR': 171.0,
    'NGA': 167.0, 'ZAF': 168.0, 'KEN': 169.6, 'GHA': 169.5, 'ETH': 167.6,
    'TZA': 166.0, 'UGA': 166.3, 'SEN': 175.3, 'CIV': 170.1, 'CMR': 170.6,
    'COD': 166.5, 'AGO': 168.0, 'MOZ': 166.0, 'MDG': 161.5, 'ZMB': 166.5,
    'ZWE': 170.0, 'RWA': 164.5, 'MLI': 171.3, 'BFA': 170.6,
    'MRT': 170.0, 'NER': 168.0, 'TCD': 172.0, 'SDN': 171.0,
    'MAR': 171.0, 'TUN': 173.6, 'DZA': 172.2, 'LBY': 173.0,
    'KAZ': 172.0, 'UZB': 171.0, 'TKM': 172.0, 'TJK': 170.0, 'KGZ': 171.0,
    'AFG': 168.2, 'BWA': 171.0, 'NAM': 170.0, 'LSO': 166.0,
    'SWZ': 168.0, 'MWI': 166.0,
}

df['average_male_height_cm'] = 0.0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in avg_height:
        df.loc[name, 'average_male_height_cm'] = avg_height[iso3]
add_to_codebook('average_male_height_cm',
                'Average adult male height in centimeters',
                'NCD Risk Factor Collaboration / WHO', 'bizarre')

# --- National holidays per year ---
national_holidays = {
    'IND': 26, 'COL': 18, 'PHL': 18, 'LKA': 25, 'BGD': 21, 'PAK': 16,
    'NPL': 24, 'IRN': 26, 'MYS': 15, 'IDN': 16, 'THA': 16, 'JPN': 16,
    'KOR': 15, 'CHN': 11, 'BRA': 13, 'ARG': 15, 'MEX': 12, 'USA': 11,
    'CAN': 10, 'GBR': 8, 'FRA': 11, 'DEU': 9, 'ITA': 12, 'ESP': 14,
    'PRT': 13, 'NLD': 8, 'BEL': 10, 'CHE': 8, 'AUT': 13, 'SWE': 13,
    'NOR': 10, 'FIN': 12, 'DNK': 11, 'ISL': 14, 'IRL': 10, 'POL': 13,
    'CZE': 13, 'SVK': 15, 'HUN': 11, 'ROU': 15, 'BGR': 14, 'GRC': 12,
    'TUR': 15, 'RUS': 14, 'UKR': 11, 'EGY': 13, 'ZAF': 12, 'NGA': 14,
    'KEN': 10, 'GHA': 13, 'ETH': 14, 'TZA': 14, 'UGA': 13,
    'MAR': 13, 'TUN': 12, 'DZA': 11, 'SAU': 7, 'ARE': 10, 'ISR': 9,
    'JOR': 12, 'KWT': 8, 'QAT': 6, 'OMN': 8, 'BHR': 8,
    'AUS': 8, 'NZL': 11, 'SGP': 11, 'VNM': 11, 'KHM': 28,
    'MMR': 14, 'LAO': 12, 'CHL': 16, 'PER': 14, 'COL': 18,
    'VEN': 15, 'ECU': 13, 'BOL': 14, 'PRY': 14, 'URY': 11,
    'CUB': 9, 'DOM': 13, 'CRI': 11, 'PAN': 12, 'GTM': 10,
    'HND': 11, 'SLV': 11, 'NIC': 10, 'JAM': 10, 'TTO': 14,
    'HTI': 15, 'CMR': 10, 'SEN': 16, 'CIV': 14, 'COD': 10,
    'AGO': 12, 'MOZ': 10, 'MDG': 12, 'ZMB': 11, 'ZWE': 12,
    'MNG': 9, 'AFG': 14, 'IRQ': 12, 'SYR': 11, 'LBN': 22,
    'SDN': 8, 'LBY': 8, 'RWA': 12, 'MLI': 11, 'BFA': 12,
    'NER': 10, 'TCD': 9, 'BWA': 11, 'NAM': 12, 'EST': 12,
    'LVA': 11, 'LTU': 13, 'BLR': 9, 'MDA': 11, 'GEO': 14,
    'ARM': 12, 'AZE': 19, 'KAZ': 10, 'UZB': 10, 'TKM': 9,
    'TJK': 11, 'KGZ': 11, 'ALB': 12, 'SRB': 10, 'HRV': 13,
    'SVN': 13, 'BIH': 9, 'MNE': 10, 'MKD': 11, 'CYP': 15,
    'MLT': 14, 'BRN': 11,
}

df['national_holidays_per_year'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in national_holidays:
        df.loc[name, 'national_holidays_per_year'] = national_holidays[iso3]
add_to_codebook('national_holidays_per_year',
                'Number of official national public holidays per year',
                'Various government sources', 'bizarre')

# --- Highest mountain peak (meters) ---
highest_peak = {
    'CHN': 8848, 'NPL': 8848, 'PAK': 8611, 'IND': 8586, 'BTN': 7570,
    'TJK': 7495, 'AFG': 7708, 'KGZ': 7439, 'KAZ': 7010, 'ARG': 6961,
    'CHL': 6893, 'PER': 6768, 'BOL': 6542, 'ECU': 6310, 'COL': 5775,
    'VEN': 4978, 'USA': 6190, 'CAN': 5959, 'MEX': 5636, 'RUS': 5642,
    'GEO': 5193, 'TUR': 5137, 'IRN': 5610, 'IDN': 4884, 'KEN': 5199,
    'TZA': 5895, 'UGA': 5109, 'COD': 5109, 'ETH': 4550, 'CMR': 4095,
    'MAR': 4167, 'PNG': 4509, 'NZL': 3724, 'JPN': 3776, 'TWN': 3952,
    'MYS': 4095, 'FRA': 4808, 'ITA': 4808, 'CHE': 4634, 'AUT': 3798,
    'ESP': 3478, 'DEU': 2962, 'NOR': 2469, 'SWE': 2111, 'GRC': 2917,
    'ALB': 2764, 'BIH': 2386, 'MNE': 2534, 'BGR': 2925, 'ROU': 2544,
    'SVN': 2864, 'HRV': 1831, 'SRB': 2169, 'MKD': 2764, 'POL': 2499,
    'SVK': 2655, 'CZE': 1602, 'HUN': 1014, 'GBR': 1345, 'IRL': 1041,
    'ISL': 2110, 'PRT': 2351, 'AUS': 2228, 'BRA': 2995, 'ZAF': 3450,
    'EGY': 2629, 'DZA': 3003, 'LBY': 2267, 'SDN': 3042, 'NGA': 2419,
    'GHA': 883, 'SEN': 581, 'CIV': 1752, 'MLI': 1155, 'BFA': 749,
    'NER': 2022, 'TCD': 3445, 'AGO': 2620, 'MOZ': 2436, 'ZMB': 2301,
    'ZWE': 2592, 'NAM': 2606, 'BWA': 1494, 'MDG': 2876, 'MWI': 3002,
    'RWA': 4507, 'BDI': 2670, 'GAB': 1575, 'COG': 1020, 'CAF': 1410,
    'LSO': 3482, 'SWZ': 1862, 'KOR': 1950, 'PRK': 2744, 'MNG': 4374,
    'VNM': 3143, 'THA': 2565, 'MMR': 5881, 'KHM': 1813, 'LAO': 2817,
    'PHL': 2954, 'LKA': 2524, 'UKR': 2061, 'BLR': 345, 'MDA': 430,
    'GEO': 5193, 'ARM': 4090, 'AZE': 4466, 'UZB': 4643, 'TKM': 3139,
    'SAU': 3133, 'YEM': 3666, 'OMN': 3004, 'JOR': 1854, 'LBN': 3088,
    'SYR': 2814, 'IRQ': 3611, 'ISR': 1208, 'KWT': 306, 'BHR': 134,
    'QAT': 103, 'ARE': 1934, 'CRI': 3820, 'PAN': 3475, 'GTM': 4220,
    'HND': 2870, 'SLV': 2381, 'NIC': 2107, 'BLZ': 1124, 'CUB': 1974,
    'DOM': 3098, 'HTI': 2680, 'JAM': 2256, 'TTO': 940,
    'URY': 514, 'PRY': 842, 'GUY': 2772, 'SUR': 1230,
    'FIN': 1324, 'DNK': 171, 'BEL': 694, 'NLD': 322, 'MLT': 253,
    'SGP': 163, 'CYP': 1952, 'EST': 318, 'LVA': 312, 'LTU': 294,
    'FJI': 1324, 'SLB': 2335, 'VUT': 1877,
}

df['highest_peak_meters'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in highest_peak:
        df.loc[name, 'highest_peak_meters'] = highest_peak[iso3]
add_to_codebook('highest_peak_meters',
                'Height of highest mountain peak in meters',
                'Various geographic sources', 'bizarre')

# --- Number of FIFA member association founding year ---
fifa_founding = {
    'GBR': 1863, 'NLD': 1889, 'DNK': 1889, 'NZL': 1891, 'ARG': 1893,
    'CHL': 1895, 'CHE': 1895, 'BEL': 1895, 'ITA': 1898, 'DEU': 1900,
    'URY': 1900, 'HUN': 1901, 'CZE': 1901, 'NOR': 1902, 'AUT': 1904,
    'ESP': 1904, 'SWE': 1904, 'FRA': 1904, 'FIN': 1907, 'USA': 1913,
    'CAN': 1912, 'RUS': 1912, 'ZAF': 1991, 'JPN': 1921, 'AUS': 1961,
    'BRA': 1914, 'PER': 1922, 'PRY': 1906, 'COL': 1924, 'MEX': 1927,
    'BOL': 1925, 'ECU': 1925, 'VEN': 1926, 'CRI': 1921, 'GTM': 1919,
    'HND': 1935, 'SLV': 1935, 'NIC': 1931, 'PAN': 1937, 'CUB': 1924,
    'HTI': 1904, 'DOM': 1953, 'JAM': 1910, 'TTO': 1908, 'EGY': 1921,
    'TUR': 1923, 'GRC': 1926, 'ISR': 1928, 'IRQ': 1948, 'IRN': 1920,
    'CHN': 1924, 'IND': 1937, 'KOR': 1928, 'PHL': 1907, 'THA': 1916,
    'IDN': 1930, 'MYS': 1933, 'SGP': 1892, 'VNM': 1962, 'MMR': 1947,
    'BGD': 1972, 'PAK': 1947, 'AFG': 1933, 'NPL': 1951, 'LKA': 1939,
    'KHM': 1933, 'LAO': 1951, 'NGA': 1945, 'GHA': 1957, 'KEN': 1960,
    'ETH': 1943, 'TZA': 1930, 'UGA': 1924, 'CMR': 1959, 'CIV': 1960,
    'SEN': 1960, 'COD': 1919, 'ZMB': 1929, 'ZWE': 1965, 'MAR': 1955,
    'TUN': 1957, 'DZA': 1962, 'SDN': 1936, 'AGO': 1979, 'MOZ': 1975,
    'MDG': 1961, 'MLI': 1960, 'BFA': 1960, 'NER': 1967, 'TCD': 1962,
    'RWA': 1972, 'BDI': 1948, 'GAB': 1962, 'COG': 1962, 'CAF': 1961,
    'POL': 1919, 'ROU': 1909, 'BGR': 1923, 'SRB': 1919, 'HRV': 1912,
    'SVN': 1920, 'BIH': 1920, 'MNE': 1931, 'MKD': 1948, 'ALB': 1930,
    'UKR': 1991, 'BLR': 1989, 'MDA': 1990, 'EST': 1921, 'LVA': 1922,
    'LTU': 1922, 'GEO': 1990, 'ARM': 1992, 'AZE': 1992, 'KAZ': 1994,
    'UZB': 1946, 'TKM': 1992, 'TJK': 1936, 'KGZ': 1992, 'MNG': 1959,
    'IRL': 1921, 'ISL': 1947, 'PRT': 1914, 'MLT': 1900, 'CYP': 1934,
    'SVK': 1938, 'LBN': 1933, 'JOR': 1949, 'SYR': 1936, 'KWT': 1952,
    'SAU': 1956, 'ARE': 1971, 'QAT': 1970, 'OMN': 1978, 'BHR': 1957,
    'YEM': 1940, 'LBY': 1962, 'BWA': 1970, 'NAM': 1990, 'SWZ': 1968,
    'LSO': 1932, 'MWI': 1966, 'GNQ': 1986, 'STP': 1975, 'CPV': 1982,
    'GMB': 1952, 'GNB': 1986, 'GIN': 1960, 'SLE': 1960, 'LBR': 1936,
    'TGO': 1960, 'BEN': 1962, 'MRT': 1961, 'DJI': 1979, 'SOM': 1951,
    'ERI': 1998, 'SSD': 2012, 'BRN': 1969, 'TLS': 2002, 'MUS': 1952,
    'COM': 1979, 'SYC': 1979, 'BLZ': 1986, 'GUY': 1902, 'SUR': 1929,
    'FJI': 1963, 'PNG': 1962, 'SLB': 1978, 'VUT': 1988, 'WSM': 1986,
    'TON': 1994, 'KIR': 2003, 'BRB': 1910, 'BHS': 1967, 'LCA': 1979,
    'VCT': 1988, 'KNA': 1992, 'ATG': 1970, 'DMA': 1994, 'GRD': 1924,
    'PRK': 1945,
}

df['football_association_founded'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in fifa_founding:
        df.loc[name, 'football_association_founded'] = fifa_founding[iso3]
add_to_codebook('football_association_founded',
                'Year the national football (soccer) association was founded',
                'FIFA', 'bizarre')

# --- Number of embassies abroad ---
embassies_abroad = {
    'USA': 168, 'CHN': 169, 'FRA': 163, 'RUS': 146, 'JPN': 152, 'DEU': 153,
    'GBR': 152, 'TUR': 143, 'BRA': 139, 'ITA': 126, 'IND': 123, 'ESP': 118,
    'KOR': 116, 'EGY': 111, 'MEX': 107, 'ARG': 98, 'SAU': 95, 'IDN': 95,
    'AUS': 96, 'CAN': 99, 'NLD': 107, 'CHL': 75, 'IRN': 87, 'POL': 95,
    'CUB': 85, 'NGA': 86, 'PRT': 81, 'GRC': 82, 'PAK': 84, 'COL': 74,
    'PER': 68, 'BEL': 82, 'AUT': 82, 'CHE': 98, 'NOR': 83, 'SWE': 91,
    'DNK': 75, 'FIN': 74, 'IRL': 69, 'ISR': 77, 'CZE': 78, 'ROU': 85,
    'ZAF': 75, 'UKR': 73, 'HUN': 72, 'THA': 68, 'VEN': 60, 'PHL': 65,
    'MYS': 63, 'VNM': 70, 'ARE': 60, 'KWT': 58, 'QAT': 55, 'IRQ': 58,
    'JOR': 55, 'MAR': 70, 'DZA': 68, 'TUN': 54, 'LBY': 52, 'ETH': 50,
    'KEN': 50, 'GHA': 42, 'SEN': 42, 'TZA': 38, 'UGA': 30,
    'SDN': 40, 'AGO': 32, 'MOZ': 28, 'COD': 30, 'CMR': 30,
    'CIV': 35, 'BGD': 45, 'LKA': 38, 'MMR': 25, 'KHM': 22,
    'AFG': 35, 'NPL': 22, 'BLR': 50, 'GEO': 25, 'AZE': 35,
    'KAZ': 40, 'UZB': 33, 'MNG': 20, 'BOL': 28, 'ECU': 40,
    'PRY': 25, 'URY': 38, 'PAN': 35, 'CRI': 32, 'GTM': 28,
    'DOM': 30, 'CUB': 85, 'JAM': 22, 'TTO': 20, 'SGP': 42,
    'BRN': 18, 'NZL': 45, 'ISL': 20, 'MLT': 22, 'CYP': 28,
    'EST': 28, 'LVA': 30, 'LTU': 32, 'SVK': 55, 'SVN': 35,
    'HRV': 48, 'SRB': 52, 'BIH': 30, 'MNE': 15, 'MKD': 25,
    'ALB': 30, 'BLR': 50, 'MDA': 22, 'BGR': 50, 'ARM': 20,
    'TKM': 18, 'TJK': 15, 'KGZ': 18, 'LBN': 40, 'SYR': 30,
    'YEM': 20, 'OMN': 30, 'BHR': 20,
}

df['embassies_abroad'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in embassies_abroad:
        df.loc[name, 'embassies_abroad'] = embassies_abroad[iso3]
add_to_codebook('embassies_abroad',
                'Number of diplomatic embassies/missions maintained abroad',
                'Various diplomatic sources', 'bizarre')

# --- Number of metro systems ---
metro_systems = {
    'CHN': 44, 'USA': 15, 'IND': 13, 'RUS': 7, 'KOR': 6, 'DEU': 4,
    'JPN': 9, 'GBR': 3, 'FRA': 4, 'ESP': 4, 'BRA': 6, 'MEX': 2,
    'ITA': 4, 'CAN': 3, 'TUR': 4, 'IRN': 3, 'EGY': 1, 'ARG': 1,
    'COL': 1, 'CHL': 2, 'PER': 1, 'VEN': 2, 'PAN': 1, 'DOM': 1,
    'CUB': 0, 'AUS': 2, 'NZL': 0, 'SGP': 1, 'MYS': 1, 'THA': 1,
    'IDN': 1, 'PHL': 1, 'VNM': 0, 'BGD': 0, 'PAK': 1, 'SAU': 1,
    'ARE': 1, 'ISR': 1, 'UKR': 3, 'BLR': 1, 'UZB': 1, 'KAZ': 1,
    'GEO': 1, 'AZE': 1, 'ARM': 1, 'POL': 1, 'HUN': 1, 'CZE': 1,
    'ROU': 1, 'BGR': 1, 'GRC': 1, 'PRT': 1, 'NLD': 1, 'BEL': 1,
    'AUT': 1, 'SWE': 1, 'NOR': 1, 'FIN': 1, 'DNK': 1, 'CHE': 0,
    'IRL': 0, 'NGA': 1, 'DZA': 1, 'ETH': 1, 'ZAF': 1,
}

df['metro_systems_count'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in metro_systems:
        df.loc[name, 'metro_systems_count'] = metro_systems[iso3]
add_to_codebook('metro_systems_count',
                'Number of urban metro/subway systems in the country',
                'International Association of Public Transport', 'bizarre')

# --- National anthem duration (seconds, approximate) ---
anthem_duration = {
    'GRC': 158, 'URY': 318, 'ARG': 210, 'BRA': 198, 'FRA': 80,
    'USA': 82, 'GBR': 60, 'DEU': 86, 'ITA': 48, 'ESP': 52,
    'RUS': 210, 'CHN': 46, 'JPN': 54, 'KOR': 55, 'IND': 52,
    'CAN': 62, 'AUS': 77, 'NZL': 45, 'MEX': 270, 'TUR': 66,
    'ISR': 68, 'SAU': 36, 'EGY': 78, 'ZAF': 134, 'NGA': 60,
    'KEN': 90, 'GHA': 65, 'ETH': 48, 'TZA': 55, 'UGA': 40,
    'MAR': 55, 'TUN': 42, 'DZA': 110, 'COL': 300, 'PER': 340,
    'CHL': 124, 'VEN': 199, 'ECU': 108, 'BOL': 120, 'PRY': 300,
    'PAN': 75, 'CRI': 160, 'CUB': 68, 'DOM': 85, 'GTM': 180,
    'HND': 280, 'SLV': 195, 'NIC': 95, 'JAM': 55, 'TTO': 56,
    'HTI': 65, 'SWE': 56, 'NOR': 38, 'FIN': 36, 'DNK': 44,
    'ISL': 48, 'IRL': 70, 'PRT': 72, 'NLD': 50, 'BEL': 58,
    'CHE': 45, 'AUT': 64, 'POL': 82, 'CZE': 58, 'SVK': 50,
    'HUN': 68, 'ROU': 54, 'BGR': 50, 'GRC': 158, 'HRV': 62,
    'SVN': 45, 'SRB': 72, 'BIH': 58, 'MNE': 65, 'MKD': 52,
    'ALB': 58, 'CYP': 158, 'MLT': 50, 'EST': 42, 'LVA': 40,
    'LTU': 55, 'BLR': 190, 'UKR': 45, 'MDA': 50, 'GEO': 52,
    'ARM': 68, 'AZE': 65, 'KAZ': 55, 'UZB': 75, 'TKM': 62,
    'TJK': 58, 'KGZ': 55, 'AFG': 65, 'IRN': 55, 'IRQ': 65,
    'SYR': 68, 'JOR': 52, 'LBN': 42, 'KWT': 40, 'BHR': 36,
    'QAT': 50, 'OMN': 42, 'YEM': 55, 'LBY': 55, 'SDN': 42,
    'PAK': 80, 'BGD': 25, 'IDN': 110, 'MYS': 58, 'THA': 52,
    'VNM': 68, 'PHL': 62, 'SGP': 55, 'MMR': 52, 'KHM': 62,
    'LAO': 48, 'NPL': 55, 'LKA': 60, 'MNG': 78, 'BRN': 48,
    'ZMB': 55, 'ZWE': 55, 'BWA': 50, 'NAM': 58, 'SWZ': 52,
    'LSO': 55, 'MWI': 52, 'MDG': 65, 'MUS': 52, 'RWA': 42,
    'BDI': 55, 'COD': 58, 'COG': 55, 'GAB': 42, 'CMR': 52,
    'CAF': 55, 'AGO': 68, 'MOZ': 55, 'SEN': 55, 'CIV': 52,
    'MLI': 65, 'BFA': 58, 'NER': 52, 'TCD': 55, 'GIN': 52,
    'SLE': 55, 'LBR': 58, 'TGO': 52, 'BEN': 55, 'GMB': 48,
    'GNB': 52, 'CPV': 55, 'DJI': 48, 'SOM': 55, 'ERI': 55,
    'SSD': 60, 'FJI': 52, 'PNG': 55, 'SLB': 48, 'VUT': 52,
    'PRK': 85, 'BLZ': 55, 'GUY': 72, 'SUR': 58,
}

df['national_anthem_duration_sec'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in anthem_duration:
        df.loc[name, 'national_anthem_duration_sec'] = anthem_duration[iso3]
add_to_codebook('national_anthem_duration_sec',
                'Duration of national anthem in seconds',
                'Various musicological sources', 'bizarre')

# --- Number of national parks ---
national_parks = {
    'AUS': 685, 'USA': 63, 'CHN': 10, 'GBR': 15, 'FRA': 11, 'DEU': 16,
    'ITA': 25, 'ESP': 16, 'BRA': 74, 'CAN': 48, 'IND': 106, 'JPN': 34,
    'KOR': 22, 'MEX': 67, 'ARG': 47, 'RUS': 64, 'ZAF': 22, 'NZL': 13,
    'IDN': 54, 'THA': 131, 'COL': 60, 'PER': 15, 'CHL': 42, 'VEN': 43,
    'ECU': 11, 'BOL': 22, 'CRI': 30, 'PAN': 15, 'NGA': 8, 'KEN': 23,
    'TZA': 22, 'ETH': 22, 'GHA': 7, 'UGA': 10, 'ZMB': 20, 'ZWE': 10,
    'BWA': 4, 'NAM': 20, 'MOZ': 7, 'MDG': 6, 'CMR': 14, 'SEN': 6,
    'COD': 8, 'AGO': 6, 'RWA': 4, 'MWI': 5, 'GAB': 13,
    'POL': 23, 'CZE': 4, 'SVK': 9, 'HUN': 10, 'ROU': 14, 'BGR': 3,
    'HRV': 8, 'SVN': 1, 'SRB': 5, 'GRC': 2, 'TUR': 46, 'ISR': 3,
    'NOR': 47, 'SWE': 30, 'FIN': 40, 'DNK': 5, 'ISL': 3, 'IRL': 6,
    'PRT': 1, 'NLD': 20, 'BEL': 0, 'CHE': 1, 'AUT': 6, 'EST': 6,
    'LVA': 4, 'LTU': 5, 'UKR': 50, 'BLR': 4, 'GEO': 14,
    'ARM': 4, 'AZE': 11, 'KAZ': 14, 'UZB': 3, 'MNG': 30,
    'IRN': 30, 'PAK': 35, 'BGD': 17, 'NPL': 12, 'LKA': 3,
    'VNM': 34, 'MYS': 28, 'PHL': 35, 'SGP': 0, 'MMR': 6,
    'KHM': 7, 'LAO': 24, 'FJI': 0, 'PNG': 0,
    'SAU': 15, 'EGY': 30, 'MAR': 12, 'TUN': 8, 'DZA': 11,
    'JOR': 9, 'DOM': 29, 'CUB': 14, 'JAM': 2, 'GTM': 34,
    'HND': 18, 'SLV': 1, 'NIC': 78, 'BLZ': 2,
}

df['national_parks_count'] = 0
for name in df.index:
    iso3 = name_to_iso3.get(name)
    if iso3 and iso3 in national_parks:
        df.loc[name, 'national_parks_count'] = national_parks[iso3]
add_to_codebook('national_parks_count',
                'Number of designated national parks',
                'Various government and IUCN sources', 'bizarre')

print(f"  ✓ Added 9 web-sourced bizarre features")

# ============================================================================
# SAVE
# ============================================================================
df = df.fillna(0)
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_df.to_csv('codebook.csv', index=False)

role_counts = codebook_df['role'].value_counts()
print(f"\n" + "=" * 80)
print(f"DONE! Dataset: {df.shape[0]} countries × {df.shape[1]} features")
print(f"  Target:   {role_counts.get('target', 0)}")
print(f"  Causal:   {role_counts.get('causal', 0)}")
print(f"  Bizarre:  {role_counts.get('bizarre', 0)}")
print(f"  Noise:    {role_counts.get('noise', 0)}")
print(f"  Missing:  {df.isnull().sum().sum()}")
print("=" * 80)
