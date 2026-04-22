def print_status(robots):
    print("\n--- ROBOT STATES ---")
    for r in robots:
        print(f"{r.id}: status={r.status}, load={r.load}")

def print_auction(bids, winner, task_id):
    print(f"\nTask {task_id} auction:")
    for r, b in bids.items():
        print(f"{r}: {round(b,2)}")

    print(f"Winner: {winner}")