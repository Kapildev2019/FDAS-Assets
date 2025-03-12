import streamlit as st 
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk
import matplotlib
from shapely.geometry import Point, Polygon

# Streamlit App Title
st.title("Standing tree volume calculation")

# User Input for EPSG
EPSG = st.text_input("Enter 32644 (UTM44) or 32645 (UTM45)", value="32645")

# User Input for Grid Spacing
grid_spacing = st.number_input("Mother tree to mother tree distance in meter", value=20)

# File Upload for Excel
uploaded_file = st.file_uploader(":file_folder: Upload your excel data file", type=['xlsx', 'xls'])

# Create the data dictionary with Nepali species names
data = {
    "प्रजाती": ['साल', 'साज', 'उत्तिस', 'चिलाउने', 'पात्ले कटुस', 'ढाल्ने कटुस', 'मुसुरे कटुस', 'खयर', 'शिशौ', 'खोटेसल्ला', 
                'शिरिष', 'पाटेसल्ला', 'टिक', 'कर्मा', 'सिमल', 'टुनी', 'जामुन', 'मसला', 'पपलर', 'बोटधँगेरो', 
                'चाँप', 'हर्रो', 'बर्रो', 'आँप', 'सौर', 'भुडकुल/लाटी कर्मा', 'सतिसाल', 'विजयसाल', 'गुटेल', 'गम्हारी', 
                'सन्दन/पाजन', 'बाँझी', 'ओखर', 'दार', 'गोब्रेसल्ला', 'खस्रु', 'ठिङ्ग्रेसल्ला', 'धूपी सल्ला/सुगा', 
                'फल्दु', 'तालिसपत्र', 'देवदार', 'स्प्रुस', 'श्वेत चन्दन', 'तराईका अन्य प्रजाति', 'पहाडका अन्य प्रजाति'],
    'a': [-2.4554, -2.4616, -2.7761, -2.7385, -2.3204, -2.3204, -2.3204, -2.3256, -2.1959, -2.977, 
          -2.4284, -2.3204, -2.3993, -2.5626, -2.3865, -2.1832, -2.5693, -2.3993, -2.3993, -2.3411, 
          -2.0152, -2.3993, -2.3993, -2.3993, -2.3204, -2.585, -2.3993, -2.3993, -2.4585, -2.3993, 
          -2.3993, -2.272, -2.3204, -2.3204, -2.8195, -2.36, -2.4453, -2.5293, -2.3204, -2.3204, 
          -2.3204, -2.3204, -2.3204, -2.3993, -2.3204],
    'b': [1.9026, 1.8497, 1.9006, 1.8155, 1.8507, 1.8507, 1.8507, 1.6476, 1.6567, 1.9235, 
          1.7609, 1.8507, 1.7836, 1.8598, 1.7414, 1.8679, 1.8816, 1.7836, 1.7836, 1.7246, 
          1.8555, 1.7836, 1.7836, 1.7836, 1.8507, 1.9437, 1.7836, 1.7836, 1.8043, 1.7836, 
          1.7836, 1.7499, 1.8507, 1.8507, 1.725, 1.968, 1.722, 1.7815, 1.8507, 1.8507, 
          1.8507, 1.8507, 1.8507, 1.7836, 1.8507],
    'c': [0.8352, 0.88, 0.9428, 1.0072, 0.8223, 0.8223, 0.8223, 1.0552, 0.9899, 1.0019, 
          0.9662, 0.8223, 0.9546, 0.8783, 1.0063, 0.7569, 0.8498, 0.9546, 0.9546, 0.9702, 
          0.763, 0.9546, 0.9546, 0.9546, 0.8223, 0.7902, 0.9546, 0.9546, 0.922, 0.9546, 
          0.9546, 0.9174, 0.8223, 0.8223, 1.1623, 0.7469, 1.0757, 1.0369, 0.8223, 0.8223, 
          0.8223, 0.8223, 0.8223, 0.9546, 0.8223],
    'a1': [5.2026, 4.5968, 6.019, 7.4617, 5.5323, 5.5323, 5.5323, 5.4401, 4.358, 6.2696, 
           4.4031, 5.5323, 4.8991, 5.4681, 4.5554, 4.9705, 5.1749, 4.8991, 4.8991, 5.3349, 
           3.3499, 4.8991, 4.8991, 4.8991, 5.5323, 5.5572, 4.8991, 4.8991, 5.3475, 4.8991, 
           4.8991, 4.9502, 5.5323, 5.5323, 5.7216, 4.8511, 5.4443, 5.2774, 5.5323, 5.5323, 
           5.5323, 5.5323, 5.5323, 4.8991, 5.5323],
    'b1': [-2.4788, -2.2305, -2.7271, -3.0676, -2.4815, -2.4815, -2.4815, -2.491, -2.1559, -2.8252, 
           -2.2094, -2.4815, -2.3406, -2.4398, -2.3009, -2.3436, -2.3636, -2.3406, -2.3406, -2.4428, 
           -2.0161, -2.3406, -2.3406, -2.3406, -2.4815, -2.496, -2.3406, -2.3406, -2.4774, -2.3406, 
           -2.3406, -2.3353, -2.4815, -2.4815, -2.6788, -2.4494, -2.6902, -2.6483, -2.4815, -2.4815, 
           -2.4815, -2.4815, -2.4815, -2.3406, -2.4815],
    'small': [0.055, 0.4, 0.803, 0.52, 0.4, 0.4, 0.4, 0.4, 0.684, 0.189, 
              0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
              0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
              0.4, 0.4, 0.4, 0.4, 0.683, 0.747, 0.436, 0.436, 0.4, 0.4, 
              0.4, 0.4, 0.4, 0.4, 0.4],
    'medium': [0.341, 0.4, 1.226, 0.186, 0.4, 0.4, 0.4, 0.4, 0.684, 0.256, 
               0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
               0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
               0.4, 0.4, 0.4, 0.4, 0.488, 0.96, 0.372, 0.372, 0.4, 0.4, 
               0.4, 0.4, 0.4, 0.4, 0.4],
    'big': [0.357, 0.4, 1.51, 0.168, 0.4, 0.4, 0.4, 0.4, 0.684, 0.3, 
            0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
            0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
            0.4, 0.4, 0.4, 0.4, 0.41, 1.06, 0.355, 0.355, 0.4, 0.4, 
            0.4, 0.4, 0.4, 0.4, 0.4]
}
df_par = pd.DataFrame(data)

# Initialize layer and view_state before the conditional block
layer = None  # Ensure layer is defined
view_state = pdk.ViewState(latitude=0, longitude=0, zoom=2, pitch=0)  # Default view state

# Function to calculate additional fields
def add_calculated_columns(df):  
    df['stem_volume'] = np.exp(df['a'] + df['b'] * np.log(df['dia_cm']) + df['c'] * np.log(df['height_m'])) / 1000

    # Branch ratio calculation based on dia_cm
    conditions = [
        df['dia_cm'] < 10,
        (df['dia_cm'] >= 10) & (df['dia_cm'] < 40),
        (df['dia_cm'] >= 40) & (df['dia_cm'] < 70),
        df['dia_cm'] >= 70
    ]

    choices = [
        df['small'],  # For dia_cm < 10
        ((df["dia_cm"] - 10) * df["big"] + (40 - df["dia_cm"]) * df["medium"]) / 30,
        ((df["dia_cm"] - 40) * df["big"] + (70 - df["dia_cm"]) * df["medium"]) / 30,
        df['big']   # For dia_cm >= 70
    ]

    df['branch_ratio'] = np.select(conditions, choices)
    df['branch_volume'] = df['stem_volume'] * df['branch_ratio']
    df['tree_volume'] = df['stem_volume'] + df['branch_volume']
    df['cm10diaratio'] = np.exp(df['a1'] + df['b1'] * np.log(df['dia_cm']))
    df['cm10topvolume'] = df['stem_volume'] * df['cm10diaratio']
    df['gross_volume'] = df['stem_volume'] - df['cm10topvolume']
    df['net_volume'] = df.apply(lambda row: row['gross_volume'] * 0.9 if row.get('class', '') == 'A' else row['gross_volume'] * 0.8, axis=1)
    df['net_volum_cft'] = df['net_volume'] * 35.3147
    df['firewood_m3'] = df['tree_volume'] - df['net_volume']
    df['firewood_chatta'] = df['firewood_m3'] * 0.105944
    df['counted'] = 1

    return df

# Function to create a square grid
def create_square_grid(input_gdf, spacing=20):
    # Ensure the GeoDataFrame has the correct CRS
    if input_gdf.crs.to_epsg() != 32645:
        input_gdf = input_gdf.to_crs(epsg=32645)
    # Get the bounding box of the GeoDataFrame
    minx, miny, maxx, maxy = input_gdf.total_bounds
    # Create arrays of coordinates based on the spacing
    x_coords = np.arange(minx, maxx, spacing)
    y_coords = np.arange(miny, maxy, spacing)
    # Create the square polygons
    polygons = []
    for x in x_coords:
        for y in y_coords:
            polygon = Polygon([(x, y), (x + spacing, y), (x + spacing, y + spacing), (x, y + spacing)])
            polygons.append(polygon)
    # Create a GeoDataFrame with the square polygons
    grid_gdf = gpd.GeoDataFrame(geometry=polygons, crs=input_gdf.crs)
    return grid_gdf

if uploaded_file:
    # Read the Excel file into a dictionary of DataFrames (one per sheet)
    excel_df_dict = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_list = list(excel_df_dict.keys())
    selected_sheet = st.selectbox("📘 Select a sheet from excel file that contain tree data:", sheet_list)
    
    if selected_sheet:
        excel_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        species_columns = ['Species', 'species', 'sps', 'Sps', 'Spp', 'Spps', 'Tree', 'Trees', 'spp', 'SPP', 'SPPS', 'SPPs', 'SPS', 'SPs', 'Sp','sp', 'SP', 'spps', 
        'जात', 'प्रजाती', 'प्रजाति', 'रुखको जात', 'रुखको प्रजाती', 'रुखको प्रजाति', 'रुख प्रजाती','रुख प्रजाति', 'tree', 'trees',  'TREE', 'Tree Spps', 'Tree Spp','Tree Species',
        'वनस्पति', 'वनस्पती', 'बनस्पति', 'बनस्पती','जाति','जाती', 'नाम', 'स्पेशिस', 'जात', 'spp.', 'SPP.', 'SPPS.', 'SPPs.', 'SPS.', 'SPs.', 'Sp.','sp.', 'SP.', 'spps.', 'Tree spp.','Tree spp',
        'स्पेशीस', 'स्पेसिस', 'स्पेसीस', 'स्पेशिश', 'स्पेशीश', 'स्पेसिश', 'स्पेसीश', 'Prajati', 'prajati', 'Jati', 'jati', 'Jat','jat','specie','Specie','SPECIES', 'Tree Spp.',  'tree Spp', 'tree spp', 'tree Spp.', 'tree spp.',
        'रुखको नाम', 'रुख', 'प्रजातीको नाम', 'प्रजातिको नाम', 'प्रजाती नाम', 'प्रजाति नाम', 'प्रजाती', 'प्रजाति (Species)', 'जात (Species)', 'hft', 'k|hftL', 'k|hflt', 'hflt', 'hftL', '?v', '?vsf] hft', '?vsf] k|hftL', '?vsf] k|hflt',
        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 
        'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', 
        'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX',
        'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
        'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह', 'क्ष', 'त्र', 'ज्ञ'
        ]

    valid_species_column = next((col for col in species_columns 
                        if col in excel_df.columns), None)

    # Column Mapping in an Expander
    with st.expander("🔧 Column Mapping (Optional)"):
        # Check for a valid species column
        species_columns = ['Species', 'प्रजाती', 'species']  # Possible species column names
        valid_species_column = next((col for col in species_columns if col in excel_df.columns), None)
        
        # --- Column Mapping ---
        if valid_species_column:
            st.markdown("#### :material/database_search: Please choose matching column:")
            mandatory_cols = ['रुख नं.', 'Species', 'गोलाई/ब्यास', 'उचाई', 'दर्जा']  # Mandatory columns
            optional_cols = ['सि.नं.', 'X-Coordinate', 'Y-Coordinate', 'कैफियत']  # Optional columns
            all_cols = mandatory_cols + optional_cols
            column_mappings = {}
            cols = st.columns(len(all_cols))
            for i, col in enumerate(all_cols):
                with cols[i]:
                    column_mappings[col] = st.selectbox(f"{col}:", [''] + list(excel_df.columns), key=f"col_map_{i}")

            if all(column_mappings[col] != '' for col in mandatory_cols):
                mapped_excel_df = excel_df.rename(columns={column_mappings[col]: col for col in column_mappings if column_mappings[col] != ''})
                
                for col in optional_cols:  # Add missing optional columns
                    if col not in mapped_excel_df.columns:
                        mapped_excel_df[col] = ''
                
                # Proceed with mapped DataFrame
                excel_df = mapped_excel_df  # Update excel_df with mapped columns
    
    # Merge with predefined species data (using the possibly mapped DataFrame)
    joined_df = excel_df.merge(df_par, left_on='Species', right_on='प्रजाती', how='left')
    
    # Rename columns to English for consistency with further processing
    joined_df = joined_df.rename(columns={
        'रुख नं.': 'TID',
        'गोलाई/ब्यास': 'dia_cm',
        'उचाई': 'height_m',
        'दर्जा': 'class',
        'X-Coordinate': 'LONGITUDE',
        'Y-Coordinate': 'LATITUDE'
    })
    
    # Create geometry column
    joined_df['geometry'] = joined_df.apply(lambda row: Point(row['LONGITUDE'], row['LATITUDE']) if pd.notna(row['LONGITUDE']) and pd.notna(row['LATITUDE']) else None, axis=1)
    joined_gdf = gpd.GeoDataFrame(joined_df, geometry='geometry')
    joined_gdf = joined_gdf.set_crs(epsg=4326)
    joined_gdf = add_calculated_columns(df=joined_gdf)
    result_gdf = joined_gdf.to_crs(epsg=EPSG)
    
    # Create grid
    grid_gdf = create_square_grid(input_gdf=result_gdf, spacing=grid_spacing)
    grid_gdf['gid'] = grid_gdf.index + 1
    # Spatial join to assign 'gid' to points based on intersection
    result_gdf = gpd.sjoin(result_gdf, grid_gdf, how='inner', predicate='intersects')
    result_gdf = result_gdf.sort_values(by='gid', ascending=True)
    # Create a boolean mask to identify the first unique 'gid' value
    first_unique_mask = result_gdf['gid'].duplicated(keep='first')
    # Create the 'remark' column and populate it based on the mask
    result_gdf['remark'] = 'Felling Tree'
    result_gdf.loc[~first_unique_mask, 'remark'] = 'Mother Tree'
    result_gdf['color'] = result_gdf['remark'].apply(lambda x: 'red' if x == 'Mother Tree' else 'green')
    result_gdf['color'] = result_gdf['color'].apply(lambda x: matplotlib.colors.to_rgba(x))
    result_gdf['color'] = result_gdf['color'].apply(lambda x: list(x))
    result_gdf['color'] = result_gdf['color'].apply(lambda x: [int(val * 255) for val in x])
    
    # Ensure joined_gdf and result_gdf are in EPSG:4326
    joined_gdf = joined_gdf.to_crs(epsg=4326)
    result_gdf = result_gdf.to_crs(epsg=4326)
    
    # Add longitude and latitude columns for centroids
    joined_gdf["LONGITUDE"] = joined_gdf.geometry.centroid.x
    joined_gdf["LATITUDE"] = joined_gdf.geometry.centroid.y
    
    # Define Pydeck layers
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        result_gdf,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=2,
        get_color="color",
        pickable=True,
        auto_highlight=True,
        tooltip={
            "html": """
            <b>TID:</b> {TID}<br>
            <b>Species:</b> {Species}<br>
            """
        }
    )
    
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        grid_gdf,
        get_polygon="geometry",
        get_fill_color=[155, 50, 50, 140],
        get_line_color=[0, 100, 100, 200],
        pickable=True,
    )
    
    # View state for the map
    view_state = pdk.ViewState(
        latitude=result_gdf["LATITUDE"].mean(),
        longitude=result_gdf["LONGITUDE"].mean(),
        zoom=15,
        pitch=0,
    )
    
    # Combine layers into a Pydeck Deck
    deck = pdk.Deck(
        layers=[point_layer, polygon_layer],
        initial_view_state=view_state,
    )
    
    # Display the map
    st.write("View the Mother Tree and Felling Tree Location")
    st.pydeck_chart(deck)