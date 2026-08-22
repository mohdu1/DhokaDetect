import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

print("Loading Dataset...")
df = pd.read_csv('upi_transactions_2024.csv') # Adjust path if your CSV is elsewhere

# Drop columns we don't need for ML
df_ml = df.drop(columns=['transaction id', 'timestamp'])

# Encode text columns into numbers
categorical_cols = df_ml.select_dtypes(include=['object']).columns
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df_ml[col] = le.fit_transform(df_ml[col])
    label_encoders[col] = le

X = df_ml.drop('fraud_flag', axis=1)
y = df_ml['fraud_flag']

print("Training Random Forest Classifier...")
# We use class_weight='balanced' because there are very few fraud cases in the CSV
clf = RandomForestClassifier(n_estimators=50, max_depth=10, class_weight='balanced', random_state=42)
clf.fit(X, y)

print("Saving Model Weights...")
joblib.dump(clf, 'behavioral_model.pkl')
joblib.dump(label_encoders, 'behavioral_encoders.pkl')
print("Training Complete! The behavioral engine is ready.")