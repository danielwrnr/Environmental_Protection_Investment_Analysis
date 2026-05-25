-- ==========================================
-- DATABASE METADATA (Data Management Plan)
-- ==========================================
-- Database Name: EU_Environmental_Investment_Analysis
-- Title: Do Rich Countries Invest More in Saving the Planet? Analysis of Europe’s Green Investment Landscape
-- Description: Environmental protection investments across EU countries (2014-2022) based on the reuse of existing data from the Eurostat Open Data Portal.
-- Publisher: Eurostat
-- Creator: Eurostat
-- License: CC BY 4.0 (Eurostat reuse policy)
-- Rights: European Union / Eurostat
-- Republisher: Luka Premuš / TU Wien
-- Republisher Email: e12552143@student.tuwien.ac.at
-- Republisher Affiliation: TU Wien (Course 194.045 Data Stewardship)
-- DMP Version: 1.0
-- DMP Date: 2026-05-25
-- Metadata Standard: DataCite Metadata Schema
-- Controlled Vocabularies: ISO 3166, CEPA
-- ==========================================

CREATE TABLE Country (
    country_code VARCHAR(2) PRIMARY KEY COMMENT '2-letter ISO country code',
    country_name VARCHAR(255) NOT NULL COMMENT 'Full name of the country'
) COMMENT='Country dimension table with ISO codes';

CREATE TABLE Environmental_Activity (
    ceparema_code VARCHAR(50) PRIMARY KEY COMMENT 'CEPA/CReMA activity code',
    activity_name VARCHAR(255) NOT NULL COMMENT 'Name of the environmental protection activity'
) COMMENT='Environmental activity dimension table (CEPA/CReMA classifications)';

CREATE TABLE Macroeconomic_Indicator (
    country_code VARCHAR(2) COMMENT '2-letter ISO country code',
    year INT COMMENT 'Observation year',
    population BIGINT COMMENT 'Total population',
    gdp_per_capita DECIMAL(15,2) COMMENT 'Gross Domestic Product per capita',
    PRIMARY KEY (country_code, year),
    FOREIGN KEY (country_code) REFERENCES Country(country_code)
) COMMENT='Macroeconomic indicators for EU countries';

CREATE TABLE Environmental_Investment (
    country_code VARCHAR(2) COMMENT '2-letter ISO country code',
    year INT COMMENT 'Observation year',
    ceparema_code VARCHAR(50) COMMENT 'CEPA/CReMA activity code',
    inv_gov DECIMAL(15,2) COMMENT 'Investment by general government',
    inv_corp_spec DECIMAL(15,2) COMMENT 'Investment by specialist producers',
    inv_corp_anc DECIMAL(15,2) COMMENT 'Investment by ancillary producers',
    inv_corp_total DECIMAL(15,2) COMMENT 'Total corporate investment',
    inv_total DECIMAL(15,2) COMMENT 'Total environmental investment',
    PRIMARY KEY (country_code, year, ceparema_code),
    FOREIGN KEY (country_code) REFERENCES Country(country_code),
    FOREIGN KEY (ceparema_code) REFERENCES Environmental_Activity(ceparema_code)
) COMMENT='Environmental protection investments across EU countries';
