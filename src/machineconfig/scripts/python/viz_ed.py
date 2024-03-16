
def visualize_dict_items(container_dict, capacity_dict):
    for container, items in container_dict.items():
        item_count = len(items)
        print(f"{container:10}: {'#' * item_count}", end="")
        remaining_capacity = capacity_dict[container] - item_count
        print(f"{'-' * remaining_capacity}")
container_dict = {
    "Box": ["Apple", "Banana", "Cherry"],
    "Bag": ["Notebook", "Pen", "Eraser", "Ruler"],
    "Cupboard": ["Plate", "Cup", "Bowl"]
}

capacity_dict = {
    "Box": 5,
    "Bag": 6,
    "Cupboard": 10
}

visualize_dict_items(container_dict, capacity_dict)