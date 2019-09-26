import os
import csv
import argparse

def main(params):

    splits = ['train', 'test']
    path_dict = {s: [os.path.join(params.dirpath, f) for f in os.listdir(params.dirpath) if s in f] for s in splits}

    for s in splits:
        fp_list = [open(f, 'rb') for f in path_dict[s]]
        contents = [fp.read().decode('utf-8', errors='ignore').lower() for fp in fp_list]
        contents = [c.split('\n') for c in contents]
        [fp.close() for fp in fp_list]

        # eliminating corrupted lines
        num_files = len(contents)
        num_lines = len(contents[0])
        assert all(len(contents[i]) == num_lines for i in range(num_files))

        for j in reversed(range(num_lines)):
            if any(contents[i][j] == '' or contents[i][j] == ' ' for i in range(num_files)):
                print('Deleting empty line [{}] from {}'.format(j, path_dict[s]))
                [contents[i].pop(j) for i in range(num_files)]

        num_lines = len(contents[0])
        assert all(len(contents[i]) == num_lines for i in range(num_files))
        contents = ['\n'.join(c) for c in contents]
        fp_list = [open(f, 'w') for f in path_dict[s]]
        [fp.write(contents[i]) for i, fp in enumerate(fp_list)]
        [fp.close() for fp in fp_list]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Preprocess ROC Stories dataser")
    parser.add_argument("--dirpath", type=str, default='cmdc', help='Path to ROC Stories dir containing two csv files')
    params = parser.parse_args()
    main(params)