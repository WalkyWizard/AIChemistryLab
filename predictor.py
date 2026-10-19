import torch
import numpy as np
from transformers import AutoTokenizer, RobertaModel
from huggingface_hub import hf_hub_download
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors


class ChemBERTaPredictor:
    def __init__(self, model_id='DeepChem/ChemBERTa-77M-MTR'):
        self.model_id = model_id
        self.tokenizer = None
        self.roberta = None
        self.dense_w = None
        self.dense_b = None
        self.out_w = None
        self.out_b = None
        self.norm_mean = None
        self.norm_std = None
        self._load_model()

    def _load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        weights_path = hf_hub_download(self.model_id, 'pytorch_model.bin')
        state_dict = torch.load(weights_path, map_location='cpu')
        self.roberta = RobertaModel.from_pretrained(self.model_id)
        self.roberta.eval()
        self.dense_w = state_dict['regression.dense.weight']
        self.dense_b = state_dict['regression.dense.bias']
        self.out_w = state_dict['regression.out_proj.weight']
        self.out_b = state_dict['regression.out_proj.bias']
        self.norm_mean = state_dict['norm_mean']
        self.norm_std = state_dict['norm_std']

    def _get_mtr_outputs(self, smiles):
        inputs = self.tokenizer(smiles, return_tensors='pt')
        with torch.no_grad():
            features = self.roberta(**inputs).last_hidden_state[:, 0, :]
            x = torch.tanh(torch.nn.functional.linear(features, self.dense_w, self.dense_b))
            raw = torch.nn.functional.linear(x, self.out_w, self.out_b)[0]
            denorm = (raw * self.norm_std + self.norm_mean).numpy()
        return denorm

    @staticmethod
    def _classify_toxicity(ld50_mg_kg):
        if ld50_mg_kg < 5:
            return 'Клас 1: Надзвичайно токсична'
        elif ld50_mg_kg < 50:
            return 'Клас 2: Дуже токсична'
        elif ld50_mg_kg < 300:
            return 'Клас 3: Токсична'
        elif ld50_mg_kg < 2000:
            return 'Клас 4: Мало токсична'
        elif ld50_mg_kg < 5000:
            return 'Клас 5: Практично нетоксична'
        return 'Нетоксична'

    @staticmethod
    def _classify_solubility(logs):
        if logs > 0:
            return 'Добре розчинна'
        elif logs > -1:
            return 'Розчинна'
        elif logs > -2:
            return 'Помірно розчинна'
        elif logs > -4:
            return 'Малорозчинна'
        return 'Практично нерозчинна'

    def validate_smiles(self, smiles):
        if not smiles or not isinstance(smiles, str):
            raise ValueError('Рядок SMILES не може бути порожнім.')
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            raise ValueError(f'Некоректний рядок SMILES: {smiles}')
        canonical = Chem.MolToSmiles(mol)
        formula = rdMolDescriptors.CalcMolFormula(mol)
        return canonical, formula

    def predict(self, smiles):
        canonical_smiles, formula = self.validate_smiles(smiles)
        d = self._get_mtr_outputs(canonical_smiles)

        pred_logp = float(0.7442 * d[112] + 0.7958)
        pred_mw = float(max(10.0, -17.7153 * d[34] + 66.4938))
        pred_logs = float(-0.72 * pred_logp - 0.005 * pred_mw + 0.15)

        pred_bp = float(-2.9218 * d[41] + 159.4631 * d[143] + 209.1978)

        pred_mp = float(-5.4541 * d[78] - 7615.6284 * d[147] - 731.9878)

        pred_log_ld50 = float(-0.0019 * d[18] + 0.4267 * d[115] + 0.4329)
        pred_ld50 = float(max(1.0, 10 ** pred_log_ld50))

        return {
            'canonical_smiles': canonical_smiles,
            'formula': formula,
            'water_solubility_logs': round(pred_logs, 2),
            'solubility_class': self._classify_solubility(pred_logs),
            'boiling_point_c': round(pred_bp, 1),
            'melting_point_c': round(pred_mp, 1),
            'ld50_mg_kg': round(pred_ld50, 0),
            'toxicity_class': self._classify_toxicity(pred_ld50),
        }
