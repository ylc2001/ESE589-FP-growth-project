"""
Benchmark experiments for FP-Growth algorithm on Online Retail dataset.

This module runs comprehensive experiments to validate and benchmark
the FP-growth implementation.
"""

import os
import time
import json
from typing import Dict, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from fp_growth import mine_frequent_itemsets
from preprocess import preprocess_online_retail


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {seconds % 60:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def run_experiment(transactions: List[List[str]], 
                   min_support: float,
                   experiment_name: str = "Experiment") -> Dict:
    """
    Run a single FP-growth experiment and collect results.
    
    Args:
        transactions: List of transactions
        min_support: Minimum support threshold
        experiment_name: Name of the experiment
        
    Returns:
        Dictionary with experiment results
    """
    print(f"\n{'='*70}")
    print(f"{experiment_name}")
    print(f"{'='*70}")
    print(f"Transactions: {len(transactions)}")
    print(f"Min Support: {min_support}")
    
    # Run FP-growth with memory tracking
    start_time = time.time()
    result = mine_frequent_itemsets(
        transactions, 
        min_support=min_support,
        track_memory=True  # Enable memory tracking
    )
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Analyze results
    frequent_itemsets = result['frequent_itemsets']
    memory_stats = result.get('memory_stats', {})
    
    # Group by size
    by_size = {}
    for itemset in frequent_itemsets.keys():
        size = len(itemset)
        by_size[size] = by_size.get(size, 0) + 1
    
    print(f"\nExecution Time: {format_time(execution_time)}")
    print(f"Frequent Itemsets Found: {len(frequent_itemsets)}")
    print(f"Min Support Count: {result['min_support_count']}")
    
    # Print memory statistics
    if memory_stats:
        print(f"\nMemory Statistics:")
        print(f"  Peak Memory: {memory_stats['peak_memory_mb']:.2f} MB ({memory_stats['peak_memory_kb']:.2f} KB)")
        print(f"  Memory Used: {memory_stats['memory_used_mb']:.2f} MB ({memory_stats['memory_used_kb']:.2f} KB)")
        tree_stats = memory_stats.get('tree_stats', {})
        if tree_stats:
            print(f"  Total FP-Trees Created: {tree_stats['total_trees_created']}")
            print(f"  Max Tree Nodes: {tree_stats['max_tree_nodes']}")
            print(f"  Max Tree Depth: {tree_stats['max_tree_depth']}")
            print(f"  Total Tree Memory: {tree_stats['total_tree_memory_bytes'] / 1024:.2f} KB")
    
    print("\nItemsets by Size:")
    for size in sorted(by_size.keys()):
        print(f"  {size}-itemsets: {by_size[size]}")
    
    # Compile results
    experiment_result = {
        'name': experiment_name,
        'num_transactions': len(transactions),
        'min_support': min_support,
        'min_support_count': result['min_support_count'],
        'num_frequent_itemsets': len(frequent_itemsets),
        'itemsets_by_size': by_size,
        'execution_time': execution_time,
    }
    
    # Add memory statistics to results
    if memory_stats:
        experiment_result['memory_stats'] = {
            'peak_memory_mb': memory_stats['peak_memory_mb'],
            'peak_memory_kb': memory_stats['peak_memory_kb'],
            'memory_used_mb': memory_stats['memory_used_mb'],
            'memory_used_kb': memory_stats['memory_used_kb'],
            'total_trees_created': memory_stats['tree_stats']['total_trees_created'],
            'max_tree_nodes': memory_stats['tree_stats']['max_tree_nodes'],
            'max_tree_depth': memory_stats['tree_stats']['max_tree_depth'],
            'total_tree_memory_kb': memory_stats['tree_stats']['total_tree_memory_bytes'] / 1024,
        }
    
    # Top frequent itemsets
    top_itemsets = sorted(
        [(set(itemset), support) for itemset, support in frequent_itemsets.items()],
        key=lambda x: -x[1]
    )[:20]
    
    print("\nTop 20 Frequent Itemsets:")
    for itemset, support in top_itemsets:
        support_pct = (support / len(transactions)) * 100
        print(f"  {itemset}: {support} ({support_pct:.1f}%)")
    
    experiment_result['top_itemsets'] = [
        {
            'itemset': list(itemset),
            'support': int(support),
            'support_pct': float((support / len(transactions)) * 100)
        }
        for itemset, support in top_itemsets
    ]
    
    return experiment_result


def run_support_variation_experiments(transactions: List[List[str]],
                                      support_values: List[float]) -> List[Dict]:
    """
    Run experiments with varying support thresholds.
    
    Args:
        transactions: List of transactions
        support_values: List of support thresholds to test
        
    Returns:
        List of experiment results
    """
    print("\n" + "="*70)
    print("SUPPORT THRESHOLD VARIATION EXPERIMENTS")
    print("="*70)
    
    results = []
    for min_support in support_values:
        result = run_experiment(
            transactions,
            min_support=min_support,
            experiment_name=f"Experiment: Support = {min_support}"
        )
        results.append(result)
    
    return results


def run_scalability_experiments(base_transactions: List[List[str]],
                                sizes: List[int],
                                min_support: float) -> List[Dict]:
    """
    Run experiments with varying dataset sizes to test scalability.
    
    Args:
        base_transactions: Full list of transactions
        sizes: List of dataset sizes to test
        min_support: Minimum support threshold
        
    Returns:
        List of experiment results
    """
    print("\n" + "="*70)
    print("SCALABILITY EXPERIMENTS")
    print("="*70)
    
    results = []
    for size in sizes:
        if size > len(base_transactions):
            print(f"\nSkipping size {size} (exceeds dataset size {len(base_transactions)})")
            continue
        
        # Sample transactions
        transactions_sample = base_transactions[:size]
        
        result = run_experiment(
            transactions_sample,
            min_support=min_support,
            experiment_name=f"Experiment: {size} Transactions"
        )
        results.append(result)
    
    return results


def create_visualizations(results: List[Dict], output_dir: str = 'results'):
    """
    Create visualizations from experiment results.
    
    Args:
        results: List of experiment results
        output_dir: Directory to save visualizations
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if results vary by support or size
    support_values = [r['min_support'] for r in results]
    sizes = [r['num_transactions'] for r in results]
    
    # Check if memory stats are available
    has_memory_stats = all('memory_stats' in r for r in results)
    
    if len(set(support_values)) > 1:
        # Support variation plots
        num_plots = 6 if has_memory_stats else 4
        fig, axes = plt.subplots(3, 2, figsize=(14, 15)) if has_memory_stats else plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('FP-Growth Performance vs Support Threshold', fontsize=16)
        
        axes_flat = axes.flatten() if has_memory_stats else axes.flatten()
        
        # Plot 1: Number of frequent itemsets vs support
        ax1 = axes_flat[0]
        ax1.plot(support_values, [r['num_frequent_itemsets'] for r in results], 
                marker='o', linewidth=2, markersize=8)
        ax1.set_xlabel('Minimum Support', fontsize=12)
        ax1.set_ylabel('Number of Frequent Itemsets', fontsize=12)
        ax1.set_title('Frequent Itemsets vs Support')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Execution time vs support
        ax2 = axes_flat[1]
        ax2.plot(support_values, [r['execution_time'] for r in results], 
                marker='s', color='red', linewidth=2, markersize=8)
        ax2.set_xlabel('Minimum Support', fontsize=12)
        ax2.set_ylabel('Execution Time (seconds)', fontsize=12)
        ax2.set_title('Execution Time vs Support')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Itemsets by size (stacked bar)
        ax3 = axes_flat[2]
        max_size = max(max(r['itemsets_by_size'].keys()) for r in results if r['itemsets_by_size'])
        sizes_data = {size: [] for size in range(1, max_size + 1)}
        for result in results:
            for size in range(1, max_size + 1):
                sizes_data[size].append(result['itemsets_by_size'].get(size, 0))
        
        bottom = [0] * len(results)
        for size in range(1, max_size + 1):
            ax3.bar(range(len(results)), sizes_data[size], bottom=bottom, 
                   label=f'{size}-itemsets')
            bottom = [b + s for b, s in zip(bottom, sizes_data[size])]
        
        ax3.set_xlabel('Experiment Index', fontsize=12)
        ax3.set_ylabel('Number of Itemsets', fontsize=12)
        ax3.set_title('Itemset Size Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Min support count
        ax4 = axes_flat[3]
        ax4.plot(support_values, [r['min_support_count'] for r in results], 
                marker='^', color='green', linewidth=2, markersize=8)
        ax4.set_xlabel('Minimum Support', fontsize=12)
        ax4.set_ylabel('Minimum Support Count', fontsize=12)
        ax4.set_title('Minimum Support Count vs Support')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Memory usage (if available)
        if has_memory_stats:
            ax5 = axes_flat[4]
            memory_used = [r['memory_stats']['memory_used_mb'] for r in results]
            ax5.plot(support_values, memory_used, 
                    marker='D', color='purple', linewidth=2, markersize=8)
            ax5.set_xlabel('Minimum Support', fontsize=12)
            ax5.set_ylabel('Memory Used (MB)', fontsize=12)
            ax5.set_title('Memory Usage vs Support')
            ax5.grid(True, alpha=0.3)
            
            # Plot 6: FP-tree statistics
            ax6 = axes_flat[5]
            trees_created = [r['memory_stats']['total_trees_created'] for r in results]
            max_nodes = [r['memory_stats']['max_tree_nodes'] for r in results]
            
            ax6_twin = ax6.twinx()
            line1 = ax6.plot(support_values, trees_created, 
                    marker='o', color='blue', linewidth=2, markersize=8, label='Trees Created')
            line2 = ax6_twin.plot(support_values, max_nodes, 
                    marker='s', color='orange', linewidth=2, markersize=8, label='Max Nodes')
            
            ax6.set_xlabel('Minimum Support', fontsize=12)
            ax6.set_ylabel('Trees Created', fontsize=12, color='blue')
            ax6_twin.set_ylabel('Max Tree Nodes', fontsize=12, color='orange')
            ax6.set_title('FP-Tree Statistics vs Support')
            ax6.tick_params(axis='y', labelcolor='blue')
            ax6_twin.tick_params(axis='y', labelcolor='orange')
            ax6.grid(True, alpha=0.3)
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax6.legend(lines, labels, loc='best')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'support_variation.png'), dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved visualization: {output_dir}/support_variation.png")
        plt.close()
    
    elif len(set(sizes)) > 1:
        # Scalability plots
        num_plots = 6 if has_memory_stats else 4
        fig, axes = plt.subplots(3, 2, figsize=(14, 15)) if has_memory_stats else plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('FP-Growth Scalability Analysis', fontsize=16)
        
        axes_flat = axes.flatten() if has_memory_stats else axes.flatten()
        
        # Plot 1: Execution time vs dataset size
        ax1 = axes_flat[0]
        ax1.plot(sizes, [r['execution_time'] for r in results], 
                marker='o', linewidth=2, markersize=8)
        ax1.set_xlabel('Number of Transactions', fontsize=12)
        ax1.set_ylabel('Execution Time (seconds)', fontsize=12)
        ax1.set_title('Execution Time vs Dataset Size')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Frequent itemsets vs dataset size
        ax2 = axes_flat[1]
        ax2.plot(sizes, [r['num_frequent_itemsets'] for r in results], 
                marker='s', color='red', linewidth=2, markersize=8)
        ax2.set_xlabel('Number of Transactions', fontsize=12)
        ax2.set_ylabel('Number of Frequent Itemsets', fontsize=12)
        ax2.set_title('Frequent Itemsets vs Dataset Size')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Time per transaction
        ax3 = axes_flat[2]
        time_per_trans = [r['execution_time'] / r['num_transactions'] * 1000 
                         for r in results]
        ax3.plot(sizes, time_per_trans, 
                marker='^', color='green', linewidth=2, markersize=8)
        ax3.set_xlabel('Number of Transactions', fontsize=12)
        ax3.set_ylabel('Time per Transaction (ms)', fontsize=12)
        ax3.set_title('Time per Transaction vs Dataset Size')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Summary table
        ax4 = axes_flat[3]
        ax4.axis('tight')
        ax4.axis('off')
        table_data = [
            ['Transactions', 'Time (s)', 'Itemsets', 'Time/Trans (ms)']
        ]
        for r in results:
            table_data.append([
                str(r['num_transactions']),
                f"{r['execution_time']:.2f}",
                str(r['num_frequent_itemsets']),
                f"{r['execution_time'] / r['num_transactions'] * 1000:.3f}"
            ])
        
        table = ax4.table(cellText=table_data, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header row
        for i in range(4):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Plot 5: Memory usage vs dataset size (if available)
        if has_memory_stats:
            ax5 = axes_flat[4]
            memory_used = [r['memory_stats']['memory_used_mb'] for r in results]
            ax5.plot(sizes, memory_used, 
                    marker='D', color='purple', linewidth=2, markersize=8)
            ax5.set_xlabel('Number of Transactions', fontsize=12)
            ax5.set_ylabel('Memory Used (MB)', fontsize=12)
            ax5.set_title('Memory Usage vs Dataset Size')
            ax5.grid(True, alpha=0.3)
            
            # Plot 6: FP-tree growth
            ax6 = axes_flat[5]
            max_nodes = [r['memory_stats']['max_tree_nodes'] for r in results]
            max_depth = [r['memory_stats']['max_tree_depth'] for r in results]
            
            ax6_twin = ax6.twinx()
            line1 = ax6.plot(sizes, max_nodes, 
                    marker='o', color='blue', linewidth=2, markersize=8, label='Max Nodes')
            line2 = ax6_twin.plot(sizes, max_depth, 
                    marker='s', color='orange', linewidth=2, markersize=8, label='Max Depth')
            
            ax6.set_xlabel('Number of Transactions', fontsize=12)
            ax6.set_ylabel('Max Tree Nodes', fontsize=12, color='blue')
            ax6_twin.set_ylabel('Max Tree Depth', fontsize=12, color='orange')
            ax6.set_title('FP-Tree Growth vs Dataset Size')
            ax6.tick_params(axis='y', labelcolor='blue')
            ax6_twin.tick_params(axis='y', labelcolor='orange')
            ax6.grid(True, alpha=0.3)
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax6.legend(lines, labels, loc='best')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'scalability.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization: {output_dir}/scalability.png")
        plt.close()


def save_results(results: List[Dict], output_dir: str = 'results', 
                filename: str = 'experiment_results.json'):
    """
    Save experiment results to JSON file.
    
    Args:
        results: List of experiment results
        output_dir: Directory to save results
        filename: Output filename
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")
