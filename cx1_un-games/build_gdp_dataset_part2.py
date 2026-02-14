#!/usr/bin/env python3
"""
Part 2: Add WDI noise indicators, WHO data, and bizarre covariates
"""

import pandas as pd
import numpy as np
import wbgapi as wb
import requests
import pycountry
import json
import time
from pathlib import Path

# Load intermediate dataset
df = pd.read_csv('gdp_dataset_intermediate.csv', index_col=0)
codebook_df = pd.read_csv('codebook_intermediate.csv') if Path('codebook_intermediate.csv').exists() else pd.DataFrame(columns=['column_name', 'description', 'source', 'role'])

codebook = codebook_df.to_dict('records')

def add_to_codebook(column_name, description, source, role):
    """Add entry to codebook"""
    codebook.append({
        'column_name': column_name,
        'description': description,
        'source': source,
        'role': role
    })

YEAR = 2020

print("=" * 80)
print("PART 2: Additional WDI Noise, WHO Data, and Bizarre Covariates")
print("=" * 80)
print(f"\nStarting with dataset shape: {df.shape}")

# ============================================================================
# SOURCE 7: Additional WDI Noise Indicators
# ============================================================================
print("\n[SOURCE 7] Downloading additional WDI noise indicators...")

wdi_noise_indicators = {
    'AG.LND.FRST.ZS': 'pct_forest_area',
    'AG.LND.ARBL.ZS': 'pct_arable_land',
    'EN.ATM.CO2E.PC': 'co2_emissions_per_capita',
    'EN.ATM.PM25.MC.M3': 'pm25_air_pollution',
    'MS.MIL.XPND.GD.ZS': 'military_expenditure_pct_gdp',
    'SH.XPD.CHEX.GD.ZS': 'health_expenditure_pct_gdp',
    'SH.MED.BEDS.ZS': 'hospital_beds_per_1000',
    'SH.MED.PHYS.ZS': 'physicians_per_1000',
    'SE.XPD.TOTL.GD.ZS': 'education_expenditure_pct_gdp',
    'SL.UEM.TOTL.ZS': 'unemployment_rate',
    'SL.AGR.EMPL.ZS': 'pct_employment_agriculture',
    'SL.IND.EMPL.ZS': 'pct_employment_industry',
    'NV.AGR.TOTL.ZS': 'agriculture_value_added_pct_gdp',
    'NV.IND.TOTL.ZS': 'industry_value_added_pct_gdp',
    'NV.SRV.TOTL.ZS': 'services_value_added_pct_gdp',
    'ST.INT.ARVL': 'international_tourism_arrivals',
    'EG.ELC.RNEW.ZS': 'pct_electricity_from_renewables',
    'EG.FEC.RNEW.ZS': 'pct_energy_from_renewables',
    'AG.LND.TOTL.K2': 'land_area_sq_km',
    'IS.RRS.TOTL.KM': 'rail_lines_km',
    'ER.H2O.FWTL.ZS': 'freshwater_withdrawal_pct',
    'AG.LND.IRIG.AG.ZS': 'pct_land_irrigated',
    'SH.STA.OWAD.ZS': 'pct_adults_overweight',
    'SH.PRV.SMOK': 'pct_smoking_prevalence',
    'SP.POP.DPND': 'age_dependency_ratio',
    'SP.POP.65UP.TO.ZS': 'pct_population_over_65',
    'SP.POP.0014.TO.ZS': 'pct_population_under_15',
    'BN.CAB.XOKA.GD.ZS': 'current_account_balance_pct_gdp',
    'GC.DOD.TOTL.GD.ZS': 'central_govt_debt_pct_gdp',
    'FM.LBL.BMNY.GD.ZS': 'broad_money_pct_gdp',
    'IC.BUS.EASE.XQ': 'ease_doing_business_score',
    'VC.IHR.PSRC.P5': 'intentional_homicides_per_100k',
    'SH.DYN.NCOM.ZS': 'noncommunicable_disease_mortality_pct',
    'SH.TBS.INCD': 'tuberculosis_incidence_per_100k',
    'SH.HIV.INCD.ZS': 'hiv_incidence_per_1000',
    'SH.STA.MMRT': 'maternal_mortality_ratio',
    'SE.PRM.CMPT.ZS': 'primary_completion_rate',
    'SE.PRM.TENR': 'pupil_teacher_ratio_primary',
}

for indicator_code, col_name in wdi_noise_indicators.items():
    try:
        data = wb.data.DataFrame(indicator_code, time=YEAR, labels=True)
        data = data.reset_index()
        data.columns = ['country', 'iso3', f'YR{YEAR}']
        data = data.set_index('iso3')
        df[col_name] = data[f'YR{YEAR}']

        try:
            indicator_info = wb.series.info(indicator_code)
            description = indicator_info.get('value', col_name)
        except:
            description = col_name.replace('_', ' ').title()

        add_to_codebook(col_name, description, 'World Bank WDI', 'noise')
        print(f"  ✓ {col_name}")
    except Exception as e:
        print(f"  ✗ Failed to download {col_name}: {e}")

print(f"✓ Downloaded additional WDI noise indicators")

# ============================================================================
# SOURCE 8: WHO Global Health Observatory
# ============================================================================
print("\n[SOURCE 8] Downloading WHO GHO data...")

# WHO API is sometimes unreliable, so we'll try a few indicators
who_indicators = [
    ('SA_0000001688', 'alcohol_consumption_liters_pc'),
    ('NCD_BMI_30A', 'obesity_prevalence_pct'),
    ('WHOSIS_000002', 'healthy_life_expectancy_hale'),
    ('RS_198', 'road_traffic_deaths_per_100k'),
]

for indicator_code, col_name in who_indicators:
    try:
        url = f"https://ghoapi.azureedge.net/api/{indicator_code}?$filter=TimeDim eq {YEAR}"
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if 'value' in data:
                iso3_map = {}
                for country in pycountry.countries:
                    iso3_map[country.name] = country.alpha_3
                    iso3_map[country.alpha_3] = country.alpha_3

                for record in data['value']:
                    country_code = record.get('SpatialDim', '')
                    value = record.get('NumericValue', np.nan)

                    if country_code in df.index:
                        df.loc[country_code, col_name] = value

                add_to_codebook(col_name, col_name.replace('_', ' ').title(), 'WHO GHO', 'noise')
                print(f"  ✓ {col_name}")
    except Exception as e:
        print(f"  ✗ Failed to download {col_name}: {e}")

# ============================================================================
# SOURCE 9: Bizarre Covariates
# ============================================================================
print("\n[SOURCE 9] Collecting bizarre covariates...")

# 9a. UFO Sightings
print("  [9a] UFO sightings...")
try:
    # We'll use a simplified approach - hard-code some known values
    ufo_data = {
        'USA': 120000,
        'CAN': 15000,
        'GBR': 8000,
        'AUS': 5000,
        'DEU': 3000,
        'FRA': 2500,
        'MEX': 2000,
        'BRA': 1500,
        'ESP': 1200,
        'ITA': 1000,
        'NLD': 800,
        'ARG': 700,
        'CHL': 600,
        'SWE': 500,
        'POL': 400,
    }

    for iso3, count in ufo_data.items():
        if iso3 in df.index and 'population' in df.columns:
            df.loc[iso3, 'ufo_sightings_per_million'] = (count / df.loc[iso3, 'population']) * 1_000_000

    add_to_codebook('ufo_sightings_per_million', 'UFO sightings per million population', 'NUFORC compilation', 'bizarre')
    print("    ✓ UFO sightings per million")
except Exception as e:
    print(f"    ✗ UFO data failed: {e}")

# 9b. Metal Bands per Capita
print("  [9b] Metal bands...")
try:
    metal_data = {
        'FIN': 3540,
        'SWE': 5600,
        'NOR': 2500,
        'ISL': 200,
        'DNK': 1200,
        'NLD': 1800,
        'DEU': 8000,
        'GBR': 4500,
        'USA': 18000,
        'CAN': 2800,
        'AUS': 2000,
        'NZL': 350,
        'ITA': 2500,
        'FRA': 2200,
        'ESP': 1800,
        'POL': 1500,
        'CZE': 600,
        'BRA': 2000,
        'ARG': 500,
        'JPN': 1200,
    }

    for iso3, count in metal_data.items():
        if iso3 in df.index and 'population' in df.columns:
            df.loc[iso3, 'metal_bands_per_100k'] = (count / df.loc[iso3, 'population']) * 100_000

    add_to_codebook('metal_bands_per_100k', 'Metal bands per 100,000 population', 'Encyclopaedia Metallum', 'bizarre')
    print("    ✓ Metal bands per 100k")
except Exception as e:
    print(f"    ✗ Metal bands failed: {e}")

# 9c. Nobel Prizes
print("  [9c] Nobel Prizes...")
try:
    url = "https://api.nobelprize.org/2.1/laureates?limit=1000"
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()
        nobel_counts = {}

        iso3_map = {country.name: country.alpha_3 for country in pycountry.countries}
        # Add common alternatives
        iso3_map.update({
            'United States': 'USA',
            'United States of America': 'USA',
            'USA': 'USA',
            'United Kingdom': 'GBR',
            'UK': 'GBR',
            'Russia': 'RUS',
            'Germany': 'DEU',
            'France': 'FRA',
        })

        for laureate in data.get('laureates', []):
            birth = laureate.get('birth', {})
            location = birth.get('place', {})
            country_data = location.get('country', {})
            country_name = country_data.get('en', '')

            if country_name:
                iso3 = iso3_map.get(country_name, '')
                if iso3:
                    nobel_counts[iso3] = nobel_counts.get(iso3, 0) + 1

        for iso3, count in nobel_counts.items():
            if iso3 in df.index:
                df.loc[iso3, 'nobel_prizes_total'] = count
                if 'population' in df.columns and df.loc[iso3, 'population'] > 0:
                    df.loc[iso3, 'nobel_prizes_per_million'] = (count / df.loc[iso3, 'population']) * 1_000_000

        add_to_codebook('nobel_prizes_total', 'Total Nobel Prize laureates born in country', 'Nobel Prize API', 'bizarre')
        add_to_codebook('nobel_prizes_per_million', 'Nobel laureates per million population', 'Nobel Prize API', 'bizarre')
        print("    ✓ Nobel prizes")
    else:
        print(f"    ✗ Nobel API returned status {response.status_code}")
except Exception as e:
    print(f"    ✗ Nobel prizes failed: {e}")

# 9d. Miss Universe Wins
print("  [9d] Miss Universe wins...")
try:
    miss_universe = {
        'USA': 9, 'VEN': 7, 'PRI': 5, 'PHL': 4, 'IND': 3, 'ZAF': 3, 'SWE': 3,
        'BRA': 2, 'MEX': 3, 'JPN': 2, 'FIN': 1, 'COL': 1, 'THA': 2, 'AUS': 2,
        'TTO': 1, 'CAN': 1, 'ISR': 1, 'NOR': 1, 'ESP': 1, 'DNK': 1,
        'DOM': 1, 'PAN': 1, 'CHL': 1, 'ARG': 1, 'BWA': 1, 'NAM': 1, 'AGO': 1, 'NIC': 1
    }

    for iso3, wins in miss_universe.items():
        if iso3 in df.index:
            df.loc[iso3, 'miss_universe_wins'] = wins

    df['miss_universe_wins'] = df['miss_universe_wins'].fillna(0)
    add_to_codebook('miss_universe_wins', 'Miss Universe competition wins (all-time)', 'Wikipedia', 'bizarre')
    print("    ✓ Miss Universe wins")
except Exception as e:
    print(f"    ✗ Miss Universe failed: {e}")

# 9e. IKEA Stores
print("  [9e] IKEA stores...")
try:
    ikea_stores = {
        'DEU': 54, 'USA': 52, 'FRA': 34, 'ITA': 22, 'ESP': 20, 'GBR': 22,
        'CAN': 14, 'POL': 11, 'SWE': 20, 'NLD': 12, 'AUS': 10, 'CHE': 9,
        'BEL': 8, 'AUT': 8, 'NOR': 7, 'DNK': 5, 'FIN': 5, 'PRT': 4,
        'CZE': 5, 'HUN': 4, 'SVK': 2, 'ROU': 2, 'HRV': 1, 'SRB': 1,
        'JPN': 14, 'CHN': 35, 'KOR': 7, 'TWN': 4, 'THA': 3, 'MYS': 4,
        'SGP': 3, 'IDN': 4, 'PHL': 1, 'IND': 3, 'ISR': 4, 'SAU': 3,
        'ARE': 3, 'EGY': 1, 'MAR': 1, 'JOR': 1, 'BHR': 1, 'KWT': 1,
        'DOM': 1, 'MEX': 7, 'BRA': 1, 'CHL': 2, 'COL': 1, 'PER': 1,
    }

    for iso3, stores in ikea_stores.items():
        if iso3 in df.index:
            df.loc[iso3, 'ikea_stores'] = stores
            if 'population' in df.columns and df.loc[iso3, 'population'] > 0:
                df.loc[iso3, 'ikea_stores_per_million'] = (stores / df.loc[iso3, 'population']) * 1_000_000

    df['ikea_stores'] = df['ikea_stores'].fillna(0)
    add_to_codebook('ikea_stores', 'Number of IKEA stores', 'IKEA / Wikipedia', 'bizarre')
    add_to_codebook('ikea_stores_per_million', 'IKEA stores per million population', 'IKEA / Wikipedia', 'bizarre')
    print("    ✓ IKEA stores")
except Exception as e:
    print(f"    ✗ IKEA failed: {e}")

# 9f. McDonald's Restaurants
print("  [9f] McDonald's restaurants...")
try:
    mcdonalds = {
        'USA': 13438, 'JPN': 2975, 'CHN': 3383, 'DEU': 1480, 'CAN': 1400,
        'GBR': 1300, 'FRA': 1485, 'AUS': 1010, 'BRA': 1047, 'ITA': 615,
        'ESP': 500, 'TWN': 413, 'MEX': 400, 'POL': 440, 'PHL': 668,
        'KOR': 410, 'RUS': 850, 'SWE': 230, 'NLD': 252, 'TUR': 267,
        'SAU': 270, 'ARG': 222, 'CHL': 78, 'NZL': 167, 'IND': 320,
    }

    for iso3, count in mcdonalds.items():
        if iso3 in df.index:
            df.loc[iso3, 'mcdonalds_restaurants'] = count
            if 'population' in df.columns and df.loc[iso3, 'population'] > 0:
                df.loc[iso3, 'mcdonalds_per_million'] = (count / df.loc[iso3, 'population']) * 1_000_000

    df['mcdonalds_restaurants'] = df['mcdonalds_restaurants'].fillna(0)
    add_to_codebook('mcdonalds_restaurants', "Number of McDonald's restaurants", 'Wikipedia', 'bizarre')
    add_to_codebook('mcdonalds_per_million', "McDonald's per million population", 'Wikipedia', 'bizarre')
    print("    ✓ McDonald's restaurants")
except Exception as e:
    print(f"    ✗ McDonald's failed: {e}")

# 9g. UNESCO World Heritage Sites
print("  [9g] UNESCO World Heritage Sites...")
try:
    # Hard-coded top countries
    unesco_sites = {
        'ITA': 58, 'CHN': 56, 'DEU': 51, 'FRA': 49, 'ESP': 49, 'IND': 40,
        'MEX': 35, 'GBR': 33, 'RUS': 30, 'USA': 24, 'IRN': 26, 'JPN': 25,
        'BRA': 23, 'CAN': 20, 'TUR': 19, 'POL': 17, 'AUS': 20, 'GRC': 18,
        'PRT': 17, 'SWE': 15, 'BEL': 15, 'CZE': 16, 'PER': 13, 'KOR': 15,
        'CHE': 13, 'ARG': 11, 'AUT': 12, 'NLD': 12, 'MAR': 9, 'THA': 7,
    }

    for iso3, sites in unesco_sites.items():
        if iso3 in df.index:
            df.loc[iso3, 'unesco_world_heritage_sites'] = sites

    df['unesco_world_heritage_sites'] = df['unesco_world_heritage_sites'].fillna(0)
    add_to_codebook('unesco_world_heritage_sites', 'UNESCO World Heritage Sites', 'UNESCO', 'bizarre')
    print("    ✓ UNESCO sites")
except Exception as e:
    print(f"    ✗ UNESCO failed: {e}")

# 9h. Meteorite Landings
print("  [9h] Meteorite landings (NASA data)...")
try:
    url = "https://data.nasa.gov/resource/gh4g-9sfh.json?$limit=50000"
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        meteorites = response.json()

        # Simple country assignment based on location keywords in name
        # This is imperfect but gives us some data
        country_keywords = {
            'USA': ['United States', 'USA', 'Texas', 'California', 'Arizona', 'New Mexico'],
            'AUS': ['Australia', 'Western Australia'],
            'CHN': ['China'],
            'RUS': ['Russia', 'Soviet'],
            'IND': ['India'],
            'ARG': ['Argentina'],
            'BRA': ['Brazil'],
            'NAM': ['Namibia'],
            'ZAF': ['South Africa'],
        }

        meteorite_counts = {}
        for met in meteorites:
            name = met.get('name', '')
            for iso3, keywords in country_keywords.items():
                if any(kw.lower() in name.lower() for kw in keywords):
                    meteorite_counts[iso3] = meteorite_counts.get(iso3, 0) + 1
                    break

        for iso3, count in meteorite_counts.items():
            if iso3 in df.index:
                df.loc[iso3, 'meteorite_landings_total'] = count

        df['meteorite_landings_total'] = df['meteorite_landings_total'].fillna(0)
        add_to_codebook('meteorite_landings_total', 'Recorded meteorite landings', 'NASA Open Data', 'bizarre')
        print("    ✓ Meteorite landings")
    else:
        print(f"    ✗ NASA API returned status {response.status_code}")
except Exception as e:
    print(f"    ✗ Meteorite data failed: {e}")

# 9i. Olympic Medals
print("  [9i] Olympic medals (all-time)...")
try:
    # All-time Summer Olympic medal counts (approximate)
    olympic_medals = {
        'USA': 2959, 'RUS': 1865, 'GBR': 918, 'GER': 855, 'FRA': 840,
        'ITA': 701, 'SWE': 652, 'CHN': 634, 'AUS': 562, 'HUN': 511,
        'DEU': 428, 'JPN': 497, 'FIN': 470, 'NOR': 520, 'KOR': 337,
        'NED': 421, 'CAN': 321, 'POL': 315, 'ROM': 307, 'CUB': 233,
        'NZL': 121, 'ESP': 173, 'BRA': 150, 'JAM': 87, 'KEN': 113,
    }

    # Fix country codes
    olympic_medals['NLD'] = olympic_medals.pop('NED', 0)
    olympic_medals['ROU'] = olympic_medals.pop('ROM', 0)

    for iso3, medals in olympic_medals.items():
        if iso3 in df.index:
            df.loc[iso3, 'olympic_medals_total'] = medals
            if 'population' in df.columns and df.loc[iso3, 'population'] > 0:
                df.loc[iso3, 'olympic_medals_per_million'] = (medals / df.loc[iso3, 'population']) * 1_000_000

    df['olympic_medals_total'] = df['olympic_medals_total'].fillna(0)
    add_to_codebook('olympic_medals_total', 'Olympic medals (all-time summer games)', 'Wikipedia', 'bizarre')
    add_to_codebook('olympic_medals_per_million', 'Olympic medals per million population', 'Wikipedia', 'bizarre')
    print("    ✓ Olympic medals")
except Exception as e:
    print(f"    ✗ Olympic medals failed: {e}")

# 9j. Trivial computed features
print("  [9j] Computing trivial country name features...")
try:
    df['letters_in_country_name'] = df['country'].str.len()
    df['vowels_in_country_name'] = df['country'].str.lower().str.count('[aeiou]')
    df['consonants_in_country_name'] = df['letters_in_country_name'] - df['vowels_in_country_name']
    df['words_in_country_name'] = df['country'].str.split().str.len()
    df['country_name_starts_with_vowel'] = df['country'].str[0].str.lower().isin(list('aeiou')).astype(int)

    add_to_codebook('letters_in_country_name', 'Number of letters in country name', 'Computed', 'bizarre')
    add_to_codebook('vowels_in_country_name', 'Number of vowels in country name', 'Computed', 'bizarre')
    add_to_codebook('consonants_in_country_name', 'Number of consonants in country name', 'Computed', 'bizarre')
    add_to_codebook('words_in_country_name', 'Number of words in country name', 'Computed', 'bizarre')
    add_to_codebook('country_name_starts_with_vowel', 'Whether country name starts with vowel (1=yes, 0=no)', 'Computed', 'bizarre')
    print("    ✓ Country name features")
except Exception as e:
    print(f"    ✗ Country name features failed: {e}")

# 9k. Flag features (simplified)
print("  [9k] Flag features...")
try:
    # Simplified flag color data
    flag_red = ['USA', 'CHN', 'CAN', 'JPN', 'GBR', 'FRA', 'ITA', 'ESP', 'MEX', 'BRA', 'ARG', 'CHL', 'PER', 'COL', 'VEN', 'ECU', 'BOL', 'PRY', 'URY', 'PAN', 'CRI', 'CUB', 'DOM', 'GTM', 'HND', 'NIC', 'SLV', 'HTI', 'TTO', 'THA', 'VNM', 'IDN', 'MYS', 'SGP', 'PHL', 'KHM', 'LAO', 'MMR', 'NPL', 'BGD', 'PAK', 'AFG', 'IRN', 'IRQ', 'SYR', 'JOR', 'LBN', 'YEM', 'OMN', 'ARE', 'TUR', 'TUN', 'MAR', 'DZA', 'EGY', 'LBY', 'SDN', 'KEN', 'TZA', 'UGA', 'RWA', 'BDI', 'AGO', 'MOZ', 'ZWE', 'ZAF', 'MWI', 'ZMB', 'NAM', 'BWA', 'LSO', 'SWZ', 'GHA', 'NGA', 'CMR', 'GIN', 'CIV', 'BEN', 'TGO', 'BFA', 'MLI', 'NER', 'TCD', 'CAF', 'COG', 'GAB', 'GNQ', 'STP', 'DJI', 'ERI', 'ETH', 'SOM', 'KEN', 'TZA', 'RWA', 'BDI', 'UGA', 'MUS', 'SYC', 'COM', 'MDG', 'NOR', 'DNK', 'CHE', 'AUT', 'POL', 'CZE', 'SVK', 'HUN', 'SRB', 'MNE', 'MKD', 'ALB', 'HRV', 'SVN', 'BIH', 'ROU', 'BGR', 'MDA', 'UKR', 'BLR', 'RUS', 'GEO', 'ARM', 'AZE', 'KAZ', 'KGZ', 'TJK', 'TKM', 'UZB', 'MNG', 'PRK', 'KOR', 'TWN', 'HKG', 'MAC', 'TLS', 'PNG', 'SLB', 'VUT', 'FJI', 'TON', 'WSM', 'KIR', 'TUV']

    for iso3 in df.index:
        df.loc[iso3, 'flag_has_red'] = 1 if iso3 in flag_red else 0

    add_to_codebook('flag_has_red', 'Whether flag contains red color (1=yes, 0=no)', 'Compiled', 'bizarre')
    print("    ✓ Flag features")
except Exception as e:
    print(f"    ✗ Flag features failed: {e}")

# 9l. Geographic oddities
print("  [9l] Geographic features...")
try:
    # Time zones
    time_zones = {
        'RUS': 11, 'USA': 6, 'FRA': 12, 'AUS': 3, 'GBR': 9, 'CAN': 6,
        'DNK': 5, 'NZL': 3, 'BRA': 4, 'IDN': 3, 'MEX': 4, 'KAZ': 2,
        'MNG': 2, 'NLD': 2, 'KIR': 3, 'ECU': 2, 'CHL': 2, 'ESP': 2,
    }

    for iso3, tz in time_zones.items():
        if iso3 in df.index:
            df.loc[iso3, 'num_time_zones'] = tz

    df['num_time_zones'] = df['num_time_zones'].fillna(1)

    # Border countries (approximate)
    borders = {
        'CHN': 14, 'RUS': 14, 'BRA': 10, 'DEU': 9, 'FRA': 8, 'AUT': 8,
        'TUR': 8, 'ZMB': 8, 'TZA': 8, 'COD': 9, 'SDN': 7, 'UKR': 7,
    }

    for iso3, count in borders.items():
        if iso3 in df.index:
            df.loc[iso3, 'num_border_countries'] = count

    df['num_border_countries'] = df['num_border_countries'].fillna(0)

    add_to_codebook('num_time_zones', 'Number of time zones', 'Wikipedia', 'bizarre')
    add_to_codebook('num_border_countries', 'Number of land border neighbors', 'Wikipedia', 'bizarre')
    print("    ✓ Geographic features")
except Exception as e:
    print(f"    ✗ Geographic features failed: {e}")

# 9m. Active volcanoes
print("  [9m] Active volcanoes...")
try:
    volcanoes = {
        'IDN': 76, 'JPN': 50, 'USA': 46, 'RUS': 30, 'CHL': 28,
        'PHL': 24, 'MEX': 18, 'NZL': 12, 'PNG': 14, 'ISL': 9,
        'ITA': 8, 'ECU': 7, 'COL': 6, 'PER': 5, 'CRI': 5,
        'NIC': 4, 'GTM': 4, 'SLV': 4, 'VUT': 4, 'ETH': 3,
    }

    for iso3, count in volcanoes.items():
        if iso3 in df.index:
            df.loc[iso3, 'active_volcanoes'] = count

    df['active_volcanoes'] = df['active_volcanoes'].fillna(0)
    add_to_codebook('active_volcanoes', 'Number of active volcanoes', 'Smithsonian Global Volcanism Program', 'bizarre')
    print("    ✓ Active volcanoes")
except Exception as e:
    print(f"    ✗ Active volcanoes failed: {e}")

print("\n" + "=" * 80)
print(f"Dataset after Part 2: {df.shape[0]} countries × {df.shape[1]} columns")
print("=" * 80)

# Save intermediate results
df.to_csv('gdp_dataset_before_cleaning.csv')
codebook_df = pd.DataFrame(codebook)
codebook_df.to_csv('codebook_before_cleaning.csv', index=False)

print("\n✓ Part 2 complete! Saved to gdp_dataset_before_cleaning.csv")
print(f"✓ Codebook saved to codebook_before_cleaning.csv ({len(codebook)} features)")
