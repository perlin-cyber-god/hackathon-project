# flawed_code.py
import math

global_counter = 0

def calculate_something(x, y):
    """
    This function has a missing docstring (oops, I fixed it here for clarity but it'd be missing in the flawed example)
    It calculates the hypotenuse.
    """
    temp = 0 # Unused variable
    result = math.sqrt(x**2 + y**2)
    return result

def process_data(data_list, z):
    global global_counter
    new_data = []
    for item in data_list:
        if item > z:
            if item % 2 == 0:
                new_data.append(item * 2)
            else:
                new_data.append(item * 3)
        elif item == z:
            new_data.append(item + 5)
        else:
            if item < 0:
                new_data.append(abs(item))
            else:
                new_data.append(item / 2)
        global_counter += 1 # Modifying a global directly
    return new_data

class MyClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value # Missing docstring and 'self' not used
    
def main():
    data = [1, 5, -2, 8, 3]
    threshold = 3
    processed = process_data(data, threshold)
    print(f"Processed data: {processed}")
    
    hypotenuse = calculate_something(3, 4)
    print(f"Hypotenuse: {hypotenuse}")
    
    obj = MyClass(10)
    print(f"Object value: {obj.get_value()}")
    
if __name__ == "__main__":
    main()
