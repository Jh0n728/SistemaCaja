import pandas as pd
import streamlit as st
import os

st.set_page_config(page_title="Sistema de Pagos - Caja y Valores", layout="wide")

st.title("Universidad Pedagógica - Caja y Valores")
st.write("Sistema de Consulta de Pagos y Valores")

archivo_cuenta33 = "BASE CUOTAS PARA SISTEMA.xlsx"
archivo_cuenta14 = "BASE VALORES PARA SISTEMA.xlsx"


archivos_faltantes = []
if not os.path.exists(archivo_cuenta33):
    archivos_faltantes.append(archivo_cuenta33)
if not os.path.exists(archivo_cuenta14):
    archivos_faltantes.append(archivo_cuenta14)

if archivos_faltantes:
    st.error(f"No se encuentran los siguientes archivos en la carpeta: {', '.join(archivos_faltantes)}. Asegúrate de que estén junto a app.py")
else:

    @st.cache_data
    def cargar_y_unificar_datos():
  
        df33 = pd.read_excel(archivo_cuenta33)
        if 'Unnamed: 0' in df33.columns:
            df33 = df33.drop(columns=['Unnamed: 0'])
        
        df33['TIPO_CUENTA'] = 'CUENTA 33 (Cuotas)'
        df33 = df33.rename(columns={
            'N° DE DEPOSITO': 'DEPOSITO',
            'NOMBRE': 'NOMBRE_COMPLETO',
            'PROGRAMA-DESCRIPCION': 'DETALLE'
        })

   
        df14 = pd.read_excel(archivo_cuenta14)
        df14.columns = df14.columns.str.strip()
        
        df14['TIPO_CUENTA'] = 'CUENTA 14 (Valores)'
        df14 = df14.rename(columns={
            'Nº DE POSITO': 'DEPOSITO',
            'NOMBRE Y APELLIDO': 'NOMBRE_COMPLETO',
            'MONTO': 'MONTO',
            'DESCRIPCION': 'DETALLE'
        })
    
        if 'Nº DEPOSITO' in df14.columns:
            df14 = df14.rename(columns={'Nº DEPOSITO': 'DEPOSITO'})

  
        df_unificado = pd.concat([df33, df14], ignore_index=True)
        
  
        if 'FECHA' in df_unificado.columns:
            df_unificado['FECHA'] = pd.to_datetime(df_unificado['FECHA'], errors='coerce')
            
        return df_unificado

    try:
        df_pagos = cargar_y_unificar_datos()
        
  
        st.markdown("---")
        st.subheader(" Búsqueda y Filtros")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            busqueda = st.text_input("Nombre, Apellidos o N° de Depósito, THERIANO:")
            
        with col2:
         
            opcion_cuenta = st.selectbox(
                "Tipo de Cuenta:",
                ["Todas", "CUENTA 33 (Cuotas)", "CUENTA 14 (Valores)"]
            )
            
        with col3:
            filtrar_monto = st.checkbox("Filtrar por Monto exacto")
            monto_buscado = None
            if filtrar_monto:
                monto_buscado = st.number_input("Monto (Bs):", min_value=0.0, step=10.0)
                
        with col4:
            filtrar_fecha = st.checkbox("Filtrar por Rango de Fechas")

      
        fecha_inicio, fecha_fin = None, None
        if filtrar_fecha:
            st.markdown("---")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                fecha_inicio = st.date_input("Fecha de Inicio:")
            with col_f2:
                fecha_fin = st.date_input("Fecha de Fin:")
        
        st.markdown("---")

       
        resultado = df_pagos.copy()

        
        if busqueda:
            busqueda_limpia = busqueda.strip()
            palabras = busqueda_limpia.split()

            def coincide_registro(row):
                texto_nombre = str(row.get('NOMBRE_COMPLETO', ''))
                texto_participante = str(row.get('PARTICIPANTE', ''))
                texto_deposito = str(row.get('DEPOSITO', ''))
                
                contenido_completo = f"{texto_nombre} {texto_participante} {texto_deposito}".lower()
                return all(palabra.lower() in contenido_completo for palabra in palabras)

            resultado = resultado[resultado.apply(coincide_registro, axis=1)]

       
        if opcion_cuenta != "Todas":
            resultado = resultado[resultado['TIPO_CUENTA'] == opcion_cuenta]

        if filtrar_monto and not resultado.empty:
            if 'MONTO' in resultado.columns:
                resultado = resultado[resultado['MONTO'] == monto_buscado]

      
        if filtrar_fecha and not resultado.empty:
            if 'FECHA' in resultado.columns:
                f_ini = pd.to_datetime(fecha_inicio)
                f_fin = pd.to_datetime(fecha_fin)
                resultado = resultado[(resultado['FECHA'] >= f_ini) & (resultado['FECHA'] <= f_fin)]

       
        if not resultado.empty:
            st.success(f"Se encontraron {len(resultado)} registros que coinciden con los filtros")
        
            df_mostrar = resultado.copy()
            if 'FECHA' in df_mostrar.columns:
                df_mostrar['FECHA'] = df_mostrar['FECHA'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(df_mostrar, use_container_width=True)
            
            if 'MONTO' in df_mostrar.columns:
                total_monto = df_mostrar['MONTO'].sum()
                st.metric(label="Monto Total General Encontrado", value=f"{total_monto:,.2f} Bs")
        else:
            st.warning("No se encontró ningún registro con los filtros especificados.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos de Excel: {e}")