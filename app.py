import pandas as pd
import streamlit as st
import os

st.set_page_config(page_title="Sistema de Pagos - Caja y Valores", layout="wide")

st.title("Universidad Pedagógica - Caja y Valores")
st.write("Sistema para consulta de Pagos")

archivo_excel = "BASE CUOTAS PARA SISTEMA.xlsx"

if not os.path.exists(archivo_excel):
    st.error(f"No se encuentra el archivo '{archivo_excel}' en la carpeta. Asegúrate de que esté junto a app.py")
else:
    # Cargamos los datos con caché
    @st.cache_data
    def cargar_datos():
        df = pd.read_excel(archivo_excel)
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        return df

    try:
        df_pagos = cargar_datos()
        
        # Creamos dos columnas en la interfaz para ordenar mejor los filtros
        col1, col2 = st.columns([2, 1])
        
        with col1:
            busqueda = st.text_input("Hola TILIN, escribI el Nombre, Apellidos o N° de Depósito:")
            
        with col2:
            # Filtro opcional por monto exacto (o dejar en blanco para ver todos)
            filtrar_monto = st.checkbox("Filtrar también por Monto específico")
            monto_buscado = None
            if filtrar_monto:
                monto_buscado = st.number_input("Ingrese el Monto (Bs):", min_value=0.0, step=10.0)

        if busqueda or filtrar_monto:
            # 1. Filtro por texto (Nombre, Participante o Depósito)
            if busqueda:
                busqueda_limpia = busqueda.strip()
                palabras = busqueda_limpia.split()

                def coincide_registro(row):
                    texto_nombre = str(row.get('NOMBRE', ''))
                    texto_participante = str(row.get('PARTICIPANTE', ''))
                    texto_deposito = str(row.get('N° DE DEPOSITO', ''))
                    
                    contenido_completo = f"{texto_nombre} {texto_participante} {texto_deposito}".lower()
                    return all(palabra.lower() in contenido_completo for palabra in palabras)

                resultado = df_pagos[df_pagos.apply(coincide_registro, axis=1)]
            else:
                # Si no escribió texto pero activó el filtro de monto, partimos de todos los datos
                resultado = df_pagos.copy()

            # 2. Filtro adicional por monto (si está activado)
            if filtrar_monto and not resultado.empty:
                if 'MONTO' in resultado.columns:
                    # Filtramos donde el monto sea exactamente igual al ingresado
                    resultado = resultado[resultado['MONTO'] == monto_buscado]

            # Mostrar resultados
            if not resultado.empty:
                st.success(f"¡Se encontraron {len(resultado)} registros!")
                st.dataframe(resultado, use_container_width=True)
                
                if 'MONTO' in resultado.columns:
                    total_monto = resultado['MONTO'].sum()
                    st.metric(label="Monto Total Encontrado", value=f"{total_monto:,.2f} Bs")
            else:
                st.warning("No se encontró ningún registro con los filtros especificados.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo de Excel: {e}")