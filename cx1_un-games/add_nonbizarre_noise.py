#!/usr/bin/env python3
"""
Add Non-Bizarre but Non-Causal Features

These are real, measurable features that logically should NOT predict GDP,
making them perfect "noise" for teaching feature selection.
"""

import pandas as pd
import numpy as np
import pycountry

print("=" * 80)
print("ADDING NON-BIZARRE NON-CAUSAL FEATURES")
print("=" * 80)

# Load dataset
df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook_df = pd.read_csv('codebook.csv')
codebook = codebook_df.to_dict('records')

def add_to_codebook(column_name, description, source, role):
    if column_name not in [c['column_name'] for c in codebook]:
        codebook.append({
            'column_name': column_name,
            'description': description,
            'source': source,
            'role': role
        })

# Create name to ISO3 mapping
name_to_iso3 = {}
for country in pycountry.countries:
    name_to_iso3[country.name] = country.alpha_3

wb_names = {
    'United States': 'USA', 'United Kingdom': 'GBR', 'Korea, Rep.': 'KOR',
    'Iran, Islamic Rep.': 'IRN', 'Egypt, Arab Rep.': 'EGY', 'Venezuela, RB': 'VEN',
    'Yemen, Rep.': 'YEM', 'Turkiye': 'TUR', 'Czechia': 'CZE', 'Slovak Republic': 'SVK',
    'Russian Federation': 'RUS', 'Lao PDR': 'LAO', 'Kyrgyz Republic': 'KGZ',
}
name_to_iso3.update(wb_names)

def add_feature_by_iso3(feature_dict, column_name, description, source):
    """Add feature using ISO3 codes"""
    df[column_name] = 0.0  # or np.nan for continuous features
    for name in df.index:
        iso3 = name_to_iso3.get(name)
        if iso3 and iso3 in feature_dict:
            df.loc[name, column_name] = feature_dict[iso3]
    add_to_codebook(column_name, description, source, 'noise')
    return (df[column_name] != 0).sum()

print(f"\nStarting: {df.shape[0]} countries × {df.shape[1]} features")

# =============================================================================
# CATEGORY 1: Geographic/Physical Features
# =============================================================================
print("\n[GEOGRAPHY] Adding geographic features...")

# Latitude (absolute distance from equator)
latitudes = {
    'ISL': 65, 'NOR': 62, 'SWE': 62, 'FIN': 64, 'RUS': 60, 'CAN': 56,
    'DNK': 56, 'LTU': 55, 'LVA': 57, 'EST': 59, 'GBR': 54, 'IRL': 53,
    'NLD': 52, 'DEU': 51, 'POL': 52, 'BLR': 54, 'UKR': 49, 'KAZ': 48,
    'MNG': 46, 'USA': 38, 'CHN': 35, 'JPN': 36, 'KOR': 37, 'ESP': 40,
    'ITA': 42, 'GRC': 39, 'TUR': 39, 'IRN': 32, 'AFG': 33, 'PAK': 30,
    'IND': 20, 'THA': 15, 'PHL': 13, 'MYS': 2, 'SGP': 1, 'IDN': 5,
    'BRA': 10, 'ARG': 34, 'CHL': 30, 'AUS': 25, 'NZL': 41, 'ZAF': 29,
}
n = add_feature_by_iso3(latitudes, 'latitude_abs', 'Absolute latitude (distance from equator)', 'Geographic')
print(f"  ✓ Latitude ({n} countries)")

# Average elevation (meters)
elevations = {
    'CHN': 1840, 'NPL': 3265, 'BTN': 3280, 'KGZ': 2988, 'TJK': 3186,
    'AFG': 1884, 'AND': 1996, 'LIE': 1500, 'BOL': 1192, 'PER': 1555,
    'CHL': 1871, 'ECU': 1117, 'COL': 593, 'ETH': 1330, 'RWA': 1598,
    'USA': 760, 'CAN': 487, 'MEX': 1111, 'BRA': 320, 'ARG': 595,
    'AUS': 330, 'NZL': 388, 'JPN': 438, 'CHE': 1350, 'AUT': 910,
    'ITA': 538, 'ESP': 660, 'FRA': 375, 'DEU': 263, 'POL': 173,
    'RUS': 600, 'IND': 160, 'PAK': 900, 'IRN': 1305, 'TUR': 1132,
}
n = add_feature_by_iso3(elevations, 'average_elevation_m', 'Average elevation above sea level (meters)', 'Geographic')
print(f"  ✓ Elevation ({n} countries)")

# Coastline length (km per 1000 sq km of land - to normalize)
coastlines = {
    'CAN': 202080, 'IDN': 54716, 'RUS': 37653, 'PHL': 36289, 'JPN': 29751,
    'AUS': 25760, 'NOR': 25148, 'USA': 19924, 'NZL': 15134, 'CHN': 14500,
    'GRC': 13676, 'GBR': 12429, 'MEX': 9330, 'ITA': 7600, 'IND': 7517,
    'DNK': 7314, 'TUR': 7200, 'CHL': 6435, 'KOR': 2413, 'FRA': 3427,
    'ESP': 4964, 'BRA': 7491, 'ARG': 4989, 'SWE': 3218, 'FIN': 1250,
}
n = add_feature_by_iso3(coastlines, 'coastline_length_km', 'Coastline length (km)', 'Geographic')
print(f"  ✓ Coastline ({n} countries)")

# Number of islands (for island nations/countries with significant islands)
islands = {
    'IDN': 17508, 'PHL': 7641, 'JPN': 6852, 'FIN': 40000, 'SWE': 50000,
    'NOR': 25000, 'CAN': 36563, 'AUS': 8222, 'GRC': 6000, 'GBR': 6289,
    'USA': 18617, 'CHL': 5000, 'KOR': 3348, 'DNK': 7314, 'IRL': 80,
}
n = add_feature_by_iso3(islands, 'number_of_islands', 'Number of islands', 'Geographic')
print(f"  ✓ Islands ({n} countries)")

# =============================================================================
# CATEGORY 2: Biological/Ecological Features
# =============================================================================
print("\n[ECOLOGY] Adding ecological features...")

# Mammal species (approximate)
mammals = {
    'IDN': 670, 'MEX': 544, 'BRA': 648, 'CHN': 551, 'COL': 456,
    'PER': 441, 'IND': 412, 'UGA': 345, 'TZA': 316, 'KEN': 315,
    'VEN': 353, 'ECU': 382, 'USA': 432, 'MYS': 286, 'AUS': 386,
    'COD': 415, 'CMR': 297, 'ZAF': 299, 'BOL': 316, 'MMR': 300,
}
n = add_feature_by_iso3(mammals, 'mammal_species_count', 'Number of mammal species', 'Ecological')
print(f"  ✓ Mammals ({n} countries)")

# Bird species
birds = {
    'COL': 1871, 'PER': 1781, 'BRA': 1813, 'IDN': 1711, 'ECU': 1616,
    'VEN': 1381, 'CHN': 1314, 'IND': 1263, 'MEX': 1096, 'USA': 1107,
    'ARG': 1026, 'TZA': 1051, 'KEN': 1104, 'AUS': 828, 'BOL': 1441,
    'COD': 1086, 'MYS': 821, 'PHL': 695, 'PNG': 895, 'THA': 1055,
}
n = add_feature_by_iso3(birds, 'bird_species_count', 'Number of bird species', 'Ecological')
print(f"  ✓ Birds ({n} countries)")

# Endemic species (found only in that country)
endemic = {
    'MDG': 280, 'AUS': 254, 'IDN': 219, 'MEX': 215, 'BRA': 191,
    'PHL': 175, 'IND': 158, 'CHN': 145, 'PNG': 137, 'PER': 120,
    'USA': 118, 'ECU': 112, 'TZA': 91, 'COL': 95, 'ZAF': 84,
}
n = add_feature_by_iso3(endemic, 'endemic_species_count', 'Number of endemic species', 'Ecological')
print(f"  ✓ Endemic species ({n} countries)")

# =============================================================================
# CATEGORY 3: Astronomical/Calendar Features
# =============================================================================
print("\n[ASTRONOMY] Adding astronomical features...")

# Hours of daylight on summer solstice
daylight_max = {
    'ISL': 21, 'NOR': 20, 'SWE': 19, 'FIN': 19, 'RUS': 18, 'CAN': 16,
    'DNK': 17, 'EST': 19, 'LVA': 18, 'LTU': 17, 'GBR': 17, 'IRL': 17,
    'DEU': 16, 'POL': 16, 'USA': 15, 'CHN': 15, 'JPN': 15, 'KOR': 15,
    'ESP': 15, 'ITA': 15, 'GRC': 15, 'TUR': 15, 'IRN': 14, 'IND': 14,
    'THA': 13, 'MYS': 12, 'SGP': 12, 'IDN': 12, 'BRA': 13, 'ARG': 14,
}
n = add_feature_by_iso3(daylight_max, 'max_daylight_hours', 'Maximum daylight hours (summer solstice)', 'Astronomical')
print(f"  ✓ Max daylight ({n} countries)")

# Seasonal daylight variation (hours between longest and shortest day)
daylight_var = {
    'ISL': 18, 'NOR': 15, 'SWE': 13, 'FIN': 13, 'RUS': 12, 'CAN': 10,
    'DNK': 11, 'EST': 13, 'GBR': 9, 'DEU': 8, 'POL': 8, 'USA': 6,
    'CHN': 6, 'JPN': 6, 'ESP': 6, 'ITA': 6, 'IND': 4, 'THA': 2,
    'MYS': 0, 'SGP': 0, 'IDN': 0, 'BRA': 4, 'ARG': 6, 'AUS': 6,
}
n = add_feature_by_iso3(daylight_var, 'daylight_variation_hours', 'Seasonal daylight variation (hours)', 'Astronomical')
print(f"  ✓ Daylight variation ({n} countries)")

# =============================================================================
# CATEGORY 4: Historical/Cultural Features
# =============================================================================
print("\n[HISTORY] Adding historical features...")

# Years of documented history (very approximate!)
history_years = {
    'IRQ': 5000, 'EGY': 5000, 'CHN': 3500, 'IND': 3000, 'GRC': 3000,
    'IRN': 2700, 'ITA': 2800, 'TUR': 2000, 'SYR': 4000, 'ISR': 3000,
    'JPN': 2000, 'KOR': 2000, 'MEX': 3000, 'PER': 3000, 'BOL': 2500,
    'ESP': 2500, 'FRA': 2500, 'GBR': 2000, 'DEU': 2000, 'RUS': 1200,
    'USA': 400, 'CAN': 400, 'AUS': 250, 'NZL': 200, 'BRA': 500,
}
n = add_feature_by_iso3(history_years, 'documented_history_years', 'Years of documented written history', 'Historical')
print(f"  ✓ Historical years ({n} countries)")

# Years since independence (for countries that gained independence)
independence_years = {
    'USA': 248, 'FRA': 235, 'HAT': 220, 'MEX': 214, 'BRA': 202,
    'ARG': 208, 'CHL': 214, 'PER': 203, 'COL': 214, 'VEN': 214,
    'GRC': 203, 'BEL': 194, 'ITA': 163, 'DEU': 153, 'NOR': 119,
    'IRL': 102, 'ISR': 76, 'IND': 77, 'PAK': 77, 'LKA': 76,
    'MMR': 76, 'IDN': 79, 'PHL': 78, 'KOR': 79, 'VNM': 79,
    'KEN': 61, 'UGA': 62, 'TZA': 63, 'NGA': 64, 'GHA': 67,
}
n = add_feature_by_iso3(independence_years, 'years_since_independence', 'Years since independence (2024 reference)', 'Historical')
print(f"  ✓ Years independent ({n} countries)")

# =============================================================================
# CATEGORY 5: Administrative Features
# =============================================================================
print("\n[ADMINISTRATIVE] Adding administrative features...")

# Number of first-level administrative divisions (states/provinces)
admin_divisions = {
    'USA': 50, 'CHN': 34, 'IND': 36, 'BRA': 26, 'RUS': 85,
    'MEX': 32, 'ARG': 24, 'CAN': 13, 'AUS': 8, 'DEU': 16,
    'ESP': 19, 'ITA': 20, 'FRA': 18, 'GBR': 4, 'JPN': 47,
    'KOR': 17, 'THA': 77, 'VNM': 63, 'PHL': 81, 'IDN': 38,
    'NGA': 36, 'ZAF': 9, 'EGY': 27, 'TUR': 81, 'IRN': 31,
}
n = add_feature_by_iso3(admin_divisions, 'admin_divisions_count', 'Number of first-level administrative divisions', 'Administrative')
print(f"  ✓ Admin divisions ({n} countries)")

# Government system (encoded: 0=parliamentary, 1=presidential, 2=semi-presidential, 3=other)
govt_system = {
    'USA': 1, 'FRA': 2, 'RUS': 2, 'CHN': 3, 'IND': 0, 'GBR': 0,
    'DEU': 0, 'JPN': 0, 'BRA': 1, 'MEX': 1, 'ARG': 1, 'CHL': 1,
    'ESP': 0, 'ITA': 0, 'CAN': 0, 'AUS': 0, 'KOR': 1, 'TUR': 1,
}
n = add_feature_by_iso3(govt_system, 'government_system_type', 'Government system (0=parl, 1=pres, 2=semi-pres, 3=other)', 'Administrative')
print(f"  ✓ Government type ({n} countries)")

# =============================================================================
# CATEGORY 6: Linguistic Features
# =============================================================================
print("\n[LANGUAGE] Adding linguistic features...")

# Writing system (0=Latin, 1=Cyrillic, 2=Arabic, 3=Chinese, 4=Other)
writing_system = {
    'USA': 0, 'GBR': 0, 'FRA': 0, 'DEU': 0, 'ESP': 0, 'ITA': 0,
    'BRA': 0, 'MEX': 0, 'ARG': 0, 'RUS': 1, 'UKR': 1, 'BLR': 1,
    'BGR': 1, 'SRB': 1, 'SAU': 2, 'EGY': 2, 'IRN': 2, 'IRQ': 2,
    'CHN': 3, 'JPN': 3, 'KOR': 4, 'IND': 4, 'THA': 4, 'VNM': 0,
}
n = add_feature_by_iso3(writing_system, 'primary_writing_system', 'Primary writing system (0=Latin, 1=Cyrillic, 2=Arabic, 3=Chinese, 4=Other)', 'Linguistic')
print(f"  ✓ Writing system ({n} countries)")

# Number of official languages
official_langs = {
    'CHE': 4, 'SGP': 4, 'IND': 22, 'ZAF': 11, 'BEL': 3, 'LUX': 3,
    'CAN': 2, 'FIN': 2, 'IRL': 2, 'NZL': 3, 'PAK': 2, 'PHL': 2,
    'USA': 0, 'CHN': 1, 'JPN': 1, 'KOR': 1, 'FRA': 1, 'DEU': 1,
    'ESP': 1, 'ITA': 1, 'BRA': 1, 'MEX': 1, 'ARG': 1, 'RUS': 1,
}
n = add_feature_by_iso3(official_langs, 'num_official_languages', 'Number of official languages', 'Linguistic')
print(f"  ✓ Official languages ({n} countries)")

# =============================================================================
# Summary and Save
# =============================================================================
print("\n" + "=" * 80)
print("NON-BIZARRE NOISE FEATURES ADDED")
print("=" * 80)

new_features = df.shape[1] - 273  # Original was 273
print(f"\nAdded {new_features} new non-bizarre noise features")
print(f"Dataset shape: {df.shape[0]} countries × {df.shape[1]} features")

# Save
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_df = pd.DataFrame(codebook)
codebook_df.to_csv('codebook.csv', index=False)

print(f"\nMissing values: {df.isnull().sum().sum()}")

print("\n" + "=" * 80)
print("✓ NON-BIZARRE NOISE FEATURES COMPLETE!")
print("=" * 80)

print("\nAdded feature categories:")
print("  • Geographic: latitude, elevation, coastline, islands")
print("  • Ecological: mammal/bird/endemic species counts")
print("  • Astronomical: daylight hours, seasonal variation")
print("  • Historical: documented history, years since independence")
print("  • Administrative: division counts, government type")
print("  • Linguistic: writing system, official languages")

print("\nThese features are:")
print("  ✓ Real, measurable data")
print("  ✓ Non-bizarre (students won't laugh)")
print("  ✓ Logically non-causal (no mechanism to predict GDP)")
print("  ✓ Perfect for teaching critical thinking about features!")
