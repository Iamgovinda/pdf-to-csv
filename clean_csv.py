# Select relevant columns
import re

import pandas as pd

df = pd.read_csv("output.csv", encoding="utf-8")
df = df[["MOT", "ANGLAIS", "filename"]]

# Add the 'WordType' column to store the extracted word type
df["WordType"] = None


# Function to split MOT column content
def split_mot_column(mot_text):
    # If mot_text is not a string, return empty strings
    if not isinstance(mot_text, str):
        return "", None

    # Regular expression to match text before and inside parentheses
    match = re.match(r"(.*?)(\((.*?)\))?$", mot_text.strip())  # Match text before and inside parentheses
    if match:
        before_paren = match.group(1).strip()  # Text before parentheses
        inside_paren = match.group(3) if match.group(3) else None  # Text inside parentheses
        return before_paren, inside_paren
    return mot_text, None  # In case no parentheses are found


# Apply the function to the 'MOT' column
df[['MOT', 'WordType']] = df['MOT'].apply(lambda x: pd.Series(split_mot_column(x)))
# Save the updated DataFrame to a new CSV file
df.to_csv('final_output.csv', index=False, header=True)

print("Data processed and saved successfully.")
