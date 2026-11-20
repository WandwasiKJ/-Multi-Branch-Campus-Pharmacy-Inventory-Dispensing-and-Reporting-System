PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS medicines (
    medicine_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    unit_price REAL NOT NULL,
    reorder_level INTEGER NOT NULL,
    medicine_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    branch_code TEXT PRIMARY KEY,
    branch_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stock (
    medicine_code TEXT NOT NULL,
    branch_code TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (medicine_code, branch_code),
    FOREIGN KEY (medicine_code) REFERENCES medicines(medicine_code),
    FOREIGN KEY (branch_code) REFERENCES branches(branch_code)
);

CREATE TABLE IF NOT EXISTS authorised_prescribers (
    prescriber_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);