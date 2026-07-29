# Test data for Registration, Auth, Profiles, and Emergency Contacts

# Registration Payloads
RESIDENT_REGISTRATION_DATA = {
    "username": "resident1",
    "email": "resident1@example.com",
    "password": "Password123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "RESIDENT",
    "phone_number": "1234567890",
    "age": 30,
    "blood_group": "O+",
    "medical_conditions": "None",
    "is_senior_citizen": False
}

RESIDENT_WITH_FLAT_REGISTRATION_DATA = {
    "username": "resident_flat",
    "email": "resident_flat@example.com",
    "password": "Password123!",
    "first_name": "Flat",
    "last_name": "Owner",
    "role": "RESIDENT",
    "phone_number": "9998881111",
    "age": 32
}

GUARDIAN_REGISTRATION_DATA = {
    "username": "guardian1",
    "email": "guardian1@example.com",
    "password": "Password123!",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "GUARDIAN",
    "phone_number": "0987654321",
    "age": 45,
    "occupation": "Doctor",
    "relation_notes": "Neighbor"
}

VOLUNTEER_REGISTRATION_DATA = {
    "username": "volunteer1",
    "email": "volunteer1@example.com",
    "password": "Password123!",
    "first_name": "Jack",
    "last_name": "Smith",
    "role": "VOLUNTEER",
    "phone_number": "1112223333",
    "age": 25,
    "skills": "First Aid",
    "id_proof_type": "Aadhaar",
    "id_proof_number": "123456789012"
}

SECURITY_REGISTRATION_DATA = {
    "username": "security1",
    "email": "security1@example.com",
    "password": "Password123!",
    "first_name": "Officer",
    "last_name": "Bob",
    "role": "SECURITY",
    "phone_number": "4445556666",
    "age": 40,
    "badge_number": "SEC-001",
    "assigned_gate": "Gate 1",
    "shift_timing": "Day"
}

# User Setup Data (Used in SetUp methods)
TEST_USER_CREDENTIALS = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "Password123!",
    "phone_number": "1234567890",
    "age": 30,
    "address": "123 Street"
}

RESIDENT_USER_DATA = {
    "username": "resident1",
    "email": "resident1@example.com",
    "password": "Password123!",
    "phone_number": "1234567890",
    "age": 30,
    "role": "RESIDENT",
    "address": "123 Street"
}

GUARDIAN_USER_DATA = {
    "username": "guardian1",
    "email": "guardian1@example.com",
    "password": "Password123!",
    "phone_number": "0987654321",
    "age": 40,
    "role": "GUARDIAN",
    "first_name": "Guardian",
    "last_name": "One"
}

OTHER_USER_DATA = {
    "username": "other1",
    "email": "other1@example.com",
    "password": "Password123!",
    "phone_number": "5555555555",
    "age": 25,
    "role": "RESIDENT"
}

ADMIN_USER_DATA = {
    "username": "admin1",
    "email": "admin1@example.com",
    "password": "Password123!",
    "phone_number": "9999999999",
    "age": 35
}

# Emergency Contact Data
EMERGENCY_CONTACT_POST_DATA = {
    "name": "Jane Doe",
    "phone_number": "1112223333",
    "relationship": "Sister",
    "priority": "PRIMARY"
}
