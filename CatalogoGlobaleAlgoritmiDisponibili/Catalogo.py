from collections import defaultdict
from Models.Algorithm import Algorithm
from Models.ObjectType import ObjectType


class AlgCatalog:  # Rappresenta il catalogo globale degli algoritmi disponibili

    def __init__(self):  # Costruttore del catalogo
        self._algorithms = []  # Lista interna di tutti gli algoritmi
        self._input_index = defaultdict(list)  # Indice input -> lista algoritmi compatibili
        self._output_index = defaultdict(list)  # Indice output -> lista algoritmi compatibili

    @property
    def algorithms(self):  # Getter della lista algoritmi
        return self._algorithms  # Restituisce tutti gli algoritmi del catalogo

    def add_algorithm(self, algorithm: Algorithm):  # Aggiunge un algoritmo al catalogo
        if not isinstance(algorithm, Algorithm):  # Controlla che l'oggetto sia un Algorithm
            raise ValueError("algorithm must be an Algorithm")  # Errore se non valido

        if algorithm in self._algorithms:  # Evita duplicati nel catalogo
            return  # Non aggiunge due volte lo stesso algoritmo

        self._algorithms.append(algorithm)  # Aggiunge l'algoritmo alla lista generale
        self._input_index[algorithm.input_type].append(algorithm)  # Indicizza per tipo input
        self._output_index[algorithm.output_type].append(algorithm)  # Indicizza per tipo output

    def get_by_input(self, object_type: ObjectType):  # Restituisce gli algoritmi che accettano un certo input
        if not isinstance(object_type, ObjectType):  # Controlla che il parametro sia ObjectType
            raise ValueError("object_type must be ObjectType")  # Errore se non valido
        return self._input_index.get(object_type, [])  # Ritorna lista algoritmi o lista vuota

    def get_by_output(self, object_type: ObjectType):  # Restituisce gli algoritmi che producono un certo output
        if not isinstance(object_type, ObjectType): 
            raise ValueError("object_type must be ObjectType")
        return self._output_index.get(object_type, []) 

    # Restituisce tutti gli algoritmi del catalogo
    def get_all(self): 
        return list(self._algorithms)
    
    def __repr__(self):  # Rappresentazione leggibile del catalogo
        if not self._algorithms:  # Caso catalogo vuoto
            return "AlgCatalog vuoto"
        return "\n".join(str(algorithm) for algorithm in self._algorithms) # Unisce tutti gli algoritmi in stringa

    def load_from_db(self, db_algorithms, valid_object_types=None):
        valid_names = None
        if valid_object_types:
            valid_names = {obj.name for obj in valid_object_types}

        for alg_db in db_algorithms:

            if valid_names:
                if alg_db.input_type not in valid_names or alg_db.output_type not in valid_names:
                    continue

            input_type = ObjectType(name=alg_db.input_type)
            output_type = ObjectType(name=alg_db.output_type)

            algorithm = Algorithm(
                name=alg_db.name,
                input_type=input_type,
                output_type=output_type,
                cost=alg_db.cost,
                id=getattr(alg_db, "id", None)
            )

            self.add_algorithm(algorithm)