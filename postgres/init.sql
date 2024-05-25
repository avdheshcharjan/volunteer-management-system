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
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL
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
    date DATE NOT NULL,
    time TIME NOT NULL
);

-- Create assignments table
CREATE TABLE assignments (
    assignment_id SERIAL PRIMARY KEY,
    recipient_id INTEGER NOT NULL REFERENCES recipients(recipient_id),
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id),
    status VARCHAR(20) NOT NULL
);

-- Optional: Insert sample data
INSERT INTO organizations (admin_telegram_user_id, organization_code, name, contact_person, email, phone_number, description)
VALUES ('admin_telegram_id', 'org123', 'Helping Hands', 'Jane Doe', 'jane.doe@example.com', '1234567890', 'A non-profit organization focused on community service');

INSERT INTO admins (org_id, name, email, password)
VALUES (1, 'Admin User', 'admin@example.com', 'hashedpassword');
