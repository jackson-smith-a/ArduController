"""Encapsulate a sequence of stacked, validated entry fields.

Jackson Smith
Final Project
"""


import tkinter as tk


class EntryCollection(tk.Frame):
    """A collection of stacked Entry objects."""
    def __init__(self, master, name, properties, defaults=None):
        """
        Initialize a new EntryCollection instance.

        Args:
            master: The parent widget for the EntryCollection.
            name: The title of the EntryCollection.
            properties: A list of tuples, where each tuple contains a
                        property name and optional validator and converter.
            defaults: A dictionary of default values for the properties.
        """
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
                label.grid(sticky=tk.W, column=1, row=row, pady=10)
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
        """Update the values of the Entry objects in the collection.

        Args:
            defaults (dict): A dictionary containing the default values for the properties.
        """
        for prop in self.entries.keys():
            entry, _ = self.entries[prop]
            entry.delete(0, tk.END)
            if defaults.get(prop, None) is None:
                continue
            entry.insert(0, defaults[prop])

    def get(self):
        """Retrieve the values of the Entry objects in the collection.

        Returns:
            A dictionary containing the values of the Entry objects.
            The keys of the dictionary are the property names, and the values
            are the converted values of the Entry objects.
            If an Entry object is empty, the corresponding value in the dictionary will be None.
        """
        results = {}
        for prop, (entry, converter) in self.entries.items():
            value = entry.get()
            if value:
                results[prop] = converter(value)
            else:
                results[prop] = None

        return results
