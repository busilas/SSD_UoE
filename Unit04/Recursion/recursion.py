def towers_of_hanoi(n, source, target, auxiliary):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return 1

    # Move n-1 disks from source to auxiliary, using target as a temporary rod
    moves = towers_of_hanoi(n - 1, source, auxiliary, target)

    # Move the nth disk from source to target
    print(f"Move disk {n} from {source} to {target}")
    moves += 1

    # Move n-1 disks from auxiliary to target, using source as a temporary rod
    moves += towers_of_hanoi(n - 1, auxiliary, target, source)

    return moves

def main():
    try:
        n = int(input("Enter the number of disks: "))
        if n <= 0:
            print("Number of disks must be positive!")
            return

        print("\nTowers of Hanoi solution:")
        total_moves = towers_of_hanoi(n, 'A', 'C', 'B')

        print(f"\nTotal moves executed: {total_moves}")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

if __name__ == "__main__":
    main()
