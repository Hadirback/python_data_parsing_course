import re


story_info = "Газета.Ru 15:37"
time = re.findall("\d{2}\:\d{2}$", story_info)[0]
print(time)