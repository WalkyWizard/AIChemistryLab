import csv
import os


class CompoundManager:
    def __init__(self, predictor):
        self.predictor = predictor
        self.compounds = []
        self._init_default_compounds()

    def _init_default_compounds(self):
        dataset = [
            ('Етанол', 'C2H6O', 'CCO'),
            ('Оцтова кислота', 'C2H4O2', 'CC(=O)O'),
            ('Бензен', 'C6H6', 'C1=CC=CC=C1'),
            ('Аспірин', 'C9H8O4', 'CC(=O)Oc1ccccc1C(=O)O'),
            ('Парацетамол', 'C8H9NO2', 'CC(=O)Nc1ccc(O)cc1'),
            ('Кофеїн', 'C8H10N4O2', 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C'),
            ('Ібупрофен', 'C13H18O2', 'CC(C)Cc1ccc(cc1)C(C)C(=O)O'),
            ('Ацетон', 'C3H6O', 'CC(=O)C'),
            ('Ментол', 'C10H20O', 'CC1CCC(C(C1)O)C(C)C'),
            ('Хлороформ', 'CHCl3', 'ClC(Cl)Cl'),
            ('Толуен', 'C7H8', 'Cc1ccccc1'),
            ('Фенол', 'C6H6O', 'c1ccccc1O'),
            ('Глюкоза', 'C6H12O6', 'C(C1C(C(C(C(O1)O)O)O)O)O'),
            ('Сечовина', 'CH4N2O', 'NC(=O)N'),
        ]
        for name, formula, smiles in dataset:
            self.add_compound(name=name, formula=formula, smiles=smiles)

    def add_compound(self, name, formula, smiles):
        if not name or not name.strip():
            raise ValueError('Назва сполуки обовʼязкова для заповнення.')
        preds = self.predictor.predict(smiles)
        final_formula = formula.strip() if (formula and formula.strip()) else preds['formula']
        entry = {
            'molecule_name': name.strip(),
            'formula': final_formula,
            'smiles': preds['canonical_smiles'],
            'water_solubility_logs': preds['water_solubility_logs'],
            'solubility_class': preds['solubility_class'],
            'boiling_point_c': preds['boiling_point_c'],
            'melting_point_c': preds['melting_point_c'],
            'ld50_mg_kg': preds['ld50_mg_kg'],
            'toxicity_class': preds['toxicity_class'],
        }
        for idx, existing in enumerate(self.compounds):
            if existing['molecule_name'].lower() == entry['molecule_name'].lower():
                self.compounds[idx] = entry
                return entry
        self.compounds.append(entry)
        return entry

    def remove_compound(self, name):
        self.compounds = [c for c in self.compounds if c['molecule_name'].lower() != name.lower()]

    def get_all(self):
        return list(self.compounds)

    def find_by_name(self, query):
        if not query or not query.strip():
            return self.get_all()
        q = query.strip().lower()
        return [
            c for c in self.compounds
            if q in c['molecule_name'].lower() or q in c['formula'].lower() or q in c['smiles'].lower()
        ]

    def sort_by(self, key, reverse=False):
        valid_keys = [
            'water_solubility_logs', 'boiling_point_c', 'melting_point_c',
            'ld50_mg_kg', 'molecule_name'
        ]
        if key not in valid_keys:
            key = 'water_solubility_logs'
        return sorted(self.compounds, key=lambda x: (x[key] is None, x[key]), reverse=reverse)

    def compare_compounds(self, names):
        lower_names = [n.lower() for n in names]
        return [c for c in self.compounds if c['molecule_name'].lower() in lower_names]

    def save_to_csv(self, filepath='chemistry_results.csv'):
        headers = [
            'molecule_name', 'formula', 'smiles',
            'water_solubility_logS', 'solubility_class',
            'boiling_point_C', 'melting_point_C',
            'ld50_mg_kg', 'toxicity_class'
        ]
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            for c in self.compounds:
                writer.writerow([
                    c['molecule_name'],
                    c['formula'],
                    c['smiles'],
                    c['water_solubility_logs'],
                    c['solubility_class'],
                    c['boiling_point_c'],
                    c['melting_point_c'],
                    c['ld50_mg_kg'],
                    c['toxicity_class'],
                ])

    def load_from_csv(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'Файл {filepath} не знайдено.')
        with open(filepath, mode='r', encoding='utf-8') as f:
            sample = f.read(2048)
            delimiter = ';' if ';' in sample else ','
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)
            loaded_count = 0
            for row in reader:
                name = row.get('molecule_name') or row.get('name')
                formula = row.get('formula')
                smiles = row.get('smiles')
                if not name or not smiles:
                    continue
                self.add_compound(name=name, formula=formula, smiles=smiles)
                loaded_count += 1
            return loaded_count
