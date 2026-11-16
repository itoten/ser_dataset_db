# local/

A working space for connecting this DB to your own research. It is not part of the DB: git ignores
new files here, so what you put here stays on your machine unless you add it with `git add -f`.

In this repository the project maintainer's own files here (dataset choices, filtering configs and
outputs, license groupings, analysis scripts) are tracked on purpose and therefore public. This is
to be reviewed before the DB is promoted for public use. Removing them later does not remove them
from the git history.

The public DB records only facts that a source states. Anything that depends on your purpose
belongs here instead: which datasets you use and why, how you group licenses for your
experiments, how you map labels onto a common set, which recipes belong to your benchmark.

Join your files to the DB by `dataset_id` (the key of `data/datasets.csv`). The DB's tools and
validator never read this folder.
