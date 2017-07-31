import pandas  as pd
import numpy as np
d = pd.DataFrame({"test":np.arange(1,10,1)})
d.to_csv("to.csv")
