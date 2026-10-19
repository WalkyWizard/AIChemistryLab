import sys
import tkinter as tk
from predictor import ChemBERTaPredictor
from compound_manager import CompoundManager
from app_gui import AIChemistryLabGUI

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def run_cli_mode(manager):
    compounds = manager.get_all()
    csv_file = 'chemistry_results.csv'
    manager.save_to_csv(csv_file)

    print('========================================================================================')
    print('                   AI CHEMISTRY LAB: ChemBERTa-77M-MTR                                  ')
    print('========================================================================================')
    print(f'Кількість проаналізованих сполук: {len(compounds)}')
    print('----------------------------------------------------------------------------------------')
    fmt = '{:<15} {:<10} {:<8} {:<8} {:<8} {:<8} {}'
    print(fmt.format('Назва', 'Формула', 'logS', 'Т.кип', 'Т.пл', 'LD50', 'Токсичність'))
    print('----------------------------------------------------------------------------------------')
    for c in compounds:
        print(fmt.format(
            c['molecule_name'],
            c['formula'],
            f"{c['water_solubility_logs']:.2f}",
            f"{c['boiling_point_c']:.1f}",
            f"{c['melting_point_c']:.1f}",
            f"{c['ld50_mg_kg']:.0f}",
            c['toxicity_class']
        ))
    print('========================================================================================')
    print(f'Результати збережено у файл: {csv_file}')
    print('========================================================================================')


def main():
    predictor = ChemBERTaPredictor()
    manager = CompoundManager(predictor)

    manager.save_to_csv('chemistry_results.csv')

    if '--cli' in sys.argv:
        run_cli_mode(manager)
        return

    try:
        root = tk.Tk()
        app = AIChemistryLabGUI(root, manager)
        root.mainloop()
    except (tk.TclError, Exception):
        run_cli_mode(manager)


if __name__ == '__main__':
    main()
