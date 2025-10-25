#!/usr/bin/env python3
"""
NX Witness Storage Calculation Script
====================================

This script calculates video storage requirements for NX Witness based on:
- Bitrate (Mbps)
- Recording duration (days/hours)
- FPS (Frames Per Second)

CORRECTED FORMULAS (Based on real NX Witness data analysis):
- Exact Formula: Storage (GB) = (Bitrate × 60 × 60 × 24 × Days) / (8 × 1024) × 0.356
- Quick Shortcut: Storage (GB) ≈ Bitrate (Mbps) × 3.75 × Days

Note: Original formulas overestimated by ~2.8x due to NX Witness compression.
These corrected formulas account for the actual compression used by NX Witness.
"""

import math
from typing import Dict, List, Tuple


class NXWitnessStorageCalculator:
    """NX Witness Storage Calculator Class"""
    
    # Constants
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_DAY = 86400  # 60 × 60 × 24
    BITS_TO_BYTES = 8
    MB_TO_GB = 1024
    
    def __init__(self):
        """Initialize the calculator"""
        self.reference_fps = 25  # Default reference FPS
    
    def calculate_storage_gb(self, bitrate_mbps: float, days: float) -> float:
        """
        Calculate storage in GB using the NX Witness corrected formula
        
        Args:
            bitrate_mbps: Stream bitrate in Mbps
            days: Recording duration in days
            
        Returns:
            Storage requirement in GB (corrected for NX Witness compression)
        """
        # Original theoretical formula
        theoretical_storage = (bitrate_mbps * self.SECONDS_PER_DAY * days) / (self.BITS_TO_BYTES * self.MB_TO_GB)
        
        # Apply NX Witness compression factor (based on real data analysis)
        compression_factor = 0.356  # NX Witness uses ~35.6% of theoretical storage
        storage_gb = theoretical_storage * compression_factor
        
        return round(storage_gb, 2)
    
    def calculate_storage_quick(self, bitrate_mbps: float, days: float) -> float:
        """
        Calculate storage using the NX Witness corrected quick formula
        
        Args:
            bitrate_mbps: Stream bitrate in Mbps
            days: Recording duration in days
            
        Returns:
            Storage requirement in GB (corrected for NX Witness compression)
        """
        # NX Witness corrected coefficient: 3.75 GB per Mbps per day
        storage_gb = bitrate_mbps * 3.75 * days
        return round(storage_gb, 2)
    
    def calculate_storage_hourly(self, bitrate_mbps: float, hours: float) -> float:
        """
        Calculate storage for hourly duration
        
        Args:
            bitrate_mbps: Stream bitrate in Mbps
            hours: Recording duration in hours
            
        Returns:
            Storage requirement in GB
        """
        days = hours / 24
        return self.calculate_storage_gb(bitrate_mbps, days)
    
    def calculate_effective_bitrate(self, base_bitrate: float, fps: float, reference_fps: float = None) -> float:
        """
        Calculate effective bitrate based on FPS changes
        
        Args:
            base_bitrate: Original bitrate in Mbps
            fps: New FPS
            reference_fps: Reference FPS (default: 25)
            
        Returns:
            Effective bitrate in Mbps
        """
        if reference_fps is None:
            reference_fps = self.reference_fps
        
        effective_bitrate = base_bitrate * (fps / reference_fps)
        return round(effective_bitrate, 2)
    
    def generate_storage_table(self, bitrates: List[float], durations: List[float]) -> Dict:
        """
        Generate storage estimation table
        
        Args:
            bitrates: List of bitrates in Mbps
            durations: List of durations in days
            
        Returns:
            Dictionary containing the storage table
        """
        table = {}
        
        for bitrate in bitrates:
            table[f"{bitrate} Mbps"] = {}
            for days in durations:
                storage_gb = self.calculate_storage_gb(bitrate, days)
                table[f"{bitrate} Mbps"][f"{days} Days"] = storage_gb
        
        return table
    
    def print_storage_table(self, bitrates: List[float] = None, durations: List[float] = None):
        """
        Print formatted storage estimation table
        
        Args:
            bitrates: List of bitrates (default: [1, 2, 3, 4, 5])
            durations: List of durations (default: [1, 7, 15, 30])
        """
        if bitrates is None:
            bitrates = [1, 2, 3, 4, 5]
        if durations is None:
            durations = [1, 7, 15, 30]
        
        table = self.generate_storage_table(bitrates, durations)
        
        print("\n" + "="*60)
        print("NX WITNESS STORAGE ESTIMATION TABLE")
        print("="*60)
        
        # Header
        header = f"{'Bitrate':<12}"
        for days in durations:
            header += f"{f'{days} Days (GB)':<15}"
        print(header)
        print("-" * 60)
        
        # Data rows
        for bitrate_str, data in table.items():
            row = f"{bitrate_str:<12}"
            for days_str, storage in data.items():
                row += f"{storage:<15}"
            print(row)
        
        print("="*60)
    
    def print_quick_reference(self):
        """Print quick reference values"""
        print("\n" + "="*50)
        print("NX WITNESS QUICK REFERENCE VALUES")
        print("(Corrected for NX Witness compression)")
        print("="*50)
        print(f"1 Mbps ≈ {self.calculate_storage_hourly(1, 1):.2f} GB/hour")
        print(f"1 Mbps ≈ {self.calculate_storage_gb(1, 1):.2f} GB/day")
        print(f"1 Mbps ≈ {self.calculate_storage_gb(1, 30):.0f} GB/month (30 days)")
        print("="*50)
        print("Note: Values are corrected for NX Witness compression (35.6% of theoretical)")
    
    def calculate_multiple_cameras(self, cameras_data: List[Dict], days: float) -> Dict:
        """
        Calculate storage for multiple cameras
        
        Args:
            cameras_data: List of dictionaries containing camera info
                         Each dict should have: {'name': str, 'bitrate': float, 'fps': float, 'hours_per_day': float}
            days: Recording duration in days
            
        Returns:
            Dictionary with individual and total storage calculations
        """
        results = {
            'cameras': [],
            'total_storage_gb': 0.0,
            'total_storage_tb': 0.0
        }
        
        for i, camera in enumerate(cameras_data, 1):
            name = camera.get('name', f'Camera {i}')
            bitrate = camera.get('bitrate', 0)
            fps = camera.get('fps', 25)
            hours_per_day = camera.get('hours_per_day', 24)
            
            # Calculate effective bitrate based on recording hours
            effective_bitrate = bitrate * (hours_per_day / 24.0)
            
            # Calculate storage
            storage_gb = self.calculate_storage_gb(effective_bitrate, days)
            
            camera_result = {
                'name': name,
                'bitrate': bitrate,
                'fps': fps,
                'hours_per_day': hours_per_day,
                'effective_bitrate': round(effective_bitrate, 2),
                'storage_gb': storage_gb
            }
            
            results['cameras'].append(camera_result)
            results['total_storage_gb'] += storage_gb
        
        results['total_storage_tb'] = round(results['total_storage_gb'] / 1024, 2)
        return results
    
    def print_multiple_cameras_results(self, results: Dict, days: float):
        """Print formatted results for multiple cameras"""
        print(f"\n[INFO] MULTIPLE CAMERAS STORAGE CALCULATION ({days} days)")
        print("=" * 100)
        print(f"{'Camera':<20} {'Bitrate':<10} {'FPS':<6} {'Hours/Day':<10} {'Eff. Bitrate':<12} {'Storage (GB)':<12}")
        print("-" * 100)
        
        for camera in results['cameras']:
            print(f"{camera['name']:<20} {camera['bitrate']:<10} {camera['fps']:<6} {camera['hours_per_day']:<10} {camera['effective_bitrate']:<12} {camera['storage_gb']:<12}")
        
        print("-" * 100)
        print(f"{'TOTAL STORAGE':<20} {'':<10} {'':<6} {'':<10} {'':<12} {results['total_storage_gb']:<12}")
        print(f"{'TOTAL STORAGE (TB)':<20} {'':<10} {'':<6} {'':<10} {'':<12} {results['total_storage_tb']:<12}")
        print("=" * 100)


def interactive_calculator():
    """Interactive command-line interface for storage calculations"""
    calc = NXWitnessStorageCalculator()
    
    print("NX Witness Storage Calculator")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Calculate storage for specific bitrate and duration")
        print("2. Calculate FPS impact on bitrate")
        print("3. Show storage estimation table")
        print("4. Show quick reference values")
        print("5. Calculate storage for multiple cameras")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            try:
                bitrate = float(input("Enter bitrate (Mbps): "))
                duration_type = input("Enter duration type (days/hours): ").lower()
                
                if duration_type == "days":
                    duration = float(input("Enter duration (days): "))
                    storage_gb = calc.calculate_storage_gb(bitrate, duration)
                    storage_quick = calc.calculate_storage_quick(bitrate, duration)
                    
                    print(f"\nStorage Calculation Results:")
                    print(f"Bitrate: {bitrate} Mbps")
                    print(f"Duration: {duration} days")
                    print(f"Storage (exact): {storage_gb} GB")
                    print(f"Storage (quick): {storage_quick} GB")
                    
                elif duration_type == "hours":
                    duration = float(input("Enter duration (hours): "))
                    storage_gb = calc.calculate_storage_hourly(bitrate, duration)
                    
                    print(f"\nStorage Calculation Results:")
                    print(f"Bitrate: {bitrate} Mbps")
                    print(f"Duration: {duration} hours")
                    print(f"Storage: {storage_gb} GB")
                    
                else:
                    print("Invalid duration type. Please enter 'days' or 'hours'.")
                    
            except ValueError:
                print("[ERROR] Invalid input. Please enter valid numbers.")
        
        elif choice == "2":
            try:
                base_bitrate = float(input("Enter base bitrate (Mbps): "))
                reference_fps = float(input("Enter reference FPS (default 25): ") or "25")
                new_fps = float(input("Enter new FPS: "))
                
                effective_bitrate = calc.calculate_effective_bitrate(base_bitrate, new_fps, reference_fps)
                
                print(f"\n[INFO] FPS Impact Calculation:")
                print(f"Base bitrate: {base_bitrate} Mbps at {reference_fps} FPS")
                print(f"New FPS: {new_fps}")
                print(f"Effective bitrate: {effective_bitrate} Mbps")
                
                # Calculate storage impact for 1 day
                original_storage = calc.calculate_storage_gb(base_bitrate, 1)
                new_storage = calc.calculate_storage_gb(effective_bitrate, 1)
                increase = ((new_storage - original_storage) / original_storage) * 100
                
                print(f"Storage impact (1 day):")
                print(f"  Original: {original_storage} GB")
                print(f"  New: {new_storage} GB")
                print(f"  Increase: {increase:.1f}%")
                
            except ValueError:
                print("[ERROR] Invalid input. Please enter valid numbers.")
        
        elif choice == "3":
            calc.print_storage_table()
        
        elif choice == "4":
            calc.print_quick_reference()
        
        elif choice == "5":
            try:
                print("\n[CAMERA] Multiple Cameras Storage Calculation")
                print("-" * 50)
                
                # Get number of cameras
                num_cameras = int(input("Enter number of cameras: "))
                if num_cameras <= 0:
                    print("[ERROR] Number of cameras must be positive.")
                    continue
                
                # Get duration
                days = float(input("Enter recording duration (days): "))
                
                # Collect camera data
                cameras_data = []
                print(f"\nEnter details for {num_cameras} camera(s):")
                print("-" * 40)
                
                for i in range(num_cameras):
                    print(f"\nCamera {i+1}:")
                    # Auto-generate camera name
                    name = f"Cam{i+1}"
                    print(f"  Camera name: {name} (auto-generated)")
                    
                    bitrate = float(input("  Bitrate (Mbps): "))
                    fps = float(input("  FPS (default 25): ") or "25")
                    hours_per_day = float(input("  Recording hours per day (default 24): ") or "24")
                    
                    cameras_data.append({
                        'name': name,
                        'bitrate': bitrate,
                        'fps': fps,
                        'hours_per_day': hours_per_day
                    })
                
                # Calculate and display results
                results = calc.calculate_multiple_cameras(cameras_data, days)
                calc.print_multiple_cameras_results(results, days)
                
                # Ask for different durations
                while True:
                    more_durations = input("\nCalculate for different duration? (y/n): ").lower()
                    if more_durations in ['y', 'yes']:
                        days = float(input("Enter new duration (days): "))
                        results = calc.calculate_multiple_cameras(cameras_data, days)
                        calc.print_multiple_cameras_results(results, days)
                    else:
                        break
                        
            except ValueError:
                print("[ERROR] Invalid input. Please enter valid numbers.")
            except KeyboardInterrupt:
                print("\n[ERROR] Operation cancelled.")
        
        elif choice == "6":
            print("[EXIT] Goodbye!")
            break
        
        else:
            print("[ERROR] Invalid choice. Please enter 1-6.")


def main():
    """Main function to run the calculator"""
    calc = NXWitnessStorageCalculator()
    
    # Example calculations
    print("🎥 NX Witness Storage Calculator - Examples")
    print("=" * 50)
    
    # Example 1: Basic calculation
    print("\n[EXAMPLE] Example 1: Basic Storage Calculation")
    print("-" * 40)
    bitrate = 4  # Mbps
    days = 7
    storage = calc.calculate_storage_gb(bitrate, days)
    storage_quick = calc.calculate_storage_quick(bitrate, days)
    
    print(f"Bitrate: {bitrate} Mbps")
    print(f"Duration: {days} days")
    print(f"Storage (exact formula): {storage} GB")
    print(f"Storage (quick formula): {storage_quick} GB")
    
    # Example 2: FPS impact
    print("\n[EXAMPLE] Example 2: FPS Impact Calculation")
    print("-" * 40)
    base_bitrate = 4  # Mbps
    reference_fps = 25
    new_fps = 30
    
    effective_bitrate = calc.calculate_effective_bitrate(base_bitrate, new_fps, reference_fps)
    print(f"Base bitrate: {base_bitrate} Mbps at {reference_fps} FPS")
    print(f"New FPS: {new_fps}")
    print(f"Effective bitrate: {effective_bitrate} Mbps")
    
    # Example 3: Hourly calculation
    print("\n[EXAMPLE] Example 3: Hourly Storage Calculation")
    print("-" * 40)
    bitrate = 2  # Mbps
    hours = 12
    storage_hourly = calc.calculate_storage_hourly(bitrate, hours)
    
    print(f"Bitrate: {bitrate} Mbps")
    print(f"Duration: {hours} hours")
    print(f"Storage: {storage_hourly} GB")
    
    # Print reference table
    calc.print_storage_table()
    
    # Print quick reference
    calc.print_quick_reference()
    
    # Example: Multiple cameras calculation
    print("\n[EXAMPLE] Example: Multiple Cameras Storage Calculation")
    print("-" * 50)
    
    sample_cameras = [
        {'name': 'Entrance Camera', 'bitrate': 4.0, 'fps': 25.0, 'hours_per_day': 24.0},
        {'name': 'Parking Lot Camera', 'bitrate': 2.0, 'fps': 30.0, 'hours_per_day': 12.0},
        {'name': 'Office Camera', 'bitrate': 6.0, 'fps': 25.0, 'hours_per_day': 8.0},
        {'name': 'Warehouse Camera', 'bitrate': 8.0, 'fps': 25.0, 'hours_per_day': 24.0}
    ]
    
    results = calc.calculate_multiple_cameras(sample_cameras, 7)
    calc.print_multiple_cameras_results(results, 7)
    
    # Ask if user wants interactive mode
    print("\n" + "="*50)
    interactive = input("Would you like to use the interactive calculator? (y/n): ").lower()
    if interactive in ['y', 'yes']:
        interactive_calculator()


if __name__ == "__main__":
    main()
