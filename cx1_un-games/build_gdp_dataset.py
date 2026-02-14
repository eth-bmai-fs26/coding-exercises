#!/usr/bin/env python3
"""
Build GDP Spurious Regression Dataset

This script downloads data from multiple sources to create a dataset for demonstrating
spurious regression and regularization in machine learning.

Target: GDP per capita (2020)
Features: ~40 causal, ~30 bizarre, ~300 noise covariates
"""

import pandas as pd
import numpy as np
import wbgapi as wb
import requests
import pycountry
import time
import zipfile
import io
import os
from pathlib import Path

# Configuration
YEAR = 2020
YEAR_FALLBACK = 2019
DATA_DIR = Path("gdp_dataset_downloads")
DATA_DIR.mkdir(exist_ok=True)

# For tracking the codebook
codebook = []

def add_to_codebook(column_name, description, source, role):
    """Add entry to codebook"""
    codebook.append({
        'column_name': column_name,
        'description': description,
        'source': source,
        'role': role
    })

def get_country_iso3_mapping():
    """Create mapping from various country name formats to ISO3 codes"""
    iso3_map = {}
    for country in pycountry.countries:
        iso3_map[country.name] = country.alpha_3
        iso3_map[country.alpha_2] = country.alpha_3
        iso3_map[country.alpha_3] = country.alpha_3

    # Add common alternatives
    manual_mappings = {
        'United States': 'USA',
        'United Kingdom': 'GBR',
        'Russia': 'RUS',
        'South Korea': 'KOR',
        'Iran': 'IRN',
        'Syria': 'SYR',
        'Venezuela': 'VEN',
        'Bolivia': 'BOL',
        'Tanzania': 'TZA',
        'Vietnam': 'VNM',
        'Laos': 'LAO',
        'Moldova': 'MDA',
        'Czechia': 'CZE',
        'Czech Republic': 'CZE',
        'Türkiye': 'TUR',
        'Turkey': 'TUR',
    }
    iso3_map.update(manual_mappings)
    return iso3_map

print("=" * 80)
print("BUILDING GDP SPURIOUS REGRESSION DATASET")
print("=" * 80)

# ============================================================================
# SOURCE 0: Target Variable and Population
# ============================================================================
print("\n[SOURCE 0] Downloading GDP per capita and population from World Bank...")

try:
    # Get GDP per capita
    gdp_data = wb.data.DataFrame('NY.GDP.PCAP.CD', time=YEAR, labels=True)
    gdp_data = gdp_data.reset_index()
    gdp_data.columns = ['country', 'iso3', f'YR{YEAR}']
    gdp_data = gdp_data.rename(columns={f'YR{YEAR}': 'gdp_per_capita_usd'})

    # Get population
    pop_data = wb.data.DataFrame('SP.POP.TOTL', time=YEAR, labels=True)
    pop_data = pop_data.reset_index()
    pop_data.columns = ['country', 'iso3', f'YR{YEAR}']
    pop_data = pop_data.rename(columns={f'YR{YEAR}': 'population'})

    # Merge
    df = gdp_data.merge(pop_data[['iso3', 'population']], on='iso3', how='left')
    df = df.set_index('iso3')

    print(f"✓ Downloaded GDP and population for {len(df)} countries")

    add_to_codebook('gdp_per_capita_usd', 'GDP per capita, current US dollars', 'World Bank WDI', 'target')
    add_to_codebook('population', 'Total population', 'World Bank WDI', 'metadata')

except Exception as e:
    print(f"✗ Error downloading GDP/population: {e}")
    exit(1)

# ============================================================================
# SOURCE 1: Causal Covariates from World Bank WDI
# ============================================================================
print("\n[SOURCE 1] Downloading causal covariates from World Bank WDI...")

wdi_causal_indicators = {
    'SP.DYN.LE00.IN': 'life_expectancy_at_birth',
    'SP.DYN.TFRT.IN': 'fertility_rate',
    'SP.DYN.IMRT.IN': 'infant_mortality_per_1000',
    'SP.URB.TOTL.IN.ZS': 'pct_urban_population',
    'SE.ADT.LITR.ZS': 'adult_literacy_rate',
    'SE.SEC.ENRR': 'secondary_enrollment_gross',
    'SE.TER.ENRR': 'tertiary_enrollment_gross',
    'NE.GDI.TOTL.ZS': 'gross_capital_formation_pct_gdp',
    'BX.KLT.DINV.WD.GD.ZS': 'fdi_net_inflows_pct_gdp',
    'NY.GNS.ICTR.ZS': 'gross_savings_pct_gdp',
    'NE.TRD.GNFS.ZS': 'trade_pct_gdp',
    'NE.EXP.GNFS.ZS': 'exports_pct_gdp',
    'IT.NET.USER.ZS': 'pct_internet_users',
    'IT.CEL.SETS.P2': 'mobile_subscriptions_per_100',
    'EG.USE.ELEC.KH.PC': 'electric_power_consumption_kwh_pc',
    'FP.CPI.TOTL.ZG': 'inflation_consumer_prices_annual',
    'NE.CON.GOVT.ZS': 'govt_consumption_pct_gdp',
    'GC.TAX.TOTL.GD.ZS': 'tax_revenue_pct_gdp',
    'NY.GDP.TOTL.RT.ZS': 'total_natural_resources_rent_pct_gdp',
}

for indicator_code, col_name in wdi_causal_indicators.items():
    try:
        data = wb.data.DataFrame(indicator_code, time=YEAR, labels=True)
        data = data.reset_index()
        data.columns = ['country', 'iso3', f'YR{YEAR}']
        data = data.set_index('iso3')
        df[col_name] = data[f'YR{YEAR}']

        # Get indicator description
        try:
            indicator_info = wb.series.info(indicator_code)
            description = indicator_info.get('value', col_name)
        except:
            description = col_name.replace('_', ' ').title()

        add_to_codebook(col_name, description, 'World Bank WDI', 'causal')
        print(f"  ✓ {col_name}")
    except Exception as e:
        print(f"  ✗ Failed to download {col_name}: {e}")

print(f"✓ Downloaded {len(wdi_causal_indicators)} causal indicators from WDI")

# ============================================================================
# SOURCE 2: World Governance Indicators
# ============================================================================
print("\n[SOURCE 2] Downloading World Governance Indicators...")

wgi_indicators = {
    'RL.EST': 'rule_of_law_index',
    'CC.EST': 'control_of_corruption_index',
    'RQ.EST': 'regulatory_quality_index',
    'GE.EST': 'government_effectiveness_index',
    'PV.EST': 'political_stability_index',
    'VA.EST': 'voice_and_accountability_index',
}

for indicator_code, col_name in wgi_indicators.items():
    try:
        data = wb.data.DataFrame(indicator_code, time=YEAR, labels=True)
        data = data.reset_index()
        data.columns = ['country', 'iso3', f'YR{YEAR}']
        data = data.set_index('iso3')
        df[col_name] = data[f'YR{YEAR}']

        description = col_name.replace('_', ' ').title()
        add_to_codebook(col_name, description, 'World Bank WGI', 'causal')
        print(f"  ✓ {col_name}")
    except Exception as e:
        print(f"  ✗ Failed to download {col_name}: {e}")

print(f"✓ Downloaded {len(wgi_indicators)} governance indicators")

# ============================================================================
# SOURCE 3: UNDP Human Development Data
# ============================================================================
print("\n[SOURCE 3] Downloading UNDP Human Development data...")

# Try to download HDI data
try:
    # UNDP data API endpoint
    url = "https://hdr.undp.org/sites/default/files/2021-22_HDR/HDR21-22_Composite_indices_complete_time_series.csv"
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        hdi_data = pd.read_csv(io.StringIO(response.text))

        # Filter for 2020 or 2019
        if 2020 in hdi_data.columns or str(2020) in hdi_data.columns:
            year_col = 2020
        elif 2019 in hdi_data.columns or str(2019) in hdi_data.columns:
            year_col = 2019
        else:
            year_col = None

        if year_col:
            iso3_map = get_country_iso3_mapping()

            # Process HDI indicators
            hdi_indicators = {
                'hdi': 'hdi_index',
                'mys': 'mean_years_schooling',
                'eys': 'expected_years_schooling',
                'gii': 'gender_inequality_index',
            }

            for raw_col, new_col in hdi_indicators.items():
                subset = hdi_data[hdi_data['indicator_name'].str.contains(raw_col, case=False, na=False)]
                if not subset.empty:
                    subset = subset[['country', year_col]].copy()
                    subset['iso3'] = subset['country'].map(iso3_map)
                    subset = subset.dropna(subset='iso3').set_index('iso3')

                    for iso3 in subset.index:
                        if iso3 in df.index:
                            df.loc[iso3, new_col] = subset.loc[iso3, year_col]

                    role = 'causal' if 'schooling' in new_col else 'noise'
                    add_to_codebook(new_col, new_col.replace('_', ' ').title(), 'UNDP HDR', role)
                    print(f"  ✓ {new_col}")
    else:
        print(f"  ✗ Could not download UNDP data (status {response.status_code})")

except Exception as e:
    print(f"  ✗ Error downloading UNDP data: {e}")

# ============================================================================
# SOURCE 4: FAOSTAT Food Balance Sheets
# ============================================================================
print("\n[SOURCE 4] Downloading FAOSTAT Food Balance Sheets...")
print("  (This may take several minutes - downloading ~300MB file)")

try:
    fbs_url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheets_E_All_Data_(Normalized).zip"

    fbs_file = DATA_DIR / "faostat_fbs.zip"

    if not fbs_file.exists():
        print("  Downloading Food Balance Sheets...")
        response = requests.get(fbs_url, timeout=300, stream=True)
        with open(fbs_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("  ✓ Download complete")
    else:
        print("  ✓ Using cached file")

    # Extract and read
    with zipfile.ZipFile(fbs_file, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        if csv_files:
            with zip_ref.open(csv_files[0]) as csv_file:
                fbs_data = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)

    # Filter for Food supply quantity (kg/capita/yr) - Element Code 5142 or 664
    # Year 2020, and food items
    fbs_filtered = fbs_data[
        (fbs_data['Year'] == YEAR) &
        (fbs_data['Element'].str.contains('Food supply quantity', case=False, na=False))
    ].copy()

    if fbs_filtered.empty:
        # Try with different element description
        fbs_filtered = fbs_data[
            (fbs_data['Year'] == YEAR) &
            (fbs_data['Element Code'].isin([664, 5142]))
        ].copy()

    if not fbs_filtered.empty:
        # Pivot to wide format
        fbs_pivot = fbs_filtered.pivot_table(
            index='Area Code (M49)',
            columns='Item',
            values='Value',
            aggfunc='first'
        )

        # Map M49 codes to ISO3
        m49_to_iso3 = {}
        for country in pycountry.countries:
            try:
                m49_code = int(country.numeric)
                m49_to_iso3[m49_code] = country.alpha_3
            except:
                pass

        fbs_pivot.index = fbs_pivot.index.map(m49_to_iso3)
        fbs_pivot = fbs_pivot.dropna(how='all')

        # Clean column names
        for col in fbs_pivot.columns:
            clean_name = 'food_' + col.lower().replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('-', '_')
            clean_name = clean_name[:60]  # Limit length

            # Add to main dataframe
            df[clean_name] = fbs_pivot[col]
            add_to_codebook(clean_name, f"Food supply: {col} (kg/capita/year)", 'FAOSTAT FBS', 'noise')

        print(f"  ✓ Added {len(fbs_pivot.columns)} food commodities")
    else:
        print("  ✗ No food supply data found for 2020")

except Exception as e:
    print(f"  ✗ Error downloading FAOSTAT FBS: {e}")

# ============================================================================
# SOURCE 5: FAOSTAT Livestock
# ============================================================================
print("\n[SOURCE 5] Downloading FAOSTAT Livestock data...")

try:
    livestock_url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/Production_Livestock_E_All_Data_(Normalized).zip"

    livestock_file = DATA_DIR / "faostat_livestock.zip"

    if not livestock_file.exists():
        print("  Downloading Livestock data...")
        response = requests.get(livestock_url, timeout=300, stream=True)
        with open(livestock_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("  ✓ Download complete")
    else:
        print("  ✓ Using cached file")

    with zipfile.ZipFile(livestock_file, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        if csv_files:
            with zip_ref.open(csv_files[0]) as csv_file:
                livestock_data = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)

    # Filter for Stocks (live animals)
    livestock_filtered = livestock_data[
        (livestock_data['Year'] == YEAR) &
        (livestock_data['Element'] == 'Stocks')
    ].copy()

    if livestock_filtered.empty:
        livestock_filtered = livestock_data[
            (livestock_data['Year'] == YEAR) &
            (livestock_data['Element Code'] == 5112)
        ].copy()

    if not livestock_filtered.empty:
        livestock_pivot = livestock_filtered.pivot_table(
            index='Area Code (M49)',
            columns='Item',
            values='Value',
            aggfunc='first'
        )

        # Map M49 to ISO3
        livestock_pivot.index = livestock_pivot.index.map(m49_to_iso3)
        livestock_pivot = livestock_pivot.dropna(how='all')

        # Divide by population to get per capita
        for col in livestock_pivot.columns:
            clean_name = 'livestock_' + col.lower().replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('-', '_')
            clean_name = clean_name[:60]

            # Per capita calculation
            livestock_pc = livestock_pivot[col] / df['population']
            df[clean_name + '_per_capita'] = livestock_pc

            add_to_codebook(clean_name + '_per_capita', f"Livestock: {col} per capita", 'FAOSTAT Livestock', 'noise')

        print(f"  ✓ Added {len(livestock_pivot.columns)} livestock types")
    else:
        print("  ✗ No livestock data found for 2020")

except Exception as e:
    print(f"  ✗ Error downloading FAOSTAT Livestock: {e}")

# ============================================================================
# SOURCE 6: FAOSTAT Crop Production (Area Harvested)
# ============================================================================
print("\n[SOURCE 6] Downloading FAOSTAT Crop Area data...")

try:
    crops_url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/Production_Crops_E_All_Data_(Normalized).zip"

    crops_file = DATA_DIR / "faostat_crops.zip"

    if not crops_file.exists():
        print("  Downloading Crops data...")
        response = requests.get(crops_url, timeout=300, stream=True)
        with open(crops_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("  ✓ Download complete")
    else:
        print("  ✓ Using cached file")

    with zipfile.ZipFile(crops_file, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        if csv_files:
            with zip_ref.open(csv_files[0]) as csv_file:
                crops_data = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)

    # Filter for Area harvested
    crops_filtered = crops_data[
        (crops_data['Year'] == YEAR) &
        (crops_data['Element'] == 'Area harvested')
    ].copy()

    if crops_filtered.empty:
        crops_filtered = crops_data[
            (crops_data['Year'] == YEAR) &
            (crops_data['Element Code'] == 5312)
        ].copy()

    if not crops_filtered.empty:
        crops_pivot = crops_filtered.pivot_table(
            index='Area Code (M49)',
            columns='Item',
            values='Value',
            aggfunc='first'
        )

        crops_pivot.index = crops_pivot.index.map(m49_to_iso3)
        crops_pivot = crops_pivot.dropna(how='all')

        # Divide by population
        for col in crops_pivot.columns:
            clean_name = 'crop_area_' + col.lower().replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('-', '_')
            clean_name = clean_name[:60]

            crop_area_pc = crops_pivot[col] / df['population']
            df[clean_name + '_ha_per_capita'] = crop_area_pc

            add_to_codebook(clean_name + '_ha_per_capita', f"Crop area: {col} (ha per capita)", 'FAOSTAT Crops', 'noise')

        print(f"  ✓ Added {len(crops_pivot.columns)} crop types")
    else:
        print("  ✗ No crop area data found for 2020")

except Exception as e:
    print(f"  ✗ Error downloading FAOSTAT Crops: {e}")

print("\n" + "=" * 80)
print(f"Current dataset shape: {df.shape[0]} countries × {df.shape[1]} columns")
print("=" * 80)

# Save intermediate progress
df.to_csv('gdp_dataset_intermediate.csv')
print("\n✓ Intermediate dataset saved to gdp_dataset_intermediate.csv")
print("\nContinuing with additional WDI indicators, WHO data, and bizarre covariates...")
