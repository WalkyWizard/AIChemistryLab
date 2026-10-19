import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class AIChemistryLabGUI:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager

        self.root.title('AI Chemistry Lab — Прогнозування властивостей молекул')
        self.root.geometry('1280x740')
        self.root.minsize(1000, 600)

        self._setup_styles()
        self._build_ui()
        self._refresh_table()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', rowheight=26, font=('Segoe UI', 9))
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))
        style.configure('TLabel', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 9))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        input_group = ttk.LabelFrame(main_frame, text='Додавання хімічної сполуки', padding=10)
        input_group.pack(fill=tk.X, pady=(0, 10))

        grid_frame = ttk.Frame(input_group)
        grid_frame.pack(fill=tk.X)

        ttk.Label(grid_frame, text='Назва речовини:').grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.entry_name = ttk.Entry(grid_frame, width=22)
        self.entry_name.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(grid_frame, text='Формула (опціонально):').grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
        self.entry_formula = ttk.Entry(grid_frame, width=16)
        self.entry_formula.grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(grid_frame, text='SMILES:').grid(row=0, column=4, sticky=tk.W, padx=4, pady=4)
        self.entry_smiles = ttk.Entry(grid_frame, width=30)
        self.entry_smiles.grid(row=0, column=5, sticky=tk.W, padx=4, pady=4)

        btn_box = ttk.Frame(grid_frame)
        btn_box.grid(row=0, column=6, padx=8)

        ttk.Button(btn_box, text='Прогнозувати та додати', command=self._on_add_compound).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text='Очистити поля', command=self._clear_inputs).pack(side=tk.LEFT, padx=4)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(control_frame, text='Пошук:').pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self._on_search())
        ttk.Entry(control_frame, textvariable=self.search_var, width=26).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(control_frame, text='Сортувати за:').pack(side=tk.LEFT, padx=(0, 4))
        self.sort_prop_var = tk.StringVar(value='Розчинність logS')
        sort_combo = ttk.Combobox(
            control_frame,
            textvariable=self.sort_prop_var,
            values=['Розчинність logS', 'Температура кипіння', 'Температура плавлення', 'Токсичність LD50', 'Назва'],
            state='readonly',
            width=22
        )
        sort_combo.pack(side=tk.LEFT, padx=(0, 6))
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self._on_sort())

        self.sort_order_var = tk.StringVar(value='Зростання')
        order_combo = ttk.Combobox(
            control_frame,
            textvariable=self.sort_order_var,
            values=['Зростання', 'Спадання'],
            state='readonly',
            width=12
        )
        order_combo.pack(side=tk.LEFT, padx=(0, 10))
        order_combo.bind('<<ComboboxSelected>>', lambda e: self._on_sort())

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('name', 'formula', 'smiles', 'logs', 'sol_class', 'bp', 'mp', 'ld50', 'tox_class')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='extended')

        headings = {
            'name': 'Назва',
            'formula': 'Формула',
            'smiles': 'SMILES',
            'logs': 'Розчинність logS',
            'sol_class': 'Клас розчинності',
            'bp': 'Т. кипіння (°C)',
            'mp': 'Т. плавлення (°C)',
            'ld50': 'LD50 (мг/кг)',
            'tox_class': 'Клас токсичності',
        }
        widths = {
            'name': 130, 'formula': 85, 'smiles': 185,
            'logs': 110, 'sol_class': 145, 'bp': 110,
            'mp': 110, 'ld50': 100, 'tox_class': 200
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=widths[col], anchor=tk.CENTER if col != 'name' else tk.W)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(actions_frame, text='Порівняти обрані сполуки', command=self._on_compare_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions_frame, text='Зберегти в CSV', command=self._on_export_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions_frame, text='Завантажити з CSV', command=self._on_import_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions_frame, text='Видалити обрану', command=self._on_delete_compound).pack(side=tk.RIGHT, padx=4)

        self.status_label = ttk.Label(main_frame, text='', relief=tk.SUNKEN, anchor=tk.W, padding=4)
        self.status_label.pack(fill=tk.X)

    def _clear_inputs(self):
        self.entry_name.delete(0, tk.END)
        self.entry_formula.delete(0, tk.END)
        self.entry_smiles.delete(0, tk.END)

    def _on_add_compound(self):
        name = self.entry_name.get().strip()
        formula = self.entry_formula.get().strip()
        smiles = self.entry_smiles.get().strip()

        if not name:
            messagebox.showerror('Помилка валідації', 'Будь ласка, вкажіть назву хімічної сполуки.')
            return
        if not smiles:
            messagebox.showerror('Помилка валідації', 'Будь ласка, введіть рядок SMILES для молекули.')
            return

        try:
            self.manager.add_compound(name=name, formula=formula, smiles=smiles)
            self._clear_inputs()
            self._refresh_table()
            self.status_label.config(text=f'Сполуку "{name}" успішно проаналізовано та додано.')
        except Exception as e:
            messagebox.showerror('Помилка аналізу молекули', str(e))

    def _on_delete_compound(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo('Інформація', 'Виберіть сполуку у таблиці для видалення.')
            return
        for item_id in selected:
            values = self.tree.item(item_id, 'values')
            if values:
                self.manager.remove_compound(values[0])
        self._refresh_table()
        self.status_label.config(text='Обрані сполуки видалено.')

    def _on_search(self):
        results = self.manager.find_by_name(self.search_var.get())
        self._populate_tree(results)

    def _on_sort(self):
        mapping = {
            'Розчинність logS': 'water_solubility_logs',
            'Температура кипіння': 'boiling_point_c',
            'Температура плавлення': 'melting_point_c',
            'Токсичність LD50': 'ld50_mg_kg',
            'Назва': 'molecule_name',
        }
        key = mapping.get(self.sort_prop_var.get(), 'water_solubility_logs')
        reverse = self.sort_order_var.get() == 'Спадання'
        result = self.manager.sort_by(key, reverse=reverse)
        query = self.search_var.get().strip().lower()
        if query:
            result = [c for c in result if query in c['molecule_name'].lower() or query in c['formula'].lower()]
        self._populate_tree(result)

    def _populate_tree(self, compounds):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in compounds:
            self.tree.insert('', tk.END, values=(
                c['molecule_name'],
                c['formula'],
                c['smiles'],
                f"{c['water_solubility_logs']:.2f}",
                c['solubility_class'],
                f"{c['boiling_point_c']:.1f}",
                f"{c['melting_point_c']:.1f}",
                f"{c['ld50_mg_kg']:.0f}",
                c['toxicity_class'],
            ))
        self.status_label.config(text=f'Завантажено сполук: {len(compounds)}')

    def _refresh_table(self):
        self._populate_tree(self.manager.get_all())

    def _on_compare_selected(self):
        selected = self.tree.selection()
        if len(selected) < 2:
            messagebox.showinfo('Порівняння', 'Виберіть щонайменше 2 сполуки (Ctrl або Shift + клік).')
            return
        names = [self.tree.item(item_id, 'values')[0] for item_id in selected]
        matched = self.manager.compare_compounds(names)
        self._show_comparison_window(matched)

    def _show_comparison_window(self, compounds):
        win = tk.Toplevel(self.root)
        win.title('Порівняльний аналіз хімічних сполук')
        win.geometry('900x480')

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        cols = ['Властивість'] + [c['molecule_name'] for c in compounds]
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        tree.heading('Властивість', text='Властивість')
        tree.column('Властивість', width=240, anchor=tk.W)
        for c in compounds:
            tree.heading(c['molecule_name'], text=c['molecule_name'])
            tree.column(c['molecule_name'], width=140, anchor=tk.CENTER)

        rows = [
            ('Хімічна формула', lambda c: c['formula']),
            ('SMILES', lambda c: c['smiles']),
            ('Розчинність у воді logS (mol/L)', lambda c: f"{c['water_solubility_logs']:.2f}"),
            ('Клас розчинності', lambda c: c['solubility_class']),
            ('Температура кипіння (°C)', lambda c: f"{c['boiling_point_c']:.1f}"),
            ('Температура плавлення (°C)', lambda c: f"{c['melting_point_c']:.1f}"),
            ('LD50 (мг/кг)', lambda c: f"{c['ld50_mg_kg']:.0f}"),
            ('Клас токсичності (ГГС)', lambda c: c['toxicity_class']),
        ]

        for label, extractor in rows:
            tree.insert('', tk.END, values=[label] + [extractor(c) for c in compounds])

        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        ttk.Button(frame, text='Закрити', command=win.destroy).pack(side=tk.RIGHT)

    def _on_export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='chemistry_results.csv'
        )
        if filepath:
            self.manager.save_to_csv(filepath)
            messagebox.showinfo('Експорт', f'Дані збережено у файл: {filepath}')

    def _on_import_csv(self):
        filepath = filedialog.askopenfilename(
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
        )
        if filepath:
            try:
                count = self.manager.load_from_csv(filepath)
                self._refresh_table()
                messagebox.showinfo('Імпорт', f'Завантажено {count} сполук із файлу.')
            except Exception as e:
                messagebox.showerror('Помилка імпорту', str(e))
