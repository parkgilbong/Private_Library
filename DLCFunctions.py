def df_to_dic_single(df, ignore_bodyparts:str = 'PatchCordBase'):
    """
    Convert single dlc output data to a python dictionary. The input data format should be a pandas DataFrame format. 
    """

    # Create a dictionary to map body part names to coordinate columns 
    body_part_data = {} 
    # Get unique body parts from the first level of the MultiIndex (excluding 'bodyparts')
    unique_body_parts = df.columns.get_level_values(0).unique().tolist() 
    unique_body_parts.remove('bodyparts')
    unique_body_parts.remove(ignore_bodyparts)
        
    for part in unique_body_parts:
      # Use the MultiIndex to access the data
         body_part_data[part] = {
            "x": df.loc[:, (part, 'x')].to_numpy(),
            "y": df.loc[:, (part, 'y')].to_numpy(), 
            "likelihood": df.loc[:, (part, 'likelihood')].to_numpy()
            }
             
    for part in body_part_data.keys():
         print(f"body parts: {part}")

    return body_part_data


def df_to_dic_multi(df, ignore_bodyparts:str = 'PatchCordBase'):     
     """
     Convert multi dlc output data to two python dictionaries. The input data format should be a pandas DataFrame format.
     """

     # Create a dictionary to map body part names to coordinate columns
     body_part_data1 = {}
     body_part_data2 = {}

     # Get unique body parts from the first level of the MultiIndex (excluding 'bodyparts')
     unique_body_parts = df.columns.get_level_values(0).unique().tolist()
     unique_body_parts.remove('bodyparts')
     unique_body_parts.remove(ignore_bodyparts)
        
     for part in unique_body_parts:
        # Use the MultiIndex to access the data
        body_part_data1[part] = {
            "x": df.loc[:, (part, 'x')].to_numpy(), 
            "y": df.loc[:, (part, 'y')].to_numpy(), 
            "likelihood": df.loc[:, (part, 'likelihood')].to_numpy()}
        
     for part in unique_body_parts:
        # Use the MultiIndex to access the data
        body_part_data2[part] = {
            "x": df.loc[:, (part, 'x.1')].to_numpy(), 
            "y": df.loc[:, (part, 'y.1')].to_numpy(), 
            "likelihood": df.loc[:, (part, 'likelihood.1')].to_numpy()}
     
     return body_part_data1, body_part_data2