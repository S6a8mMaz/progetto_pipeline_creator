from DB.ConfigDB import SessionLocal
from DB.OpDB_Context import create_context
from DB.OpDB_ObjectType import create_object_type
from DB.OpDB_Algorithm import create_algorithm
from DB import OpDB_Pipeline
from Models.ObjectType import ObjectType
from Models.Algorithm import Algorithm
from Models.Pipeline import Pipeline


# ============================================================
# UTILITY: costruzione e salvataggio pipeline
# ============================================================
def build_and_save_pipeline(db, pipeline_name, context_id, start_type_name, steps):
    """
    Questa funzione costruisce una pipeline runtime e la salva nel DB.

    steps = [
        ("nome_algoritmo", "input_type", "output_type", costo),
        ...
    ]

    NOTA IMPORTANTE:
    Qui stiamo simulando esecuzione reale della pipeline,
    rispettando i vincoli del modello Pipeline (compatibilità input/output).
    """
    pipeline = Pipeline(ObjectType(start_type_name))

    for alg_name, input_type, output_type, cost in steps:
        algorithm = Algorithm(
            name=alg_name,
            input_type=ObjectType(input_type),
            output_type=ObjectType(output_type),
            cost=cost
        )
        pipeline.add_step(algorithm)

    OpDB_Pipeline.create_pipeline(
        db=db,
        pipeline=pipeline,
        name=pipeline_name,
        context_id=context_id
    )


# ============================================================
# SEED DATABASE
# ============================================================
def seed_db():

    db = SessionLocal()

    try:
        # =====================================================
        # 1. CONTEXTS (GERARCHIA OSPEDALIERA)
        # =====================================================

        # ROOT: contesto generale Hospital
        ctx_hospital = create_context(db, "Hospital")

        # LIVELLO 1
        ctx_diagnostics = create_context(db, "Diagnostics", ctx_hospital.id)
        ctx_monitoring = create_context(db, "Monitoring", ctx_hospital.id)

        # LIVELLO 2 (sottocontesti)
        ctx_tac = create_context(db, "CTscan", ctx_diagnostics.id)
        ctx_rm = create_context(db, "MRI", ctx_diagnostics.id)

        ctx_activity = create_context(db, "Sport", ctx_monitoring.id)

        # =====================================================
        # 2. OBJECT TYPES
        # =====================================================

        # -------------------------
        # ROOT (generici → riusabili ovunque)
        # -------------------------
        create_object_type(db, "RawData", context_id=ctx_hospital.id)
        create_object_type(db, "CleanData", context_id=ctx_hospital.id)
        create_object_type(db, "FeatureData", context_id=ctx_hospital.id)
        create_object_type(db, "Report", context_id=ctx_hospital.id)

        # -------------------------
        # Diagnostics
        # -------------------------
        create_object_type(db, "MedicalImage", context_id=ctx_diagnostics.id)
        create_object_type(db, "ProcessedImage", context_id=ctx_diagnostics.id)
        create_object_type(db, "Diagnosis", context_id=ctx_diagnostics.id)

        # -------------------------
        # CTscan
        # -------------------------
        create_object_type(db, "CTscan_Image", context_id=ctx_tac.id)
        create_object_type(db, "CTscan_Processed", context_id=ctx_tac.id)
        create_object_type(db, "CTscan_Diagnosis", context_id=ctx_tac.id)

        # -------------------------
        # RM
        # -------------------------
        create_object_type(db, "RM_Image", context_id=ctx_rm.id)
        create_object_type(db, "RM_Processed", context_id=ctx_rm.id)
        create_object_type(db, "RM_Diagnosis", context_id=ctx_rm.id)

        # -------------------------
        # MONITORAGGIO
        # -------------------------
        create_object_type(db, "SensorData", context_id=ctx_monitoring.id)
        create_object_type(db, "TimeSeries", context_id=ctx_monitoring.id)
        create_object_type(db, "Alert", context_id=ctx_monitoring.id)

        # -------------------------
        # ATTIVITA FISICA
        # -------------------------
        create_object_type(db, "GPSData", context_id=ctx_activity.id)
        create_object_type(db, "ActivityPattern", context_id=ctx_activity.id)
        create_object_type(db, "PerformanceReport", context_id=ctx_activity.id)

        # =====================================================
        # 3. ALGORITHMS
        # =====================================================

        # -------------------------
        # ROOT → pipeline generica dati
        # -------------------------
        create_algorithm(db, "clean_data", "RawData", "CleanData", 1.0, ctx_hospital.id)
        create_algorithm(db, "extract_features", "CleanData", "FeatureData", 1.0, ctx_hospital.id)
        create_algorithm(db, "generate_report", "FeatureData", "Report", 1.0, ctx_hospital.id)

        # -------------------------
        # Diagnostics → immagini mediche
        # -------------------------
        create_algorithm(db, "convert_to_image", "RawData", "MedicalImage", 1.0, ctx_diagnostics.id)
        create_algorithm(db, "enhance_image", "MedicalImage", "ProcessedImage", 1.0, ctx_diagnostics.id)
        create_algorithm(db, "diagnose", "ProcessedImage", "Diagnosis", 2.0, ctx_diagnostics.id)

        # -------------------------
        # CTscan → specializzazione
        # -------------------------
        create_algorithm(db, "tac_reconstruction", "MedicalImage", "CTscan_Image", 2.0, ctx_tac.id)
        create_algorithm(db, "tac_filtering", "CTscan_Image", "CTscan_Processed", 1.0, ctx_tac.id)
        create_algorithm(db, "tac_analysis", "CTscan_Processed", "CTscan_Diagnosis", 2.0, ctx_tac.id)

        # -------------------------
        # RM → specializzazione
        # -------------------------
        create_algorithm(db, "rm_reconstruction", "MedicalImage", "RM_Image", 2.0, ctx_rm.id)
        create_algorithm(db, "rm_denoising", "RM_Image", "RM_Processed", 1.0, ctx_rm.id)
        create_algorithm(db, "rm_analysis", "RM_Processed", "RM_Diagnosis", 2.0, ctx_rm.id)

        # -------------------------
        # MONITORAGGIO
        # -------------------------
        create_algorithm(db, "normalize_sensor", "RawData", "SensorData", 1.0, ctx_monitoring.id)
        create_algorithm(db, "build_timeseries", "SensorData", "TimeSeries", 1.0, ctx_monitoring.id)
        create_algorithm(db, "detect_anomaly", "TimeSeries", "Alert", 2.0, ctx_monitoring.id)

        # -------------------------
        # ATTIVITA FISICA
        # -------------------------
        create_algorithm(db, "gps_processing", "SensorData", "GPSData", 1.0, ctx_activity.id)
        create_algorithm(db, "pattern_detection", "GPSData", "ActivityPattern", 1.0, ctx_activity.id)
        create_algorithm(db, "performance_eval", "ActivityPattern", "PerformanceReport", 1.0, ctx_activity.id)

        print("\t*** DB populated with a standard ***")

        # =====================================================
        # 4. PIPELINE (CHIAVE PER LA PRESENTAZIONE)
        # =====================================================

        # -----------------------------------------------------
        # 🟢 PIPELINE GENERICA (RIUSABILE OVUNQUE)
        # -----------------------------------------------------
        """
        Questa pipeline rappresenta il flusso dati BASE.

        ✔ Può essere usata in QUALSIASI contesto
        ✔ Perché i suoi ObjectType sono definiti nel ROOT
        ✔ Grazie all’ereditarietà dei contesti

        ESEMPIO:
        Può essere usata anche in CTscan o AttivitàFisica
        """
        build_and_save_pipeline(
            db,
            "Generic_pipeline",
            ctx_hospital.id,
            "RawData",
            [
                ("clean_data", "RawData", "CleanData", 1.0),
                ("extract_features", "CleanData", "FeatureData", 1.0),
                ("generate_report", "FeatureData", "Report", 1.0),
            ]
        )

        # -----------------------------------------------------
        # 🔵 Diagnostics (figlio)
        # -----------------------------------------------------
        """
        Pipeline per analisi immagini mediche GENERICHE.

        ✔ Usa ObjectType del padre + propri
        ✔ Può essere usata in CTscan e RM

        NON può essere usata nel ROOT perché introduce:
        - MedicalImage
        """
        build_and_save_pipeline(
            db,
            "pipeline_Diagnostics",
            ctx_diagnostics.id,
            "RawData",
            [
                ("convert_to_image", "RawData", "MedicalImage", 1.0),
                ("enhance_image", "MedicalImage", "ProcessedImage", 1.0),
                ("diagnose", "ProcessedImage", "Diagnosis", 2.0),
            ]
        )

        # -----------------------------------------------------
        # 🟠 MONITORAGGIO
        # -----------------------------------------------------
        build_and_save_pipeline(
            db,
            "pipeline_monitoraggio",
            ctx_monitoring.id,
            "RawData",
            [
                ("normalize_sensor", "RawData", "SensorData", 1.0),
                ("build_timeseries", "SensorData", "TimeSeries", 1.0),
                ("detect_anomaly", "TimeSeries", "Alert", 2.0),
            ]
        )

        # -----------------------------------------------------
        # 🟣 CTscan (nipote)
        # -----------------------------------------------------
        """
        Pipeline altamente specializzata.

        ✔ Usa algoritmi specifici CTscan
        ✔ Usa MedicalImage ereditato da Diagnostics

        ❌ NON può essere usata in Diagnostics o Hospital
        perché CTscan_Image NON esiste lì
        """
        build_and_save_pipeline(
            db,
            "pipeline_CTscan",
            ctx_tac.id,
            "RawData",
            [
                ("convert_to_image", "RawData", "MedicalImage", 1.0),
                ("tac_reconstruction", "MedicalImage", "CTscan_Image", 2.0),
                ("tac_filtering", "CTscan_Image", "CTscan_Processed", 1.0),
                ("tac_analysis", "CTscan_Processed", "CTscan_Diagnosis", 2.0),
            ]
        )

        # -----------------------------------------------------
        # 🟣 RM
        # -----------------------------------------------------
        build_and_save_pipeline(
            db,
            "pipeline_RM",
            ctx_rm.id,
            "RawData",
            [
                ("convert_to_image", "RawData", "MedicalImage", 1.0),
                ("rm_reconstruction", "MedicalImage", "RM_Image", 2.0),
                ("rm_denoising", "RM_Image", "RM_Processed", 1.0),
                ("rm_analysis", "RM_Processed", "RM_Diagnosis", 2.0),
            ]
        )

        # -----------------------------------------------------
        # 🔴 ATTIVITA FISICA (nipote)
        # -----------------------------------------------------
        build_and_save_pipeline(
            db,
            "pipeline_attivita_fisica",
            ctx_activity.id,
            "RawData",
            [
                ("normalize_sensor", "RawData", "SensorData", 1.0),
                ("gps_processing", "SensorData", "GPSData", 1.0),
                ("pattern_detection", "GPSData", "ActivityPattern", 1.0),
                ("performance_eval", "ActivityPattern", "PerformanceReport", 1.0),
            ]
        )

    except Exception as e:
        print("\t❌ ERRORE:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
