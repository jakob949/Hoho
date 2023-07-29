import numpy as np
from sklearn.model_selection import StratifiedKFold

# Read labels and features from file
def read_data(filename):
    labels = []
    features = []
    with open(filename, 'r') as f:
        for line in f:
            label, feature = line.split(':', 1)
            labels.append(label)
            features.append(feature)
    return np.array(labels), np.array(features)

# Create stratified splits
def create_splits(labels, features, n_splits):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=1)
    splits = list(skf.split(features, labels))
    split_dict = {}
    for i, (train_index, test_index) in enumerate(splits):
        split_dict[f"split_{i+1}"] = {
            "train": {"labels": labels[train_index].tolist(), "features": features[train_index].tolist()},
            "test": {"labels": labels[test_index].tolist(), "features": features[test_index].tolist()},
        }
    return split_dict

# Write splits to files
def write_splits_to_file(splits, base_file_path):
    for i, split in enumerate(splits, 1):
        for subset in ['train', 'test']:
            with open(f"{base_file_path}_split{i}_{subset}.txt", 'w') as f:
                for label, feature in zip(split[subset]['labels'], split[subset]['features']):
                    f.write(f"{label}:{feature}")
        break

# Main function
def main():
    filename = "dataset_large_US_tech_rounded.txt"
    base_file_path = "dataset_large_US_tech"
    n_splits = 4
    labels, features = read_data(filename)
    splits = create_splits(labels, features, n_splits)
    write_splits_to_file(splits.values(), base_file_path)

if __name__ == "__main__":
    main()
