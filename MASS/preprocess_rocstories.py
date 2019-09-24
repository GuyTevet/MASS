import os
import csv
import argparse

def main(params):

    csv_list = [os.path.join(params.dirpath, f) for f in os.listdir(params.dirpath) if f.endswith('.csv')]
    assert len(csv_list) == 2 # 2017 & 2016 datasets
    fp_in = [open(path, 'r') for path in csv_list]
    fp_out = {'{}-{}'.format(_set, _part): open(os.path.join(params.dirpath, '{}.{}.txt'.format(_set, _part)), 'w')
              for _set, _part in zip(['train', 'valid', 'test'] * 2, ['story'] * 3 + ['end'] *3 )}
    num_lines = sum(sum(1 for row in fp) - 1 for fp in fp_in) # substracting headlines
    [fp.seek(0) for fp in fp_in]
    num_valid_test_lines = int(num_lines * 0.05)
    num_train_lines = num_lines - (num_valid_test_lines * 2)
    row_i = 0
    cur_set = 'train'

    for fp in fp_in:
        reader = csv.DictReader(fp)
        for row in reader:
            fp_out['{}-story'.format(cur_set)].write('{}. {} {} {} {}\n'.format(row['storytitle'], row['sentence1'], row['sentence2'], row['sentence3'], row['sentence4']))
            fp_out['{}-end'.format(cur_set)].write('{}\n'.format(row['sentence5']))

            row_i +=1
            if row_i < num_train_lines:
                cur_set = 'train'
            elif row_i < num_train_lines + num_valid_test_lines:
                cur_set = 'valid'
            else:
                cur_set = 'test'


    [fp.close() for fp in fp_in]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Preprocess ROC Stories dataser")
    parser.add_argument("--dirpath", type=str, default='ROCStories', help='Path to ROC Stories dir containing two csv files')
    params = parser.parse_args()
    main(params)

