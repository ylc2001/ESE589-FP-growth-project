"""
Data preprocessing module for the Online Retail dataset.

Downloads and preprocesses the Online Retail dataset from UCI Machine Learning Repository
for use with the FP-growth algorithm.
"""

import os
import pandas as pd
import numpy as np
from typing import List, Tuple
import urllib.request
import zipfile
import warnings
warnings.filterwarnings('ignore')


def download_dataset(data_dir: str = 'data') -> str:
    """
    Download the Online Retail dataset from UCI repository.
    
    Args:
        data_dir: Directory to save the dataset
        
    Returns:
        Path to the downloaded Excel file
    """
    os.makedirs(data_dir, exist_ok=True)
    
    # URL for the Online Retail dataset
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    file_path = os.path.join(data_dir, "Online_Retail.xlsx")
    
    if os.path.exists(file_path):
        print(f"Dataset already exists at {file_path}")
        return file_path
    
    print(f"Downloading Online Retail dataset from {url} ...")
    
    try:
        urllib.request.urlretrieve(url, file_path)
        print(f"Dataset downloaded successfully to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        raise


def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """
    Load and perform initial cleaning of the Online Retail dataset.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Cleaned DataFrame
    """
    print("\nLoading dataset...")
    df = pd.read_excel(file_path)
    
    print(f"Original dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Display basic info
    print("\nDataset Info:")
    print(df.info())
    
    print("\nFirst few rows:")
    print(df.head())
    
    print("\n" + "="*70)
    print("Data Cleaning Steps:")
    print("="*70)
    
    # # Step 1: Remove rows with missing CustomerID
    # initial_rows = len(df)
    # df = df[df['CustomerID'].notna()]
    # removed = initial_rows - len(df)
    # print(f"1. Removed {removed} rows with missing CustomerID")
    # print(f"   Remaining rows: {len(df)}")
    
    # Step 2: Remove rows with missing Description
    initial_rows = len(df)
    df = df[df['Description'].notna()]
    removed = initial_rows - len(df)
    print(f"2. Removed {removed} rows with missing Description")
    print(f"   Remaining rows: {len(df)}")
    
    # Step 3: Remove rows with negative or zero Quantity
    initial_rows = len(df)
    df = df[df['Quantity'] > 0]
    removed = initial_rows - len(df)
    print(f"3. Removed {removed} rows with Quantity <= 0 (returns/cancellations)")
    print(f"   Remaining rows: {len(df)}")
    
    # Step 4: Remove rows with negative UnitPrice
    initial_rows = len(df)
    df = df[df['UnitPrice'] > 0]
    removed = initial_rows - len(df)
    print(f"4. Removed {removed} rows with UnitPrice <= 0")
    print(f"   Remaining rows: {len(df)}")
    
    # Step 5: Clean Description - remove special characters and convert to lowercase
    df['Description'] = df['Description'].str.strip().str.lower()
    
    # Step 6: Remove items that are not products (e.g., postage, manual, etc.)
    non_product_keywords = ['postage', 'manual', 'damaged', 'lost', 'wrong', 'adjustment', 
                           'bank charges', 'dotcom', 'amazon fee', 'carriage']
    initial_rows = len(df)
    for keyword in non_product_keywords:
        df = df[~df['Description'].str.contains(keyword, na=False)]
    removed = initial_rows - len(df)
    print(f"5. Removed {removed} rows with non-product items")
    print(f"   Remaining rows: {len(df)}")
    
    print(f"\nFinal dataset shape: {df.shape}")
    
    return df


def create_transactions(df: pd.DataFrame, 
                       sample_size: int = None,
                       min_items_per_transaction: int = 1) -> Tuple[List[List[str]], pd.DataFrame]:
    """
    Convert the cleaned DataFrame into transaction format for FP-growth.
    
    Args:
        df: Cleaned DataFrame
        sample_size: Number of transactions to sample (None for all)
        min_items_per_transaction: Minimum number of items per transaction
        
    Returns:
        Tuple of (list of transactions, transactions DataFrame)
    """
    print("\n" + "="*70)
    print("Creating Transaction Format:")
    print("="*70)
    
    # Group by InvoiceNo to create transactions
    print("Grouping by InvoiceNo to create transactions...")
    transactions_df = df.groupby('InvoiceNo')['Description'].apply(list).reset_index()
    transactions_df.columns = ['InvoiceNo', 'Items']
    
    # Add transaction size
    transactions_df['TransactionSize'] = transactions_df['Items'].apply(len)
    
    # Filter by minimum items
    initial_count = len(transactions_df)
    transactions_df = transactions_df[transactions_df['TransactionSize'] >= min_items_per_transaction]
    filtered = initial_count - len(transactions_df)
    print(f"Filtered {filtered} transactions with < {min_items_per_transaction} items")
    
    # Sample if requested
    if sample_size and sample_size < len(transactions_df):
        print(f"Sampling {sample_size} transactions from {len(transactions_df)} total")
        transactions_df = transactions_df.sample(n=sample_size, random_state=42)
    
    print(f"\nTotal transactions: {len(transactions_df)}")
    print(f"Average items per transaction: {transactions_df['TransactionSize'].mean():.2f}")
    print(f"Median items per transaction: {transactions_df['TransactionSize'].median():.0f}")
    print(f"Min items per transaction: {transactions_df['TransactionSize'].min()}")
    print(f"Max items per transaction: {transactions_df['TransactionSize'].max()}")
    
    # Transaction size distribution
    print("\nTransaction Size Distribution:")
    size_dist = transactions_df['TransactionSize'].value_counts().sort_index().head(10)
    for size, count in size_dist.items():
        print(f"  {size} items: {count} transactions")
    
    # Convert to list format
    transactions = transactions_df['Items'].tolist()
    
    return transactions, transactions_df


def get_item_statistics(transactions: List[List[str]]) -> pd.DataFrame:
    """
    Get statistics about items in the transactions.
    
    Args:
        transactions: List of transactions
        
    Returns:
        DataFrame with item statistics
    """
    from collections import Counter
    
    # Count item frequencies
    item_counter = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counter[item] += 1
    
    # Create statistics DataFrame
    stats_df = pd.DataFrame([
        {'Item': item, 'Frequency': count, 
         'Support': count / len(transactions)}
        for item, count in item_counter.most_common()
    ])
    
    return stats_df


def preprocess_online_retail(data_dir: str = 'data',
                             sample_size: int = None,
                             min_items_per_transaction: int = 1,
                             force_download: bool = False) -> Tuple[List[List[str]], pd.DataFrame, pd.DataFrame]:
    """
    Complete preprocessing pipeline for Online Retail dataset.
    
    Args:
        data_dir: Directory to save/load the dataset
        sample_size: Number of transactions to sample (None for all)
        min_items_per_transaction: Minimum number of items per transaction
        force_download: Force re-download even if file exists
        
    Returns:
        Tuple of (transactions list, transactions DataFrame, item statistics DataFrame)
    """
    print("="*70)
    print("ONLINE RETAIL DATASET PREPROCESSING")
    print("="*70)
    
    # Download dataset
    if force_download:
        file_path = os.path.join(data_dir, "Online_Retail.xlsx")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    file_path = download_dataset(data_dir)
    
    # Load and clean data
    df = load_and_clean_data(file_path)
    
    # Create transactions
    transactions, transactions_df = create_transactions(
        df, sample_size, min_items_per_transaction
    )
    
    # Get item statistics
    print("\n" + "="*70)
    print("Item Statistics:")
    print("="*70)
    
    item_stats = get_item_statistics(transactions)
    print(f"\nTotal unique items: {len(item_stats)}")
    print(f"\nTop 20 most frequent items:")
    print(item_stats.head(20).to_string(index=False))
    
    return transactions, transactions_df, item_stats


if __name__ == "__main__":
    # Example usage with a small sample
    print("\nExample: Preprocessing with 1000 transactions sample")
    transactions, trans_df, item_stats = preprocess_online_retail(
        sample_size=1000,
        min_items_per_transaction=2
    )
    
    print("\n" + "="*70)
    print("Sample Transactions:")
    print("="*70)
    for i, transaction in enumerate(transactions[:5], 1):
        print(f"Transaction {i} ({len(transaction)} items): {transaction[:10]}{'...' if len(transaction) > 10 else ''}")
    
    # Save preprocessed data
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    trans_df.to_csv(os.path.join(output_dir, 'transactions.csv'), index=False)
    item_stats.to_csv(os.path.join(output_dir, 'item_statistics.csv'), index=False)
    
    print(f"\n✓ Preprocessed data saved to {output_dir}/")
