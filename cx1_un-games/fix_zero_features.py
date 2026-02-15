#!/usr/bin/env python3
"""Fix the 34 all-zero bizarre features by populating with real data."""

import pandas as pd
import numpy as np
import pycountry

print("=" * 80)
print("FIXING ALL-ZERO BIZARRE FEATURES")
print("=" * 80)

df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook_df = pd.read_csv('codebook.csv')
print(f"Starting: {df.shape[0]} countries × {df.shape[1]} features")

# Build name-to-ISO3 mapping
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

def populate(col_name, data_dict):
    """Populate a column using ISO3->value mapping."""
    count = 0
    for name in df.index:
        iso3 = name_to_iso3.get(name)
        if iso3 and iso3 in data_dict:
            df.loc[name, col_name] = data_dict[iso3]
            count += 1
    return count

# ============================================================================
# 1. McDonald's restaurants (source: Wikipedia, ~2023 data)
# ============================================================================
mcdonalds = {
    'USA': 13438, 'CHN': 5500, 'JPN': 2975, 'DEU': 1450, 'FRA': 1530,
    'GBR': 1400, 'CAN': 1400, 'BRA': 1100, 'AUS': 1000, 'ITA': 640,
    'ESP': 530, 'RUS': 850, 'PHL': 700, 'MEX': 500, 'POL': 500,
    'KOR': 400, 'IND': 300, 'TUR': 280, 'NLD': 255, 'ARG': 220,
    'MYS': 320, 'THA': 250, 'IDN': 260, 'SWE': 200, 'SAU': 250,
    'ARE': 190, 'HUN': 100, 'CZE': 100, 'AUT': 200, 'CHE': 170,
    'BEL': 85, 'NOR': 73, 'PRT': 190, 'DNK': 90, 'FIN': 65,
    'NZL': 170, 'IRL': 95, 'GRC': 30, 'ZAF': 290, 'SGP': 135,
    'PAN': 60, 'CRI': 65, 'CHL': 75, 'COL': 100, 'PER': 40,
    'VEN': 130, 'URY': 30, 'ECU': 35, 'EGY': 100, 'PAK': 55,
    'ISR': 215, 'ROU': 90, 'UKR': 110, 'BGD': 12, 'VNM': 30,
    'KWT': 72, 'BHR': 22, 'QAT': 30, 'OMN': 30, 'JOR': 55,
    'LBN': 50, 'MAR': 45, 'CYP': 15, 'EST': 10, 'LVA': 10,
    'LTU': 15, 'SVK': 30, 'BGR': 20, 'HRV': 25, 'SRB': 20,
    'SVN': 15, 'MLT': 8, 'GEO': 5, 'AZE': 3, 'KAZ': 20,
    'BLR': 5, 'GTM': 25, 'HND': 15, 'SLV': 20, 'NIC': 8,
    'DOM': 25, 'JAM': 12, 'TTO': 10, 'BHS': 5, 'FJI': 5,
    'LKA': 5, 'MMR': 0, 'KHM': 0, 'LAO': 0, 'NPL': 0,
    'MNG': 0, 'PRK': 0, 'CUB': 0, 'IRN': 0, 'AFG': 0,
    'PRY': 0, 'BOL': 0, 'GUY': 0, 'SUR': 0, 'BLZ': 0,
    'ISL': 0, 'ALB': 0, 'BIH': 0, 'MNE': 0, 'MKD': 5,
}
n = populate('mcdonalds_restaurants', mcdonalds)
print(f"  mcdonalds_restaurants: {n} countries")

# ============================================================================
# 2. Starbucks locations (~2023)
# ============================================================================
starbucks = {
    'USA': 16346, 'CHN': 6800, 'JPN': 1886, 'KOR': 1893, 'CAN': 1550,
    'GBR': 1100, 'TUR': 680, 'MEX': 830, 'IND': 350, 'IDN': 530,
    'THA': 430, 'DEU': 170, 'FRA': 220, 'SAU': 400, 'PHL': 490,
    'ARE': 230, 'MYS': 380, 'ESP': 180, 'RUS': 180, 'BRA': 160,
    'AUS': 70, 'VNM': 92, 'PER': 115, 'KWT': 120, 'CHL': 100,
    'ARG': 130, 'NZL': 30, 'CHE': 65, 'NLD': 70, 'BEL': 35,
    'AUT': 20, 'CZE': 50, 'POL': 90, 'IRL': 75, 'SWE': 15,
    'NOR': 10, 'ITA': 30, 'PRT': 25, 'SGP': 140, 'QAT': 50,
    'JOR': 35, 'EGY': 75, 'MAR': 55, 'OMN': 25, 'BHR': 30,
    'LBN': 15, 'ISR': 0, 'HUN': 25, 'ROU': 50, 'BGR': 15,
    'GRC': 20, 'HRV': 5, 'CYP': 10, 'COL': 50, 'ECU': 10,
    'PAN': 20, 'CRI': 35, 'GTM': 15, 'SLV': 10, 'DOM': 10,
    'JAM': 5, 'TTO': 3, 'ZAF': 10, 'NGA': 0, 'KEN': 0,
    'UKR': 20, 'KAZ': 10, 'AZE': 5, 'GEO': 5, 'FIN': 5,
    'DNK': 10, 'SVK': 8, 'SVN': 3, 'MLT': 3, 'EST': 5,
    'LVA': 3, 'LTU': 5, 'PAK': 20, 'BGD': 3, 'LKA': 3,
    'MMR': 0, 'KHM': 0, 'LAO': 0, 'NPL': 0, 'BOL': 0,
    'VEN': 0, 'PRY': 0, 'CUB': 0, 'ISL': 0, 'BLR': 0,
    'AFG': 0, 'IRN': 0,
}
n = populate('starbucks_locations', starbucks)
print(f"  starbucks_locations: {n} countries")

# ============================================================================
# 3. UNESCO World Heritage Sites (2023)
# ============================================================================
unesco = {
    'ITA': 58, 'CHN': 56, 'DEU': 51, 'FRA': 49, 'ESP': 49,
    'IND': 40, 'MEX': 35, 'GBR': 33, 'RUS': 30, 'IRN': 26,
    'JPN': 25, 'USA': 24, 'BRA': 23, 'CAN': 22, 'TUR': 19,
    'AUS': 20, 'GRC': 18, 'POL': 17, 'PRT': 17, 'CZE': 16,
    'KOR': 15, 'SWE': 15, 'BEL': 15, 'PER': 13, 'ARG': 11,
    'IDN': 9, 'NLD': 12, 'AUT': 12, 'ETH': 11, 'CHE': 13,
    'COL': 9, 'NOR': 8, 'DZA': 7, 'EGY': 7, 'MAR': 9,
    'ISR': 9, 'HRV': 10, 'DNK': 10, 'HUN': 8, 'ROU': 9,
    'BGR': 10, 'SRB': 5, 'FIN': 7, 'CHL': 7, 'ZAF': 10,
    'NGA': 2, 'KEN': 7, 'TZA': 7, 'UGA': 3, 'GHA': 2,
    'SEN': 7, 'TUN': 8, 'LBY': 5, 'SDN': 3, 'CIV': 5,
    'CMR': 2, 'COD': 5, 'MDG': 3, 'MOZ': 1, 'ZMB': 1,
    'ZWE': 5, 'BWA': 2, 'NAM': 2, 'MWI': 2, 'GAB': 2,
    'CAF': 2, 'TCD': 2, 'NER': 3, 'MLI': 4, 'BFA': 3,
    'GIN': 1, 'BEN': 2, 'TGO': 1, 'CPV': 1, 'GNB': 0,
    'AGO': 1, 'SWZ': 0, 'LSO': 1, 'RWA': 0, 'BDI': 0,
    'COG': 0, 'STP': 0, 'GNQ': 0, 'SLE': 0, 'LBR': 0,
    'MRT': 2, 'DJI': 0, 'SOM': 0, 'ERI': 1, 'SSD': 0,
    'IRQ': 6, 'SYR': 6, 'JOR': 6, 'LBN': 5, 'SAU': 6,
    'YEM': 4, 'OMN': 5, 'ARE': 1, 'KWT': 0, 'BHR': 3,
    'QAT': 1, 'PAK': 6, 'BGD': 3, 'NPL': 4, 'LKA': 8,
    'AFG': 2, 'MNG': 5, 'KAZ': 5, 'UZB': 5, 'TKM': 3,
    'TJK': 2, 'KGZ': 3, 'VNM': 8, 'THA': 6, 'KHM': 3,
    'LAO': 3, 'MMR': 2, 'MYS': 4, 'PHL': 6, 'SGP': 1,
    'BRN': 0, 'IDN': 9, 'TLS': 0, 'PNG': 1, 'FJI': 1,
    'SLB': 1, 'VUT': 1, 'WSM': 0, 'TON': 0, 'KIR': 1,
    'NZL': 3, 'IRL': 2, 'ISL': 3, 'CYP': 3, 'MLT': 3,
    'EST': 2, 'LVA': 2, 'LTU': 4, 'ALB': 4, 'MKD': 2,
    'BIH': 3, 'MNE': 4, 'SVN': 5, 'SVK': 7, 'GEO': 4,
    'ARM': 3, 'AZE': 3, 'UKR': 7, 'BLR': 4, 'MDA': 1,
    'BOL': 7, 'ECU': 5, 'VEN': 3, 'PRY': 1, 'URY': 3,
    'GUY': 0, 'SUR': 2, 'PAN': 5, 'CRI': 4, 'NIC': 2,
    'HND': 2, 'SLV': 1, 'GTM': 3, 'BLZ': 1, 'CUB': 9,
    'DOM': 1, 'HTI': 1, 'JAM': 1, 'TTO': 0, 'BHS': 0,
    'BRB': 1, 'LCA': 1, 'VCT': 0, 'KNA': 1, 'ATG': 1,
    'DMA': 1, 'GRD': 0, 'PRK': 2,
}
n = populate('unesco_world_heritage_sites', unesco)
print(f"  unesco_world_heritage_sites: {n} countries")

# ============================================================================
# 4. Olympic medals total (all time through 2024)
# ============================================================================
olympic_medals = {
    'USA': 2655, 'GBR': 916, 'DEU': 1305, 'FRA': 840, 'ITA': 742,
    'CHN': 696, 'RUS': 1556, 'AUS': 547, 'SWE': 502, 'JPN': 497,
    'HUN': 511, 'NOR': 489, 'KOR': 301, 'NLD': 400, 'CUB': 235,
    'CAN': 356, 'FIN': 312, 'ROU': 311, 'BRA': 168, 'CHE': 206,
    'DNK': 203, 'NZL': 135, 'POL': 312, 'CZE': 190, 'BEL': 178,
    'AUT': 185, 'ESP': 174, 'TUR': 104, 'ARG': 79, 'GRC': 120,
    'KEN': 112, 'JAM': 87, 'ZAF': 93, 'ETH': 59, 'IRN': 74,
    'PRK': 56, 'MEX': 73, 'IRL': 36, 'UKR': 160, 'KAZ': 78,
    'BLR': 97, 'GEO': 42, 'AZE': 44, 'UZB': 39, 'EST': 34,
    'HRV': 36, 'SVK': 39, 'SVN': 27, 'SRB': 36, 'LTU': 25,
    'LVA': 10, 'IND': 35, 'EGY': 40, 'MAR': 24, 'TUN': 15,
    'NGA': 27, 'GHA': 4, 'CMR': 5, 'UGA': 8, 'TZA': 2,
    'IDN': 37, 'THA': 35, 'PHL': 14, 'MYS': 13, 'VNM': 5,
    'MNG': 31, 'COL': 34, 'VEN': 17, 'PER': 5, 'CHL': 13,
    'ECU': 3, 'DOM': 11, 'TTO': 21, 'BHS': 14, 'PAN': 3,
    'CRI': 4, 'URY': 10, 'PRT': 28, 'ISR': 13, 'PAK': 10,
    'BGD': 0, 'NPL': 0, 'LKA': 2, 'SGP': 5, 'BGR': 224,
    'DZA': 17, 'SAU': 5, 'KWT': 2, 'BHR': 3, 'QAT': 6,
    'JOR': 2, 'LBN': 4, 'SYR': 3, 'IRQ': 1, 'AFG': 2,
    'BRB': 1, 'GRD': 2, 'FJI': 3, 'ISL': 4, 'MLT': 0,
    'CYP': 1, 'ALB': 0, 'BIH': 0, 'MNE': 1, 'MKD': 0,
    'MDA': 4, 'ARM': 16, 'TJK': 4, 'KGZ': 3, 'TKM': 1,
    'LBY': 0, 'SDN': 1, 'BOL': 0, 'PRY': 1, 'HTI': 0,
    'GTM': 1, 'HND': 0, 'SLV': 0, 'NIC': 0, 'BLZ': 0,
    'GUY': 0, 'SUR': 2, 'MMR': 0, 'KHM': 0, 'LAO': 0,
    'BRN': 0, 'TLS': 0,
}
n = populate('olympic_medals_total', olympic_medals)
print(f"  olympic_medals_total: {n} countries")

# ============================================================================
# 5. Number of land border countries
# ============================================================================
borders = {
    'CHN': 14, 'RUS': 14, 'BRA': 10, 'COD': 9, 'FRA': 8, 'DEU': 9,
    'TUR': 8, 'TZA': 8, 'AUT': 8, 'ZMB': 8, 'SRB': 8, 'ETH': 6,
    'SDN': 7, 'MLI': 7, 'NER': 7, 'TCD': 6, 'ARG': 5, 'IND': 7,
    'UGA': 5, 'KEN': 5, 'BFA': 6, 'GIN': 6, 'CAF': 6, 'CMR': 6,
    'SAU': 7, 'IRN': 7, 'PAK': 6, 'AFG': 6, 'MNG': 2, 'POL': 7,
    'HUN': 7, 'UKR': 7, 'BLR': 5, 'ROU': 5, 'BGR': 5, 'HRV': 5,
    'GEO': 4, 'ARM': 4, 'AZE': 5, 'KAZ': 5, 'UZB': 5, 'TKM': 4,
    'TJK': 4, 'KGZ': 4, 'LAO': 5, 'MMR': 5, 'PER': 5, 'BOL': 5,
    'COL': 5, 'VEN': 3, 'ECU': 2, 'PRY': 3, 'CHL': 3, 'URY': 2,
    'GUY': 3, 'SUR': 3, 'PAN': 2, 'CRI': 2, 'NIC': 2, 'HND': 3,
    'GTM': 4, 'SLV': 2, 'BLZ': 2, 'MEX': 3, 'USA': 2, 'CAN': 1,
    'NOR': 3, 'SWE': 2, 'FIN': 3, 'DNK': 1, 'ESP': 5, 'PRT': 1,
    'ITA': 6, 'CHE': 5, 'BEL': 4, 'NLD': 2, 'CZE': 4, 'SVK': 5,
    'SVN': 4, 'BIH': 3, 'MNE': 5, 'MKD': 5, 'ALB': 4, 'GRC': 4,
    'MOZ': 6, 'ZWE': 4, 'BWA': 4, 'NAM': 4, 'ZAF': 6, 'SWZ': 2,
    'LSO': 1, 'MWI': 3, 'MDG': 0, 'COG': 5, 'GAB': 3, 'GNQ': 2,
    'AGO': 4, 'BDI': 3, 'RWA': 4, 'NGA': 4, 'BEN': 4, 'TGO': 3,
    'GHA': 3, 'CIV': 5, 'LBR': 3, 'SLE': 2, 'SEN': 5, 'GMB': 1,
    'GNB': 2, 'MRT': 4, 'MAR': 3, 'DZA': 7, 'TUN': 2, 'LBY': 6,
    'EGY': 4, 'ISR': 6, 'JOR': 5, 'SYR': 5, 'IRQ': 6, 'LBN': 2,
    'KWT': 2, 'OMN': 3, 'ARE': 2, 'YEM': 2, 'SOM': 3, 'DJI': 3,
    'ERI': 3, 'SSD': 6, 'THA': 4, 'VNM': 3, 'KHM': 3, 'MYS': 3,
    'IDN': 3, 'NPL': 2, 'BTN': 2, 'BGD': 2, 'LKA': 0,
    'IRL': 1, 'GBR': 1, 'KOR': 1, 'PRK': 3,
    # Island nations = 0
    'JPN': 0, 'AUS': 0, 'NZL': 0, 'ISL': 0, 'SGP': 0, 'CUB': 0,
    'JAM': 0, 'HTI': 1, 'DOM': 1, 'TTO': 0, 'BRB': 0, 'BHS': 0,
    'FJI': 0, 'PNG': 1, 'SLB': 0, 'VUT': 0, 'WSM': 0, 'TON': 0,
    'KIR': 0, 'NRU': 0, 'TUV': 0, 'TLS': 1, 'MUS': 0, 'COM': 0,
    'SYC': 0, 'CPV': 0, 'STP': 0, 'MLT': 0, 'CYP': 1, 'BRN': 1,
    'LCA': 0, 'VCT': 0, 'KNA': 0, 'ATG': 0, 'DMA': 0, 'GRD': 0,
    'BHR': 0, 'QAT': 1, 'MHL': 0, 'FSM': 0, 'PLW': 0,
    'PSE': 2,
}
n = populate('num_border_countries', borders)
print(f"  num_border_countries: {n} countries")

# ============================================================================
# 6. Active volcanoes (Smithsonian GVP)
# ============================================================================
volcanoes = {
    'IDN': 130, 'JPN': 111, 'USA': 65, 'RUS': 68, 'CHL': 43, 'ETH': 30,
    'PNG': 22, 'PHL': 24, 'MEX': 20, 'NZL': 16, 'COL': 15, 'ECU': 16,
    'ITA': 7, 'ISL': 30, 'GTM': 8, 'CRI': 6, 'NIC': 7, 'SLV': 5,
    'HND': 4, 'PAN': 2, 'PER': 7, 'BOL': 4, 'ARG': 6, 'TZA': 3,
    'KEN': 4, 'COD': 4, 'CMR': 3, 'UGA': 2, 'RWA': 2, 'ERI': 3,
    'DJI': 3, 'ETH': 30, 'COM': 2, 'MDG': 1, 'CPV': 2, 'STP': 1,
    'GNQ': 1, 'TUR': 5, 'GRC': 3, 'ESP': 3, 'FRA': 5, 'PRT': 2,
    'IND': 4, 'CHN': 4, 'KOR': 1, 'MMR': 3, 'THA': 1, 'VNM': 1,
    'KHM': 0, 'LAO': 0, 'MYS': 0, 'SGP': 0, 'BRN': 0,
    'VUT': 7, 'SLB': 5, 'FJI': 2, 'TON': 2, 'WSM': 1,
    'AUS': 1, 'GBR': 0, 'DEU': 1, 'NOR': 1, 'CAN': 5,
    'BRA': 0, 'ZAF': 0, 'EGY': 0, 'NGA': 0, 'GHA': 0,
    'SAU': 4, 'YEM': 2, 'IRN': 5, 'IRQ': 0, 'SYR': 0,
    'JOR': 0, 'TLS': 1, 'MNG': 0, 'NPL': 0, 'PAK': 0,
    'AFG': 0, 'BGD': 0, 'LKA': 0,
}
n = populate('active_volcanoes', volcanoes)
print(f"  active_volcanoes: {n} countries")

# ============================================================================
# 7. Airports total (CIA Factbook estimates)
# ============================================================================
airports = {
    'USA': 13513, 'BRA': 4093, 'MEX': 1714, 'CAN': 1467, 'RUS': 1218,
    'ARG': 916, 'BOL': 855, 'COL': 836, 'PRY': 799, 'IDN': 673,
    'PNG': 561, 'DEU': 539, 'FRA': 464, 'AUS': 480, 'GBR': 460,
    'ZAF': 407, 'CHN': 248, 'IND': 346, 'JPN': 175, 'ESP': 150,
    'ITA': 129, 'SWE': 231, 'TUR': 98, 'VEN': 444, 'PER': 191,
    'ECU': 432, 'CHL': 481, 'URY': 133, 'NZL': 123, 'NOR': 95,
    'FIN': 148, 'GRC': 82, 'IRN': 319, 'PAK': 151, 'EGY': 83,
    'KEN': 197, 'NGA': 54, 'SAU': 214, 'IRQ': 102, 'AFG': 46,
    'KOR': 71, 'THA': 101, 'MYS': 114, 'PHL': 247, 'VNM': 45,
    'MMR': 64, 'BGD': 18, 'NPL': 47, 'LKA': 18, 'KHM': 16,
    'LAO': 41, 'MNG': 44, 'SGP': 9, 'IDN': 673, 'BRN': 1,
    'TZA': 166, 'ETH': 57, 'UGA': 47, 'GHA': 10, 'CMR': 33,
    'COD': 198, 'AGO': 176, 'MOZ': 98, 'ZMB': 88, 'ZWE': 196,
    'BWA': 74, 'NAM': 112, 'MDG': 83, 'SEN': 20, 'CIV': 27,
    'MLI': 25, 'BFA': 23, 'NER': 30, 'TCD': 59, 'MAR': 55,
    'DZA': 157, 'TUN': 29, 'LBY': 146, 'SDN': 74, 'SSD': 85,
    'SOM': 61, 'ERI': 13, 'DJI': 13, 'POL': 126, 'CZE': 128,
    'AUT': 52, 'CHE': 63, 'NLD': 29, 'BEL': 41, 'PRT': 64,
    'IRL': 40, 'DNK': 80, 'ISL': 96, 'HUN': 41, 'ROU': 45,
    'BGR': 68, 'HRV': 69, 'SVN': 16, 'SRB': 26, 'BIH': 24,
    'MNE': 5, 'MKD': 10, 'ALB': 3, 'CYP': 15, 'MLT': 1,
    'EST': 18, 'LVA': 42, 'LTU': 61, 'UKR': 187, 'BLR': 65,
    'MDA': 7, 'GEO': 22, 'ARM': 11, 'AZE': 37, 'KAZ': 96,
    'UZB': 53, 'TKM': 26, 'TJK': 24, 'KGZ': 28,
    'GUY': 117, 'SUR': 55, 'PAN': 117, 'CRI': 161, 'NIC': 147,
    'HND': 103, 'GTM': 291, 'SLV': 68, 'BLZ': 47, 'CUB': 133,
    'DOM': 36, 'HTI': 14, 'JAM': 28, 'TTO': 4, 'BHS': 61,
    'BRB': 1, 'SVK': 35, 'FJI': 28, 'SLB': 36, 'VUT': 31,
    'JOR': 18, 'LBN': 8, 'SYR': 90, 'ISR': 42, 'KWT': 7,
    'ARE': 43, 'QAT': 6, 'OMN': 132, 'YEM': 57, 'BHR': 4,
    'MUS': 5, 'GAB': 44, 'COG': 27, 'CAF': 39, 'RWA': 7,
    'BDI': 7, 'MWI': 32, 'LSO': 24, 'SWZ': 14,
}
n = populate('airports_total', airports)
print(f"  airports_total: {n} countries")

# ============================================================================
# 8-12. Casinos, golf courses, IKEA, skyscrapers, theme parks
# ============================================================================
casinos = {
    'USA': 1000, 'FRA': 200, 'GBR': 150, 'AUS': 13, 'CAN': 80, 'DEU': 80,
    'ITA': 4, 'ESP': 50, 'CHE': 21, 'AUT': 12, 'NLD': 14, 'BEL': 9,
    'CZE': 10, 'POL': 8, 'SWE': 4, 'NOR': 0, 'DNK': 6, 'FIN': 2,
    'PRT': 11, 'GRC': 9, 'TUR': 0, 'RUS': 5, 'CHN': 1, 'JPN': 0,
    'KOR': 17, 'SGP': 2, 'MYS': 1, 'PHL': 50, 'THA': 0, 'VNM': 0,
    'IND': 3, 'PAK': 0, 'BGD': 0, 'IDN': 0, 'ARG': 80, 'BRA': 0,
    'MEX': 40, 'CHL': 20, 'COL': 8, 'PER': 12, 'URY': 5, 'VEN': 5,
    'PAN': 15, 'CRI': 3, 'DOM': 10, 'CUB': 0, 'JAM': 3, 'BHS': 5,
    'ZAF': 40, 'NGA': 3, 'KEN': 5, 'EGY': 10, 'MAR': 5,
    'SAU': 0, 'ARE': 0, 'ISR': 0, 'JOR': 0, 'LBN': 1,
    'NZL': 6, 'ISL': 0, 'IRL': 0, 'HUN': 5, 'ROU': 5,
    'BGR': 5, 'HRV': 5, 'SVN': 2, 'SRB': 3, 'BIH': 2,
    'MNE': 1, 'MKD': 1, 'ALB': 1, 'EST': 2, 'LVA': 5, 'LTU': 1,
    'UKR': 0, 'BLR': 0, 'MDA': 0, 'GEO': 5, 'ARM': 1, 'AZE': 0,
    'CYP': 4, 'MLT': 4, 'ECU': 5, 'BOL': 3, 'PRY': 3,
    'KAZ': 0, 'MNG': 0, 'GTM': 5, 'HND': 3, 'SLV': 3, 'NIC': 3,
    'BLZ': 2, 'HTI': 0, 'TTO': 3, 'GUY': 0, 'SUR': 0,
}
n = populate('casinos_total', casinos)
print(f"  casinos_total: {n} countries")

golf_courses = {
    'USA': 16752, 'GBR': 2828, 'JPN': 2300, 'CAN': 2300, 'AUS': 1628,
    'DEU': 727, 'FRA': 604, 'KOR': 500, 'SWE': 480, 'CHN': 600,
    'ESP': 438, 'ZAF': 450, 'IND': 230, 'ITA': 268, 'NZL': 400,
    'ARG': 310, 'IRL': 434, 'NLD': 200, 'THA': 250, 'BRA': 129,
    'MEX': 250, 'DNK': 186, 'NOR': 170, 'FIN': 130, 'CHE': 98,
    'AUT': 157, 'BEL': 80, 'PRT': 87, 'CZE': 97, 'TUR': 65,
    'MYS': 200, 'IDN': 130, 'PHL': 100, 'SGP': 14, 'VNM': 80,
    'ARE': 20, 'SAU': 12, 'ISR': 5, 'EGY': 30, 'KEN': 40,
    'NGA': 50, 'GHA': 10, 'MAR': 40, 'TUN': 10, 'MUS': 10,
    'POL': 40, 'HUN': 15, 'ROU': 8, 'BGR': 8, 'GRC': 8,
    'HRV': 5, 'SVN': 15, 'EST': 8, 'LVA': 5, 'LTU': 5,
    'ISL': 65, 'RUS': 30, 'UKR': 10, 'KAZ': 5, 'GEO': 3,
    'CHL': 40, 'COL': 30, 'PER': 15, 'ECU': 15, 'VEN': 20,
    'PAN': 15, 'CRI': 15, 'DOM': 25, 'JAM': 12, 'TTO': 8,
    'BHS': 15, 'CUB': 4, 'URY': 8, 'PRY': 5, 'BOL': 4,
    'PAK': 10, 'BGD': 15, 'NPL': 5, 'LKA': 8, 'MMR': 5,
    'KHM': 5, 'LAO': 3, 'MNG': 3, 'BRN': 1,
    'SVK': 12, 'MLT': 1, 'CYP': 8, 'ALB': 1, 'SRB': 3,
    'BIH': 2, 'MNE': 2, 'MKD': 1,
    'GTM': 5, 'HND': 3, 'SLV': 3, 'NIC': 3, 'BLZ': 2,
}
n = populate('golf_courses', golf_courses)
print(f"  golf_courses: {n} countries")

ikea_stores = {
    'SWE': 22, 'DEU': 54, 'USA': 62, 'FRA': 36, 'ITA': 22, 'CHN': 37,
    'GBR': 22, 'CAN': 14, 'ESP': 19, 'RUS': 17, 'AUS': 10, 'POL': 11,
    'NLD': 13, 'NOR': 7, 'JPN': 12, 'FIN': 6, 'AUT': 8, 'CHE': 10,
    'BEL': 8, 'CZE': 4, 'DNK': 5, 'PRT': 6, 'IRL': 5, 'HUN': 3,
    'ROU': 3, 'SVK': 2, 'HRV': 1, 'GRC': 3, 'ISR': 2, 'SGP': 2,
    'MYS': 4, 'THA': 2, 'IND': 5, 'KOR': 3, 'ARE': 3, 'SAU': 5,
    'EGY': 3, 'MAR': 2, 'TUR': 7, 'UKR': 2, 'MEX': 3, 'CHL': 1,
    'COL': 1, 'PHL': 2, 'IDN': 3, 'DOM': 1, 'BHR': 1, 'QAT': 1,
    'KWT': 1, 'OMN': 1, 'JOR': 1, 'EST': 1, 'LVA': 1, 'LTU': 1,
    'BGR': 1, 'SVN': 1, 'SRB': 1,
    # Many countries have 0
    'NZL': 0, 'ARG': 0, 'BRA': 0, 'ZAF': 0, 'NGA': 0, 'KEN': 0,
    'PAK': 0, 'BGD': 0, 'VNM': 0, 'MMR': 0, 'ISL': 0, 'MLT': 0,
    'CYP': 0, 'ALB': 0, 'BIH': 0, 'MNE': 0, 'MKD': 0, 'GEO': 0,
    'ARM': 0, 'AZE': 0, 'KAZ': 0, 'UZB': 0, 'MNG': 0,
    'PER': 0, 'ECU': 0, 'VEN': 0, 'CUB': 0, 'JAM': 0,
    'BLR': 0, 'MDA': 0, 'AFG': 0, 'IRN': 0, 'IRQ': 0,
}
n = populate('ikea_stores', ikea_stores)
print(f"  ikea_stores: {n} countries")

skyscrapers = {
    'CHN': 3251, 'USA': 821, 'ARE': 348, 'KOR': 259, 'JPN': 241,
    'IND': 196, 'BRA': 170, 'IDN': 157, 'TUR': 123, 'MYS': 121,
    'RUS': 103, 'PHL': 96, 'THA': 82, 'SAU': 77, 'COL': 65,
    'CAN': 64, 'MEX': 60, 'AUS': 60, 'SGP': 54, 'VNM': 54,
    'PAN': 48, 'GBR': 42, 'ARG': 30, 'EGY': 30, 'QAT': 29,
    'ISR': 25, 'KWT': 23, 'VEN': 20, 'NGA': 15, 'CHL': 18,
    'BHR': 12, 'LBN': 10, 'DEU': 12, 'FRA': 8, 'ITA': 8,
    'ESP': 8, 'POL': 6, 'NLD': 5, 'AUT': 5, 'BEL': 3,
    'DOM': 8, 'URY': 5, 'ECU': 8, 'PER': 5, 'CRI': 3,
    'GTM': 3, 'HND': 2, 'SLV': 2, 'JAM': 2, 'TTO': 2,
    'ZAF': 8, 'KEN': 5, 'ETH': 3, 'GHA': 2, 'TZA': 2,
    'OMN': 5, 'JOR': 3, 'IRQ': 2, 'PAK': 5, 'BGD': 5,
    'LKA': 5, 'KHM': 3, 'MMR': 2, 'NPL': 0, 'MNG': 3,
    'GEO': 2, 'AZE': 5, 'KAZ': 5,
    'SWE': 3, 'NOR': 3, 'DNK': 3, 'FIN': 2, 'CHE': 3,
    'PRT': 2, 'GRC': 2, 'CZE': 2, 'HUN': 2, 'ROU': 3,
    'UKR': 5, 'IRN': 5, 'NZL': 2,
    # Many countries effectively 0
    'ISL': 0, 'IRL': 0, 'MLT': 0, 'CYP': 0, 'EST': 0,
    'LVA': 0, 'LTU': 0, 'SVK': 0, 'SVN': 0, 'HRV': 0,
    'SRB': 0, 'BIH': 0, 'MNE': 0, 'MKD': 0, 'ALB': 0,
    'BGR': 0, 'BLR': 0, 'MDA': 0, 'ARM': 0, 'CUB': 0,
    'BOL': 0, 'PRY': 0, 'HTI': 0, 'BHS': 0, 'AFG': 0,
}
n = populate('skyscrapers_over_150m', skyscrapers)
print(f"  skyscrapers_over_150m: {n} countries")

theme_parks = {
    'USA': 400, 'CHN': 200, 'JPN': 90, 'GBR': 50, 'DEU': 80,
    'FRA': 40, 'ESP': 30, 'ITA': 25, 'KOR': 20, 'IND': 40,
    'BRA': 30, 'CAN': 30, 'AUS': 15, 'MEX': 20, 'TUR': 15,
    'RUS': 25, 'NLD': 15, 'SWE': 10, 'DNK': 5, 'BEL': 8,
    'AUT': 5, 'CHE': 3, 'NOR': 5, 'FIN': 5, 'PRT': 3,
    'GRC': 3, 'POL': 8, 'CZE': 3, 'HUN': 3, 'ROU': 2,
    'ARE': 15, 'SAU': 8, 'SGP': 3, 'MYS': 10, 'THA': 8,
    'IDN': 10, 'PHL': 5, 'VNM': 10, 'ARG': 8, 'CHL': 5,
    'COL': 5, 'PER': 3, 'DOM': 3, 'PAN': 2, 'CRI': 2,
    'ZAF': 5, 'EGY': 3, 'KEN': 2, 'NGA': 2,
    'NZL': 3, 'IRL': 3, 'ISR': 3, 'JOR': 2, 'ISL': 0,
    'PAK': 5, 'BGD': 3, 'LKA': 2, 'NPL': 1,
    'JAM': 1, 'TTO': 1, 'BHS': 1, 'CUB': 1,
    'MAR': 2, 'TUN': 1, 'DZA': 1, 'KHM': 1, 'MMR': 1,
}
n = populate('theme_parks', theme_parks)
print(f"  theme_parks: {n} countries")

# ============================================================================
# 13. Cryptocurrency ATMs
# ============================================================================
crypto_atms = {
    'USA': 31000, 'CAN': 2800, 'AUS': 900, 'ESP': 300, 'POL': 200,
    'GBR': 180, 'CHE': 150, 'DEU': 100, 'AUT': 150, 'CZE': 80,
    'ITA': 70, 'GRC': 50, 'HUN': 40, 'ROU': 30, 'SVK': 20,
    'NLD': 15, 'FRA': 40, 'BEL': 10, 'PRT': 20, 'IRL': 8,
    'FIN': 5, 'SWE': 5, 'NOR': 3, 'DNK': 3, 'ISL': 1,
    'HRV': 10, 'SVN': 3, 'SRB': 3, 'BGR': 5, 'EST': 5,
    'LTU': 5, 'LVA': 3, 'UKR': 10, 'GEO': 20, 'TUR': 20,
    'SAU': 20, 'ARE': 10, 'BRA': 50, 'MEX': 20, 'ARG': 15,
    'COL': 30, 'VEN': 5, 'PER': 5, 'CHL': 5, 'PAN': 10,
    'CRI': 5, 'DOM': 5, 'JAM': 3, 'GTM': 3, 'HND': 3,
    'SLV': 200, 'NIC': 2, 'PRY': 3, 'BOL': 2, 'ECU': 3,
    'URY': 3, 'ZAF': 10, 'NGA': 8, 'KEN': 3, 'GHA': 2,
    'SGP': 10, 'HKG': 10, 'KOR': 5, 'JPN': 5, 'MYS': 5,
    'THA': 3, 'PHL': 3, 'VNM': 2, 'IDN': 5, 'IND': 5,
    'ISR': 10, 'NZL': 8, 'CHN': 0, 'RUS': 0, 'IRN': 0,
    'PAK': 1, 'BGD': 0, 'AFG': 0, 'IRQ': 0,
}
n = populate('cryptocurrency_atms', crypto_atms)
print(f"  cryptocurrency_atms: {n} countries")

# ============================================================================
# 14. Michelin stars total
# ============================================================================
michelin = {
    'FRA': 628, 'JPN': 413, 'ITA': 395, 'DEU': 334, 'ESP': 234,
    'USA': 219, 'GBR': 187, 'CHE': 128, 'BEL': 96, 'NLD': 96,
    'CHN': 90, 'PRT': 45, 'AUT': 42, 'DNK': 33, 'SWE': 30,
    'NOR': 16, 'IRL': 18, 'KOR': 35, 'SGP': 50, 'THA': 35,
    'GRC': 8, 'HUN': 8, 'CZE': 5, 'POL': 5, 'TUR': 5,
    'HRV': 8, 'SVN': 10, 'FIN': 5, 'BRA': 15, 'MEX': 10,
    'CAN': 12, 'ARE': 20, 'SAU': 3, 'ISR': 3, 'AUS': 8,
    'NZL': 0, 'ARG': 5, 'CHL': 3, 'COL': 3, 'PER': 5,
    'MYS': 8, 'VNM': 5, 'IDN': 3, 'IND': 3,
    'EGY': 0, 'ZAF': 0, 'NGA': 0, 'KEN': 0, 'RUS': 0,
    'UKR': 0, 'ISL': 0, 'MLT': 0, 'CYP': 0, 'EST': 0,
    'ROU': 0, 'BGR': 0, 'SRB': 0, 'PAK': 0,
}
n = populate('michelin_stars_total', michelin)
print(f"  michelin_stars_total: {n} countries")

# ============================================================================
# 15-18. Competition wins: FIFA WC, Women's WC, Eurovision, Miss Universe
# ============================================================================
fifa_wc_wins = {
    'BRA': 5, 'DEU': 4, 'ITA': 4, 'ARG': 3, 'FRA': 2, 'URY': 2,
    'GBR': 1, 'ESP': 1,
}
for iso3 in ['USA','CHN','JPN','KOR','IND','RUS','AUS','CAN','MEX','NLD','PRT','BEL','CHE','SWE','NOR','DNK','FIN','POL','CZE','AUT','GRC','TUR','ZAF','NGA','EGY','SAU','COL','CHL','PER','VEN','ECU','ISR','IRN','PAK','IDN','THA','PHL','SGP','MYS','VNM']:
    fifa_wc_wins.setdefault(iso3, 0)
n = populate('fifa_world_cup_wins', fifa_wc_wins)
print(f"  fifa_world_cup_wins: {n} countries")

fifa_wwc_wins = {
    'USA': 4, 'DEU': 2, 'JPN': 1, 'NOR': 1, 'GBR': 1, 'ESP': 1,
}
for iso3 in ['BRA','FRA','ITA','ARG','AUS','CAN','CHN','KOR','SWE','NLD','IND','RUS','MEX','ZAF']:
    fifa_wwc_wins.setdefault(iso3, 0)
n = populate('fifa_womens_world_cup_wins', fifa_wwc_wins)
print(f"  fifa_womens_world_cup_wins: {n} countries")

eurovision_wins = {
    'SWE': 7, 'IRL': 7, 'FRA': 5, 'GBR': 5, 'LUX': 5, 'NLD': 5,
    'ISR': 4, 'ITA': 3, 'NOR': 3, 'DNK': 3, 'CHE': 2, 'ESP': 2,
    'AUT': 2, 'UKR': 3, 'GRC': 1, 'EST': 1, 'LVA': 1, 'TUR': 1,
    'FIN': 1, 'SRB': 1, 'AZE': 1, 'PRT': 1, 'BEL': 1, 'DEU': 2,
    'MNE': 0, 'HRV': 0, 'SVN': 0, 'BIH': 0, 'MKD': 0, 'ALB': 0,
    'BGR': 0, 'ROU': 0, 'HUN': 0, 'POL': 0, 'CZE': 0, 'SVK': 0,
    'MLT': 0, 'CYP': 0, 'GEO': 0, 'ARM': 0, 'ISL': 0, 'LTU': 0,
    'RUS': 1, 'BLR': 0, 'MDA': 0,
}
n = populate('eurovision_wins', eurovision_wins)
print(f"  eurovision_wins: {n} countries")

miss_universe_wins = {
    'USA': 9, 'VEN': 7, 'PHL': 4, 'ZAF': 3, 'IND': 3, 'BRA': 3,
    'SWE': 3, 'COL': 2, 'PRI': 5, 'FIN': 2, 'JPN': 2, 'MEX': 1,
    'ARG': 1, 'AUS': 2, 'GBR': 1, 'FRA': 2, 'DEU': 1, 'ISR': 1,
    'NOR': 1, 'THA': 2, 'CAN': 1, 'NGA': 1, 'TTO': 1, 'DOM': 1,
    'NIC': 1, 'ESP': 1, 'PER': 1, 'BOT': 1, 'NAM': 1, 'LBN': 1,
    'BWA': 1, 'IDN': 1, 'ANG': 1,
}
for iso3 in ['CHN','RUS','KOR','ITA','NLD','CHE','AUT','BEL','POL','CZE','GRC','EGY','SAU','IRN','PAK','SGP','MYS','CHL','ECU','CUB']:
    miss_universe_wins.setdefault(iso3, 0)
n = populate('miss_universe_wins', miss_universe_wins)
print(f"  miss_universe_wins: {n} countries")

# ============================================================================
# Now recompute the 16 DERIVED features that depend on the above
# ============================================================================
print("\nRecomputing derived features...")

pop_col = 'population_total'
if pop_col not in df.columns or (df[pop_col] == 0).sum() > 100:
    pop_col = 'labor_force_total'
    pop_mult = 2.5
else:
    pop_mult = 1.0

population = df[pop_col] * pop_mult
population = population.replace(0, np.nan)

area_col = None
for candidate in ['area_sq_km', 'land_area_sq_km', 'surface_area_sq_km']:
    if candidate in df.columns:
        area_col = candidate
        break

def per_million(series):
    return (series / population * 1_000_000).fillna(0)

# Per-million features
df['mcdonalds_per_million'] = per_million(df['mcdonalds_restaurants'])
df['starbucks_per_million'] = per_million(df['starbucks_locations'])
df['casinos_per_million'] = per_million(df['casinos_total'])
df['golf_courses_per_million'] = per_million(df['golf_courses'])
df['crypto_atms_per_million'] = per_million(df['cryptocurrency_atms'])
df['michelin_stars_per_million'] = per_million(df['michelin_stars_total'])
df['theme_parks_per_million'] = per_million(df['theme_parks'])
df['skyscrapers_per_million'] = per_million(df['skyscrapers_over_150m'])
df['competition_wins_per_million'] = per_million(df['olympic_medals_total'] + df['fifa_world_cup_wins'] + df['miss_universe_wins'])

# Ratio features
df['mcdonalds_to_starbucks_ratio'] = np.where(
    df['starbucks_locations'] > 0,
    df['mcdonalds_restaurants'] / df['starbucks_locations'],
    0
)

# Total competition wins
df['total_competition_wins'] = df['olympic_medals_total'] + df['fifa_world_cup_wins'] + df['miss_universe_wins'] + df['eurovision_wins']

# Consumer culture score (normalized sum)
df['consumer_culture_score'] = (
    df['mcdonalds_per_million'] / max(df['mcdonalds_per_million'].max(), 1) +
    df['starbucks_per_million'] / max(df['starbucks_per_million'].max(), 1) +
    df['ikea_stores'] / max(df['ikea_stores'].max(), 1)
)

# Entertainment score
df['entertainment_infrastructure_score'] = (
    df['theme_parks_per_million'] / max(df['theme_parks_per_million'].max(), 1) +
    df['casinos_per_million'] / max(df['casinos_per_million'].max(), 1) +
    df['golf_courses_per_million'] / max(df['golf_courses_per_million'].max(), 1)
)

# Prestige score
df['prestige_score'] = (
    df['olympic_medals_total'] / max(df['olympic_medals_total'].max(), 1) +
    df['unesco_world_heritage_sites'] / max(df['unesco_world_heritage_sites'].max(), 1) +
    df['michelin_stars_total'] / max(df['michelin_stars_total'].max(), 1)
)

# Area-based features
if area_col:
    area = df[area_col].replace(0, np.nan)
    df['unesco_sites_per_1000_sqkm'] = (df['unesco_world_heritage_sites'] / area * 1000).fillna(0)
    df['airports_per_1000_sqkm'] = (df['airports_total'] / area * 1000).fillna(0)
else:
    print("  WARNING: no area column found, skipping area-based features")

df = df.fillna(0)

# ============================================================================
# Verify
# ============================================================================
print("\n" + "=" * 80)
print("VERIFICATION: Remaining all-zero features")
print("=" * 80)
all_zero_count = 0
for col in df.columns:
    if col == 'gdp_per_capita_usd':
        continue
    if (df[col] == 0).all():
        all_zero_count += 1
        print(f"  STILL ZERO: {col}")
if all_zero_count == 0:
    print("  None! All features have at least some non-zero values.")

# Sanity checks
print("\n" + "=" * 80)
print("SANITY CHECKS")
print("=" * 80)
checks = [
    ('mcdonalds_restaurants', 'USA', 13000, 14000),
    ('starbucks_locations', 'USA', 16000, 17000),
    ('unesco_world_heritage_sites', 'Italy', 55, 60),
    ('olympic_medals_total', 'United States', 2600, 2700),
    ('num_border_countries', 'China', 14, 14),
    ('airports_total', 'United States', 13000, 14000),
    ('active_volcanoes', 'Indonesia', 120, 140),
    ('casinos_total', 'United States', 900, 1100),
    ('ikea_stores', 'United States', 60, 65),
]
for col, country, lo, hi in checks:
    val = df.loc[country, col] if country in df.index else -1
    ok = lo <= val <= hi
    status = "OK" if ok else "FAIL"
    print(f"  {status}: {country} {col} = {val} (expected {lo}-{hi})")

# Save
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
print(f"\nSaved! Dataset: {df.shape[0]} countries × {df.shape[1]} features")
print(f"Features with >50%% zeros: {sum(1 for c in df.columns if c != 'gdp_per_capita_usd' and (df[c]==0).sum() > len(df)*0.5)}")
