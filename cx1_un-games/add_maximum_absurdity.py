#!/usr/bin/env python3
"""
Add Maximum Absurdity Features to GDP Dataset

This script adds the most ridiculous, absurd features we can find
to demonstrate spurious correlations in the most entertaining way possible.
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("ADDING MAXIMUM ABSURDITY FEATURES")
print("=" * 80)

# Load current dataset
df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook_df = pd.read_csv('codebook.csv')
codebook = codebook_df.to_dict('records')

def add_to_codebook(column_name, description, source, role):
    """Add entry to codebook"""
    if column_name not in [c['column_name'] for c in codebook]:
        codebook.append({
            'column_name': column_name,
            'description': description,
            'source': source,
            'role': role
        })

print(f"\nStarting with: {df.shape[0]} countries × {df.shape[1]} features")

# Count current bizarre features
current_bizarre = len([c for c in codebook if c['role'] == 'bizarre'])
print(f"Current bizarre features: {current_bizarre}")

# ============================================================================
# ABSURD CATEGORY 1: Eurovision Song Contest
# ============================================================================
print("\n[EUROVISION] Adding Eurovision Song Contest data...")

try:
    # Eurovision wins by country (all-time)
    eurovision_wins = {
        'IRL': 7,   # Ireland
        'SWE': 7,   # Sweden
        'FRA': 5,   # France
        'LUX': 5,   # Luxembourg
        'GBR': 5,   # United Kingdom
        'NLD': 5,   # Netherlands
        'ISR': 4,   # Israel
        'DNK': 3,   # Denmark
        'NOR': 3,   # Norway
        'ITA': 3,   # Italy
        'UKR': 3,   # Ukraine
        'ESP': 2,   # Spain
        'CHE': 2,   # Switzerland
        'AUT': 2,   # Austria
        'DEU': 2,   # Germany
        'BEL': 1,   # Belgium
        'EST': 1,   # Estonia
        'LVA': 1,   # Latvia
        'TUR': 1,   # Turkey
        'YUG': 1,   # Yugoslavia (historical)
        'FIN': 1,   # Finland
        'GRC': 1,   # Greece
        'PRT': 1,   # Portugal
        'AZE': 1,   # Azerbaijan
    }

    df['eurovision_wins'] = 0
    for iso3, wins in eurovision_wins.items():
        if iso3 in df.index:
            df.loc[iso3, 'eurovision_wins'] = wins

    add_to_codebook('eurovision_wins', 'Eurovision Song Contest wins (all-time)',
                    'Eurovision/Wikipedia', 'bizarre')
    print("  ✓ Eurovision wins added")

except Exception as e:
    print(f"  ✗ Eurovision failed: {e}")

# ============================================================================
# ABSURD CATEGORY 2: FIFA World Cup
# ============================================================================
print("\n[FOOTBALL] Adding FIFA World Cup data...")

try:
    # World Cup wins
    world_cup_wins = {
        'BRA': 5,  # Brazil
        'DEU': 4,  # Germany
        'ITA': 4,  # Italy
        'ARG': 3,  # Argentina
        'FRA': 2,  # France
        'URY': 2,  # Uruguay
        'ESP': 1,  # Spain
        'GBR': 1,  # England (using GBR code)
        'ENG': 1,  # England (alt code if exists)
    }

    df['fifa_world_cup_wins'] = 0
    for iso3, wins in world_cup_wins.items():
        if iso3 in df.index:
            df.loc[iso3, 'fifa_world_cup_wins'] = wins

    # Women's World Cup wins
    womens_wc = {
        'USA': 4,
        'DEU': 2,
        'NOR': 1,
        'JPN': 1,
        'ESP': 1,
    }

    df['fifa_womens_world_cup_wins'] = 0
    for iso3, wins in womens_wc.items():
        if iso3 in df.index:
            df.loc[iso3, 'fifa_womens_world_cup_wins'] = wins

    add_to_codebook('fifa_world_cup_wins', "Men's FIFA World Cup wins",
                    'FIFA/Wikipedia', 'bizarre')
    add_to_codebook('fifa_womens_world_cup_wins', "Women's FIFA World Cup wins",
                    'FIFA/Wikipedia', 'bizarre')
    print("  ✓ World Cup wins added")

except Exception as e:
    print(f"  ✗ World Cup failed: {e}")

# ============================================================================
# ABSURD CATEGORY 3: Alcohol Consumption
# ============================================================================
print("\n[ALCOHOL] Adding alcohol consumption data...")

try:
    # Beer consumption (liters per capita per year) - approximate from various sources
    beer_consumption = {
        'CZE': 188.6, 'AUT': 102.0, 'POL': 100.8, 'ROU': 100.3, 'DEU': 99.0,
        'LTU': 97.7, 'EST': 89.5, 'ESP': 83.8, 'BEL': 81.0, 'HRV': 80.3,
        'SVN': 78.6, 'FIN': 76.8, 'GBR': 67.7, 'DNK': 65.3, 'IRL': 64.2,
        'USA': 72.5, 'AUS': 66.8, 'NLD': 64.0, 'CAN': 59.0, 'NZL': 62.0,
        'BRA': 59.0, 'MEX': 52.0, 'ARG': 45.0, 'CHL': 42.0, 'COL': 35.0,
    }

    df['beer_consumption_liters_pc'] = np.nan
    for iso3, liters in beer_consumption.items():
        if iso3 in df.index:
            df.loc[iso3, 'beer_consumption_liters_pc'] = liters

    # Wine consumption (liters per capita per year)
    wine_consumption = {
        'FRA': 46.9, 'ITA': 42.2, 'PRT': 41.7, 'CHE': 35.7, 'AUT': 28.3,
        'ESP': 26.7, 'ARG': 24.5, 'URY': 22.0, 'DEU': 20.7, 'AUS': 20.5,
        'NZL': 18.5, 'GRC': 18.0, 'GBR': 15.2, 'BEL': 14.8, 'NLD': 13.0,
        'USA': 11.4, 'CAN': 10.0, 'CHL': 12.5, 'SWE': 8.5, 'DNK': 8.0,
    }

    df['wine_consumption_liters_pc'] = np.nan
    for iso3, liters in wine_consumption.items():
        if iso3 in df.index:
            df.loc[iso3, 'wine_consumption_liters_pc'] = liters

    add_to_codebook('beer_consumption_liters_pc',
                    'Beer consumption (liters per capita per year)',
                    'WHO/Wikipedia', 'bizarre')
    add_to_codebook('wine_consumption_liters_pc',
                    'Wine consumption (liters per capita per year)',
                    'WHO/Wikipedia', 'bizarre')
    print("  ✓ Alcohol consumption added")

except Exception as e:
    print(f"  ✗ Alcohol consumption failed: {e}")

# ============================================================================
# ABSURD CATEGORY 4: Coffee & Tea
# ============================================================================
print("\n[COFFEE] Adding coffee consumption data...")

try:
    # Coffee consumption (kg per capita per year)
    coffee_consumption = {
        'FIN': 12.0, 'NOR': 9.9, 'ISL': 9.0, 'DNK': 8.7, 'NLD': 8.4,
        'SWE': 8.2, 'CHE': 7.9, 'BEL': 6.8, 'LUX': 6.5, 'CAN': 6.5,
        'BIH': 6.2, 'AUT': 5.5, 'ITA': 5.9, 'BRA': 5.8, 'DEU': 5.5,
        'SVN': 4.9, 'FRA': 5.4, 'HRV': 4.8, 'CYP': 4.5, 'LBN': 4.8,
        'USA': 4.2, 'EST': 4.5, 'ESP': 4.5, 'PRT': 4.3, 'GRC': 5.4,
    }

    df['coffee_consumption_kg_pc'] = np.nan
    for iso3, kg in coffee_consumption.items():
        if iso3 in df.index:
            df.loc[iso3, 'coffee_consumption_kg_pc'] = kg

    add_to_codebook('coffee_consumption_kg_pc',
                    'Coffee consumption (kg per capita per year)',
                    'ICO/Wikipedia', 'bizarre')
    print("  ✓ Coffee consumption added")

except Exception as e:
    print(f"  ✗ Coffee failed: {e}")

# ============================================================================
# ABSURD CATEGORY 5: Casinos
# ============================================================================
print("\n[CASINOS] Adding casino data...")

try:
    casinos = {
        'USA': 1511, 'FRA': 202, 'RUS': 170, 'MEX': 250, 'ARG': 120,
        'AUS': 14, 'CAN': 27, 'ITA': 4, 'ESP': 43, 'GBR': 143,
        'DEU': 71, 'AUT': 12, 'NLD': 15, 'BEL': 9, 'CHE': 21,
        'ZAF': 40, 'PER': 26, 'CHL': 24, 'COL': 25, 'URY': 8,
        'PAN': 18, 'CRI': 20, 'MAC': 41, 'SGP': 2, 'PHL': 46,
    }

    df['casinos_total'] = 0
    for iso3, count in casinos.items():
        if iso3 in df.index:
            df.loc[iso3, 'casinos_total'] = count

    add_to_codebook('casinos_total', 'Number of casinos',
                    'Various casino databases/Wikipedia', 'bizarre')
    print("  ✓ Casino counts added")

except Exception as e:
    print(f"  ✗ Casinos failed: {e}")

# ============================================================================
# ABSURD CATEGORY 6: Airports
# ============================================================================
print("\n[AIRPORTS] Adding airport data...")

try:
    # Number of airports (approximate, large airports)
    airports = {
        'USA': 13513, 'BRA': 4093, 'MEX': 1714, 'CAN': 1467, 'RUS': 1218,
        'ARG': 1138, 'AUS': 480, 'COL': 836, 'CHN': 507, 'IND': 346,
        'IDN': 673, 'DEU': 539, 'FRA': 464, 'GBR': 460, 'JPN': 175,
        'ESP': 150, 'ITA': 129, 'TUR': 98, 'ZAF': 566, 'PER': 191,
    }

    df['airports_total'] = 0
    for iso3, count in airports.items():
        if iso3 in df.index:
            df.loc[iso3, 'airports_total'] = count

    add_to_codebook('airports_total', 'Total number of airports',
                    'CIA World Factbook/Wikipedia', 'bizarre')
    print("  ✓ Airport counts added")

except Exception as e:
    print(f"  ✗ Airports failed: {e}")

# ============================================================================
# ABSURD CATEGORY 7: Starbucks
# ============================================================================
print("\n[STARBUCKS] Adding Starbucks locations...")

try:
    starbucks = {
        'USA': 16346, 'CHN': 6975, 'JPN': 1901, 'KOR': 1872, 'GBR': 1089,
        'CAN': 1468, 'MEX': 785, 'TUR': 536, 'TWN': 565, 'THA': 511,
        'IDN': 467, 'PHL': 423, 'DEU': 158, 'FRA': 187, 'ESP': 156,
        'ITA': 30, 'NLD': 77, 'CHE': 69, 'SAU': 253, 'ARE': 225,
        'BRA': 180, 'MYS': 377, 'SGP': 158, 'IND': 290, 'AUS': 60,
    }

    df['starbucks_locations'] = 0
    for iso3, count in starbucks.items():
        if iso3 in df.index:
            df.loc[iso3, 'starbucks_locations'] = count

    add_to_codebook('starbucks_locations', 'Number of Starbucks locations',
                    'Starbucks corporate data', 'bizarre')
    print("  ✓ Starbucks locations added")

except Exception as e:
    print(f"  ✗ Starbucks failed: {e}")

# ============================================================================
# ABSURD CATEGORY 8: Skyscrapers
# ============================================================================
print("\n[SKYSCRAPERS] Adding skyscraper data...")

try:
    # Buildings over 150m
    skyscrapers = {
        'CHN': 3090, 'USA': 880, 'ARE': 238, 'JPN': 302, 'KOR': 276,
        'AUS': 79, 'CAN': 80, 'IND': 144, 'PHL': 122, 'MYS': 161,
        'IDN': 127, 'THA': 111, 'TUR': 85, 'RUS': 118, 'BRA': 65,
        'MEX': 50, 'SGP': 92, 'SAU': 76, 'QAT': 63, 'KWT': 45,
        'GBR': 40, 'ESP': 25, 'ITA': 18, 'FRA': 20, 'DEU': 25,
    }

    df['skyscrapers_over_150m'] = 0
    for iso3, count in skyscrapers.items():
        if iso3 in df.index:
            df.loc[iso3, 'skyscrapers_over_150m'] = count

    add_to_codebook('skyscrapers_over_150m', 'Buildings over 150 meters tall',
                    'Skyscraper Center CTBUH', 'bizarre')
    print("  ✓ Skyscraper counts added")

except Exception as e:
    print(f"  ✗ Skyscrapers failed: {e}")

# ============================================================================
# ABSURD CATEGORY 9: Theme Parks
# ============================================================================
print("\n[THEME PARKS] Adding theme park data...")

try:
    theme_parks = {
        'USA': 475, 'CHN': 339, 'JPN': 78, 'DEU': 64, 'GBR': 56,
        'ITA': 42, 'FRA': 55, 'ESP': 38, 'BRA': 35, 'MEX': 30,
        'CAN': 28, 'AUS': 24, 'KOR': 20, 'IND': 28, 'TUR': 15,
        'NLD': 18, 'BEL': 12, 'SWE': 10, 'DNK': 8, 'POL': 12,
    }

    df['theme_parks'] = 0
    for iso3, count in theme_parks.items():
        if iso3 in df.index:
            df.loc[iso3, 'theme_parks'] = count

    add_to_codebook('theme_parks', 'Number of theme parks/amusement parks',
                    'Various theme park databases', 'bizarre')
    print("  ✓ Theme park counts added")

except Exception as e:
    print(f"  ✗ Theme parks failed: {e}")

# ============================================================================
# ABSURD CATEGORY 10: Michelin Stars
# ============================================================================
print("\n[MICHELIN] Adding Michelin star data...")

try:
    # Total Michelin stars by country
    michelin_stars = {
        'FRA': 632, 'JPN': 668, 'ITA': 395, 'DEU': 327, 'ESP': 224,
        'USA': 200, 'GBR': 172, 'CHE': 128, 'BEL': 127, 'NLD': 121,
        'AUT': 62, 'SWE': 45, 'DNK': 37, 'NOR': 20, 'FIN': 18,
        'LUX': 16, 'PRT': 30, 'HKG': 73, 'SGP': 52, 'KOR': 31,
        'CHN': 92, 'THA': 38, 'TWN': 42, 'MAC': 20, 'TUR': 8,
    }

    df['michelin_stars_total'] = 0
    for iso3, stars in michelin_stars.items():
        if iso3 in df.index:
            df.loc[iso3, 'michelin_stars_total'] = stars

    add_to_codebook('michelin_stars_total', 'Total Michelin stars awarded',
                    'Michelin Guide', 'bizarre')
    print("  ✓ Michelin stars added")

except Exception as e:
    print(f"  ✗ Michelin stars failed: {e}")

# ============================================================================
# ABSURD CATEGORY 11: Cryptocurrency ATMs
# ============================================================================
print("\n[CRYPTO] Adding cryptocurrency ATM data...")

try:
    crypto_atms = {
        'USA': 31600, 'CAN': 2650, 'AUS': 237, 'GBR': 145, 'ESP': 228,
        'POL': 180, 'AUT': 286, 'CHE': 168, 'ITA': 143, 'DEU': 102,
        'NLD': 76, 'CZE': 75, 'ROU': 78, 'HKG': 85, 'SGP': 42,
        'MEX': 75, 'BRA': 45, 'ARG': 38, 'COL': 42, 'CHL': 25,
    }

    df['cryptocurrency_atms'] = 0
    for iso3, count in crypto_atms.items():
        if iso3 in df.index:
            df.loc[iso3, 'cryptocurrency_atms'] = count

    add_to_codebook('cryptocurrency_atms', 'Number of cryptocurrency ATMs',
                    'Coin ATM Radar', 'bizarre')
    print("  ✓ Crypto ATMs added")

except Exception as e:
    print(f"  ✗ Crypto ATMs failed: {e}")

# ============================================================================
# ABSURD CATEGORY 12: Golf Courses
# ============================================================================
print("\n[GOLF] Adding golf course data...")

try:
    golf_courses = {
        'USA': 15372, 'JPN': 2383, 'CAN': 2633, 'GBR': 2270, 'AUS': 1628,
        'DEU': 731, 'FRA': 804, 'SWE': 622, 'ESP': 496, 'IRL': 494,
        'ZAF': 489, 'NZL': 418, 'KOR': 505, 'ITA': 403, 'NLD': 234,
        'CHN': 599, 'ARG': 345, 'MEX': 257, 'BRA': 124, 'CHL': 78,
    }

    df['golf_courses'] = 0
    for iso3, count in golf_courses.items():
        if iso3 in df.index:
            df.loc[iso3, 'golf_courses'] = count

    add_to_codebook('golf_courses', 'Number of golf courses',
                    'R&A Golf Around the World', 'bizarre')
    print("  ✓ Golf courses added")

except Exception as e:
    print(f"  ✗ Golf courses failed: {e}")

# ============================================================================
# Summary and Save
# ============================================================================
print("\n" + "=" * 80)
print("ABSURDITY FEATURES ADDED")
print("=" * 80)

new_bizarre = len([c for c in codebook if c['role'] == 'bizarre']) - current_bizarre
print(f"\nAdded {new_bizarre} new bizarre features")
print(f"Total bizarre features now: {current_bizarre + new_bizarre}")
print(f"Dataset shape: {df.shape[0]} countries × {df.shape[1]} features")

# Remove some synthetic noise to make room
print("\n[CLEANUP] Removing some synthetic noise features...")
synthetic_cols = [col for col in df.columns if col.startswith('synthetic_noise_')]
n_to_remove = len(synthetic_cols) - 30  # Keep only 30 synthetic
if n_to_remove > 0:
    cols_to_drop = synthetic_cols[:n_to_remove]
    df = df.drop(columns=cols_to_drop)
    codebook = [c for c in codebook if c['column_name'] not in cols_to_drop]
    print(f"  Removed {n_to_remove} synthetic noise features")
    print(f"  New shape: {df.shape[0]} countries × {df.shape[1]} features")

# Save
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_df = pd.DataFrame(codebook)
codebook_df.to_csv('codebook.csv', index=False)

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

role_counts = codebook_df['role'].value_counts()
print(f"\nDataset: {df.shape[0]} countries × {df.shape[1]} features")
print(f"\nBreakdown by role:")
for role, count in role_counts.items():
    print(f"  {role.capitalize():<12} {count:>3} features")

print("\n✓ Maximum absurdity achieved!")
print("\nNew bizarre features include:")
print("  - Eurovision Song Contest wins")
print("  - FIFA World Cup wins (men's and women's)")
print("  - Beer & wine consumption per capita")
print("  - Coffee consumption per capita")
print("  - Casinos, airports, Starbucks locations")
print("  - Skyscrapers over 150m")
print("  - Theme parks and golf courses")
print("  - Michelin stars")
print("  - Cryptocurrency ATMs")

print("\n" + "=" * 80)
