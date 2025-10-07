import asyncio
import time
import random
import argparse

async def worker_task(name: str, duration: int, should_fail: bool = False):
    """
    A simple asynchronous task that simulates a long-running job.
    It prints when it starts and finishes. It can be configured to fail.
    """
    print(f"-> [{name}] Starting, will simulate work for {duration} seconds...")
    await asyncio.sleep(duration)
    
    if should_fail:
        # Raise an exception to simulate a task failure
        raise ValueError(f"[{name}] Oh no! I was designed to fail.")
        
    print(f"<- [{name}] Finished.")
    return f"Result from [{name}]"

async def main(fail_mode: str):
    """
    The main function to orchestrate the asyncio tasks.
    """
    print("--- Testing Asynchronous Task Execution with asyncio.gather ---")
    print(f"Current Mode: '{fail_mode}'")
    
    start_time = time.monotonic()
    
    # --- Define our list of tasks ---
    # Task 'C' is the one we will make fail in our tests.
    tasks_to_run = [
        worker_task("Task A (Short)", duration=10),
        worker_task("Task B (Medium)", duration=20),
        worker_task("Task C (Longest)", duration=30, should_fail=(fail_mode != 'none')),
        worker_task("Task D (Medium)", duration=15),
    ]

    # --- Execute tasks based on the chosen mode ---
    results = []
    if fail_mode == 'fail_fast':
        print("\nRunning in 'fail_fast' mode. One exception will stop everything.")
        try:
            # The default behavior: return_exceptions=False
            results = await asyncio.gather(*tasks_to_run)
        except ValueError as e:
            print(f"\n❌ CAUGHT EXCEPTION: asyncio.gather was cancelled because a task failed.")
            print(f"   Error: {e}")
            
    else: # This covers 'none' and 'robust' modes
        print("\nRunning in 'robust' mode. Exceptions will be caught and returned as results.")
        # return_exceptions=True prevents one failed task from stopping the others.
        results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

    # --- Report the results ---
    end_time = time.monotonic()
    total_time = end_time - start_time
    
    print("\n--- Results ---")
    for result in results:
        if isinstance(result, Exception):
            print(f"  - Task Failed. Result: \033[91m{result}\033[0m") # Red text
        else:
            print(f"  - Task Succeeded. Result: \033[92m{result}\033[0m") # Green text

    print("\n--- Summary ---")
    print(f"Total time taken: {total_time:.2f} seconds.")
    print("Note: The total time should be close to the longest task (30s), not the sum of all durations.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test asyncio.gather behavior.")
    parser.add_argument(
        '--fail-mode',
        type=str,
        choices=['none', 'robust', 'fail_fast'],
        default='none',
        help=(
            "Set the failure mode. 'none': all tasks succeed. "
            "'robust': one task fails but others complete. "
            "'fail_fast': one failure cancels everything."
        )
    )
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.fail_mode))
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")