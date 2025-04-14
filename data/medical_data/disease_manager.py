import json
import os
from datetime import datetime

class DiseaseManager:
    def __init__(self, database_path):
        self.database_path = database_path
        self.disease_data = self._load_database()
    
    def _load_database(self):
        """Load the disease database from JSON file"""
        try:
            if os.path.exists(self.database_path):
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"diseases": {}, "metadata": {
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "version": "1.0",
                    "source": "Orphanet Database",
                    "update_frequency": "Monthly"
                }}
        except Exception as e:
            print(f"Error loading database: {str(e)}")
            return {"diseases": {}, "metadata": {}}
    
    def save_database(self):
        """Save the disease database to JSON file"""
        try:
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.disease_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving database: {str(e)}")
            return False
    
    def get_disease_info(self, orpha_code):
        """Get information for a specific disease"""
        return self.disease_data.get("diseases", {}).get(str(orpha_code), {})
    
    def update_disease_info(self, orpha_code, info):
        """Update information for a specific disease"""
        if "diseases" not in self.disease_data:
            self.disease_data["diseases"] = {}
        
        self.disease_data["diseases"][str(orpha_code)] = info
        self.disease_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        return self.save_database()
    
    def add_disease(self, orpha_code, name, summary, symptoms, genes, 
                   diagnostic_methods, treatments, prevalence, age_of_onset, 
                   inheritance, medical_priority, monitoring_frequency, 
                   critical_organs, emergency_protocol):
        """Add a new disease to the database"""
        disease_info = {
            "name": name,
            "orpha_code": orpha_code,
            "summary": summary,
            "symptoms": symptoms,
            "genes": genes,
            "diagnostic_methods": diagnostic_methods,
            "treatments": treatments,
            "prevalence": prevalence,
            "age_of_onset": age_of_onset,
            "inheritance": inheritance,
            "medical_priority": medical_priority,
            "monitoring_frequency": monitoring_frequency,
            "critical_organs": critical_organs,
            "emergency_protocol": emergency_protocol
        }
        return self.update_disease_info(orpha_code, disease_info)
    
    def get_all_diseases(self):
        """Get information for all diseases"""
        return self.disease_data.get("diseases", {})
    
    def search_diseases(self, query):
        """Search diseases by name, symptoms, or genes"""
        results = []
        query = query.lower()
        
        for orpha_code, disease in self.disease_data.get("diseases", {}).items():
            if (query in disease.get("name", "").lower() or
                any(query in symptom.lower() for symptom in disease.get("symptoms", [])) or
                any(query in gene.lower() for gene in disease.get("genes", []))):
                results.append(disease)
        
        return results
    
    def get_emergency_protocol(self, orpha_code):
        """Get emergency protocol for a specific disease"""
        disease = self.get_disease_info(orpha_code)
        return disease.get("emergency_protocol", {})
    
    def get_critical_organs(self, orpha_code):
        """Get critical organs for a specific disease"""
        disease = self.get_disease_info(orpha_code)
        return disease.get("critical_organs", [])
    
    def get_monitoring_schedule(self, orpha_code):
        """Get monitoring schedule for a specific disease"""
        disease = self.get_disease_info(orpha_code)
        return {
            "frequency": disease.get("monitoring_frequency", "Not specified"),
            "organs": disease.get("critical_organs", []),
            "priority": disease.get("medical_priority", "Not specified")
        }

def main():
    # Example usage
    db_path = os.path.join(os.path.dirname(__file__), "disease_database.json")
    manager = DiseaseManager(db_path)
    
    # Example: Get Fabry Disease information
    fabry_info = manager.get_disease_info("324")
    print("Fabry Disease Information:")
    print(json.dumps(fabry_info, indent=2))
    
    # Example: Search for diseases with specific symptoms
    results = manager.search_diseases("kidney")
    print("\nDiseases with kidney-related symptoms:")
    for disease in results:
        print(f"- {disease['name']} (OrphaCode: {disease['orpha_code']})")

if __name__ == "__main__":
    main() 