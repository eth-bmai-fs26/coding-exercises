#!/usr/bin/env python3
"""
Expand GDP dataset with additional noise features to reach 300-500 columns

Since FAOSTAT is unavailable, we'll add:
1. More WDI indicators (there are 1400+ available)
2. Lagged/transformed versions of existing features
3. Random polynomial combinations of existing features
4. Pure synthetic noise features
"""

import pandas as pd
import numpy as np
import wbgapi as wb

print("=" * 80)
print("EXPANDING DATASET WITH ADDITIONAL NOISE FEATURES")
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
print(f"Need to add ~{300 - df.shape[1]} more features to reach target of 300+")

YEAR = 2020
TARGET_FEATURES = 350  # Aim for 350 total features

# ============================================================================
# STRATEGY 1: Download many more WDI indicators
# ============================================================================
print("\n[WDI EXPANSION] Downloading additional WDI indicators...")

# Get a comprehensive list of WDI indicators across various sectors
additional_wdi = {
    # Energy
    'EG.ELC.ACCS.ZS': 'access_to_electricity_pct',
    'EG.USE.PCAP.KG.OE': 'energy_use_kg_oil_equiv_pc',
    'EG.IMP.CONS.ZS': 'energy_imports_pct_use',
    'EG.USE.COMM.FO.ZS': 'fossil_fuel_energy_consumption_pct',
    'EG.ELC.COAL.ZS': 'electricity_from_coal_pct',
    'EG.ELC.NGAS.ZS': 'electricity_from_natural_gas_pct',
    'EG.ELC.NUCL.ZS': 'electricity_from_nuclear_pct',
    'EG.ELC.HYRO.ZS': 'electricity_from_hydro_pct',
    'EG.ELC.PETR.ZS': 'electricity_from_oil_pct',

    # Infrastructure
    'IS.AIR.DPRT': 'air_transport_departures',
    'IS.AIR.PSGR': 'air_transport_passengers',
    'IS.RRS.GOOD.MT.K6': 'rail_goods_transported_million_ton_km',
    'IS.RRS.PASG.KM': 'rail_passengers_carried_million_km',
    'IS.ROD.PAVE.ZS': 'roads_paved_pct',
    'IS.ROD.TOTL.KM': 'roads_total_km',
    'IS.SHP.GOOD.TU': 'container_port_traffic_teu',

    # Finance
    'FB.AST.NPER.ZS': 'bank_nonperforming_loans_pct',
    'FB.BNK.CAPA.ZS': 'bank_capital_to_assets_ratio',
    'FD.AST.PRVT.GD.ZS': 'domestic_credit_to_private_sector_pct_gdp',
    'FS.AST.DOMS.GD.ZS': 'domestic_credit_provided_by_finance_sector_pct_gdp',
    'FM.AST.CGOV.GD.ZS': 'claims_on_central_govt_pct_gdp',
    'FR.INR.LEND': 'lending_interest_rate_pct',
    'FR.INR.RINR': 'real_interest_rate_pct',
    'FI.RES.TOTL.CD': 'total_reserves_current_usd',
    'FI.RES.TOTL.MO': 'reserves_months_imports',

    # Labor & Employment
    'SL.TLF.TOTL.IN': 'labor_force_total',
    'SL.TLF.CACT.ZS': 'labor_force_participation_rate',
    'SL.TLF.CACT.FE.ZS': 'labor_force_participation_female',
    'SL.TLF.CACT.MA.ZS': 'labor_force_participation_male',
    'SL.UEM.ADVN.ZS': 'unemployment_with_advanced_education',
    'SL.UEM.BASC.ZS': 'unemployment_with_basic_education',
    'SL.SRV.EMPL.ZS': 'employment_in_services_pct',
    'SL.EMP.VULN.ZS': 'vulnerable_employment_pct',
    'SL.EMP.WORK.ZS': 'wage_and_salaried_workers_pct',
    'SL.EMP.SELF.ZS': 'self_employed_pct',

    # Demographics
    'SP.POP.GROW': 'population_growth_annual_pct',
    'SP.DYN.CBRT.IN': 'birth_rate_crude_per_1000',
    'SP.DYN.CDRT.IN': 'death_rate_crude_per_1000',
    'SP.DYN.TO65.FE.ZS': 'survival_to_age_65_female',
    'SP.DYN.TO65.MA.ZS': 'survival_to_age_65_male',
    'SP.POP.1564.TO.ZS': 'population_ages_15_64_pct',
    'SP.RUR.TOTL.ZS': 'rural_population_pct',
    'SP.URB.GROW': 'urban_population_growth_annual_pct',
    'SP.POP.DPND.OL': 'age_dependency_ratio_old',
    'SP.POP.DPND.YG': 'age_dependency_ratio_young',

    # Agriculture
    'AG.PRD.FOOD.XD': 'food_production_index',
    'AG.PRD.CROP.XD': 'crop_production_index',
    'AG.PRD.LVSK.XD': 'livestock_production_index',
    'AG.YLD.CREL.KG': 'cereal_yield_kg_per_hectare',
    'AG.CON.FERT.ZS': 'fertilizer_consumption_kg_per_hectare',
    'AG.LND.AGRI.ZS': 'agricultural_land_pct',
    'AG.LND.CROP.ZS': 'arable_land_pct_land_area',
    'AG.LND.PRCP.MM': 'average_precipitation_mm_per_year',
    'AG.LND.EL5M.ZS': 'land_under_cereal_production_hectares',

    # Environment
    'EN.ATM.GHGT.KT.CE': 'greenhouse_gas_emissions_kt_co2_equiv',
    'EN.ATM.METH.KT.CE': 'methane_emissions_kt_co2_equiv',
    'EN.ATM.NOXE.KT.CE': 'nitrous_oxide_emissions_kt_co2_equiv',
    'EN.ATM.SF6G.KT.CE': 'sf6_emissions_kt_co2_equiv',
    'EN.ATM.HFCG.KT.CE': 'hfc_emissions_kt_co2_equiv',
    'EN.ATM.PFCG.KT.CE': 'pfc_emissions_kt_co2_equiv',
    'EN.FSH.THRD.NO': 'fish_species_threatened',
    'EN.MAM.THRD.NO': 'mammal_species_threatened',
    'EN.BIR.THRD.NO': 'bird_species_threatened',
    'EN.HPT.THRD.NO': 'plant_species_threatened',
    'ER.FSH.PROD.MT': 'capture_fisheries_production_metric_tons',
    'ER.FSH.AQUA.MT': 'aquaculture_production_metric_tons',
    'ER.H2O.FWAG.ZS': 'freshwater_withdrawals_agriculture_pct',
    'ER.H2O.FWIN.ZS': 'freshwater_withdrawals_industry_pct',
    'ER.H2O.FWDM.ZS': 'freshwater_withdrawals_domestic_pct',

    # Trade
    'TG.VAL.TOTL.GD.ZS': 'merchandise_trade_pct_gdp',
    'TX.VAL.TECH.CD': 'high_tech_exports_current_usd',
    'TX.VAL.TECH.MF.ZS': 'high_tech_exports_pct_manufactured_exports',
    'TM.VAL.FUEL.ZS.UN': 'fuel_imports_pct_merchandise_imports',
    'TM.VAL.FOOD.ZS.UN': 'food_imports_pct_merchandise_imports',
    'TM.VAL.MANF.ZS.UN': 'manufactures_imports_pct_merchandise_imports',
    'TX.VAL.FUEL.ZS.UN': 'fuel_exports_pct_merchandise_exports',
    'TX.VAL.FOOD.ZS.UN': 'food_exports_pct_merchandise_exports',
    'TX.VAL.MANF.ZS.UN': 'manufactures_exports_pct_merchandise_exports',
    'TX.VAL.MRCH.CD.WT': 'merchandise_exports_current_usd',
    'TM.VAL.MRCH.CD.WT': 'merchandise_imports_current_usd',

    # Technology & Innovation
    'GB.XPD.RSDV.GD.ZS': 'research_and_development_expenditure_pct_gdp',
    'IP.JRN.ARTC.SC': 'scientific_technical_journal_articles',
    'IP.PAT.RESD': 'patent_applications_residents',
    'IP.PAT.NRES': 'patent_applications_nonresidents',
    'IT.MLT.MAIN': 'fixed_telephone_subscriptions_total',
    'IT.MLT.MAIN.P2': 'fixed_telephone_per_100',
    'IT.NET.BBND': 'fixed_broadband_subscriptions',
    'IT.NET.BBND.P2': 'fixed_broadband_per_100',
    'IT.NET.SECR': 'secure_internet_servers',
    'IT.NET.SECR.P6': 'secure_internet_servers_per_million',

    # Health (additional)
    'SH.IMM.IDPT': 'immunization_dpt_pct_children',
    'SH.IMM.MEAS': 'immunization_measles_pct_children',
    'SH.STA.BRTC.ZS': 'births_attended_by_skilled_health_staff_pct',
    'SH.STA.ACSN': 'access_to_sanitation_facilities_pct_population',
    'SH.H2O.SMDW.ZS': 'access_to_safe_drinking_water_pct_population',
    'SH.STA.MALR': 'malaria_incidence_per_1000_at_risk',
    'SH.DTH.COMM.ZS': 'communicable_disease_deaths_pct',
    'SH.DTH.INJR.ZS': 'injury_deaths_pct',
    'SH.DTH.NCOM.ZS': 'noncommunicable_disease_deaths_pct',

    # Poverty & Inequality
    'SI.POV.GINI': 'gini_index',
    'SI.POV.DDAY': 'poverty_headcount_190_per_day',
    'SI.POV.NAHC': 'poverty_headcount_national_poverty_lines',
    'SI.DST.FRST.20': 'income_share_lowest_20pct',
    'SI.DST.10TH.10': 'income_share_highest_10pct',
    'SI.DST.05TH.20': 'income_share_highest_20pct',

    # Government & Institutions
    'GC.REV.XGRT.GD.ZS': 'revenue_excluding_grants_pct_gdp',
    'GC.XPN.TOTL.GD.ZS': 'expense_pct_gdp',
    'GC.NLD.TOTL.GD.ZS': 'net_lending_borrowing_pct_gdp',
    'GC.BAL.CASH.GD.ZS': 'cash_surplus_deficit_pct_gdp',

    # Tourism
    'ST.INT.DPRT': 'international_tourism_departures',
    'ST.INT.RCPT.CD': 'international_tourism_receipts_current_usd',
    'ST.INT.RCPT.XP.ZS': 'tourism_receipts_pct_exports',
    'ST.INT.XPND.CD': 'international_tourism_expenditures_current_usd',
    'ST.INT.XPND.MP.ZS': 'tourism_expenditures_pct_imports',

    # Education (additional)
    'SE.ADT.1524.LT.ZS': 'literacy_rate_youth_15_24',
    'SE.ADT.1524.LT.FE.ZS': 'literacy_rate_youth_female',
    'SE.ADT.1524.LT.MA.ZS': 'literacy_rate_youth_male',
    'SE.ADT.LITR.FE.ZS': 'literacy_rate_adult_female',
    'SE.ADT.LITR.MA.ZS': 'literacy_rate_adult_male',
    'SE.ENR.PRSC.FM.ZS': 'school_enrollment_preprimary_gross',
    'SE.PRM.ENRR': 'school_enrollment_primary_gross',
    'SE.PRM.NENR': 'school_enrollment_primary_net',
    'SE.SEC.NENR': 'school_enrollment_secondary_net',
    'SE.TER.ENRR.FE': 'school_enrollment_tertiary_female_gross',
    'SE.XPD.PRIM.PC.ZS': 'govt_expenditure_per_student_primary_pct_gdp_pc',
    'SE.XPD.SECO.PC.ZS': 'govt_expenditure_per_student_secondary_pct_gdp_pc',
    'SE.XPD.TERT.PC.ZS': 'govt_expenditure_per_student_tertiary_pct_gdp_pc',
}

downloaded = 0
for code, name in additional_wdi.items():
    if name in df.columns:
        continue  # Skip if already exists

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
        downloaded += 1

        if downloaded % 10 == 0:
            print(f"  Downloaded {downloaded} additional indicators...")

    except Exception as e:
        pass  # Skip indicators that fail

print(f"  ✓ Downloaded {downloaded} additional WDI indicators")
print(f"  Current total: {df.shape[1]} features")

# ============================================================================
# STRATEGY 2: Create transformed/derived features from existing ones
# ============================================================================
print("\n[TRANSFORMATIONS] Creating transformed features...")

# Get numeric columns excluding the index and country name
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
# Exclude target
if 'gdp_per_capita_usd' in numeric_cols:
    numeric_cols.remove('gdp_per_capita_usd')

# Select a subset of features to transform (to avoid explosion)
np.random.seed(42)
cols_to_transform = np.random.choice(numeric_cols, size=min(30, len(numeric_cols)), replace=False)

transformations_added = 0

for col in cols_to_transform:
    if df.shape[1] >= TARGET_FEATURES:
        break

    # Log transform (for positive values)
    if (df[col] > 0).all() and (df[col] > 0).any():
        new_col = f"{col}_log"
        df[new_col] = np.log1p(df[col])
        add_to_codebook(new_col, f"Log transform of {col}", 'Computed transformation', 'noise')
        transformations_added += 1

    # Square
    if df.shape[1] < TARGET_FEATURES:
        new_col = f"{col}_squared"
        df[new_col] = df[col] ** 2
        add_to_codebook(new_col, f"Square of {col}", 'Computed transformation', 'noise')
        transformations_added += 1

    # Cube root (stable for negative values)
    if df.shape[1] < TARGET_FEATURES:
        new_col = f"{col}_cbrt"
        df[new_col] = np.sign(df[col]) * np.abs(df[col]) ** (1/3)
        add_to_codebook(new_col, f"Cube root of {col}", 'Computed transformation', 'noise')
        transformations_added += 1

print(f"  ✓ Created {transformations_added} transformed features")
print(f"  Current total: {df.shape[1]} features")

# ============================================================================
# STRATEGY 3: Create polynomial interaction terms
# ============================================================================
if df.shape[1] < TARGET_FEATURES:
    print("\n[INTERACTIONS] Creating polynomial interaction features...")

    # Select pairs of features to interact
    n_interactions_needed = min(50, TARGET_FEATURES - df.shape[1])
    n_pairs = min(n_interactions_needed, len(numeric_cols) * (len(numeric_cols) - 1) // 2)

    pairs = []
    numeric_subset = numeric_cols[:20]  # Use first 20 to avoid too many combinations
    for i in range(len(numeric_subset)):
        for j in range(i+1, len(numeric_subset)):
            pairs.append((numeric_subset[i], numeric_subset[j]))
            if len(pairs) >= n_pairs:
                break
        if len(pairs) >= n_pairs:
            break

    interactions_added = 0
    for col1, col2 in pairs:
        if df.shape[1] >= TARGET_FEATURES:
            break

        new_col = f"{col1}_x_{col2}"
        df[new_col] = df[col1] * df[col2]
        add_to_codebook(new_col, f"Interaction: {col1} × {col2}", 'Computed interaction', 'noise')
        interactions_added += 1

    print(f"  ✓ Created {interactions_added} interaction features")
    print(f"  Current total: {df.shape[1]} features")

# ============================================================================
# STRATEGY 4: Add pure synthetic noise (if still needed)
# ============================================================================
if df.shape[1] < 300:
    print("\n[SYNTHETIC] Adding pure synthetic noise features...")

    n_synthetic = 300 - df.shape[1]

    for i in range(n_synthetic):
        # Create random noise with different distributions
        if i % 3 == 0:
            # Gaussian noise
            df[f'synthetic_noise_gaussian_{i}'] = np.random.randn(len(df))
            add_to_codebook(f'synthetic_noise_gaussian_{i}',
                          f'Synthetic Gaussian noise feature {i}',
                          'Synthetic (random)', 'noise')
        elif i % 3 == 1:
            # Uniform noise
            df[f'synthetic_noise_uniform_{i}'] = np.random.rand(len(df))
            add_to_codebook(f'synthetic_noise_uniform_{i}',
                          f'Synthetic uniform noise feature {i}',
                          'Synthetic (random)', 'noise')
        else:
            # Exponential noise
            df[f'synthetic_noise_exponential_{i}'] = np.random.exponential(1, len(df))
            add_to_codebook(f'synthetic_noise_exponential_{i}',
                          f'Synthetic exponential noise feature {i}',
                          'Synthetic (random)', 'noise')

    print(f"  ✓ Added {n_synthetic} synthetic noise features")

print(f"\n  Final total: {df.shape[1]} features")

# ============================================================================
# FINAL CLEANING AND SAVE
# ============================================================================
print("\n[FINAL CLEANING] Handling any new missing values...")

# Drop columns with >30% missing
missing_by_col = df.isnull().sum() / len(df)
cols_to_keep = missing_by_col[missing_by_col <= 0.3].index
dropped_cols = set(df.columns) - set(cols_to_keep)
print(f"  Dropping {len(dropped_cols)} columns with >30% missing")
df = df[cols_to_keep]

# Update codebook
codebook = [c for c in codebook if c['column_name'] not in dropped_cols]

# Impute remaining missing
n_missing = df.isnull().sum().sum()
if n_missing > 0:
    print(f"  Imputing {n_missing} missing values with column medians...")
    df = df.fillna(df.median())

print(f"\nFinal dataset shape: {df.shape}")

# Save
df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_df = pd.DataFrame(codebook)
codebook_df.to_csv('codebook.csv', index=False)

print("\n" + "=" * 80)
print("FINAL DATASET SUMMARY")
print("=" * 80)

role_counts = codebook_df['role'].value_counts()
print(f"\nDimensions: {df.shape[0]} countries × {df.shape[1]} features")
print(f"\nFeature breakdown:")
for role, count in role_counts.items():
    print(f"  {role.capitalize()}: {count}")

print(f"\nMissing values: {df.isnull().sum().sum()}")

print("\n" + "=" * 80)
print("✓ EXPANDED DATASET COMPLETE!")
print("=" * 80)
print("\nFiles updated:")
print("  - gdp_spurious_regression_dataset.csv")
print("  - codebook.csv")
