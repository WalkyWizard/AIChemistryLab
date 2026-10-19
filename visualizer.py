import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class ChemistryVisualizer:
    def __init__(self, output_path='property_comparison.png'):
        self.output_path = output_path

    def generate_comparison_dashboard(self, compounds):
        if not compounds:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        names = [c['molecule_name'] for c in compounds]
        preds_logs = [c['predicted_logs'] for c in compounds]
        preds_logp = [c['predicted_logp'] for c in compounds]

        y_pos = np.arange(len(names))
        bar_height = 0.38

        color_logs = (0.17, 0.36, 0.56)
        color_logp = (0.85, 0.37, 0.01)
        color_scatter = (0.11, 0.62, 0.47)

        ax1.barh(y_pos - bar_height / 2, preds_logs, height=bar_height, label='Розчинність logS (AI)', color=color_logs)
        ax1.barh(y_pos + bar_height / 2, preds_logp, height=bar_height, label='Ліпофільність LogP (AI)', color=color_logp)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(names, fontsize=9)
        ax1.invert_yaxis()
        ax1.axvline(0, color='gray', linestyle='--', linewidth=0.8)
        ax1.set_xlabel('Прогнозоване значення властивості')
        ax1.set_title('Прогнозування властивостей молекул (ChemBERTa-77M-MTR)')
        ax1.legend(loc='lower right')
        ax1.grid(axis='x', linestyle=':', alpha=0.6)

        pairs = [(c['predicted_logs'], c['exp_logs'], c['molecule_name']) for c in compounds if c['exp_logs'] is not None]
        if pairs:
            p_vals = np.array([p[0] for p in pairs])
            e_vals = np.array([p[1] for p in pairs])
            labels = [p[2] for p in pairs]

            ax2.scatter(e_vals, p_vals, color=color_scatter, s=70, edgecolor='black', zorder=3)
            for i, txt in enumerate(labels):
                ax2.annotate(txt, (e_vals[i], p_vals[i]), fontsize=8, xytext=(4, 4), textcoords='offset points')

            min_val = min(min(e_vals), min(p_vals)) - 0.5
            max_val = max(max(e_vals), max(p_vals)) + 0.5
            ax2.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', label='Ідеальна відповідність (y=x)')

            mae = float(np.mean(np.abs(p_vals - e_vals)))
            corr = float(np.corrcoef(p_vals, e_vals)[0, 1])

            ax2.set_xlim(min_val, max_val)
            ax2.set_ylim(min_val, max_val)
            ax2.set_xlabel('Експериментальне значення logS')
            ax2.set_ylabel('Прогнозоване значення logS (ChemBERTa)')
            ax2.set_title(f'Порівняння з експериментом (MAE={mae:.2f}, Corr={corr:.2f})')
            ax2.legend(loc='upper left')
            ax2.grid(True, linestyle=':', alpha=0.6)

        plt.tight_layout()
        plt.savefig(self.output_path, dpi=200)
        plt.close(fig)
        return self.output_path
