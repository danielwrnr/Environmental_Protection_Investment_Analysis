CREATE TABLE Country (
    country_code VARCHAR(2) PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL
);

CREATE TABLE Environmental_Activity (
    ceparema_code VARCHAR(50) PRIMARY KEY,
    activity_name VARCHAR(255) NOT NULL
);

CREATE TABLE Macroeconomic_Indicator (
    country_code VARCHAR(2),
    year INT,
    population BIGINT,
    gdp_per_capita DECIMAL(15,2),
    PRIMARY KEY (country_code, year),
    FOREIGN KEY (country_code) REFERENCES Country(country_code)
);

CREATE TABLE Environmental_Investment (
    country_code VARCHAR(2),
    year INT,
    ceparema_code VARCHAR(50),
    inv_gov DECIMAL(15,2),
    inv_corp_spec DECIMAL(15,2),
    inv_corp_anc DECIMAL(15,2),
    inv_corp_total DECIMAL(15,2),
    inv_total DECIMAL(15,2),
    PRIMARY KEY (country_code, year, ceparema_code),
    FOREIGN KEY (country_code) REFERENCES Country(country_code),
    FOREIGN KEY (ceparema_code) REFERENCES Environmental_Activity(ceparema_code)
);
