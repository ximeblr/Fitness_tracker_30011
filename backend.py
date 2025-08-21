# backend.py
# This file contains all the database interaction logic.
# It uses psycopg2 to connect to a PostgreSQL database.

import psycopg2
from datetime import datetime

# --- DATABASE CONFIGURATION ---
# IMPORTANT: Replace these with your actual PostgreSQL credentials.
DBNAME = "aadhar system"
USER = "postgres"
PASSWORD = "tiwari"
HOST = "localhost"

def create_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

def setup_database():
    """
    Creates the necessary tables if they do not exist.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            # Create citizens table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS citizens (
                    aadhaar_id VARCHAR(12) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    dob DATE,
                    gender VARCHAR(10),
                    address TEXT,
                    biometric_hash TEXT UNIQUE NOT NULL,
                    enrollment_date TIMESTAMP
                );
            """)
            # Create authentication log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS auth_log (
                    log_id SERIAL PRIMARY KEY,
                    aadhaar_id VARCHAR(12) REFERENCES citizens(aadhaar_id),
                    attempt_date TIMESTAMP,
                    status VARCHAR(10) -- 'success' or 'failed'
                );
            """)
            # Create de-duplication log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS deduplication_conflicts (
                    conflict_id SERIAL PRIMARY KEY,
                    biometric_hash TEXT,
                    attempt_date TIMESTAMP
                );
            """)
        conn.commit()
        conn.close()

# --- CRUD Operations ---

def create_citizen(aadhaar_id, name, dob, gender, address, biometric_hash):
    """
    Creates a new citizen record (Enrollment).
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO citizens (aadhaar_id, name, dob, gender, address, biometric_hash, enrollment_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (aadhaar_id, name, dob, gender, address, biometric_hash, datetime.now()))
                conn.commit()
                conn.close()
                return True, "Enrollment successful!"
            except psycopg2.Error as e:
                conn.close()
                return False, f"Database error: {e}"
    return False, "Failed to connect to database."

def read_citizen(aadhaar_id):
    """
    Reads a citizen's record from the database.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM citizens WHERE aadhaar_id = %s", (aadhaar_id,))
            record = cur.fetchone()
        conn.close()
        return record
    return None

def read_all_citizens():
    """
    Reads all citizen records from the database.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM citizens")
            records = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        conn.close()
        return records, columns
    return [], []

def update_citizen(aadhaar_id, name, dob, gender, address):
    """
    Updates a citizen's demographic details.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE citizens
                SET name = %s, dob = %s, gender = %s, address = %s
                WHERE aadhaar_id = %s
            """, (name, dob, gender, address, aadhaar_id))
            conn.commit()
        conn.close()
        return True, "Citizen record updated successfully!"
    return False, "Failed to connect to database."

def delete_citizen(aadhaar_id):
    """
    Deletes a citizen's record from the database.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            try:
                # First delete from auth_log to avoid foreign key constraint issues
                cur.execute("DELETE FROM auth_log WHERE aadhaar_id = %s", (aadhaar_id,))
                cur.execute("DELETE FROM citizens WHERE aadhaar_id = %s", (aadhaar_id,))
                conn.commit()
                conn.close()
                return True, "Citizen record deleted successfully."
            except psycopg2.Error as e:
                conn.close()
                return False, f"Error deleting record: {e}"
    return False, "Failed to connect to database."

# --- Authentication and De-duplication Logic ---

def check_deduplication(biometric_hash):
    """
    Performs a de-duplication check based on biometric hash.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT aadhaar_id FROM citizens WHERE biometric_hash = %s", (biometric_hash,))
            result = cur.fetchone()
            if result:
                # Log the conflict
                cur.execute("INSERT INTO deduplication_conflicts (biometric_hash, attempt_date) VALUES (%s, %s)",
                            (biometric_hash, datetime.now()))
                conn.commit()
            conn.close()
            return result is not None
    return False

def authenticate(aadhaar_id, biometric_hash):
    """
    Processes an authentication request and logs the result.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT biometric_hash FROM citizens WHERE aadhaar_id = %s", (aadhaar_id,))
            result = cur.fetchone()
            
            status = 'failed'
            if result and result[0] == biometric_hash:
                status = 'success'
            
            # Record the authentication attempt
            cur.execute("INSERT INTO auth_log (aadhaar_id, attempt_date, status) VALUES (%s, %s, %s)",
                        (aadhaar_id, datetime.now(), status))
            conn.commit()
            conn.close()
            return status == 'success'
    return False

# --- Reporting and Analytics ---

def get_business_insights():
    """
    Retrieves key business insights using SQL aggregation functions.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cur:
            # Total enrolled citizens
            cur.execute("SELECT COUNT(*) FROM citizens;")
            total_enrolled = cur.fetchone()[0]

            # Authentication attempts
            cur.execute("SELECT COUNT(*), COUNT(CASE WHEN status = 'success' THEN 1 END) FROM auth_log;")
            total_auth_attempts, successful_auths = cur.fetchone()
            failed_auths = total_auth_attempts - successful_auths

            # De-duplication conflicts
            cur.execute("SELECT COUNT(*) FROM deduplication_conflicts;")
            dedup_conflicts = cur.fetchone()[0]

            # Average age of citizens (conceptual)
            cur.execute("SELECT AVG(EXTRACT(YEAR FROM AGE(NOW(), dob))) FROM citizens;")
            avg_age = cur.fetchone()[0]

            # Most recent enrollment date
            cur.execute("SELECT MAX(enrollment_date) FROM citizens;")
            last_enrollment = cur.fetchone()[0]

            # Oldest enrollment date
            cur.execute("SELECT MIN(enrollment_date) FROM citizens;")
            first_enrollment = cur.fetchone()[0]

        conn.close()
        return {
            "total_enrolled": total_enrolled,
            "total_auth_attempts": total_auth_attempts,
            "successful_auths": successful_auths,
            "failed_auths": failed_auths,
            "dedup_conflicts": dedup_conflicts,
            "avg_age": f"{avg_age:.2f}" if avg_age else "N/A",
            "last_enrollment": last_enrollment,
            "first_enrollment": first_enrollment
        }
    return {}
