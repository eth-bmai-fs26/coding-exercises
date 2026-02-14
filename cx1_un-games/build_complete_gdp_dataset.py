#!/usr/bin/env python3
"""
Complete GDP Spurious Regression Dataset Builder
Combines all data sources and handles missing data
"""

import pandas as pd
import numpy as np
import json
import requests
import pycountry
import zipfile
import io
from pathlib import Path

print("=" * 80)
print("BUILDING COMPLETE GDP SPURIOUS REGRESSION DATASET")
print("=" * 80)

# Load intermediate data
df = pd.read_csv('gdp_dataset_intermediate.csv', index_col=0)
codebook_df = pd.read_csv('codebook_intermediate.csv')
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

YEAR = 2020

print(f"\nStarting with: {df.shape[0]} countries × {df.shape[1]} columns")
print(f"Codebook has {len(codebook)} entries")

# Update todo list
from dataclasses import dataclass

@dataclass
class ProgressTracker:
    completed_sources = []

    def mark_complete(self, source_name):
        self.completed_sources.append(source_name)
        print(f"  ✓ {source_name} complete")

progress = ProgressTracker()

# ============================================================================
# Additional WDI Noise Indicators
# ============================================================================
print("\n[ADDITIONAL WDI] Downloading noise indicators...")

try:
    import wbgapi as wb

    wdi_noise = {
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

    for code, name in wdi_noise.items():
        try:
            data = wb.data.DataFrame(code, time=YEAR, labels=True)
            data = data.reset_index()
            data.columns = ['country', 'iso3', f'YR{YEAR}']
            data = data.set_index('iso3')
            df[name] = data[f'YR{YEAR}']

            try:
                desc = wb.series.info(code).get('value', name)
            except:
                desc = name.replace('_', ' ').title()

            add_to_codebook(name, desc, 'World Bank WDI', 'noise')
        except Exception as e:
            print(f"    Skipped {name}: {e}")

    progress.mark_complete("Additional WDI indicators")
except Exception as e:
    print(f"  ✗ Error with WDI: {e}")

# ============================================================================
# FAOSTAT - Use API instead of bulk downloads
# ============================================================================
print("\n[FAOSTAT] Attempting to get food data via API...")

try:
    # Try FAOSTAT API for food balance
    fao_url = "https://fenixservices.fao.org/faostat/api/v1/en/data/FBS"
    params = {
        'area_cs': 'M49',
        'year': YEAR,
        'element': '664',  # Food supply quantity
        'show_codes': 'true'
    }

    response = requests.get(fao_url, params=params, timeout=60)

    if response.status_code == 200:
        fao_data = response.json()
        if 'data' in fao_data:
            # Convert to dataframe
            fao_df = pd.DataFrame(fao_data['data'])

            # Pivot
            if not fao_df.empty and 'areaCode_M49' in fao_df.columns:
                pivot = fao_df.pivot_table(
                    index='areaCode_M49',
                    columns='item',
                    values='value',
                    aggfunc='first'
                )

                # Map M49 to ISO3
                m49_to_iso3 = {}
                for country in pycountry.countries:
                    try:
                        m49_to_iso3[str(country.numeric)] = country.alpha_3
                    except:
                        pass

                for m49, iso3 in m49_to_iso3.items():
                    if m49 in pivot.index and iso3 in df.index:
                        for item in pivot.columns:
                            col_name = f"food_{item[:40].lower().replace(' ', '_')}_kg_pc"
                            df.loc[iso3, col_name] = pivot.loc[m49, item]
                            add_to_codebook(col_name, f"Food: {item} (kg/capita/year)", 'FAOSTAT', 'noise')

                progress.mark_complete(f"FAOSTAT food data ({len(pivot.columns)} items)")
    else:
        print(f"  ✗ FAOSTAT API returned status {response.status_code}")

except Exception as e:
    print(f"  ✗ FAOSTAT API failed: {e}")
    print("  Continuing without detailed food data...")

# ============================================================================
# Bizarre Covariates
# ============================================================================
print("\n[BIZARRE] Adding bizarre covariates...")

# Nobel Prizes
try:
    url = "https://api.nobelprize.org/2.1/laureates?limit=1000"
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()
        nobel_counts = {}

        iso3_map = {country.name: country.alpha_3 for country in pycountry.countries}
        iso3_map.update({
            'United States': 'USA', 'USA': 'USA', 'United Kingdom': 'GBR',
            'UK': 'GBR', 'Russia': 'RUS', 'Germany': 'DEU', 'France': 'FRA',
        })

        for laureate in data.get('laureates', []):
            birth = laureate.get('birth', {})
            loc = birth.get('place', {})
            country_data = loc.get('country', {})
            country_name = country_data.get('en', '')

            iso3 = iso3_map.get(country_name, '')
            if iso3:
                nobel_counts[iso3] = nobel_counts.get(iso3, 0) + 1

        for iso3, count in nobel_counts.items():
            if iso3 in df.index:
                df.loc[iso3, 'nobel_prizes_total'] = count
                if df.loc[iso3, 'population'] > 0:
                    df.loc[iso3, 'nobel_prizes_per_million'] = (count / df.loc[iso3, 'population']) * 1e6

        add_to_codebook('nobel_prizes_total', 'Nobel laureates born in country', 'Nobel API', 'bizarre')
        add_to_codebook('nobel_prizes_per_million', 'Nobel laureates per million', 'Nobel API', 'bizarre')
        print("  ✓ Nobel prizes")
except:
    print("  ✗ Nobel prizes failed")

# Hard-coded bizarre data
bizarre_data = {
    'miss_universe_wins': {
        'data': {'USA': 9, 'VEN': 7, 'PRI': 5, 'PHL': 4, 'IND': 3, 'ZAF': 3, 'SWE': 3,
                 'BRA': 2, 'MEX': 3, 'JPN': 2, 'FIN': 1, 'COL': 1, 'THA': 2, 'AUS': 2},
        'desc': 'Miss Universe wins (all-time)', 'source': 'Wikipedia'
    },
    'ikea_stores': {
        'data': {'DEU': 54, 'USA': 52, 'FRA': 34, 'ITA': 22, 'ESP': 20, 'GBR': 22,
                 'CAN': 14, 'POL': 11, 'SWE': 20, 'NLD': 12, 'AUS': 10, 'CHE': 9},
        'desc': 'Number of IKEA stores', 'source': 'IKEA/Wikipedia'
    },
    'mcdonalds_restaurants': {
        'data': {'USA': 13438, 'JPN': 2975, 'CHN': 3383, 'DEU': 1480, 'CAN': 1400,
                 'GBR': 1300, 'FRA': 1485, 'AUS': 1010, 'BRA': 1047, 'ITA': 615},
        'desc': "Number of McDonald's restaurants", 'source': 'Wikipedia'
    },
    'unesco_world_heritage_sites': {
        'data': {'ITA': 58, 'CHN': 56, 'DEU': 51, 'FRA': 49, 'ESP': 49, 'IND': 40,
                 'MEX': 35, 'GBR': 33, 'RUS': 30, 'USA': 24, 'IRN': 26, 'JPN': 25},
        'desc': 'UNESCO World Heritage Sites', 'source': 'UNESCO'
    },
    'olympic_medals_total': {
        'data': {'USA': 2959, 'RUS': 1865, 'GBR': 918, 'DEU': 855, 'FRA': 840,
                 'ITA': 701, 'SWE': 652, 'CHN': 634, 'AUS': 562, 'HUN': 511},
        'desc': 'Olympic medals (all-time summer)', 'source': 'Wikipedia'
    },
    'active_volcanoes': {
        'data': {'IDN': 76, 'JPN': 50, 'USA': 46, 'RUS': 30, 'CHL': 28,
                 'PHL': 24, 'MEX': 18, 'NZL': 12, 'PNG': 14, 'ISL': 9},
        'desc': 'Number of active volcanoes', 'source': 'Smithsonian GVP'
    },
}

for col_name, info in bizarre_data.items():
    # Initialize column if not exists
    if col_name not in df.columns:
        df[col_name] = np.nan

    for iso3, value in info['data'].items():
        if iso3 in df.index:
            df.loc[iso3, col_name] = value

            # Add per capita version for some
            if col_name in ['ikea_stores', 'mcdonalds_restaurants', 'olympic_medals_total']:
                pc_col = col_name + '_per_million'
                if pc_col not in df.columns:
                    df[pc_col] = np.nan
                if 'population' in df.columns and df.loc[iso3, 'population'] > 0:
                    df.loc[iso3, pc_col] = (value / df.loc[iso3, 'population']) * 1e6

                if pc_col not in [c['column_name'] for c in codebook]:
                    add_to_codebook(pc_col, info['desc'] + ' per million', info['source'], 'bizarre')

    df[col_name] = df[col_name].fillna(0)
    add_to_codebook(col_name, info['desc'], info['source'], 'bizarre')

print(f"  ✓ Added {len(bizarre_data)} hard-coded bizarre features")

# Trivial features
df['letters_in_country_name'] = df['country'].str.len()
df['vowels_in_country_name'] = df['country'].str.lower().str.count('[aeiou]')
df['consonants_in_country_name'] = df['letters_in_country_name'] - df['vowels_in_country_name']
df['words_in_country_name'] = df['country'].str.split().str.len()
df['country_name_starts_with_vowel'] = df['country'].str[0].str.lower().isin(list('aeiou')).astype(int)

trivial = [
    ('letters_in_country_name', 'Letters in country name'),
    ('vowels_in_country_name', 'Vowels in country name'),
    ('consonants_in_country_name', 'Consonants in country name'),
    ('words_in_country_name', 'Words in country name'),
    ('country_name_starts_with_vowel', 'Starts with vowel (1=yes)'),
]

for col, desc in trivial:
    add_to_codebook(col, desc, 'Computed', 'bizarre')

print("  ✓ Added trivial computed features")

# Geographic features
df['num_time_zones'] = 1  # Initialize with default
time_zones = {'RUS': 11, 'USA': 6, 'FRA': 12, 'AUS': 3, 'GBR': 9, 'CAN': 6}
for iso3, tz in time_zones.items():
    if iso3 in df.index:
        df.loc[iso3, 'num_time_zones'] = tz

df['num_border_countries'] = 0  # Initialize with default
borders = {'CHN': 14, 'RUS': 14, 'BRA': 10, 'DEU': 9, 'FRA': 8, 'AUT': 8}
for iso3, n in borders.items():
    if iso3 in df.index:
        df.loc[iso3, 'num_border_countries'] = n

add_to_codebook('num_time_zones', 'Number of time zones', 'Wikipedia', 'bizarre')
add_to_codebook('num_border_countries', 'Number of land borders', 'Wikipedia', 'bizarre')

print("  ✓ Added geographic features")

progress.mark_complete("All bizarre covariates")

print("\n" + "=" * 80)
print(f"Dataset before cleaning: {df.shape[0]} countries × {df.shape[1]} columns")
print("=" * 80)

# ============================================================================
# DATA CLEANING AND MISSING VALUE HANDLING
# ============================================================================
print("\n[CLEANING] Handling missing data...")

# Drop 'country' column as it's not a feature
if 'country' in df.columns:
    country_names = df['country'].copy()
    df = df.drop(columns=['country'])

# Drop 'population' as it was just for computing per-capita
if 'population' in df.columns:
    df = df.drop(columns=['population'])

# Remove codebook entries for dropped columns
codebook = [c for c in codebook if c['column_name'] not in ['country', 'population']]

print(f"\nBefore cleaning: {df.shape}")

# 1. Drop countries with > 50% missing
missing_by_country = df.isnull().sum(axis=1) / len(df.columns)
countries_to_keep = missing_by_country[missing_by_country <= 0.5].index
print(f"  Keeping {len(countries_to_keep)} countries (dropped {len(df) - len(countries_to_keep)} with >50% missing)")
df = df.loc[countries_to_keep]

# 2. Drop columns with > 30% missing
missing_by_col = df.isnull().sum() / len(df)
cols_to_keep = missing_by_col[missing_by_col <= 0.3].index
print(f"  Keeping {len(cols_to_keep)} columns (dropped {len(df.columns) - len(cols_to_keep)} with >30% missing)")

dropped_cols = set(df.columns) - set(cols_to_keep)
df = df[cols_to_keep]

# Update codebook
codebook = [c for c in codebook if c['column_name'] not in dropped_cols]

# 3. Impute remaining missing with column medians
print(f"  Imputing remaining {df.isnull().sum().sum()} missing values with column medians...")
df = df.fillna(df.median())

# 4. Ensure target variable is present
if 'gdp_per_capita_usd' not in df.columns:
    print("  ERROR: Target variable was dropped!")
    exit(1)

# 5. Drop any remaining rows with missing target
df = df.dropna(subset=['gdp_per_capita_usd'])

print(f"\nAfter cleaning: {df.shape}")

# ============================================================================
# SAVE FINAL FILES
# ============================================================================
print("\n[SAVING] Writing final files...")

# Save dataset
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
print(f"  ✓ Saved dataset: {df.shape[0]} countries × {df.shape[1]} features")

# Save codebook
codebook_df = pd.DataFrame(codebook)
codebook_df = codebook_df[codebook_df['column_name'].isin(df.columns)]
codebook_df.to_csv('codebook.csv', index=False)
print(f"  ✓ Saved codebook: {len(codebook_df)} entries")

# Print summary
print("\n" + "=" * 80)
print("FINAL DATASET SUMMARY")
print("=" * 80)

role_counts = codebook_df['role'].value_counts()
print(f"\nDimensions: {df.shape[0]} countries × {df.shape[1]} features")
print(f"\nFeature breakdown:")
for role, count in role_counts.items():
    print(f"  {role.capitalize()}: {count}")

print(f"\nMissing values: {df.isnull().sum().sum()} (should be 0)")
print(f"\nTarget variable (GDP per capita):")
print(f"  Min: ${df['gdp_per_capita_usd'].min():,.2f}")
print(f"  Max: ${df['gdp_per_capita_usd'].max():,.2f}")
print(f"  Mean: ${df['gdp_per_capita_usd'].mean():,.2f}")
print(f"  Median: ${df['gdp_per_capita_usd'].median():,.2f}")

print("\n" + "=" * 80)
print("✓ DATASET BUILD COMPLETE!")
print("=" * 80)
print("\nFiles created:")
print("  - gdp_spurious_regression_dataset.csv")
print("  - codebook.csv")
