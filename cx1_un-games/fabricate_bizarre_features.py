#!/usr/bin/env python3
"""
Fabricate Bizarre Features from Existing Data

This script creates derived bizarre features from:
1. Country name linguistics (letter positions, syllables, numerology)
2. Ratios and combinations of existing bizarre features
3. Geographic transformations
4. Pseudoscientific numerology

Goal: Maximum spurious correlations!
"""

import pandas as pd
import numpy as np
import re
from collections import Counter

print("=" * 80)
print("FABRICATING BIZARRE FEATURES FROM EXISTING DATA")
print("=" * 80)

# Load dataset and codebook
df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook_df = pd.read_csv('codebook.csv')

print(f"\nStarting: {df.shape[0]} countries × {df.shape[1]} features")

# Helper function to add to codebook
def add_to_codebook(column_name, description, source, role='bizarre'):
    """Add a new entry to the codebook"""
    global codebook_df
    new_row = pd.DataFrame({
        'column_name': [column_name],
        'description': [description],
        'source': [source],
        'role': [role]
    })
    codebook_df = pd.concat([codebook_df, new_row], ignore_index=True)

# ============================================================================
# PART 1: COUNTRY NAME LINGUISTIC FEATURES
# ============================================================================

print("\n" + "=" * 80)
print("PART 1: COUNTRY NAME LINGUISTIC FEATURES")
print("=" * 80)

def count_syllables(name):
    """Approximate syllable count using vowel clusters"""
    name = name.lower()
    # Remove trailing 'e' (silent e)
    name = re.sub(r'e\s*$', '', name)
    # Count vowel groups
    vowel_groups = re.findall(r'[aeiou]+', name)
    count = len(vowel_groups)
    return max(1, count)  # At least 1 syllable

def letter_to_number(letter):
    """Convert letter to alphabetical position (A=1, Z=26)"""
    return ord(letter.upper()) - ord('A') + 1

def calculate_numerology_score(name):
    """Sum of all letter positions (A=1, B=2, ... Z=26)"""
    return sum(letter_to_number(c) for c in name if c.isalpha())

# First letter alphabetical position
df['first_letter_position'] = df.index.map(lambda x: letter_to_number(x[0]))
add_to_codebook('first_letter_position',
                'Alphabetical position of first letter (A=1, Z=26)',
                'Derived from country name')

# Last letter alphabetical position
df['last_letter_position'] = df.index.map(lambda x: letter_to_number(x.strip()[-1]))
add_to_codebook('last_letter_position',
                'Alphabetical position of last letter (A=1, Z=26)',
                'Derived from country name')

# Syllable count
df['syllables_in_country_name'] = df.index.map(count_syllables)
add_to_codebook('syllables_in_country_name',
                'Approximate number of syllables in country name',
                'Derived from country name')

# Unique letters count
df['unique_letters_count'] = df.index.map(lambda x: len(set(c.lower() for c in x if c.isalpha())))
add_to_codebook('unique_letters_count',
                'Number of unique letters in country name',
                'Derived from country name')

# Vowel to consonant ratio
def vowel_consonant_ratio(name):
    vowels = sum(1 for c in name.lower() if c in 'aeiou')
    consonants = sum(1 for c in name.lower() if c.isalpha() and c not in 'aeiou')
    return vowels / consonants if consonants > 0 else 0

df['vowel_to_consonant_ratio'] = df.index.map(vowel_consonant_ratio)
add_to_codebook('vowel_to_consonant_ratio',
                'Ratio of vowels to consonants in country name',
                'Derived from country name')

# Repeated letters count
def count_repeated_letters(name):
    name = name.lower().replace(' ', '')
    letter_counts = Counter(c for c in name if c.isalpha())
    return sum(count - 1 for count in letter_counts.values() if count > 1)

df['repeated_letters_count'] = df.index.map(count_repeated_letters)
add_to_codebook('repeated_letters_count',
                'Number of repeated letters in country name (e.g., Philippines has repeated p)',
                'Derived from country name')

# Longest consonant cluster
def longest_consonant_cluster(name):
    name = name.lower().replace(' ', '')
    clusters = re.findall(r'[^aeiou]+', name)
    return max(len(c) for c in clusters) if clusters else 0

df['longest_consonant_cluster'] = df.index.map(longest_consonant_cluster)
add_to_codebook('longest_consonant_cluster',
                'Length of longest consonant cluster in country name',
                'Derived from country name')

# Name numerology score (A=1, B=2, ... Z=26, sum all)
df['name_numerology_score'] = df.index.map(calculate_numerology_score)
add_to_codebook('name_numerology_score',
                'Numerology score: sum of alphabetical positions of all letters',
                'Derived from country name (pseudoscience)')

# Lucky number (numerology score mod 9)
df['name_lucky_number'] = df['name_numerology_score'] % 9
df['name_lucky_number'] = df['name_lucky_number'].replace(0, 9)  # 0 becomes 9 in numerology
add_to_codebook('name_lucky_number',
                'Lucky number from numerology (score mod 9, range 1-9)',
                'Derived from country name (pseudoscience)')

# Alphabetical rank
df['country_name_alphabetical_rank'] = df.index.to_series().rank(method='min').astype(int)
add_to_codebook('country_name_alphabetical_rank',
                'Alphabetical ranking of country name (1=first, 254=last)',
                'Derived from country name')

print(f"  ✓ Added 10 name-based linguistic features")

# ============================================================================
# PART 2: RATIOS AND COMBINATIONS OF EXISTING BIZARRE FEATURES
# ============================================================================

print("\n" + "=" * 80)
print("PART 2: RATIOS FROM EXISTING BIZARRE FEATURES")
print("=" * 80)

# Get population for per-capita calculations
# Use labor_force_total as proxy (multiply by ~2.5 to estimate total population)
if 'labor_force_total' in df.columns:
    population = df['labor_force_total'] * 2.5  # Rough estimate: labor force is ~40% of population
    print(f"  Using labor_force_total × 2.5 as population proxy")
elif 'population_total' in df.columns:
    population = df['population_total']
else:
    print("  ⚠️  Warning: No population data found, per-million features will use labor force only")
    population = df.get('labor_force_total', pd.Series(1_000_000, index=df.index))

# McDonald's per million people
if 'mcdonalds_restaurants' in df.columns:
    df['mcdonalds_per_million'] = (df['mcdonalds_restaurants'] / population * 1_000_000).round(2)
    add_to_codebook('mcdonalds_per_million',
                    "McDonald's restaurants per million people",
                    'Derived from McDonald\'s data / population')

# Starbucks per million people
if 'starbucks_locations' in df.columns:
    df['starbucks_per_million'] = (df['starbucks_locations'] / population * 1_000_000).round(2)
    add_to_codebook('starbucks_per_million',
                    'Starbucks locations per million people',
                    'Derived from Starbucks data / population')

# Casinos per million people
if 'casinos_total' in df.columns:
    df['casinos_per_million'] = (df['casinos_total'] / population * 1_000_000).round(2)
    add_to_codebook('casinos_per_million',
                    'Casinos per million people',
                    'Derived from casino data / population')

# Golf courses per million people
if 'golf_courses' in df.columns:
    df['golf_courses_per_million'] = (df['golf_courses'] / population * 1_000_000).round(2)
    add_to_codebook('golf_courses_per_million',
                    'Golf courses per million people',
                    'Derived from golf course data / population')

# Crypto ATMs per million people
if 'cryptocurrency_atms' in df.columns:
    df['crypto_atms_per_million'] = (df['cryptocurrency_atms'] / population * 1_000_000).round(2)
    add_to_codebook('crypto_atms_per_million',
                    'Cryptocurrency ATMs per million people',
                    'Derived from crypto ATM data / population')

# Michelin stars per million people
if 'michelin_stars_total' in df.columns:
    df['michelin_stars_per_million'] = (df['michelin_stars_total'] / population * 1_000_000).round(2)
    add_to_codebook('michelin_stars_per_million',
                    'Michelin stars per million people',
                    'Derived from Michelin data / population')

# Theme parks per million people
if 'theme_parks' in df.columns:
    df['theme_parks_per_million'] = (df['theme_parks'] / population * 1_000_000).round(2)
    add_to_codebook('theme_parks_per_million',
                    'Theme parks per million people',
                    'Derived from theme park data / population')

# Beer to wine ratio
if 'beer_consumption_liters_pc' in df.columns and 'wine_consumption_liters_pc' in df.columns:
    # Avoid division by zero
    wine_safe = df['wine_consumption_liters_pc'].replace(0, 0.01)
    df['beer_to_wine_ratio'] = (df['beer_consumption_liters_pc'] / wine_safe).round(2)
    add_to_codebook('beer_to_wine_ratio',
                    'Ratio of beer consumption to wine consumption per capita',
                    'Derived from beer and wine consumption data')

# Total alcohol consumption
if 'beer_consumption_liters_pc' in df.columns and 'wine_consumption_liters_pc' in df.columns:
    df['total_alcohol_liters_pc'] = (df['beer_consumption_liters_pc'] +
                                      df['wine_consumption_liters_pc']).round(2)
    add_to_codebook('total_alcohol_liters_pc',
                    'Total alcohol consumption (beer + wine) per capita in liters',
                    'Derived from beer and wine consumption data')

# Coffee to population ratio (scaled)
if 'coffee_consumption_kg_pc' in df.columns:
    df['coffee_intensity_score'] = (df['coffee_consumption_kg_pc'] * 100).round(2)
    add_to_codebook('coffee_intensity_score',
                    'Coffee consumption intensity score (kg per capita × 100)',
                    'Derived from coffee consumption data')

# Total competition wins
total_wins_cols = []
if 'eurovision_wins' in df.columns:
    total_wins_cols.append('eurovision_wins')
if 'fifa_world_cup_wins' in df.columns:
    total_wins_cols.append('fifa_world_cup_wins')
if 'fifa_womens_world_cup_wins' in df.columns:
    total_wins_cols.append('fifa_womens_world_cup_wins')
if 'olympic_medals_total' in df.columns:
    total_wins_cols.append('olympic_medals_total')
if 'miss_universe_wins' in df.columns:
    total_wins_cols.append('miss_universe_wins')

if total_wins_cols:
    df['total_competition_wins'] = df[total_wins_cols].sum(axis=1)
    add_to_codebook('total_competition_wins',
                    'Total wins across Eurovision, FIFA World Cups, Olympics, and Miss Universe',
                    'Derived from competition data')

    # Wins per million people
    df['competition_wins_per_million'] = (df['total_competition_wins'] / population * 1_000_000).round(2)
    add_to_codebook('competition_wins_per_million',
                    'Total competition wins per million people',
                    'Derived from competition data / population')

# McDonald's to Starbucks ratio
if 'mcdonalds_restaurants' in df.columns and 'starbucks_locations' in df.columns:
    starbucks_safe = df['starbucks_locations'].replace(0, 0.1)
    df['mcdonalds_to_starbucks_ratio'] = (df['mcdonalds_restaurants'] / starbucks_safe).round(2)
    add_to_codebook('mcdonalds_to_starbucks_ratio',
                    "Ratio of McDonald's to Starbucks locations",
                    'Derived from McDonald\'s and Starbucks data')

# Consumer culture score (normalized)
consumer_cols = []
if 'mcdonalds_restaurants' in df.columns:
    consumer_cols.append('mcdonalds_restaurants')
if 'starbucks_locations' in df.columns:
    consumer_cols.append('starbucks_locations')
if 'ikea_stores' in df.columns:
    consumer_cols.append('ikea_stores')

if consumer_cols:
    df['consumer_culture_score'] = df[consumer_cols].sum(axis=1)
    add_to_codebook('consumer_culture_score',
                    'Total count of McDonald\'s, Starbucks, and IKEA locations',
                    'Derived from retail location data')

# Entertainment infrastructure score
entertainment_cols = []
if 'casinos_total' in df.columns:
    entertainment_cols.append('casinos_total')
if 'theme_parks' in df.columns:
    entertainment_cols.append('theme_parks')
if 'golf_courses' in df.columns:
    entertainment_cols.append('golf_courses')

if entertainment_cols:
    df['entertainment_infrastructure_score'] = df[entertainment_cols].sum(axis=1)
    add_to_codebook('entertainment_infrastructure_score',
                    'Total count of casinos, theme parks, and golf courses',
                    'Derived from entertainment venue data')

# Prestige score
prestige_cols = []
if 'unesco_world_heritage_sites' in df.columns:
    prestige_cols.append('unesco_world_heritage_sites')
if 'michelin_stars_total' in df.columns:
    prestige_cols.append('michelin_stars_total')
if 'olympic_medals_total' in df.columns:
    prestige_cols.append('olympic_medals_total')

if prestige_cols:
    df['prestige_score'] = df[prestige_cols].sum(axis=1)
    add_to_codebook('prestige_score',
                    'Combined prestige score: UNESCO sites + Michelin stars + Olympic medals',
                    'Derived from cultural and sporting achievement data')

ratio_count = len([c for c in df.columns if c not in codebook_df['column_name'].tolist()
                   and c in ['mcdonalds_per_million', 'starbucks_per_million', 'casinos_per_million',
                            'golf_courses_per_million', 'crypto_atms_per_million', 'michelin_stars_per_million',
                            'theme_parks_per_million', 'beer_to_wine_ratio', 'total_alcohol_liters_pc',
                            'coffee_intensity_score', 'total_competition_wins', 'competition_wins_per_million',
                            'mcdonalds_to_starbucks_ratio', 'consumer_culture_score',
                            'entertainment_infrastructure_score', 'prestige_score']])
print(f"  ✓ Added {ratio_count} ratio/combination features")

# ============================================================================
# PART 3: GEOGRAPHIC TRANSFORMATIONS
# ============================================================================

print("\n" + "=" * 80)
print("PART 3: GEOGRAPHIC TRANSFORMATIONS")
print("=" * 80)

# Try to find area column (used multiple times below)
area_col = None
for col in df.columns:
    if 'area' in col.lower() and 'land' in col.lower():
        area_col = col
        break

# Distance from equator (absolute latitude)
if 'latitude_avg' in df.columns:
    df['distance_from_equator'] = df['latitude_avg'].abs().round(2)
    add_to_codebook('distance_from_equator',
                    'Absolute latitude (distance from equator in degrees)',
                    'Derived from latitude data')

# Coastline to area ratio (if we have area)
if 'coastline_km' in df.columns and area_col:
    area_safe = df[area_col].replace(0, 1)  # Avoid division by zero
    df['coastline_to_area_ratio'] = (df['coastline_km'] / area_safe * 1000).round(4)
    add_to_codebook('coastline_to_area_ratio',
                    'Ratio of coastline length to land area (km coastline per 1000 km² land)',
                    'Derived from coastline and area data')

# Islands per 1000 sq km
if 'num_islands' in df.columns and area_col:
    area_safe = df[area_col].replace(0, 1)
    df['islands_per_1000_sqkm'] = (df['num_islands'] / area_safe * 1000).round(2)
    add_to_codebook('islands_per_1000_sqkm',
                    'Number of islands per 1000 km² of land area',
                    'Derived from island count and area data')

# Airports per 1000 sq km
if 'airports_total' in df.columns and area_col:
    area_safe = df[area_col].replace(0, 1)
    df['airports_per_1000_sqkm'] = (df['airports_total'] / area_safe * 1000).round(2)
    add_to_codebook('airports_per_1000_sqkm',
                    'Number of airports per 1000 km² of land area',
                    'Derived from airport count and area data')

# Skyscrapers per million people
if 'skyscrapers_over_150m' in df.columns:
    df['skyscrapers_per_million'] = (df['skyscrapers_over_150m'] / population * 1_000_000).round(2)
    add_to_codebook('skyscrapers_per_million',
                    'Skyscrapers over 150m per million people',
                    'Derived from skyscraper data / population')

# UNESCO sites per 1000 sq km
if 'unesco_world_heritage_sites' in df.columns and area_col:
    area_safe = df[area_col].replace(0, 1)
    df['unesco_sites_per_1000_sqkm'] = (df['unesco_world_heritage_sites'] / area_safe * 1000).round(4)
    add_to_codebook('unesco_sites_per_1000_sqkm',
                    'UNESCO World Heritage Sites per 1000 km² of land area',
                    'Derived from UNESCO data and area data')

geo_count = len([c for c in df.columns if c not in codebook_df['column_name'].tolist()
                 and c in ['distance_from_equator', 'coastline_to_area_ratio', 'islands_per_1000_sqkm',
                          'airports_per_1000_sqkm', 'skyscrapers_per_million', 'unesco_sites_per_1000_sqkm']])
print(f"  ✓ Added {geo_count} geographic transformation features")

# ============================================================================
# PART 4: RANKING FEATURES
# ============================================================================

print("\n" + "=" * 80)
print("PART 4: RANKING FEATURES (for continuous variation)")
print("=" * 80)

# Beer consumption rank
if 'beer_consumption_liters_pc' in df.columns:
    df['beer_consumption_rank'] = df['beer_consumption_liters_pc'].rank(ascending=False, method='min')
    add_to_codebook('beer_consumption_rank',
                    'Ranking by beer consumption per capita (1=highest consumer)',
                    'Derived from beer consumption data')

# Wine consumption rank
if 'wine_consumption_liters_pc' in df.columns:
    df['wine_consumption_rank'] = df['wine_consumption_liters_pc'].rank(ascending=False, method='min')
    add_to_codebook('wine_consumption_rank',
                    'Ranking by wine consumption per capita (1=highest consumer)',
                    'Derived from wine consumption data')

# Coffee consumption rank
if 'coffee_consumption_kg_pc' in df.columns:
    df['coffee_consumption_rank'] = df['coffee_consumption_kg_pc'].rank(ascending=False, method='min')
    add_to_codebook('coffee_consumption_rank',
                    'Ranking by coffee consumption per capita (1=highest consumer)',
                    'Derived from coffee consumption data')

# Eurovision rank
if 'eurovision_wins' in df.columns:
    df['eurovision_rank'] = df['eurovision_wins'].rank(ascending=False, method='min')
    add_to_codebook('eurovision_rank',
                    'Ranking by Eurovision Song Contest wins (1=most wins)',
                    'Derived from Eurovision data')

# Latitude rank (northernmost to southernmost)
if 'latitude_avg' in df.columns:
    df['latitude_rank'] = df['latitude_avg'].rank(ascending=False, method='min')
    add_to_codebook('latitude_rank',
                    'Ranking by latitude (1=northernmost, 254=southernmost)',
                    'Derived from latitude data')

# Olympic medals rank
if 'olympic_medals_total' in df.columns:
    df['olympic_medals_rank'] = df['olympic_medals_total'].rank(ascending=False, method='min')
    add_to_codebook('olympic_medals_rank',
                    'Ranking by total Olympic medals (1=most medals)',
                    'Derived from Olympic data')

ranking_count = len([c for c in df.columns if c not in codebook_df['column_name'].tolist()
                     and 'rank' in c])
print(f"  ✓ Added {ranking_count} ranking features")

# ============================================================================
# PART 5: PSEUDOSCIENTIFIC FEATURES
# ============================================================================

print("\n" + "=" * 80)
print("PART 5: PSEUDOSCIENTIFIC FEATURES")
print("=" * 80)

# Independence year features (if we have it)
if 'independence_year' in df.columns:
    df['years_since_independence'] = 2020 - df['independence_year']
    add_to_codebook('years_since_independence',
                    'Number of years since independence (as of 2020)',
                    'Derived from independence year')

    df['independence_century'] = (df['independence_year'] // 100).astype(int)
    add_to_codebook('independence_century',
                    'Century of independence (e.g., 18=18th century, 20=20th century)',
                    'Derived from independence year')

    df['independence_decade'] = (df['independence_year'] // 10).astype(int)
    add_to_codebook('independence_decade',
                    'Decade of independence (e.g., 196=1960s)',
                    'Derived from independence year')

# Historical years rank
if 'documented_history_years' in df.columns:
    df['historical_age_rank'] = df['documented_history_years'].rank(ascending=False, method='min')
    add_to_codebook('historical_age_rank',
                    'Ranking by documented history length (1=oldest documented history)',
                    'Derived from documented history data')

pseudo_count = len([c for c in df.columns if c not in codebook_df['column_name'].tolist()
                    and c in ['years_since_independence', 'independence_century', 'independence_decade',
                             'historical_age_rank']])
print(f"  ✓ Added {pseudo_count} pseudoscientific features")

# ============================================================================
# RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

new_features = df.shape[1] - 185  # Starting from 185 features
print(f"\nDataset shape:")
print(f"  Before: 254 countries × 185 features")
print(f"  After:  {df.shape[0]} countries × {df.shape[1]} features")
print(f"  Added:  {new_features} fabricated bizarre features")

# Check for NaN values
nan_counts = df.isnull().sum()
features_with_nans = nan_counts[nan_counts > 0]
if len(features_with_nans) > 0:
    print(f"\n⚠️  Features with NaN values:")
    for col, count in features_with_nans.items():
        print(f"    {col}: {count} NaNs")
    print(f"\n  Filling NaN values with 0 (most are zeros from missing data in source features)...")
    df = df.fillna(0)
else:
    print(f"\n✓ No NaN values found")

# Update role counts
role_counts = codebook_df['role'].value_counts()
print(f"\nFeature breakdown by role:")
print(f"  {'Role':<12} {'Count':>8}")
print(f"  {'-'*12} {'-'*8}")
for role in ['target', 'causal', 'bizarre', 'noise']:
    count = role_counts.get(role, 0)
    print(f"  {role.capitalize():<12} {count:>8}")

# Show examples of new features
print(f"\n" + "=" * 80)
print("EXAMPLE FABRICATED FEATURES")
print("=" * 80)

# Sample some countries
sample_countries = ['United States', 'Finland', 'France', 'Brazil', 'Japan']
sample_countries = [c for c in sample_countries if c in df.index]

# Linguistic features
print("\n1. LINGUISTIC FEATURES (examples):")
ling_features = ['first_letter_position', 'last_letter_position', 'syllables_in_country_name',
                 'name_numerology_score', 'vowel_to_consonant_ratio']
for country in sample_countries[:3]:
    print(f"\n  {country}:")
    for feat in ling_features:
        if feat in df.columns:
            print(f"    {feat}: {df.loc[country, feat]}")

# Ratio features
print("\n2. RATIO FEATURES (examples):")
ratio_features = ['mcdonalds_per_million', 'beer_to_wine_ratio', 'competition_wins_per_million']
for country in sample_countries[:3]:
    print(f"\n  {country}:")
    for feat in ratio_features:
        if feat in df.columns:
            print(f"    {feat}: {df.loc[country, feat]}")

# Save
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_df.to_csv('codebook.csv', index=False)

print("\n" + "=" * 80)
print("✓ FABRICATION COMPLETE!")
print("=" * 80)

print(f"\nAdded {new_features} new bizarre features:")
print("  ✓ Name linguistics (positions, syllables, numerology)")
print("  ✓ Per-capita ratios (McDonald's, Starbucks, casinos, etc.)")
print("  ✓ Consumption ratios (beer/wine, alcohol totals)")
print("  ✓ Competition scores (total wins, prestige)")
print("  ✓ Geographic transformations (distances, densities)")
print("  ✓ Rankings (consumption, medals, latitude)")
print("  ✓ Pseudoscience (numerology, independence patterns)")

print(f"\nMissing values: {df.isnull().sum().sum()}")
print("\nFiles updated:")
print("  - gdp_spurious_regression_dataset.csv")
print("  - codebook.csv")

print("\n" + "=" * 80)
print("READY FOR MAXIMUM SPURIOUS CORRELATIONS!")
print("=" * 80)
