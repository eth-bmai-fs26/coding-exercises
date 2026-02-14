#!/usr/bin/env python3
"""Add more World Bank WDI indicators as noise features."""

import pandas as pd
import numpy as np
import wbgapi as wb
import pycountry

print("=" * 80)
print("ADDING MORE WORLD BANK INDICATORS")
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
    'Cote d\'Ivoire': 'CIV', 'Gambia, The': 'GMB', 'Bahamas, The': 'BHS',
    'Micronesia, Fed. Sts.': 'FSM', 'St. Lucia': 'LCA', 'St. Vincent and the Grenadines': 'VCT',
    'St. Kitts and Nevis': 'KNA', 'Yemen, Rep.': 'YEM', 'Syria': 'SYR',
    'North Macedonia': 'MKD', 'Eswatini': 'SWZ', 'Brunei Darussalam': 'BRN',
    'West Bank and Gaza': 'PSE', 'Timor-Leste': 'TLS',
}
name_to_iso3.update(wb_mappings)
iso3_to_name = {v: k for k, v in name_to_iso3.items() if k in df.index}

# New WDI indicators to download
new_indicators = {
    # Transport & Infrastructure
    'IS.VEH.NVEH.P3': ('motor_vehicles_per_1000', 'Motor vehicles per 1,000 people'),
    'IS.RRS.TOTL.KM': ('rail_lines_total_km', 'Total railway line length in km'),
    'IS.AIR.GOOD.MT.K1': ('air_freight_million_ton_km', 'Air freight in million ton-km'),
    'IS.SHP.GOOD.TU': ('container_port_traffic', 'Container port traffic (TEU)'),
    # Environment
    'EN.ATM.CO2E.PC': ('co2_emissions_per_capita', 'CO2 emissions metric tons per capita'),
    'EN.ATM.METH.KT.CE': ('methane_emissions_kt', 'Methane emissions in kt CO2 equivalent'),
    'EN.ATM.NOXE.KT.CE': ('nitrous_oxide_emissions_kt', 'Nitrous oxide emissions in kt CO2 equivalent'),
    'AG.LND.FRST.K2': ('forest_area_sq_km', 'Forest area in sq km'),
    'ER.MRN.PTMR.ZS': ('marine_protected_areas_pct', 'Marine protected areas as % of territorial waters'),
    'ER.LND.PTLD.ZS': ('terrestrial_protected_areas_pct', 'Terrestrial protected areas as % of total land'),
    # Finance & Economy
    'FB.ATM.TOTL.P5': ('atms_per_100k_adults', 'ATMs per 100,000 adults'),
    'FB.CBK.BRCH.P5': ('bank_branches_per_100k', 'Commercial bank branches per 100,000 adults'),
    'CM.MKT.LCAP.GD.ZS': ('stock_market_cap_pct_gdp', 'Market capitalization of listed companies % GDP'),
    'CM.MKT.LDOM.NO': ('listed_domestic_companies', 'Number of listed domestic companies'),
    'BX.TRF.PWKR.CD.DT': ('remittances_received_usd', 'Personal remittances received in USD'),
    'BX.KLT.DINV.WD.GD.ZS': ('fdi_net_inflows_pct_gdp', 'Foreign direct investment net inflows % GDP'),
    'GC.TAX.TOTL.GD.ZS': ('tax_revenue_pct_gdp', 'Tax revenue as % of GDP'),
    'GC.DOD.TOTL.GD.ZS': ('govt_debt_pct_gdp', 'Central government debt as % of GDP'),
    # Technology & Innovation
    'IT.NET.USER.ZS': ('internet_users_pct', 'Individuals using the Internet %'),
    'IT.CEL.SETS.P2': ('mobile_subscriptions_per_100', 'Mobile cellular subscriptions per 100 people'),
    'IP.PAT.RESD': ('patent_applications_residents', 'Patent applications by residents'),
    'IP.PAT.NRES': ('patent_applications_nonresidents', 'Patent applications by non-residents'),
    'IP.TMK.TOTL': ('trademark_applications_total', 'Trademark applications total'),
    'GB.XPD.RSDV.GD.ZS': ('research_development_pct_gdp', 'Research and development expenditure % GDP'),
    # Demographics & Health
    'SP.DYN.LE00.MA.IN': ('life_expectancy_male', 'Life expectancy at birth male'),
    'SP.DYN.LE00.FE.IN': ('life_expectancy_female', 'Life expectancy at birth female'),
    'SP.POP.DPND': ('dependency_ratio_total', 'Age dependency ratio total'),
    'SH.STA.OWAD.ZS': ('overweight_adults_pct', 'Prevalence of overweight adults %'),
    'SH.STA.SUIC.P5': ('suicide_rate_per_100k', 'Suicide mortality rate per 100,000'),
    'SH.ALC.PCAP.LI': ('alcohol_consumption_liters_pc', 'Total alcohol consumption per capita liters'),
    'SH.PRV.SMOK.MA': ('smoking_prevalence_male', 'Smoking prevalence males %'),
    'SH.PRV.SMOK.FE': ('smoking_prevalence_female', 'Smoking prevalence females %'),
    'SP.URB.TOTL.IN.ZS': ('urban_population_pct', 'Urban population %'),
    'SP.POP.TOTL': ('population_total', 'Total population'),
    # Education
    'SE.XPD.TOTL.GD.ZS': ('education_expenditure_total_pct_gdp', 'Government expenditure on education % GDP'),
    'SE.TER.ENRR': ('tertiary_enrollment_gross', 'Gross enrollment ratio tertiary education'),
    'SE.SEC.ENRR': ('secondary_enrollment_gross', 'Gross enrollment ratio secondary education'),
    'SE.ADT.LITR.ZS': ('literacy_rate_adult', 'Literacy rate adult %'),
    # Tourism
    'ST.INT.ARVL': ('international_tourist_arrivals', 'International tourism number of arrivals'),
    'ST.INT.RCPT.CD': ('tourism_receipts_usd', 'International tourism receipts in USD'),
    'ST.INT.DPRT': ('international_tourist_departures', 'International tourism number of departures'),
    'ST.INT.XPND.CD': ('tourism_expenditure_usd', 'International tourism expenditures in USD'),
}

def add_to_codebook(column_name, description, source, role='noise'):
    global codebook_df
    if column_name not in codebook_df['column_name'].values:
        new_row = pd.DataFrame({
            'column_name': [column_name],
            'description': [description],
            'source': [source],
            'role': [role]
        })
        codebook_df = pd.concat([codebook_df, new_row], ignore_index=True)

added = 0
failed = 0

for indicator_code, (col_name, description) in new_indicators.items():
    if col_name in df.columns:
        print(f"  SKIP {col_name} (already exists)")
        continue
    try:
        data = wb.data.DataFrame(indicator_code, time=2020, labels=False)
        if data.empty:
            data = wb.data.DataFrame(indicator_code, time=2019, labels=False)
        if data.empty:
            data = wb.data.DataFrame(indicator_code, time=2018, labels=False)

        if data.empty:
            print(f"  FAIL {col_name} - no data")
            failed += 1
            continue

        col = data.columns[0]
        df[col_name] = 0.0
        count = 0
        for iso3, value in data[col].items():
            if iso3 in iso3_to_name and pd.notna(value):
                df.loc[iso3_to_name[iso3], col_name] = value
                count += 1

        add_to_codebook(col_name, description, f'World Bank WDI ({indicator_code})')
        added += 1
        print(f"  OK   {col_name}: {count} countries")

    except Exception as e:
        print(f"  FAIL {col_name}: {str(e)[:60]}")
        failed += 1

# Fill NaN with 0
df = df.fillna(0)

print(f"\nAdded {added} indicators, {failed} failed")
print(f"Dataset: {df.shape[0]} countries × {df.shape[1]} features")

df.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_df.to_csv('codebook.csv', index=False)
print("Saved!")
