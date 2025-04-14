import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

class OrphanetParser:
    def __init__(self, xml_path, json_path):
        self.xml_path = xml_path
        self.json_path = json_path
        self.disease_data = {}
        print(f"Initializing OrphanetParser with XML: {xml_path} and JSON: {json_path}")
        if not os.path.exists(xml_path):
            print(f"Warning: XML file not found at {xml_path}")
        if not os.path.exists(json_path):
            print(f"Warning: JSON file not found at {json_path}")
        self.parse_xml()
        self.parse_json()

    def parse_xml(self):
        try:
            if not os.path.exists(self.xml_path):
                print(f"Error: XML file not found at {self.xml_path}")
                return
                
            print(f"Parsing XML file: {self.xml_path}")
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            for disorder in root.findall(".//Disorder"):
                try:
                    orpha_code = disorder.find("OrphaCode").text
                    name = disorder.find(".//Name[@lang='en']").text
                    
                    # Get summary if available
                    summary_node = disorder.find(".//TextSectionList/TextSection/Contents[@lang='en']")
                    summary = summary_node.text if summary_node is not None else ""
                    
                    self.disease_data[orpha_code] = {
                        'name': name,
                        'summary': summary,
                        'symptoms': [],
                        'genes': [],
                        'diagnostic_methods': [],
                        'treatments': []
                    }
                    
                    # Extract clinical signs
                    for sign in disorder.findall(".//ClinicalSign/Name[@lang='en']"):
                        if sign is not None and sign.text:
                            self.disease_data[orpha_code]['symptoms'].append(sign.text)
                    
                    # Extract genes
                    for gene in disorder.findall(".//Gene/Name"):
                        if gene is not None and gene.text:
                            self.disease_data[orpha_code]['genes'].append(gene.text)
                    
                    print(f"Processed disease: {name} (OrphaCode: {orpha_code})")
                except Exception as e:
                    print(f"Error processing disorder: {str(e)}")
                    continue
                
        except Exception as e:
            print(f"Error parsing XML file: {str(e)}")

    def parse_json(self):
        try:
            if not os.path.exists(self.json_path):
                print(f"Error: JSON file not found at {self.json_path}")
                return
                
            print(f"Parsing JSON file: {self.json_path}")
            with open(self.json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            for disorder in json_data.get('disorders', []):
                try:
                    orpha_code = str(disorder.get('orpha_code'))
                    if orpha_code in self.disease_data:
                        # Add prevalence
                        prevalence = disorder.get('prevalence', {}).get('name', 'Unknown')
                        self.disease_data[orpha_code]['prevalence'] = prevalence
                        
                        # Add age of onset
                        onset = disorder.get('age_of_onset', {}).get('name', 'Unknown')
                        self.disease_data[orpha_code]['age_of_onset'] = onset
                        
                        # Add inheritance
                        inheritance = disorder.get('inheritance', {}).get('name', 'Unknown')
                        self.disease_data[orpha_code]['inheritance'] = inheritance
                        
                        print(f"Updated disease info for OrphaCode: {orpha_code}")
                except Exception as e:
                    print(f"Error processing disorder in JSON: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error parsing JSON file: {str(e)}")

    def get_disease_info(self, orpha_code):
        orpha_code = str(orpha_code)
        if orpha_code not in self.disease_data:
            print(f"Warning: No information found for OrphaCode: {orpha_code}")
            return None
        return self.disease_data[orpha_code]

    def generate_disease_report(self, orpha_code):
        disease_info = self.get_disease_info(orpha_code)
        if not disease_info:
            return f"No information found for OrphaCode: {orpha_code}"
        
        report = f"Disease Report - {disease_info['name']} (OrphaCode: {orpha_code})\n"
        report += "=" * 80 + "\n\n"
        
        report += "Summary:\n"
        report += f"{disease_info['summary']}\n\n"
        
        report += "Clinical Features:\n"
        for symptom in disease_info['symptoms']:
            report += f"- {symptom}\n"
        report += "\n"
        
        report += "Additional Information:\n"
        report += f"- Prevalence: {disease_info.get('prevalence', 'Unknown')}\n"
        report += f"- Age of Onset: {disease_info.get('age_of_onset', 'Unknown')}\n"
        report += f"- Inheritance: {disease_info.get('inheritance', 'Unknown')}\n\n"
        
        if disease_info['genes']:
            report += "Associated Genes:\n"
            for gene in disease_info['genes']:
                report += f"- {gene}\n"
        
        report += f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        return report

if __name__ == "__main__":
    # Example usage
    parser = OrphanetParser("data/orphanet/en_product1.xml", "data/orphanet/en_product1.json")
    # Example: Generate report for Fabry Disease (OrphaCode: 324)
    report = parser.generate_disease_report("324")
    
    # Save report to file
    os.makedirs("output", exist_ok=True)
    with open("output/orphanet_disease_report.txt", "w", encoding='utf-8') as f:
        f.write(report)
    
    print("Report generated successfully!") 