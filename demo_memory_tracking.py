"""
Demonstration of memory tracking features in FP-growth algorithm.

This script shows how to use the memory tracking functionality added
to the FP-growth implementation.
"""

from fp_growth import mine_frequent_itemsets


def demonstrate_memory_tracking():
    """Demonstrate the memory tracking functionality."""
    print("="*70)
    print("MEMORY TRACKING DEMONSTRATION")
    print("="*70)
    
    # Sample dataset
    transactions = [
        ['bread', 'milk'],
        ['bread', 'diaper', 'beer', 'eggs'],
        ['milk', 'diaper', 'beer', 'cola'],
        ['bread', 'milk', 'diaper', 'beer'],
        ['bread', 'milk', 'diaper', 'cola']
    ]
    
    print(f"\nDataset: {len(transactions)} transactions")
    print(f"Min Support: 40%")
    
    # Run with memory tracking enabled
    print("\n" + "-"*70)
    print("Running FP-growth with memory tracking enabled...")
    print("-"*70)
    
    result = mine_frequent_itemsets(
        transactions, 
        min_support=0.4,
        track_memory=True  # Enable memory tracking
    )
    
    print(f"\n✓ Found {len(result['frequent_itemsets'])} frequent itemsets")
    
    # Display memory statistics
    if 'memory_stats' in result:
        print("\n" + "="*70)
        print("MEMORY STATISTICS")
        print("="*70)
        
        mem = result['memory_stats']
        
        print("\n1. Overall Memory Usage:")
        print(f"   Peak Memory:    {mem['peak_memory_mb']:.4f} MB ({mem['peak_memory_kb']:.2f} KB)")
        print(f"   Memory Used:    {mem['memory_used_mb']:.4f} MB ({mem['memory_used_kb']:.2f} KB)")
        print(f"   Current Memory: {mem['current_memory_bytes'] / 1024:.2f} KB")
        
        tree_stats = mem['tree_stats']
        print("\n2. FP-Tree Statistics:")
        print(f"   Total Trees Created:     {tree_stats['total_trees_created']}")
        print(f"   Max Tree Nodes:          {tree_stats['max_tree_nodes']}")
        print(f"   Max Tree Depth:          {tree_stats['max_tree_depth']}")
        print(f"   Total Tree Memory:       {tree_stats['total_tree_memory_bytes'] / 1024:.2f} KB")
        
        print("\n3. Memory Efficiency:")
        bytes_per_itemset = mem['memory_used_bytes'] / len(result['frequent_itemsets'])
        print(f"   Memory per Itemset:      {bytes_per_itemset:.2f} bytes")
        bytes_per_transaction = mem['memory_used_bytes'] / len(transactions)
        print(f"   Memory per Transaction:  {bytes_per_transaction:.2f} bytes")
        
        print("\n4. Tree Efficiency:")
        compression_ratio = len(transactions) / tree_stats['max_tree_nodes']
        print(f"   Compression Ratio:       {compression_ratio:.2f}x")
        print(f"   (Transactions / Max Nodes)")
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nHow to use memory tracking in your code:")
    print("  result = mine_frequent_itemsets(transactions, min_support=0.4, track_memory=True)")
    print("  mem_stats = result['memory_stats']")
    print("  print(f'Peak memory: {mem_stats[\"peak_memory_mb\"]:.2f} MB')")


if __name__ == "__main__":
    demonstrate_memory_tracking()
