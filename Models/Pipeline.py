from Models.ObjectType import ObjectType
from Models.Algorithm import Algorithm

class PipelineStep:  # Rappresenta uno step: input --algorithm--> output

    def __init__(self, input_type: ObjectType, algorithm: Algorithm):  # Costruttore step
        if not isinstance(input_type, ObjectType):  # Controlla tipo input
            raise ValueError("input_type must be ObjectType")  # Errore se non valido

        if not isinstance(algorithm, Algorithm):  # Controlla tipo algoritmo
            raise ValueError("algorithm must be Algorithm")  # Errore se non valido

        if algorithm.input_type != input_type:  # Verifica compatibilità
            raise ValueError("Algorithm is not compatible with input")  # Errore se incompatibile

        self._input_type = input_type  # Input interno (immutabile)
        self._algorithm = algorithm  # Algoritmo interno
        self._output_type = algorithm.output_type  # Output derivato automaticamente

    @property
    def input_type(self):  # Getter input
        return self._input_type  # Restituisce input

    @property
    def algorithm(self):  # Getter algoritmo
        return self._algorithm  # Restituisce algoritmo

    @property
    def output_type(self):  # Getter output
        return self._output_type  # Restituisce output

    def __repr__(self):  # Rappresentazione leggibile
        return f"\t{self.input_type.name} --[{self.algorithm.name}]--> {self.output_type.name}"  # Forma step


class Pipeline:  # Rappresenta una sequenza ordinata di step

    def __init__(self, start_type: ObjectType, id: int = None, name: str = None):  # Costruttore pipeline
        if not isinstance(start_type, ObjectType):  # Controlla tipo iniziale
            raise ValueError("start_type must be ObjectType")  # Errore se non valido
        
        self.name = name
        self.id = id  # ID opzionale (per DB)
        self._start_type = start_type  # Tipo iniziale
        self._steps = []  # Lista interna degli step

    @property
    def start_type(self):  # Getter start
        return self._start_type  # Restituisce tipo iniziale

    @property
    def steps(self):  # Getter steps
        return self._steps  # Restituisce lista step

    def add_step(self, algorithm: Algorithm):  # Aggiunge uno step alla pipeline
        if not isinstance(algorithm, Algorithm):  # Controllo tipo algoritmo
            raise ValueError("algorithm must be Algorithm")  # Errore se non valido

        current_type = self.get_last_output()  # Tipo corrente (ultimo nodo)

        if algorithm.input_type != current_type:  # Verifica compatibilità
            raise ValueError(
                f"Incompatible algorithm: expected {current_type.name}, "
                f"found {algorithm.input_type.name}"
            )

        step = PipelineStep(current_type, algorithm)  # Crea nuovo step
        self._steps.append(step)  # Aggiunge lo step

    def get_total_cost(self):  # Calcola costo totale pipeline
        return sum(step.algorithm.cost for step in self._steps)  # Somma costi

    def get_last_output(self):  # Restituisce tipo finale
        if not self._steps:  # Se pipeline vuota
            return self.start_type  # Ritorna tipo iniziale
        return self._steps[-1].output_type  # Output ultimo step

    def get_current_type(self):  # Alias del tipo corrente
        return self.get_last_output()  # Riusa metodo

    def get_algorithms(self):  # Restituisce lista algoritmi
        return [step.algorithm for step in self._steps]  # Estrae algoritmi

    def is_empty(self):  # Controlla se pipeline vuota
        return len(self._steps) == 0  # True se nessuno step

    def __repr__(self):  # Rappresentazione completa pipeline
        if not self._steps:  # Caso pipeline vuota
            return f"Empy pipeline from {self.start_type.name}"

        lines = [f"Start: {self.start_type.name}"]  # Inizio pipeline

        for step in self._steps:  # Itera sugli step
            lines.append(str(step))  # Aggiunge rappresentazione step

        lines.append(f"End: {self.get_last_output().name}")  # Nodo finale
        lines.append(f"Total cost: {self.get_total_cost()}")  # Costo totale

        return "\n".join(lines)  # Costruisce stringa finale