# sistema_camara/core/processors/poses.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Jean / Bryan
# Descripción: Extrae los puntos clave del esqueleto para "Duro contra el Muro".

class PosesProcessor:
    # Mapeo de índices de MediaPipe a los nombres del contrato API
    MAPEO_LANDMARKS = {
        0:  "nariz",
        11: "hombro_izquierdo",
        12: "hombro_derecho",
        13: "codo_izquierdo",
        14: "codo_derecho",
        15: "muneca_izquierda",
        16: "muneca_derecha",
        23: "cadera_izquierda",
        24: "cadera_derecha",
        25: "rodilla_izquierda",
        26: "rodilla_derecha",
        27: "tobillo_izquierdo",
        28: "tobillo_derecho"
    }

    def procesar(self, landmarks_filtrados: list) -> dict:
        """
        Toma la lista de 33 landmarks y devuelve solo los 
        necesarios para el juego de Poses.
        """
        esqueleto = {}
        
        for indice, nombre in self.MAPEO_LANDMARKS.items():
            # landmarks_filtrados ya viene como lista de dicts {x, y, z, confidence}
            esqueleto[nombre] = landmarks_filtrados[indice]
            
        return {"esqueleto": esqueleto}