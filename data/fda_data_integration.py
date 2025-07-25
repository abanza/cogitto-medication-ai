# data/fda_data_integration.py
# Generated FDA Medication Data for Cogitto
# This file contains real FDA medication data to replace your sample data

from datetime import datetime

# FDA Medications Data - Ready for Cogitto Integration
FDA_MEDICATIONS_DATA = [
    {
        "id": "acetaminophen",
        "generic_name": "acetaminophen",
        "brand_names": ['Pain Reliever Extra Strength'],
        "dosage_form": "unknown",
        "strength": "ACETAMINOPHEN strength varies",
        "prescription_required": True,
        "indications": ['pain', 'arthritis'],
        "warnings": ['Warnings Liver warning: This product contains acetaminophen'],
        "manufacturer": "Valu Merchandisers Company",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "2047428"
    },
    {
        "id": "ibuprofen",
        "generic_name": "ibuprofen",
        "brand_names": ['Ibuprofen Dye Free'],
        "dosage_form": "unknown",
        "strength": "IBUPROFEN strength varies",
        "prescription_required": True,
        "indications": ['pain', 'arthritis'],
        "warnings": ['Warnings Allergy alert: Ibuprofen may cause a severe allergic reaction, especially in people allergic to aspirin'],
        "manufacturer": "CVS Pharmacy",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "1100070"
    },
    {
        "id": "aspirin",
        "generic_name": "aspirin",
        "brand_names": ['Low Dose Aspirin Enteric Safety-Coated'],
        "dosage_form": "unknown",
        "strength": "ASPIRIN strength varies",
        "prescription_required": True,
        "indications": ['pain'],
        "warnings": ["Warnings Reye's syndrome : Children and teenagers who have or are recovering from chicken pox or flu-like symptoms should not use this product"],
        "manufacturer": "P & L Development, LLC",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "2047428"
    },
    {
        "id": "lisinopril_and_hydrochlorothiazide_tablets",
        "generic_name": "lisinopril and hydrochlorothiazide tablets",
        "brand_names": ['Lisinopril and Hydrochlorothiazide'],
        "dosage_form": "unknown",
        "strength": "HYDROCHLOROTHIAZIDE strength varies",
        "prescription_required": True,
        "indications": ['blood pressure', 'diabetes', 'heart'],
        "warnings": ['WARNING: FETAL TOXICITY When pregnancy is detected, discontinue lisinopril and hydrochlorothiazide tablets as soon as possible'],
        "manufacturer": "ST. MARY'S MEDICAL PARK PHARMACY",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "197885"
    },
    {
        "id": "sitagliptin_and_metformin_hydrochloride",
        "generic_name": "sitagliptin and metformin hydrochloride",
        "brand_names": ['ZITUVIMET'],
        "dosage_form": "unknown",
        "strength": "METFORMIN HYDROCHLORIDE strength varies",
        "prescription_required": True,
        "indications": ['diabetes'],
        "warnings": ['WARNING: LACTIC ACIDOSIS WARNING: LACTIC ACIDOSIS See full prescribing information for complete boxed warning', '5 WARNINGS AND PRECAUTIONS Lactic Acidosis: See boxed warning', '4 CONTRAINDICATIONS Severe renal impairment: (eGFR below 30 mL/min/1'],
        "manufacturer": "Zydus Lifesciences Limited",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "atorvastatin_calcium",
        "generic_name": "atorvastatin calcium",
        "brand_names": ['Atorvastatin calcium'],
        "dosage_form": "unknown",
        "strength": "ATORVASTATIN CALCIUM TRIHYDRATE strength varies",
        "prescription_required": True,
        "indications": ['diabetes', 'cholesterol', 'heart'],
        "warnings": ['4 CONTRAINDICATIONS Acute liver failure or decompensated cirrhosis [see Warnings and Precautions (5'],
        "manufacturer": "Bryant Ranch Prepack",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "amlodipine_besylate",
        "generic_name": "amlodipine besylate",
        "brand_names": ['Amlodipine Besylate'],
        "dosage_form": "unknown",
        "strength": "AMLODIPINE BESYLATE strength varies",
        "prescription_required": True,
        "indications": ['blood pressure', 'diabetes', 'heart'],
        "warnings": ['5 WARNINGS AND PRECAUTIONS Symptomatic hypotension is possible, particularly in patients with severe aortic stenosis', '4 CONTRAINDICATIONS Known sensitivity to amlodipine ( 4 ) Amlodipine besylate tablets are contraindicated in patients with known sensitivity to amlodipine'],
        "manufacturer": "Lupin Pharmaceuticals, Inc.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "metoprolol_tartrate",
        "generic_name": "metoprolol tartrate",
        "brand_names": ['Metoprolol Tartrate'],
        "dosage_form": "unknown",
        "strength": "METOPROLOL TARTRATE strength varies",
        "prescription_required": True,
        "indications": ['blood pressure', 'diabetes', 'heart'],
        "warnings": ['5 WARNINGS AND PRECAUTIONS Abrupt cessation may exacerbate myocardial ischemia'],
        "manufacturer": "PD-Rx Pharmaceuticals, Inc.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "2712152"
    },
    {
        "id": "omeprazole",
        "generic_name": "omeprazole",
        "brand_names": ['Omeprazole'],
        "dosage_form": "unknown",
        "strength": "OMEPRAZOLE strength varies",
        "prescription_required": True,
        "indications": ['heart'],
        "warnings": ['Warnings Allergy alert: do not use if you are allergic to omeprazole omeprazole may cause severe skin reactions'],
        "manufacturer": "Chain Drug Marketing Association INC",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "1291987"
    },
    {
        "id": "ezetimibe_and_simvastatin",
        "generic_name": "ezetimibe and simvastatin",
        "brand_names": ['Ezetimibe and Simvastatin'],
        "dosage_form": "unknown",
        "strength": "EZETIMIBE strength varies",
        "prescription_required": True,
        "indications": ['diabetes', 'cholesterol', 'heart'],
        "warnings": ['Follow healthcare provider instructions'],
        "manufacturer": "Actavis Pharma, Inc.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "losartan_potassium",
        "generic_name": "losartan potassium",
        "brand_names": ['Losartan Potassium'],
        "dosage_form": "unknown",
        "strength": "LOSARTAN POTASSIUM strength varies",
        "prescription_required": True,
        "indications": ['blood pressure', 'diabetes', 'heart'],
        "warnings": ['WARNING: FETAL TOXICITY When pregnancy is detected, discontinue losartan potassium as soon as possible', '5 WARNINGS AND PRECAUTIONS • Hypotension: Correct volume or salt depletion prior to administration of losartan potassium', '4 CONTRAINDICATIONS Losartan potassium is contraindicated: • In patients who are hypersensitive to any component of this product'],
        "manufacturer": "Cardinal Health 107, LLC",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "2709046"
    },
    {
        "id": "lisinopril_and_hydrochlorothiazide_tablets",
        "generic_name": "lisinopril and hydrochlorothiazide tablets",
        "brand_names": ['Lisinopril and Hydrochlorothiazide'],
        "dosage_form": "unknown",
        "strength": "HYDROCHLOROTHIAZIDE strength varies",
        "prescription_required": True,
        "indications": ['blood pressure', 'diabetes', 'heart'],
        "warnings": ['WARNING: FETAL TOXICITY When pregnancy is detected, discontinue lisinopril and hydrochlorothiazide tablets as soon as possible'],
        "manufacturer": "ST. MARY'S MEDICAL PARK PHARMACY",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "197885"
    },
    {
        "id": "gabapentin",
        "generic_name": "gabapentin",
        "brand_names": ['Gabapentin'],
        "dosage_form": "unknown",
        "strength": "GABAPENTIN strength varies",
        "prescription_required": True,
        "indications": ['seizure'],
        "warnings": ['5 WARNINGS AND PRECAUTIONS Drug Reaction with Eosinophilia and Systemic Symptoms (Multiorgan hypersensitivity): Discontinue if alternative etiology is not be established (5', '4 CONTRAINDICATIONS Gabapentin is contraindicated in patients who have demonstrated hypersensitivity to the drug or its ingredients'],
        "manufacturer": "Bryant Ranch Prepack",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "2398512"
    },
    {
        "id": "sertraline_hydrochloride",
        "generic_name": "sertraline hydrochloride",
        "brand_names": ['Sertraline Hydrochloride'],
        "dosage_form": "unknown",
        "strength": "SERTRALINE HYDROCHLORIDE strength varies",
        "prescription_required": True,
        "indications": ['pain', 'heart', 'anxiety'],
        "warnings": ['Follow healthcare provider instructions'],
        "manufacturer": "Proficient Rx LP",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "levothyroxine,_liothyronine",
        "generic_name": "levothyroxine, liothyronine",
        "brand_names": ['NP Thyroid 120'],
        "dosage_form": "unknown",
        "strength": "LEVOTHYROXINE strength varies",
        "prescription_required": True,
        "indications": ['cancer'],
        "warnings": ['Drugs with thyroid hormone activity, alone or together with other therapeutic agents, have been used for the treatment of obesity', 'WARNINGS Drugs with thyroid hormone activity, alone or together with other therapeutic agents, have been used for the treatment of obesity'],
        "manufacturer": "Acella Pharmaceuticals, LLC",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "amoxicillin",
        "generic_name": "amoxicillin",
        "brand_names": ['Amoxicillin'],
        "dosage_form": "unknown",
        "strength": "AMOXICILLIN strength varies",
        "prescription_required": True,
        "indications": ['infection'],
        "warnings": ['5 WARNINGS AND PRECAUTIONS Anaphylactic reactions: Serious and occasionally fatal anaphylactic reactions have been reported in patients on penicillin therapy', '4 CONTRAINDICATIONS Amoxicillin is contraindicated in patients who have experienced a serious hypersensitivity reaction (e'],
        "manufacturer": "Northwind Pharmaceuticals, LLC",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "1291987"
    },
    {
        "id": "prednisone",
        "generic_name": "prednisone",
        "brand_names": ['PredniSONE'],
        "dosage_form": "unknown",
        "strength": "PREDNISONE strength varies",
        "prescription_required": True,
        "indications": ['inflammation', 'cancer', 'arthritis', 'asthma'],
        "warnings": ['WARNINGS In patients on corticosteroid therapy subjected to unusual stress, increased dosage of rapidly acting corticosteroids before, during, and after the stressful situation is indicated', 'CONTRAINDICATIONS Systemic fungal infections and known hypersensitivity to components'],
        "manufacturer": "A-S Medication Solutions",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "763179"
    },
    {
        "id": "tramadol_hydrochloride",
        "generic_name": "tramadol hydrochloride",
        "brand_names": ['TRAMADOL HYDROCHLORIDE'],
        "dosage_form": "unknown",
        "strength": "TRAMADOL HYDROCHLORIDE strength varies",
        "prescription_required": True,
        "indications": ['pain'],
        "warnings": ['4 CONTRAINDICATIONS Tramadol hydrochloride extended-release tablets are contraindicated for: all children younger than 12 years of age [see Warnings and Precautions (5'],
        "manufacturer": "Sun Pharmaceutical Industries, Inc.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "1148482"
    },
    {
        "id": "ciprofloxacin",
        "generic_name": "ciprofloxacin",
        "brand_names": ['ciprofloxacin'],
        "dosage_form": "unknown",
        "strength": "CIPROFLOXACIN HYDROCHLORIDE strength varies",
        "prescription_required": True,
        "indications": ['infection'],
        "warnings": ['WARNINGS NOT FOR INJECTION INTO THE EYE', 'CONTRAINDICATIONS A history of hypersensitivity to ciprofloxacin or any other component of the medication is a contraindication to its use'],
        "manufacturer": "A-S Medication Solutions",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "103943"
    },
    {
        "id": "warfarin_sodium",
        "generic_name": "warfarin sodium",
        "brand_names": ['Warfarin Sodium'],
        "dosage_form": "unknown",
        "strength": "WARFARIN SODIUM strength varies",
        "prescription_required": True,
        "indications": ['as prescribed by healthcare provider'],
        "warnings": ['WARNING: BLEEDING RISK Warfarin sodium can cause major or fatal bleeding [see Warnings and Precautions ( 5', '5 WARNINGS AND PRECAUTIONS Tissue necrosis: Necrosis or gangrene of skin or other tissues can occur, with severe cases requiring debridement or amputation'],
        "manufacturer": "Teva Pharmaceuticals USA, Inc.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "855290"
    },
    {
        "id": "furosemide",
        "generic_name": "furosemide",
        "brand_names": ['Furosemide'],
        "dosage_form": "unknown",
        "strength": "FUROSEMIDE strength varies",
        "prescription_required": True,
        "indications": ['heart'],
        "warnings": ['WARNING Furosemide is a potent diuretic which, if given in excessive amounts, can lead to a profound diuresis with water and electrolyte depletion', 'CONTRAINDICATIONS Furosemide tablets are contraindicated in patients with anuria and in patients with a history of hypersensitivity to furosemide'],
        "manufacturer": "Bryant Ranch Prepack",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "1112201"
    },
    {
        "id": "pantoprazole_sodium",
        "generic_name": "pantoprazole sodium",
        "brand_names": ['Pantoprazole Sodium'],
        "dosage_form": "unknown",
        "strength": "PANTOPRAZOLE SODIUM strength varies",
        "prescription_required": True,
        "indications": ['as prescribed by healthcare provider'],
        "warnings": ['5 WARNINGS AND PRECAUTIONS Gastric Malignancy : In adults, symptomatic response to therapy with pantoprazole sodium does not preclude the presence of gastric malignancy', '4 CONTRAINDICATIONS Pantoprazole sodium is contraindicated in patients with known hypersensitivity reactions including anaphylaxis to the formulation or any substituted benzimidazole'],
        "manufacturer": "Meitheal Pharmaceuticals Inc.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "escitalopram_oral",
        "generic_name": "escitalopram oral",
        "brand_names": ['Escitalopram Oral Solution'],
        "dosage_form": "unknown",
        "strength": "ESCITALOPRAM OXALATE strength varies",
        "prescription_required": True,
        "indications": ['anxiety'],
        "warnings": ['WARNING: SUICIDAL THOUGHTS AND BEHAVIORS Antidepressants increased the risk of suicidal thoughts and behaviors in pediatric and young adult patients in short-term studies', '5 WARNINGS AND PRECAUTIONS Serotonin Syndrome: Increased risk when co-administered with other serotonergic agents, but also when taken alone'],
        "manufacturer": "Chartwell RX, LLC",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "montelukast_sodium",
        "generic_name": "montelukast sodium",
        "brand_names": ['Montelukast Sodium'],
        "dosage_form": "unknown",
        "strength": "MONTELUKAST SODIUM strength varies",
        "prescription_required": True,
        "indications": ['asthma'],
        "warnings": ['5', '4'],
        "manufacturer": "Proficient Rx LP",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": ""
    },
    {
        "id": "bupropion_hydrochloride",
        "generic_name": "bupropion hydrochloride",
        "brand_names": ['Bupropion Hydrochloride XL'],
        "dosage_form": "unknown",
        "strength": "BUPROPION HYDROCHLORIDE strength varies",
        "prescription_required": True,
        "indications": ['as prescribed by healthcare provider'],
        "warnings": ['4 CONTRAINDICATIONS Bupropion hydrochloride extended-release tablets (XL) are contraindicated in patients with seizure disorder'],
        "manufacturer": "REMEDYREPACK INC.",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "1232591"
    },
]

# FDA Drug Interactions Data
FDA_INTERACTIONS = {
}


# Integration Instructions:
# 1. Replace MEDICATIONS_DATA in your app.py with FDA_MEDICATIONS_DATA
# 2. Replace INTERACTIONS with FDA_INTERACTIONS  
# 3. Update any ID references to use the new format
# 4. Test your endpoints to ensure compatibility

# Example usage:
# MEDICATIONS = [Medication(**med) for med in FDA_MEDICATIONS_DATA]

print(f"🏥 FDA Data loaded: {len(FDA_MEDICATIONS_DATA)} medications, {len(FDA_INTERACTIONS)} interactions")
