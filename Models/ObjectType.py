class ObjectType:  # Rappresenta un tipo di dato (nodo della pipeline)

    def __init__(self, name: str, description: str = "", id: int = None):  # Costruttore della classe
        
        if not name or not isinstance(name, str):  # Controlla che il nome sia valido
            raise ValueError("ObjectType name must be a non-empty string")  # Errore se non valido

        self.id = id  # Identificativo opzionale (utile per DB)
        self._name = name.strip()  # Nome interno (immutabile)
        self._description = description.strip() if description else ""  # Descrizione opzionale pulita

    @property
    def name(self):  # Getter per il nome (read-only)
        return self._name  # Restituisce il nome interno
    @property
    def description(self):  # Getter per la descrizione (read-only)
        return self._description  # Restituisce la descrizione

    def __repr__(self):  # Rappresentazione ufficiale per debug
        return f"ObjectType(name='{self.name}', description='{self.description}')"  # Stringa leggibile

    def __eq__(self, other):  # Definisce quando due ObjectType sono uguali
        if not isinstance(other, ObjectType):  # Controlla il tipo
            return False  # Non sono confrontabili
        return self.name == other.name  # Uguali se hanno lo stesso nome

    def __hash__(self):  # Permette uso in set/dict
        return hash(self.name)  # Hash basato sul nome

    def __str__(self):  # Rappresentazione semplice
        return self.name  # Mostra solo il nome