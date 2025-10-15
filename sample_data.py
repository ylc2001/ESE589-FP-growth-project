"""
Generate sample retail transaction data for testing and demonstration.

Since the Online Retail dataset requires internet access to download,
this module generates realistic synthetic data that mimics the structure
and patterns of retail transactions.
"""

import random
import pandas as pd
from typing import List, Tuple


# Sample product catalog (realistic retail items)
PRODUCT_CATALOG = [
    # Common household items
    "white hanging heart t-light holder", "white metal lantern", "cream cupid hearts coat hanger",
    "knitted union flag hot water bottle", "red woolly hottie white heart",
    "set 7 babushka nesting boxes", "glass star frosted t-light holder",
    
    # Kitchen items
    "spaceboy lunch box", "robot lunch box", "dolly girl lunch box",
    "jumbo bag red retrospot", "jumbo bag pink polkadot", "jumbo bag baroque black white",
    "lunch bag red retrospot", "lunch bag pink polkadot", "lunch bag black skull",
    
    # Decorative items
    "regency cakestand 3 tier", "charlotte bag dolly girl design",
    "pink regency teacup and saucer", "green regency teacup and saucer",
    "roses regency teacup and saucer", "vintage doily bunting",
    
    # Party supplies
    "pack of 72 retrospot cake cases", "pack of 60 pink paisley cake cases",
    "pack of 60 red retrospot cake cases", "paper chain kit 50's christmas",
    "paper chain kit vintage christmas", "red retrospot paper napkins",
    
    # Storage and organization
    "wooden box of dominoes", "wooden box of chess", "wooden box of draughts",
    "spotty bunting", "baking set 9 piece retrospot", "alarm clock bakelike red",
    "alarm clock bakelike green", "alarm clock bakelike pink",
    
    # Home decor
    "jumbo storage bag suki", "jumbo bag strawberry", "jumbo shopper vintage red paisley",
    "party bunting", "bunting flag red", "bunting flag pink", "bunting flag blue",
    "red toadstool led night light", "chocolate hot water bottle",
    
    # Toys and gifts
    "rubber ducky hot water bottle", "spotty pencil box", "fairy cake flannel assorted colour",
    "mini paint set vintage", "spotty water bottle", "dinosaur water bottle",
    "pirate water bottle", "folk art flowers jumbo bag", "strawberry lunch box",
    
    # Seasonal items
    "mini lights glass jars", "advent calendar gingham sack", "christmas gift bag small",
    "christmas gift bag medium", "christmas wrapping paper", "christmas card pack",
    "christmas baubles red", "christmas baubles silver", "christmas baubles gold",
    
    # Kitchen accessories
    "set of 3 cake tins pink", "set of 3 cake tins green", "set of 3 cake tins blue",
    "recipe box retrospot", "recipe box pantry design", "oven glove spotty",
    "tea cosy retrospot", "doormat red retrospot", "doormat new england",
    
    # Office supplies
    "notebook set of 3", "red retrospot pencils", "pencil sharpener retrospot",
    "tape dispenser retrospot", "scissors retrospot", "ruler retrospot",
    
    # Bags and accessories
    "weekender bag red retrospot", "shopper bag pink polkadot", "tote bag red retrospot",
    "shoulder bag red retrospot", "mini shoulder bag pink", "clutch bag red retrospot",
]

# Create product frequency tiers (some items are more popular)
VERY_COMMON_ITEMS = PRODUCT_CATALOG[:15]  # 15% of products, 50% of purchases
COMMON_ITEMS = PRODUCT_CATALOG[15:35]     # 20% of products, 30% of purchases  
UNCOMMON_ITEMS = PRODUCT_CATALOG[35:]     # 65% of products, 20% of purchases


def generate_transaction(avg_items: int = 10, std_dev: int = 5) -> List[str]:
    """
    Generate a single synthetic transaction.
    
    Args:
        avg_items: Average number of items per transaction
        std_dev: Standard deviation of items per transaction
        
    Returns:
        List of items in the transaction
    """
    # Determine transaction size (following normal distribution)
    size = max(1, int(random.gauss(avg_items, std_dev)))
    
    items = []
    
    # Follow realistic shopping patterns:
    # - 50% chance of items from very common products
    # - 30% chance of items from common products
    # - 20% chance of items from uncommon products
    
    for _ in range(size):
        rand = random.random()
        if rand < 0.5:
            item = random.choice(VERY_COMMON_ITEMS)
        elif rand < 0.8:
            item = random.choice(COMMON_ITEMS)
        else:
            item = random.choice(UNCOMMON_ITEMS)
        
        # Avoid duplicates in same transaction
        if item not in items:
            items.append(item)
    
    return items


def generate_sample_dataset(num_transactions: int = 5000,
                            avg_items: int = 10,
                            std_dev: int = 5,
                            seed: int = 42) -> Tuple[List[List[str]], pd.DataFrame]:
    """
    Generate a synthetic retail dataset.
    
    Args:
        num_transactions: Number of transactions to generate
        avg_items: Average number of items per transaction
        std_dev: Standard deviation of items per transaction
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (transactions list, DataFrame with transaction info)
    """
    random.seed(seed)
    
    print(f"\nGenerating {num_transactions} synthetic retail transactions...")
    print(f"Product catalog: {len(PRODUCT_CATALOG)} unique items")
    print(f"Average items per transaction: {avg_items} ± {std_dev}")
    
    transactions = []
    transaction_data = []
    
    for i in range(num_transactions):
        transaction = generate_transaction(avg_items, std_dev)
        transactions.append(transaction)
        
        transaction_data.append({
            'InvoiceNo': f'INV{i+1:06d}',
            'Items': transaction,
            'TransactionSize': len(transaction)
        })
    
    df = pd.DataFrame(transaction_data)
    
    print(f"\nGenerated {len(transactions)} transactions")
    print(f"Actual average items per transaction: {df['TransactionSize'].mean():.2f}")
    print(f"Median items per transaction: {df['TransactionSize'].median():.0f}")
    print(f"Min items: {df['TransactionSize'].min()}")
    print(f"Max items: {df['TransactionSize'].max()}")
    
    # Calculate item frequencies
    from collections import Counter
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    
    print(f"\nTop 10 most frequent items:")
    for item, count in item_counts.most_common(10):
        support = count / len(transactions)
        print(f"  {item}: {count} ({support:.2%})")
    
    return transactions, df


def get_sample_data(size: int = 5000) -> Tuple[List[List[str]], pd.DataFrame, pd.DataFrame]:
    """
    Get sample data in the same format as preprocess_online_retail.
    
    Args:
        size: Number of transactions to generate
        
    Returns:
        Tuple of (transactions list, transactions DataFrame, item statistics DataFrame)
    """
    transactions, trans_df = generate_sample_dataset(size)
    
    # Create item statistics
    from collections import Counter
    item_counter = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counter[item] += 1
    
    stats_df = pd.DataFrame([
        {'Item': item, 'Frequency': count, 
         'Support': count / len(transactions)}
        for item, count in item_counter.most_common()
    ])
    
    return transactions, trans_df, stats_df


if __name__ == "__main__":
    print("="*70)
    print("SAMPLE RETAIL DATA GENERATOR")
    print("="*70)
    
    # Generate sample data
    transactions, df, stats = get_sample_data(1000)
    
    print("\n" + "="*70)
    print("Sample Transactions:")
    print("="*70)
    for i, transaction in enumerate(transactions[:5], 1):
        print(f"Transaction {i} ({len(transaction)} items):")
        print(f"  {transaction[:5]}{'...' if len(transaction) > 5 else ''}")
    
    print("\n✓ Sample data generation successful!")
