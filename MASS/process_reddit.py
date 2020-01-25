import os
import argparse



if __name__ == '__main__':

    separator = '|||||'
    parser = argparse.ArgumentParser(description="Generate internal experimet")
    parser.add_argument("--input_dir", type=str, default='reddit_dialog', help='')
    params = parser.parse_args()
    names = ['train', 'val', 'test']

    in_path = {s: os.path.join(params.input_dir, '{}_reddit.txt'.format(s)) for s in names}
    out_path = {s: [os.path.join(params.input_dir, '{}.context.txt'.format(s)), os.path.join(params.input_dir, '{}.resp.txt'.format(s))] for s in names}
    for name in names:
        with open(in_path[name]) as f:
            lines = f.readlines()
        lines = [l.replace('\n', '').split(separator) for l in lines]
        lines = [l for l in lines if len(l) == 2]
        context_lens = [len([e for e in l[0].split(' ') if e != '']) for l in lines]
        resp_lens = [len([e for e in l[1].split(' ') if e != '']) for l in lines]
        filter_in_list = list(range(8, 12+1))
        filtered_lines = [l for l, c, r in zip(lines, context_lens, resp_lens) if c in filter_in_list and r > 3]

        analyze = False
        if analyze:
            import matplotlib.pyplot as plt
            hist, _, _ = plt.hist(context_lens, bins=max(context_lens))

        for type_i in range(2):
            with open(out_path[name][type_i], 'w') as f:
                n_lines = len(filtered_lines) if name == 'train' else min(len(filtered_lines), 1000)
                for line_i in range(n_lines):
                    f.write(filtered_lines[line_i][type_i] + '\n')