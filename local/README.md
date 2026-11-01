# local/

A working space for connecting this DB to your own research. Nothing here except this README is
tracked by git, so what you put here stays on your machine.

The public DB records only facts that a source states. Anything that depends on your purpose
belongs here instead: which datasets you use and why, how you group licenses for your
experiments, how you map labels onto a common set, which recipes belong to your benchmark.

Join your files to the DB by `dataset_id` (the key of `data/datasets.csv`). The DB's tools and
validator never read this folder.
