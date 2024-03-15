# $ pip install h5py
# $ pip install --no-cache-dir h5py

import h5py
import numpy as np
import matplotlib.pyplot as plt

filename = "data_test_1_13032024.h5"

def h5_tree(val, pre=''):
    items = len(val)
    for key, val in val.items():
        items -= 1
        if items == 0:
            # the last item
            if type(val) == h5py._hl.group.Group:
                print(pre + '└── ' + key)
                h5_tree(val, pre+'    ')
            else:
                print(pre + '└── ' + key + ' (%d)' % len(val))
        else:
            if type(val) == h5py._hl.group.Group:
                print(pre + '├── ' + key)
                h5_tree(val, pre+'│   ')
            else:
                print(pre + '├── ' + key + ' (%d)' % len(val))


with h5py.File(filename, "r") as f:

    print(h5_tree(f))

    # Print all root level object names (aka keys) # these can be group or dataset names 
    print("Root level objects (keys): %s" % f.keys())
    print('     type :', type(f.keys()))

    # get first object name/key; may or may NOT be a group
    root_key0 = list(f.keys())[0]
    root_key00 = f.get('RawData/Detector000/Data0D/CH00/Data00') # == f['RawData/Detector000/Data0D/CH00/Data00'][()]
    print("\\.%s" % root_key0)
    print('     type :', type(root_key0)) # type for first_groupe_key: usually group or dataset
    print("\\.%s" % root_key00)
    print('     type :', type(root_key00)) # type for first_groupe_key: usually group or dataset

    Data00_array = np.array(f.get('RawData/Detector000/Data0D/CH00/Data00'))
    print("Data00_array:", Data00_array)
    Data01_array = np.array(f.get('RawData/Detector000/Data0D/CH00/Data01'))
    print("Data01_array:", Data01_array)

    # x_axis = Data00_array[0]
    # y_axis = Data00_array[1]
    # print('x_axis: ', x_axis)

    # plt.rcParams["figure.figsize"] = [7.50, 3.50]
    # plt.rcParams["figure.autolayout"] = True

    # plt.title("Line graph")
    # plt.plot(x_axis, y_axis, color="red")

    # plt.show()