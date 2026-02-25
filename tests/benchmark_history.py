
import timeit
import collections
from datetime import datetime

# Configuration
MAX_HISTORY = 20
LARGE_HISTORY = 100000  # To demonstrate O(n) vs O(1) impact clearly
ITERATIONS = 10000

def test_list_performance(max_history_size):
    history = []
    # Pre-fill
    for i in range(max_history_size):
        history.append({
            "turn": i,
            "command": "test",
            "intent": "TEST",
            "response": "response",
            "timestamp": datetime.now().isoformat()
        })

    def operation():
        history.append({
            "turn": len(history) + 1,
            "command": "new",
            "intent": "NEW",
            "response": "new_response",
            "timestamp": datetime.now().isoformat()
        })
        if len(history) > max_history_size:
            history.pop(0)

    return timeit.timeit(operation, number=ITERATIONS)

def test_deque_performance(max_history_size):
    history = collections.deque(maxlen=max_history_size)
    # Pre-fill
    for i in range(max_history_size):
        history.append({
            "turn": i,
            "command": "test",
            "intent": "TEST",
            "response": "response",
            "timestamp": datetime.now().isoformat()
        })

    def operation():
        # deque with maxlen automatically pops from the other end when full
        history.append({
            "turn": len(history) + 1,
            "command": "new",
            "intent": "NEW",
            "response": "new_response",
            "timestamp": datetime.now().isoformat()
        })
        # No need for explicit pop(0) or popleft() check if maxlen is set
        # But if we want to mimic the explicit check behavior (though maxlen is better):
        # if len(history) > max_history_size:
        #    history.popleft()
        # For the sake of the optimization task, using maxlen is the idiomatic deque way.
        # However, the task description says "Using collections.deque provides O(1) pops from both ends."
        # I should probably check if I should rely on maxlen or manual pop.
        # Manual pop with deque is also O(1).
        # Let's use manual pop to compare apples to apples with the logic structure,
        # although maxlen is the "right" way to use deque for this.

    return timeit.timeit(operation, number=ITERATIONS)

def test_deque_manual_pop_performance(max_history_size):
    history = collections.deque()
    # Pre-fill
    for i in range(max_history_size):
        history.append({
            "turn": i,
            "command": "test",
            "intent": "TEST",
            "response": "response",
            "timestamp": datetime.now().isoformat()
        })

    def operation():
        history.append({
            "turn": len(history) + 1,
            "command": "new",
            "intent": "NEW",
            "response": "new_response",
            "timestamp": datetime.now().isoformat()
        })
        if len(history) > max_history_size:
            history.popleft()

    return timeit.timeit(operation, number=ITERATIONS)

print(f"--- Benchmarking with MAX_HISTORY={MAX_HISTORY} ---")
list_time = test_list_performance(MAX_HISTORY)
deque_time = test_deque_manual_pop_performance(MAX_HISTORY)
print(f"List time:  {list_time:.6f} seconds")
print(f"Deque time: {deque_time:.6f} seconds")
print(f"Speedup: {list_time / deque_time:.2f}x")

print(f"\n--- Benchmarking with MAX_HISTORY={LARGE_HISTORY} ---")
list_time_large = test_list_performance(LARGE_HISTORY)
deque_time_large = test_deque_manual_pop_performance(LARGE_HISTORY)
print(f"List time:  {list_time_large:.6f} seconds")
print(f"Deque time: {deque_time_large:.6f} seconds")
print(f"Speedup: {list_time_large / deque_time_large:.2f}x")
