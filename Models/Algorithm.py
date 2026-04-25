from Models.ObjectType import ObjectType

class Algorithm:  # Rappresenta una trasformazione tra ObjectType (arco della pipeline)

    def __init__(
        self,
        name: str,                    # Nome dell'algoritmo
        input_type: ObjectType,       # Tipo di dato in ingresso
        output_type: ObjectType,      # Tipo di dato in uscita
        cost: float = 1.0,            # Costo dell'operazione
        id: int = None                # Identificativo opzionale (per DB)
    ):
        if not name or not isinstance(name, str):  # Controlla validità nome
            raise ValueError("Algorithm name must be a non-empty string")  # Errore se non valido

        if not isinstance(input_type, ObjectType):  # Controlla tipo input
            raise ValueError("input_type must be ObjectType")  # Errore se non valido

        if not isinstance(output_type, ObjectType):  # Controlla tipo output
            raise ValueError("output_type must be ObjectType")  # Errore se non valido

        if not isinstance(cost, (int, float)) or cost < 0:  # Controlla costo valido
            raise ValueError("cost must be a non-negative number")  # Errore se non valido

        self.id = id  # ID opzionale
        self._name = name.strip()  # Nome interno (immutabile)
        self._input_type = input_type  # Tipo input interno
        self._output_type = output_type  # Tipo output interno
        self._cost = float(cost)  # Costo interno

    @property
    def name(self):  # Getter nome
        return self._name  # Restituisce nome
    @property
    def input_type(self):  # Getter input
        return self._input_type  # Restituisce input type
    @property
    def output_type(self):  # Getter output
        return self._output_type  # Restituisce output type
    @property
    def cost(self):  # Getter costo
        return self._cost  # Restituisce costo

    def __repr__(self):  # Rappresentazione per debug
        return (
            f"Algorithm(name='{self.name}', "  # Nome algoritmo
            f"input='{self.input_type.name}', "  # Tipo input
            f"output='{self.output_type.name}', "  # Tipo output
            f"cost={self.cost})"  # Costo
        )

    def __str__(self):  # Rappresentazione semplice
        return f"{self.input_type} --{self.name}--> {self.output_type}"  # Forma leggibile pipeline

    def __eq__(self, other):  # Definisce quando due algoritmi sono uguali
        if not isinstance(other, Algorithm):  # Controllo tipo
            return False  # Non uguali
        return (
            self.name == other.name and  # Nome uguale
            self.input_type == other.input_type and  # Input uguale
            self.output_type == other.output_type  # Output uguale
        )

    def __hash__(self):  # Permette uso in set/dict
        return hash((self.name, self.input_type, self.output_type))  # Hash coerente con __eq__