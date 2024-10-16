import pandas as pd
from ydata_profiling import ProfileReport

df = pd.read_csv("navigator2022.csv", sep=";", encoding='ISO-8859-1')

profile = ProfileReport(df, title="Pandas Profiling Report")

# profile.to_file("navigator2022_report.html")
profile.to_file("report.json")
