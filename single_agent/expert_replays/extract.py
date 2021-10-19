import pandas.io.clipboard

with open ("list.txt", "r") as file:
  input_lines = file.readlines()

output_lines = []

for i in range(len(input_lines)):
  if input_lines[i].find('-episode-') < 0:
    continue

  text = input_lines[i]

  text = text[text.find('-episode-') + 9:]
  text = text[:text.find('"')]

  output_lines.append(text)

pandas.io.clipboard.copy('\n'.join(output_lines))