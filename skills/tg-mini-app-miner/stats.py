"""
agents/miner_stats.py
Backend logic for the Miner game.
"""
import time, random

def get_miner_stats():
    return {
        "balance": 0.50,
        "gas_spent": 0.00,
        "profit": 0.00,
        "win_rate": 0.35,
        "rpc_calls": random.randint(0, 40),
        "hash_rate": "5/hr",
        "verdict": "Working",
        "timestamp": time.time()
    }
