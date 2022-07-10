import os
import matplotlib.pyplot as plt
import yaml
import numpy as np


resultsFilename = 'results.yaml'
requiredFields = ['accuracy', 'partitionNumber', 'totalNumberPartitions']
outputRoot = 'Output'

results = []
results_2 = []
for path, subdirs, files in os.walk(outputRoot):
    for name in files:
        if name == resultsFilename:
            res = yaml.safe_load(open(os.path.join(path, name)))
            result = (res['partitionNumber'],res['accuracy'])
            if "_100_2" in path:
                results_2.append(result)
            else:
                results.append(result)

print(list(sorted(results)))
print(list(sorted(results_2)))

xs = [x for (_,x),(_,y) in zip(sorted(results), sorted(results_2))]
ys = [y for (_, x), (_, y) in zip(sorted(results), sorted(results_2))]

r = np.corrcoef(xs, ys)
print(r)
plt.scatter(xs,ys)
plt.show()