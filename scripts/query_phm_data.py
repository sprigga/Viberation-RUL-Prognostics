#!/usr/bin/env python3
"""
Query tool for PHM IEEE 2012 data stored in SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


class PHMDataQuery:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_bearings(self) -> List[Dict[str, Any]]:
        """Get all bearings."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bearings ORDER BY bearing_name")
        return [dict(row) for row in cursor.fetchall()]

    def get_bearing_stats(self, bearing_name: str) -> Dict[str, Any]:
        """Get statistics for a specific bearing."""
        cursor = self.conn.cursor()

        # Get bearing info
        cursor.execute("""
            SELECT * FROM bearings WHERE bearing_name = ?
        """, (bearing_name,))
        bearing = dict(cursor.fetchone())

        # Get file count
        cursor.execute("""
            SELECT COUNT(*) as file_count
            FROM measurement_files
            WHERE bearing_id = ?
        """, (bearing['bearing_id'],))
        bearing['file_count'] = cursor.fetchone()[0]

        # Get measurement count
        cursor.execute("""
            SELECT COUNT(*) as measurement_count
            FROM measurements m
            JOIN measurement_files mf ON m.file_id = mf.file_id
            WHERE mf.bearing_id = ?
        """, (bearing['bearing_id'],))
        bearing['measurement_count'] = cursor.fetchone()[0]

        return bearing

    def get_measurements(
        self,
        bearing_name: str,
        file_number: int = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """Get measurements for a bearing."""
        cursor = self.conn.cursor()

        if file_number:
            query = """
                SELECT
                    m.hour, m.minute, m.second, m.microsecond,
                    m.horizontal_acceleration, m.vertical_acceleration,
                    mf.file_name, mf.file_number
                FROM measurements m
                JOIN measurement_files mf ON m.file_id = mf.file_id
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ? AND mf.file_number = ?
                ORDER BY m.measurement_id
                LIMIT ?
            """
            cursor.execute(query, (bearing_name, file_number, limit))
        else:
            query = """
                SELECT
                    m.hour, m.minute, m.second, m.microsecond,
                    m.horizontal_acceleration, m.vertical_acceleration,
                    mf.file_name, mf.file_number
                FROM measurements m
                JOIN measurement_files mf ON m.file_id = mf.file_id
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ?
                ORDER BY mf.file_number, m.measurement_id
                LIMIT ?
            """
            cursor.execute(query, (bearing_name, limit))

        rows = cursor.fetchall()
        return pd.DataFrame([dict(row) for row in rows])

    def get_file_summary(self, bearing_name: str) -> pd.DataFrame:
        """Get summary of all files for a bearing."""
        cursor = self.conn.cursor()

        query = """
            SELECT
                mf.file_number,
                mf.file_name,
                mf.record_count,
                MIN(m.hour) as start_hour,
                MIN(m.minute) as start_minute,
                MAX(m.hour) as end_hour,
                MAX(m.minute) as end_minute,
                AVG(m.horizontal_acceleration) as avg_h_acc,
                AVG(m.vertical_acceleration) as avg_v_acc,
                MAX(ABS(m.horizontal_acceleration)) as max_h_acc,
                MAX(ABS(m.vertical_acceleration)) as max_v_acc
            FROM measurement_files mf
            JOIN measurements m ON mf.file_id = m.file_id
            JOIN bearings b ON mf.bearing_id = b.bearing_id
            WHERE b.bearing_name = ?
            GROUP BY mf.file_id, mf.file_number, mf.file_name, mf.record_count
            ORDER BY mf.file_number
        """
        cursor.execute(query, (bearing_name,))

        rows = cursor.fetchall()
        return pd.DataFrame([dict(row) for row in rows])

    def get_acceleration_stats(
        self,
        bearing_name: str
    ) -> Dict[str, Any]:
        """Get acceleration statistics for a bearing."""
        cursor = self.conn.cursor()

        query = """
            SELECT
                COUNT(*) as total_measurements,
                AVG(m.horizontal_acceleration) as avg_h_acc,
                AVG(m.vertical_acceleration) as avg_v_acc,
                MIN(m.horizontal_acceleration) as min_h_acc,
                MIN(m.vertical_acceleration) as min_v_acc,
                MAX(m.horizontal_acceleration) as max_h_acc,
                MAX(m.vertical_acceleration) as max_v_acc
            FROM measurements m
            JOIN measurement_files mf ON m.file_id = mf.file_id
            JOIN bearings b ON mf.bearing_id = b.bearing_id
            WHERE b.bearing_name = ?
        """
        cursor.execute(query, (bearing_name,))

        row = cursor.fetchone()
        return dict(row) if row else {}


def main():
    """Example usage."""
    project_root = Path(__file__).parent.parent
    db_path = project_root / "backend" / "phm_data.db"

    with PHMDataQuery(str(db_path)) as query:
        # List all bearings
        print("All Bearings:")
        print("=" * 60)
        bearings = query.get_bearings()
        for bearing in bearings:
            print(f"  {bearing['bearing_name']} (ID: {bearing['bearing_id']})")

        # Get stats for Bearing1_1
        print("\nBearing1_1 Statistics:")
        print("=" * 60)
        stats = query.get_bearing_stats('Bearing1_1')
        print(f"  Files: {stats['file_count']}")
        print(f"  Measurements: {stats['measurement_count']:,}")

        # Get acceleration stats
        acc_stats = query.get_acceleration_stats('Bearing1_1')
        print(f"\nAcceleration Statistics:")
        print(f"  Horizontal - Min: {acc_stats['min_h_acc']:.3f}, "
              f"Max: {acc_stats['max_h_acc']:.3f}, "
              f"Avg: {acc_stats['avg_h_acc']:.3f}")
        print(f"  Vertical   - Min: {acc_stats['min_v_acc']:.3f}, "
              f"Max: {acc_stats['max_v_acc']:.3f}, "
              f"Avg: {acc_stats['avg_v_acc']:.3f}")

        # Get sample measurements
        print("\nSample Measurements (first 10):")
        print("=" * 60)
        df = query.get_measurements('Bearing1_1', file_number=1, limit=10)
        print(df.to_string(index=False))

        # Get file summary
        print("\nFile Summary (first 10 files):")
        print("=" * 60)
        file_summary = query.get_file_summary('Bearing1_1')
        print(file_summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
