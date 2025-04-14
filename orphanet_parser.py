import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

class OrphanetParser:
    def __init__(self, xml_path, json_path):
        self.xml_path = xml_path
        self.json_path = json_path
        self.disease_data = {}
        
    def parse_xml(self):
        """Parse Orphanet XML file"""
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            for disorder in root.findall('.//Disorder'):
                orpha_code = disorder.find('OrphaCode').text
                name = disorder.find('Name').text
                
                # Get disease information
                summary = disorder.find('.//Summary')
                summary_text = summary.text if summary is not None else "No summary available"
                
                # Get symptoms
                symptoms = []
                for symptom in disorder.findall('.//Symptom/Name'):
                    symptoms.append(symptom.text)
                
                # Get genes
                genes = []
                for gene in disorder.findall('.//Gene/Symbol'):
                    genes.append(gene.text)
                
                # Get diagnostic methods
                diagnostics = []
                for diag in disorder.findall('.//DiagnosticMethod/Name'):
                    diagnostics.append(diag.text)
                
                # Get treatments
                treatments = []
                for treatment in disorder.findall('.//Treatment/Name'):
                    treatments.append(treatment.text)
                
                # Store disease information
                self.disease_data[orpha_code] = {
                    'name': name,
                    'summary': summary_text,
                    'symptoms': symptoms,
                    'genes': genes,
                    'diagnostic_methods': diagnostics,
                    'treatments': treatments
                }
                
        except Exception as e:
            print(f"Error parsing XML file: {str(e)}")
    
    def parse_json(self):
        """Parse Orphanet JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
                for disorder in json_data.get('DisorderList', {}).get('Disorder', []):
                    orpha_code = str(disorder.get('OrphaCode'))
                    
                    if orpha_code in self.disease_data:
                        # Add additional information from JSON
                        self.disease_data[orpha_code].update({
                            'prevalence': disorder.get('Prevalence', 'Not specified'),
                            'age_of_onset': disorder.get('AgeOfOnset', 'Not specified'),
                            'inheritance': disorder.get('Inheritance', 'Not specified')
                        })
                        
        except Exception as e:
            print(f"Error parsing JSON file: {str(e)}")
    
    def get_disease_info(self, orpha_code):
        """Get comprehensive disease information"""
        return self.disease_data.get(str(orpha_code), {})
    
    def generate_disease_report(self, orpha_code):
        """Generate a detailed disease report"""
        disease_info = self.get_disease_info(orpha_code)
        if not disease_info:
            return "Disease information not found"
            
        report = f"""Disease Information Report
=======================

Disease Name: {disease_info.get('name', 'Not specified')}
OrphaCode: {orpha_code}

Summary:
{disease_info.get('summary', 'No summary available')}

Clinical Features:
{chr(10).join('- ' + symptom for symptom in disease_info.get('symptoms', []))}

Genetic Information:
{chr(10).join('- ' + gene for gene in disease_info.get('genes', []))}

Diagnostic Methods:
{chr(10).join('- ' + method for method in disease_info.get('diagnostic_methods', []))}

Available Treatments:
{chr(10).join('- ' + treatment for treatment in disease_info.get('treatments', []))}

Additional Information:
- Prevalence: {disease_info.get('prevalence', 'Not specified')}
- Age of Onset: {disease_info.get('age_of_onset', 'Not specified')}
- Inheritance: {disease_info.get('inheritance', 'Not specified')}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

def main():
    # Initialize parser with Orphanet files
    parser = OrphanetParser(
        xml_path='data/en_product1.xml',
        json_path='data/en_product1.json'
    )
    
    # Parse both files
    print("Parsing Orphanet XML file...")
    parser.parse_xml()
    print("Parsing Orphanet JSON file...")
    parser.parse_json()
    
    # Generate report for Fabry Disease (OrphaCode: 324)
    report = parser.generate_disease_report('324')
    
    # Save report
    os.makedirs('output', exist_ok=True)
    with open('output/orphanet_disease_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Disease report generated successfully!")

if __name__ == "__main__":
    main() 