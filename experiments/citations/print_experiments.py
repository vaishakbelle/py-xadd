from __future__ import print_function

import argparse
import json

from os.path import dirname, basename

import numpy

from experiments.citations.citations import CitationExperiment, ExperimentRunner

attributes = [
    ("Run", lambda experiment, i: i),
    ("Size", lambda experiment, i: experiment.size),
    ("Copy Rate", lambda experiment, i: experiment.copy_rate),
    ("Links", lambda experiment, i: experiment.links),
    ("Density", lambda experiment, i: experiment.density),
    ("Damping Factor", lambda experiment, i: experiment.damping_factor),
    ("Tree Depth", lambda experiment, i: experiment.tree_depth),
    ("Leaf Cutoff Rate", lambda experiment, i: experiment.leaf_cutoff_rate),
    ("Positive", lambda experiment, i: experiment.positive),
    ("Accuracy Positive", lambda experiment, i: experiment.accuracy_positive),
    ("Negative", lambda experiment, i: experiment.negative),
    ("Accuracy Negative", lambda experiment, i: experiment.accuracy_negative),
    ("Kendall Tau (lifted-ground)", lambda experiment, i: experiment.kendall_tau),
    ("Kendall Tau (ground-verification)", lambda experiment, i: experiment.kt_ground_verification),
    ("Kendall Tau (lifted-verification)", lambda experiment, i: experiment.kt_lifted_verification),
    ("Kendall Tau (unseen, lifted-ground)", lambda experiment, i: experiment.unseen_kendall_tau_lifted_ground),
    ("Kendall Tau (unseen, ground-verification)", lambda experiment, i: experiment.unseen_kt_ground_verification),
    ("Kendall Tau (unseen, lifted-verification)", lambda experiment, i: experiment.unseen_kt_lifted_verification),
    ("Kendall Tau (constant-verification)", lambda experiment, i: experiment.constant_verification),
    ("Kendall Tau (random-verification)", lambda experiment, i: experiment.random_verification),
    ("Iterations", lambda experiment, i: experiment.iterations),
    ("Verification Iterations", lambda experiment, i: experiment.verification_iterations),
    ("Folds", lambda experiment, i: experiment.folds),
    ("Lifted Speed Learning", lambda experiment, i: experiment.lifted_speed_learning),
    ("Lifted Speed PageRank", lambda experiment, i: experiment.lifted_speed_pagerank),
    ("Lifted Speed Grounding", lambda experiment, i: experiment.lifted_speed_grounding),
    ("Lifted Speed", lambda experiment, i: experiment.lifted_speed),
    ("Ground Speed", lambda experiment, i: experiment.ground_speed),
    ("Top Count", lambda experiment, i: experiment.top_count),
    ("TI (seen ground-lifted)", lambda experiment, i: experiment.seen_top_inclusion_ground_lifted),
    ("TI (seen lifted-verification)", lambda experiment, i: experiment.seen_top_inclusion_lifted_verification),
    ("TI (seen ground-verification)", lambda experiment, i: experiment.seen_top_inclusion_ground_verification),
    ("TI (unseen ground-lifted)", lambda experiment, i: experiment.unseen_top_inclusion_ground_lifted),
    ("TI (unseen lifted-verification)", lambda experiment, i: experiment.unseen_top_inclusion_lifted_verification),
    ("TI (unseen ground-verification)", lambda experiment, i: experiment.unseen_top_inclusion_ground_verification),
    ("TI (unseen constant-verification)", lambda experiment, i: experiment.unseen_top_inclusion_constant_verification),
    ("TI (unseen random-verification)", lambda experiment, i: experiment.unseen_top_inclusion_random_verification),
    ("Top KT (seen ground-lifted)", lambda experiment, i: experiment.seen_top_kt_ground_lifted),
    ("Top KT (seen lifted-verification)", lambda experiment, i: experiment.seen_top_kt_lifted_verification),
    ("Top KT (seen ground-verification)", lambda experiment, i: experiment.seen_top_kt_ground_verification),
    ("Top KT (unseen ground-lifted)", lambda experiment, i: experiment.unseen_top_kt_ground_lifted),
    ("Top KT (unseen lifted-verification)", lambda experiment, i: experiment.unseen_top_kt_lifted_verification),
    ("Top KT (unseen ground-verification)", lambda experiment, i: experiment.unseen_top_kt_ground_verification),
    ("Top KT (unseen constant-verification)", lambda experiment, i: experiment.unseen_top_kt_constant_verification),
    ("Top KT (unseen random-verification)", lambda experiment, i: experiment.unseen_top_kt_random_verification),
    ("Learning sample count", lambda experiment, i: experiment.learning_sample_count),
]


def interleave(list1, list2):
    return [val for pair in zip(list1, list2) for val in pair]


def get_experiments_table(experiments, print_attributes=None):
    if print_attributes is None:
        print_attributes = attributes
    titles = [t[0] for t in print_attributes]
    titles = interleave(titles, ["std dev"] * len(titles))
    header = "\t".join(titles)
    rows = [header]
    for i in range(len(experiments)):
        experiment = experiments[i]
        values = [numpy.average(list(t[1](e, i) for e in experiment)) for t in print_attributes]
        deviation = [numpy.std(list(t[1](e, i) for e in experiment)) for t in print_attributes]
        values = interleave(values, deviation)
        rows.append("\t".join(str(value) for value in values))
    return "\n".join(rows) + "\n"


def print_experiments(experiments, print_attributes=None, filename=None):
    if filename is None:
        print(get_experiments_table(experiments, print_attributes))
    else:
        with open(filename, "w") as stream:
            print(get_experiments_table(experiments, print_attributes), file=stream)

if __name__ == "__main__":
    # p = argparse.ArgumentParser()
    # p.add_argument("file")
    # arguments = vars(p.parse_args())
    full_path = "log/temp_20170406_124735_c63b8c59-0c67-4cc7-8616-214dc6ac625d/output_20170406_124931.txt"  #arguments["file"]
    directory = dirname(full_path)
    output_file = basename(full_path)
    print(get_experiments_table(ExperimentRunner.load_experiments(directory, output_file).experiments))
