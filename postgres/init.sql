-- Create organizations table
CREATE TABLE organizations (
    org_id SERIAL PRIMARY KEY,
    admin_telegram_user_id VARCHAR(100) NOT NULL UNIQUE,
    organization_code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    description TEXT
);

-- Create admins table
CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    telegram_user_id VARCHAR(100) NOT NULL UNIQUE,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- Create volunteers table
CREATE TABLE volunteers (
    volunteer_id SERIAL PRIMARY KEY,
    telegram_user_id VARCHAR(100) NOT NULL UNIQUE,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    availability JSON,
    capabilities JSON
);

-- Create recipients table
CREATE TABLE recipients (
    recipient_id SERIAL PRIMARY KEY,
    telegram_user_id VARCHAR(100) NOT NULL UNIQUE,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    help_needed TEXT NOT NULL,
    availability JSON
);

-- Create assignments table
CREATE TABLE assignments (
    assignment_id SERIAL PRIMARY KEY,
    recipient_id INTEGER NOT NULL REFERENCES recipients(recipient_id),
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id),
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(20) NOT NULL
);

