import tkinter as tk


class EntryCollection(tk.Frame):
    def __init__(self, master, name, properties, defaults=None):
        super().__init__(master)
        
        self.defaults = defaults
        
        self.title = tk.Label(self, text=name)
        self.title.grid(row=0, column=1)

        self.labels = {}
        self.entries = {}

        row = 0

        for i, (prop, *rest) in enumerate(properties):
            row += 1
            label = tk.Label(self, text=prop)
            self.labels[prop] = label

            if not rest:
                label.grid(sticky = tk.W, column=1, row=row, pady=10)
                continue
        
            label.grid(column=0, row=row)
            validator, converter = rest

            vcmd = self.register(validator)
            entry = tk.Entry(self, validate="all", validatecommand=(vcmd, "%P"))
            
            if defaults:
                default = defaults.get(prop, None)
                
                if default is not None:
                    entry.insert(0, default)

            entry.grid(column=2, row=row)
        
            self.entries[prop] = (entry, converter)

    def set(self, defaults):
        for prop in self.entries.keys():
            entry, _ = self.entries[prop]
            entry.delete(0, tk.END)
            if defaults.get(prop, None) is None:
                continue
            entry.insert(0, defaults[prop])
            
    def restore_defaults(self):
        self.set(self.defaults)
        
    def get(self):
        results = {}
        for prop, (entry, converter) in self.entries.items():
            value = entry.get()
            if value:
                results[prop] = converter(value)
            else:
                results[prop] = None
                
        return results
