def selection_sort():
    # Read the size of the array
    n = int(input())
    
    # Read the elements of the array
    arr = list(map(int, input().split()))
    
    # Traverse through all array elements except the last one
    for i in range(n - 1):
        # Find the minimum element in the unsorted array
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
                
        # Swap the found minimum element with the first element of the unsorted part
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        
        # Print the array elements separated by space
        print(" ".join(map(str, arr)))

if __name__ == "__main__":
    selection_sort()
