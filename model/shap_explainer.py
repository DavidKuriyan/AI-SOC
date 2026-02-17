import shap
import pickle
import numpy as np
import matplotlib.pyplot as plt
import os

# Initialise SHAP - this might be resource intensive so we do it on demand or load a small background dataset
# For the purpose of this lightweight app, we will load the model and initialize the explainer when needed or at startup.

MODEL_PATH = os.path.join("model", "soc_model.pkl")
SHAP_PLOT_DIR = os.path.join("static", "shap_plots")
os.makedirs(SHAP_PLOT_DIR, exist_ok=True)

class SOCExplainer:
    def __init__(self):
        self.model = None
        self.explainer = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(MODEL_PATH):
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                
                # We need some background data for the TreeExplainer to be most effective, 
                # but for Tree models it's often optional or we can use a summary.
                # For this prototype, we'll initialize it without background data or zero out some background.
                if self.model:
                     self.explainer = shap.TreeExplainer(self.model)
            else:
                print("⚠️ Model not found at", MODEL_PATH)
        except Exception as e:
            print(f"❌ Error loading model for SHAP: {e}")

    def generate_explanation(self, feature_vector, alert_id):
        """
        Generate a SHAP force plot or summary plot for a single instance.
        Saves the plot to static/shap_plots/{alert_id}.png
        """
        if not self.explainer:
            return None

        try:
            # SHAP values for this specific instance
            shap_values = self.explainer.shap_values(np.array([feature_vector]))
            
            # For multi-class, shap_values is a list of arrays (one for each class).
            # We usually care about the predicted class or the 'Malicious' class.
            # Assuming binary or we pick the max class.
            
            # If binary, shap_values might be just one array or list of two.
            # Let's assume prediction is the index of interest.
            prediction = self.model.predict([feature_vector])[0]
            # Map label string to index if necessary. 
            # Our model returns strings ('normal', 'ddos', etc.).
            # sklearn classes_ attribute holds the order.
            class_idx = np.where(self.model.classes_ == prediction)[0][0]
            
            vals = shap_values[class_idx][0] if isinstance(shap_values, list) else shap_values[0]
            
            # Feature Names
            feature_names = ["Failed Logins", "Packet Size", "Duration", "Port", "Internal IP"]
            
            plt.figure(figsize=(10, 6))
            # Summary plot for just one sample is a bar plot essentially
            # We can use waterflow or bar
            shap.plots.bar(
                shap.Explanation(
                    values=vals, 
                    base_values=self.explainer.expected_value[class_idx], 
                    data=feature_vector, 
                    feature_names=feature_names
                ),
                show=False
            )
            
            output_path = os.path.join(SHAP_PLOT_DIR, f"shap_{alert_id}.png")
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            
            return f"shap_plots/shap_{alert_id}.png"
            
        except Exception as e:
            print(f"❌ Error generating SHAP plot: {e}")
            return None
