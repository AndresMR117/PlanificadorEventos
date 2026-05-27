import os
import requests
from typing import List, Dict

class SPARQLService:
    def __init__(self):
        self.endpoint = os.getenv('SPARQL_ENDPOINT', '').strip()
        self.user = os.getenv('SPARQL_USER', '').strip()
        self.password = os.getenv('SPARQL_PASSWORD', '').strip()
        self.timeout = int(os.getenv('SPARQL_TIMEOUT', '10'))
    
    def query(self, query_string: str) -> List[Dict]:
        if not self.endpoint:
            return []

        try:
            auth = (self.user, self.password) if self.user and self.password else None
            response = requests.get(
                self.endpoint,
                params={'query': query_string},
                headers={'Accept': 'application/json'},
                auth=auth,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return response.json()
            return [{"status": response.status_code, "text": response.text}]
        except Exception as e:
            return [{"error": str(e)}]
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        results = []
        for binding in data.get('results', {}).get('bindings', []):
            item = {}
            for key, value in binding.items():
                item[key] = value.get('value', '')
            results.append(item)
        return results
    
    # ==================== PROVEEDORES ====================
    
    def obtener_proveedores(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?calificacion ?ciudad ?telefono ?whatsapp ?instagram WHERE {
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:nombre ?nombre .
            OPTIONAL { ?empresa ev:calificacion ?calificacion }
            OPTIONAL { ?empresa ev:ciudad      ?ciudad      }
            OPTIONAL { ?empresa ev:telefono    ?telefono    }
            OPTIONAL { ?empresa ev:whatsapp    ?whatsapp    }
            OPTIONAL { ?empresa ev:instagram   ?instagram   }
        }
        ORDER BY DESC(xsd:decimal(?calificacion))
        """
        return self.query(query)
    
    def obtener_proveedores_destacados(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?calificacion ?ciudad ?telefono WHERE {
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:nombre       ?nombre       .
            ?empresa ev:calificacion ?calificacion .
            OPTIONAL { ?empresa ev:ciudad   ?ciudad   }
            OPTIONAL { ?empresa ev:telefono ?telefono }
        }
        ORDER BY DESC(xsd:decimal(?calificacion))
        """
        return self.query(query)
    
    def obtener_todos_proveedores(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?calificacion ?ciudad ?telefono WHERE {
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:nombre ?nombre .
            OPTIONAL { ?empresa ev:calificacion ?calificacion }
            OPTIONAL { ?empresa ev:ciudad       ?ciudad       }
            OPTIONAL { ?empresa ev:telefono     ?telefono     }
        }
        ORDER BY DESC(xsd:decimal(?calificacion))
        """
        return self.query(query)
    
    def obtener_proveedor_por_nombre(self, nombre: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?calificacion ?ciudad ?descripcion ?telefono WHERE {{
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:nombre "{nombre}"@es .
            ?empresa ev:nombre ?nombre .
            OPTIONAL {{ ?empresa ev:calificacion ?calificacion }}
            OPTIONAL {{ ?empresa ev:ciudad ?ciudad }}
            OPTIONAL {{ ?empresa ev:descripcion ?descripcion }}
            OPTIONAL {{ ?empresa ev:telefono ?telefono }}
        }}
        """
        return self.query(query)
    
    def obtener_proveedores_por_ciudad(self, ciudad: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?calificacion ?telefono WHERE {{
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:nombre  ?nombre  .
            ?empresa ev:ciudad  "{ciudad}"@es .
            OPTIONAL {{ ?empresa ev:calificacion ?calificacion }}
            OPTIONAL {{ ?empresa ev:telefono     ?telefono     }}
        }}
        ORDER BY DESC(xsd:decimal(?calificacion))
        """
        return self.query(query)
    
    def obtener_proveedores_por_categoria(self, categoria: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?calificacion ?ciudad WHERE {{
            ?servicio rdf:type ev:Servicio .
            ?servicio ev:ofrecidoPor ?empresa .
            ?empresa ev:nombre ?nombre .
            ?servicio ev:tieneCategoria ?categoriaObj .
            FILTER(CONTAINS(LCASE(STR(?categoriaObj)), LCASE("{categoria}")))
            OPTIONAL {{ ?empresa ev:calificacion ?calificacion }}
            OPTIONAL {{ ?empresa ev:ciudad ?ciudad }}
        }}
        ORDER BY DESC(xsd:decimal(?calificacion))
        """
        return self.query(query)
    
    # ==================== TIPOS DE EVENTO ====================
    
    def obtener_tipos_evento(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?descripcion WHERE {
            ?tipo rdf:type ev:TipoEvento .
            ?tipo ev:nombre ?nombre .
            OPTIONAL { ?tipo ev:descripcion ?descripcion }
        }
        ORDER BY ?nombre
        """
        return self.query(query)
    
    # ==================== CATEGORÍAS ====================
    
    def obtener_categorias_servicio(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre WHERE {
            ?categoria rdf:type ev:CategoriaServicio .
            ?categoria ev:nombre ?nombre .
        }
        ORDER BY ?nombre
        """
        return self.query(query)
    
    # ==================== SERVICIOS ====================
    
    def obtener_servicios(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?precioBase ?precioMinimo ?precioMaximo ?precioPorPersona ?categoria ?empresa WHERE {
            ?servicio rdf:type ev:Servicio .
            ?servicio ev:nombre ?nombre .
            OPTIONAL { ?servicio ev:precioBase ?precioBase }
            OPTIONAL { ?servicio ev:precioMinimo ?precioMinimo }
            OPTIONAL { ?servicio ev:precioMaximo ?precioMaximo }
            OPTIONAL { ?servicio ev:precioPorPersona ?precioPorPersona }
            ?servicio ev:tieneCategoria ?categoriaObj . ?categoriaObj ev:nombre ?categoria .
            ?servicio ev:ofrecidoPor ?empresaObj . ?empresaObj ev:nombre ?empresa .
        }
        ORDER BY ?precioBase
        """
        return self.query(query)
    
    def obtener_servicios_por_tipo(self, tipo_evento: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?precioBase ?precioPorPersona ?categoria ?empresa WHERE {{
            ?servicio rdf:type ev:Servicio .
            ?servicio ev:nombre ?nombre .
            ?servicio ev:compatibleConTipo ev:{tipo_evento} .
            OPTIONAL {{ ?servicio ev:precioBase      ?precioBase      }}
            OPTIONAL {{ ?servicio ev:precioPorPersona ?precioPorPersona }}
            ?servicio ev:tieneCategoria ?categoriaObj .
            ?categoriaObj ev:nombre ?categoria .
            ?servicio ev:ofrecidoPor ?empresaObj .
            ?empresaObj ev:nombre ?empresa .
        }}
        ORDER BY xsd:decimal(?precioBase)
        """
        return self.query(query)
    
    def obtener_servicios_por_categoria(self, categoria: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?precioBase ?precioMinimo ?precioMaximo ?empresa WHERE {{
            ?servicio rdf:type ev:Servicio .
            ?servicio ev:nombre ?nombre .
            ?servicio ev:tieneCategoria ?categoriaObj .
            FILTER(CONTAINS(LCASE(STR(?categoriaObj)), LCASE("{categoria}")))
            OPTIONAL {{ ?servicio ev:precioBase ?precioBase }}
            OPTIONAL {{ ?servicio ev:precioMinimo ?precioMinimo }}
            OPTIONAL {{ ?servicio ev:precioMaximo ?precioMaximo }}
            ?servicio ev:ofrecidoPor ?empresaObj . ?empresaObj ev:nombre ?empresa .
        }}
        ORDER BY ?precioBase
        """
        return self.query(query)
    
    def obtener_servicios_por_rango_precio(self, min_precio: float, max_precio: float) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?precioBase ?categoria ?empresa WHERE {{
            ?servicio rdf:type ev:Servicio .
            ?servicio ev:nombre ?nombre .
            ?servicio ev:precioBase ?precioBase .
            FILTER(xsd:decimal(?precioBase) >= {min_precio} && xsd:decimal(?precioBase) <= {max_precio})
            ?servicio ev:tieneCategoria ?categoriaObj . ?categoriaObj ev:nombre ?categoria .
            ?servicio ev:ofrecidoPor ?empresaObj . ?empresaObj ev:nombre ?empresa .
        }}
        ORDER BY xsd:decimal(?precioBase)
        """
        return self.query(query)
    
    # ==================== PAQUETES ====================
    
    def obtener_paquetes(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?precioBase ?descuentoPct ?tipoEvento WHERE {
            ?paquete rdf:type ev:Paquete .
            ?paquete ev:nombre ?nombre .
            OPTIONAL { ?paquete ev:precioBase ?precioBase }
            OPTIONAL { ?paquete ev:descuentoPct ?descuentoPct }
            ?paquete ev:paqueteParaTipo ?tipoObj . ?tipoObj ev:nombre ?tipoEvento .
        }
        """
        return self.query(query)
    
    def obtener_paquetes_por_tipo(self, tipo_evento: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev:  <http://eventos.caqueta.co/ontologia#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?nombre ?precioBase ?descuentoPct WHERE {{
            ?paquete rdf:type ev:Paquete .
            ?paquete ev:nombre ?nombre .
            ?paquete ev:paqueteParaTipo ev:{tipo_evento} .
            OPTIONAL {{ ?paquete ev:precioBase   ?precioBase   }}
            OPTIONAL {{ ?paquete ev:descuentoPct ?descuentoPct }}
        }}
        ORDER BY xsd:decimal(?precioBase)
        """
        return self.query(query)
    
    # ==================== ACCESORIOS ====================
    
    def obtener_accesorios(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?precioBase ?tipoEvento WHERE {
            ?accesorio rdf:type ev:Accesorio .
            ?accesorio ev:nombre ?nombre .
            OPTIONAL { ?accesorio ev:precioBase ?precioBase }
            ?accesorio ev:accesorioParaTipo ?tipoObj . ?tipoObj ev:nombre ?tipoEvento .
        }
        """
        return self.query(query)
    
    def obtener_accesorios_por_tipo(self, tipo_evento: str) -> List[Dict]:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?precioBase WHERE {{
            ?accesorio rdf:type ev:Accesorio .
            ?accesorio ev:nombre ?nombre .
            ?accesorio ev:accesorioParaTipo ev:{tipo_evento} .
            OPTIONAL {{ ?accesorio ev:precioBase ?precioBase }}
        }}
        """
        return self.query(query)
    
    # ==================== UBICACIONES ====================
    
    def obtener_ubicaciones(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT DISTINCT ?ciudad WHERE {
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:ciudad ?ciudad .
        }
        ORDER BY ?ciudad
        """
        return self.query(query)
    
    # ==================== FACTORES ====================
    
    def obtener_factores_distancia(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?multiplicador WHERE {
            ?factor rdf:type ev:FactorDistancia .
            ?factor ev:nombre ?nombre .
            OPTIONAL { ?factor ev:multiplicador ?multiplicador }
        }
        ORDER BY ?nombre
        """
        return self.query(query)
    
    def obtener_temporadas(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?nombre ?factorTemporada WHERE {
            ?temporada rdf:type ev:Temporada .
            ?temporada ev:temporadaNombre ?nombre .
            OPTIONAL { ?temporada ev:factorTemporada ?factorTemporada }
        }
        ORDER BY ?nombre
        """
        return self.query(query)
    
    # ==================== RECOMENDACIONES ====================
    
    def generar_recomendaciones(self, tipo_evento: str) -> Dict:
        servicios = self.obtener_servicios_por_tipo(tipo_evento)
        paquetes = self.obtener_paquetes_por_tipo(tipo_evento)
        proveedores = self.obtener_proveedores_destacados()
        
        return {
            'tipo_evento': tipo_evento,
            'proveedores_destacados': proveedores[:5],
            'servicios_recomendados': servicios[:8],
            'paquetes_recomendados': paquetes,
            'presupuesto_estimado': sum(float(s.get('precioBase', 0)) for s in servicios[:4]) if servicios else 0
        }
    
    def generar_recomendaciones_completas(self, tipo_evento: str, presupuesto_max: float = None, ciudad: str = None) -> Dict:
        servicios = self.obtener_servicios_por_tipo(tipo_evento)
        paquetes = self.obtener_paquetes_por_tipo(tipo_evento)
        proveedores = self.obtener_proveedores_destacados()
        
        if presupuesto_max:
            servicios = [s for s in servicios if float(s.get('precioBase', 0)) <= presupuesto_max]
        
        if ciudad:
            proveedores_ciudad = self.obtener_proveedores_por_ciudad(ciudad)
        else:
            proveedores_ciudad = proveedores
        
        return {
            'tipo_evento': tipo_evento,
            'proveedores_destacados': proveedores[:5],
            'proveedores_por_ciudad': proveedores_ciudad[:5] if proveedores_ciudad else [],
            'servicios_recomendados': servicios[:10],
            'paquetes_recomendados': paquetes,
            'presupuesto_estimado': sum(float(s.get('precioBase', 0)) for s in servicios[:4]) if servicios else 0
        }
    
    # ==================== CIUDADES DISPONIBLES ====================
    
    def obtener_ciudades_disponibles(self) -> List[str]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT DISTINCT ?ciudad WHERE {
            ?empresa rdf:type ev:Empresa .
            ?empresa ev:ciudad ?ciudad .
        }
        ORDER BY ?ciudad
        """
        resultados = self.query(query)
        return [r.get('ciudad', '') for r in resultados if r.get('ciudad')]
    
    def contar_proveedores_por_categoria(self) -> List[Dict]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ev: <http://eventos.caqueta.co/ontologia#>
        
        SELECT ?categoria (COUNT(DISTINCT ?empresa) AS ?total) WHERE {
            ?servicio rdf:type ev:Servicio .
            ?servicio ev:ofrecidoPor ?empresa .
            ?servicio ev:tieneCategoria ?categoriaObj .
            ?categoriaObj ev:nombre ?categoria .
        }
        GROUP BY ?categoria
        ORDER BY DESC(?total)
        """
        return self.query(query)
