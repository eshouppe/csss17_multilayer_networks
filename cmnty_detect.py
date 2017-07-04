"""
Steps:
- Replace fillna 0 with x
- Use prediction accuracy on all layers to select K
- Run multitensor on all site pairs
- Create mask in update functions to only use intersection in denominator
- Calculate uwv product for each pair
- Compare expected value to actual edge weight using Cat penalty code
- Detect assortativeness by layer with rotation
"""
import os
import re

import pandas as pd
import numpy as np


def calculate_directed_AUC(exp_act_ew_dict):
    """Calculate area under the ROC curve. Ideal is for ordering of expected edge weights
    to match to ordering of actual edge weights."""
    pass

#
def select_k():
    """Select global parameter k, which is number of communities
    MultiTensor divides the network layers into. Use 80% of all
    edges to predict remaining edges. Pick k with max accuracy.
    Steps:
    - Input AllSites_adjacency.dat to MultiTensor main.py
    - Confirm dimensions of 3 outputted matrices u, v, w
    - Get product of u * w * v.  Output matrix should be size N * N * L
    - Compare E(edge weight) with actual with AUC calculation
    - Put those steps in a loop for multiple values of k
    - Select k with highest prediction accuracy
    """
    #python main.py -a="AllSites_adjacency.dat" -f="all_layer_adjacency" -l=14 -k=2
    checked_ks = []

    for file_name in os.listdir(ALL_ADJ_DIR):
        if file_name.split('_')[0] in ['u', 'v', 'w']:
            this_k = re.findall(r'\d+', file_name)[0]
            if this_k not in checked_ks:
                checked_ks.append(this_k)
                # Read u matrix file to a dataframe and then convert to np array
                u_df = pd.read_table(os.path.join(ALL_ADJ_DIR, 'u_K'+this_k+'.dat'),
                                     delim_whitespace=True, skiprows=[0],
                                     header=None, index_col=0)
                u_mat = np.asarray(u_df.values)

                # Read v matrix file to a dataframe and then convert to np array
                v_df = pd.read_table(os.path.join(ALL_ADJ_DIR, 'v_K'+this_k+'.dat'),
                                     delim_whitespace=True, skiprows=[0],
                                     header=None, index_col=0)
                v_mat = np.asarray(v_df.values)

                # Create placeholder 3d tensor. Read thru file and build tensor out
                w_mat = np.zeros((int(this_k), int(this_k), 14))
                with open(os.path.join(ALL_ADJ_DIR, 'w_K'+this_k+'.dat'), 'r') as infile:
                    infile.readline() #Skip info on first row
                    flag = 0
                    for line in infile:
                        if "layer" in line:
                            this_layer = int(re.findall(r'\d+', line)[0])
                            flag = 1
                            continue
                        if flag == 1:
                            layer1_array = np.asarray(line.split(" "), dtype=np.float64)
                            flag = 2
                            continue
                        if flag == 2:
                            layer2_array = np.asarray(line.split(" "), dtype=np.float64)
                            w_mat[:, :, this_layer] = np.asarray((layer1_array, layer2_array))
                            flag = 0
                
                print "U shape:", np.shape(u_mat), "V shape:", np.shape(v_mat), "W shape:", np.shape(w_mat)

                # Matrix multiple u and each layer of w and v. Product shape is N x N x L
                expect_edg_wght = np.zeros((np.shape(u_mat)[0], np.shape(u_mat)[0], 14))
                for lyr in range(14):
                    u_dot_w = np.mat(u_mat) * np.mat(w_mat[:, :, lyr])
                    expect_edg_wght[:, :, lyr] = u_dot_w * np.mat(v_mat.T)
                
                # Ordered node names to use in comparison
                node_names = list(v_df.index)

                col_names = ["Pollinator", "Plant"] + ["L"+l for l in range(1, 15)]
                actual_edg_wght_df = pd.read_table(os.path.join(ALL_ADJ_DIR, 'AllSites_holdout.dat'),
                                                   delim_whitespace=True,
                                                   header=None, index_col=False,
                                                   names=col_names, usecols=[1:])

                
                # Build list of tuples of (expected_ew, actual_ew) for AUC calculation
                exp_act = {lyr: [] for lyr in range(1, 15)}

                for row in actual_edg_wght_df.itertuples():
                    pol_idx = node_names.index(row[1])
                    plt_idx = node_names.index(row[2])
                    for idx, act_edg_wght in enumerate(row[3:]):
                        expected_ew = expect_edg_wght[pol_idx, plt_idx, idx]
                        # Add tuple to correct layer
                        exp_act[idx+1].append((expected_ew, act_edg_wght))
                
                calc_auc = calculate_directed_AUC(exp_act)




if __name__ == "__main__":
    ALL_ADJ_DIR = os.path.join("data", "all_layer_adjacency")
    # AllSites_holdout.dat
    select_k()
