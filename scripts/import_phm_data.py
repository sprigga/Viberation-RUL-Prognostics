#!/usr/bin/env python3
"""
Import PHM IEEE 2012 Learning_set data into SQLite database.

Data structure:
- 6 bearing directories (Bearing1_1, Bearing1_2, Bearing2_1, Bearing2_2, Bearing3_1, Bearing3_2)
- Each bearing has multiple CSV files (acc_*.csv)
- Each CSV file contains vibration measurements with format:
  hour, minute, second, microsecond, horizontal_acceleration, vertical_acceleration
"""

import os
import sqlite3
import csv
from pathlib import Path
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PHMDataImporter:
    def __init__(self, db_path: str, data_dir: str):
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.conn = None

    def create_database_schema(self):
        """Create database tables for PHM data."""
        logger.info("Creating database schema...")

        cursor = self.conn.cursor()

        # Bearings table: stores metadata about each bearing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bearings (
                bearing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bearing_name TEXT UNIQUE NOT NULL,
                condition_id INTEGER,
                description TEXT
            )
        """)

        # Files table: stores information about each CSV file
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurement_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bearing_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_number INTEGER,
                record_count INTEGER,
                FOREIGN KEY (bearing_id) REFERENCES bearings(bearing_id),
                UNIQUE(bearing_id, file_name)
            )
        """)

        # Measurements table: stores actual vibration data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,
                second INTEGER NOT NULL,
                microsecond INTEGER NOT NULL,
                horizontal_acceleration REAL NOT NULL,
                vertical_acceleration REAL NOT NULL,
                FOREIGN KEY (file_id) REFERENCES measurement_files(file_id)
            )
        """)

        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_file_id
            ON measurements(file_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_time
            ON measurements(hour, minute, second, microsecond)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_bearing_id
            ON measurement_files(bearing_id)
        """)

        self.conn.commit()
        logger.info("Database schema created successfully")

    def insert_bearing(self, bearing_name: str, condition_id: int = None, description: str = None) -> int:
        """Insert a bearing record and return its ID."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO bearings (bearing_name, condition_id, description)
                VALUES (?, ?, ?)
            """, (bearing_name, condition_id, description))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Bearing already exists, fetch its ID
            cursor.execute("SELECT bearing_id FROM bearings WHERE bearing_name = ?", (bearing_name,))
            return cursor.fetchone()[0]

    def insert_file(self, bearing_id: int, file_name: str, file_number: int, record_count: int) -> int:
        """Insert a measurement file record and return its ID."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO measurement_files (bearing_id, file_name, file_number, record_count)
                VALUES (?, ?, ?, ?)
            """, (bearing_id, file_name, file_number, record_count))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # File already exists, fetch its ID
            cursor.execute("""
                SELECT file_id FROM measurement_files
                WHERE bearing_id = ? AND file_name = ?
            """, (bearing_id, file_name))
            return cursor.fetchone()[0]

    def insert_measurements_batch(self, file_id: int, measurements: List[Tuple]):
        """Insert a batch of measurements."""
        cursor = self.conn.cursor()
        cursor.executemany("""
            INSERT INTO measurements
            (file_id, hour, minute, second, microsecond, horizontal_acceleration, vertical_acceleration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, measurements)
        self.conn.commit()

    def import_csv_file(self, bearing_id: int, csv_path: Path) -> int:
        """Import a single CSV file."""
        file_name = csv_path.name
        file_number = int(file_name.replace('acc_', '').replace('.csv', ''))

        # Read and prepare measurements
        measurements = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 6:
                    hour, minute, second, microsecond, h_acc, v_acc = row
                    # Convert microsecond to int (handles both regular and scientific notation)
                    microsecond_int = int(float(microsecond))
                    measurements.append((
                        file_id := 0,  # Will be set after file insertion
                        int(hour), int(minute), int(second), microsecond_int,
                        float(h_acc), float(v_acc)
                    ))

        record_count = len(measurements)

        # Insert file record
        file_id = self.insert_file(bearing_id, file_name, file_number, record_count)

        # Update file_id in measurements
        measurements = [
            (file_id, hour, minute, second, microsecond, h_acc, v_acc)
            for (_, hour, minute, second, microsecond, h_acc, v_acc) in measurements
        ]

        # Insert measurements in batches
        batch_size = 1000
        for i in range(0, len(measurements), batch_size):
            batch = measurements[i:i + batch_size]
            self.insert_measurements_batch(file_id, batch)

        return record_count

    def import_bearing_directory(self, bearing_dir: Path):
        """Import all CSV files from a bearing directory."""
        bearing_name = bearing_dir.name
        logger.info(f"Importing bearing: {bearing_name}")

        # Insert bearing record
        bearing_id = self.insert_bearing(bearing_name)

        # Get all CSV files
        csv_files = sorted(bearing_dir.glob('acc_*.csv'))
        total_files = len(csv_files)

        logger.info(f"Found {total_files} CSV files for {bearing_name}")

        total_records = 0
        for idx, csv_file in enumerate(csv_files, 1):
            try:
                record_count = self.import_csv_file(bearing_id, csv_file)
                total_records += record_count

                if idx % 100 == 0 or idx == total_files:
                    logger.info(f"  Progress: {idx}/{total_files} files processed ({total_records} records)")
            except Exception as e:
                logger.error(f"  Error processing {csv_file.name}: {e}")

        logger.info(f"Completed {bearing_name}: {total_records} total records imported")

    def import_all_data(self):
        """Import all data from Learning_set directory."""
        logger.info("Starting PHM data import...")

        # Connect to database
        self.conn = sqlite3.connect(self.db_path)

        try:
            # Create schema
            self.create_database_schema()

            # Get all bearing directories
            bearing_dirs = sorted([d for d in self.data_dir.iterdir() if d.is_dir() and d.name.startswith('Bearing')])

            logger.info(f"Found {len(bearing_dirs)} bearing directories")

            # Import each bearing
            for bearing_dir in bearing_dirs:
                self.import_bearing_directory(bearing_dir)

            # Print summary statistics
            self.print_summary()

            logger.info("Data import completed successfully!")

        except Exception as e:
            logger.error(f"Error during import: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

    def print_summary(self):
        """Print summary statistics of imported data."""
        cursor = self.conn.cursor()

        logger.info("\n" + "="*60)
        logger.info("DATABASE SUMMARY")
        logger.info("="*60)

        # Bearing count
        cursor.execute("SELECT COUNT(*) FROM bearings")
        bearing_count = cursor.fetchone()[0]
        logger.info(f"Total bearings: {bearing_count}")

        # File count
        cursor.execute("SELECT COUNT(*) FROM measurement_files")
        file_count = cursor.fetchone()[0]
        logger.info(f"Total files: {file_count}")

        # Measurement count
        cursor.execute("SELECT COUNT(*) FROM measurements")
        measurement_count = cursor.fetchone()[0]
        logger.info(f"Total measurements: {measurement_count:,}")

        # Per-bearing statistics
        logger.info("\nPer-bearing statistics:")
        cursor.execute("""
            SELECT
                b.bearing_name,
                COUNT(DISTINCT mf.file_id) as file_count,
                COUNT(m.measurement_id) as measurement_count
            FROM bearings b
            LEFT JOIN measurement_files mf ON b.bearing_id = mf.bearing_id
            LEFT JOIN measurements m ON mf.file_id = m.file_id
            GROUP BY b.bearing_id, b.bearing_name
            ORDER BY b.bearing_name
        """)

        for bearing_name, file_count, measurement_count in cursor.fetchall():
            logger.info(f"  {bearing_name}: {file_count} files, {measurement_count:,} measurements")

        logger.info("="*60 + "\n")


def main():
    """Main entry point."""
    # Configuration
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "phm-ieee-2012-data-challenge-dataset" / "Learning_set"
    db_path = project_root / "backend" / "phm_data.db"

    # Verify data directory exists
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return

    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Database path: {db_path}")

    # Create importer and run
    importer = PHMDataImporter(str(db_path), str(data_dir))
    importer.import_all_data()


if __name__ == "__main__":
    main()
