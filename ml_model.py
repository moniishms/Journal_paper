import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)

# Load dataset generated earlier
df = pd.read_csv("dataset.csv")

# Quick check of the Sm distribution before training
print(df["Sm"].describe())
print(df.groupby("label")["Sm"].describe())

# Features and labels
X = df[["Cm", "Sm", "hop"]]
y = df["label"]

# Train test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Decision Tree Model
model = DecisionTreeClassifier(
    criterion="gini",
    max_depth=5,
    min_samples_leaf=8,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Save trained model for use in the scheduler simulation
joblib.dump(model, "resqmesh_dt_model.pkl")

# Predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)
auc_score = roc_auc_score(y_test, y_prob[:, 1])

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("Confusion Matrix:\n", cm)
print("ROC AUC Score:", auc_score)

# Feature importances
print("Feature importances (Cm, Sm, hop):", model.feature_importances_)

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_prob[:, 1])

plt.figure(figsize=(6, 6))
plt.plot(fpr, tpr, color='blue', linewidth=2,
         label=f'ROC Curve (AUC = {auc_score:.3f})')
plt.plot([0, 1], [0, 1], color='red', linestyle='--',
         label='Random Classifier')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Receiver Operating Characteristic (ROC) Curve")
plt.legend(loc="lower right")
plt.grid(True)
plt.show()