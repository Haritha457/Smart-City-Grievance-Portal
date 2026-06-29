import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle

# Load dataset
data = pd.read_csv("complaint_dataset.csv")

# Features and labels
X = data["complaint"]
y = data["category"]

# Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB())
])

# Train model
model.fit(X, y)

# Save model
with open("model/complaint_classifier.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model trained successfully!")