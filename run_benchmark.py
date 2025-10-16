"""
Run benchmark experiments using either real Online Retail data or synthetic data.

This script automatically falls back to synthetic data if the Online Retail
dataset cannot be downloaded.
"""

import os
import sys
from benchmark import (
    run_support_variation_experiments,
    run_scalability_experiments,
    run_experiment,
    create_visualizations,
    save_results,
    generate_summary_report
)


def get_data(sample_size=5000):
    """
    Get transaction data - tries Online Retail first, falls back to synthetic data.
    
    Args:
        sample_size: Number of transactions to use
        
    Returns:
        Tuple of (transactions, transactions_df, item_stats)
    """
    print("\n" + "="*70)
    print("LOADING DATA")
    print("="*70)
    
    # Try to load real Online Retail data
    try:
        print("\nAttempting to download Online Retail dataset...")
        from preprocess import preprocess_online_retail
        
        transactions, trans_df, item_stats = preprocess_online_retail(
            sample_size=sample_size,
            min_items_per_transaction=2
        )
        print("\n✓ Using real Online Retail dataset")
        return transactions, trans_df, item_stats, "Online Retail"
        
    except Exception as e:
            print(f"\n⚠ Could not download Online Retail dataset: {e}")
            sys.exit(1)  # Exit the program with an error code


def main():    
    print("\n[1/3] Loading transaction data...")
    transactions, trans_df, item_stats, data_source = get_data(sample_size=15000)
    
    print(f"\nData source: {data_source}")
    print(f"Transactions: {len(transactions)}")
    print(f"Unique items: {len(item_stats)}")
    
    # Experiment 1: Support variation
    print("\n[2/3] Running support variation experiments...")
    support_values = [0.01, 0.02, 0.05, 0.1, 0.15]
    support_results = run_support_variation_experiments(transactions, support_values)
    
    # Experiment 2: Scalability
    print("\n[3/3] Running scalability experiments...")
    sizes = [500, 1000, 2000, 3000, 5000, 8000, 12000, 15000]
    scalability_results = run_scalability_experiments(
        transactions, sizes, min_support=0.05
    )
    
    # Save results
    print("\n" + "="*70)
    print("SAVING RESULTS AND CREATING VISUALIZATIONS")
    print("="*70)
    
    save_results(support_results, filename='support_variation_results.json')
    save_results(scalability_results, filename='scalability_results.json')
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_visualizations(support_results)
    create_visualizations(scalability_results)
    
    # Generate summary report
    print("\nGenerating summary report...")
    generate_summary_report(support_results, scalability_results)
    
    print("\n" + "="*70)
    print("✓ BENCHMARK COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nResults saved to 'results/' directory:")
    print("  - support_variation_results.json")
    print("  - scalability_results.json")
    print("  - support_variation.png")
    print("  - scalability.png")
    print("  - BENCHMARK_REPORT.md")
    print("\nRun 'cat results/BENCHMARK_REPORT.md' to view the summary report.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
